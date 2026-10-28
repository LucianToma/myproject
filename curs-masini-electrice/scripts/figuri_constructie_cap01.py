"""Desenele constructive ale capitolului 1 – Transformatorul (schematice, nu la scară)."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, FancyBboxPatch, Circle, Ellipse
from comun import C1, C2, C3, C4, C5, TEXT, TEXT2, GRILA, FUNDAL, salveaza
from modele import trepte_optime

FIER = "#c9c8c2"          # oțel electrotehnic
FIER_INCHIS = "#8f8e88"
JT, IT = C3, C2           # înfășurarea de joasă tensiune / de înaltă tensiune
ULEI = "#e7f0fb"


def eticheta(ax, text, xy, xytext, ha="left", fs=9):
    ax.annotate(text, xy=xy, xytext=xytext, color=TEXT, fontsize=fs, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))


def miez(ax, coloane, latime_col, inaltime, jug, x_stg, x_dr, latimi=None):
    """Miez cu coloane verticale (centre `coloane`) și juguri sus/jos, între x_stg și x_dr."""
    ax.add_patch(Rectangle((x_stg, 0), x_dr - x_stg, jug, facecolor=FIER, edgecolor=FIER_INCHIS, lw=1))
    ax.add_patch(Rectangle((x_stg, inaltime - jug), x_dr - x_stg, jug, facecolor=FIER, edgecolor=FIER_INCHIS, lw=1))
    for i, xc in enumerate(coloane):
        w = latimi[i] if latimi else latime_col
        ax.add_patch(Rectangle((xc - w / 2, jug), w, inaltime - 2 * jug, facecolor=FIER, edgecolor=FIER_INCHIS, lw=1))


def bobine(ax, xc, w_col, inaltime, jug, g1=0.06, t_jt=0.22, g2=0.1, t_it=0.32, h_fr=0.82):
    """Înfășurare concentrică pe o coloană (vedere frontală): JT lângă miez, ÎT la exterior."""
    h = (inaltime - 2 * jug) * h_fr
    y0 = jug + (inaltime - 2 * jug - h) / 2
    for semn in (-1, 1):
        x_jt = xc + semn * (w_col / 2 + g1) - (t_jt if semn < 0 else 0)
        ax.add_patch(Rectangle((x_jt, y0 + 0.08), t_jt, h - 0.16, facecolor=JT, edgecolor=FUNDAL, lw=0.8))
        x_it = xc + semn * (w_col / 2 + g1 + t_jt + g2) - (t_it if semn < 0 else 0)
        ax.add_patch(Rectangle((x_it, y0), t_it, h, facecolor=IT, edgecolor=FUNDAL, lw=0.8))


# --- Tipuri de miez ----------------------------------------------------------
fig, axs = plt.subplots(1, 4, figsize=(12, 3.6), gridspec_kw=dict(width_ratios=[1, 1.05, 1.5, 1.9]))
H, J = 3.0, 0.45
# (a) monofazat cu coloane: înfășurările împărțite pe cele două coloane
ax = axs[0]
miez(ax, [0.4, 2.6], 0.5, H, J, 0.15, 2.85)
for xc in (0.4, 2.6):
    bobine(ax, xc, 0.5, H, J, t_jt=0.12, t_it=0.17, g2=0.05)
ax.set_title("(a) monofazat, cu coloane", fontsize=10)
# (b) monofazat în manta: înfășurările pe coloana centrală, fluxul se întoarce prin coloanele laterale
ax = axs[1]
miez(ax, [0.2, 1.6, 3.0], 0.4, H, J, 0.0, 3.2, latimi=[0.4, 0.8, 0.4])
bobine(ax, 1.6, 0.8, H, J, t_jt=0.12, t_it=0.17, g2=0.05)
ax.set_title("(b) monofazat, în manta", fontsize=10)
# (c) trifazat cu trei coloane
ax = axs[2]
miez(ax, [0.5, 2.2, 3.9], 0.45, H, J, 0.2, 4.2)
for xc in (0.5, 2.2, 3.9):
    bobine(ax, xc, 0.45, H, J, t_jt=0.13, t_it=0.17, g2=0.05)
ax.set_title("(c) trifazat, cu trei coloane", fontsize=10)
# (d) trifazat cu cinci coloane: coloanele laterale fără înfășurări, juguri mai joase
ax = axs[3]
J5 = 0.3
miez(ax, [0.15, 1.3, 3.0, 4.7, 5.85], 0.45, H, J5, 0.0, 6.0, latimi=[0.3, 0.45, 0.45, 0.45, 0.3])
for xc in (1.3, 3.0, 4.7):
    bobine(ax, xc, 0.45, H, J5, t_jt=0.13, t_it=0.17, g2=0.05)
ax.set_title("(d) trifazat, cu cinci coloane", fontsize=10)
for ax, lim in zip(axs, ((-0.45, 3.45), (-0.2, 3.4), (-0.4, 4.6), (-0.2, 6.2))):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_ylim(-0.6, H + 0.15)
    ax.set_xlim(*lim)
fig.legend(handles=[Rectangle((0, 0), 1, 1, facecolor=FIER, edgecolor=FIER_INCHIS),
                    Rectangle((0, 0), 1, 1, facecolor=JT), Rectangle((0, 0), 1, 1, facecolor=IT)],
           labels=["miez (tole de oțel electrotehnic)", "înfășurarea de JT (lângă miez)", "înfășurarea de ÎT (la exterior)"],
           loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.02), fontsize=9)
salveaza(fig, "f01-1-tipuri-miez")

# --- Secțiunea în trepte a coloanei și îmbinările tolelor ---------------------------
th, kf = trepte_optime(7)
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(11, 3.9), gridspec_kw=dict(width_ratios=[1, 1, 1]))
a1.add_patch(Circle((0, 0), 1, fill=False, color=TEXT2, lw=1))
ths = np.concatenate([[0.0], th])
for k in range(1, len(ths)):
    w = 2 * np.cos(ths[k])
    for semn in (1, -1):
        y0, y1 = semn * np.sin(ths[k - 1]), semn * np.sin(ths[k])
        a1.add_patch(Rectangle((-w / 2, min(y0, y1)), w, abs(y1 - y0), facecolor=FIER,
                               edgecolor=FIER_INCHIS if k % 2 else TEXT2, lw=0.8))
a1.annotate("", xy=(1, -1.18), xytext=(-1, -1.18), arrowprops=dict(arrowstyle="<->", color=TEXT2, lw=0.8))
a1.text(0, -1.3, "diametrul cercului circumscris D", ha="center", va="top", color=TEXT, fontsize=9)
a1.set_title(f"(a) secțiune în 7 trepte:\numple {100 * kf:.1f} % din cerc".replace(".", ","), fontsize=10)
a1.set_xlim(-1.25, 1.25)
a1.set_ylim(-1.55, 1.2)


def colt(ax, tip):
    """Colțul miezului: coloana verticală (stânga) întâlnește jugul orizontal (sus)."""
    w = 1.0
    # contur exterior în L
    contur = Polygon([(0, 0), (0, 3), (3, 3), (3, 3 - w), (w, 3 - w), (w, 0)], closed=True,
                     facecolor=FIER, edgecolor=FIER_INCHIS, lw=1)
    ax.add_patch(contur)
    if tip == "drept":
        ax.plot([0, w], [3 - w, 3 - w], color=TEXT, lw=1.6)
    else:
        for i, d in enumerate((-0.2, 0.0, 0.2)):
            linie, = ax.plot([-1 + d, w + 1 + d], [3 - w - 1, 3 + 1], color=TEXT, lw=1.4 if i == 1 else 1.0,
                             ls="-" if i == 1 else (0, (3, 2)))
            linie.set_clip_path(contur)
    # direcția de laminare (a cristalelor) în coloană și în jug
    ax.annotate("", xy=(w / 2, 1.6), xytext=(w / 2, 0.3), arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.6))
    ax.annotate("", xy=(2.8, 3 - w / 2), xytext=(1.6, 3 - w / 2), arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.6))
    ax.set_xlim(-0.5, 3.4)
    ax.set_ylim(-0.4, 3.4)


colt(a2, "drept")
a2.set_title("(b) îmbinare dreaptă\n(fluxul traversează tola perpendicular\npe direcția de laminare)", fontsize=9.5)
colt(a3, "step-lap")
a3.set_title("(c) îmbinare la 45° în trepte (step-lap)\n(fluxul rămâne în direcția de laminare;\nrosturile straturilor sunt decalate)", fontsize=9.5)
a3.text(1.75, 0.6, "săgeți: direcția de laminare\na tolelor cu grăunți orientați", color=TEXT2, fontsize=8.5, ha="center")
for a in (a1, a2, a3):
    a.set_aspect("equal")
    a.axis("off")
fig.tight_layout()
salveaza(fig, "f01-2-sectiune-imbinari")

# --- Înfășurările: secțiune prin coloană și fereastră --------------------------------
fig, ax = plt.subplots(figsize=(8.0, 4.8))
Hf, Jf = 5.0, 0.7
ax.add_patch(Rectangle((-1.2, 0), 1.2, Hf, facecolor=FIER, edgecolor=FIER_INCHIS, lw=1))       # coloana (jumătate)
ax.add_patch(Rectangle((-1.2, -Jf), 6.4, Jf, facecolor=FIER, edgecolor=FIER_INCHIS, lw=1))     # jug jos
ax.add_patch(Rectangle((-1.2, Hf), 6.4, Jf, facecolor=FIER, edgecolor=FIER_INCHIS, lw=1))      # jug sus
ax.plot([-1.2, -1.2], [-Jf, Hf + Jf], color=TEXT2, lw=0.8, ls=(0, (6, 3)))
ax.text(-1.2, -Jf - 0.15, "axa coloanei", ha="center", va="top", color=TEXT2, fontsize=8.5)
ax.add_patch(Rectangle((0.08, 0.25), 0.07, Hf - 0.5, facecolor="#e9d8b4", edgecolor="none"))   # cilindru izolant
x = 0.25
for i in range(9):                                                                              # JT din folie
    ax.add_patch(Rectangle((x, 0.45), 0.055, Hf - 0.9, facecolor=JT, edgecolor="none"))
    x += 0.085
x_jt_fin = x
for i in range(8):                                                                              # canal de răcire + distanțiere
    ax.add_patch(Rectangle((x_jt_fin + 0.02, 0.4 + i * 0.6), 0.18, 0.12, facecolor="#e9d8b4", edgecolor="none"))
x_it = x_jt_fin + 0.32
ax.add_patch(Rectangle((x_it - 0.08, 0.25), 0.06, Hf - 0.5, facecolor="#e9d8b4", edgecolor="none"))
n_disc, h_disc, gap = 11, 0.33, 0.07
y = (Hf - (n_disc * h_disc + (n_disc - 1) * gap)) / 2
for i in range(n_disc):                                                                         # ÎT din discuri
    ax.add_patch(Rectangle((x_it, y), 1.0, h_disc, facecolor=IT, edgecolor=FUNDAL, lw=0.6))
    y += h_disc + gap
ax.add_patch(Rectangle((-1.2 + 0, 0), 0, 0, fill=False))
ax.text(4.2, Hf / 2, "fereastra miezului\n(spre coloana vecină)", ha="center", va="center", color=TEXT2, fontsize=9)
ax.add_patch(Rectangle((x_it + 1.0 + 0.1, 0.25), 0.06, Hf - 0.5, facecolor="#e9d8b4", edgecolor="none"))
eticheta(ax, "coloana miezului", (-0.6, 4.2), (-6.2, 4.6))
eticheta(ax, "cilindru izolant\n(carton electroizolant)", (0.12, 1.0), (-6.2, 1.0))
eticheta(ax, "înfășurarea JT din folie\n(spire = straturi de folie de Al sau Cu,\nseparate de hârtie)", (0.6, 2.7), (-6.2, 2.8))
eticheta(ax, "canal axial de răcire\ncu distanțiere", (x_jt_fin + 0.11, 4.65), (2.6, 6.2))
eticheta(ax, "înfășurarea ÎT din discuri (galeți)\nconectate în serie", (x_it + 0.9, 3.7), (3.3, 4.6))
eticheta(ax, "canale radiale de ulei\nîntre discuri", (x_it + 0.5, 1.62), (3.3, 0.9))
eticheta(ax, "jug", (2.0, -0.35), (3.3, -0.35))
ax.set_xlim(-6.3, 6.4)
ax.set_ylim(-0.9, 6.6)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Secțiune prin coloană și înfășurări (jumătate de fereastră, schematic)", fontsize=10)
salveaza(fig, "f01-3-infasurari")

# --- Transformatorul de distribuție în ulei – vedere de ansamblu ----------------------
fig, ax = plt.subplots(figsize=(10, 6.6))
Y_CAPAC = 4.38
ax.add_patch(Rectangle((0, 0.6), 4.4, 3.6, facecolor=ULEI, edgecolor=TEXT2, lw=1.4))            # cuva cu ulei
ax.add_patch(Rectangle((-0.15, 4.2), 4.7, 0.18, facecolor="#d9d8d3", edgecolor=TEXT2, lw=1.2))  # capacul
for x0, semn in ((-0.05, -1), (4.45, 1)):                                                        # radiatoare
    for k in range(6):
        xx = x0 + semn * (0.08 + k * 0.17)
        ax.add_patch(Rectangle((xx - 0.05, 1.0), 0.1, 2.9, facecolor="#e4e3df", edgecolor=TEXT2, lw=0.7))
    ax.plot([x0, x0 + semn * 1.05], [3.95, 3.95], color=TEXT2, lw=1.2)
    ax.plot([x0, x0 + semn * 1.05], [0.95, 0.95], color=TEXT2, lw=1.2)
# partea activă (miez și înfășurări), văzută prin cuvă – linii întrerupte
ax.add_patch(Rectangle((0.5, 1.15), 3.4, 2.6, fill=False, edgecolor=FIER_INCHIS, lw=1.2, ls=(0, (5, 3))))
for xc in (1.1, 2.2, 3.3):
    ax.add_patch(Rectangle((xc - 0.42, 1.45), 0.84, 2.0, fill=False, edgecolor=IT, lw=1.2, ls=(0, (4, 2))))
    ax.add_patch(Rectangle((xc - 0.12, 1.15), 0.24, 2.6, fill=False, edgecolor=FIER_INCHIS, lw=1.0, ls=(0, (4, 2))))
# izolatoare de trecere ÎT (3, înalte) și JT (4, scurte)
for xc in (0.7, 1.4, 2.1):
    ax.add_patch(Rectangle((xc - 0.08, Y_CAPAC), 0.16, 1.05, facecolor="#f3efe6", edgecolor=TEXT2, lw=0.8))
    for j in range(5):
        ax.add_patch(Ellipse((xc, Y_CAPAC + 0.12 + j * 0.2), 0.42, 0.12, facecolor="#f3efe6", edgecolor=TEXT2, lw=0.8))
    ax.plot([xc, xc], [Y_CAPAC + 1.05, Y_CAPAC + 1.27], color=TEXT, lw=2)
for xc in (2.65, 3.0, 3.35, 3.7):
    ax.add_patch(Rectangle((xc - 0.07, Y_CAPAC), 0.14, 0.34, facecolor="#f3efe6", edgecolor=TEXT2, lw=0.8))
    ax.plot([xc, xc], [Y_CAPAC + 0.34, Y_CAPAC + 0.5], color=TEXT, lw=2)
# conservatorul pe suporți, conducta cu releul Buchholz, filtrul de aer, indicatorul de nivel
ax.add_patch(FancyBboxPatch((3.3, 5.6), 2.3, 0.62, boxstyle="round,pad=0,rounding_size=0.3", facecolor=ULEI,
                            edgecolor=TEXT2, lw=1.2))
for xs in (3.6, 5.3):
    ax.plot([xs, xs], [Y_CAPAC if xs < 4.4 else 3.9, 5.6], color=TEXT2, lw=1.0)
ax.plot([5.3, 4.45], [3.9, 3.9], color=TEXT2, lw=1.0)
ax.plot([4.1, 4.1, 4.85, 4.85], [Y_CAPAC, 5.15, 5.15, 5.6], color=TEXT, lw=2.2)
ax.add_patch(Rectangle((4.25, 5.01), 0.34, 0.28, facecolor=C4, edgecolor=TEXT, lw=0.8))
ax.plot([5.75, 5.75], [5.3, 5.85], color=TEXT, lw=1)
ax.plot([5.6, 5.75], [5.85, 5.85], color=TEXT, lw=1)
ax.add_patch(Rectangle((5.65, 4.85), 0.2, 0.45, facecolor="#f0d9e6", edgecolor=TEXT, lw=0.8))
ax.add_patch(Rectangle((3.33, 5.75), 0.07, 0.32, facecolor="white", edgecolor=TEXT, lw=0.8))
# comutatorul de prize, termometrul, roțile, șasiul, borna de împământare, plăcuța
ax.add_patch(Circle((0.2, Y_CAPAC + 0.1), 0.1, facecolor=C5, edgecolor=TEXT, lw=0.8))
ax.add_patch(Rectangle((4.18, Y_CAPAC), 0.1, 0.22, facecolor=TEXT2, edgecolor=TEXT, lw=0.6))
for xc in (0.6, 3.8):
    ax.add_patch(Circle((xc, 0.35), 0.25, facecolor="#d9d8d3", edgecolor=TEXT2, lw=1))
ax.add_patch(Rectangle((0.15, 0.6), 4.1, 0.15, facecolor="#d9d8d3", edgecolor=TEXT2, lw=0.8))
ax.add_patch(Rectangle((1.9, 0.82), 0.6, 0.24, facecolor="white", edgecolor=TEXT2, lw=0.8))
ax.plot([4.4, 4.62], [0.85, 0.85], color=C3, lw=2.5)
eticheta(ax, "izolatoare de trecere ÎT (A, B, C)", (0.7, 5.25), (-5.9, 6.2))
eticheta(ax, "comutator de prize (manevrat fără tensiune)", (0.2, Y_CAPAC + 0.1), (-5.9, 5.2))
eticheta(ax, "cuvă cu ulei (ulei mineral sau ester)", (0.3, 3.9), (-5.9, 4.3))
eticheta(ax, "radiatoare", (-0.6, 2.6), (-5.9, 3.1))
eticheta(ax, "partea activă: miez + înfășurări", (0.62, 1.3), (-5.9, 1.9))
eticheta(ax, "plăcuța indicatoare", (1.9, 0.94), (-5.9, 1.2))
eticheta(ax, "roți și șasiu", (0.6, 0.15), (-5.9, 0.3))
eticheta(ax, "conservator (vas de expansiune a uleiului)", (4.6, 6.22), (6.3, 6.6))
eticheta(ax, "indicator de nivel al uleiului", (3.37, 5.95), (6.3, 6.2), fs=9)
eticheta(ax, "filtru de aer cu silicagel", (5.85, 5.05), (6.3, 5.05))
eticheta(ax, "releu de gaze (Buchholz) pe conducta\ndintre cuvă și conservator", (4.55, 5.15), (6.3, 5.62))
eticheta(ax, "izolatoare de trecere JT (a, b, c, n)", (3.7, 4.82), (6.3, 4.55))
eticheta(ax, "termometru (teacă în capac)", (4.25, 4.55), (6.3, 4.05))
eticheta(ax, "bornă de împământare", (4.6, 0.85), (6.3, 0.85))
ax.set_xlim(-6.0, 10.3)
ax.set_ylim(0.0, 6.9)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Transformator de distribuție în ulei, cu conservator (schematic, nu la scară)", fontsize=10)
salveaza(fig, "f01-4-transformator-ulei")
