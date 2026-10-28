"""Desenele constructive ale capitolului 2 – Mașina asincronă (schematice, nu la scară)."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyBboxPatch, Wedge
from comun import C1, C2, C3, C4, C5, TEXT, TEXT2, GRILA, FUNDAL, salveaza

FIER, FIER_INCHIS = "#c9c8c2", "#8f8e88"
CARCASA = "#dcdad3"
CU, AL = C2, C1          # cupru (înfășurarea statorică), aluminiu (colivia)
IZOLATIE = "#e9d8b4"


def eticheta(ax, text, xy, xytext, ha="left", fs=9):
    ax.annotate(text, xy=xy, xytext=xytext, color=TEXT, fontsize=fs, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))


def rulment(ax, xc, yc, h=0.42, w=0.22):
    """Rulment radial cu bile (vedere în secțiune: inelele și două bile)."""
    for semn in (1, -1):
        y = yc + semn * 0.33
        ax.add_patch(Rectangle((xc - w / 2, y - h / 2), w, h, facecolor="#b9c4d0", edgecolor=TEXT2, lw=0.8))
        ax.add_patch(Circle((xc, y), 0.08, facecolor="white", edgecolor=TEXT2, lw=0.8))


# --- Vedere explodată a motorului asincron închis, ventilat exterior --------------------
fig, ax = plt.subplots(figsize=(11.5, 6.4))
Y1, Y2 = 4.9, 1.0          # axa rândului de sus (carcasă) și a rândului de jos (rotor)
for y in (Y1, Y2):
    ax.plot([-0.6, 11.6], [y, y], color=TEXT2, lw=0.8, ls=(0, (8, 3, 2, 3)))
# scutul DE (partea de antrenare)
ax.add_patch(Polygon([(0.2, Y1 - 1.05), (0.5, Y1 - 1.05), (0.5, Y1 - 0.3), (0.75, Y1 - 0.3), (0.75, Y1 + 0.3),
                      (0.5, Y1 + 0.3), (0.5, Y1 + 1.05), (0.2, Y1 + 1.05)], closed=True, facecolor=CARCASA,
                     edgecolor=TEXT2, lw=1))
# carcasa cu aripioare, statorul (secțiune) și cutia de borne
x0, x1 = 1.4, 5.4
ax.add_patch(Rectangle((x0, Y1 - 1.25), x1 - x0, 2.5, facecolor=CARCASA, edgecolor=TEXT2, lw=1.2))
for k in range(10):
    xa = x0 + 0.2 + k * 0.38
    ax.add_patch(Rectangle((xa, Y1 + 1.25), 0.12, 0.25, facecolor=CARCASA, edgecolor=TEXT2, lw=0.7))
    ax.add_patch(Rectangle((xa, Y1 - 1.5), 0.12, 0.25, facecolor=CARCASA, edgecolor=TEXT2, lw=0.7))
ax.add_patch(Rectangle((x0 + 0.5, Y1 - 0.95), x1 - x0 - 1.0, 1.9, facecolor=FIER, edgecolor=FIER_INCHIS, lw=1))
for xx in np.linspace(x0 + 0.55, x1 - 0.55, 26):
    ax.plot([xx, xx], [Y1 - 0.95, Y1 - 0.45], color=FIER_INCHIS, lw=0.5)
    ax.plot([xx, xx], [Y1 + 0.45, Y1 + 0.95], color=FIER_INCHIS, lw=0.5)
ax.add_patch(Rectangle((x0 + 0.5, Y1 - 0.45), x1 - x0 - 1.0, 0.9, facecolor=FUNDAL, edgecolor=FIER_INCHIS, lw=0.8))
for xe in (x0 + 0.15, x1 - 0.5):
    for semn in (1, -1):
        ax.add_patch(FancyBboxPatch((xe, Y1 + semn * 0.7 - 0.22), 0.35, 0.44, boxstyle="round,pad=0,rounding_size=0.12",
                                    facecolor=CU, edgecolor=FUNDAL, lw=0.8))
ax.add_patch(Rectangle((x0 + 1.4, Y1 + 1.5), 1.1, 0.55, facecolor=CARCASA, edgecolor=TEXT2, lw=1))
ax.add_patch(Rectangle((x0 + 1.32, Y1 + 2.05), 1.26, 0.12, facecolor=CARCASA, edgecolor=TEXT2, lw=1))
for xf in (x0 + 0.3, x1 - 0.9):
    ax.add_patch(Rectangle((xf, Y1 - 1.75), 0.6, 0.25, facecolor=CARCASA, edgecolor=TEXT2, lw=1))
# scutul NDE, ventilatorul și capacul ventilatorului
ax.add_patch(Polygon([(6.05, Y1 - 1.05), (6.35, Y1 - 1.05), (6.35, Y1 + 1.05), (6.05, Y1 + 1.05),
                      (6.05, Y1 + 0.3), (5.8, Y1 + 0.3), (5.8, Y1 - 0.3), (6.05, Y1 - 0.3)], closed=True,
                     facecolor=CARCASA, edgecolor=TEXT2, lw=1))
ax.add_patch(Rectangle((7.0, Y1 - 0.15), 0.25, 0.3, facecolor="#9fb3c8", edgecolor=TEXT2, lw=0.8))
for semn in (1, -1):
    ax.add_patch(Polygon([(7.05, Y1 + semn * 0.15), (7.2, Y1 + semn * 0.15), (7.5, Y1 + semn * 0.95),
                          (6.95, Y1 + semn * 0.95)], closed=True, facecolor="#9fb3c8", edgecolor=TEXT2, lw=0.8))
ax.add_patch(Polygon([(7.9, Y1 - 1.1), (9.0, Y1 - 1.1), (9.25, Y1 - 0.8), (9.25, Y1 + 0.8), (9.0, Y1 + 1.1),
                      (7.9, Y1 + 1.1)], closed=True, facecolor=CARCASA, edgecolor=TEXT2, lw=1))
for yy in np.linspace(Y1 - 0.6, Y1 + 0.6, 7):
    ax.plot([9.1, 9.25], [yy, yy], color=TEXT2, lw=1.2)
# rotorul cu arbore, colivie, rulmenți și pană
ax.add_patch(Rectangle((-0.4, Y2 - 0.2), 8.0, 0.4, facecolor="#b0b2b5", edgecolor=TEXT2, lw=1))
ax.add_patch(Rectangle((0.0, Y2 + 0.2), 0.75, 0.1, facecolor=TEXT2, edgecolor=TEXT, lw=0.6))
ax.add_patch(Rectangle((2.4, Y2 - 0.85), 2.6, 1.7, facecolor=FIER, edgecolor=FIER_INCHIS, lw=1))
for k in range(9):
    xa = 2.5 + k * 0.29
    ax.plot([xa, xa + 0.25], [Y2 - 0.85, Y2 + 0.85], color=AL, lw=1.6)
for xi in (2.25, 5.0):
    ax.add_patch(Rectangle((xi, Y2 - 0.85), 0.15, 1.7, facecolor=AL, edgecolor=FUNDAL, lw=0.8))
rulment(ax, 1.35, Y2)
rulment(ax, 6.3, Y2)
# etichete
eticheta(ax, "scut DE (partea de antrenare)", (0.35, Y1 + 0.9), (-0.6, Y1 + 2.5))
eticheta(ax, "cutie de borne", (x0 + 1.95, Y1 + 2.15), (1.9, Y1 + 2.75))
eticheta(ax, "carcasă cu aripioare de răcire\n(fontă, aluminiu sau oțel)", (x1 - 0.4, Y1 + 1.45), (3.9, Y1 + 2.6))
eticheta(ax, "scut NDE", (6.2, Y1 + 1.0), (6.4, Y1 + 2.15))
eticheta(ax, "ventilator", (7.3, Y1 + 0.85), (7.6, Y1 + 1.75))
eticheta(ax, "capacul ventilatorului\ncu grilă de aspirație", (9.2, Y1 + 0.5), (9.6, Y1 + 1.3))
eticheta(ax, "tălpi de fixare (formă IM B3)", (x0 + 0.6, Y1 - 1.7), (-0.6, Y1 - 2.35))
eticheta(ax, "pachet de tole statorice", (x0 + 2.0, Y1 - 0.75), (2.85, Y1 - 2.35))
eticheta(ax, "capete de bobină ale înfășurării\nstatorice (cupru emailat)", (x1 - 0.32, Y1 - 0.75), (5.5, Y1 - 2.35))
eticheta(ax, "capătul arborelui cu pană", (0.3, Y2 + 0.3), (-0.6, Y2 + 0.95))
eticheta(ax, "rulment DE", (1.35, Y2 - 0.55), (0.4, Y2 - 1.25))
eticheta(ax, "pachet de tole rotorice", (3.2, Y2 - 0.6), (2.2, Y2 - 1.3))
eticheta(ax, "colivie din aluminiu turnat: bare înclinate\n+ inele de scurtcircuitare", (5.07, Y2 + 0.6), (7.7, Y2 + 0.85))
eticheta(ax, "rulment NDE", (6.3, Y2 - 0.55), (7.0, Y2 - 1.25))
eticheta(ax, "arbore (oțel)", (7.3, Y2 - 0.1), (8.6, Y2 - 0.5))
ax.text(-0.6, Y1 + 0.12, "axa", color=TEXT2, fontsize=8, va="bottom")
ax.set_xlim(-0.8, 12.0)
ax.set_ylim(-0.5, Y1 + 3.0)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Motor asincron cu rotor în colivie, închis, cu ventilație exterioară – vedere explodată (schematic)",
             fontsize=10)
salveaza(fig, "f02-1-vedere-explodata")

# --- Crestătura statorică și formele crestăturilor rotorice -------------------------------
fig = plt.figure(figsize=(12, 4.6))
ax = fig.add_axes([0.0, 0.0, 0.47, 0.93])
# o crestătură semiînchisă între doi dinți; întrefierul jos
ax.add_patch(Rectangle((-2.2, -0.2), 4.4, 4.6, facecolor=FIER, edgecolor="none"))
cr = [(-0.15, -0.2), (-0.15, 0.25), (-0.75, 0.6), (-0.95, 3.6), (0.95, 3.6), (0.75, 0.6), (0.15, 0.25), (0.15, -0.2)]
ax.add_patch(Polygon(cr, closed=True, facecolor=FUNDAL, edgecolor=FIER_INCHIS, lw=1))
ax.add_patch(Polygon([(-0.72, 0.85), (-0.9, 3.5), (0.9, 3.5), (0.72, 0.85)], closed=True, facecolor="none",
                     edgecolor=IZOLATIE, lw=3))
ax.add_patch(Polygon([(-0.66, 0.62), (0.66, 0.62), (0.7, 0.82), (-0.7, 0.82)], closed=True, facecolor="#b48f5a",
                     edgecolor="none"))
ax.plot([-0.78, 0.78], [2.15, 2.15], color=IZOLATIE, lw=3)
rng = np.random.default_rng(3)
for y0, y1 in ((0.95, 2.05), (2.25, 3.4)):
    for _ in range(26):
        for _t in range(50):
            yy = rng.uniform(y0 + 0.07, y1 - 0.07)
            lim = 0.70 + (0.88 - 0.70) * (yy - 0.85) / (3.5 - 0.85) - 0.14
            xx = rng.uniform(-lim, lim)
            if all(np.hypot(xx - c.center[0], yy - c.center[1]) > 0.15 for c in ax.patches[3:] if isinstance(c, Circle)):
                ax.add_patch(Circle((xx, yy), 0.07, facecolor=CU, edgecolor="#7a3415", lw=0.4))
                break
ax.add_patch(Rectangle((-2.2, -0.75), 4.4, 0.55, facecolor=FUNDAL, edgecolor="none"))
ax.text(0, -0.5, "întrefier (spre rotor)", ha="center", color=TEXT2, fontsize=9)
eticheta(ax, "dinte", (-1.5, 2.0), (-4.5, 2.0))
eticheta(ax, "jugul statoric", (-1.2, 4.1), (-4.5, 4.1))
eticheta(ax, "izolație de crestătură", (-0.88, 3.0), (-4.5, 3.0))
eticheta(ax, "conductoare din cupru emailat\n(două straturi de bobine)", (0.3, 1.5), (2.5, 1.2))
eticheta(ax, "separator între straturi", (0.6, 2.15), (2.5, 2.3))
eticheta(ax, "pană de închidere", (0.4, 0.72), (2.5, 0.35))
eticheta(ax, "deschiderea crestăturii", (0.15, 0.1), (2.5, -0.35))
ax.set_xlim(-4.7, 6.2)
ax.set_ylim(-0.8, 4.6)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("(a) crestătură statorică semiînchisă (motor de joasă tensiune)", fontsize=10)

forme = [("(b) bară\nrotundă", [("cerc", 0, 2.5, 0.45)]),
         ("(c) bară înaltă\n(refulare)", [("poli", [(-0.12, 3.2), (0.12, 3.2), (0.18, 0.5), (-0.18, 0.5)])]),
         ("(d) colivie\ndublă", [("cerc", 0, 3.0, 0.22),
                                                             ("poli", [(-0.05, 2.78), (0.05, 2.78), (0.05, 2.2), (-0.05, 2.2)]),
                                                             ("poli", [(-0.3, 2.2), (0.3, 2.2), (0.36, 0.8), (-0.36, 0.8)])]),
         ("(e) bară în\nformă de pară", [("poli", [(-0.28, 3.1), (0.28, 3.1), (0.42, 2.6), (0.12, 0.7),
                                                                         (-0.12, 0.7), (-0.42, 2.6)])])]
for i, (titlu, elemente) in enumerate(forme):
    a = fig.add_axes([0.48 + i * 0.13, 0.08, 0.12, 0.76])
    a.add_patch(Rectangle((-0.9, 0.0), 1.8, 3.6, facecolor=FIER, edgecolor="none"))
    a.add_patch(Rectangle((-0.9, 3.6), 1.8, 0.4, facecolor=FUNDAL, edgecolor="none"))
    a.add_patch(Rectangle((-0.04, 3.38), 0.08, 0.22, facecolor=AL, edgecolor="none"))
    for el in elemente:
        if el[0] == "cerc":
            a.add_patch(Circle((el[1], el[2]), el[3], facecolor=AL, edgecolor=FUNDAL, lw=0.6))
        else:
            a.add_patch(Polygon(el[1], closed=True, facecolor=AL, edgecolor=FUNDAL, lw=0.6))
    a.text(0, 3.85, "întrefier", ha="center", color=TEXT2, fontsize=8)
    a.set_title(titlu, fontsize=9)
    a.set_xlim(-1.0, 1.0)
    a.set_ylim(-0.1, 4.1)
    a.set_aspect("equal")
    a.axis("off")
fig.text(0.74, 0.01, "crestături rotorice (aluminiu turnat în pachetul de tole); sus – suprafața dinspre întrefier",
         ha="center", color=TEXT2, fontsize=8.5)
salveaza(fig, "f02-3-crestaturi")

# --- Cutia de borne: conexiunile stea și triunghi ---------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(9.5, 4.0))
pozitii = {"W2": (0, 1), "U2": (1, 1), "V2": (2, 1), "U1": (0, 0), "V1": (1, 0), "W1": (2, 0)}
for ax, (titlu, punti) in zip(axs, (("Conexiunea stea (Y)", [("W2", "V2")]),
                                    ("Conexiunea triunghi (Δ)", [("U1", "W2"), ("V1", "U2"), ("W1", "V2")]))):
    ax.add_patch(FancyBboxPatch((-0.5, -0.5), 3.0, 2.0, boxstyle="round,pad=0,rounding_size=0.15",
                                facecolor="#efeee9", edgecolor=TEXT2, lw=1.2))
    for (a, b) in punti:
        (xa, ya), (xb, yb) = pozitii[a], pozitii[b]
        if ya == yb:
            ax.add_patch(Rectangle((xa - 0.12, ya - 0.1), xb - xa + 0.24, 0.2, facecolor="#c7a24a",
                                   edgecolor=TEXT2, lw=0.8))
        else:
            ax.add_patch(Rectangle((xa - 0.1, min(ya, yb) - 0.12), 0.2, abs(yb - ya) + 0.24, facecolor="#c7a24a",
                                   edgecolor=TEXT2, lw=0.8))
    for nume, (x, y) in pozitii.items():
        ax.add_patch(Circle((x, y), 0.17, facecolor="#d9d8d3", edgecolor=TEXT, lw=1, zorder=3))
        ax.add_patch(Circle((x, y), 0.06, facecolor=TEXT2, edgecolor="none", zorder=4))
        ax.text(x + 0.22, y + 0.2, nume, color=TEXT, fontsize=10, zorder=5)
    for x, L in ((0, "L1"), (1, "L2"), (2, "L3")):
        ax.plot([x, x], [-1.3, -0.17], color=TEXT, lw=1.6, zorder=2)
        ax.text(x, -1.45, L, ha="center", va="top", color=TEXT, fontsize=10)
    ax.set_title(titlu, fontsize=10)
    ax.set_xlim(-0.9, 2.9)
    ax.set_ylim(-1.9, 1.75)
    ax.set_aspect("equal")
    ax.axis("off")
fig.text(0.5, -0.02, "Capetele fazelor: U1–U2, V1–V2, W1–W2 (IEC 60034-8). Punțile (galbene) se mută pentru a schimba conexiunea.",
         ha="center", color=TEXT2, fontsize=9)
salveaza(fig, "f02-4-cutie-borne")
