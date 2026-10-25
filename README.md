# Memorial acadêmico no formato Tufte

Se você quer um memorial semelhante ao do exemplo, siga estes passos.

Este repositório contém o sistema de formatação usado no memorial que Alexandre
Araújo Costa apresentou à Universidade de Brasília em outubro de 2026, para
promoção à classe de Professor Titular. Você escreve em Markdown, num editor
qualquer, e o programa gera um PDF com capa, folha de rosto, sumário, notas na
margem e figuras na margem, no desenho tipográfico dos livros de Edward Tufte.

O resultado está em [`memorial-alexandre/memorial.pdf`](memorial-alexandre/memorial.pdf),
com 143 páginas, ao lado do arquivo `.md` que o gerou. É o mesmo texto, nas duas
pontas do processo.

## 1. Instale o que é preciso

São três programas, e nenhum deles é pago.

**Pandoc**, que converte o Markdown. Baixe em <https://pandoc.org/installing.html>.

**Uma distribuição TeX**, que compõe o PDF: MiKTeX no Windows
(<https://miktex.org>), TeX Live no Linux (`sudo apt install texlive-xetex
texlive-fonts-extra`) ou MacTeX no macOS (<https://tug.org/mactex>). São
necessários os pacotes `tufte-latex` e `etbb`, que o MiKTeX instala sozinho na
primeira execução e que no TeX Live vêm em `texlive-full`.

**Python 3 com a biblioteca Pillow**, só para gerar a capa:

```bash
pip install -r requirements.txt
```

## 2. Confira a instalação antes de escrever

Gere o exemplo. Se ele sair, a sua instalação está correta.

```bash
python build.py exemplo/memorial-exemplo.md --capa
```

O arquivo `exemplo/memorial-exemplo.pdf` deve ter sete páginas, com capa, uma
nota na margem e uma figura na margem. Se faltar algum pacote do TeX, a mensagem
de erro diz qual, e o MiKTeX costuma oferecer a instalação na hora.

## 3. Comece o seu memorial

Copie o exemplo e escreva por cima dele:

```bash
cp exemplo/memorial-exemplo.md meu-memorial.md
```

Troque os seis campos do cabeçalho, entre as linhas de três traços. Eles
alimentam a capa e a folha de rosto:

```yaml
---
title: "Memorial Acadêmico"
subtitle: "Promoção à classe de Professor Titular"
author: "Seu Nome Completo"
titulacao: "Professor Associado da Faculdade de X"
institution: "Universidade Y · Faculdade de X"
date: "Mês · 2026"
---
```

Depois, a cada versão:

```bash
python build.py meu-memorial.md --capa
```

## 4. As convenções do texto

O corpo é Markdown comum. Cinco coisas são específicas deste formato.

**Nota na margem.** Escreva uma nota de rodapé normal, com `[^nome]` no texto e
a definição em qualquer lugar do arquivo. Ela sai na margem, ao lado do
parágrafo que a chamou, e não no pé da página.

**Figura na margem.** Precisa de uma linha em branco antes e da marcação
`{.margin}` depois:

```markdown
![Legenda da figura.](imagens/foto.jpg){.margin}
```

Faltando qualquer uma das duas, a imagem vai para o meio do texto, em tamanho
natural, e a legenda desaparece. É o erro mais comum.

**Figura em largura inteira.** A mesma linha, sem o `{.margin}`.

**Quebra de página.** Uma linha isolada com três traços.

**Tabelas.** Usam barras verticais. A largura de cada coluna no PDF vem do
número de traços na linha de separação, e não do conteúdo.

As imagens ficam onde você quiser, desde que o caminho no texto seja relativo ao
arquivo `.md`. Uma pasta `imagens/` ao lado dele resolve.

## 5. Se você escreve no Word

Dá para começar de um `.docx`:

```bash
python build.py meu-memorial.docx --capa
```

O programa converte para Markdown, extrai as imagens para uma pasta `imagens/` e
segue adiante. Medimos o que sobrevive à conversão, no memorial inteiro: títulos,
notas de rodapé, imagens, negrito, itálico, citações e tabelas passam intactos.

O que o Word não tem é a nota na margem. Para não perdê-la, escreva no corpo do
texto, onde quiser que a nota apareça:

```
[margem: O texto que deve ir para a margem.]
```

O programa converte isso em nota lateral. O resto do Word, como estilos,
cabeçalhos e numeração automática, é descartado: quem formata é o modelo.

## 6. A capa

A capa é gerada por `modelos/gerar_capa.py`, e você pode chamá-la direto para
experimentar antes de compor o PDF:

```bash
python modelos/gerar_capa.py --autor "Seu Nome" --rodape "Faculdade · 2026" --saida capa.png
```

Para pôr a marca da sua instituição, passe `--marca caminho/para/marca.png`. O
desenho se ajusta sozinho: o arco cruza o pé da página a uma distância da borda
igual à sua própria espessura, o corpo do título preenche a largura disponível e
o subtítulo fecha exatamente na largura que o título tem.

As cores saem com `--cor-arco` e `--cor-texto`, em hexadecimal. As que vêm por
padrão são o verde e o azul da marca da UnB.

A fonte da capa é a Century Gothic, que pertence à Microsoft e não pode ser
redistribuída. O programa a usa se ela existir na máquina, e sem ela procura, em
ordem, Questrial, Jost, Didact Gothic e DejaVu Sans. Se quiser outra, ponha o
arquivo `.ttf` em `modelos/fontes/`.

## 7. O que este repositório não traz

A marca da UnB não está aqui, por ser marca institucional. Baixe a sua no sítio
da sua universidade e passe com `--marca`.

A Century Gothic também não, pela razão acima.

## 8. Sobre a estrutura do memorial

A lei que rege a promoção manda que o memorial considere ensino, pesquisa,
extensão, gestão acadêmica e produção profissional relevante. O arquivo
[`exemplo/memorial-exemplo.md`](exemplo/memorial-exemplo.md) traz uma ordem
possível, em nove seções, e o memorial do exemplo completo mostra como ela se
preenche.

Dois conselhos de quem já passou por isso. Levante os números antes de escrever
(turmas ministradas, orientações concluídas, trabalhos publicados, citações),
porque eles mudam o que se pode afirmar. E deixe os anexos com as listas
completas: é neles que a banca confere o que o texto resume.

## Licença

Os modelos, os programas e o texto deste README são de uso livre, com atribuição.

O memorial em `memorial-alexandre/` é de autoria de Alexandre Araújo Costa e
está aqui como exemplo. Reproduzir trechos dele exige a citação habitual.
