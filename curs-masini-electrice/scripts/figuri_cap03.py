"""Figurile capitolului 3 – Generatorul sincron."""

import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm
from comun import C1, C2, C3, C4, TEXT, TEXT2, GRILA, FUNDAL, FIGURI, salveaza, virgula, sageata, salveaza_schema
from modele import SQRT3, generator_E0

schemdraw.use("matplotlib")
schemdraw.config(fontsize=12, bgcolor=FUNDAL, lw=1.6)

Sn, Un, cos_n = 10e6, 6300.0, 0.8
In = Sn / (SQRT3 * Un)
Uf = Un / SQRT3
Ie0, Isc0 = 200.0, 830.0
Xs = Uf / Isc0

# --- Rotor cu poli înecați vs rotor cu poli aparenți ------------------------
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 4.2))
for ax in (a1, a2):
    ax.add_patch(plt.Circle((0, 0), 1.0, color="#d9d8d3", ec=TEXT2, lw=1))
    ax.add_patch(plt.Circle((0, 0), 0.72, color=FUNDAL, ec=TEXT2, lw=1))
# poli înecați: rotor cilindric cu crestături pe ~2/3 din periferie
a1.add_patch(plt.Circle((0, 0), 0.69, color="#c9c8c2", ec=TEXT2, lw=1))
for k in range(24):
    a = 2 * np.pi * k / 24
    if abs(np.sin(a)) > 0.87:         # zonele polare (fără crestături) sunt în jurul axei verticale
        continue
    a1.add_patch(plt.Rectangle((0.5, -0.025), 0.17, 0.05, angle=np.degrees(a), rotation_point=(0, 0),
                               color=C2, ec=FUNDAL, lw=0.5))
a1.text(0, 0.42, "N", ha="center", va="center", color=TEXT, fontsize=14, fontweight="bold")
a1.text(0, -0.42, "S", ha="center", va="center", color=TEXT, fontsize=14, fontweight="bold")
a1.add_patch(plt.Circle((0, 0), 0.1, color=TEXT2))
a1.set_title("Poli înecați (turbogenerator, 2p = 2)\nrotor cilindric, n = 3000 rot/min la 50 Hz", fontsize=10)
# poli aparenți: 8 poli
for k in range(8):
    a = 2 * np.pi * k / 8
    ax = a2
    pol = plt.Polygon([(0.25, -0.09), (0.55, -0.09), (0.55, -0.2), (0.69, -0.2), (0.69, 0.2), (0.55, 0.2),
                       (0.55, 0.09), (0.25, 0.09)], closed=True, color="#c9c8c2", ec=TEXT2, lw=1)
    tr = plt.matplotlib.transforms.Affine2D().rotate(a) + ax.transData
    pol.set_transform(tr)
    ax.add_patch(pol)
    for y in (0.11, -0.17):
        b = plt.Rectangle((0.3, y), 0.23, 0.06, color=C2, ec=FUNDAL, lw=0.5)
        b.set_transform(tr)
        ax.add_patch(b)
    ax.text(0.6 * np.cos(a), 0.6 * np.sin(a), "NS"[k % 2], ha="center", va="center", color=TEXT, fontsize=9,
            fontweight="bold")
a2.add_patch(plt.Circle((0, 0), 0.27, color="#c9c8c2", ec=TEXT2, lw=1))
a2.add_patch(plt.Circle((0, 0), 0.1, color=TEXT2))
a2.set_title("Poli aparenți (hidrogenerator, aici 2p = 8)\nn = 750 rot/min la 50 Hz", fontsize=10)
for ax in (a1, a2):
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect("equal")
    ax.axis("off")
fig.text(0.5, 0.02, "portocaliu: înfășurarea de excitație (curent continuu); inelul exterior: statorul (înfășurarea trifazată nu este desenată)",
         ha="center", color=TEXT2, fontsize=9)
salveaza(fig, "f03-1-tipuri-rotor")

# --- Caracteristicile de mers în gol și de scurtcircuit ----------------------
ksat = 1.15                                   # factor de saturație la tensiunea nominală (ipoteză de model)
panta = ksat * Uf / Ie0                       # panta dreptei întrefierului [V/A]
b = Uf * Ie0 / (panta * Ie0 - Uf)             # E = a·Ie/(b + Ie), cu a/b = panta și E(Ie0) = Uf
a = panta * b
Ie = np.linspace(0, 500, 300)
E = a * Ie / (b + Ie)
Isc = Isc0 / Ie0 * Ie
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.9))
a1.plot(Ie, E * SQRT3 / 1e3, color=C1, label="mers în gol U₀(I$_e$)")
a1.plot(Ie[Ie < 330], panta * Ie[Ie < 330] * SQRT3 / 1e3, color=C3, lw=1.4, label="dreapta întrefierului")
a1.plot([Ie0], [Un / 1e3], "o", color=C1, ms=8, mec=FUNDAL, mew=2)
a1.annotate("Uₙ = 6,3 kV la I$_e$ = 200 A", xy=(Ie0, Un / 1e3), xytext=(240, 4.4), color=TEXT,
            arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
a1.set_xlabel("I$_e$ [A]")
a1.set_ylabel("U₀ [kV] (de linie)")
a1.set_title("Caracteristica de mers în gol")
a1.legend(loc="lower right")
a2.plot(Ie, Isc, color=C2)
a2.plot([Ie0], [Isc0], "o", color=C2, ms=8, mec=FUNDAL, mew=2)
a2.annotate("I$_{sc}$ = 830 A la I$_e$ = 200 A", xy=(Ie0, Isc0), xytext=(230, 600), color=TEXT,
            arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
a2.axhline(In, color=TEXT2, lw=0.8)
a2.text(5, In + 40, "Iₙ = 916 A", color=TEXT2, fontsize=9)
a2.set_xlabel("I$_e$ [A]")
a2.set_ylabel("I$_{sc}$ [A]")
a2.set_title("Caracteristica de scurtcircuit (liniară)")
for ax in (a1, a2):
    virgula(ax)
salveaza(fig, "f03-2-gol-scurtcircuit")

# --- Schema echivalentă pe fază ----------------------------------------------
with schemdraw.Drawing(show=False) as d:
    d.add(elm.SourceSin().up(4))
    d.add(elm.Label().at((-0.9, 2)).label("$\\underline{E}_0$"))
    d.add(elm.Line().right(0.6))
    d.add(elm.Inductor2(loops=3).right().label("$jX_s$"))
    d.add(elm.Resistor().right().label("$R$"))
    d.add(elm.Line().right(1.4).label("$\\underline{I}$ →", loc="top"))
    t = d.add(elm.Dot(open=True))
    x = t.center.x
    d.add(elm.Line().right(1.4))
    d.add(elm.Resistor().down(4).label("$\\underline{Z}_s$ (sarcină)", loc="bottom"))
    d.add(elm.Line().left(1.4))
    d.add(elm.Dot(open=True))
    d.add(elm.Line().left(x))
    d.add(elm.Gap().at((x, 4)).to((x, 0)).label(["+", "$\\underline{U}$", "–"]))
    salveaza_schema(d, "f03-3-schema-echivalenta")

# --- Diagrame fazoriale pentru trei tipuri de sarcină (I = Iₙ, U = Uₙ) ---------
fig, axs = plt.subplots(1, 3, figsize=(11, 4.0))
for ax, (titlu, phi) in zip(axs, (("sarcină inductivă (cos φ = 0,8)", np.arccos(0.8)),
                                   ("sarcină rezistivă (cos φ = 1)", 0.0),
                                   ("sarcină capacitivă (cos φ = 0,8)", -np.arccos(0.8)))):
    E0, Iz = generator_E0(Uf, In, phi, Xs)
    U = Uf + 0j
    sageata(ax, 0j, U, C1, "$\\underline{U}$", offset=(0, -12), ha="center", va="top", t=0.85)
    sageata(ax, 0j, Iz * 1.6, C2, "$\\underline{I}$", offset=(6, 2), ha="left", t=1.0)
    sageata(ax, U, E0, C4, "$jX_s\\underline{I}$", offset=(6, 0))
    sageata(ax, 0j, E0, TEXT, "$\\underline{E}_0$", offset=(-8, 6), ha="right")
    d_ = np.angle(E0)
    th = np.linspace(0, d_, 30)
    ax.plot(900 * np.cos(th), 900 * np.sin(th), color=TEXT2, lw=1)
    ax.text(1150 * np.cos(0.8 * d_), 1150 * np.sin(0.8 * d_), "δ", color=TEXT, fontsize=11, va="center")
    ax.text(0, -2600, f"E₀ = {abs(E0) * SQRT3 / 1e3:.2f} kV (linie)\nδ = {np.degrees(d_):.1f}°".replace(".", ","),
            color=TEXT, fontsize=9, va="top")
    ax.set_xlim(-800, 7200)
    ax.set_ylim(-3600, 5600)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(titlu, fontsize=10)
fig.suptitle("Generator sincron 10 MVA, 6,3 kV, X$_s$ = 4,38 Ω – fazori la curentul nominal (I la altă scară)",
             color=TEXT, fontsize=11)
salveaza(fig, "f03-4-fazori-sarcini")

# --- Caracteristica putere–unghi --------------------------------------------
E0, _ = generator_E0(Uf, In, np.arccos(cos_n), Xs)
Pmax = 3 * Uf * abs(E0) / Xs
dg = np.linspace(0, 180, 361)
fig, ax = plt.subplots(figsize=(6.8, 3.9))
ax.axvspan(90, 180, color="#f3f2ee", lw=0)
ax.plot(dg, Pmax * np.sin(np.radians(dg)) / 1e6, color=C1)
d0 = np.degrees(np.angle(E0))
ax.axhline(8, color=C2, lw=1.6)
ax.plot([d0], [8], "o", color=C2, ms=8, mec=FUNDAL, mew=2)
ax.annotate(f"punct de funcționare\nδ = {d0:.1f}°, P = 8 MW".replace(".", ","), xy=(d0, 8), xytext=(8, 11.5),
            color=TEXT, arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
ax.text(91, 1.0, "zonă instabilă\n(δ > 90°)", color=TEXT, fontsize=9)
ax.text(155, 8.4, "puterea turbinei", color=TEXT2, fontsize=9)
ax.annotate(f"P$_{{max}}$ = {Pmax / 1e6:.2f} MW".replace(".", ","), xy=(90, Pmax / 1e6), xytext=(105, 16.5),
            color=TEXT, arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
ax.set_xlim(0, 180)
ax.set_ylim(0, 18.5)
ax.set_xlabel("δ [°]")
ax.set_ylabel("P [MW]")
ax.set_title("P(δ) = 3·U·E₀·sin δ / X$_s$ (excitație constantă)")
virgula(ax)
salveaza(fig, "f03-6-putere-unghi")

# --- Caracteristicile externe (excitație constantă, aleasă pentru U = Uₙ la Iₙ) ---
fig, ax = plt.subplots(figsize=(6.8, 3.9))
Ir = np.linspace(0, 1.2, 200) * In
for (nume, phi), c in zip((("cos φ = 0,8 inductiv", np.arccos(0.8)), ("cos φ = 1", 0.0),
                           ("cos φ = 0,8 capacitiv", -np.arccos(0.8))), (C1, C2, C3)):
    E0f = abs(generator_E0(Uf, In, phi, Xs)[0])
    with np.errstate(invalid="ignore"):   # peste limita de stabilitate (δ = 90°) nu există soluție
        U = -Xs * Ir * np.sin(phi) + np.sqrt(E0f**2 - (Xs * Ir * np.cos(phi)) ** 2)
    ax.plot(Ir / In, U * SQRT3 / 1e3, color=c, label=nume)
ax.axhline(Un / 1e3, color=TEXT2, lw=0.8)
ax.axvline(1, color=TEXT2, lw=0.8)
ax.set_xlabel("I/Iₙ")
ax.set_ylabel("U [kV] (de linie)")
ax.set_title("Caracteristici externe U(I) la I$_e$ = const (model liniar)")
ax.annotate("limita de stabilitate\n(δ = 90°)", xy=(1.068, 4.9), xytext=(0.72, 4.3), color=TEXT, fontsize=9,
            arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
ax.legend(loc="lower left")
virgula(ax)
salveaza(fig, "f03-5-caracteristici-externe")

# --- Statismul: împărțirea sarcinii între două generatoare ---------------------
fig, ax = plt.subplots(figsize=(6.8, 3.9))
P = np.linspace(0, 110, 200)
for (nume, Pn_, s_, P0_), c in zip((("G1: 100 MW, statism 4 %", 100, 0.04, 60), ("G2: 50 MW, statism 5 %", 50, 0.05, 30)),
                                  (C1, C2)):
    f0 = 50 + s_ * 50 * P0_ / Pn_         # frecvența de mers în gol reglată pentru P0_ la 50 Hz
    m = P <= Pn_
    ax.plot(P[m], f0 - s_ * 50 * P[m] / Pn_, color=c, label=nume)
    df = 12 / 70
    P1_ = P0_ + Pn_ / (s_ * 50) * df
    ax.plot([P0_, P1_], [50, 50 - df], "o", color=c, ms=7, mec=FUNDAL, mew=2)
ax.axhline(50, color=TEXT2, lw=0.8)
ax.axhline(50 - 12 / 70, color=TEXT2, lw=0.8)
ax.text(2, 50 - 12 / 70 - 0.06, "f = 49,83 Hz după creșterea sarcinii cu 12 MW", color=TEXT, fontsize=9, va="top")
ax.text(2, 50.03, "f = 50 Hz", color=TEXT, fontsize=9)
ax.set_xlabel("P [MW]")
ax.set_ylabel("f [Hz]")
ax.set_title("Caracteristici de statism f(P) ale regulatoarelor de viteză")
ax.legend(loc="upper right")
virgula(ax)
salveaza(fig, "f03-7-statism")
