"""Figurile capitolului 1 – Regimuri de defect."""

import numpy as np
import matplotlib.pyplot as plt
from comun import C1, C2, C3, C4, C5, TEXT, TEXT2, FUNDAL, salveaza, virgula, sageata, bloc, legatura
from modele import (SQRT3, W0, C_MAX, C_MIN, DATE, A_INV, a_op, kappa, retea_referinta, defect_faze,
                    RN_rezistor)

d = DATE

# --- Figura 1.1: componentele simetrice ale tensiunilor de la bara A, la defect monofazat în B ---
r = retea_referinta(cu_capacitati=False)
p = r.rezolva_faze(defect_faze("B", "1f"))
Vref = C_MAX * d["U110"] / SQRT3
V = r.tensiuni_faze(p, "A") / Vref
V0, V1, V2 = A_INV @ V
fig, axe = plt.subplots(1, 4, figsize=(12, 3.6))
culori = (C1, C2, C3)
titluri = ["Tensiunile de fază\nla bara A (u.r.)", "Secvența directă", "Secvența inversă", "Secvența homopolară"]
seturi = [V, V1 * np.array([1, a_op**2, a_op]), V2 * np.array([1, a_op, a_op**2]), V0 * np.ones(3)]
for ax, tit, S in zip(axe, titluri, seturi):
    lim = 1.15 if ax is axe[0] or ax is axe[1] else 0.25
    for k, (z, c) in enumerate(zip(S, culori)):
        if ax is axe[3] and k > 0:
            continue
        sageata(ax, 0j, z, c, "a, b, c" if ax is axe[3] else "abc"[k], offset=(4, 2), t=1.0, fs=10)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.set_title(tit, fontsize=10)
    ax.axhline(0, color=TEXT2, lw=0.6)
    ax.axvline(0, color=TEXT2, lw=0.6)
    virgula(ax)
axe[0].set_xlabel(f"|Va| = {abs(V[0]):.3f}, |Vb| = {abs(V[1]):.3f}, |Vc| = {abs(V[2]):.3f}".replace(".", ","),
                  fontsize=8.5, color=TEXT2)
axe[1].set_xlabel(f"|V1| = {abs(V1):.3f}".replace(".", ","), fontsize=8.5, color=TEXT2)
axe[2].set_xlabel(f"|V2| = {abs(V2):.3f}".replace(".", ","), fontsize=8.5, color=TEXT2)
axe[3].set_xlabel(f"|V0| = {abs(V0):.3f} (aceeași pe toate fazele)".replace(".", ","), fontsize=8.5, color=TEXT2)
salveaza(fig, "f01-1-componente-simetrice")

# --- Figura 1.2: conectarea rețelelor de secvență pentru defectele nesimetrice ---
fig, axe = plt.subplots(1, 3, figsize=(12, 3.9))
for ax in axe:
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4.4)
    ax.axis("off")


def retea(ax, x, y, txt, c, w=1.5):
    bloc(ax, x, y, w, 0.7, txt, c, fs=8.5)


ax = axe[0]
ax.set_title("monofazat (faza a – pământ)", fontsize=10)
retea(ax, 1.2, 3.3, "directă\nE, Z₁", C1)
retea(ax, 1.2, 2.1, "inversă\nZ₂", C2)
retea(ax, 1.2, 0.9, "homopolară\nZ₀", C3)
for y0, y1 in ((3.3, 2.8), (2.1, 1.6)):
    legatura(ax, (2.7, y0 + 0.2), (2.7, y1), sageata_la_capat=False)
ax.plot([2.7, 3.3, 3.3, 2.7], [3.5, 3.5, 1.1, 1.1], color=TEXT2, lw=1.2)
ax.text(3.4, 2.3, r"$3Z_f$", fontsize=10, color=TEXT2, va="center")
ax.text(2.0, 0.35, "I₁ = I₂ = I₀ (în serie)", ha="center", fontsize=9, color=TEXT)
ax = axe[1]
ax.set_title("bifazat (fazele b – c)", fontsize=10)
retea(ax, 0.4, 2.4, "directă\nE, Z₁", C1)
retea(ax, 2.2, 2.4, "inversă\nZ₂", C2)
ax.plot([1.15, 1.15, 2.95, 2.95], [3.1, 3.6, 3.6, 3.1], color=TEXT2, lw=1.2)
ax.plot([1.15, 1.15, 2.95, 2.95], [2.4, 1.9, 1.9, 2.4], color=TEXT2, lw=1.2)
ax.text(2.0, 3.7, r"$Z_f$", ha="center", fontsize=10, color=TEXT2)
ax.text(2.0, 1.2, "I₁ = −I₂, I₀ = 0\n(rețelele în paralel)", ha="center", fontsize=9, color=TEXT)
ax = axe[2]
ax.set_title("bifazat cu pământ (b – c – pământ)", fontsize=10)
retea(ax, 0.05, 2.4, "directă\nE, Z₁", C1, w=1.1)
retea(ax, 1.45, 2.4, "inversă\nZ₂", C2, w=1.1)
retea(ax, 2.85, 2.4, "homopolară\nZ₀", C3, w=1.1)
ax.plot([0.6, 0.6, 3.4, 3.4], [3.1, 3.6, 3.6, 3.1], color=TEXT2, lw=1.2)
ax.plot([2.0, 2.0], [3.1, 3.6], color=TEXT2, lw=1.2)
ax.plot([0.6, 0.6, 3.4, 3.4], [2.4, 1.9, 1.9, 2.4], color=TEXT2, lw=1.2)
ax.plot([2.0, 2.0], [2.4, 1.9], color=TEXT2, lw=1.2)
ax.text(2.0, 1.2, "I₁ + I₂ + I₀ = 0\n(toate trei în paralel)", ha="center", fontsize=9, color=TEXT)
salveaza(fig, "f01-2-conectare-secvente")

# --- Figura 1.3: curentul de scurtcircuit cu componentă aperiodică la bara B2 ---
s = r.scurtcircuit_secvente("B2", "3f")
Z1 = s["Zth"][1]
Ik = abs(s["I_faza"][0])
R, X = Z1.real, Z1.imag
tau = X / (W0 * R)
phi = np.arctan2(X, R)
t = np.linspace(0, 0.12, 4000)
al = phi - np.pi / 2          # conectare la unghiul care dă componenta aperiodică maximă
i = np.sqrt(2) * Ik * (np.sin(W0 * t + al - phi) - np.sin(al - phi) * np.exp(-t / tau))
idc = -np.sqrt(2) * Ik * np.sin(al - phi) * np.exp(-t / tau)
ip = kappa(R, X) * np.sqrt(2) * Ik
fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(t * 1e3, i / 1e3, color=C1, label="curentul de scurtcircuit i(t)")
ax.plot(t * 1e3, idc / 1e3, color=C2, lw=1.6, ls="--", label="componenta aperiodică")
ax.plot(t * 1e3, (idc + np.sqrt(2) * Ik) / 1e3, color=TEXT2, lw=0.9, ls=":")
ax.plot(t * 1e3, (idc - np.sqrt(2) * Ik) / 1e3, color=TEXT2, lw=0.9, ls=":", label="înfășurătoarea")
ax.axhline(ip / 1e3, color=C3, lw=1.2)
ax.text(119, ip / 1e3 + 0.4, f"ip = κ·√2·I\"k = {ip / 1e3:.2f} kA".replace(".", ","), ha="right", color=C3, fontsize=9)
ax.axhline(np.sqrt(2) * Ik / 1e3, color=TEXT2, lw=0.8)
ax.text(119, np.sqrt(2) * Ik / 1e3 - 1.4, f"√2·I\"k = {np.sqrt(2) * Ik / 1e3:.2f} kA".replace(".", ","),
        ha="right", color=TEXT2, fontsize=9)
ax.set_xlabel("t [ms]")
ax.set_ylabel("i [kA]")
ax.set_ylim(-12, 18)
ax.legend(loc="lower right", ncol=3, fontsize=8.5)
ax.set_title(f"Bara B2: I\"k = {Ik / 1e3:.2f} kA, R/X = {R / X:.3f}, T = X/(ωR) = {tau * 1e3:.1f} ms".replace(".", ","))
virgula(ax)
salveaza(fig, "f01-3-curent-soc")

# --- Figura 1.4: curentul de defect în lungul fiderului F1 ---
r_min80 = retea_referinta(c=C_MIN, cu_capacitati=False, kR20=1 + 0.004 * 60)
lc, la, lb = d["l_cablu_F1"], d["l_lea_F1a"], d["l_lea_F1b"]


def z_traseu(x_km, kR=1.0):
    """Impedanța de secvență directă a fiderului de la B2 până la distanța x (km)."""
    def kz(z):
        return kR * z.real + 1j * z.imag
    zc, zl = kz(d["z1_cablu"]), kz(d["z1_lea20"])
    if x_km <= lc:
        return zc * x_km
    return zc * lc + zl * (x_km - lc)


Z1max = r.scurtcircuit_secvente("B2", "3f")["Zth"][1]
Z1min = r_min80.scurtcircuit_secvente("B2", "3f")["Zth"][1]
x = np.linspace(0, lc + la + lb, 400)
I3 = np.array([C_MAX * d["U20"] / SQRT3 / abs(Z1max + z_traseu(xx)) for xx in x])
I2 = np.array([SQRT3 / 2 * C_MIN * d["U20"] / SQRT3 / abs(Z1min + z_traseu(xx, 1.24)) for xx in x])
fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(x, I3 / 1e3, color=C1, label="trifazat maxim (c = 1,1)")
ax.plot(x, I2 / 1e3, color=C2, label="bifazat minim (c = 1,0; R la 80 °C)")
for xx, nume in ((0, "B2"), (lc + la, "P1"), (lc + la + lb, "P2")):
    ax.axvline(xx, color=TEXT2, lw=0.8, ls=":")
    ax.text(xx + 0.2, 0.15, nume, color=TEXT, fontsize=10, fontweight="bold")
ax.axvspan(0, lc, color="#ecebe7", zorder=0)
ax.text(lc / 2, 5.4, "cablu", ha="center", fontsize=8.5, color=TEXT2)
ax.set_xlabel("distanța de la bara B2 [km]")
ax.set_ylabel("curentul de defect [kA]")
ax.set_ylim(0, 6.8)
ax.legend(loc="upper right", bbox_to_anchor=(0.97, 0.98))
virgula(ax)
salveaza(fig, "f01-4-profil-fider")

# --- Figura 1.5: punerea la pământ în rețeaua de 20 kV ---
Uf = d["U20"] / SQRT3
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw=dict(width_ratios=[1, 1.15]))
ri = retea_referinta("izolat", c=1.0)
pi = ri.rezolva_faze(defect_faze("B2", "1f"))
Vd = ri.tensiuni_faze(pi, "B2") / Uf
pre = ri.tensiuni_faze(ri.rezolva_faze([]), "B2") / Uf
rot = np.exp(-1j * np.angle(pre[0]))          # faza a pe axa reală
Vd, pre = Vd * rot, pre * rot
for k, c in enumerate((C1, C2, C3)):
    a1.plot([0, pre[k].real], [0, pre[k].imag], color=c, lw=1.0, ls=":")
# Neutrul sursei N este în origine, vârfurile triunghiului sunt t.e.m. de fază; potențialul pământului
# devine cel al fazei a (punctul G), iar tensiunile fazelor față de pământ pornesc din G.
G = -np.mean(Vd)          # U_N = U0 față de pământ, deci pământul este în −U0 față de neutru
for k, c in enumerate((C1, C2, C3)):
    if k:
        sageata(a1, G, G + Vd[k], c, f"U{'abc'[k]} față de pământ", offset=(6, 0), t=0.55, fs=8.5)
a1.plot([G.real], [G.imag], "o", color=TEXT, ms=5)
a1.text(G.real + 0.02, G.imag + 0.08, "G = pământul\n(potențialul fazei a)", ha="left", fontsize=8.5, color=TEXT)
a1.plot([0], [0], "o", color=TEXT2, ms=4)
a1.text(-0.05, 0.06, "N", ha="right", fontsize=9, color=TEXT2)
sageata(a1, G, 0j, TEXT2, "U0", offset=(0, -14), t=0.5, lw=1.2, fs=8.5)
a1.set_xlim(-1.3, 1.9)
a1.set_ylim(-1.3, 1.3)
a1.set_aspect("equal")
a1.set_title("Neutru izolat, faza a pusă la pământ\n(punctat: tensiunile înainte de defect)", fontsize=10)
virgula(a1)
# curenții de defect pentru cele trei tratări
C0_tot = (d["c_cablu"] * (d["l_cablu_F1"] + d["l_cablu_rest"]) +
          d["c0_lea20"] * (d["l_lea_F1a"] + d["l_lea_F1b"] + d["l_lea_rest"]))
XN = 1 / (1.1 * 3 * W0 * C0_tot)
rez = []
for nume, net in (("izolat", ri), ("bobină de stingere\n(acord +10 %)", retea_referinta("bobina", c=1.0, Zn_bobina=XN)),
                  ("rezistor\n(300 A)", retea_referinta("rezistor", c=1.0))):
    pp = net.rezolva_faze(defect_faze("B2", "1f"))
    rez.append((nume, abs(net.curent_defect_faze(pp)[0])))
a2.bar(range(3), [v for _, v in rez], color=[C2, C3, C1], width=0.55)
for k, (_, v) in enumerate(rez):
    a2.text(k, v + 6, f"{v:.1f} A".replace(".", ","), ha="center", fontsize=9, color=TEXT)
a2.set_xticks(range(3), [n for n, _ in rez])
a2.set_ylabel("curentul la locul defectului [A]")
a2.set_title("Curentul de punere la pământ (rețeaua de 20 kV din B2)", fontsize=10)
a2.grid(axis="x", visible=False)
a2.set_ylim(0, 380)
salveaza(fig, "f01-5-punere-pamant")
