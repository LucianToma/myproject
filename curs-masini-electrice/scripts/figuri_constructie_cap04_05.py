"""Desenele constructive ale capitolelor 4 (rotoare sincrone moderne) și 5 (componentele acționării)."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, Wedge, FancyBboxPatch, Arc
from comun import C1, C2, C3, C4, C5, TEXT, TEXT2, GRILA, FUNDAL, salveaza

FIER, FIER_INCHIS = "#c9c8c2", "#8f8e88"
OTEL = "#b0b2b5"
NORD, SUD = "#d9534f", "#3f7fc4"          # culori convenționale pentru polii magneților


def eticheta(ax, text, xy, xytext, ha="left", fs=9):
    ax.annotate(text, xy=xy, xytext=xytext, color=TEXT, fontsize=fs, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))


def rot(pts, a):
    c, s = np.cos(a), np.sin(a)
    return [(c * x - s * y, s * x + c * y) for x, y in pts]


# --- Rotoare de motoare sincrone moderne (4 poli) -----------------------------------------
fig, axs = plt.subplots(1, 3, figsize=(12, 4.6))
R = 1.0
# (a) magneți pe suprafață, cu bandaj
ax = axs[0]
ax.add_patch(Circle((0, 0), 0.82, facecolor=FIER, edgecolor=FIER_INCHIS, lw=1))
for k in range(4):
    a0 = 90 * k + 45 - 40
    ax.add_patch(Wedge((0, 0), 0.97, a0, a0 + 80, width=0.15, facecolor=NORD if k % 2 == 0 else SUD,
                       edgecolor=FUNDAL, lw=1))
ax.add_patch(Circle((0, 0), 1.0, fill=False, edgecolor=C4, lw=2.5))
ax.add_patch(Circle((0, 0), 0.22, facecolor=OTEL, edgecolor=TEXT2, lw=1))
ax.set_title("(a) magneți pe suprafață (SPM)\ncu bandaj de reținere", fontsize=10)
eticheta(ax, "bandaj (fibră de sticlă/carbon\nsau manșon nemagnetic)", (0.7, 0.72), (0.2, 1.45))
# (b) magneți îngropați în V
ax = axs[1]
ax.add_patch(Circle((0, 0), R, facecolor=FIER, edgecolor=FIER_INCHIS, lw=1))
def banda(p0, p1, g):
    """Dreptunghi de grosime g de-a lungul segmentului p0–p1."""
    d = np.subtract(p1, p0)
    n = np.array([-d[1], d[0]]) / np.hypot(*d) * g / 2
    return [tuple(p0 + n), tuple(p1 + n), tuple(p1 - n), tuple(p0 - n)]


for k in range(4):
    a = np.radians(90 * k + 45)
    for semn in (1, -1):
        p0, p1 = np.array([0.42, semn * 0.05]), np.array([0.84, semn * 0.33])
        ax.add_patch(Polygon(rot(banda(p0, p1, 0.07), a), closed=True, facecolor=NORD if k % 2 == 0 else SUD,
                             edgecolor=FUNDAL, lw=0.8))
        q1 = p1 + (p1 - p0) / np.hypot(*(p1 - p0)) * 0.1
        ax.add_patch(Polygon(rot(banda(p1, q1, 0.09), a), closed=True, facecolor=FUNDAL, edgecolor=FIER_INCHIS, lw=0.6))
ax.add_patch(Circle((0, 0), 0.22, facecolor=OTEL, edgecolor=TEXT2, lw=1))
ax.set_title("(b) magneți îngropați în V (IPM)\ncuplu sincron + cuplu de reluctanță", fontsize=10)
eticheta(ax, "barieră de flux (aer)\nla capătul magnetului", (0.42, 0.86), (0.3, 1.45))
# (c) rotor sincron cu reluctanță: bariere de flux, fără magneți și fără colivie
ax = axs[2]
ax.add_patch(Circle((0, 0), R, facecolor=FIER, edgecolor=FIER_INCHIS, lw=1))
for k in range(4):
    a = np.radians(90 * k)
    for r_b, lat in ((0.95, 0.06), (0.80, 0.07), (0.64, 0.08)):
        t = np.linspace(-0.62, 0.62, 40) * (r_b / 0.95)
        # barieră în formă de arc, centrată pe axa q (între poli), concavă spre centrul polului
        xc, yc = 1.32 * r_b, 0.0
        ext = [(xc - (xc - r_b * 0.62 * 0 - 0.0) * 0 + (r_b * 0.62) * np.cos(tt), 0) for tt in t]
        pts_out = [(np.cos(a0) * (r_b), np.sin(a0) * (r_b)) for a0 in t]
        th = np.linspace(-0.75, 0.75, 40)
        rr = 0.62 * r_b + 0.0
        cx = r_b * 1.25
        out = [(cx - (rr + lat / 2) * np.cos(q), (rr + lat / 2) * np.sin(q)) for q in th]
        inn = [(cx - (rr - lat / 2) * np.cos(q), (rr - lat / 2) * np.sin(q)) for q in th[::-1]]
        poly = [p for p in out + inn if np.hypot(*p) < 0.965]
        if len(poly) > 3:
            ax.add_patch(Polygon(rot(poly, a + np.pi / 4), closed=True, facecolor=FUNDAL, edgecolor=FIER_INCHIS, lw=0.6))
ax.add_patch(Circle((0, 0), 0.22, facecolor=OTEL, edgecolor=TEXT2, lw=1))
ax.set_title("(c) rotor cu reluctanță (SynRM)\nbariere de flux, fără magneți", fontsize=10)
eticheta(ax, "nervuri subțiri de fier\nțin segmentele împreună", (0.15, 0.93), (0.1, 1.45))
for ax in axs:
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.25, 1.75)
    ax.set_aspect("equal")
    ax.axis("off")
fig.legend(handles=[Rectangle((0, 0), 1, 1, facecolor=NORD), Rectangle((0, 0), 1, 1, facecolor=SUD),
                    Rectangle((0, 0), 1, 1, facecolor=FIER, edgecolor=FIER_INCHIS)],
           labels=["magnet – pol N", "magnet – pol S", "tole rotorice"], loc="lower center", ncol=3,
           bbox_to_anchor=(0.5, -0.02), fontsize=9)
salveaza(fig, "f04-4-rotoare-moderne")

# --- Lanțul cinematic al unui troliu ------------------------------------------------------
fig, ax = plt.subplots(figsize=(11.5, 4.6))
ax.plot([-0.3, 7.8], [2, 2], color=TEXT2, lw=0.8, ls=(0, (8, 3, 2, 3)))
# encoder
ax.add_patch(Rectangle((-0.2, 1.75), 0.45, 0.5, facecolor="#9fb3c8", edgecolor=TEXT2, lw=1))
# motorul cu aripioare
ax.add_patch(Rectangle((0.3, 1.0), 2.6, 2.0, facecolor="#dcdad3", edgecolor=TEXT2, lw=1.2))
for k in range(8):
    ax.add_patch(Rectangle((0.45 + k * 0.3, 3.0), 0.1, 0.2, facecolor="#dcdad3", edgecolor=TEXT2, lw=0.6))
ax.add_patch(Rectangle((1.2, 3.2), 0.8, 0.35, facecolor="#dcdad3", edgecolor=TEXT2, lw=1))
ax.add_patch(Rectangle((2.9, 1.85), 0.5, 0.3, facecolor=OTEL, edgecolor=TEXT2, lw=0.8))
# frâna electromagnetică (pe motor sau între motor și reductor)
ax.add_patch(Rectangle((3.4, 1.35), 0.45, 1.3, facecolor=C4, edgecolor=TEXT2, lw=1))
# cuplajul elastic
ax.add_patch(Rectangle((3.85, 1.55), 0.3, 0.9, facecolor=OTEL, edgecolor=TEXT2, lw=0.8))
ax.add_patch(Rectangle((4.15, 1.6), 0.12, 0.8, facecolor="#7a6", edgecolor=TEXT2, lw=0.6))
ax.add_patch(Rectangle((4.27, 1.55), 0.3, 0.9, facecolor=OTEL, edgecolor=TEXT2, lw=0.8))
# reductorul cu roți dințate
ax.add_patch(FancyBboxPatch((4.75, 0.7), 2.0, 2.7, boxstyle="round,pad=0,rounding_size=0.15", facecolor="#e7e5df",
                            edgecolor=TEXT2, lw=1.2))
for (cx, cy, r) in ((5.25, 2.0, 0.25), (5.85, 2.0, 0.42), (5.85, 1.25, 0.18), (6.3, 1.25, 0.35)):
    ax.add_patch(Circle((cx, cy), r, facecolor="none", edgecolor=TEXT2, lw=1, ls=(0, (3, 2))))
# arborele de ieșire și tamburul cu cablu
ax.add_patch(Rectangle((6.75, 1.12), 0.6, 0.26, facecolor=OTEL, edgecolor=TEXT2, lw=0.8))
ax.add_patch(Rectangle((7.35, 0.35), 1.6, 1.8, facecolor="#cfd5dc", edgecolor=TEXT2, lw=1.2))
for x in np.linspace(7.45, 8.85, 12):
    ax.plot([x, x + 0.08], [0.35, 2.15], color=TEXT2, lw=0.6)
ax.plot([8.6, 8.6], [0.35, -1.2], color=TEXT, lw=1.6)
ax.add_patch(Rectangle((8.3, -1.75), 0.6, 0.55, facecolor="#8f8e88", edgecolor=TEXT, lw=1))
ax.text(8.6, -1.48, "m", ha="center", va="center", color="white", fontsize=10)
eticheta(ax, "traductor de turație/poziție\n(encoder)", (0.0, 1.75), (-0.5, 0.0))
eticheta(ax, "motor asincron sau sincron", (1.6, 3.55), (-0.5, 4.3))
eticheta(ax, "frână electromagnetică cu arcuri:\nfrânează la lipsa tensiunii", (3.6, 2.65), (3.3, 4.3))
eticheta(ax, "cuplaj elastic (compensează\nnecoaxialitatea, amortizează șocurile)", (4.21, 1.6), (2.0, -0.6))
eticheta(ax, "reductor cu roți dințate (raport i)", (5.9, 3.4), (7.4, 4.3))
eticheta(ax, "tambur cu cablu", (8.9, 1.9), (9.3, 2.6))
eticheta(ax, "sarcina", (8.9, -1.48), (9.3, -1.48))
ax.set_xlim(-0.7, 11.8)
ax.set_ylim(-2.0, 4.6)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Componentele mecanice ale unei acționări: troliul din problema 5.1 (schematic)", fontsize=10)
salveaza(fig, "f05-10-lant-cinematic")

# --- Modulul de putere cu IGBT (secțiune) -------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.2))
straturi = [("radiator (aluminiu)", 0.0, 0.8, "#cfd5dc"),
            ("pastă termoconductoare", 0.8, 0.12, "#f2f1ec"),
            ("placă de bază (cupru)", 0.92, 0.45, "#d99a6c"),
            ("lipitură", 1.37, 0.08, "#9aa0a6"),
            ("cupru (DBC)", 1.45, 0.15, "#d99a6c"),
            ("ceramică izolatoare (Al₂O₃ sau AlN)", 1.60, 0.3, "#f3efe6"),
            ("cupru (DBC)", 1.90, 0.15, "#d99a6c")]
for nume, y, h, c in straturi:
    ax.add_patch(Rectangle((0.6 if y > 0.85 else 0.0, y), 6.8 if y > 0.85 else 8.0, h, facecolor=c,
                           edgecolor=TEXT2, lw=0.8))
for x in np.linspace(0.3, 7.7, 12):
    ax.add_patch(Rectangle((x - 0.1, -0.9), 0.2, 0.9, facecolor="#cfd5dc", edgecolor=TEXT2, lw=0.6))
for xc, w, nume in ((2.0, 1.2, "cip IGBT (siliciu)"), (4.4, 0.9, "cip diodă")):
    ax.add_patch(Rectangle((xc - w / 2, 2.05), w, 0.06, facecolor="#9aa0a6", edgecolor="none"))
    ax.add_patch(Rectangle((xc - w / 2, 2.11), w, 0.22, facecolor="#5d6670", edgecolor=TEXT2, lw=0.8))
for xs, xe in ((1.7, 3.3), (2.2, 3.5), (4.3, 5.6)):
    t = np.linspace(0, np.pi, 30)
    ax.plot(xs + (xe - xs) * (1 - np.cos(t)) / 2, 2.33 + 0.55 * np.sin(t), color="#8a8f96", lw=1.6)
ax.add_patch(Rectangle((0.6, 2.05), 6.8, 1.45, fill=False, edgecolor=TEXT2, lw=1.4, ls=(0, (5, 3))))
ax.add_patch(Rectangle((6.0, 2.05), 0.25, 2.0, facecolor="#c7a24a", edgecolor=TEXT2, lw=0.8))
ax.annotate("", xy=(2.0, -1.2), xytext=(2.0, 2.2), arrowprops=dict(arrowstyle="-|>", color=C2, lw=2.2, alpha=0.75))
ax.text(1.85, 0.55, "fluxul de căldură", color=C2, fontsize=9, ha="right", rotation=90, va="center",
        bbox=dict(facecolor=FUNDAL, edgecolor="none", pad=1.5, alpha=0.9))
eticheta(ax, "cip IGBT (siliciu), lipit pe substrat", (2.4, 2.25), (8.3, 3.3))
eticheta(ax, "cip diodă de regim liber", (4.6, 2.25), (8.3, 2.9))
eticheta(ax, "fire de legătură din aluminiu", (3.0, 2.85), (8.3, 4.1))
eticheta(ax, "carcasă din plastic umplută cu gel siliconic", (7.4, 3.2), (8.3, 3.7))
eticheta(ax, "bornă de putere", (6.25, 3.9), (8.3, 4.5))
for (nume, y, h, c), xt in zip(straturi[2:][::-1], (2.5, 2.1, 1.75, 1.45, 1.15)):
    eticheta(ax, nume, (7.2, y + h / 2), (8.3, xt))
eticheta(ax, "pastă termoconductoare", (7.6, 0.86), (8.3, 0.8))
eticheta(ax, "radiator (aluminiu), răcit cu aer sau apă", (7.6, 0.3), (8.3, 0.3))
ax.text(0.0, -1.25, "substrat DBC = cupru – ceramică – cupru: conduce căldura, dar izolează electric cipurile de radiator",
        color=TEXT2, fontsize=8.5, va="top")
ax.set_xlim(-0.2, 14.0)
ax.set_ylim(-1.7, 4.8)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Modul de putere cu IGBT al unui convertor de frecvență (secțiune, schematic)", fontsize=10)
salveaza(fig, "f05-11-modul-igbt")
