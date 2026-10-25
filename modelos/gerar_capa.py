# -*- coding: utf-8 -*-
"""Gera a imagem de capa: marca no alto à esquerda e anel grosso cruzando o pé.

Esta é a versão portátil do gerador usado no memorial de Alexandre Araújo Costa.
Em relação ao original, três coisas mudaram para que ele rode na máquina de
outra pessoa: a fonte é escolhida entre as disponíveis, a marca da instituição é
opcional e todos os caminhos vêm por parâmetro.

Quase nada aqui é arbitrado; quase tudo é deduzido de outra coisa:

    raio do anel   <- chega à direita a uma distância da borda igual à sua
                      própria espessura
    corpo do título <- preenche o bloco que vai da borda direita até o início
                      do texto da marca (título e marca partilham a coluna)
    tracking do subtítulo <- fecha exatamente na largura que o título tem
    espaços verticais <- os blocos se distribuem com folgas iguais entre o pé da
                      marca e o ápice do arco

Uso:
    python gerar_capa.py --titulo "Memorial Acadêmico" \
        --subtitulo "Promoção à classe de Professor Titular" \
        --autor "Nome do Autor" --rodape "Faculdade · 2026" \
        --marca caminho/para/marca.png --saida capa.png
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

DPI = 300
W = int(210 / 25.4 * DPI)    # A4 em pixels
H = int(297 / 25.4 * DPI)
WHITE = (255, 255, 255)

# Azul e verde extraídos da marca da UnB. Troque pelos da sua instituição.
AZUL = (1, 63, 122)
VERDE = (0, 129, 55)

MARGIN = 230
MAX_W = W - 2 * MARGIN
RIGHT_EDGE = W - MARGIN

# Espessura do anel: 70,87 pts de traço numa página de 612,28 de altura, medida
# na capa-modelo em CorelDRAW de onde este desenho veio.
RING_THICKNESS_RATIO = 0.1157
RING_SS = 4                  # supersampling, para a borda do anel não serrilhar

LOGO_ALTURA = 105
SUBTITLE_SIZE = 60
SUBTITLE_TRACKING_MAX = 0.22
NOME_SIZE_MAX = 130
TITLE_TO_SUB_GAP = 60
RODAPE_LEADING = 1.4
GOTHIC_CAP_RATIO = 0.736     # altura de maiúscula da Century Gothic, a 1000pt

# Famílias geométricas, da preferida para a alternativa. A Century Gothic é da
# Microsoft e não se redistribui; as demais são abertas. Se nenhuma existir, o
# programa avisa em vez de desenhar com uma fonte que desmancha o layout.
FAMILIAS = [
    ("Century Gothic", "GOTHIC.TTF", "GOTHICB.TTF"),
    ("Questrial", "Questrial-Regular.ttf", "Questrial-Regular.ttf"),
    ("Jost", "Jost-Regular.ttf", "Jost-SemiBold.ttf"),
    ("Didact Gothic", "DidactGothic-Regular.ttf", "DidactGothic-Regular.ttf"),
    ("DejaVu Sans", "DejaVuSans.ttf", "DejaVuSans-Bold.ttf"),
]

PASTAS_DE_FONTE = [
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts"),
    os.path.expanduser("~/.fonts"),
    os.path.expanduser("~/Library/Fonts"),
    "/usr/share/fonts/truetype",
    "/usr/local/share/fonts",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "fontes"),
]


def acha_fonte(nome_arquivo):
    for pasta in PASTAS_DE_FONTE:
        for raiz, _, arquivos in os.walk(pasta) if os.path.isdir(pasta) else []:
            if nome_arquivo in arquivos:
                return os.path.join(raiz, nome_arquivo)
    return None


def escolhe_familia():
    for nome, regular, negrito in FAMILIAS:
        r, n = acha_fonte(regular), acha_fonte(negrito)
        if r and n:
            return nome, r, n
    raise SystemExit(
        u"Nenhuma das fontes previstas foi encontrada. Instale uma destas: "
        + u", ".join(f[0] for f in FAMILIAS)
        + u", ou ponha o arquivo .ttf em modelos/fontes/.")


FAMILIA, ARQ_REG, ARQ_BOLD = escolhe_familia()
f_reg = lambda s: ImageFont.truetype(ARQ_REG, s)
f_bold = lambda s: ImageFont.truetype(ARQ_BOLD, s)


def cap_height(size):
    return size * GOTHIC_CAP_RATIO


def arco_afundado(r_out, cruza_direita_em=None, pe_x=None):
    """Centro do arco que cruza o pé em `pe_x` e a borda direita na altura dada.

    Duas condições, duas incógnitas: subtraindo as equações dos dois pontos
    sobre o círculo sobra uma reta em (cx, cy); substituindo-a numa delas,
    resolve-se cy por bisseção."""
    if cruza_direita_em is None:
        cruza_direita_em = H / 2
    if pe_x is None:
        pe_x = MARGIN
    a = 2 * (W - pe_x)
    b = 2 * (cruza_direita_em - H)
    c = pe_x ** 2 - W ** 2 + H ** 2 - cruza_direita_em ** 2
    cx_de = lambda cy: -(b * cy + c) / a
    f = lambda cy: (pe_x - cx_de(cy)) ** 2 + (H - cy) ** 2 - r_out ** 2
    lo, hi = float(H), float(H) * 2.5
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    cy = (lo + hi) / 2
    return cx_de(cy), cy


def ring_geometry():
    """Arco meio-termo: o ápice entra na página e aponta para o bloco do texto."""
    espessura = RING_THICKNESS_RATIO * H
    r_out = W - espessura
    cx_alto = MARGIN + r_out
    y_alto = float(H) - (r_out ** 2 - (cx_alto - W) ** 2) ** 0.5
    alvo = (y_alto + H / 2) / 2
    cx, cy = arco_afundado(r_out, alvo)
    return cx, cy, r_out, r_out - espessura


def pintar_anel(img, cx, cy, r_out, r_in, cor):
    """Círculo externo cheio menos o interno vazado, numa camada ampliada."""
    ss = RING_SS
    layer = Image.new("RGBA", (W * ss, H * ss), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    sx, sy, ro, ri = cx * ss, cy * ss, r_out * ss, r_in * ss
    d.ellipse([sx - ro, sy - ro, sx + ro, sy + ro], fill=cor + (255,))
    d.ellipse([sx - ri, sy - ri, sx + ri, sy + ri], fill=(0, 0, 0, 0))
    layer = layer.resize((W, H), Image.LANCZOS)
    img.paste(layer, (0, 0), layer)


def caixa_alta(texto, size):
    fonte = f_reg(size)
    return [(c, fonte) for c in texto.upper()]


def largura(glifos, tracking):
    return sum(f.getlength(c) for c, f in glifos) + tracking * (len(glifos) - 1)


def fit_size(largura_de, alvo, lo=20, hi=320):
    return min(range(lo, hi), key=lambda s: abs(largura_de(s) - alvo))


def draw_tracked(d, glifos, x, base, cor, tracking, align="left"):
    if align == "right":
        x -= largura(glifos, tracking)
    elif align == "center":
        x -= largura(glifos, tracking) / 2
    for ch, fonte in glifos:
        d.text((x, base), ch, font=fonte, fill=cor, anchor="ls")
        x += fonte.getlength(ch) + tracking


def carregar_marca(caminho):
    """Devolve (imagem, recuo). O recuo é a distância do escudo ao texto da
    marca, e vira o degrau da página. Sem marca, a margem faz as suas vezes."""
    if not caminho:
        return None, MARGIN
    img = Image.open(caminho)
    if img.mode == "RGBA":
        fundo = Image.new("RGB", img.size, WHITE)
        fundo.paste(img, mask=img.split()[3])
        img = fundo
    else:
        img = img.convert("RGB")
    larg = round(LOGO_ALTURA * img.width / img.height)
    # 0,2036 é onde começa o texto na marca da UnB; para outra marca, ajuste.
    return img.resize((larg, LOGO_ALTURA)), larg * 0.2036


def text_metrics(titulo, subtitulo, bloco_w):
    """Corpo do título, e corpo e espacejamento do subtítulo.

    O subtítulo fecha na largura que o título de fato tem. Se o espacejamento
    exigido passar do teto, quem cede é o corpo, que cresce até o espacejamento
    voltar ao razoável: sem essa válvula, subtítulo curto vira fila de letras."""
    title_size = fit_size(lambda s: f_bold(s).getlength(titulo), bloco_w)
    block_w = f_bold(title_size).getlength(titulo)

    def mede(s):
        g = caixa_alta(subtitulo, s)
        return g, (block_w - largura(g, 0)) / (len(g) - 1)

    size, vistos = SUBTITLE_SIZE, set()
    while size not in vistos:
        vistos.add(size)
        _, tracking = mede(size)
        if tracking < 0 and size > 16:
            size -= 1          # subtítulo longo: encolhe até caber na largura
        elif tracking > SUBTITLE_TRACKING_MAX * size and size < title_size:
            size += 1          # subtítulo curto: cresce até o espacejamento voltar
        else:
            break
    glifos, tracking = mede(size)
    return title_size, size, glifos, max(tracking, 0.0)


def gerar(titulo, subtitulo, autor, rodape, marca, saida, cor_arco, cor_texto):
    img = Image.new("RGB", (W, H), WHITE)
    cx, cy, r_out, r_in = ring_geometry()
    pintar_anel(img, cx, cy, r_out, r_in, cor_arco)
    d = ImageDraw.Draw(img)

    logo, recuo = carregar_marca(marca)
    if logo is not None:
        img.paste(logo, (MARGIN, MARGIN))
        pe_da_marca = MARGIN + LOGO_ALTURA
    else:
        pe_da_marca = MARGIN

    bloco_w = RIGHT_EDGE - (MARGIN + recuo)
    nome_w = bloco_w - recuo
    t_size, s_size, s_glifos, tracking = text_metrics(titulo, subtitulo, bloco_w)
    n_size = min(fit_size(lambda s: f_bold(s).getlength(autor), nome_w), NOME_SIZE_MAX)

    # Os dois blocos se distribuem entre o pé da marca e o ápice do arco, com
    # três folgas iguais. Nenhuma distância vertical é arbitrada.
    apice = cy - r_out
    alt_titulo = cap_height(t_size) + TITLE_TO_SUB_GAP + cap_height(s_size)
    folga = (apice - pe_da_marca - alt_titulo - cap_height(n_size)) / 3

    title_b = pe_da_marca + folga + cap_height(t_size)
    sub_b = title_b + TITLE_TO_SUB_GAP + cap_height(s_size)
    autor_b = sub_b + folga + cap_height(n_size)

    d.text((RIGHT_EDGE, title_b), titulo, font=f_bold(t_size), fill=cor_texto, anchor="rs")
    draw_tracked(d, s_glifos, RIGHT_EDGE, sub_b, cor_texto, tracking, align="right")
    d.text((RIGHT_EDGE, autor_b), autor, font=f_bold(n_size), fill=cor_texto, anchor="rs")

    # O rodapé não encolhe junto com o subtítulo: quando o subtítulo é longo e
    # precisa diminuir para caber, o rodapé ficaria ilegível se o acompanhasse.
    r_size = max(s_size, round(SUBTITLE_SIZE * 0.75))
    linhas = [caixa_alta(l, r_size) for l in rodape]
    alvo = max(largura(g, 0) for g in linhas) if linhas else 0
    for i, glifos in enumerate(linhas):
        tr = (alvo - largura(glifos, 0)) / max(len(glifos) - 1, 1)
        if tr > SUBTITLE_TRACKING_MAX * r_size:
            tr = 0
        base = (H - MARGIN) - (len(linhas) - 1 - i) * r_size * RODAPE_LEADING
        draw_tracked(d, glifos, RIGHT_EDGE, base, cor_texto, tr, align="right")

    img.save(saida, dpi=(DPI, DPI))
    print(u"capa: %s | fonte %s | título %d, subtítulo %d, nome %d"
          % (saida, FAMILIA, t_size, s_size, n_size))
    return saida


def cor(texto):
    t = texto.lstrip("#")
    return tuple(int(t[i:i + 2], 16) for i in (0, 2, 4))


def main():
    p = argparse.ArgumentParser(description=u"Gera a capa do memorial.")
    p.add_argument("--titulo", default=u"Memorial Acadêmico")
    p.add_argument("--subtitulo", default=u"Promoção à classe de Professor Titular")
    p.add_argument("--autor", required=True)
    p.add_argument("--rodape", default=u"", help=u"linhas separadas por ponto e vírgula")
    p.add_argument("--marca", default=None, help=u"PNG ou JPG da marca da instituição")
    p.add_argument("--saida", default="capa.png")
    p.add_argument("--cor-arco", default="008137")
    p.add_argument("--cor-texto", default="013F7A")
    a = p.parse_args()
    gerar(a.titulo, a.subtitulo, a.autor,
          [l.strip() for l in a.rodape.split(";") if l.strip()],
          a.marca, a.saida, cor(a.cor_arco), cor(a.cor_texto))


if __name__ == "__main__":
    main()
