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
def sursa_curent(ax, x, y, sus, c):
    """Simbolul unei surse de curent (secundarul unui TC) cu săgeata în sus (sus=True) sau în jos."""
    ax.add_patch(Circle((x, y), 0.3, fc=FUNDAL, ec=c, lw=1.6, zorder=3))
    dy = 0.18 if sus else -0.18
    ax.annotate("", xy=(x, y + dy), xytext=(x, y - dy),
                arrowprops=dict(arrowstyle="-|>", color=c, lw=1.4, mutation_scale=11), zorder=4)


def schema_principiu(ax, interior):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    # conductorul primar și obiectul protejat
    ax.plot([0.3, 9.7], [4.9, 4.9], color=TEXT, lw=2.4)
    ax.add_patch(Rectangle((3.6, 4.45), 2.8, 0.9, fc="#d9d8d3", ec=TEXT2, lw=1.2, zorder=3))
    ax.text(5.0, 4.9, "obiect protejat", ha="center", va="center", fontsize=8.5, color=TEXT, zorder=4)
    yt, yb, ys = 3.3, 0.9, 2.1         # conductorul pilot de sus, cel de jos, poziția surselor
    for x in (2.4, 7.6):
        ax.add_patch(Circle((x, 4.9), 0.32, fc="none", ec=C1, lw=1.8, zorder=3))
        ax.text(x, 5.45, "TC", ha="center", fontsize=8.5, color=C1)
        ax.plot([x, x], [4.55, ys + 0.35], color=C1, lw=0.8, ls=":")      # cuplajul magnetic (simbolic)
        ax.plot([x, x], [yt, ys + 0.3], color=C1, lw=1.4)
        ax.plot([x, x], [ys - 0.3, yb], color=C1, lw=1.4)
    ax.plot([2.4, 7.6], [yt, yt], color=C1, lw=1.4)
    ax.plot([2.4, 7.6], [yb, yb], color=C1, lw=1.4)
    ax.plot([5.0, 5.0], [yt, yb], color=C2, lw=1.4)
    ax.add_patch(Rectangle((4.6, ys - 0.35), 0.8, 0.7, fc=FUNDAL, ec=C2, lw=1.6, zorder=3))
    ax.text(5.0, ys, "R", ha="center", va="center", fontsize=10, color=C2, fontweight="bold", zorder=4)
    ax.text(1.15, ys, "secundarul\nTC (sursă\nde curent)", ha="center", va="center", fontsize=7.5, color=C1)
    if interior:
        sursa_curent(ax, 2.4, ys, True, C1)
        sursa_curent(ax, 7.6, ys, True, C1)
        ax.annotate("", xy=(5.0, 3.95), xytext=(5.0, 4.45), arrowprops=dict(arrowstyle="-|>", color=C2, lw=1.6))
        ax.text(5.15, 4.05, "defect", fontsize=8.5, color=C2)
        sageti = [((0.6, 5.15), (1.6, 5.15), "I₁"), ((9.4, 5.15), (8.4, 5.15), "I₂")]
        for x0, x1 in ((3.0, 4.2), (7.0, 5.8)):
            ax.annotate("", xy=(x1, yt + 0.15), xytext=(x0, yt + 0.15), arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.2))
        ax.annotate("", xy=(5.25, ys - 0.45), xytext=(5.25, yt - 0.1), arrowprops=dict(arrowstyle="-|>", color=C2, lw=1.2))
        ax.text(5.6, 0.35, "prin releu trece i₁ + i₂ → acționează", fontsize=8.5, color=C2, ha="center")
        titlu = "Defect interior: curenții secundari se adună în releu"
    else:
        sursa_curent(ax, 2.4, ys, True, C1)
        sursa_curent(ax, 7.6, ys, False, C1)
        ax.annotate("", xy=(9.7, 4.2), xytext=(9.7, 4.8), arrowprops=dict(arrowstyle="-|>", color=C2, lw=1.6))
        ax.text(9.4, 3.85, "defect\nexterior", fontsize=8.5, color=C2, ha="center")
        sageti = [((0.6, 5.15), (1.6, 5.15), "I"), ((8.4, 5.15), (9.4, 5.15), "I")]
        ax.annotate("", xy=(4.2, yt + 0.15), xytext=(3.0, yt + 0.15), arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.2))
        ax.annotate("", xy=(7.0, yt + 0.15), xytext=(5.8, yt + 0.15), arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.2))
        ax.annotate("", xy=(3.0, yb - 0.15), xytext=(4.2, yb - 0.15), arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.2))
        ax.annotate("", xy=(5.8, yb - 0.15), xytext=(7.0, yb - 0.15), arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.2))
        ax.text(5.6, 0.25, "curentul circulă prin conductoarele pilot; prin releu: i − i = 0", fontsize=8.5,
                color=C1, ha="center")
        titlu = "Defect exterior: curentul secundar circulă, releul nu este parcurs"
    for (p0, p1, et) in sageti:
        ax.annotate("", xy=p1, xytext=p0, arrowprops=dict(arrowstyle="-|>", color=TEXT, lw=1.4))
        ax.text((p0[0] + p1[0]) / 2, 5.3, et, ha="center", fontsize=9, color=TEXT)
    ax.set_title(titlu, fontsize=9.5)


fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.5, 4.2))
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
Id_b, Ib_b = P["Id_b"][0], P["Ib_b"][0]
ax.annotate("", xy=(9.85, 11.45), xytext=(9.3, 10.0), arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.4))
ax.text(9.2, 9.7, f"defect interior la 110 kV, în afara graficului:\nIb = {Ib_b:.1f}·In, Id = {Id_b:.1f}·In "
        f"(treapta nefrânată)".replace(".", ","), fontsize=8.3, color=TEXT, ha="right", va="top")
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
fig, ax = plt.subplots(figsize=(11, 4.6))
ax.set_xlim(0, 12)
ax.set_ylim(0, 5.2)
ax.axis("off")
yt, yb = 3.7, 0.9
ax.plot([0.8, 11.4], [yt, yt], color=TEXT2, lw=1.4)
ax.plot([0.8, 11.4], [yb, yb], color=TEXT2, lw=1.4)
ym = (yt + yb) / 2
# TC sănătoase: surse de curent ideale
for x, et in ((1.1, "TC L1\n(sursă de curent)"), (3.7, "TC L2\n(sursă de curent)")):
    ax.plot([x, x], [yt, ym + 0.38], color=C1, lw=1.4)
    ax.plot([x, x], [ym - 0.38, yb], color=C1, lw=1.4)
    ax.add_patch(Circle((x, ym), 0.38, fc=FUNDAL, ec=C1, lw=1.6))
    ax.annotate("", xy=(x, ym + 0.25), xytext=(x, ym - 0.25), arrowprops=dict(arrowstyle="-|>", color=C1, lw=1.4))
    ax.text(x + 0.48, ym, et, fontsize=8.2, color=TEXT, va="center")
# TC saturat (celula T1): numai Rct, în serie cu conductoarele de legătură
x = 6.6
ax.plot([x, x], [yt, 3.25], color=C2, lw=1.4)
ax.add_patch(Rectangle((x - 0.25, 2.55), 0.5, 0.7, fc=FUNDAL, ec=C2, lw=1.6))
ax.plot([x, x], [2.55, 2.1], color=C2, lw=1.4)
ax.add_patch(Rectangle((x - 0.25, 1.4), 0.5, 0.7, fc=FUNDAL, ec=C2, lw=1.6))
ax.plot([x, x], [1.4, yb], color=C2, lw=1.4)
ax.text(x + 0.4, 2.9, "Rct (TC T1 saturat)", fontsize=8.2, color=C2, va="center")
ax.text(x + 0.4, 1.75, "2RL (conductoare)", fontsize=8.2, color=C2, va="center")
# releul cu rezistorul de stabilizare și limitatorul neliniar în paralel
x = 9.0
ax.plot([x, x], [yt, 3.0], color=C5, lw=1.4)
ax.add_patch(Rectangle((x - 0.25, 1.6), 0.5, 1.4, fc=FUNDAL, ec=C5, lw=1.6))
ax.plot([x, x], [1.6, yb], color=C5, lw=1.4)
ax.text(x - 0.4, 2.3, "releu +\nrezistor de\nstabilizare", fontsize=8.2, color=TEXT, va="center", ha="right")
x = 10.6
ax.plot([x, x], [yt, 2.85], color=C4, lw=1.4)
ax.add_patch(Rectangle((x - 0.22, 1.75), 0.44, 1.1, fc=FUNDAL, ec=C4, lw=1.6))
ax.plot([x - 0.35, x + 0.35], [1.85, 2.75], color=C4, lw=1.2)
ax.plot([x, x], [1.75, yb], color=C4, lw=1.4)
ax.text(x + 0.35, 1.45, "limitator\nneliniar", fontsize=8.2, color=TEXT, va="top")
ax.text(6.0, 4.6, f"Defect exterior după TC al celulei T1: curentul {P['I_sec']:.2f} A (secundar) al TC L1 și L2 se închide "
        f"prin TC T1 saturat".replace(".", ","), ha="center", fontsize=9.5, color=TEXT)
ax.text(6.0, 0.3, f"tensiunea pe releu ≤ I·(Rct + 2RL) = {P['Vs_min']:.2f} V  <  Vs = {P['Vs']:.0f} V  → releul rămâne stabil"
        .replace(".", ","), ha="center", fontsize=9.5, color=TEXT)
salveaza(fig, "f04-5-bare-impedanta-mare")
