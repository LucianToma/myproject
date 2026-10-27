"""Figurile capitolului 4 – Motorul sincron (motorul MS1000 din probleme)."""

import numpy as np
import matplotlib.pyplot as plt
from comun import C1, C2, C3, C4, TEXT, TEXT2, GRILA, FUNDAL, salveaza, virgula, sageata
from modele import SQRT3, motor_E0

Un, P2n, eta, cos_n, Xs = 6000.0, 1000e3, 0.96, 0.9, 36.0
Uf = Un / SQRT3
P1 = P2n / eta
In = P1 / (SQRT3 * Un * cos_n)


def curent(P, E0f):
    d = np.arcsin(P * Xs / (3 * Uf * E0f))
    E = E0f * np.exp(-1j * d)
    return (Uf - E) / (1j * Xs), E


# --- Diagrame fazoriale: subexcitat, cos φ = 1, supraexcitat ------------------
E_u = np.hypot(Uf, Xs * P1 / (3 * Uf))
fig, axs = plt.subplots(1, 3, figsize=(11, 4.6))
for ax, (titlu, E0f) in zip(axs, (("subexcitat (E₀ = 4,0 kV): cos φ inductiv", 4000.0),
                                   ("excitație normală: cos φ = 1", E_u),
                                   ("supraexcitat (E₀ = 6,34 kV): cos φ capacitiv", 6339.0))):
    I, E = curent(P1, E0f)
    U = Uf + 0j
    sageata(ax, 0j, U, C1, "$\\underline{U}$", offset=(0, 6), ha="center", t=0.85)
    sageata(ax, 0j, I * 15, C2, "$\\underline{I}$", offset=(6, 2), t=1.0)
    sageata(ax, 0j, E, TEXT, "$\\underline{E}_0$", offset=(-8, -6), ha="right", va="top")
    sageata(ax, E, U, C4, "$jX_s\\underline{I}$", offset=(8, 0), va="center")
    d_ = np.angle(E)
    th = np.linspace(0, d_, 30)
    ax.plot(800 * np.cos(th), 800 * np.sin(th), color=TEXT2, lw=1)
    ax.text(900 * np.cos(d_ / 2), 900 * np.sin(d_ / 2) - 150, "δ", color=TEXT, fontsize=11, va="center")
    S = 3 * U * np.conj(I)
    ax.text(0, 2600, f"I = {abs(I):.1f} A\ncos φ = {S.real / abs(S):.3f}".replace(".", ","), color=TEXT,
            fontsize=9, va="top")
    ax.set_xlim(-700, 5600)
    ax.set_ylim(-4900, 2700)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(titlu, fontsize=10)
fig.suptitle("Motor sincron 6 kV, P₁ = 1041,7 kW constantă – ecuația U = E₀ + jX$_s$I (I mărit de 15×)",
             color=TEXT, fontsize=11)
salveaza(fig, "f04-1-fazori-excitatie")

# --- Curbele în V ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.4, 4.4))
for frac, c in ((0.0, C1), (0.5, C2), (1.0, C3)):
    P = frac * P1
    E_min = max(P * Xs / (3 * Uf) * 1.0001, 1500.0)
    E = np.linspace(E_min, 8000, 400)
    I = [abs(curent(P, e)[0]) for e in E]
    ax.plot(E * SQRT3 / 1e3, I, color=c, label=f"P₁ = {frac:g}·P₁ₙ".replace(".", ","))
    if P > 0:
        ax.plot([E_min * SQRT3 / 1e3], [abs(curent(P, E_min)[0])], "o", color=c, ms=7, mec=FUNDAL, mew=2)
# locul geometric cos φ = 1
Pu = np.linspace(0, 1.2 * P1, 100)
Eu = np.hypot(Uf, Xs * Pu / (3 * Uf))
ax.plot(Eu * SQRT3 / 1e3, Pu / (3 * Uf), color=TEXT2, lw=1.2, ls=(0, (5, 3)))
ax.text(Eu[-1] * SQRT3 / 1e3 + 0.1, Pu[-1] / (3 * Uf), "cos φ = 1", color=TEXT, fontsize=9)
ax.axhline(In, color=TEXT2, lw=0.8)
ax.text(14.15, In, "Iₙ", color=TEXT2, fontsize=9, va="center")
ax.text(3.0, 165, "subexcitat\n(absoarbe Q)", color=TEXT, fontsize=9, ha="center")
ax.text(12.4, 165, "supraexcitat\n(furnizează Q)", color=TEXT, fontsize=9, ha="center")
ax.text(10.3, 12, "punctele marcate: limita\nde stabilitate (δ = 90°)", color=TEXT2, fontsize=8.5)
ax.set_xlim(2.5, 14)
ax.set_ylim(0, 200)
ax.set_xlabel("E₀ (de linie) [kV]  ~ proporțională cu I$_e$ în zona liniară")
ax.set_ylabel("I [A]")
ax.set_title("Curbele în V ale motorului sincron (U = 6 kV)")
ax.legend(loc="upper center")
virgula(ax)
salveaza(fig, "f04-3-curbe-V")

# --- Cuplul în funcție de unghiul intern -----------------------------------------
E0, _ = motor_E0(Uf, In, np.arccos(cos_n), Xs)
W1 = 2 * np.pi * 750 / 60
dg = np.linspace(0, 180, 361)
Mmax = 3 * Uf * abs(E0) / Xs / W1
fig, ax = plt.subplots(figsize=(6.8, 3.9))
ax.axvspan(90, 180, color="#f3f2ee", lw=0)
ax.plot(dg, Mmax * np.sin(np.radians(dg)) / 1e3, color=C1)
d0 = np.degrees(-np.angle(E0))
Mr = P1 / W1 / 1e3
ax.axhline(Mr, color=C2, lw=1.6)
ax.plot([d0], [Mr], "o", color=C2, ms=8, mec=FUNDAL, mew=2)
ax.annotate(f"sarcină nominală: δ = {d0:.1f}°".replace(".", ","), xy=(d0, Mr), xytext=(5, 19),
            color=TEXT, arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
ax.annotate(f"M$_{{max}}$ ≈ {Mmax / 1e3:.1f} kN·m (cuplu de desprindere)".replace(".", ","), xy=(90, Mmax / 1e3),
            xytext=(95, 25), color=TEXT, arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
ax.text(120, 3, "desincronizare", color=TEXT, fontsize=9)
ax.set_xlim(0, 180)
ax.set_ylim(0, 27)
ax.set_xlabel("δ [°] (rotorul rămâne în urma câmpului)")
ax.set_ylabel("M [kN·m]")
ax.set_title("M(δ) = 3·U·E₀·sin δ / (X$_s$·Ω₁) – motor MS1000, E₀ nominal")
virgula(ax)
salveaza(fig, "f04-2-cuplu-unghi")
