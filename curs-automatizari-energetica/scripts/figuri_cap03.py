"""Figurile capitolului 3 – Protecția maximală de curent."""

import contextlib
import io
import runpy
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from comun import C1, C2, C3, C4, C5, TEXT, TEXT2, FUNDAL, ZONA, salveaza, virgula, sageata, bloc
from modele import timp_invers, retea_referinta, defect_faze

# Reglajele sunt luate direct din rezolvarea problemelor (aceeași sursă de adevăr)
with contextlib.redirect_stdout(io.StringIO()):
    P = runpy.run_path(str(Path(__file__).with_name("probleme_cap03.py")))
relee, I3, I_inst, T_INST = P["relee"], P["I3"], P["I_inst_R1"], P["T_INST"]

# --- Figura 3.1: caracteristicile dependente IEC și IEEE ---
G = np.logspace(np.log10(1.05), np.log10(30), 300)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
for ax, curbe, tms, tit in ((a1, (("SI", "normal invers (SI)"), ("VI", "foarte invers (VI)"),
                                    ("EI", "extrem de invers (EI)")), 0.1, "IEC 60255-151, TMS = 0,1"),
                             (a2, (("MI-IEEE", "moderat invers (MI)"), ("VI-IEEE", "foarte invers (VI)"),
                                   ("EI-IEEE", "extrem de invers (EI)")), 1.0, "IEEE C37.112, TD = 1")):
    for (cod, et), c in zip(curbe, (C1, C2, C3)):
        ax.plot(G, timp_invers(G, 1.0, tms, cod), color=c, label=et)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(1, 30)
    ax.set_ylim(0.01, 100)
    ax.set_xlabel("I / Is")
    ax.set_title(tit, fontsize=10)
    ax.legend(loc="upper right", fontsize=8.5)
    ax.grid(True, which="both", lw=0.5)
    virgula(ax)
a1.set_ylabel("timpul de acționare [s]")
salveaza(fig, "f03-1-curbe-dependente")

# --- Figura 3.2: coordonarea protecțiilor maximale pe fiderul F1 ---
fig, ax = plt.subplots(figsize=(10, 5.6))
I = np.logspace(np.log10(60), np.log10(8000), 600)
culori = {"R3": C3, "R2": C2, "R1": C1, "R0": C5}
for nume in ("R3", "R2", "R1", "R0"):
    rl = relee[nume]
    t = timp_invers(I, rl["Is"], rl["TMS"])
    if nume == "R1":
        t = np.where(I >= I_inst, T_INST, t)
    ax.plot(I, t, color=culori[nume], label=f"{nume}: Is = {rl['Is']:.0f} A, TMS = {rl['TMS']:.2f}".replace(".", ",")
            + (f", I>> = {I_inst:.0f} A" if nume == "R1" else ""))
for b, et in (("P2", "I\"k3max(P2)"), ("P1", "I\"k3max(P1)"), ("B2", "I\"k3max(B2)")):
    ax.axvline(I3[b], color=TEXT2, lw=0.8, ls=":")
    ax.text(I3[b] * 1.02, 22, f"{et}\n{I3[b]:.0f} A", fontsize=8, color=TEXT2, va="top")
# marjele în punctele de coordonare
for sus, jos, Ic in (("R2", "R3", I3["P2"]), ("R1", "R2", I3["P1"]), ("R0", "R1", I_inst)):
    t_s = float(timp_invers(Ic, relee[sus]["Is"], relee[sus]["TMS"]))
    t_j = float(timp_invers(Ic, relee[jos]["Is"], relee[jos]["TMS"]))
    ax.annotate("", xy=(Ic, t_s), xytext=(Ic, t_j), arrowprops=dict(arrowstyle="<->", color=TEXT, lw=1.0))
    ax.text(Ic * 0.97, np.sqrt(t_s * t_j), f"{t_s - t_j:.2f} s".replace(".", ","), ha="right", va="center",
            fontsize=8.5, color=TEXT)
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(60, 8000)
ax.set_ylim(0.02, 30)
ax.set_xlabel("curentul primar la 20 kV [A]")
ax.set_ylabel("timpul de acționare [s]")
ax.grid(True, which="both", lw=0.5)
ax.legend(loc="lower left", fontsize=8.5)
ax.set_title("Coordonarea protecțiilor maximale R3 – R2 – R1 – R0 (caracteristica SI)", fontsize=10)
virgula(ax)
salveaza(fig, "f03-2-coordonare")

# --- Figura 3.3: protecția barelor prin blocare – diagrama de timp ---
fig, axe = plt.subplots(2, 1, figsize=(10, 4.6), sharex=True)
semnale = ["defect", "pornire R1 (I>)", "blocare spre R0", "treapta rapidă R0 (0,10 s)", "declanșare"]
for ax, caz in zip(axe, ("defect pe fiderul F1 (în aval de R1)", "defect pe bara B2")):
    for k, sg in enumerate(semnale):
        y = len(semnale) - 1 - k
        ax.text(-0.02, y + 0.3, sg, ha="right", va="center", fontsize=8.5, color=TEXT)
        ax.plot([0, 0.5], [y, y], color="#d6d5d0", lw=0.8)
    def puls(ax, y, t0, t1, c):
        ax.fill_between([t0, t1], y, y + 0.6, color=c, alpha=0.85, lw=0)
    puls(ax, 4, 0.0, 0.10 if "fider" in caz else 0.16, C2)
    if "fider" in caz:
        puls(ax, 3, 0.02, 0.11, C1)
        puls(ax, 2, 0.023, 0.12, C1)   # blocarea ajunge la R0 după 23 ms (problema 9.3)
        ax.text(0.14, 1.3, "R0 rămâne blocat cât timp R1 este pornit (nu ajunge la 0,10 s)", fontsize=8.5,
                color=TEXT2)
        puls(ax, 0, 0.04, 0.10, C3)
        ax.text(0.105, 0.3, "R1 (I>>, 0,04 s) + întrerupător (0,06 s): defect eliminat la 0,10 s", fontsize=8,
                color=TEXT2, va="center")
    else:
        ax.text(0.05, 3.3, "niciun releu de fider nu pornește", fontsize=8.5, color=TEXT2, va="center")
        puls(ax, 1, 0.0, 0.10, C5)
        puls(ax, 0, 0.10, 0.16, C3)
        ax.text(0.165, 0.3, "R0 + întrerupător: 0,10 + 0,06 = 0,16 s", fontsize=8, color=TEXT2, va="center")
    ax.set_title(caz, fontsize=10, loc="left")
    ax.set_ylim(-0.2, 5)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.grid(False)
axe[-1].set_xlabel("t [s]")
axe[-1].set_xlim(0, 0.5)
virgula(axe[-1], "x")
salveaza(fig, "f03-3-blocare-bare")

# --- Figura 3.4: direcția curentului homopolar (neutru izolat și rezistor) ---
fig, axe = plt.subplots(1, 2, figsize=(10.5, 4.6))
for ax, (neutru, tit) in zip(axe, (("izolat", "Neutru izolat"), ("rezistor", "Neutru tratat prin rezistor (300 A)"))):
    net = retea_referinta(neutru, c=1.0)
    for loc, c, et in (("P1", C2, "fider defect"), ("B2", C1, "fider sănătos")):
        p = net.rezolva_faze(defect_faze(loc, "1f"))
        I0 = np.sum(net.curenti_ramura_faze(p, "F1a", 1))
        U0 = np.mean(net.tensiuni_faze(p, "B2"))
        z = I0 / abs(I0) * np.exp(-1j * np.angle(U0))      # 3I0 raportat la direcția lui U0
        sageata(ax, 0j, z, c, f"3I0 – {et}\n({abs(I0):.1f} A)".replace(".", ","), offset=(4, 4), t=1.0, fs=8.5)
    sageata(ax, 0j, 1 + 0j, TEXT, "U0 (referință)", offset=(-60, 6), t=1.0, lw=2.4, fs=8.5)
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect("equal")
    ax.axhline(0, color=TEXT2, lw=0.6)
    ax.axvline(0, color=TEXT2, lw=0.6)
    ax.set_title(tit, fontsize=10)
    virgula(ax)
fig.text(0.5, 0.01, "fazori normați (lungime unitară); fiderul F1, defect pe F1 în P1 sau pe bara B2",
         ha="center", fontsize=8.5, color=TEXT2)
salveaza(fig, "f03-4-directie-homopolara")
