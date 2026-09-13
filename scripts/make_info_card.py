"""Gera info-card.svg: card estilo neofetch com linhas que entram em sequência.

Edite LINHAS pra atualizar o conteúdo. STATIC=1 gera versão congelada.
"""
import os
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "info-card.svg"
ESTATICO = os.environ.get("STATIC") == "1"

LARGURA = 490
ALTURA = 400
ESQ = 24
COLUNA_VALOR = 104

USUARIO = "joaolopest@github"
LINHAS = [
    ("Nome", "João Lopes"),
    ("Papel", "Full-Stack · Co-founder @ ZenixCode"),
    ("Local", "Aracaju-SE, Brasil"),
    ("Agora", "Simulados SEDU — plataforma estadual c/ IA"),
    ("Antes", "Painel Realtime · Porto Digital · CajuHub"),
    ("Front", "React · Next.js · TypeScript · Tailwind"),
    ("Motion", "Framer Motion · GSAP"),
    ("Back", "Node · Fastify · Hono · Prisma"),
    ("Dados", "PostgreSQL · MySQL · Supabase"),
    ("Infra", "Docker · Coolify · Nginx · VPS"),
    ("IA", "Claude API · OpenAI · prompt engineering"),
    ("Aberto a", "CLT BR · remoto global · freelance"),
    ("Mantra", "Motion é interface, não decoração."),
]
CORES_PALETA = ["#0d1117", "#ff5f57", "#febc2e", "#28c840", "#39d353", "#58a6ff", "#bc8cff", "#e6edf3"]


def animacao(ordem: int) -> str:
    return "" if ESTATICO else f' style="animation-delay:{0.35 + ordem * 0.11:.2f}s"'


def renderizar() -> str:
    y = 52
    blocos = [
        f'<g class="ln"{animacao(0)}><text class="prompt" x="{ESQ}" y="{y}">❯</text>'
        f'<text class="val" x="{ESQ + 16}" y="{y}">neofetch</text></g>'
    ]
    y += 30
    blocos.append(
        f'<g class="ln"{animacao(1)}><text class="titulo" x="{ESQ}" y="{y}">{USUARIO}</text>'
        f'<text class="dim" x="{ESQ}" y="{y + 14}">{"─" * len(USUARIO)}</text></g>'
    )
    y += 34
    for n, (chave, valor) in enumerate(LINHAS):
        blocos.append(
            f'<g class="ln"{animacao(n + 2)}><text class="chave" x="{ESQ}" y="{y}">{escape(chave)}</text>'
            f'<text class="val" x="{COLUNA_VALOR}" y="{y}">{escape(valor)}</text></g>'
        )
        y += 19.5

    y += 4
    quadrados = "".join(
        f'<rect x="{ESQ + i * 26}" y="{y}" width="22" height="12" rx="2" fill="{cor}" stroke="#30363d"/>'
        for i, cor in enumerate(CORES_PALETA)
    )
    blocos.append(f'<g class="ln"{animacao(len(LINHAS) + 2)}>{quadrados}</g>')
    cursor_x = ESQ + len(CORES_PALETA) * 26 + 6
    blocos.append(f'<rect class="cursor" x="{cursor_x}" y="{y}" width="8" height="13" fill="#39d353"/>')

    css = """
    text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px}
    .dim{fill:#484f58}.val{fill:#e6edf3}.chave{fill:#39d353;font-weight:600}
    .titulo{fill:#69f0a0;font-weight:700;font-size:14px}.prompt{fill:#39d353}
    .barra{fill:#7d8590;font-size:11px}
    """
    if not ESTATICO:
        css += """
    .ln{opacity:0;animation:entra .45s ease-out forwards}
    @keyframes entra{from{opacity:0;transform:translateX(-10px)}to{opacity:1;transform:none}}
    .cursor{animation:pisca 1s steps(1) infinite}
    @keyframes pisca{50%{opacity:0}}
    """

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{LARGURA}" height="{ALTURA}" viewBox="0 0 {LARGURA} {ALTURA}">
<style>{css}</style>
<rect width="{LARGURA}" height="{ALTURA}" rx="10" fill="#0d1117" stroke="#30363d"/>
<circle cx="20" cy="18" r="5" fill="#ff5f57"/><circle cx="38" cy="18" r="5" fill="#febc2e"/><circle cx="56" cy="18" r="5" fill="#28c840"/>
<text class="barra" x="{LARGURA / 2}" y="22" text-anchor="middle">~/joaolopest — zsh</text>
{chr(10).join(blocos)}
</svg>
"""


if __name__ == "__main__":
    SAIDA.write_text(renderizar())
    print(f"card → {SAIDA}")
