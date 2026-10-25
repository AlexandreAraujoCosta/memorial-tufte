# -*- coding: utf-8 -*-
"""Traz o memorial de Alexandre Araújo Costa para dentro do repositório.

O arquivo original aponta para imagens espalhadas pela máquina do autor (pasta
do Typora, Downloads). Aqui elas são copiadas para `imagens/` e os caminhos
reescritos, para que o exemplo funcione na máquina de qualquer pessoa.

Conferências, com o caso que cada uma reprova:
  imagens    toda referência passa a existir dentro do repositório;
  texto      o número de palavras não muda (só os caminhos mudam);
  caminhos   nenhum caminho absoluto sobra (um inventado seria acusado).
"""
import io
import os
import re
import shutil

ORIGEM = r"D:\vscode\memorial-titular\memorial.md"
PDF_ORIGEM = r"D:\vscode\memorial-titular\output\memorial.pdf"
DESTINO = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "memorial-alexandre")
IMAGENS = os.path.join(DESTINO, "imagens")


def caminho_de(ref):
    """Separa o caminho do título entre aspas: ![x](caminho "título")."""
    m = re.match(r'^(.*?)(\s+"[^"]*"?)?$', ref.strip(), re.S)
    return m.group(1).strip(), (m.group(2) or "")


def main():
    os.makedirs(IMAGENS, exist_ok=True)
    texto = io.open(ORIGEM, encoding="utf-8").read()
    palavras_antes = len(texto.split())

    usados, faltando = {}, []

    def troca(m):
        ref = m.group(1)
        caminho, titulo = caminho_de(ref)
        if not os.path.exists(caminho):
            faltando.append(caminho)
            return m.group(0)
        base = os.path.basename(caminho)
        # nomes repetidos em pastas diferentes ganham sufixo
        if base in usados and usados[base] != caminho:
            raiz, ext = os.path.splitext(base)
            i = 2
            while "%s-%d%s" % (raiz, i, ext) in usados:
                i += 1
            base = "%s-%d%s" % (raiz, i, ext)
        usados[base] = caminho
        destino = os.path.join(IMAGENS, base)
        if not os.path.exists(destino):
            shutil.copy2(caminho, destino)
        return m.group(0).replace(ref, "imagens/" + base + titulo)

    novo = re.sub(r"!\[[^\]]*\]\(([^)]+)\)", troca, texto)
    io.open(os.path.join(DESTINO, "memorial.md"), "w",
            encoding="utf-8", newline="\n").write(novo)

    if os.path.exists(PDF_ORIGEM):
        shutil.copy2(PDF_ORIGEM, os.path.join(DESTINO, "memorial.pdf"))

    refs = [caminho_de(r)[0] for r in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", novo)]
    fora = [r for r in refs if not r.startswith("imagens/")]
    ausentes = [r for r in refs
                if r.startswith("imagens/") and not os.path.exists(os.path.join(DESTINO, r))]
    absolutos = len(re.findall(r"\]\([A-Za-z]:\\", novo))
    mb = sum(os.path.getsize(os.path.join(IMAGENS, f))
             for f in os.listdir(IMAGENS)) / 1e6

    print(u"imagens copiadas: %d (%.1f MB)" % (len(usados), mb))
    print(u"referências fora de imagens/: %d | arquivos ausentes: %d | "
          u"caminhos absolutos restantes: %d" % (len(fora), len(ausentes), absolutos))
    print(u"palavras: %d antes, %d depois" % (palavras_antes, len(novo.split())))
    for f in faltando:
        print(u"   não encontrei: %s" % f)
    assert not fora and not ausentes and absolutos == 0
    assert palavras_antes == len(novo.split())


if __name__ == "__main__":
    main()
