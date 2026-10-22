"""Gera os diagramas da dash da Alice AI (SVG) no padrão visual da dash de revisão de canais.

Uso: python3 gerar.py  ->  escreve img/<nome>.svg. O PNG 2x sai do render.sh (Chrome headless).
As imagens não levam número interno, id de card nem nome de tabela: isso fica no texto do Metabase.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent / "img"

BG, INK, BODY, MUTED = "#FAFAFA", "#141414", "#333333", "#6F6F6F"
STROKE, ARROW, WHITE = "#CEC6B9", "#827667", "#FFFFFF"
MAGENTA, BETERRABA, DARK = "#BE0380", "#690046", "#40002D"
PINK, MAUVE, NEUTRAL, ROXO = "#FBF0F7", "#E2D7E0", "#F3F2F0", "#5B2263"
FONT = "DM Sans, Helvetica, Arial, sans-serif"


def cw(ch):
    if ch == " ":
        return 0.26
    if ch in "iljI.,:;'!|":
        return 0.25
    if ch in "tfr()[]-":
        return 0.36
    if ch in "mwMW":
        return 0.82
    if ch.isupper() or ch in "×÷":
        return 0.66
    if ch.isdigit():
        return 0.56
    return 0.54


def tw(s, size, weight=400):
    return sum(cw(c) for c in s) * size * (1.05 if weight >= 600 else 1.0) * 1.1


def wrap(s, size, maxw, weight=400):
    out, cur = [], ""
    for word in s.split(" "):
        cand = (cur + " " + word).strip()
        if cur and tw(cand, size, weight) > maxw:
            out.append(cur)
            cur = word
        else:
            cur = cand
    if cur:
        out.append(cur)
    return out


class Svg:
    def __init__(self, w, h, label):
        self.w, self.h, self.label, self.p = w, h, label, []

    def rect(self, x, y, w, h, rx=12, fill=WHITE, stroke=STROKE, sw=1.2, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{st}{d}/>')

    def text(self, x, y, s, size=13, fill=BODY, weight=400, anchor="start", italic=False):
        it = ' font-style="italic"' if italic else ""
        self.p.append(
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
            f'text-anchor="{anchor}"{it}>{escape(s)}</text>'
        )

    def para(self, x, y, s, size=13, maxw=300, lh=None, **kw):
        lh = lh or size * 1.42
        for i, ln in enumerate(wrap(s, size, maxw, kw.get("weight", 400))):
            self.text(x, y + i * lh, ln, size=size, **kw)
        return y + len(wrap(s, size, maxw, kw.get("weight", 400))) * lh

    def line(self, x1, y1, x2, y2, stroke=ARROW, sw=1.4, arrow=None, dash=None):
        m = f' marker-end="url(#{arrow})"' if arrow else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{d}{m}/>')

    def path(self, d, stroke=ARROW, sw=1.3, fill="none", arrow=None, dash=None):
        m = f' marker-end="url(#{arrow})"' if arrow else ""
        ds = f' stroke-dasharray="{dash}"' if dash else ""
        self.p.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{ds}{m}/>')

    def circle(self, cx, cy, r, fill, stroke=None, sw=1.6):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{st}/>')

    def num(self, cx, cy, n, fill=DARK):
        self.circle(cx, cy, 11, fill)
        self.text(cx, cy + 4.5, str(n), size=12.5, fill=WHITE, weight=700, anchor="middle")

    def svg(self):
        def mk(i, c):
            return (f'<marker id="{i}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                    f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>')
        defs = "<defs>" + mk("ah", ARROW) + mk("ahm", MAGENTA) + mk("ahd", DARK) + "</defs>"
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" width="{self.w}" '
                f'height="{self.h}" role="img" aria-label="{escape(self.label)}" font-family="{FONT}">')
        return head + f'<rect width="{self.w}" height="{self.h}" fill="{BG}"/>' + defs + "".join(self.p) + "</svg>"

    def save(self, name):
        OUT.mkdir(exist_ok=True)
        (OUT / f"{name}.svg").write_text(self.svg(), encoding="utf-8")


def box(s, x, y, w, h, title=None, lines=(), tsize=15, bsize=13, accent=None, fill=WHITE,
        title_color=INK, pad=16, dash=None, sw=None):
    if h is None:
        need = tsize * 0.78 + (len(wrap(title, tsize, w - 2 * pad, 700)) * tsize * 1.3 + 3 if title else 0)
        for item in lines:
            txt, style = (item, "body") if isinstance(item, str) else item
            sz = bsize if style != "muted" else bsize - 0.5
            need += len(wrap(txt, sz, w - 2 * pad, 600 if style in ("bold", "accent") else 400)) * sz * 1.42
        h = round(need + pad * 1.4)
    s.rect(x, y, w, h, fill=fill, stroke=accent or STROKE, sw=sw or (1.4 if accent else 1.2), dash=dash)
    s.last_h = h
    cy = y + pad + tsize * 0.78
    if title:
        for ln in wrap(title, tsize, w - 2 * pad, 700):
            s.text(x + pad, cy, ln, size=tsize, fill=title_color, weight=700)
            cy += tsize * 1.3
        cy += 3
    for item in lines:
        txt, style = (item, "body") if isinstance(item, str) else item
        size = bsize if style != "muted" else bsize - 0.5
        color = {"body": BODY, "muted": MUTED, "bold": INK, "accent": MAGENTA}[style]
        weight = 600 if style in ("bold", "accent") else 400
        for ln in wrap(txt, size, w - 2 * pad, weight):
            s.text(x + pad, cy, ln, size=size, fill=color, weight=weight)
            cy += size * 1.42
    return cy


# --------------------------------------------------------------------------------------------
# 2. Quem tem acesso à Alice AI e em que grupo cai
def acesso_e_grupos():
    s = Svg(1200, 660, "Como o membro ganha acesso à Alice AI (sorteio da recomendação de HS, convite ao "
                       "opt-in ou Pitaya) e em qual grupo do filtro Grupo de membros ele cai.")
    s.text(20, 32, "Como o membro ganha acesso", size=15, fill=INK, weight=700)
    s.text(900, 32, "Grupo no filtro Grupo de membros", size=15, fill=INK, weight=700)

    box(s, 20, 215, 170, 90, "Base de membros", [("elegíveis ao produto", "muted")])

    box(s, 230, 56, 330, 138, "Sorteio da recomendação de HS",
        ["acontece quando o membro abre o app", ("o braço sorteado não muda depois", "muted")])
    box(s, 600, 56, 260, 64, "Tratamento", ["Alice AI com indicação de HS"],
        tsize=14.5, accent=MAGENTA, title_color=MAGENTA, pad=14)
    box(s, 600, 130, 260, 64, "Controle", ["fica no Agente 00, sem a Alice AI"], tsize=14.5, pad=14)
    s.line(560, 125, 597, 90, arrow="ah")
    s.line(560, 125, 597, 160, arrow="ah")

    box(s, 230, 226, 330, 100, "Convite ao opt-in", ["enviado a um lote da base elegível"])
    box(s, 600, 226, 260, 100, "Aceite", ["Alice AI completa", ("quem aceita escolheu aceitar", "muted")],
        tsize=14.5, accent=BETERRABA, pad=14)
    s.line(560, 276, 597, 276, arrow="ah")

    box(s, 230, 358, 630, 78, "Pitayas",
        ["colaboradores e dependentes, com acesso desde o alfa, fora do sorteio e do convite"],
        tsize=14.5, dash="5 4", pad=14)

    for ty in (125, 276, 397):
        s.line(190, 260, 227, ty, arrow="ah")

    # grupos do filtro, aninhados quando um contém o outro
    s.rect(900, 50, 280, 150, fill="#F6EEF4", stroke=BETERRABA, sw=1.2)
    s.text(916, 166, "Recomendação de HS", size=13, fill=INK, weight=600)
    s.text(916, 184, "[Controle + Tratamento]", size=13, fill=INK, weight=600)
    s.rect(914, 62, 252, 60, rx=9, fill=WHITE, stroke=MAGENTA, sw=1.4)
    s.text(930, 87, "Recomendação de HS", size=13, fill=MAGENTA, weight=600)
    s.text(930, 105, "[Tratamento]", size=13, fill=MAGENTA, weight=600)
    s.line(860, 88, 912, 88, stroke=MAGENTA, sw=1.3, arrow="ahm")
    s.line(860, 162, 898, 162, arrow="ah")

    s.rect(900, 216, 280, 120, fill="#F6EEF4", stroke=BETERRABA, sw=1.2)
    s.text(916, 320, "Base convidada ao opt-in", size=13, fill=INK, weight=600)
    s.rect(914, 228, 252, 60, rx=9, fill=WHITE, stroke=BETERRABA, sw=1.4)
    s.text(930, 263, "Base com aceite do opt-in", size=13, fill=BETERRABA, weight=600)
    s.line(860, 258, 912, 258, arrow="ah")

    s.rect(900, 358, 130, 78, rx=10, fill=WHITE, stroke=STROKE)
    s.text(916, 402, "Pitayas", size=13, fill=INK, weight=600)
    s.rect(1042, 358, 138, 78, rx=10, fill=WHITE, stroke=STROKE)
    s.text(1056, 392, "Não Pitayas", size=13, fill=INK, weight=600)
    s.text(1056, 411, "o resto da base", size=12, fill=MUTED)
    s.line(860, 397, 898, 397, arrow="ah")

    s.rect(900, 452, 280, 64, rx=10, fill=WHITE, stroke=STROKE, dash="5 4")
    s.text(916, 477, "Quem usou a indicação de HS", size=13, fill=INK, weight=600)
    s.text(916, 497, "recebeu o card, por qualquer porta", size=12, fill=MUTED)

    box(s, 20, 548, 540, 92, "Só o sorteio permite ler diferença entre grupos como efeito",
        ["No convite, quem aceita escolheu aceitar; entre Pitayas e o resto da base, o perfil é outro."],
        tsize=14.5, accent=MAGENTA, fill=PINK, title_color=MAGENTA, pad=14)
    s.rect(580, 548, 600, 92, fill=WHITE, stroke=STROKE)
    notes = ["[Controle + Tratamento] inclui convidados ao opt-in, postos no controle sem sorteio",
             "o mesmo membro pode estar em mais de um grupo",
             "Todos os membros é o filtro desligado, não um grupo"]
    for i, n in enumerate(notes):
        s.circle(598, 573 + i * 22, 2.5, ARROW)
        s.text(608, 577 + i * 22, n, size=13)
    s.save("acesso-e-grupos")


# --------------------------------------------------------------------------------------------
# 3. Quem entra na comparação de custo
def comparacao_de_custo():
    s = Svg(1200, 706, "Quem entra em cada lado da comparação de custo com e sem a Alice AI, e quais capítulos "
                       "cada opção do filtro Natureza do custo deixa no numerador.")
    s.rect(20, 16, 1160, 330, fill=WHITE, stroke=STROKE)
    s.text(40, 46, "Base com plano vigente no dia 1 do mês", size=15, fill=INK, weight=700)
    s.text(1160, 46, "é a linha Geral do gráfico por grupo", size=12.5, fill=MUTED, anchor="end")
    s.rect(44, 64, 1112, 264, fill=BG, stroke=BETERRABA, sw=1.2)
    s.text(64, 94, "Abriu algum canal no Alice Agora no mês", size=15, fill=INK, weight=700)
    s.text(1136, 94, "é o universo das comparações com e sem a Alice AI", size=12.5, fill=MUTED, anchor="end")
    box(s, 70, 114, 480, 88, "Passou pela Alice AI", ["ao menos um canal do mês teve a Alice AI"],
        accent=MAGENTA, fill=PINK, title_color=MAGENTA)
    s.text(600, 166, "×", size=26, fill=MUTED, anchor="middle")
    box(s, 650, 114, 480, 88, "Só fora da Alice AI", ["abriu canal no mês, e nenhum teve a Alice AI"])
    s.text(70, 234, "Em cada lado: custo do mês ÷ membros do lado no mês. Membro sem custo no mês entra como zero.",
           size=13.5, fill=INK, weight=600)
    s.circle(76, 264, 4, MAGENTA)
    s.text(88, 268, "controla: os dois lados buscaram atendimento no mês", size=13)
    s.circle(76, 292, 4, DARK)
    s.text(88, 296, "não controla: quem passou pela Alice AI escolheu usar; o efeito causal só sai do A/B do rollout",
           size=13)

    s.text(20, 384, "Natureza do custo: quais capítulos entram no numerador", size=15, fill=INK, weight=700)
    cols = [("Agudo de entrada", "PS, PA Digital, Triagem"),
            ("Ambulatorial", "consultas, exames, terapias"),
            ("Internação e procedimento", "uma conversa não move"),
            ("Demais capítulos", "o restante da conta")]
    x0, cwid = 330, 212
    for i, (t, sub) in enumerate(cols):
        cx = x0 + i * cwid + cwid / 2
        s.text(cx, 418, t, size=13, fill=INK, weight=700, anchor="middle")
        s.text(cx, 436, sub, size=12, fill=MUTED, anchor="middle")
    rows = [("Todo o custo", "é o CUt", [1, 1, 1, 1]),
            ("Sem internação e procedimento", None, [1, 1, 0, 1]),
            ("Só agudo de entrada", None, [1, 0, 0, 0]),
            ("Só ambulatorial", None, [0, 1, 0, 0])]
    for r, (lab, tag, cells) in enumerate(rows):
        y = 456 + r * 40
        s.text(20, y + 21, lab, size=13.5, fill=INK, weight=600)
        if tag:
            s.text(20 + tw(lab, 13.5, 600) + 10, y + 21, tag, size=12.5, fill=MAGENTA, weight=600)
        for i, on in enumerate(cells):
            cx = x0 + i * cwid + 18
            if on:
                s.rect(cx, y + 4, cwid - 36, 24, rx=6, fill=MAGENTA if r == 0 else BETERRABA, stroke=None)
            else:
                s.rect(cx, y + 4, cwid - 36, 24, rx=6, fill=NEUTRAL, stroke=STROKE, sw=1, dash="4 3")
    s.rect(330, 622, 14, 14, rx=3, fill=BETERRABA, stroke=None)
    s.text(352, 634, "entra no numerador", size=12.5, fill=MUTED)
    s.rect(500, 622, 14, 14, rx=3, fill=NEUTRAL, stroke=STROKE, sw=1, dash="4 3")
    s.text(522, 634, "fica fora", size=12.5, fill=MUTED)
    s.para(20, 668, "Fora de Todo o custo, o número é o custo do recorte, não o CUt, e não se compara com o CUt do "
                    "fórum. O custo vem da conta viva: fica um pouco acima do publicado, e meses recentes ainda "
                    "podem subir.", size=12.5, maxw=1160, fill=MUTED)
    s.save("comparacao-de-custo")


# --------------------------------------------------------------------------------------------
# 4. Anatomia de um canal: o que é uso e onde cada relógio corre
def anatomia_do_canal():
    s = Svg(1200, 600, "Linha do tempo de um canal da Alice AI: o trecho da IA, o handoff para a rota seguinte, "
                       "o que conta como uso e onde começa e termina cada tempo medido.")
    A, H, E = 150, 640, 1170  # abertura, handoff, fim
    # dimensões no topo
    s.line(A, 44, H, 44, stroke=MUTED, sw=1.1)
    for x in (A, H):
        s.line(x, 38, x, 50, stroke=MUTED, sw=1.1)
    s.text((A + H) / 2, 34, "trecho até o handoff", size=12.5, fill=MUTED, anchor="middle")
    s.line(A, 70, E, 70, stroke=MUTED, sw=1.1)
    for x in (A, E):
        s.line(x, 64, x, 76, stroke=MUTED, sw=1.1)
    s.text((H + E) / 2, 62, "conversa inteira, da abertura ao arquivamento", size=12.5, fill=MUTED, anchor="middle")

    s.text(20, 115, "Rotas", size=14, fill=INK, weight=700)
    s.rect(A, 92, H - A, 36, rx=8, fill=MAGENTA, stroke=None)
    s.text(A + 14, 115, "Alice AI", size=13.5, fill=WHITE, weight=600)
    s.rect(H, 92, E - H, 36, rx=8, fill=BETERRABA, stroke=None)
    s.text(H + 14, 115, "rota seguinte: time humano", size=13.5, fill=WHITE, weight=600)
    s.line(H, 84, H, 336, stroke=DARK, sw=1.4, dash="5 4")
    s.text(H + 8, 152, "handoff", size=12.5, fill=DARK, weight=700)
    s.text(A, 152, "abertura", size=12.5, fill=MUTED)

    s.text(20, 198, "Mensagens", size=14, fill=INK, weight=700)
    for i, t in enumerate(["M: membro", "IA: Alice AI", "H: humano"]):
        s.text(20, 218 + i * 15, t, size=11.5, fill=MUTED)
    msgs = [(185, "M"), (265, "IA"), (345, "M"), (425, "IA"), (505, "M"), (585, "IA"),
            (735, "H"), (815, "M"), (895, "H"), (975, "M"), (1055, "H")]
    pos = {}
    for k, (x, t) in enumerate(msgs):
        fill, fc, st = {"M": (WHITE, INK, STROKE), "IA": (PINK, MAGENTA, MAGENTA), "H": (MAUVE, BETERRABA, BETERRABA)}[t]
        s.rect(x - 22, 180, 44, 26, rx=13, fill=fill, stroke=st, sw=1.2)
        s.text(x, 198, t, size=12.5, fill=fc, weight=700, anchor="middle")
        pos[k] = x

    def clock(x1, x2, n):
        y = 226
        s.line(x1, y, x2, y, stroke=DARK, sw=1.4)
        s.line(x1, y - 5, x1, y + 5, stroke=DARK, sw=1.4)
        s.line(x2, y - 5, x2, y + 5, stroke=DARK, sw=1.4)
        s.num((x1 + x2) / 2, y + 22, n)
    clock(A, pos[1], 1)
    clock(pos[2], pos[3], 2)
    clock(H, pos[6], 3)
    clock(pos[7], pos[8], 4)

    s.text(20, 300, "Conta como", size=14, fill=INK, weight=700)
    s.rect(A, 280, H - A - 6, 36, rx=8, fill=PINK, stroke=MAGENTA, sw=1.2)
    s.text(A + 14, 303, "uso da Alice AI: mensagem do membro antes do handoff", size=13, fill=MAGENTA, weight=600)
    s.rect(H + 6, 280, E - H - 6, 36, rx=8, fill=NEUTRAL, stroke=STROKE, sw=1.2)
    s.text(H + 20, 303, "uso do Alice Agora, não da Alice AI", size=13, fill=BODY, weight=600)
    s.text(A, 342, "Abrir o canal não é uso: conta o membro mandar mensagem.", size=12.5, fill=MUTED)

    legend_l = [(1, "Primeira resposta", "abertura do canal até a 1ª resposta da IA"),
                (2, "Tempo entre interações", "mensagem do membro até a resposta da IA"),
                (None, "Handoff precoce ou tardio", "trecho até o handoff ÷ conversa inteira, em tempo e em mensagens")]
    legend_r = [(3, "Do handoff ao humano", "saída da IA até a 1ª resposta humana"),
                (4, "Ritmo humano", "mensagem do membro até a resposta humana, contra canal que nunca passou pela IA")]
    for col, items in ((20, legend_l), (620, legend_r)):
        for i, (n, t, d) in enumerate(items):
            y = 392 + i * 52
            if n:
                s.num(col + 11, y - 5, n)
            else:
                s.line(col + 2, y - 5, col + 20, y - 5, stroke=MUTED, sw=1.1)
            s.text(col + 32, y, t, size=14, fill=INK, weight=700)
            s.text(col + 32, y + 20, d, size=13)
    box(s, 620, 488, 560, None, "Handoff",
        ["basta existir rota seguinte à da Alice AI, mesmo que o humano não responda; acontece por pedido "
         "do membro, guardrail ou timeout da IA"],
        tsize=14, accent=DARK, title_color=DARK, pad=14)
    s.save("anatomia-do-canal")


# --------------------------------------------------------------------------------------------
# 5. Como ler o incremento
def leitura_do_incremento():
    s = Svg(1200, 608, "Matriz de leitura do incremento: total de canais contra canais com staff, cada quadrante "
                       "com o desenho esperado das duas linhas contra o baseline.")
    s.text(455, 36, "Canais com staff estáveis ou caindo", size=14.5, fill=INK, weight=700, anchor="middle")
    s.text(945, 36, "Canais com staff subindo junto", size=14.5, fill=INK, weight=700, anchor="middle")
    s.text(20, 168, "Total de canais", size=14.5, fill=INK, weight=700)
    s.text(20, 188, "sobe", size=14.5, fill=INK, weight=700)
    s.text(20, 388, "Total de canais", size=14.5, fill=INK, weight=700)
    s.text(20, 408, "estável", size=14.5, fill=INK, weight=700)
    cells = [
        (220, 56, "Incremento, o esperado",
         "mais demanda atendida com a mesma carga humana; a distância entre as linhas é o ganho", "up", "flat", True),
        (710, 56, "Carga extra", "a demanda nova chega, mas leva atendimento humano junto", "up", "up", False),
        (220, 276, "Absorção",
         "a IA passa a atender o que o humano atendia, sem demanda nova; com as duas linhas paradas, "
         "não há efeito", "flat", "down", False),
        (710, 276, "Piora", "a mesma demanda passa a pedir mais atendimento humano", "flat", "up", False),
    ]
    for x, y, t, d, canais, staff, best in cells:
        s.rect(x, y, 470, 205, fill=PINK if best else WHITE, stroke=MAGENTA if best else STROKE,
               sw=1.4 if best else 1.2)
        s.text(x + 20, y + 36, t, size=16.5, fill=MAGENTA if best else INK, weight=700)
        s.para(x + 20, y + 64, d, size=13, maxw=215)
        # minigráfico
        gx, gy, gw = x + 262, y + 30, 186
        mid = gx + 78
        s.line(mid, gy, mid, gy + 150, stroke=STROKE, sw=1, dash="2 3")
        s.text(mid, gy + 166, "início", size=11, fill=MUTED, anchor="middle")
        for lvl, how, color in ((gy + 50, canais, MAGENTA), (gy + 112, staff, BETERRABA)):
            end = {"up": lvl - 38, "flat": lvl, "down": lvl + 30}[how]
            s.line(mid, lvl, gx + gw, lvl, stroke=color, sw=1.3, dash="5 4")
            s.path(f"M{gx},{lvl} L{mid},{lvl} L{gx + gw},{end}", stroke=color, sw=2.6)
    s.path(f"M220,534 L250,534", stroke=MAGENTA, sw=2.6)
    s.text(258, 538, "canais", size=12.5, fill=MUTED)
    s.path(f"M330,534 L360,534", stroke=BETERRABA, sw=2.6)
    s.text(368, 538, "canais com staff", size=12.5, fill=MUTED)
    s.line(500, 534, 530, 534, stroke=MUTED, sw=1.3, dash="5 4")
    s.text(538, 538, "baseline de janeiro a maio", size=12.5, fill=MUTED)
    s.para(220, 570, "Ler por mil membros ativos: base que cresce sozinha sobe as duas linhas sem ser incremento. "
                     "O WAU do Alice Agora subindo confirma que a demanda nova vem de mais membros.",
           size=12.5, maxw=960, fill=MUTED)
    s.save("leitura-do-incremento")


# --------------------------------------------------------------------------------------------
# 6. A taxa de resolução da Alice AI só vê os canais que caíram
def cobertura_da_resolucao():
    s = Svg(1200, 446, "Duas populações de canais e a parte de cada uma com desfecho registrado: do lado da "
                       "Alice AI, só os canais com handoff entram na taxa de resolução.")
    X0, X1 = 300, 1180

    def bar(y, label, segs):
        s.text(20, y + 28, label, size=14.5, fill=INK, weight=700)
        x = X0
        for frac, txt, on, color in segs:
            w = (X1 - X0) * frac
            if on:
                s.rect(x, y, w - 4, 44, rx=8, fill=color, stroke=None)
                s.text(x + 16, y + 28, txt, size=13.5, fill=WHITE, weight=600)
            else:
                s.rect(x, y, w - 4, 44, rx=8, fill=NEUTRAL, stroke=STROKE, sw=1.1, dash="5 4")
                s.text(x + 16, y + 28, txt, size=13.5, fill=BODY, weight=600)
            x += w

    bar(40, "Com Alice AI", [(0.6, "contidos, sem handoff", False, None), (0.4, "com handoff", True, MAGENTA)])
    s.text(316, 108, "sem desfecho registrado: fica fora da conta", size=12.5, fill=MUTED)
    s.text(X0 + (X1 - X0) * 0.6 + 16, 108, "a taxa da Alice AI sai só daqui", size=13, fill=MAGENTA, weight=700)
    s.text(X0 + (X1 - X0) * 0.6 + 16, 126, "o desfecho é registrado no handoff", size=12.5, fill=MUTED)

    bar(168, "Sem Alice AI", [(0.75, "com desfecho registrado", True, BETERRABA), (0.25, "sem desfecho", False, None)])
    s.text(316, 236, "a taxa sem a Alice AI sai daqui", size=13, fill=BETERRABA, weight=700)

    s.rect(X0, 268, 14, 14, rx=3, fill=BETERRABA, stroke=None)
    s.text(X0 + 22, 280, "entra no denominador da taxa", size=12.5, fill=MUTED)
    s.rect(X0 + 230, 268, 14, 14, rx=3, fill=NEUTRAL, stroke=STROKE, sw=1, dash="4 3")
    s.text(X0 + 252, 280, "fica fora", size=12.5, fill=MUTED)
    s.text(X1, 280, "proporções ilustrativas", size=12, fill=MUTED, anchor="end", italic=True)

    box(s, 20, 306, 1160, None, "Os contidos, onde a Alice AI resolve sozinha, nunca entram na taxa",
        ["Do lado da Alice AI, a taxa descreve só os canais que caíram para humano, o pior subconjunto do "
         "produto. Taxa alta com cobertura baixa é amostra enviesada, e não resolução alta.",
         ("Resolvido: desfecho clínico Resolutivo ou, nos canais administrativos, resposta Sim em "
          "\"Esse atendimento resolveu sua demanda?\".", "muted")],
        tsize=15, accent=MAGENTA, fill=PINK, title_color=MAGENTA)
    s.save("cobertura-da-resolucao")


# --------------------------------------------------------------------------------------------
# 7. Da conversa à consulta
def da_conversa_a_consulta():
    s = Svg(1200, 560, "Caminho da conversa com a Alice AI até a consulta com o especialista, as pontes de dado "
                       "entre as etapas e onde começa e termina cada um dos três funis de indicação.")
    xs = [20, 210, 400, 590, 780]
    W = 160
    steps = [("Conversa", ["conversa real tem duas ou mais mensagens do membro"]),
             ("Pede uma especialidade", ["cada par canal × especialidade é uma busca"]),
             ("Indicação", []),
             ("Clique", ["ver perfil ou agendar"]),
             ("Consulta", ["na especialidade buscada, em até 30 dias"])]
    for i, (x, (t, ls)) in enumerate(zip(xs, steps)):
        box(s, x, 30, W, 126, t, ls, tsize=14.5, bsize=12.5, pad=14,
            accent=BETERRABA if i == 4 else None)
        if i < 4:
            s.line(x + W + 2, 90, xs[i + 1] - 3, 90, arrow="ah")
    for k in range(3):
        s.rect(414 + k * 44, 76, 36, 30, rx=7, fill=PINK, stroke=MAGENTA, sw=1.1)
        s.text(432 + k * 44, 96, str(k + 1), size=13, fill=MAGENTA, weight=700, anchor="middle")
    s.para(414, 132, "card com os indicados, por posição", size=12, maxw=W - 28, fill=MUTED, lh=16)

    s.line(670, 156, 670, 180, stroke=ARROW, sw=1.2, dash="3 3")
    box(s, 420, 180, 340, None, None, ["o clique não traz o canal: vai para o último canal que o membro "
                                     "abriu antes dele"], bsize=12.5, pad=14, fill=NEUTRAL)
    s.line(860, 156, 860, 180, stroke=ARROW, sw=1.2, dash="3 3")
    box(s, 780, 180, 400, None, None, ["a consulta casa pelo mesmo profissional e pela especialidade, "
                                     "na conta médica"], bsize=12.5, pad=14, fill=NEUTRAL)

    s.text(20, 290, "Três funis sobre o mesmo caminho", size=15, fill=INK, weight=700)
    centers = [x + W / 2 for x in xs]
    tracks = [("Recomendação HS · por membro", [0, 2, 3, 4], "termina em: consultou um profissional recomendado",
               MAGENTA),
              ("Direcionamento · por membro", [2, 3, 4], "termina em: consultou o profissional que clicou",
               BETERRABA),
              ("Direcionamento · por busca, canal × especialidade", [2, 3, 4],
               "termina em: consultou qualquer um dos exibidos", ROXO)]
    for r, (lab, idx, end, color) in enumerate(tracks):
        y = 340 + r * 62
        x1, x2 = centers[idx[0]], centers[idx[-1]]
        s.text(x1 - 6, y - 12, lab, size=13, fill=color, weight=700)
        s.line(x1, y, x2, y, stroke=color, sw=2.4)
        for i in idx:
            s.circle(centers[i], y, 6, WHITE, stroke=color, sw=2.2)
        s.circle(x2, y, 6, color)
        s.para(890, y + 4, end, size=12.5, maxw=290, fill=BODY)
    s.text(20, 534, "As etapas de consulta são piso: a coorte precisa de 30 dias, e a conta médica chega com atraso.",
           size=12.5, fill=MUTED)
    s.save("da-conversa-a-consulta")


# --------------------------------------------------------------------------------------------
# 8. Substituição de PS: três comparações, três respostas
def substituicao_de_ps():
    s = Svg(1200, 586, "Três comparações de substituição de PS pelo PA Digital, o que cada uma responde e o que "
                       "não responde.")
    s.text(20, 34, "Substituição = PA Digital ÷ (PA Digital + Pronto Socorro)", size=16, fill=INK, weight=700)
    s.text(1180, 34, "cada linha compara grupos diferentes", size=12.5, fill=MUTED, anchor="end")
    s.text(76, 76, "Compara", size=13, fill=MUTED, weight=700)
    s.text(580, 76, "Responde", size=13, fill=MUTED, weight=700)
    s.text(880, 76, "Não responde", size=13, fill=MUTED, weight=700)
    rows = [
        (90, 142, "Quem aceitou o opt-in contra ela mesma antes", None,
         "A substituição mudou para quem aceitou?",
         "Se a mudança veio da Alice AI: aceitar é escolha, e o aceite vem logo depois de uma piora, por isso "
         "os 30 dias anteriores saem da base."),
        (242, 142, "Convidados contra elegíveis não convidados",
         "quem separou os grupos foi a campanha, não o membro",
         "O convite moveu a substituição de quem foi convidado?",
         "O efeito em quem usa: poucos convidados aceitam, então o efeito chega diluído."),
        (394, 92, "KR de substituição na base inteira", "acompanhado na dash do KR, fora desta",
         "A meta da empresa está sendo cumprida?",
         "O papel da Alice AI: soma todos os caminhos até o PA Digital."),
    ]
    for n, (y, h, comp, sub, resp, nao) in enumerate(rows, start=1):
        s.rect(20, y, 1160, h, fill=WHITE, stroke=STROKE)
        s.num(44, y + 26, n)
        s.text(76, y + 31, comp, size=14.5, fill=INK, weight=700)
        if sub:
            s.text(76, y + 52, sub, size=12.5, fill=MUTED)
        s.para(580, y + 31, resp, size=13.5, maxw=270, fill=INK, weight=600)
        s.para(880, y + 31, nao, size=13, maxw=285)
        s.line(560, y + 14, 560, y + h - 14, stroke=STROKE, sw=1)
        s.line(860, y + 14, 860, y + h - 14, stroke=STROKE, sw=1)
    # minilinha do tempo da linha 1
    y = 90 + 66
    s.rect(76, y, 200, 32, rx=6, fill=MAUVE, stroke=None)
    s.text(88, y + 21, "linha de base", size=12.5, fill=BETERRABA, weight=600)
    s.rect(280, y, 90, 32, rx=6, fill=NEUTRAL, stroke=STROKE, sw=1, dash="4 3")
    s.text(325, y + 21, "30 dias fora", size=11.5, fill=MUTED, anchor="middle")
    s.line(374, y - 8, 374, y + 40, stroke=MAGENTA, sw=1.6)
    s.text(374, y + 54, "aceite", size=11.5, fill=MAGENTA, weight=700, anchor="middle")
    s.rect(380, y, 160, 32, rx=6, fill=MAGENTA, stroke=None)
    s.text(392, y + 21, "depois, acumulado", size=12.5, fill=WHITE, weight=600)
    # minigráfico da linha 2
    y0 = 242 + 74
    s.line(300, y0 - 10, 300, y0 + 40, stroke=MAGENTA, sw=1.6)
    s.text(306, y0 - 2, "convite", size=11.5, fill=MAGENTA, weight=700)
    s.path(f"M76,{y0 + 8} L140,{y0 + 4} L200,{y0 + 10} L300,{y0 + 6} L540,{y0 + 6}", stroke=MAGENTA, sw=2.4)
    s.path(f"M76,{y0 + 26} L140,{y0 + 22} L200,{y0 + 28} L300,{y0 + 24} L540,{y0 + 24}", stroke=BETERRABA, sw=2.4)
    s.text(76, y0 + 50, "antes do convite, as linhas andam juntas", size=11.5, fill=MUTED)
    s.text(420, y0 - 2, "convidados", size=11.5, fill=MAGENTA, weight=600, anchor="middle")
    s.text(420, y0 + 42, "não convidados", size=11.5, fill=BETERRABA, weight=600, anchor="middle")

    box(s, 20, 500, 1160, None, "Nenhuma das três mede o efeito causal da Alice AI em quem usa",
        ["Isso pede um braço sorteado, que hoje só existe na recomendação de HS."],
        tsize=15, accent=MAGENTA, fill=PINK, title_color=MAGENTA, pad=14)
    s.save("substituicao-de-ps")


# --------------------------------------------------------------------------------------------
# 9. Árvore de métricas do teste da recomendação
def arvore_do_teste():
    s = Svg(1200, 566, "Árvore de métricas do teste da recomendação de HS: a métrica principal, os dois guardrails "
                       "e as leituras de substituição, com o papel de cada uma.")
    s.rect(250, 20, 700, 62, fill=WHITE, stroke=DARK, sw=1.4)
    s.text(600, 57, "A recomendação leva consultas para HS priorizados sem custo a mais?", size=16.5, fill=INK,
           weight=700, anchor="middle")
    xs = [20, 315, 610, 905]
    W = 275
    s.line(600, 82, 600, 104, stroke=ARROW, sw=1.3)
    s.line(xs[0] + W / 2, 104, xs[3] + W / 2, 104, stroke=ARROW, sw=1.3)
    for x in xs:
        s.line(x + W / 2, 104, x + W / 2, 128, stroke=ARROW, sw=1.3, arrow="ah")
    branches = [
        ("Principal", "decide o teste", MAGENTA, "Share de consultas em HS priorizado",
         ["tratamento contra controle", ("é a pergunta do teste em um número", "muted")]),
        ("Guardrail de custo", "pode pausar o teste", BETERRABA, "Custo de consulta com especialista",
         ["por membro, tratamento contra controle",
          "se o tratamento descolar para cima, pausa, mesmo com a principal boa",
          ("limiar ainda em aberto", "muted")]),
        ("Guardrail de perdedores", "pode pausar o teste", BETERRABA, "Concentração nos mais recomendados",
         ["quantos profissionais a feature recomenda e quanto fica com os cinco mais recomendados",
          "se subir de forma sustentada, o ranking virou funil",
          ("limiar ainda em aberto", "muted")]),
        ("Substituição", "explica o resultado", ROXO, "A feature cria valor ou só desloca?",
         ["pedido de indicação no SI, tratamento contra controle",
          "rotas até o especialista: feature, canal humano e rede",
          "caminho que levou a cada consulta",
          ("só a primeira compara braços; as outras duas descrevem quem tem acesso", "muted")]),
    ]
    for x, (kind, role, color, title, ls) in zip(xs, branches):
        s.rect(x, 130, W, 318, fill=WHITE, stroke=STROKE)
        pw = tw(kind, 12.5, 700) + 26
        s.rect(x + 16, 146, pw, 26, rx=13, fill=color, stroke=None)
        s.text(x + 28, 164, kind, size=12.5, fill=WHITE, weight=700)
        s.text(x + 16, 194, role, size=12.5, fill=color, weight=600)
        cy = s.para(x + 16, 224, title, size=15, maxw=W - 32, fill=INK, weight=700, lh=20) + 6
        for item in ls:
            txt, style = (item, "body") if isinstance(item, str) else item
            if style == "body":
                s.circle(x + 20, cy - 4, 2.5, ARROW)
                cy = s.para(x + 30, cy, txt, size=13, maxw=W - 46) + 6
            else:
                cy = s.para(x + 16, cy + 2, txt, size=12.5, maxw=W - 32, fill=MUTED) + 6
    box(s, 20, 466, 1160, None, "Comum aos quatro: a comparação é entre braços sorteados",
        ["Poucos sorteados acionam a feature, então o efeito chega diluído na comparação entre braços, "
         "e os cards ainda não acusam nada por desenho, e não por defeito."],
        tsize=15, accent=DARK, title_color=DARK, pad=14)
    s.save("arvore-do-teste")


# --------------------------------------------------------------------------------------------
# 10. Lembrete e linha do tempo do teste de lançamento (Resumo)
def linha_do_tempo():
    import datetime as dt
    W, H = 1200, 262
    s = Svg(W, H, "Lembrete: os números do teste de lançamento já aparecem, mas cada leitura só vale quando amadurece. "
                  "Linha do tempo com as datas estimadas de maturação: início em 21/10, 10 mil no tratamento por volta "
                  "de 06/11, primeira leitura por volta de 07/12, leitura principal por volta de 04/01 e custo e "
                  "desfechos por volta de 08/03.")
    s.text(24, 36, "Lembrete: os números já aparecem, mas cada leitura só vale quando amadurece", size=18, fill=INK, weight=700)
    s.text(24, 60, "As datas são estimativas de maturação da leitura e podem se mover com o ritmo de entrada no teste.",
           size=13.5, fill=MUTED)
    ini, fim = dt.date(2026, 10, 21), dt.date(2027, 3, 8)
    x0, x1, y = 44, 1156, 152
    X = lambda d: x0 + (d - ini).days / (fim - ini).days * (x1 - x0)
    xp = X(dt.date(2027, 1, 4))
    s.rect(x0, 98, xp - x0, 30, rx=15, fill=PINK, stroke=None)
    s.text(x0 + 16, 118, "Acompanhamento: a diferença ainda pode mudar de lado", size=13, fill=BETERRABA, weight=600)
    s.rect(xp, 98, x1 - xp, 30, rx=15, fill=NEUTRAL, stroke=None)
    s.text(xp + 16, 118, "Custo e desfechos seguem amadurecendo", size=13, fill=MUTED, weight=600)
    s.line(x0, y, x1, y, stroke=STROKE, sw=3)
    marcos = [
        (dt.date(2026, 10, 21), "21/10", "Início do teste", None, DARK, 7, "start"),
        (dt.date(2026, 11, 6), "~06/11", "10 mil no tratamento", None, MAUVE, 6, "start"),
        (dt.date(2026, 12, 7), "~07/12", "Primeira leitura", "uso nas semanas 2 a 4", MAGENTA, 8, "middle"),
        (dt.date(2027, 1, 4), "~04/01", "Leitura principal", "decide o teste", MAGENTA, 11, "middle"),
        (dt.date(2027, 3, 8), "~08/03", "Custo e desfechos", "CUt, PS e internação", BETERRABA, 8, "end"),
    ]
    for d, data, titulo, sub, cor, r, ancora in marcos:
        x = X(d)
        if cor == MAGENTA and r < 10:
            s.circle(x, y, r, WHITE, stroke=MAGENTA, sw=3)
        else:
            s.circle(x, y, r, cor, stroke=WHITE if cor == MAUVE else None, sw=0)
        tx = x - (r if ancora == "start" else -r if ancora == "end" else 0)
        s.text(tx, y + 34, data, size=15, fill=cor if cor != MAUVE else MUTED, weight=700, anchor=ancora)
        s.text(tx, y + 54, titulo, size=13.5, fill=INK, weight=600, anchor=ancora)
        if sub:
            s.text(tx, y + 72, sub, size=12.5, fill=MUTED, anchor=ancora)
    s.save("linha-do-tempo-do-teste")


# --------------------------------------------------------------------------------------------
# 11. Linha do tempo compacta, para a coluna da esquerda do topo do Resumo (15 de 24 colunas, 3 linhas)
def linha_do_tempo_compacta():
    import datetime as dt
    W, H = 1000, 188
    s = Svg(W, H, "Lembrete: os números já aparecem, mas cada leitura só vale quando amadurece. Datas estimadas: "
                  "início em 21/10, primeira leitura por volta de 07/12, leitura principal por volta de 04/01 e custo "
                  "e desfechos por volta de 08/03.")
    s.text(8, 30, "Lembrete: os números já aparecem, mas cada leitura só vale quando amadurece", size=21, fill=INK, weight=700)
    s.text(8, 58, "Datas estimadas de maturação da leitura", size=16, fill=MUTED)
    ini, fim = dt.date(2026, 10, 21), dt.date(2027, 3, 8)
    x0, x1, y = 22, 978, 104
    X = lambda d: x0 + (d - ini).days / (fim - ini).days * (x1 - x0)
    xp = X(dt.date(2027, 1, 4))
    s.line(x0, y, xp, y, stroke="#E58BC0", sw=5)
    s.line(xp, y, x1, y, stroke="#DDDDD5", sw=5)
    marcos = [
        (dt.date(2026, 10, 21), "21/10", "Início", DARK, 8, "start"),
        (dt.date(2026, 12, 7), "~07/12", "Primeira leitura", MAGENTA, 8, "middle"),
        (dt.date(2027, 1, 4), "~04/01", "Leitura principal", MAGENTA, 12, "middle"),
        (dt.date(2027, 3, 8), "~08/03", "Custo e desfechos", BETERRABA, 8, "end"),
    ]
    for d, data, titulo, cor, r, ancora in marcos:
        x = X(d)
        s.circle(x, y, r, cor)
        tx = x - (r if ancora == "start" else -r if ancora == "end" else 0)
        s.text(tx, y + 40, data, size=19, fill=cor, weight=700, anchor=ancora)
        s.text(tx, y + 66, titulo, size=17, fill=INK, weight=600, anchor=ancora)
    s.save("linha-do-tempo-compacta")


if __name__ == "__main__":
    for f in (acesso_e_grupos, comparacao_de_custo, anatomia_do_canal, leitura_do_incremento,
              cobertura_da_resolucao, da_conversa_a_consulta, substituicao_de_ps, arvore_do_teste, linha_do_tempo,
              linha_do_tempo_compacta):
        f()
    print("ok:", sorted(p.name for p in OUT.glob("*.svg")))
