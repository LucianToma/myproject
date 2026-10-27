"""Figurile capitolului 6 – Protecția generatoarelor și a motoarelor."""

import contextlib
import io
import runpy
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from comun import C1, C2, C3, C4, C5, TEXT, TEXT2, FUNDAL, ZONA, salveaza, virgula, bloc, legatura
from modele import GEN, MOTOR, timp_termic
from calcul_cap06 import (IN_M, IB_M, K_TERMIC, cerc_pierdere_excitatie, impedanta_borne, in_cerc_geometric,
                          tensiune_neutru)

with contextlib.redirect_stdout(io.StringIO()):
    P = runpy.run_path(str(Path(__file__).with_name("probleme_cap06.py")))

G = GEN
M = MOTOR

# --- Figura 6.1: protecțiile grupului generator–transformator ------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 5.2))
ax.set_xlim(0, 12)
ax.set_ylim(0, 6.2)
ax.axis("off")
# circuitul principal: neutru – generator – bare 10,5 kV – TB – bara C
ax.add_patch(Circle((2.2, 3.4), 0.6, fc=FUNDAL, ec=TEXT, lw=1.8))
ax.text(2.2, 3.4, "G1", ha="center", va="center", fontsize=11, fontweight="bold", color=TEXT)
ax.plot([2.8, 6.0], [3.4, 3.4], color=TEXT, lw=2)
ax.add_patch(Circle((6.4, 3.4), 0.42, fc="none", ec=TEXT, lw=1.6))
ax.add_patch(Circle((6.95, 3.4), 0.42, fc="none", ec=TEXT, lw=1.6))
ax.text(6.68, 4.05, "TB 10,5/115 kV", ha="center", fontsize=8.5, color=TEXT)
ax.plot([7.37, 9.6], [3.4, 3.4], color=TEXT, lw=2)
ax.plot([9.6, 9.6], [2.6, 4.2], color=TEXT, lw=4)
ax.text(9.75, 4.3, "bara C\n110 kV", fontsize=8.5, color=TEXT)
ax.add_patch(Rectangle((8.4, 3.2), 0.4, 0.4, fc=FUNDAL, ec=TEXT, lw=1.4))
# neutrul generatorului legat la pământ prin transformatorul de neutru și rezistor
ax.plot([1.6, 1.0, 1.0], [3.4, 3.4, 2.4], color=TEXT, lw=1.4)
ax.add_patch(Rectangle((0.85, 1.6), 0.3, 0.8, fc=FUNDAL, ec=TEXT, lw=1.2))
ax.plot([1.0, 1.0], [1.6, 1.2], color=TEXT, lw=1.4)
ax.plot([0.75, 1.25], [1.2, 1.2], color=TEXT, lw=1.4)
ax.text(0.55, 2.0, "RN", ha="right", fontsize=8.5, color=TEXT)
# funcțiile de protecție
functii = [
    (0.2, 4.7, 1.6, "59N\nU neutru", C3, (1.0, 2.4)),
    (2.0, 5.1, 1.6, "87G\ndiferențială", C1, (2.2, 4.0)),
    (3.8, 5.1, 1.5, "40\npierderea\nexcitației", C2, (3.6, 3.4)),
    (5.4, 5.1, 1.4, "32\nputere\ninversă", C2, (4.4, 3.4)),
    (2.8, 0.5, 1.6, "46\nsarcină\nnesimetrică", C5, (3.4, 3.4)),
    (4.6, 0.5, 1.6, "27/59, 81\nU, f", C4, (4.8, 3.4)),
    (6.4, 0.5, 1.8, "87T\ndiferențiala\nblocului", C1, (6.7, 3.0)),
]
for x, y, w, et, c, (xa, ya) in functii:
    h = 0.95
    bloc(ax, x, y, w, h, et, culoare=c, fs=8.2)
    yb = y if y > ya else y + h
    ax.plot([x + w / 2, xa], [yb, ya], color=c, lw=0.9, ls="--")
salveaza(fig, "f06-1-schema-protectii")

# --- Figura 6.2: protecția termică și protecția de rotor blocat a motorului M1 -----------------------
I = np.logspace(np.log10(1.06), np.log10(8), 400)
t_rece = np.array([timp_termic(x * IN_M, IB_M, K_TERMIC, M["tau"], 0.0) for x in I])
t_cald = np.array([timp_termic(x * IN_M, IB_M, K_TERMIC, M["tau"], IN_M) for x in I])
fig, ax = plt.subplots(figsize=(9.5, 5.6))
ax.plot(I, t_rece, color=C1, label="protecția termică, din stare rece")
ax.plot(I, t_cald, color=C2, label="protecția termică, din stare caldă (după funcționare la In)")
I_set = P["I_set"] / IN_M
ax.plot([I_set, I_set, 8], [1e4, P["t_set"], P["t_set"]], color=C5, lw=1.8,
        label=f"rotor blocat: I > {I_set:.0f}·In, t = {P['t_set']:.0f} s".replace(".", ","))
ax.plot([M["Ip_In"]], [M["t_pornire"]], "o", color=C3, ms=9, mec=FUNDAL, mew=1.5,
        label=f"pornirea: {M['Ip_In']:.0f}·In timp de {M['t_pornire']:.0f} s")
ax.plot([M["Ip_In"]], [M["t_blocat_cald"]], "v", color=TEXT, ms=8, label="timpul admis cu rotorul blocat (cald / rece)")
ax.plot([M["Ip_In"]], [M["t_blocat_rece"]], "v", color=TEXT, ms=8)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(1, 8)
ax.set_ylim(1, 1e4)
ax.set_xlabel("I / In")
ax.set_ylabel("timpul de declanșare [s]")
ax.grid(True, which="both", lw=0.5)
ax.legend(loc="lower left", fontsize=8.5)
ax.set_xticks([1, 1.5, 2, 3, 4, 6, 8])
ax.xaxis.set_minor_formatter(plt.NullFormatter())
ax.set_title(f"Motorul M1: model termic cu k = {K_TERMIC:.2f}, τ = {M['tau']:.0f} s".replace(".", ","), fontsize=10)
virgula(ax)
salveaza(fig, "f06-2-termic")

# --- Figura 6.3: pierderea excitației în planul R–X ------------------------------------------------
sus, jos, centru, raza = cerc_pierdere_excitatie()
xe = P["xe"]
fig, ax = plt.subplots(figsize=(8.5, 7.2))
th = np.linspace(0, 2 * np.pi, 400)
cerc = centru + raza * np.exp(1j * th)
ax.fill(cerc.real, cerc.imag, color=ZONA, lw=0)
ax.plot(cerc.real, cerc.imag, color=TEXT, lw=1.8, label="caracteristica 40 (decalaj −x'd/2, diametru xd)")
# punctele normale
for nume, Pp, Qp in P["puncte"]:
    Z = 1.0 / np.conj(Pp + 1j * Qp)
    ax.plot(Z.real, Z.imag, "o", color=C3, ms=7, mec=FUNDAL)
ax.plot([], [], "o", color=C3, ms=7, label="regimuri normale (problema 6.5)")
# traiectoria la scăderea excitației (P = 0,85), din regimul nominal până la limita de stabilitate
V = P["V_ret"]
Es = np.linspace(abs(P["E_init"]), P["E_lim"], 80)
Zt = np.array([impedanta_borne(E, np.arcsin(np.clip(0.85 * (G["xd"] + xe) / (E * V), -1, 1)), G["xd"], xe, V)[0]
               for E in Es])
ax.plot(Zt.real, Zt.imag, color=C1, lw=2, label="excitația scade (P = 0,85), din regimul nominal până la δ = 90°")
deltas = np.radians(np.linspace(90, 360, 600))
Zs = np.array([impedanta_borne(P["E_lim"], dd, G["xd"], xe, V)[0] for dd in deltas])
ok = np.abs(Zs) < 3
ax.plot(Zs.real[ok], Zs.imag[ok], color=C2, lw=1.6, ls="--", label="alunecarea polilor (δ = 90° … 360°)")
ax.plot([0], [-G["xd"]], "D", color=C5, ms=8, mec=FUNDAL, label="excitație pierdută complet: Z = −j·xd")
ax.axhline(0, color=TEXT2, lw=0.7)
ax.axvline(0, color=TEXT2, lw=0.7)
ax.set_xlim(-1.4, 1.6)
ax.set_ylim(-1.75, 1.0)
ax.set_aspect("equal")
ax.set_xlabel("R [u.r.]")
ax.set_ylabel("X [u.r.]")
ax.legend(loc="upper left", fontsize=8.2)
virgula(ax)
salveaza(fig, "f06-3-pierderea-excitatiei")

# --- Figura 6.4: punerea la pământ a statorului: tensiunea neutrului ----------------------------------
x = np.linspace(0, 1, 401)
Ef, RN, C = P["Ef"], P["RN"], P["C"]
fig, ax = plt.subplots(figsize=(9.5, 4.8))
for Rf, c in ((1e-3, C1), (10e3, C2), (30e3, C3)):
    UN = np.abs(tensiune_neutru(x, Rf, RN, C, Ef)) / Ef
    ax.plot(100 * x, 100 * UN, color=c, label=("defect metalic" if Rf < 1 else f"Rf = {Rf / 1e3:.0f} kΩ"))
ax.axhline(100 * P["UN_set"], color=TEXT, ls="--", lw=1.2, label="reglajul 59N: 5 % Uf")
ax.axvspan(0, 5, color=ZONA, lw=0)
ax.text(6, 86, "zona neacoperită de 59N\n(primii 5 % de la neutru)\n→ metode de 100 %", fontsize=8.5, color=TEXT2)
ax.set_xlim(0, 100)
ax.set_ylim(0, 105)
ax.set_xlabel("poziția defectului în înfășurare, de la neutru [%]")
ax.set_ylabel("tensiunea neutrului $U_N$ [% din $U_f$]")
ax.legend(loc="center right", fontsize=8.5)
virgula(ax)
salveaza(fig, "f06-4-pamant-stator")
