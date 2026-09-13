"""Converte data/portrait-prepped.png em retrato ASCII SVG animado.

Fundo escuro: pixel claro vira caractere denso, fundo recortado vira espaço.
Cada linha é revelada por um clip que varre da esquerda pra direita.
"""
import os
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "data" / "portrait-prepped.png"
SAIDA = RAIZ / "joao-ascii.svg"
ESTATICO = os.environ.get("STATIC") == "1"

RAMPA = " .`:-=+*cs#%@"
COLUNAS = 104
LARGURA = 370
ALTURA = 400
MARGEM = 14
TOPO = 40
LARGURA_UTIL = LARGURA - 2 * MARGEM
# faixas de brilho: índice mínimo na RAMPA → classe CSS
FAIXAS = [(1, "t1"), (4, "t2"), (7, "t3"), (10, "t4")]


def gerar_grade() -> list[str]:
    imagem = Image.open(ENTRADA).convert("L")
    proporcao_char = 0.5  # caractere monoespaçado ≈ 2x mais alto que largo
    linhas = round(COLUNAS * imagem.height / imagem.width * proporcao_char)
    pixels = np.asarray(imagem.resize((COLUNAS, linhas), Image.LANCZOS), dtype=np.float32) / 255
    indices = np.clip((pixels ** 0.75) * (len(RAMPA) - 1) + 0.5, 0, len(RAMPA) - 1).astype(int)
    indices[pixels < 0.04] = 0
    return ["".join(RAMPA[i] for i in linha).rstrip() for linha in indices]


def classe_do(caractere: str) -> str:
    indice = RAMPA.index(caractere)
    atual = ""
    for minimo, classe in FAIXAS:
        if indice >= minimo:
            atual = classe
    return atual


def colorir(linha: str) -> str:
    """Agrupa caracteres vizinhos da mesma faixa em <tspan>."""
    partes, trecho, classe_atual = [], "", None
    for caractere in linha:
        classe = classe_do(caractere)
        if classe != classe_atual and trecho:
            partes.append((classe_atual, trecho))
            trecho = ""
        classe_atual = classe
        trecho += caractere
    if trecho:
        partes.append((classe_atual, trecho))
    return "".join(
        f'<tspan class="{classe}">{escape(texto)}</tspan>' if classe else escape(texto)
        for classe, texto in partes
    )


def renderizar(grade: list[str]) -> str:
    altura_linha = (ALTURA - TOPO - MARGEM) / len(grade)
    tamanho_fonte = altura_linha * 0.98
    largura_char = LARGURA_UTIL / COLUNAS

    clips, textos = [], []
    for n, linha in enumerate(grade):
        if not linha:
            continue
        y = TOPO + (n + 1) * altura_linha
        largura_texto = len(linha) * largura_char
        atributos = (
            f'x="{MARGEM}" y="{y:.2f}" textLength="{largura_texto:.2f}" lengthAdjust="spacingAndGlyphs"'
        )
        if ESTATICO:
            textos.append(f"<text {atributos}>{colorir(linha)}</text>")
            continue
        inicio = 0.3 + n * 0.045
        clips.append(
            f'<clipPath id="l{n}"><rect x="{MARGEM}" y="{y - altura_linha:.2f}" width="0" height="{altura_linha + 1:.2f}">'
            f'<animate attributeName="width" from="0" to="{LARGURA_UTIL}" begin="{inicio:.2f}s" dur="0.4s" fill="freeze"/>'
            f"</rect></clipPath>"
        )
        textos.append(f'<text {atributos} clip-path="url(#l{n})">{colorir(linha)}</text>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{LARGURA}" height="{ALTURA}" viewBox="0 0 {LARGURA} {ALTURA}">
<style>
text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;white-space:pre}}
.arte text{{font-size:{tamanho_fonte:.2f}px}}
.dim{{fill:#7d8590;font-size:11px}}
.t1{{fill:#1d5c30}}.t2{{fill:#2ea651}}.t3{{fill:#69f0a0}}.t4{{fill:#d9ffe8}}
</style>
<defs>{"".join(clips)}</defs>
<rect width="{LARGURA}" height="{ALTURA}" rx="10" fill="#0d1117" stroke="#30363d"/>
<circle cx="20" cy="18" r="5" fill="#ff5f57"/><circle cx="38" cy="18" r="5" fill="#febc2e"/><circle cx="56" cy="18" r="5" fill="#28c840"/>
<text class="dim" x="{LARGURA / 2}" y="22" text-anchor="middle">joao.txt</text>
<g class="arte" xml:space="preserve">
{chr(10).join(textos)}
</g>
</svg>
"""


if __name__ == "__main__":
    SAIDA.write_text(renderizar(gerar_grade()))
    print(f"retrato ASCII → {SAIDA}")
