"""Figurile capitolului 0 – Introducere."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
from comun import C1, C2, C3, C4, C5, TEXT, TEXT2, GRILA, FUNDAL, ZONA, salveaza, bloc, legatura, virgula
from modele import DATE, RN_rezistor

d = DATE


def bara_v(ax, x, y0, y1, eticheta, lw=5, culoare=TEXT, dx=0.0, dy=0.12, ha="center"):
    ax.plot([x, x], [y0, y1], color=culoare, lw=lw, solid_capstyle="butt")
    ax.text(x + dx, y1 + dy, eticheta, ha=ha, va="bottom", fontsize=10, fontweight="bold", color=TEXT)


def bara_o(ax, x0, x1, y, eticheta, lw=5, culoare=TEXT, ex=None, ey=None, ha="left"):
    ax.plot([x0, x1], [y, y], color=culoare, lw=lw, solid_capstyle="butt")
    ax.text(ex if ex is not None else x0 - 0.1, ey if ey is not None else y, eticheta, ha=ha, va="center",
            fontsize=10, fontweight="bold", color=TEXT)


def sursa(ax, x, y, r=0.28, culoare=C1):
    ax.add_patch(Circle((x, y), r, fc=FUNDAL, ec=culoare, lw=1.6))
    t = np.linspace(-0.6, 0.6, 50) * r
    ax.plot(x + t, y + 0.35 * r * np.sin(t / r * np.pi * 1.6), color=culoare, lw=1.4)


def trafo_v(ax, x, ysus, r=0.22, culoare=C2):
    ax.add_patch(Circle((x, ysus - r), r, fc="none", ec=culoare, lw=1.6))
    ax.add_patch(Circle((x, ysus - 2.4 * r), r, fc="none", ec=culoare, lw=1.6))
    return ysus - 3.4 * r


def releu(ax, x, y, nume, culoare=C5):
    ax.add_patch(FancyBboxPatch((x - 0.22, y - 0.14), 0.44, 0.28, boxstyle="round,pad=0.01,rounding_size=0.04",
                                fc=FUNDAL, ec=culoare, lw=1.3))
    ax.text(x, y, nume, ha="center", va="center", fontsize=8, color=culoare, fontweight="bold")


def intrerupator(ax, x, y, s=0.09):
    ax.add_patch(Rectangle((x - s, y - s), 2 * s, 2 * s, fc=FUNDAL, ec=TEXT, lw=1.2))


# --- Figura 0.1: rețeaua de referință ---------------------------------------
fig, ax = plt.subplots(figsize=(11, 6.6))
ax.set_xlim(-0.6, 12.2)
ax.set_ylim(-0.9, 5.6)
ax.axis("off")
y110 = 4.4
# sursa QA, bara A
sursa(ax, 0.1, y110)
ax.plot([0.38, 1.0], [y110, y110], color=TEXT, lw=1.4)
ax.text(0.1, y110 - 0.45, "QA\nS\"k = 3000 MVA", ha="center", va="top", fontsize=8.5, color=TEXT2)
bara_v(ax, 1.0, y110 - 0.5, y110 + 0.5, "A")
# linia L1
ax.plot([1.0, 5.0], [y110, y110], color=TEXT, lw=1.6)
intrerupator(ax, 1.35, y110)
intrerupator(ax, 4.65, y110)
ax.text(3.0, y110 + 0.13, "L1 – LEA 110 kV, 40 km", ha="center", va="bottom", fontsize=9, color=TEXT)
releu(ax, 1.75, y110 - 0.45, "21")
ax.plot([1.75, 1.75], [y110 - 0.31, y110 - 0.05], color=C5, lw=1.0, ls=":")
bara_v(ax, 5.0, y110 - 0.5, y110 + 0.5, "B")
# linia L2
ax.plot([5.0, 9.0], [y110, y110], color=TEXT, lw=1.6)
intrerupator(ax, 5.35, y110)
intrerupator(ax, 8.65, y110)
ax.text(7.0, y110 + 0.13, "L2 – LEA 110 kV, 30 km", ha="center", va="bottom", fontsize=9, color=TEXT)
bara_v(ax, 9.0, y110 - 0.5, y110 + 0.5, "C", dx=-0.12, ha="right")
ax.plot([9.0, 9.62], [y110, y110], color=TEXT, lw=1.4)
sursa(ax, 9.9, y110)
ax.text(9.9, y110 - 0.45, "QC\nS\"k = 1500 MVA", ha="center", va="top", fontsize=8.5, color=TEXT2)
# generatorul G1 (cap. 6–8), desenat punctat
ax.plot([9.0, 9.0], [y110 + 0.5, y110 + 0.75], color=TEXT2, lw=1.0, ls="--")
ax.text(9.15, y110 + 0.78, "centrala hidro: G1 50 MVA + TB (cap. 6–8)", ha="left", va="bottom", fontsize=8.5,
        color=TEXT2)
# transformatorul T1
ax.plot([5.0, 5.0], [y110 - 0.5, y110 - 0.75], color=TEXT, lw=1.4)
intrerupator(ax, 5.0, y110 - 0.75)
yt = trafo_v(ax, 5.0, y110 - 0.85)
ax.text(5.35, y110 - 1.15, "T1  25 MVA\n110/20 kV, YNd11\nuk = 11 %", ha="left", va="center", fontsize=8.5,
        color=TEXT)
releu(ax, 4.35, y110 - 1.15, "87T")
ax.plot([5.0, 5.0], [yt, 2.55], color=TEXT, lw=1.4)
intrerupator(ax, 5.0, 2.75)
releu(ax, 4.45, 2.75, "R0")
y20 = 2.4
bara_o(ax, 2.6, 8.8, y20, "B2 (20 kV)", ex=2.5, ha="right")
# bobina de formare a neutrului și rezistorul
xb = 3.1
ax.plot([xb, xb], [y20, y20 - 0.3], color=TEXT, lw=1.2)
ax.add_patch(Rectangle((xb - 0.22, y20 - 0.75), 0.44, 0.42, fc=FUNDAL, ec=C3, lw=1.4))
ax.text(xb, y20 - 0.54, "BPN", ha="center", va="center", fontsize=8, color=C3)
ax.plot([xb, xb], [y20 - 0.75, y20 - 0.95], color=TEXT, lw=1.2)
ax.add_patch(Rectangle((xb - 0.08, y20 - 1.45), 0.16, 0.5, fc=FUNDAL, ec=C3, lw=1.4))
ax.plot([xb - 0.2, xb + 0.2], [y20 - 1.6, y20 - 1.6], color=TEXT, lw=1.4)
ax.plot([xb, xb], [y20 - 1.45, y20 - 1.6], color=TEXT, lw=1.2)
ax.text(xb + 0.18, y20 - 1.2, f"RN = {RN_rezistor(d['U20'], d['IN_rezistor']):.1f} Ω".replace(".", ",") +
        "\n(300 A)", ha="left", va="center", fontsize=8, color=TEXT2)
# ceilalți fideri
for xf in (7.6, 8.3):
    ax.plot([xf, xf], [y20, y20 - 0.5], color=TEXT2, lw=1.2)
    intrerupator(ax, xf, y20 - 0.25)
ax.text(8.95, y20 - 0.45, "alți fideri: 37 km cablu,\n60 km LEA (capacități)", ha="left", va="center",
        fontsize=8, color=TEXT2)
# fiderul F1
xf1 = 5.8
yF = 0.7
ax.plot([xf1, xf1], [y20, yF], color=TEXT, lw=1.4)
intrerupator(ax, xf1, y20 - 0.3)
releu(ax, xf1 - 0.55, y20 - 0.3, "R1")
ax.plot([xf1, 8.2], [yF, yF], color=TEXT, lw=1.6, ls=(0, (6, 2)))
ax.plot([8.2, 11.6], [yF, yF], color=TEXT, lw=1.6)
ax.text(6.9, yF + 0.12, "3 km cablu", ha="center", va="bottom", fontsize=8.5, color=TEXT)
ax.text(8.4, yF + 0.12, "7 km LEA", ha="center", va="bottom", fontsize=8.5, color=TEXT)
bara_v(ax, 9.2, yF - 0.35, yF + 0.35, "P1", lw=4)
intrerupator(ax, 9.45, yF)
releu(ax, 9.45, yF - 0.5, "R2")
ax.text(10.3, yF + 0.12, "8 km LEA", ha="center", va="bottom", fontsize=8.5, color=TEXT)
bara_v(ax, 11.2, yF - 0.35, yF + 0.35, "P2", lw=4)
intrerupator(ax, 11.45, yF)
releu(ax, 11.45, yF - 0.5, "R3")
ax.annotate("", xy=(11.95, yF), xytext=(11.6, yF), arrowprops=dict(arrowstyle="-|>", color=TEXT, lw=1.4))
ax.text(12.0, yF, "consumator\n(50 A)", ha="left", va="center", fontsize=8, color=TEXT2)
ax.text(xf1 + 0.1, yF - 0.32, "fiderul F1 (20 kV)", ha="left", va="top", fontsize=9, color=TEXT, fontweight="bold")
ax.text(-0.5, -0.75, "□ întrerupător    ▢ releu de protecție (numerotat ca în capitolele 3–5)    "
        "– – cablu     —— linie electrică aeriană (LEA)", ha="left", va="center", fontsize=8.5, color=TEXT2)
salveaza(fig, "f00-1-retea-referinta")

# --- Figura 0.2: lanțul de protecție ----------------------------------------
fig, ax = plt.subplots(figsize=(10, 3.6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 3.6)
ax.axis("off")
bloc(ax, 0.1, 2.0, 1.8, 1.0, "Transformatoare\nde măsură\n(TC, TT)", C1)
bloc(ax, 2.6, 2.0, 2.2, 1.0, "Releu de protecție\n(măsurare, decizie,\ntemporizare)", C5)
bloc(ax, 5.5, 2.0, 1.9, 1.0, "Circuitul de\ndeclanșare (bobina\nde declanșare)", C2)
bloc(ax, 8.0, 2.0, 1.8, 1.0, "Întrerupătorul\n(stinge arcul la\ntrecerea prin zero)", C2)
for a, b in ((1.9, 2.6), (4.8, 5.5), (7.4, 8.0)):
    legatura(ax, (a, 2.5), (b, 2.5))
bloc(ax, 4.0, 0.25, 2.6, 0.8, "Sursa operativă de c.c.\n(baterie de acumulatoare)", C3)
legatura(ax, (4.6, 1.05), (3.7, 2.0))
legatura(ax, (6.0, 1.05), (6.45, 2.0))
bloc(ax, 0.1, 0.25, 3.2, 0.8, "Comunicații: teleprotecție,\nsemnalizări, SCADA (cap. 9)", C4)
legatura(ax, (2.6, 1.05), (3.2, 2.0), stil="<|-|>")
ax.text(5.0, 3.35, "timpul de eliminare a defectului = timpul releului + timpul circuitului de declanșare + "
        "timpul de întrerupere", ha="center", va="center", fontsize=9, color=TEXT)
salveaza(fig, "f00-2-lant-protectie")

# --- Figura 0.3: zone de protecție suprapuse ---------------------------------
fig, ax = plt.subplots(figsize=(10, 3.4))
ax.set_xlim(-0.3, 10.3)
ax.set_ylim(-0.7, 3.0)
ax.axis("off")
y = 1.3
sursa(ax, 0.3, y, r=0.3, culoare=C1)
ax.text(0.3, y + 0.35, "G", ha="center", va="bottom", fontsize=9, color=TEXT)
ax.plot([0.6, 1.6], [y, y], color=TEXT, lw=1.4)
trafo = 2.0
ax.add_patch(Circle((trafo - 0.18, y), 0.25, fc="none", ec=C2, lw=1.5))
ax.add_patch(Circle((trafo + 0.18, y), 0.25, fc="none", ec=C2, lw=1.5))
ax.plot([2.43, 3.8], [y, y], color=TEXT, lw=1.4)
ax.plot([4.0, 4.0], [y - 0.7, y + 0.7], color=TEXT, lw=5)
ax.plot([4.0, 9.5], [y, y], color=TEXT, lw=1.4)
for xi in (1.2, 3.5, 4.5, 9.2):
    intrerupator(ax, xi, y, s=0.1)
ax.plot([9.5, 9.9], [y, y], color=TEXT, lw=1.4)
ax.text(9.95, y, "spre\nstația\nurmătoare", ha="left", va="center", fontsize=8, color=TEXT2)
zone = [(-0.15, 1.45, "zona generatorului", C1, 0.62, "jos"), (0.95, 3.75, "zona transformatorului", C2, 0.86, "sus"),
        (3.3, 4.75, "zona barelor", C3, 0.74, "jos"), (4.25, 9.45, "zona liniei", C5, 0.86, "sus")]
for x0, x1, txt, c, h, poz in zone:
    ax.add_patch(Rectangle((x0, y - h), x1 - x0, 2 * h, fc="none", ec=c, lw=1.4, ls="--"))
    if poz == "sus":
        ax.text((x0 + x1) / 2, y + h + 0.06, txt, ha="center", va="bottom", fontsize=8.5, color=c)
    else:
        ax.text((x0 + x1) / 2, y - max(h, 0.86) - 0.08, txt, ha="center", va="top", fontsize=8.5, color=c)
ax.text(5.0, -0.6, "zonele se suprapun în jurul întrerupătoarelor: nicio porțiune a instalației nu rămâne neprotejată",
        ha="center", va="center", fontsize=9, color=TEXT2)
salveaza(fig, "f00-3-zone-protectie")

# --- Figura 0.4: redundanța (problema 0.2) ------------------------------------
pf, pu = 0.02, 0.01
sch = ["1 din 1", "1 din 2", "2 din 2", "2 din 3"]
refuz = [pf, pf**2, 1 - (1 - pf)**2, 3 * pf**2 - 2 * pf**3]
nedorit = [pu, 1 - (1 - pu)**2, pu**2, 3 * pu**2 - 2 * pu**3]
fig, ax = plt.subplots(figsize=(8, 3.8))
x = np.arange(len(sch))
ax.bar(x - 0.18, refuz, 0.34, color=C2, label="refuz de acționare (siguranța acționării)")
ax.bar(x + 0.18, nedorit, 0.34, color=C1, label="acționare nedorită (securitatea)")
ax.set_yscale("log")
ax.set_xticks(x, sch)
ax.set_ylabel("probabilitate (pe solicitare)")
ax.set_ylim(5e-5, 0.2)
ax.grid(axis="x", visible=False)
for xi, a, b in zip(x, refuz, nedorit):
    ax.text(xi - 0.18, a * 1.25, f"{a:.1e}".replace(".", ","), ha="center", va="bottom", fontsize=7.5, color=TEXT2)
    ax.text(xi + 0.18, b * 1.25, f"{b:.1e}".replace(".", ","), ha="center", va="bottom", fontsize=7.5, color=TEXT2)
ax.legend(loc="upper center", ncol=2, bbox_to_anchor=(0.5, 1.12))
ax.set_title("Protecții redundante: siguranța acționării față de securitate", pad=28)
salveaza(fig, "f00-4-redundanta")
