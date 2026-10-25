# -*- coding: utf-8 -*-
"""Gera o PDF do memorial a partir de um arquivo .md ou .docx.

    python build.py meu-memorial.md
    python build.py meu-memorial.docx --capa
    python build.py exemplo/memorial-exemplo.md --saida saida/exemplo.pdf

O que ele faz, nesta ordem:

 1. confere se pandoc e xelatex existem, e diz o que instalar se não existirem;
 2. se a entrada for .docx, converte para Markdown e extrai as imagens;
 3. opcionalmente gera a capa, a partir do cabeçalho do próprio arquivo;
 4. chama o pandoc com o modelo tufte.

Partindo de .docx, a conversão preserva títulos, notas de rodapé, imagens,
negrito, itálico, citações e tabelas. O que o Word não tem é a nota lateral: por
isso existe a convenção `[margem: ...]`, que este programa converte na marcação
que o modelo entende. Escreva no Word, no corpo do texto, algo como

    [margem: Esta observação vai na margem, ao lado do parágrafo.]

e ela virará nota lateral no PDF.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.abspath(__file__))
MODELOS = os.path.join(RAIZ, "modelos")


def precisa(programa, como_instalar):
    caminho = shutil.which(programa)
    if not caminho:
        raise SystemExit(u"%s não foi encontrado no PATH.\n%s" % (programa, como_instalar))
    return caminho


def acha_xelatex():
    caminho = shutil.which("xelatex")
    if caminho:
        return caminho
    # MiKTeX no Windows nem sempre entra no PATH
    palpites = [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\MiKTeX\miktex\bin\x64\xelatex.exe"),
        r"C:\Program Files\MiKTeX\miktex\bin\x64\xelatex.exe",
        "/usr/bin/xelatex", "/usr/local/bin/xelatex",
        "/Library/TeX/texbin/xelatex",
    ]
    for p in palpites:
        if os.path.exists(p):
            return p
    raise SystemExit(u"xelatex não foi encontrado. Instale o MiKTeX (Windows), o "
                     u"TeX Live (Linux) ou o MacTeX (macOS), com os pacotes "
                     u"tufte-latex e etbb.")


def de_docx(entrada, destino_md):
    """Converte .docx em Markdown e extrai as imagens para ao lado do texto."""
    midia = os.path.join(os.path.dirname(destino_md) or ".", "imagens")
    subprocess.run(["pandoc", entrada, "-t", "markdown",
                    "--track-changes=accept", "--extract-media", midia,
                    "-o", destino_md], check=True)
    texto = open(destino_md, encoding="utf-8").read()
    # [margem: ...] vira nota lateral; o Word não tem como marcar isso de outro jeito
    texto, n = re.subn(r"\[margem:\s*(.+?)\]", r"^[\1]", texto, flags=re.S)
    open(destino_md, "w", encoding="utf-8").write(texto)
    print(u"convertido do Word: %s | notas de margem reconhecidas: %d" % (destino_md, n))
    return destino_md


def cabecalho(md):
    """Lê o bloco YAML do início do arquivo, sem depender de biblioteca."""
    texto = open(md, encoding="utf-8").read()
    m = re.match(r"(?s)^---\s*\n(.*?)\n---\s*\n", texto)
    dados = {}
    if m:
        for linha in m.group(1).splitlines():
            c = re.match(r'^(\w+):\s*"?(.*?)"?\s*$', linha)
            if c:
                dados[c.group(1)] = c.group(2)
    return dados


def main():
    p = argparse.ArgumentParser(description=u"Gera o PDF do memorial.")
    p.add_argument("entrada", help=u"arquivo .md ou .docx")
    p.add_argument("--saida", default=None)
    p.add_argument("--capa", action="store_true", help=u"gera e aplica a capa")
    p.add_argument("--marca", default=None, help=u"imagem da marca da instituição")
    p.add_argument("--sumario", action="store_true", default=True)
    a = p.parse_args()

    precisa("pandoc", u"Baixe em https://pandoc.org/installing.html")
    xelatex = acha_xelatex()

    entrada = a.entrada
    if entrada.lower().endswith(".docx"):
        entrada = de_docx(entrada, os.path.splitext(entrada)[0] + ".md")

    saida = a.saida or os.path.splitext(entrada)[0] + ".pdf"
    os.makedirs(os.path.dirname(os.path.abspath(saida)), exist_ok=True)

    # As imagens vêm em caminho relativo ao .md, e quem as abre é o LaTeX, a
    # partir da pasta em que está rodando. Por isso o programa entra na pasta do
    # arquivo e usa caminhos absolutos para tudo o mais.
    entrada_abs = os.path.abspath(entrada)
    pasta_entrada = os.path.dirname(entrada_abs) or os.getcwd()
    saida = os.path.abspath(saida)
    entrada_rel = os.path.basename(entrada_abs)
    marca = os.path.abspath(a.marca) if a.marca else None
    os.chdir(pasta_entrada)

    cmd = ["pandoc", entrada_rel,
           "--template", os.path.join(MODELOS, "tufte.tex"),
           "--lua-filter", os.path.join(MODELOS, "pagebreak.lua"),
           "--top-level-division=part",
           "--pdf-engine=" + xelatex,
           "-o", saida]
    if a.sumario:
        cmd.append("--toc")

    if a.capa:
        dados = cabecalho(entrada_abs)
        capa = os.path.join(os.path.dirname(saida), "capa.png")
        sys.path.insert(0, MODELOS)
        import gerar_capa
        rodape = [l.strip() for l in (dados.get("institution", "") + " · "
                                      + dados.get("date", "")).split("·") if l.strip()]
        gerar_capa.gerar(dados.get("title", u"Memorial Acadêmico"),
                         dados.get("subtitle", u"Promoção à classe de Professor Titular"),
                         dados.get("author", u"Autor"),
                         [u" · ".join(rodape)] if rodape else [],
                         marca, capa, gerar_capa.VERDE, gerar_capa.AZUL)
        cmd += ["-V", "capa=" + capa.replace("\\", "/")]

    print(u"gerando %s" % saida)
    subprocess.run(cmd, check=True)

    if not os.path.exists(saida):
        raise SystemExit(u"o pandoc terminou sem erro, mas o arquivo não apareceu")
    print(u"pronto: %s (%.1f MB)" % (saida, os.path.getsize(saida) / 1e6))


if __name__ == "__main__":
    main()
