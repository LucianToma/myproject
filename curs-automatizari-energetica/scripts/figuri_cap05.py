"""Figurile capitolului 5 – Protecția de distanță."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, Wedge
from comun import C1, C2, C3, C4, C5, TEXT, TEXT2, GRILA, FUNDAL, ZONA, salveaza, virgula, bloc, legatura
from modele import SQRT3, DATE, defect_faze
from calcul_cap05 import (ZL1, ZL2, K0, FI_L, K1, Z_ZONE, R_ZONE, T_ZONE, poligon, retea_cu_bara_pe_linie, bucle,
                          masuratori_faze, z_pendulatie, impedante_pendulatie, mho_interior)

d = DATE
POL = [poligon(Z.imag, R) for Z, R in zip(Z_ZONE, R_ZONE)]
CUL_Z = (C1, C3, C4)


def mho(ax, Zr, culoare, eticheta=None, lw=1.6, ls="-"):
    ax.add_patch(Circle((Zr.real / 2, Zr.imag / 2), abs(Zr) / 2, fc="none", ec=culoare, lw=lw, ls=ls, label=eticheta))


def pol(ax, V, culoare, eticheta=None, lw=1.6, ls="-", umplere=False):
    ax.add_patch(Polygon(np.column_stack([V.real, V.imag]), closed=True, fc=ZONA if umplere else "none",
                         ec=culoare, lw=lw, ls=ls, label=eticheta, alpha=1.0))


def linia(ax):
    ax.plot([0, ZL1.real], [0, ZL1.imag], color=TEXT, lw=2.6, solid_capstyle="round", label="linia L1")
    ax.plot([ZL1.real, (ZL1 + ZL2).real], [ZL1.imag, (ZL1 + ZL2).imag], color=TEXT2, lw=2.6, ls=(0, (4, 2)),
            label="linia L2")
    ax.plot([ZL1.real], [ZL1.imag], "o", color=TEXT, ms=5)
    ax.annotate("B", (ZL1.real, ZL1.imag), xytext=(-12, 2), textcoords="offset points", fontsize=9, fontweight="bold")
    ax.annotate("C", ((ZL1 + ZL2).real, (ZL1 + ZL2).imag), xytext=(-12, 2), textcoords="offset points", fontsize=9,
                fontweight="bold")


def plan_rx(ax, xl, yl):
    ax.axhline(0, color=TEXT2, lw=0.8)
    ax.axvline(0, color=TEXT2, lw=0.8)
    ax.set_xlim(*xl)
    ax.set_ylim(*yl)
    ax.set_aspect("equal")
    ax.set_xlabel("R [Ω primar]")
    ax.set_ylabel("X [Ω primar]")
    virgula(ax)


# --- Figura 5.1: cele șase bucle la un defect monofazat și la unul bifazat -----------------
fig, axe = plt.subplots(1, 2, figsize=(11, 4.9))
for ax, tip, titlu in ((axe[0], "1f", "Defect a–pământ la 70 % din L1"), (axe[1], "2f", "Defect b–c la 70 % din L1")):
    r = retea_cu_bara_pe_linie("L1", 0.7)
    V, I, _ = masuratori_faze(r, defect_faze("F", tip))
    Z = bucle(V, I)
    pol(ax, POL[0], C1, "zona 1 (poligon)", umplere=True)
    linia(ax)
    for k, (nume, z) in enumerate(Z.items()):
        if abs(z) > 80:
            continue
        cul = C2 if nume in ("a-p", "bc") else C5
        ax.plot([z.real], [z.imag], "o", color=cul, ms=7, mec=FUNDAL, mew=1.2)
        ax.annotate(nume.replace("-p", "–p"), (z.real, z.imag), xytext=(6, 4), textcoords="offset points", fontsize=9,
                    color=TEXT)
    if tip == "1f":
        zf = V[0] / I[0]
        ax.plot([zf.real], [zf.imag], "s", color=C4, ms=7, mec=FUNDAL, mew=1.2)
        ax.annotate("a–p fără k0", (zf.real, zf.imag), xytext=(6, -10), textcoords="offset points", fontsize=9)
    ax.set_title(titlu)
    plan_rx(ax, (-45, 50), (-40, 40))
axe[0].legend(loc="upper left", fontsize=8.5)
fig.text(0.5, -0.01, "Buclele care nu apar au impedanța în afara desenului (curentul buclei este mic sau nul). "
         "La defectul b–c, buclele b–p și c–p cad în poligon, dar 3I0 ≈ 0, deci selecția fazelor nu le eliberează.",
         ha="center", fontsize=8.5, color=TEXT2, wrap=True)
salveaza(fig, "f05-1-bucle")

# --- Figura 5.2: diagrama timp–distanță ---------------------------------------
z_km = abs(d["z1_110"])
fig, ax = plt.subplots(figsize=(10.5, 4.6))
LA, LB, LC = 0.0, d["lL1"], d["lL1"] + d["lL2"]
for x, nume in ((LA, "A"), (LB, "B"), (LC, "C")):
    ax.axvline(x, color=TEXT2, lw=1.0)
    ax.text(x + 0.8, 0.97, nume, ha="left", va="top", fontsize=11, fontweight="bold")
ax.axhline(0, color=TEXT, lw=1.6)


def trepte(x0, sens, reach_ohm, timpi, culoare, eticheta, semn=1):
    xs = [x0]
    ts = []
    pos = x0
    for k, (zr, t) in enumerate(zip(reach_ohm, timpi)):
        x1 = x0 + sens * zr / z_km
        h = semn * (t + 0.05)
        ax.plot([pos, x1], [h, h], color=culoare, lw=2.4, label=eticheta if k == 0 else None)
        if k + 1 < len(reach_ohm):
            hn = semn * (timpi[k + 1] + 0.05)
            ax.plot([x1, x1], [h, hn], color=culoare, lw=2.4)
        ax.text(x1, h + semn * 0.025, f"Z{k + 1}", ha="center", va="bottom" if semn > 0 else "top", fontsize=8.5,
                color=culoare)
        pos = x1


trepte(LA, +1, [abs(z) for z in Z_ZONE], T_ZONE, C1, "releul din A (spre B, pe L1)")
trepte(LB, +1, [K1 * abs(ZL2), 1.2 * abs(ZL2)], T_ZONE[:2], C3, "releul din B (spre C, pe L2)")
trepte(LB, -1, [K1 * abs(ZL1), 1.2 * abs(ZL1)], T_ZONE[:2], C2, "releul din B (spre A, pe L1)", semn=-1)
trepte(LC, -1, [K1 * abs(ZL2), 1.2 * abs(ZL2)], T_ZONE[:2], C5, "releul din C (spre B, pe L2)", semn=-1)
ax.set_xlim(-12, 100)
ax.set_ylim(-0.95, 1.0)
ax.set_yticks([-0.65, -0.35, -0.05, 0.05, 0.35, 0.65])
ax.set_yticklabels(["0,6", "0,3", "0", "0", "0,3", "0,6"])
ax.set_xlabel("distanța de la A [km] (pentru defecte trifazate metalice)")
ax.set_ylabel("temporizarea [s]")
ax.legend(loc="lower right", fontsize=8.5)
ax.text(99, 0.12, "sus: releele care privesc spre dreapta\njos: releele care privesc spre stânga", ha="right",
        va="bottom", fontsize=8.5, color=TEXT2)
virgula(ax, "x")
salveaza(fig, "f05-2-trepte")

# --- Figura 5.3: caracteristicile mho și poligonale; sarcina -------------------
I_max, U_min = 600.0, 0.9 * d["U110"]
Zs_min = U_min / (SQRT3 * I_max)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 5.2))
for k in range(3):
    mho(a1, Z_ZONE[k], CUL_Z[k], f"zona {k + 1}")
    pol(a2, POL[k], CUL_Z[k], f"zona {k + 1}")
for ax in (a1, a2):
    linia(ax)
    w = Wedge((0, 0), 140, -30, 30, width=140 - Zs_min, fc=ZONA, ec=TEXT2, lw=0.8)
    ax.add_patch(w)
    w2 = Wedge((0, 0), 140, 150, 210, width=140 - Zs_min, fc=ZONA, ec=TEXT2, lw=0.8)
    ax.add_patch(w2)
    ax.text(Zs_min + 6, 3, "domeniul\nde sarcină", fontsize=8.5, color=TEXT2, va="bottom")
a1.set_title("Caracteristici mho (prin origine)")
a2.set_title("Caracteristici poligonale")
plan_rx(a1, (-30, 110), (-25, 45))
plan_rx(a2, (-30, 110), (-25, 45))
a1.legend(loc="upper right", fontsize=8.5)
a2.legend(loc="upper right", fontsize=8.5)
salveaza(fig, "f05-3-caracteristici")

# --- Figura 5.4: rezistența de defect și alimentarea de la celălalt capăt -------
fig, ax = plt.subplots(figsize=(8.6, 6.2))
pol(ax, POL[0], C1, "zona 1 (latura de sus orizontală)", umplere=True)
POL1i = poligon(Z_ZONE[0].imag, R_ZONE[0], inclinare=np.radians(13))
pol(ax, POL1i, C2, "zona 1 cu latura de sus înclinată cu 13°", ls="--")
linia(ax)
Rf = np.linspace(0, 15, 31)
stil = {-15.0: (C3, "δ = −15° (A importă)"), 0.0: (TEXT2, "δ = 0° (fără transfer)"), 15.0: (C5, "δ = +15° (A exportă)")}
for x, mk in ((0.7, "-"), (0.999, ":")):
    for dC, (cul, et) in stil.items():
        zs = []
        for R in Rf:
            r = retea_cu_bara_pe_linie("L1", x, dC)
            V, I, _ = masuratori_faze(r, defect_faze("F", "1f", R))
            zs.append(bucle(V, I)["a-p"])
        zs = np.array(zs)
        ax.plot(zs.real, zs.imag, mk, color=cul, lw=1.8, label=et if x == 0.7 else None)
        k10 = np.argmin(abs(Rf - 10))
        ax.plot([zs[k10].real], [zs[k10].imag], "o", color=cul, ms=5)
ax.annotate("defect la 70 % (linie continuă)", (0.7 * ZL1.real, 0.7 * ZL1.imag), xytext=(-150, 10),
            textcoords="offset points", fontsize=8.5, arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
ax.annotate("defect la bara B (linie punctată)", (ZL1.real, ZL1.imag), xytext=(-170, 25),
            textcoords="offset points", fontsize=8.5, arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
ax.set_title("Impedanța buclei a–p pentru Rf = 0…15 Ω (punctele: Rf = 10 Ω)")
plan_rx(ax, (-8, 32), (-6, 22))
ax.legend(loc="lower right", fontsize=8.3)
salveaza(fig, "f05-4-rezistenta-defect")

# --- Figura 5.5: alimentarea intermediară homopolară (T1) ------------------------
fig, ax = plt.subplots(figsize=(9.5, 4.4))
xs1 = np.linspace(0.02, 0.999, 25)
pos, z3, z1 = [], [], []
for x in xs1:
    r = retea_cu_bara_pe_linie("L1", x)
    V, I, _ = masuratori_faze(r, defect_faze("F", "1f"))
    V3, I3, _ = masuratori_faze(r, defect_faze("F", "3f"))
    pos.append(x * d["lL1"])
    z1.append(abs(bucle(V, I)["a-p"]))
    z3.append(abs(bucle(V3, I3)["ab"]))
for x in np.linspace(0.02, 0.999, 25):
    r = retea_cu_bara_pe_linie("L2", x)
    V, I, _ = masuratori_faze(r, defect_faze("F", "1f"), linie_releu="L1")
    V3, I3, _ = masuratori_faze(r, defect_faze("F", "3f"), linie_releu="L1")
    pos.append(d["lL1"] + x * d["lL2"])
    z1.append(abs(bucle(V, I)["a-p"]))
    z3.append(abs(bucle(V3, I3)["ab"]))
ax.plot(pos, z3, color=C1, label="defect trifazat (bucla a–b)")
ax.plot(pos, z1, color=C2, label="defect monofazat (bucla a–p, compensată)")
for k, Z in enumerate(Z_ZONE):
    ax.axhline(abs(Z), color=CUL_Z[k], lw=1.2, ls="--")
    ax.text(1, abs(Z) + 0.4, f"zona {k + 1}: {abs(Z):.2f} Ω".replace(".", ","), fontsize=8.5, color=CUL_Z[k])
ax.axvline(d["lL1"], color=TEXT2, lw=0.8)
ax.text(d["lL1"] - 0.5, 30, "B (neutrul lui T1\nlegat la pământ)", fontsize=8.5, color=TEXT2, ha="right")
ax.set_xlabel("locul defectului, de la A [km]")
ax.set_ylabel("|Z| văzută din A [Ω primar]")
ax.set_xlim(0, 71)
ax.set_ylim(0, 41)
ax.legend(loc="lower right", fontsize=8.5)
virgula(ax)
salveaza(fig, "f05-5-alimentare-intermediara")

# --- Figura 5.6: pendulații ------------------------------------------------------
ZSA, ZSC, ZT = impedante_pendulatie()
fig, ax = plt.subplots(figsize=(9, 6.6))
for k in range(3):
    mho(ax, Z_ZONE[k], CUL_Z[k], f"zona {k + 1}")
linia(ax)
ax.plot([-ZSA.real, 0], [-ZSA.imag, 0], color=TEXT2, lw=2.0)
ax.plot([(ZL1 + ZL2).real, (ZL1 + ZL2 + ZSC).real], [(ZL1 + ZL2).imag, (ZL1 + ZL2 + ZSC).imag], color=TEXT2, lw=2.0)
ax.annotate("ZSA", (-ZSA.real / 2, -ZSA.imag / 2), xytext=(5, -4), textcoords="offset points", fontsize=8.5)
ax.annotate("ZSC", ((ZL1 + ZL2 + ZSC / 2).real, (ZL1 + ZL2 + ZSC / 2).imag), xytext=(5, -4), textcoords="offset points",
            fontsize=8.5)
for raport, cul, et in ((1.0, C5, "|EA| = |EC|"), (0.85, C2, "|EC| = 0,85·|EA|"), (1.15, C3, "|EC| = 1,15·|EA|")):
    dl = np.radians(np.linspace(20, 340, 641))
    zz = np.array([z_pendulatie(x, raport) for x in dl])
    ax.plot(zz.real, zz.imag, color=cul, lw=1.6, label=f"locul la pendulație, {et}")
for dd in (60, 90, 120, 150, 180, 210, 240, 270, 300):
    z = z_pendulatie(np.radians(dd))
    ax.plot([z.real], [z.imag], "o", color=C5, ms=4)
    ax.annotate(f"{dd}°", (z.real, z.imag), xytext=(4, 3), textcoords="offset points", fontsize=8, color=TEXT2)
for R0, ls in ((45.0, "--"), (35.0, ":"), (-45.0, "--"), (-35.0, ":")):
    t = np.linspace(-40, 80, 2)
    ax.plot(R0 + t * np.cos(FI_L), t * np.sin(FI_L), color=TEXT2, lw=1.1, ls=ls)
ax.text(46, -14, "benzile de detecție\n(R = ±35 Ω și ±45 Ω)", fontsize=8.5, color=TEXT2)
ax.set_title("Locul impedanței văzute din A la pendulații")
plan_rx(ax, (-60, 80), (-30, 55))
ax.legend(loc="lower left", fontsize=8)
salveaza(fig, "f05-6-pendulatii")

# --- Figura 5.7: teleprotecția – logică și diagrame de timp -------------------
t_rel, t_can, t_cb, t_coord = 0.025, 0.010, 0.060, 0.020
fig = plt.figure(figsize=(11.5, 5.6))
axl = fig.add_axes([0.0, 0.0, 0.42, 1.0])
axl.set_xlim(0, 10)
axl.set_ylim(0, 10)
axl.axis("off")
axl.set_title("Logica în stația A", fontsize=11, fontweight="bold")
# POTT
axl.text(0.2, 9.1, "POTT – teledeclanșare permisivă cu supraacoperire", fontsize=9, fontweight="bold", color=TEXT)
bloc(axl, 0.3, 7.6, 2.6, 0.9, "zona extinsă\nînainte (A)", C1)
bloc(axl, 0.3, 6.4, 2.6, 0.9, "semnal permisiv\nprimit de la B", C3)
bloc(axl, 4.2, 7.0, 1.2, 0.9, "ȘI", C5)
bloc(axl, 6.7, 7.0, 2.6, 0.9, "declanșare A", C2)
legatura(axl, (2.9, 8.05), (4.2, 7.6))
legatura(axl, (2.9, 6.85), (4.2, 7.3))
legatura(axl, (5.4, 7.45), (6.7, 7.45))
# PUTT
axl.text(0.2, 5.3, "PUTT – teledeclanșare permisivă cu subacoperire", fontsize=9, fontweight="bold", color=TEXT)
bloc(axl, 0.3, 4.1, 2.6, 0.9, "zona 1 a lui B\n(trimite semnal)", C1)
bloc(axl, 4.2, 4.1, 1.2, 0.9, "ȘI", C5)
bloc(axl, 0.3, 2.9, 2.6, 0.9, "zona extinsă\nînainte (A)", C1)
bloc(axl, 6.7, 4.1, 2.6, 0.9, "declanșare A", C2)
legatura(axl, (2.9, 4.55), (4.2, 4.7))
legatura(axl, (2.9, 3.35), (4.2, 4.3))
legatura(axl, (5.4, 4.55), (6.7, 4.55))
# Blocare
axl.text(0.2, 2.0, "Schema cu blocare (comparație direcțională)", fontsize=9, fontweight="bold", color=TEXT)
bloc(axl, 0.3, 0.8, 2.6, 0.9, "zona extinsă\nînainte (A)", C1)
bloc(axl, 3.4, 0.8, 2.0, 0.9, "ȘI NU\nblocare de la B", C5, fs=7.5)
bloc(axl, 5.7, 0.8, 1.2, 0.9, "t_coord", C4)
bloc(axl, 7.4, 0.8, 2.2, 0.9, "declanșare A", C2)
legatura(axl, (2.9, 1.25), (3.4, 1.25))
legatura(axl, (5.4, 1.25), (5.7, 1.25))
legatura(axl, (6.9, 1.25), (7.4, 1.25))
ax = fig.add_axes([0.47, 0.12, 0.51, 0.78])
semnale = [
    ("zona extinsă din A pornește", t_rel, C1),
    ("zona 1 din B pornește și trimite semnal", t_rel, C3),
    ("semnalul ajunge în A", t_rel + t_can, C3),
    ("declanșare A – POTT/PUTT", t_rel + t_can, C2),
    ("declanșare A – blocare", t_rel + t_coord, C4),
    ("declanșare A – fără canal (zona 2, t2)", t_rel + T_ZONE[1], TEXT2),
]
for k, (nume, t0, cul) in enumerate(semnale):
    y = 1.2 * (len(semnale) - k)
    ax.plot([0, t0 * 1e3, t0 * 1e3, 400], [y, y, y + 0.5, y + 0.5], color=cul, lw=2)
    ax.text(t0 * 1e3 + 6, y + 0.62, nume, ha="left", va="bottom", fontsize=8.5, color=TEXT)
    ax.text(t0 * 1e3 - 4, y + 0.25, f"{t0 * 1e3:.0f} ms", fontsize=8, color=cul, va="center", ha="right")
ax.set_xlim(-60, 400)
ax.set_ylim(0.8, 1.2 * len(semnale) + 1.3)
ax.set_yticks([])
ax.set_xlabel("timpul de la apariția defectului [ms] (defect la 90 % din L1)")
ax.set_title("Diagrama de timp (date de problemă)", fontsize=11)
ax.spines["left"].set_visible(False)
salveaza(fig, "f05-7-teleprotectie")
