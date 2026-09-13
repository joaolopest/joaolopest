"""Renderiza data/contributions.json como heatmap SVG animado estilo terminal."""
import json
import os
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "data" / "contributions.json"
SAIDA = RAIZ / "contrib-heatmap.svg"
ESTATICO = os.environ.get("STATIC") == "1"

PALETA = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

LARGURA = 860
ESQ = 56
DIR = 24
TOPO = 78


def maior_sequencia(dias: list[dict]) -> int:
    maior = atual = 0
    for dia in dias:
        atual = atual + 1 if dia["contagem"] > 0 else 0
        maior = max(maior, atual)
    return maior


def renderizar(dados: dict) -> str:
    dias = dados["dias"]
    primeiro = date.fromisoformat(dias[0]["data"])
    deslocamento = (primeiro.weekday() + 1) % 7  # domingo = 0

    total_colunas = (len(dias) + deslocamento + 6) // 7
    passo = (LARGURA - ESQ - DIR) / total_colunas
    celula = round(passo * 0.8, 2)

    celulas = []
    rotulos_mes = []
    mes_anterior = None
    for i, dia in enumerate(dias):
        indice = i + deslocamento
        coluna, linha = divmod(indice, 7)
        x = round(ESQ + coluna * passo, 2)
        y = round(TOPO + linha * passo, 2)
        cor = PALETA[min(dia["nivel"], 4)]
        if dia["contagem"] >= 20:
            cor = PALETA[5]
        atraso = (coluna + linha) * 0.018
        anim = (
            ""
            if ESTATICO
            else f' style="animation-delay:{0.5 + atraso:.3f}s"'
        )
        celulas.append(
            f'<rect class="c" x="{x}" y="{y}" width="{celula}" height="{celula}" rx="2.5" fill="{cor}"{anim}>'
            f'<title>{dia["data"]}: {dia["contagem"]}</title></rect>'
        )
        mes = date.fromisoformat(dia["data"]).month
        if linha == 0 and mes != mes_anterior:
            if mes_anterior is not None or coluna == 0:
                rotulos_mes.append(
                    f'<text class="dim" x="{x}" y="{TOPO - 10}">{MESES[mes - 1]}</text>'
                )
            mes_anterior = mes

    rotulos_dia = "".join(
        f'<text class="dim" x="{ESQ - 10}" y="{TOPO + l * passo + 10}" text-anchor="end">{nome}</text>'
        for l, nome in [(1, "seg"), (3, "qua"), (5, "sex")]
    )

    base = TOPO + 7 * passo + 16
    legenda_x = ESQ + total_colunas * passo - 5 * passo - 60
    legenda = f'<text class="dim" x="{legenda_x - 8}" y="{base + 10}" text-anchor="end">menos</text>'
    legenda += "".join(
        f'<rect x="{legenda_x + n * passo}" y="{base}" width="{celula}" height="{celula}" rx="2.5" fill="{PALETA[n + 1 if n else 0]}"/>'
        for n in range(5)
    )
    legenda += f'<text class="dim" x="{legenda_x + 5 * passo + 4}" y="{base + 10}">mais</text>'

    ativos = sum(1 for d in dias if d["contagem"] > 0)
    recorde = max(dias, key=lambda d: d["contagem"])
    maior = maior_sequencia(dias)
    media = dados["total"] / ativos if ativos else 0
    estatisticas = [
        ("total", f'{dados["total"]}'),
        ("dias ativos", f"{ativos}"),
        ("maior sequência", f"{maior}d"),
        ("média/dia ativo", f"{media:.1f}"),
        ("melhor dia", f'{recorde["contagem"]}'),
    ]
    rodape_y = base + 44
    rodape = ""
    coluna_largura = (LARGURA - 2 * 28) / len(estatisticas)
    for n, (rotulo, valor) in enumerate(estatisticas):
        x = 28 + n * coluna_largura
        anim = "" if ESTATICO else f' style="animation-delay:{2.2 + n * 0.12:.2f}s"'
        rodape += (
            f'<g class="ln"{anim}><text class="val" x="{x}" y="{rodape_y}">{valor}</text>'
            f'<text class="dim" x="{x}" y="{rodape_y + 18}">{rotulo}</text></g>'
        )

    altura = rodape_y + 40
    cabecalho = f'{dados["total"]} contribuições nos últimos 12 meses'
    css = """
    text{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11px}
    .dim{fill:#7d8590}.val{fill:#e6edf3;font-size:20px;font-weight:600}
    .prompt{fill:#39d353;font-size:13px}.cmd{fill:#e6edf3;font-size:13px}
    """
    if not ESTATICO:
        css += """
    .c{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .45s cubic-bezier(.2,.8,.2,1.2) forwards}
    @keyframes pop{from{opacity:0;transform:scale(.2)}to{opacity:1;transform:scale(1)}}
    .ln{opacity:0;animation:desce .5s ease-out forwards}
    @keyframes desce{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:none}}
    .cursor{animation:pisca 1s steps(1) infinite}
    @keyframes pisca{50%{opacity:0}}
    """

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{LARGURA}" height="{altura}" viewBox="0 0 {LARGURA} {altura}">
<style>{css}</style>
<rect width="{LARGURA}" height="{altura}" rx="10" fill="#0d1117" stroke="#30363d"/>
<circle cx="20" cy="18" r="5" fill="#ff5f57"/><circle cx="38" cy="18" r="5" fill="#febc2e"/><circle cx="56" cy="18" r="5" fill="#28c840"/>
<text class="dim" x="{LARGURA / 2}" y="22" text-anchor="middle">{dados["usuario"]} — contributions.sh</text>
<text class="prompt" x="28" y="50">❯</text><text class="cmd" x="44" y="50">{cabecalho} <tspan class="cursor prompt">▋</tspan></text>
{"".join(rotulos_mes)}
{rotulos_dia}
{"".join(celulas)}
{legenda}
{rodape}
</svg>
"""


if __name__ == "__main__":
    dados = json.loads(ENTRADA.read_text())
    SAIDA.write_text(renderizar(dados))
    print(f"heatmap → {SAIDA}")
