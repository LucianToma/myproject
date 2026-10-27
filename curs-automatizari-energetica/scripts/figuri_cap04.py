"""Figurile capitolului 4 – Protecția diferențială."""

import contextlib
import io
import runpy
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from comun import C1, C2, C3, C4, C5, TEXT, TEXT2, FUNDAL, ZONA, salveaza, virgula, sageata
from modele import retea_referinta, defect_faze, C_MIN
from calcul_cap04 import (IN_IT, IN_JT, marimi_releu, prag_diferential, IDIFF_NEFRANAT, ARMONICA2,
                          simuleaza_inrush, raport_armonica2_alunecator)

# Valorile sunt luate direct din rezolvarea problemelor (aceeași sursă de adevăr)
with contextlib.redirect_stdout(io.StringIO()):
    P = runpy.run_path(str(Path(__file__).with_name("probleme_cap04.py")))


# --- Figura 4.1: principiul curenților circulanți (Merz–Price) ----------------------------------
def schema_principiu(ax, interior):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    # conductorul primar și obiectul protejat
    ax.plot([0.3, 9.7], [4.6, 4.6], color=TEXT, lw=2.4)
    ax.add_patch(Rectangle((3.6, 4.15), 2.8, 0.9, fc="#d9d8d3", ec=TEXT2, lw=1.2, zorder=3))
    ax.text(5.0, 4.6, "obiect protejat", ha="center", va="center", fontsize=8.5, color=TEXT, zorder=4)
    # transformatoarele de curent
    for x in (2.4, 7.6):
        ax.add_patch(Circle((x, 4.6), 0.32, fc="none", ec=C1, lw=1.8, zorder=3))
        ax.text(x, 5.15, "TC", ha="center", fontsize=8.5, color=C1)
    # circuitele secundare
    ax.plot([2.4, 2.4, 7.6, 7.6], [4.28, 2.6, 2.6, 4.28], color=C1, lw=1.4)
    ax.plot([2.4, 2.4, 7.6, 7.6], [4.28, 1.0, 1.0, 4.28], color=C1, lw=1.4)
    ax.plot([5.0, 5.0], [2.6, 1.0], color=C1, lw=1.4)
    ax.add_patch(Rectangle((4.6, 1.45), 0.8, 0.7, fc=FUNDAL, ec=C2, lw=1.6, zorder=3))
    ax.text(5.0, 1.8, "R", ha="center", va="center", fontsize=10, color=C2, fontweight="bold", zorder=4)
    if interior:
        ax.annotate("", xy=(5.0, 3.55), xytext=(5.0, 4.15), arrowprops=dict(arrowstyle="-|>", color=C2, lw=1.6))
        ax.text(5.15, 3.75, "defect", fontsize=8.5, color=C2)
        sageti = [((0.6, 4.85), (1.6, 4.85), "I₁"), ((9.4, 4.85), (8.4, 4.85), "I₂")]
        ax.annotate("", xy=(4.75, 2.25), xytext=(4.75, 2.55), arrowprops=dict(arrowstyle="-|>", color=C2, lw=1.4))
        ax.text(5.6, 2.15, "i₁ + i₂ → acționează", fontsize=8.5, color=C2)
        titlu = "Defect interior: curenții secundari se adună în releu"
    else:
        ax.annotate("", xy=(9.7, 3.9), xytext=(9.7, 4.5), arrowprops=dict(arrowstyle="-|>", color=C2, lw=1.6))
        ax.text(9.4, 3.6, "defect\nexterior", fontsize=8.5, color=C2, ha="center")
        sageti = [((0.6, 4.85), (1.6, 4.85), "I"), ((8.4, 4.85), (9.4, 4.85), "I")]
        ax.annotate("", xy=(4.1, 2.75), xytext=(3.1, 2.75), arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.3))
        ax.annotate("", xy=(6.9, 2.75), xytext=(5.9, 2.75), arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.3))
        ax.text(5.6, 2.15, "i − i = 0 → nu acționează", fontsize=8.5, color=C1)
        titlu = "Defect exterior: curentul circulă prin secundare, nu prin releu"
    for (p0, p1, et) in sageti:
        ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", color=TEXT, lw=1.4))
        ax.text((p0[0] + p1[0]) / 2, 5.0, et, ha="center", fontsize=9, color=TEXT)
    ax.set_title(titlu, fontsize=9.5)


fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.9))
schema_principiu(a1, False)
schema_principiu(a2, True)
salveaza(fig, "f04-1-principiu")

# --- Figura 4.2: caracteristica cu frânare și punctele de funcționare din probleme -----------------
Ib = np.linspace(0, 10, 500)
prag = prag_diferential(Ib)
fig, ax = plt.subplots(figsize=(9.5, 5.6))
ax.fill_between(Ib, prag, IDIFF_NEFRANAT, color=ZONA, lw=0)
ax.plot(Ib, prag, color=TEXT, lw=2.0, label="caracteristica frânată")
ax.axhline(IDIFF_NEFRANAT, color=C5, lw=1.6, ls="--", label=f"treapta nefrânată ({IDIFF_NEFRANAT:.0f}·In)")
ax.text(6.4, 7.6, "zona de acționare", fontsize=10, color=TEXT2)
ax.text(4.6, 0.12, "zona de stabilitate", fontsize=10, color=TEXT2)
ax.plot(Ib, P["pire_max"] * Ib, color=C4, lw=1.4, ls=":", label="plot extrem + erori opuse ale TC (problema 4.2)")
r = retea_referinta(cu_capacitati=False)
I_IT, I_JT, _ = P["curenti_T1"](r, "P1", "3f")
Id, Ibp, _, _ = marimi_releu(I_IT, I_JT)
ax.plot(Ibp[0], Id[0], "o", color=C3, ms=8, mec=FUNDAL, mew=1.5, label="defect exterior în P1 (problema 4.1)")
for (t, b, ib, idd) in P["Ib_puncte"]:
    ax.plot(ib, idd, "s", color=C4, ms=7, mec=FUNDAL, mew=1.5)
ax.plot([], [], "s", color=C4, ms=7, label="plot ±10 %, defecte exterioare (problema 4.2)")
I_IT, I_JT, _ = P["curenti_T1"](r, "B", "1f")
Idf, Ibf, _, _ = marimi_releu(I_IT, I_JT, elimina_I0=False)
ax.plot(Ibf[0], Idf[0], "X", color=C2, ms=9, mec=FUNDAL, mew=1.0,
        label="defect pe bara de 110 kV, fără eliminarea I0 (4.1)")
ax.plot(P["Ib"][0], P["Id"][0], "D", color=C1, ms=8, mec=FUNDAL, mew=1.5, label="defect interior la bornele de 20 kV (4.3)")
ax.annotate("defect interior la 110 kV:\nId = 50·In (treapta nefrânată)", xy=(9.8, 10.8), xytext=(6.8, 9.2),
            fontsize=8.5, color=TEXT, arrowprops=dict(arrowstyle="-|>", color=TEXT2, lw=0.8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 11.5)
ax.set_xlabel("curentul de frânare Ib = (|I₁| + |I₂|)/2  [multipli de In]")
ax.set_ylabel("curentul diferențial Id = |I₁ + I₂|  [multipli de In]")
ax.legend(loc="upper left", fontsize=8.2)
virgula(ax)
salveaza(fig, "f04-2-caracteristica")

# --- Figura 4.3: compensarea grupei de conexiuni (defect trifazat și monofazat în P1) -----------------
fig, axe = plt.subplots(2, 3, figsize=(11.5, 7.6))
titluri = ("110 kV: curenții de fază", "110 kV după compensare:\n(IA − IB)/√3, (IB − IC)/√3, (IC − IA)/√3",
           "20 kV: curenții de fază\nluați cu semn schimbat")
for rand, (tip, descr) in enumerate((("3f", "defect trifazat în P1"), ("1f", "defect monofazat în P1 (neutru prin rezistor)"))):
    I_IT, I_JT, _ = P["curenti_T1"](r, "P1", tip)
    _, _, c_IT, c_JT = marimi_releu(I_IT, I_JT)
    seturi = (I_IT / IN_IT, c_IT, -c_JT)
    m = 1.2 * max(np.max(np.abs(x)) for x in seturi)
    for col, (ax, s_) in enumerate(zip(axe[rand], seturi)):
        etich = ["a", "b", "c"]
        # fazorii suprapuși primesc o singură etichetă
        for k in range(3):
            for j in range(k):
                if abs(s_[k] - s_[j]) < 1e-3 * m and abs(s_[k]) > 1e-6:
                    etich[j] = etich[j] + ", " + etich[k]
                    etich[k] = None
        for k, (z, c) in enumerate(zip(s_, (C1, C2, C3))):
            if abs(z) > 1e-6 and etich[k] is not None:
                sageata(ax, 0j, z, c, etich[k], offset=(4, 2), t=0.75)
        ax.set_xlim(-m, m)
        ax.set_ylim(-m, m)
        ax.set_aspect("equal")
        ax.axhline(0, color=TEXT2, lw=0.6)
        ax.axvline(0, color=TEXT2, lw=0.6)
        if rand == 0:
            ax.set_title(titluri[col], fontsize=9.5)
        ax.tick_params(labelsize=8)
        virgula(ax)
    axe[rand][0].set_ylabel(descr + "\n[multipli de In]", fontsize=9)
fig.text(0.5, 0.01, "Pe fiecare fază, fazorul compensat de pe 110 kV coincide cu cel de pe 20 kV luat cu semn schimbat: "
         "Id = 0 pentru defectele exterioare.", ha="center", fontsize=8.5, color=TEXT2)
salveaza(fig, "f04-3-compensare")

# --- Figura 4.4: curentul de magnetizare la conectare și armonica a doua ----------------------------
t, i, _ = simuleaza_inrush(0.4, 2e-6)
tt, r2, i1 = raport_armonica2_alunecator(t, i)
In_v = np.sqrt(2) * IN_IT
fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 6.0), sharex=True)
a1.plot(t * 1e3, i / In_v, color=C1, lw=1.2)
a1.set_ylabel("i / (√2·In)")
a1.set_title("Conectarea lui T1 pe partea de 110 kV (flux remanent 0,8·ψn, la trecerea tensiunii prin zero)", fontsize=10)
a2.plot(tt * 1e3, 100 * r2, color=C2, label="I(2f)/I(f), fereastră de o perioadă")
a2.axhline(100 * ARMONICA2, color=TEXT, lw=1.2, ls="--", label=f"pragul de blocare ({100 * ARMONICA2:.0f} %)")
a2.axhline(100 * P["raport_def"]["20"], color=C3, lw=1.0, ls=":",
           label=f"defect interior la 20 kV, prima perioadă ({100 * P['raport_def']['20']:.1f} %)".replace(".", ","))
a2.set_ylim(0, 70)
a2.set_xlabel("t [ms]")
a2.set_ylabel("armonica a doua [%]")
a2.legend(loc="upper left", fontsize=8.5)
for ax in (a1, a2):
    virgula(ax)
salveaza(fig, "f04-4-inrush")

# --- Figura 4.5: protecția de bare de impedanță mare cu un TC saturat ---------------------------------
fig, ax = plt.subplots(figsize=(10, 4.2))
ax.set_xlim(0, 10)
ax.set_ylim(0, 5)
ax.axis("off")
# barele secundare (punctele comune)
ax.plot([1.0, 9.0], [3.6, 3.6], color=TEXT2, lw=1.4)
ax.plot([1.0, 9.0], [0.8, 0.8], color=TEXT2, lw=1.4)
for x, et in ((1.8, "TC L1\n(sursă de curent\nideală)"), (4.2, "TC L2\n(saturat: rămâne\nnumai Rct)"), (8.2, "releu +\nrezistor de\nstabilizare")):
    ax.text(x + 0.45, 2.2, et, fontsize=8.3, color=TEXT, va="center")
# TC ideal
ax.plot([1.8, 1.8], [3.6, 2.6], color=C1, lw=1.4)
ax.plot([1.8, 1.8], [1.8, 0.8], color=C1, lw=1.4)
ax.add_patch(Circle((1.8, 2.2), 0.38, fc=FUNDAL, ec=C1, lw=1.6))
ax.annotate("", xy=(1.8, 2.5), xytext=(1.8, 1.9), arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.4))
# TC saturat: Rct + 2RL
ax.plot([4.2, 4.2], [3.6, 3.15], color=C2, lw=1.4)
ax.add_patch(Rectangle((3.95, 2.35), 0.5, 0.8, fc=FUNDAL, ec=C2, lw=1.6))
ax.plot([4.2, 4.2], [2.35, 0.8], color=C2, lw=1.4)
ax.text(3.85, 2.75, "Rct + 2RL", ha="right", fontsize=8.5, color=C2)
# releul
ax.plot([8.2, 8.2], [3.6, 3.15], color=C5, lw=1.4)
ax.add_patch(Rectangle((7.95, 2.35), 0.5, 0.8, fc=FUNDAL, ec=C5, lw=1.6))
ax.plot([8.2, 8.2], [2.35, 0.8], color=C5, lw=1.4)
ax.text(5.0, 4.3, f"Defect exterior pe L2: curentul {P['I_sec']:.2f} A (secundar) se închide prin TC saturat".replace(".", ","),
        ha="center", fontsize=9.5, color=TEXT)
ax.text(5.0, 0.25, f"tensiunea pe releu ≤ I·(Rct + 2RL) = {P['Vs_min']:.1f} V  <  Vs = {P['Vs']:.0f} V  → releul rămâne stabil".replace(".", ","),
        ha="center", fontsize=9.5, color=TEXT)
salveaza(fig, "f04-5-bare-impedanta-mare")
