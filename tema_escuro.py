"""Converte um diagrama SVG do tema claro para o painel escuro da dash do Metabase.

O SVG claro continua sendo a fonte. Este script troca cada cor pela equivalente no escuro,
conforme o papel do elemento (texto, preenchimento ou traço), e põe o desenho num painel de
cantos arredondados com margem interna. O canvas mantém largura e altura, então a proporção
da imagem não muda e a altura do card na dash continua certa.

Uso: python3 tema_escuro.py <entrada.svg>  (escreve o SVG escuro no stdout)
"""
import re
import sys

PAINEL = "#101C26"  # fundo do card no Metabase escuro (v64)

# Cor de texto: tudo precisa de 4,5:1 sobre o painel e sobre a superfície das caixas.
TEXTO = {
    "#141414": "#F2F4F6",
    "#333333": "#C5CDD5",
    "#6F6F6F": "#95A1AD",
    "#827667": "#A29483",
    "#BE0380": "#E58BC1",
    "#690046": "#D9A3C6",
    "#40002D": "#F0C9E1",
    "#5B2263": "#CBA6DB",
    "#FFFFFF": "#FFFFFF",
}
# Preenchimento: superfícies claras viram tons escuros; acentos vão para a paleta da dash.
PREENCHIMENTO = {
    "#FAFAFA": PAINEL,
    "#FFFFFF": "#172430",
    "#F3F2F0": "#1E2B37",
    "#FBF0F7": "#2B1A2A",
    "#F6EEF4": "#251B29",
    "#E2D7E0": "#3E2E3C",
    "#E9E2DA": "#2F2B27",
    "#CEC6B9": "#4A5562",
    "#827667": "#A29483",
    "#A6947E": "#A29483",
    "#BE0380": "#D23095",
    "#690046": "#823468",
    "#40002D": "#823468",
    "#5B2263": "#8E4E9E",
}
# Traço: bordas neutras ficam discretas, bordas de acento seguem a paleta.
TRACO = {
    "#CEC6B9": "#3B4855",
    "#DDDDD5": "#4A5866",
    "#E9E2DA": "#4A443D",
    "#E2D7E0": "#5C4858",
    "#6F6F6F": "#6F7C89",
    "#827667": "#A29483",
    "#A6947E": "#A29483",
    "#BE0380": "#D23095",
    "#E58BC0": "#E58BC1",
    "#690046": "#A56B93",
    "#40002D": "#B0739C",
    "#5B2263": "#A777BA",
    "#FFFFFF": PAINEL,  # halo dos marcadores sobre a linha
}
PAPEL = {"fill": PREENCHIMENTO, "stroke": TRACO}

MARGEM_MIN = 12  # margem vertical mínima acrescentada, em unidades do viewBox
ESCALA_MAX = 0.94
RAIO = 18


def trocar_cores(svg):
    faltando = set()

    def tag(m):
        nome, attrs = m.group(1), m.group(2)
        texto = nome in ("text", "tspan")

        def cor(a):
            attr, hexa = a.group(1), a.group(2).upper()
            tabela = TEXTO if texto and attr == "fill" else PAPEL[attr]
            if hexa not in tabela:
                faltando.add((nome, attr, hexa))
                return a.group(0)
            return f'{attr}="{tabela[hexa]}"'

        return "<" + nome + re.sub(r'(fill|stroke)="(#[0-9A-Fa-f]{6})"', cor, attrs) + ">"

    out = re.sub(r"<(\w+)([^>]*)>", tag, svg)
    if faltando:
        sys.exit(f"cor sem equivalente no escuro: {sorted(faltando)}")
    return out


def emoldurar(svg):
    w, h = map(float, re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg).groups())
    s = min(ESCALA_MAX, 1 - 2 * MARGEM_MIN / h)
    dx, dy = w * (1 - s) / 2, h * (1 - s) / 2
    abre = re.match(r"<svg[^>]*>", svg).group(0)
    corpo = svg[len(abre):-len("</svg>")]
    corpo = re.sub(r'<rect width="[\d.]+" height="[\d.]+" fill="[^"]+"/>', "", corpo, count=1)
    defs = "".join(re.findall(r"<defs>.*?</defs>", corpo, flags=re.S))
    corpo = re.sub(r"<defs>.*?</defs>", "", corpo, flags=re.S)
    return (
        f'{abre}{defs}<rect width="{w:g}" height="{h:g}" rx="{RAIO}" fill="{PAINEL}"/>'
        f'<g transform="translate({dx:.2f} {dy:.2f}) scale({s:.4f})">{corpo}</g></svg>'
    )


if __name__ == "__main__":
    print(emoldurar(trocar_cores(open(sys.argv[1], encoding="utf-8").read())), end="")
