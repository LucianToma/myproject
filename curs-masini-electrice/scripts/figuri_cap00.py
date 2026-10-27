"""Figurile capitolului 0 – Noțiuni fundamentale."""

import numpy as np
import matplotlib.pyplot as plt
from comun import C1, C2, C3, C4, TEXT, TEXT2, GRILA, salveaza, virgula, sageata

# --- Curba de magnetizare și ciclul de histerezis (formă calitativă) -------------
H = np.linspace(-4000, 4000, 2001)
Bs, H0, Hc = 1.6, 450.0, 120.0
f = lambda h: Bs * np.tanh(h / H0) + 4e-7 * np.pi * h
fig, ax = plt.subplots(figsize=(6.4, 4.0))
hp = np.linspace(0, 4000, 500)
ax.plot(hp, f(hp), color=C1, label="curba de primă magnetizare")
ax.plot(H, f(H - Hc), color=C2, label="ciclul de histerezis")
ax.plot(H, f(H + Hc), color=C2)
ax.axhline(0, color=TEXT2, lw=0.8)
ax.axvline(0, color=TEXT2, lw=0.8)
ax.annotate("$B_r$ (inducție remanentă)", xy=(0, f(Hc)), xytext=(-3900, 1.25), color=TEXT,
            arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
ax.annotate("$H_c$ (câmp coercitiv)", xy=(-Hc, 0), xytext=(-3900, -0.55), color=TEXT,
            arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
ax.annotate("cot de saturație", xy=(700, f(700)), xytext=(1300, 0.7), color=TEXT,
            arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
ax.set_xlabel("H [A/m]")
ax.set_ylabel("B [T]")
ax.set_title("Oțel electrotehnic – formă calitativă")
ax.legend(loc="lower right")
virgula(ax)
salveaza(fig, "f00-1-magnetizare")

# --- Câmpul magnetic învârtitor ------------------------------------------------
fig, axs = plt.subplots(1, 4, figsize=(10, 2.9))
culori = [C1, C2, C3]
for ax, grade in zip(axs, (0, 30, 60, 90)):
    wt = np.radians(grade)
    total = 0j
    for k in range(3):
        directie = np.exp(1j * 2 * np.pi * k / 3)
        v = np.cos(wt - 2 * np.pi * k / 3) * directie
        total += v
        ax.plot([0, 1.7 * directie.real], [0, 1.7 * directie.imag], color=GRILA, lw=1, zorder=0)
        ax.text(1.85 * directie.real, 1.85 * directie.imag, "abc"[k], color=TEXT2, fontsize=9,
                ha="center", va="center")
        sageata(ax, 0j, v, culori[k], lw=1.6)
    sageata(ax, 0j, total, TEXT, lw=2.4)
    ax.add_patch(plt.Circle((0, 0), 1.5, fill=False, ls="-", lw=0.8, color=TEXT2))
    ax.set_xlim(-2.0, 2.0)
    ax.set_ylim(-2.0, 2.0)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"ωt = {grade}°", fontsize=10)
fig.legend(handles=[plt.Line2D([], [], color=c, lw=2) for c in culori + [TEXT]],
           labels=["solenația fazei a", "faza b", "faza c", "rezultanta (1,5·F$_m$)"],
           loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.06))
fig.suptitle("Câmpul învârtitor: rezultanta are amplitudine constantă și se rotește cu ωt", color=TEXT, fontsize=11)
salveaza(fig, "f00-2-camp-invartitor")

# --- Sistemul trifazat de tensiuni -------------------------------------------
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.4), gridspec_kw=dict(width_ratios=[2.2, 1]))
t = np.linspace(0, 20e-3, 1000)
Um = 230 * np.sqrt(2)
for k, (nume, c) in enumerate(zip(("$u_a$", "$u_b$", "$u_c$"), (C1, C2, C3))):
    ax1.plot(t * 1e3, Um * np.cos(2 * np.pi * 50 * t - 2 * np.pi * k / 3), color=c, label=nume)
    z = 230 * np.exp(-1j * 2 * np.pi * k / 3)
    sageata(ax2, 0j, z, c, eticheta=["$\\underline{U}_a$", "$\\underline{U}_b$", "$\\underline{U}_c$"][k],
            offset=[(4, 2), (-26, -4), (4, 2)][k])
uab = 230 * (1 - np.exp(-1j * 2 * np.pi / 3))
sageata(ax2, 230 * np.exp(-1j * 2 * np.pi / 3), 230 + 0j, C4, eticheta="$\\underline{U}_{ab}=\\sqrt{3}\\,U_f$",
        offset=(6, 0), lw=1.6)
ax1.set_xlabel("t [ms]")
ax1.set_ylabel("u [V]")
ax1.set_title("Valori instantanee (U$_f$ = 230 V, 50 Hz)")
ax1.legend(loc="upper center", ncol=3, bbox_to_anchor=(0.5, -0.2))
ax2.set_xlim(-260, 330)
ax2.set_ylim(-260, 260)
ax2.set_aspect("equal")
ax2.axis("off")
ax2.set_title("Fazori (decalaj 120°)")
virgula(ax1)
salveaza(fig, "f00-3-sistem-trifazat")

# --- Conexiunile stea și triunghi -------------------------------------------
def impedanta(ax, z0, z1, eticheta=None):
    """Dreptunghi (impedanță) pe segmentul z0–z1."""
    d = z1 - z0
    u = d / abs(d)
    a, b = z0 + 0.3 * d, z0 + 0.7 * d
    n = 1j * u * 0.09
    pts = [a + n, b + n, b - n, a - n, a + n]
    ax.plot([z0.real, a.real], [z0.imag, a.imag], color=TEXT, lw=1.4)
    ax.plot([b.real, z1.real], [b.imag, z1.imag], color=TEXT, lw=1.4)
    ax.fill([p.real for p in pts], [p.imag for p in pts], facecolor="#ffffff", edgecolor=C1, lw=1.6)
    if eticheta:
        c = (a + b) / 2 + 1j * u * 0.22
        ax.text(c.real, c.imag, eticheta, color=TEXT, ha="center", va="center", fontsize=9)


fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.8))
# stea
N = 0 + 0j
capete = [0 + 1.2j, -1.04 - 0.6j, 1.04 - 0.6j]
for z, f_ in zip(capete, "abc"):
    impedanta(a1, N, z, "Z")
    linie = z * 1.45
    a1.plot([z.real, linie.real], [z.imag, linie.imag], color=TEXT, lw=1.4)
    a1.text(linie.real * 1.08, linie.imag * 1.08, f_.upper(), ha="center", va="center", color=TEXT, fontsize=11)
a1.plot([0], [0], "o", color=TEXT, ms=5)
a1.text(-0.12, 0.12, "N", color=TEXT2, fontsize=10, ha="right", va="bottom")
a1.text(-1.7, -1.55, "$U_f = U_l/\\sqrt{3}$,  $I_f = I_l$", color=TEXT, fontsize=10)
a1.set_title("Conexiunea stea (Y)")
# triunghi
v = [0 + 1.15j, -1.0 - 0.58j, 1.0 - 0.58j]
for i in range(3):
    impedanta(a2, v[i], v[(i + 1) % 3], "Z")
for z, f_ in zip(v, "abc"):
    linie = z * 1.45
    a2.plot([z.real, linie.real], [z.imag, linie.imag], color=TEXT, lw=1.4)
    a2.plot([z.real], [z.imag], "o", color=TEXT, ms=5)
    a2.text(linie.real * 1.08, linie.imag * 1.08, f_.upper(), ha="center", va="center", color=TEXT, fontsize=11)
a2.text(-1.7, -1.55, "$U_f = U_l$,  $I_f = I_l/\\sqrt{3}$", color=TEXT, fontsize=10)
a2.set_title("Conexiunea triunghi (Δ)")
for a in (a1, a2):
    a.set_xlim(-1.9, 1.9)
    a.set_ylim(-1.75, 2.0)
    a.set_aspect("equal")
    a.axis("off")
salveaza(fig, "f00-4-stea-triunghi")
