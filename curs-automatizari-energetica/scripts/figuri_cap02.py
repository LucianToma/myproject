"""Figurile capitolului 2 – Transformatoare de măsură."""

import numpy as np
import matplotlib.pyplot as plt
import schemdraw
import schemdraw.elements as elm
from scipy.optimize import brentq
from comun import C1, C2, C3, C4, TEXT, TEXT2, FUNDAL, salveaza, salveaza_schema, virgula, sageata
from modele import SQRT3, W0, DATE, retea_referinta, defect_faze, flux_tc, tc_neliniar, a_op

schemdraw.use("matplotlib")
schemdraw.config(fontsize=12, bgcolor=FUNDAL, lw=1.6)
d = DATE

# --- Figura 2.1: schema echivalentă a TC raportată la secundar ---
with schemdraw.Drawing(show=False) as dr:
    dr += elm.SourceI().up().label("I₁/n", loc="left")
    dr += elm.Line().right().length(1.5)
    dr.push()
    dr += elm.Inductor().down().label("Lm\n(magnetizare)", loc="bottom").color(C2)
    dr += elm.Line().left().length(1.5)
    dr.pop()
    dr += elm.Line().right().length(0.8)
    dr += elm.Resistor().right().label("Rct\n(înfășurarea\nsecundară)").color(C1)
    dr += elm.Line().right().length(1.2).label("I₂ →")
    dr += elm.Resistor().down().label("Rb\n(conductoare\n+ releu)", loc="bottom").color(C3)
    dr += elm.Line().left().length(5.5)
salveaza_schema(dr, "f02-1-tc-schema")

# --- Figura 2.2: saturația TC sub componenta aperiodică (problema 2.2) ---
r = retea_referinta(cu_capacitati=False)
s = r.scurtcircuit_secvente("B2", "3f")
Ik, Z1 = abs(s["I_faza"][0]), s["Zth"][1]
I2 = Ik / 400.0
R2 = 1.5 + 0.0178 * 200 / 2.5 + 0.1
T1 = Z1.imag / (W0 * Z1.real)
E_ALF = 20 * 1.0 * (1.5 + 5.0)
psi_sat = np.sqrt(2) * E_ALF / W0
t = np.arange(0, 0.06, 2e-6)
i2 = np.sqrt(2) * I2 * (np.exp(-t / T1) - np.cos(W0 * t))
i2_nl = tc_neliniar(t, I2, R2, T1, psi_sat)
psi = flux_tc(t, I2, R2, T1)
t_sat = brentq(lambda tt: flux_tc(tt, I2, R2, T1) - psi_sat, 1e-4, 0.05)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 5.6), sharex=True, gridspec_kw=dict(height_ratios=[1.3, 1]))
a1.plot(t * 1e3, i2, color=TEXT2, lw=1.2, ls="--", label="curentul primar raportat (TC ideal)")
a1.plot(t * 1e3, i2_nl, color=C1, label="curentul secundar (TC care se saturează)")
a1.set_ylabel("i₂ [A]")
a1.legend(loc="upper right", fontsize=8.5)
a1.axvline(t_sat * 1e3, color=C2, lw=1.0, ls=":")
a2.plot(t * 1e3, psi, color=C2, label="fluxul cerut de un TC ideal ψ(t)")
a2.axhline(psi_sat, color=C3, lw=1.2)
a2.text(59, psi_sat + 0.1, f"ψ_sat = {psi_sat:.3f} V·s".replace(".", ","), ha="right", color=C3, fontsize=9)
a2.axvline(t_sat * 1e3, color=C2, lw=1.0, ls=":")
a2.text(t_sat * 1e3 + 0.8, 1.55, f"t_sat = {t_sat * 1e3:.1f} ms".replace(".", ","), color=C2, fontsize=9)
a2.set_ylabel("ψ [V·s]")
a2.set_xlabel("t [ms]")
a2.legend(loc="lower right", fontsize=8.5)
for ax in (a1, a2):
    virgula(ax)
a1.set_title(f"TC 400/1 A, 5P20 – defect la începutul fiderului F1 (I\"k = {Ik / 1e3:.2f} kA), sarcină R₂ = {R2:.2f} Ω, "
             f"T₁ = {T1 * 1e3:.1f} ms".replace(".", ","), fontsize=10)
salveaza(fig, "f02-2-saturatie")

# --- Figura 2.3: tensiunile secundare ale înfășurărilor pentru triunghiul deschis ---
fig, axe = plt.subplots(1, 2, figsize=(10, 4.2))
Uf = d["U20"] / SQRT3
n_td = Uf / (100 / 3)
ri = retea_referinta("izolat", c=1.0)
normal = ri.tensiuni_faze(ri.rezolva_faze([]), "B2")
defect = ri.tensiuni_faze(ri.rezolva_faze(defect_faze("B2", "1f")), "B2")
rot = np.exp(-1j * np.angle(normal[0]))
for ax, Vt, tit in ((axe[0], normal * rot / n_td, "Regim normal: suma este nulă"),
                    (axe[1], defect * rot / n_td, "Faza a pusă la pământ (neutru izolat)")):
    cap = 0j
    for k, c in enumerate((C1, C2, C3)):
        if abs(Vt[k]) > 1:
            sageata(ax, cap, cap + Vt[k], c, f"u{'abc'[k]}", offset=(5, 0), t=0.5)
        cap = cap + Vt[k]
    if abs(cap) > 1:
        sageata(ax, 0j, cap, TEXT, f"3U₀ = {abs(cap):.1f} V".replace(".", ","), offset=(0, 6), t=0.5, lw=2.4,
                ha="center")
    ax.plot([0], [0], "o", color=TEXT2, ms=4)
    ax.set_xlim(-110, 60)
    ax.set_ylim(-75, 75)
    ax.set_aspect("equal")
    ax.set_title(tit, fontsize=10)
    ax.set_xlabel("[V]")
    virgula(ax)
salveaza(fig, "f02-3-triunghi-deschis")

# --- Figura 2.4: tensiunea la triunghiul deschis în funcție de rezistența de defect ---
Rf = np.logspace(0, np.log10(3000), 160)
fig, ax = plt.subplots(figsize=(9, 3.8))
for nume, net, c in (("neutru izolat", ri, C2), ("rezistor de neutru (300 A)", retea_referinta("rezistor", c=1.0), C1)):
    u = []
    for R in Rf:
        sq = net.scurtcircuit_secvente("B2", "1f", Zf=R)
        u.append(3 * abs(sq["V_seq"][0][sq["idx"]["B2"]]) / n_td)
    ax.plot(Rf, u, color=c, label=nume)
ax.set_xscale("log")
ax.set_xlabel("rezistența de defect Rf [Ω]")
ax.set_ylabel("3U₀ la triunghiul deschis [V]")
ax.set_ylim(0, 110)
ax.legend(loc="upper right")
ax.set_title("Punere la pământ la bara B2: tensiunea homopolară scade cu rezistența de defect", fontsize=10)
virgula(ax, "y")
salveaza(fig, "f02-4-u0-rezistenta-defect")
