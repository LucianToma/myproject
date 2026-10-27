"""Figurile capitolului 1 – Transformatorul."""

import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm
from comun import C1, C2, C3, C4, TEXT, TEXT2, GRILA, FUNDAL, FIGURI, salveaza, virgula, sageata
from modele import SQRT3, tensiune_secundar_exacta, randament_transformator

schemdraw.use("matplotlib")
schemdraw.config(fontsize=12, bgcolor=FUNDAL, lw=1.6)

# --- Principiul transformatorului monofazat ----------------------------------
fig, ax = plt.subplots(figsize=(6.6, 3.6))
ax.add_patch(plt.Rectangle((0, 0), 6, 4, facecolor="#d9d8d3", edgecolor=TEXT2, lw=1))
ax.add_patch(plt.Rectangle((1, 1), 4, 2, facecolor=FUNDAL, edgecolor=TEXT2, lw=1))
# fluxul util (linie închisă prin miez)
ax.add_patch(plt.Rectangle((0.5, 0.5), 5, 3, fill=False, edgecolor=C1, lw=1.8, ls=(0, (6, 3))))
ax.annotate("", xy=(3.4, 3.5), xytext=(2.6, 3.5), arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.8))
ax.text(3.0, 3.72, "Φ (flux util, prin miez)", color=TEXT, ha="center", fontsize=9)
for x0, nume, c in ((0, "N₁", C2), (5, "N₂", C3)):
    for k in range(6):
        y = 0.8 + k * 0.42
        ax.add_patch(plt.Rectangle((x0 - 0.25, y), 1.5, 0.28, facecolor=c, edgecolor=FUNDAL, lw=1.5))
    ax.text(x0 + 0.5, 3.35 if x0 == 0 else 3.35, nume, color=TEXT, ha="center", fontsize=10,
            bbox=dict(facecolor=FUNDAL, edgecolor="none", pad=1))
ax.plot([-0.25, -1.2], [0.94, 0.94], color=TEXT, lw=1.4)
ax.plot([-0.25, -1.2], [2.04 + 0.84, 2.04 + 0.84], color=TEXT, lw=1.4)
ax.annotate("", xy=(-1.0, 2.75), xytext=(-1.0, 1.1), arrowprops=dict(arrowstyle="<|-", color=TEXT, lw=1.2))
ax.text(-1.15, 1.9, "$u_1$", ha="right", va="center", color=TEXT, fontsize=11)
ax.text(-1.25, 3.1, "$i_1$ →", ha="left", color=TEXT, fontsize=10)
ax.plot([6.25, 7.2], [0.94, 0.94], color=TEXT, lw=1.4)
ax.plot([6.25, 7.2], [2.88, 2.88], color=TEXT, lw=1.4)
ax.add_patch(plt.Rectangle((7.05, 1.4), 0.3, 1.0, facecolor=FUNDAL, edgecolor=TEXT, lw=1.4))
ax.text(7.5, 1.9, "$Z_s$", color=TEXT, va="center", fontsize=11)
ax.text(6.5, 1.9, "$u_2$", color=TEXT, va="center", fontsize=11)
ax.text(6.2, 3.1, "$i_2$ →", ha="left", color=TEXT, fontsize=10)
ax.text(3.0, -0.35, "miez din tole de oțel electrotehnic", ha="center", color=TEXT2, fontsize=9)
ax.set_xlim(-1.8, 8.2)
ax.set_ylim(-0.6, 4.1)
ax.set_aspect("equal")
ax.axis("off")
salveaza(fig, "f01-1-principiu")

# --- Schema echivalentă în T ------------------------------------------------
def borne(d, x_st, x_dr, H, U_st, U_dr):
    """Bara de jos, bornele și etichetele tensiunilor la cele două capete."""
    d.add(elm.Line().at((x_st, -H)).to((x_dr, -H)))
    for x in (x_st, x_dr):
        d.add(elm.Dot(open=True).at((x, -H)))
    d.add(elm.Gap().at((x_st, 0)).to((x_st, -H)).label(["+", U_st, "–"]))
    d.add(elm.Gap().at((x_dr, 0)).to((x_dr, -H)).label(["+", U_dr, "–"]))


H = 4.5
with schemdraw.Drawing(show=False) as d:
    d.add(elm.Dot(open=True).at((0, 0)))
    d.add(elm.Line().right(0.8).label("$\\underline{I}_1$ →", loc="top"))
    d.add(elm.Resistor().right().label("$R_1$"))
    d.add(elm.Inductor2(loops=3).right().label("$X_{1\\sigma}$"))
    d.add(elm.Line().right(1.2))
    nod = d.add(elm.Dot())
    d.add(elm.Line().right(1.2))
    d.add(elm.Inductor2(loops=3).right().label("$X'_{2\\sigma}$"))
    d.add(elm.Resistor().right().label("$R'_2$"))
    d.add(elm.Line().right(0.8).label("$\\underline{I}'_2$ →", loc="top"))
    t2 = d.add(elm.Dot(open=True))
    xn, xd = nod.center.x, t2.center.x
    d.add(elm.Line().at((xn, 0)).to((xn, -0.8)))
    d.add(elm.Line().at((xn - 0.9, -0.8)).to((xn + 0.9, -0.8)))
    d.add(elm.Resistor().at((xn - 0.9, -0.8)).to((xn - 0.9, -H + 0.8)).label("$R_{Fe}$", loc="bottom"))
    d.add(elm.Inductor2(loops=3).at((xn + 0.9, -0.8)).to((xn + 0.9, -H + 0.8)).label("$X_m$", loc="top"))
    d.add(elm.Line().at((xn - 0.9, -H + 0.8)).to((xn + 0.9, -H + 0.8)))
    d.add(elm.Line().at((xn, -H + 0.8)).to((xn, -H)))
    d.add(elm.Dot().at((xn, -H)))
    d.add(elm.Label().at((xn + 0.15, -0.35)).label("$\\underline{I}_0$ ↓", loc="right", halign="left"))
    borne(d, 0, xd, H, "$\\underline{U}_1$", "$\\underline{U}'_2$")
    d.save(str(FIGURI / "f01-2-schema-T.svg"))
print("  figura f01-2-schema-T.svg")

# --- Schema simplificată ---------------------------------------------------
H = 3.5
with schemdraw.Drawing(show=False) as d:
    d.add(elm.Dot(open=True).at((0, 0)))
    d.add(elm.Line().right(2.0).label("$\\underline{I}_1 \\approx \\underline{I}'_2$ →", loc="top"))
    d.add(elm.Resistor().right().label("$R_{sc} = R_1 + R'_2$"))
    d.add(elm.Inductor2(loops=3).right().label("$X_{sc} = X_{1\\sigma} + X'_{2\\sigma}$"))
    d.add(elm.Line().right(0.8))
    t2 = d.add(elm.Dot(open=True))
    borne(d, 0, t2.center.x, H, "$\\underline{U}_1$", "$\\underline{U}'_2$")
    d.save(str(FIGURI / "f01-3-schema-simplificata.svg"))
print("  figura f01-3-schema-simplificata.svg")

# --- Diagrama fazorială (transformatorul de 20 kVA, sarcină inductivă) -------
Rsc, Xsc, I = 4.32, 10.679, 8.333
U2 = tensiune_secundar_exacta(2400.0, I, 0.8, Rsc, Xsc)
mag = 5.0          # căderile de tensiune sunt mărite de 5 ori pentru vizibilitate
Iz = I * np.exp(-1j * np.arccos(0.8))
z_U2 = U2 + 0j
z_R = z_U2 + mag * Rsc * Iz
z_X = z_R + mag * 1j * Xsc * Iz
fig, ax = plt.subplots(figsize=(6.6, 3.6))
sageata(ax, 0j, z_U2, C1, "$\\underline{U}'_2$", offset=(0, -14), ha="center", va="top")
sageata(ax, 0j, Iz * 140, C2, "$\\underline{I}'_2$ (scară proprie)", offset=(-60, -16))
sageata(ax, z_U2, z_R, C3, "$R_{sc}\\underline{I}'_2$", offset=(-6, -10), ha="right", va="top")
sageata(ax, z_R, z_X, C4, "$jX_{sc}\\underline{I}'_2$", offset=(10, -4), ha="left", va="center")
sageata(ax, 0j, z_X, TEXT, "$\\underline{U}_1$", offset=(-10, 6), ha="right")
th = np.linspace(0, -np.arccos(0.8), 30)
ax.plot(300 * np.cos(th), 300 * np.sin(th), color=TEXT2, lw=1)
ax.text(330, -120, "$\\varphi_2$", color=TEXT, fontsize=11)
ax.set_xlim(-100, 3100)
ax.set_ylim(-1000, 900)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Diagrama fazorială – sarcină inductivă (căderile de tensiune mărite de 5×)", fontsize=10)
salveaza(fig, "f01-4-diagrama-fazoriala")

# --- Randamentul în funcție de încărcare (400 kVA, P0 = 0,43 kW, Psc = 4,6 kW) -
Sn, P0, Psc = 400e3, 430.0, 4600.0
beta = np.linspace(0.02, 1.25, 400)
fig, ax = plt.subplots(figsize=(6.6, 3.8))
for cosf, c in ((1.0, C1), (0.9, C2), (0.8, C3)):
    eta = 100 * randament_transformator(beta, Sn, cosf, P0, Psc)
    ax.plot(beta, eta, color=c, label=f"cos φ₂ = {cosf:g}".replace(".", ","))
bo = np.sqrt(P0 / Psc)
eo = 100 * randament_transformator(bo, Sn, 1.0, P0, Psc)
ax.plot([bo], [eo], "o", color=C1, ms=8, mec=FUNDAL, mew=2)
ax.annotate(f"η max la β = √(P₀/P$_{{sc}}$) = {bo:.3f}".replace(".", ","), xy=(bo, eo), xytext=(0.5, 99.45),
            color=TEXT, arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
ax.set_ylim(97.8, 99.6)
ax.set_xlabel("factorul de încărcare β = S/Sₙ")
ax.set_ylabel("η [%]")
ax.set_title("Randamentul transformatorului de 400 kVA")
ax.legend(loc="lower right")
virgula(ax)
salveaza(fig, "f01-6-randament")

# --- Caracteristica externă (400 kVA, 20/0,4 kV, usc = 4 %) -----------------
U2f, I2n = 400 / SQRT3, Sn / (SQRT3 * 400)
Zb = 400**2 / Sn
uR = 100 * Psc / Sn
uX = np.sqrt(4.0**2 - uR**2)
R, X = uR / 100 * Zb, uX / 100 * Zb
fig, ax = plt.subplots(figsize=(6.6, 3.8))
b = np.linspace(0, 1.2, 200)
for (nume, cosf, ind), c in zip((("cos φ₂ = 0,8 inductiv", 0.8, True), ("cos φ₂ = 1", 1.0, True),
                                 ("cos φ₂ = 0,8 capacitiv", 0.8, False)), (C1, C2, C3)):
    U = [SQRT3 * tensiune_secundar_exacta(U2f, x * I2n, cosf, R, X, inductiv=ind) for x in b]
    ax.plot(b, U, color=c, label=nume)
ax.axhline(400, color=TEXT2, lw=0.8)
ax.set_xlabel("β = I₂/I₂ₙ")
ax.set_ylabel("U₂ [V] (tensiunea de linie)")
ax.set_title("Caracteristica externă U₂(β) la U₁ = U₁ₙ")
ax.legend(loc="lower left")
virgula(ax)
salveaza(fig, "f01-5-caracteristica-externa")

# --- Grupa de conexiuni Dyn11 -------------------------------------------------
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.0, 3.8))
ceas = lambda h: np.exp(1j * np.radians(90 - 30 * h))       # poziția orei h pe cadran
A, B, C = ceas(0), ceas(4), ceas(8)
for z0, z1 in ((A, B), (B, C), (C, A)):
    a1.plot([z0.real, z1.real], [z0.imag, z1.imag], color=C1, lw=2)
for z, n in ((A, "A"), (B, "B"), (C, "C")):
    a1.plot([z.real], [z.imag], "o", color=C1, ms=7, mec=FUNDAL, mew=2)
    a1.text(1.2 * z.real, 1.2 * z.imag, n, ha="center", va="center", color=TEXT, fontsize=11)
a1.plot([0, 0], [0, 1], color=TEXT2, lw=1, ls=(0, (4, 3)))
a1.set_title("ÎT în triunghi (D)\nfazorul A la ora 12", fontsize=10)
a = ceas(11)
for h, n in ((11, "a"), (3, "b"), (7, "c")):
    z = ceas(h)
    sageata(a2, 0j, z, C2)
    a2.text(1.2 * z.real, 1.2 * z.imag, n, ha="center", va="center", color=TEXT, fontsize=11)
a2.plot([0], [0], "o", color=TEXT, ms=5)
a2.text(0.08, -0.12, "n", color=TEXT, fontsize=11)
a2.plot([0, 0], [0, 1], color=TEXT2, lw=1, ls=(0, (4, 3)))
a2.set_title("JT în stea cu neutru (yn)\nfazorul a la ora 11 → grupa 11", fontsize=10)
for ax in (a1, a2):
    for h in range(12):
        z = ceas(h)
        ax.plot([0.92 * z.real, z.real * 1.0], [0.92 * z.imag, z.imag * 1.0], color=GRILA, lw=1)
    ax.add_patch(plt.Circle((0, 0), 1.0, fill=False, color=GRILA, lw=1))
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)
    ax.set_aspect("equal")
    ax.axis("off")
fig.text(0.5, 0.0, "Tensiunea JT este defazată cu 11 × 30° = 330° în urma celei de ÎT (adică 30° înainte).",
         ha="center", color=TEXT2, fontsize=9)
salveaza(fig, "f01-7-grupa-dyn11")
