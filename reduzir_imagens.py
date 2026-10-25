# -*- coding: utf-8 -*-
"""Reduz as imagens do memorial de exemplo para distribuição.

Fotos de telefone chegam com 3000 ou 4000 pixels de lado, e a impressão em A4
usa no máximo 1600 na largura de uma página inteira. Reduzir não muda o que se
vê no papel e torna o repositório clonável.

Conferências, com o caso que cada uma reprova:
  referências  toda imagem citada no .md continua existindo depois da redução;
  tamanho      nenhuma imagem fica acima do limite (um arquivo intacto acusaria);
  proporção    a razão entre largura e altura não muda.
"""
import io
import os
import re

from PIL import Image, ImageOps

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "memorial-alexandre", "imagens")
MD = os.path.join(os.path.dirname(PASTA), "memorial.md")
LIMITE = 1600
QUALIDADE = 88


def main():
    antes_total = sum(os.path.getsize(os.path.join(PASTA, f))
                      for f in os.listdir(PASTA))
    mudadas, proporcoes = 0, []
    for nome in sorted(os.listdir(PASTA)):
        caminho = os.path.join(PASTA, nome)
        try:
            im = Image.open(caminho)
        except Exception as e:
            print(u"   ignorado (%s): %s" % (type(e).__name__, nome))
            continue
        if max(im.size) <= LIMITE:
            continue
        razao_antes = im.size[0] / float(im.size[1])
        im = ImageOps.exif_transpose(im)
        escala = LIMITE / float(max(im.size))
        novo = (max(1, int(round(im.size[0] * escala))),
                max(1, int(round(im.size[1] * escala))))
        reduzida = im.resize(novo, Image.LANCZOS)
        if caminho.lower().endswith((".jpg", ".jpeg")):
            reduzida.convert("RGB").save(caminho, quality=QUALIDADE, optimize=True)
        else:
            reduzida.save(caminho, optimize=True)
        proporcoes.append((nome, razao_antes, novo[0] / float(novo[1])))
        mudadas += 1

    depois_total = sum(os.path.getsize(os.path.join(PASTA, f))
                       for f in os.listdir(PASTA))
    grandes = [f for f in os.listdir(PASTA)
               if max(Image.open(os.path.join(PASTA, f)).size) > LIMITE]
    texto = io.open(MD, encoding="utf-8").read()
    refs = [re.match(r'^(.*?)(\s+"[^"]*"?)?$', r.strip(), re.S).group(1).strip()
            for r in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", texto)]
    ausentes = [r for r in refs
                if not os.path.exists(os.path.join(os.path.dirname(MD), r))]
    torcidas = [n for n, a, d in proporcoes if abs(a - d) > 0.01]

    print(u"reduzidas: %d imagens | %.1f MB para %.1f MB"
          % (mudadas, antes_total / 1e6, depois_total / 1e6))
    print(u"acima de %d px restantes: %d | referências quebradas: %d | "
          u"proporções alteradas: %d" % (LIMITE, len(grandes), len(ausentes),
                                         len(torcidas)))
    for x in grandes + ausentes + torcidas:
        print(u"   %s" % x)
    assert not grandes and not ausentes and not torcidas


if __name__ == "__main__":
    main()
