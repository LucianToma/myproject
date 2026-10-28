"""Desenele constructive ale capitolului 3 – Generatorul sincron (schematice, nu la scară)."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyBboxPatch
from comun import C1, C2, C3, C4, C5, TEXT, TEXT2, GRILA, FUNDAL, salveaza

FIER, FIER_INCHIS = "#c9c8c2", "#8f8e88"
OTEL = "#b0b2b5"
CU = C2
IZOLATIE = "#e9d8b4"
MICA = "#d8c7a3"


def eticheta(ax, text, xy, xytext, ha="left", fs=9):
    ax.annotate(text, xy=xy, xytext=xytext, color=TEXT, fontsize=fs, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))


# --- Rotorul unui turbogenerator (vedere laterală) ---------------------------------------
fig, ax = plt.subplots(figsize=(11.5, 4.6))
ax.plot([-0.5, 12.3], [0, 0], color=TEXT2, lw=0.8, ls=(0, (8, 3, 2, 3)))
ax.add_patch(Rectangle((-0.3, -0.3), 12.3, 0.6, facecolor=OTEL, edgecolor=TEXT2, lw=1))           # arborele
ax.add_patch(Rectangle((-0.3, -0.9), 0.25, 1.8, facecolor=OTEL, edgecolor=TEXT2, lw=1))           # flanșa de cuplaj
ax.add_patch(Rectangle((2.6, -1.1), 5.6, 2.2, facecolor=OTEL, edgecolor=TEXT2, lw=1.2))           # corpul rotorului
for y in np.linspace(-0.95, 0.95, 9):                                                              # crestăturile (pene)
    if abs(y) < 0.3:
        continue
    ax.plot([2.65, 8.15], [y, y], color=FIER_INCHIS, lw=1.0)
ax.add_patch(Rectangle((2.6, -0.28), 5.6, 0.56, facecolor="#c4c6c9", edgecolor="none"))
ax.text(5.4, 0, "zona polului (fără crestături)", ha="center", va="center", color=TEXT2, fontsize=8.5)
for xr in (1.75, 8.2):                                                                             # inelele de bandaj
    ax.add_patch(FancyBboxPatch((xr, -1.18), 0.85, 2.36, boxstyle="round,pad=0,rounding_size=0.1",
                                facecolor=C5, edgecolor=TEXT2, lw=1, alpha=0.85))
for xv in (1.35, 9.25):                                                                            # ventilatoarele axiale
    for semn in (1, -1):
        ax.add_patch(Polygon([(xv, semn * 0.3), (xv + 0.25, semn * 0.3), (xv + 0.35, semn * 1.05),
                              (xv - 0.1, semn * 1.05)], closed=True, facecolor="#9fb3c8", edgecolor=TEXT2, lw=0.8))
for xl in (0.5, 10.3):                                                                             # lagărele cu alunecare
    for semn in (1, -1):
        ax.add_patch(Rectangle((xl, semn * 0.3 - (0.35 if semn < 0 else 0)), 0.55, 0.35, facecolor="#e8d9a8",
                               edgecolor=TEXT2, lw=0.8))
for xi in (11.1, 11.45):                                                                           # inelele colectoare
    ax.add_patch(Rectangle((xi, -0.5), 0.2, 1.0, facecolor="#c7a24a", edgecolor=TEXT2, lw=0.8))
    ax.add_patch(Rectangle((xi + 0.02, 0.5), 0.16, 0.25, facecolor=TEXT2, edgecolor=TEXT, lw=0.6))
ax.annotate("", xy=(2.6, -1.55), xytext=(8.2, -1.55), arrowprops=dict(arrowstyle="<->", color=TEXT2, lw=0.8))
ax.text(5.4, -1.7, "lungimea activă (mare)", ha="center", va="top", color=TEXT, fontsize=9)
ax.annotate("", xy=(8.55, -1.1), xytext=(8.55, 1.1), arrowprops=dict(arrowstyle="<->", color=TEXT2, lw=0.8))
eticheta(ax, "flanșă de cuplaj\ncu turbina", (-0.2, 0.7), (-0.5, 2.35))
eticheta(ax, "lagăr cu alunecare\n(ulei sub presiune)", (0.75, -0.6), (-0.5, -2.45))
eticheta(ax, "ventilator", (1.45, -0.9), (1.5, -1.75))
eticheta(ax, "inel de bandaj nemagnetic\n(oțel 18Mn18Cr) peste capetele\nînfășurării de excitație", (2.2, 1.15), (1.5, 2.35))
eticheta(ax, "corpul rotorului: forjat dintr-o bucată\n(oțel aliat), cu crestături frezate\nînchise cu pene", (6.5, 0.7), (5.3, 2.35))
eticheta(ax, "diametrul\n(limitat de forța\ncentrifugă)", (8.55, -0.6), (9.0, -1.75))
eticheta(ax, "inele colectoare și perii\n(sau excitatoare fără perii)", (11.3, 0.62), (9.4, 2.35))
ax.set_xlim(-0.6, 12.6)
ax.set_ylim(-2.9, 3.0)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Rotorul unui turbogenerator cu 2 poli (vedere laterală, schematic)", fontsize=10)
salveaza(fig, "f03-3-rotor-turbo")

# --- Polul aparent al unui hidrogenerator --------------------------------------------------
fig, ax = plt.subplots(figsize=(8.8, 5.6))
R_jg = 4.0
t = np.linspace(np.radians(70), np.radians(110), 100)
jg = [(R_jg * np.cos(a), R_jg * np.sin(a)) for a in t] + [((R_jg + 0.8) * np.cos(a), (R_jg + 0.8) * np.sin(a)) for a in t[::-1]]
ax.add_patch(Polygon(jg, closed=True, facecolor=FIER, edgecolor=FIER_INCHIS, lw=1))                # janta (secțiune)
coada = [(-0.55, 4.2), (0.55, 4.2), (0.35, 4.75), (-0.35, 4.75)]
ax.add_patch(Polygon(coada, closed=True, facecolor="#b9b8b2", edgecolor=TEXT2, lw=0.8))           # coada de rândunică
ax.add_patch(Rectangle((-0.35, 4.75), 0.7, 2.3, facecolor=FIER, edgecolor=FIER_INCHIS, lw=1))      # corpul polului
talpa = [(-1.25, 7.05), (1.25, 7.05), (1.15, 7.55)] + [(1.05 * np.cos(a) * 1.0, 7.55 + 0.12 * np.sin(np.pi * (a + 1.05) / 2.1))
                                                       for a in np.linspace(1.05, -1.05, 30)] + [(-1.15, 7.55)]
ax.add_patch(Polygon(talpa, closed=True, facecolor=FIER, edgecolor=FIER_INCHIS, lw=1))             # talpa polară
for x in np.linspace(-0.85, 0.85, 7):                                                              # barele coliviei de amortizare
    ax.add_patch(Circle((x, 7.45 + 0.1 * np.cos(x)), 0.07, facecolor=C1, edgecolor="none"))
for semn in (-1, 1):                                                                               # bobina polară
    x0 = semn * 0.4 - (0.55 if semn < 0 else 0)
    ax.add_patch(Rectangle((x0, 5.0), 0.55, 1.95, facecolor=CU, edgecolor=FUNDAL, lw=0.8))
    for y in np.linspace(5.15, 6.8, 9):
        ax.plot([x0 + 0.03, x0 + 0.52], [y, y], color="#b04a22", lw=0.6)
t2 = np.linspace(np.radians(78), np.radians(102), 60)
ax.plot(8.0 * np.cos(t2) * 0 + np.linspace(-1.9, 1.9, 60), np.full(60, 7.95), color=TEXT2, lw=0.8, ls=(0, (4, 3)))
ax.text(0, 8.05, "întrefier (spre stator)", ha="center", va="bottom", color=TEXT2, fontsize=9)
eticheta(ax, "talpa polară (tole)", (1.1, 7.25), (2.2, 7.6))
eticheta(ax, "bare ale înfășurării de amortizare\n(colivie, scurtcircuitate la capete)", (0.7, 7.5), (2.2, 8.4))
eticheta(ax, "bobina de excitație (cupru)", (0.7, 6.0), (2.2, 6.4))
eticheta(ax, "corpul polului (tole strânse)", (0.2, 5.5), (2.2, 5.5))
eticheta(ax, "fixare în coadă de rândunică", (0.45, 4.5), (2.2, 4.6))
eticheta(ax, "janta rotorului (pachet de segmente\nde tablă), legată de butuc prin brațe", (-1.0, 4.4), (-6.0, 4.0))
ax.set_xlim(-6.2, 5.4)
ax.set_ylim(3.6, 8.9)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Polul aparent al unui hidrogenerator (secțiune transversală, schematic)", fontsize=10)
salveaza(fig, "f03-4-pol-aparent")

# --- Crestătura statorică cu două bare (generator de înaltă tensiune) ----------------------
fig = plt.figure(figsize=(11.5, 4.8))
ax = fig.add_axes([0.0, 0.0, 0.52, 0.93])
ax.add_patch(Rectangle((-2.0, 0.0), 4.0, 6.6, facecolor=FIER, edgecolor="none"))
ax.add_patch(Rectangle((-0.75, 0.0), 1.5, 6.0, facecolor=FUNDAL, edgecolor=FIER_INCHIS, lw=1))
ax.add_patch(Rectangle((-2.0, -0.5), 4.0, 0.5, facecolor=FUNDAL, edgecolor="none"))


def bara(ax, y0, h=2.4):
    ax.add_patch(Rectangle((-0.68, y0), 1.36, h, facecolor="#4a4a48", edgecolor="none"))             # anti-efluviu
    ax.add_patch(Rectangle((-0.62, y0 + 0.06), 1.24, h - 0.12, facecolor=MICA, edgecolor="none"))     # izolația principală
    for col in (-0.27, 0.03):
        for k in range(8):
            ax.add_patch(Rectangle((col, y0 + 0.25 + k * (h - 0.5) / 8), 0.24, (h - 0.5) / 8 - 0.05,
                                   facecolor=CU, edgecolor="#7a3415", lw=0.5))


bara(ax, 3.4)
bara(ax, 0.75)
ax.add_patch(Rectangle((-0.7, 3.17), 1.4, 0.2, facecolor=IZOLATIE, edgecolor="none"))
ax.add_patch(Rectangle((-0.75, 0.25), 1.5, 0.4, facecolor="#b48f5a", edgecolor="none"))
ax.text(0, -0.25, "întrefier (spre rotor)", ha="center", color=TEXT2, fontsize=9)
eticheta(ax, "fire elementare de cupru izolate\n(două coloane, transpuse Roebel)", (0.27, 4.95), (1.5, 5.15))
eticheta(ax, "izolație principală: bandă de mică\nimpregnată cu rășină epoxidică", (0.55, 5.6), (1.5, 6.3))
eticheta(ax, "strat de protecție anti-efluviu\n(semiconductor)", (0.66, 4.0), (1.5, 3.9))
eticheta(ax, "bara superioară", (-0.7, 4.6), (-4.6, 4.6))
eticheta(ax, "distanțier între bare", (-0.5, 3.27), (-4.6, 3.3))
eticheta(ax, "bara inferioară", (-0.7, 1.9), (-4.6, 2.0))
eticheta(ax, "pană de crestătură", (-0.5, 0.45), (-4.6, 0.7))
eticheta(ax, "miez statoric (tole)", (1.5, 1.6), (1.5, 0.3))
ax.set_xlim(-4.8, 5.3)
ax.set_ylim(-0.5, 6.8)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("(a) crestătură deschisă cu două bare (secțiune)", fontsize=10)
# (b) principiul transpoziției Roebel: fiecare fir trece prin toate pozițiile din crestătură
ax = fig.add_axes([0.55, 0.12, 0.44, 0.75])
n, L = 6, 12.0
for col, x_ofs in ((0, 0), (1, 0)):
    pass
ax.add_patch(Rectangle((0, 0), L, n, facecolor="#f3e2d6", edgecolor=TEXT2, lw=0.8))
ax.plot([0, L], [n / 2, n / 2], color=TEXT2, lw=0.6)
# traseul unui fir: urcă în coloana de jos, trece în coloana de sus, coboară, revine (360° de-a lungul barei)
pts = [(0, 0.5), (L / 4, 2.5), (L / 4 + 0.4, 3.5), (L / 2, 5.5), (3 * L / 4, 3.5), (3 * L / 4 + 0.4, 2.5), (L, 0.5)]
ax.plot([p[0] for p in pts], [p[1] for p in pts], color=C1, lw=2.4)
for y in np.arange(0.5, n, 1.0):
    ax.plot([0, L], [y, y], color=GRILA, lw=0.6, zorder=0)
ax.text(L / 2, -0.6, "lungimea barei (în crestătură) →", ha="center", va="top", color=TEXT, fontsize=9)
ax.text(-0.3, n / 4, "coloana 1", ha="right", va="center", color=TEXT2, fontsize=8.5)
ax.text(-0.3, 3 * n / 4, "coloana 2", ha="right", va="center", color=TEXT2, fontsize=8.5)
ax.set_xlim(-2.0, L + 0.3)
ax.set_ylim(-1.3, n + 0.4)
ax.axis("off")
ax.set_title("(b) transpoziția Roebel: traseul unui fir elementar (albastru)\ntrece prin toate pozițiile → tensiuni induse egale", fontsize=9.5)
salveaza(fig, "f03-2-bara-statorica")

# --- Sisteme de excitație -------------------------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(11.5, 4.4))


def bloc(ax, x, y, w, h, text, culoare="#efeee9", margine=TEXT2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.12", facecolor=culoare,
                                edgecolor=margine, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=TEXT, fontsize=8.8)


def sageata(ax, a, b, culoare=TEXT):
    ax.annotate("", xy=b, xytext=a, arrowprops=dict(arrowstyle="-|>", color=culoare, lw=1.3))


ax = axs[0]
ax.add_patch(Rectangle((2.3, 0.2), 4.7, 3.3, facecolor="#f4f7fc", edgecolor=C1, lw=1.2, ls=(0, (5, 3))))
ax.text(4.65, 3.3, "pe rotor (se rotește cu arborele)", ha="center", color=C1, fontsize=8.5)
bloc(ax, 0.0, 1.9, 1.9, 1.0, "statorul\nexcitatoarei\n(c.c. de la RAT)")
bloc(ax, 2.6, 1.9, 1.7, 1.0, "indusul\nexcitatoarei\n(trifazat)", "#e3ecf8")
bloc(ax, 4.6, 1.9, 1.6, 1.0, "redresor\nrotativ\n(diode)", "#e3ecf8")
bloc(ax, 4.15, 0.3, 2.5, 1.15, "înfășurarea\nde excitație a\ngeneratorului", "#fbe3d6")
bloc(ax, 0.0, 0.3, 1.9, 1.15, "RAT\n(regulator automat\nde tensiune)")
sageata(ax, (1.9, 2.4), (2.6, 2.4))
sageata(ax, (4.3, 2.4), (4.6, 2.4))
sageata(ax, (5.4, 1.9), (5.4, 1.45))
sageata(ax, (0.95, 1.35), (0.95, 1.9))
ax.text(1.95, 2.55, "câmp", fontsize=8, color=TEXT2)
ax.text(0.0, -0.05, "Nu există perii și inele: curentul de excitație se produce chiar pe rotor.", fontsize=8.5,
        color=TEXT2, va="top")
ax.set_title("(a) excitație fără perii (brushless)", fontsize=10)
ax = axs[1]
bloc(ax, 0.0, 2.0, 2.0, 0.9, "bornele\ngeneratorului")
bloc(ax, 0.0, 0.5, 2.0, 0.9, "transformator\nde excitație")
bloc(ax, 2.6, 0.5, 2.0, 0.9, "redresor cu\ntiristoare", "#e3ecf8")
bloc(ax, 2.6, 2.0, 2.0, 0.9, "RAT")
bloc(ax, 5.1, 0.4, 1.9, 1.1, "perii +\ninele\ncolectoare", "#efe3c6")
bloc(ax, 5.1, 2.0, 1.9, 1.1, "înfășurarea\nde excitație\n(rotor)", "#fbe3d6")
sageata(ax, (1.0, 2.0), (1.0, 1.4))
sageata(ax, (2.0, 0.95), (2.6, 0.95))
sageata(ax, (3.6, 2.0), (3.6, 1.4), C2)
sageata(ax, (4.6, 0.95), (5.1, 0.95))
sageata(ax, (6.05, 1.5), (6.05, 2.0))
ax.text(3.5, 1.7, "comanda unghiului\nde aprindere", fontsize=8, color=TEXT2, ha="right", va="center")
ax.text(0.0, -0.05, "Răspuns rapid; necesită perii și inele colectoare.", fontsize=8.5, color=TEXT2, va="top")
ax.set_title("(b) excitație statică (cu tiristoare)", fontsize=10)
for a in axs:
    a.set_xlim(-0.2, 7.2)
    a.set_ylim(-0.6, 3.7)
    a.set_aspect("equal")
    a.axis("off")
salveaza(fig, "f03-5-excitatie")
