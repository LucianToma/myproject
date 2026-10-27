"""Figurile capitolului 7 – Automatizări de rețea."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from comun import C1, C2, C3, C4, C5, TEXT, TEXT2, GRILA, FUNDAL, ZONA, salveaza, bloc, legatura, virgula
from modele import F0, unghi_critic, timp_critic
from scipy.optimize import brentq
from calcul_cap07 import (XD_T, XT, XL, XS, H, P0, punct_functionare, pmax, simuleaza, remanenta_analitic,
                          diferenta_tensiune, T0_REM, reglaje_R1, momente_aar, U_PRAG)

op = punct_functionare()
d0 = op["delta0"]
Pmax2, Pmax1 = pmax(2), pmax(1)
dcr = unghi_critic(d0)
tcr = timp_critic(d0, H, P0)


def sursa(ax, x, y, r=0.28, culoare=C1, eticheta=None):
    ax.add_patch(Circle((x, y), r, fc=FUNDAL, ec=culoare, lw=1.6))
    t = np.linspace(-0.6, 0.6, 50) * r
    ax.plot(x + t, y + 0.35 * r * np.sin(t / r * np.pi * 1.6), color=culoare, lw=1.4)
    if eticheta:
        ax.text(x, y - r - 0.12, eticheta, ha="center", va="top", fontsize=9, color=TEXT)


def intrerupator(ax, x, y, s=0.08):
    ax.add_patch(Rectangle((x - s, y - s), 2 * s, 2 * s, fc=FUNDAL, ec=TEXT, lw=1.2))


# --- Figura 7.1: schema de studiu ---------------------------------------------
fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 4.6), gridspec_kw=dict(height_ratios=[1.25, 1]))
for ax in (a1, a2):
    ax.axis("off")
a1.set_xlim(-0.5, 10.5)
a1.set_ylim(-0.9, 1.5)
y = 0.5
sursa(a1, 0.0, y, eticheta="G1\n50 MVA, 10,5 kV")
a1.plot([0.28, 1.2], [y, y], color=TEXT, lw=1.4)
a1.add_patch(Circle((1.45, y), 0.25, fc="none", ec=C2, lw=1.6))
a1.add_patch(Circle((1.8, y), 0.25, fc="none", ec=C2, lw=1.6))
a1.text(1.62, y - 0.42, "TB\n10,5/115 kV", ha="center", va="top", fontsize=9, color=TEXT)
a1.plot([2.05, 3.0], [y, y], color=TEXT, lw=1.4)
intrerupator(a1, 2.6, y)
a1.plot([3.0, 3.0], [y - 0.6, y + 0.75], color=TEXT, lw=5, solid_capstyle="butt")
a1.text(3.0, y + 0.82, "C", ha="center", va="bottom", fontsize=10, fontweight="bold")
# plecarea radială (defectul din problema 7.1)
a1.plot([3.0, 3.6, 3.6], [y - 0.45, y - 0.45, y - 0.8], color=TEXT, lw=1.2)
intrerupator(a1, 3.6, y - 0.62)
a1.text(3.75, y - 0.75, "plecare radială\n(defect în pr. 7.1, 7.6)", ha="left", va="center", fontsize=8.5, color=TEXT2)
# linia dublă
for dy, nume in ((0.3, "circuitul 1"), (-0.15, "circuitul 2")):
    a1.plot([3.0, 8.0], [y + dy, y + dy], color=TEXT, lw=1.6)
    intrerupator(a1, 3.4, y + dy)
    intrerupator(a1, 7.6, y + dy)
    a1.text(5.5, y + dy + 0.07, f"{nume}: 110 kV, 80 km", ha="center", va="bottom", fontsize=8.5, color=TEXT)
a1.plot(3.85, y + 0.3, marker="*", color=C2, ms=14)
a1.text(3.85, y + 0.55, "defect (pr. 7.3)", ha="center", va="bottom", fontsize=8.5, color=C2)
a1.plot([8.0, 8.0], [y - 0.45, y + 0.6], color=TEXT, lw=5, solid_capstyle="butt")
a1.plot([8.0, 9.0], [y, y], color=TEXT, lw=1.4)
sursa(a1, 9.3, y, culoare=C3, eticheta="sistemul\n(V = 1 ∠ 0)")
# schema echivalentă
a2.set_xlim(-0.5, 10.5)
a2.set_ylim(-0.6, 1.0)
yy = 0.3
pos = [0.0, 1.9, 3.7, 6.0, 8.0, 9.3]
a2.text(0.0, yy, "E' ∠ δ", ha="center", va="center", fontsize=11, color=C1, fontweight="bold")
etich = [f"x'd = {XD_T:.2f}".replace(".", ","), f"xT = {XT:.2f}".replace(".", ","),
         f"xL/2 = {XL / 2:.4f}".replace(".", ",") + "\n(xL = " + f"{XL:.4f}".replace(".", ",") + " cu un circuit)",
         f"xs = {XS:.2f}".replace(".", ",")]
xs_ = [(0.5, 1.5), (2.2, 3.2), (4.3, 5.7), (6.6, 7.6)]
a2.plot([0.35, 9.0], [yy, yy], color=TEXT, lw=1.2)
for (xa, xb), e in zip(xs_, etich):
    a2.add_patch(Rectangle((xa, yy - 0.12), xb - xa, 0.24, fc=FUNDAL, ec=C5, lw=1.4))
    a2.text((xa + xb) / 2, yy - 0.2, e, ha="center", va="top", fontsize=8.5, color=TEXT)
a2.plot([3.7, 3.7], [yy - 0.05, yy + 0.35], color=TEXT, lw=4)
a2.text(3.7, yy + 0.4, "C", ha="center", va="bottom", fontsize=9, fontweight="bold")
a2.text(9.3, yy, "V = 1", ha="left", va="center", fontsize=11, color=C3, fontweight="bold")
a2.text(5.0, 0.95, "schema echivalentă (u.r., baza 50 MVA, 115 kV)", ha="center", va="top", fontsize=9, color=TEXT2)
salveaza(fig, "f07-1-schema-studiu")

# --- Figura 7.2: criteriul ariilor egale și δ(t) ------------------------------
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.0))
dg = np.linspace(0, np.pi, 400)
a1.plot(np.degrees(dg), Pmax2 * np.sin(dg), color=C1, label="Pe = Pmax·sin δ (înainte și după defect)")
a1.axhline(P0, color=C2, lw=1.6, label="Pm = 0,85")
a1.plot([0, 180], [0, 0], color=C4, lw=2.4, label="Pe = 0 în timpul defectului")
m1 = (dg >= d0) & (dg <= dcr)
a1.fill_between(np.degrees(dg[m1]), 0, P0, color=C2, alpha=0.25)
du = np.pi - d0
m2 = (dg >= dcr) & (dg <= du)
a1.fill_between(np.degrees(dg[m2]), P0, Pmax2 * np.sin(dg[m2]), color=C1, alpha=0.25)
a1.text(np.degrees((d0 + dcr) / 2), P0 / 2, "A1\n(accelerare)", ha="center", va="center", fontsize=9)
a1.text(np.degrees((dcr + du) / 2) + 5, (P0 + Pmax2) / 2 - 0.1, "A2\n(frânare)", ha="center", va="center", fontsize=9)
for dd, e in ((d0, "δ0"), (dcr, "δcr"), (du, "δu")):
    a1.axvline(np.degrees(dd), color=TEXT2, lw=0.8, ls=":")
    a1.text(np.degrees(dd), -0.22, e, ha="center", va="top", fontsize=9)
a1.set_xlim(0, 180)
a1.set_ylim(-0.35, 2.3)
a1.set_xlabel("δ [°]", labelpad=14)
a1.set_ylabel("P [u.r.]")
a1.set_title("Criteriul ariilor: eliminare la δcr (A1 = A2)")
a1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), fontsize=8, ncol=2)
virgula(a1)
for k, c in ((0.38, C3), (0.98, C1), (1.02, C2)):
    t, d, _, _ = simuleaza([(k * tcr, 0.0), (2.0, Pmax2)], d0, t_final=2.0)
    a2.plot(t, np.degrees(d), color=c, label=f"eliminare la {k * tcr * 1e3:.0f} ms".replace(".", ","))
a2.axvline(tcr, color=TEXT2, lw=0.8, ls=":")
a2.text(tcr + 0.02, -70, f"tcr = {tcr * 1e3:.0f} ms", fontsize=9, color=TEXT2)
a2.set_ylim(-80, 300)
a2.set_xlim(0, 2.0)
a2.set_xlabel("t [s]")
a2.set_ylabel("δ [°]")
a2.set_title("Unghiul rotorului (model clasic)")
a2.legend(loc="upper right", fontsize=8)
virgula(a2)
fig.tight_layout()
salveaza(fig, "f07-2-arii-egale")

# --- Figura 7.3: ciclul de RAR pe fiderul F1 (defect permanent, cu accelerare) ---
t_r = reglaje_R1()["t_r"]                   # timpul treptei temporizate a lui R1 (din capitolul 3)
t_cb, t_inch, t_acc = 0.06, 0.08, 0.04
ev = [0.0]
ev.append(t_r + t_cb)                       # deschis
ev.append(ev[-1] + 0.5 + t_inch)            # închis (RAR 1)
ev.append(ev[-1] + t_acc + t_cb)            # deschis
ev.append(ev[-1] + 15.0 + t_inch)           # închis (RAR 2)
ev.append(ev[-1] + t_acc + t_cb)            # deschis definitiv
fig, axs = plt.subplots(1, 2, figsize=(10.5, 3.8), sharey=True, gridspec_kw=dict(width_ratios=[2.2, 1], wspace=0.08))
randuri = [("curent de defect", C2), ("întrerupător închis", C1), ("pauză de tensiune", C4), ("blocare (lockout)", C5)]
for ax, (xa, xb) in zip(axs, ((-0.1, 2.0), (16.3, 17.2))):
    for i, (nume, c) in enumerate(randuri):
        yb = 3 - i
        if i == 0:
            seg = [(ev[0], ev[1]), (ev[2], ev[3]), (ev[4], ev[5])]
        elif i == 1:
            seg = [(-1, ev[1]), (ev[2], ev[3]), (ev[4], ev[5])]
        elif i == 2:
            seg = [(ev[1], ev[2]), (ev[3], ev[4])]
        else:
            seg = [(ev[5], 30)]
        for s0, s1 in seg:
            ax.add_patch(Rectangle((s0, yb - 0.3), s1 - s0, 0.6, fc=c, ec="none", alpha=0.75))
    ax.set_xlim(xa, xb)
    ax.grid(axis="y", visible=False)
    virgula(ax, "x")
    ax.set_xlabel("t [s]")
for ax, sel in ((axs[0], ev[1:4]), (axs[1], ev[4:])):
    for j, e in enumerate(sel):
        ax.axvline(e, color=TEXT2, lw=0.7, ls=":")
        ax.text(e, 3.45 + 0.35 * (j % 2), f"{e:.3f} s".replace(".", ","), ha="center", va="bottom", fontsize=8,
                color=TEXT2)
axs[0].set_ylim(-0.6, 4.2)
axs[0].set_yticks([3, 2, 1, 0], [r[0] for r in randuri])
axs[0].text((ev[0] + ev[1]) / 2, 3, f"treapta temporizată {t_r:.3f} s\n+ întrerupătorul 0,06 s".replace(".", ","),
            ha="center", va="center", fontsize=7.5)
axs[0].text((ev[1] + ev[2]) / 2, 1, "pauza reglată 0,5 s\n+ închiderea 0,08 s", ha="center", va="center", fontsize=7.5)
axs[0].text(ev[3] + 0.03, 2.45, "accelerare:\n0,04 + 0,06 s", ha="left", va="bottom", fontsize=7.5)
axs[1].text(16.39, 1, "pauza reglată 15 s\n+ închiderea 0,08 s", ha="center", va="center", fontsize=6.5)
axs[1].spines["left"].set_visible(False)
axs[1].tick_params(left=False)
# semne de întrerupere a axei timpului
for ax, xs_ in ((axs[0], 1.0), (axs[1], 0.0)):
    kw = dict(transform=ax.transAxes, color=TEXT2, clip_on=False, lw=1.0)
    for dx in (-0.012, 0.012):
        ax.plot([xs_ + dx - 0.008, xs_ + dx + 0.008], [-0.03, 0.03], **kw)
fig.suptitle("Ciclul RAR cu două reanclanșări pe un defect permanent (cu accelerare după reanclanșare)",
             fontsize=11, fontweight="bold")
salveaza(fig, "f07-3-ciclu-rar")

# --- Figura 7.4: pendulațiile lui G1 la RAR pe linia dublă ----------------------
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0), gridspec_kw=dict(width_ratios=[1.5, 1]))
t_c = t_c2 = 0.12
cazuri = [("fără RAR (un circuit rămâne deschis)", [(t_c, 0.0), (5.0, Pmax1)], TEXT2, "--"),
          ("RAR reușită, pauză 0,5 s", [(t_c, 0.0), (0.5, Pmax1), (5.0, Pmax2)], C3, "-"),
          ("RAR pe defect permanent, pauză 0,5 s", [(t_c, 0.0), (0.5, Pmax1), (t_c2, 0.0), (5.0, Pmax1)], C1, "-"),
          ("RAR pe defect permanent, pauză 0,8 s", [(t_c, 0.0), (0.8, Pmax1), (t_c2, 0.0), (5.0, Pmax1)], C2, "-")]
for nume, et, c, ls in cazuri:
    t, d, _, _ = simuleaza(et, d0, t_final=3.0)
    a1.plot(t, np.degrees(d), color=c, ls=ls, label=nume)
a1.set_ylim(-20, 250)
a1.set_xlim(0, 3)
a1.set_xlabel("t [s]")
a1.set_ylabel("δ [°]")
a1.set_title("Unghiul rotorului lui G1 (model clasic, fără amortizare)")
a1.legend(loc="upper left", fontsize=8)
virgula(a1)
tms = np.round(np.arange(0.2, 1.801, 0.02), 2)
dm = []
for tm in tms:
    t, d, _, start = simuleaza([(t_c, 0.0), (tm, Pmax1), (t_c2, 0.0), (5.0, Pmax1)], d0, t_final=5.0)
    tr = start[2][0]
    dm.append(np.degrees(d[t >= tr].max()) if d.max() < np.pi else np.nan)
dm = np.array(dm)
a2.plot(tms, dm, color=C1, marker="o", ms=3, lw=1.2)
inst = np.isnan(dm)
a2.plot(tms[inst], np.full(inst.sum(), 175), "x", color=C2, ms=6, label="instabil")
a2.axhline(180, color=C2, lw=0.8, ls=":")
a2.set_xlabel("pauza de tensiune [s]")
a2.set_ylabel("δmax după reanclanșare [°]")
a2.set_title("Reanclanșare pe defect permanent")
a2.set_ylim(0, 190)
a2.legend(loc="lower right", fontsize=8)
virgula(a2)
fig.tight_layout()
salveaza(fig, "f07-4-rar-pendulatii")

# --- Figura 7.5: sincronizarea – unghiul de avans --------------------------------
df, t_close = 0.10, 0.08
alfa = 360 * df * t_close
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 3.8))
t = np.linspace(0, 10, 2001)
phi = -180 + 360 * df * t
a1.plot(t, 2 * np.abs(np.sin(np.radians(phi) / 2)), color=C1)
a1.set_xlabel("t [s]")
a1.set_ylabel("|ΔU| [u.r.]")
a1.set_title(f"Tensiunea pe întrerupătorul deschis (Δf = {df:.2f} Hz)".replace(".", ","))
a1.axvline(5.0, color=C3, lw=1.0, ls=":")
a1.text(5.1, 1.8, "φ = 0: momentul\nideal de închidere", fontsize=8.5, color=TEXT)
virgula(a1)
tz = np.linspace(4.8, 5.1, 400)
phz = -180 + 360 * df * tz
a2.plot(tz, phz, color=C1)
tc_cmd = 5.0 - t_close
a2.axvline(tc_cmd, color=C2, lw=1.0, ls="--")
a2.axvline(5.0, color=C3, lw=1.0, ls="--")
a2.axhline(-alfa, color=C2, lw=0.8, ls=":")
a2.annotate("", xy=(5.0, -alfa - 0.6), xytext=(tc_cmd, -alfa - 0.6),
            arrowprops=dict(arrowstyle="<->", color=TEXT2, lw=1))
a2.text((tc_cmd + 5.0) / 2, -alfa - 1.0, r"$t_{\mathrm{î}}$" + f" = {t_close * 1e3:.0f} ms", ha="center", va="top",
        fontsize=8.5)
a2.text(4.805, -alfa + 0.3, "comanda la\n" + f"φ = −α = −{alfa:.2f}°".replace(".", ","), ha="left", va="bottom",
        fontsize=8.5, color=C2)
a2.text(5.01, -6.5, "contactele se închid\nla φ = 0", ha="left", va="bottom", fontsize=8.5, color=C3)
a2.set_xlabel("t [s]")
a2.set_ylabel("φ [°]")
a2.set_title(r"Unghiul de avans α = 360°·Δf·$t_{\mathrm{î}}$")
a2.set_ylim(-8, 4)
virgula(a2)
fig.tight_layout()
salveaza(fig, "f07-5-sincronizare")

# --- Figura 7.6: AAR – tensiunea remanentă și unghiul ----------------------------
tt = np.linspace(0, 1.5, 3001)
w, U, th = remanenta_analitic(tt)
dU = diferenta_tensiune(U, th)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
a1.plot(tt, U, color=C1, label="tensiunea remanentă Ur")
a1.plot(tt, w, color=C3, label="turația (frecvența) n/n0")
a1.axhline(U_PRAG, color=C2, lw=0.8, ls=":")
a1.text(1.48, U_PRAG + 0.02, "prag " + f"{U_PRAG:.2f}".replace(".", ",") + " u.r.", ha="right", va="bottom",
        fontsize=8.5, color=C2)
a1.set_xlabel("t [s] (t = 0: bara rămâne fără alimentare)")
a1.set_ylabel("[u.r.]")
a1.set_ylim(0, 1.05)
a1.set_title("Bara de motoare după pierderea alimentării")
a1.legend(loc="lower left", fontsize=8.5)
virgula(a1)
a2.plot(tt, dU, color=C5)
a2.axhline(1.0, color=TEXT2, lw=0.8, ls=":")
i_f = np.argmax(dU >= 1.0)
a2.axvspan(0, tt[i_f], color=C3, alpha=0.15)
a2.text(tt[i_f] / 2, 1.97, "fereastra\nrapidă", ha="center", va="top", fontsize=8)
t_rem = brentq(lambda x: remanenta_analitic(x)[1] - U_PRAG, 0.01, 5)
a2.axvspan(t_rem, 1.5, color=C4, alpha=0.15)
a2.text((t_rem + 1.5) / 2, 1.97, "Ur ≤ " + f"{U_PRAG:.2f}".replace(".", ",") + " u.r.:\n|ΔU| ≤ "
        + f"{1 + U_PRAG:.2f}".replace(".", ",") + " u.r.", ha="center", va="top", fontsize=8)
etich = {("a", "simultan"): ("a, simultan", (0.17, 0.04)), ("a", "secvențial"): ("a, secvențial", (0.17, 0.32)),
         ("b", "simultan"): ("b, simultan", (0.17, 0.18)), ("b", "secvențial"): ("b, secvențial", (0.40, 1.80))}
culori = {"a": C3, "b": C2}
for (pornire, mod), tp in momente_aar().items():
    if pornire == "c":
        continue
    _, Up, thp = remanenta_analitic(np.array(tp))
    y = diferenta_tensiune(Up, thp)
    a2.plot(tp, y, "o" if mod == "simultan" else "s", color=culori[pornire], ms=6, mec=FUNDAL, mew=1.2)
    txt, (xt, yt) = etich[(pornire, mod)]
    a2.annotate(f"{txt}, {tp * 1e3:.0f} ms", xy=(tp, y), xytext=(xt, yt), fontsize=7.5,
                arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.7))
tc_min = momente_aar()[("c", "secvențial")]
a2.axvline(tc_min, color=TEXT2, lw=0.8, ls="--")
a2.text(tc_min + 0.01, 0.12, f"c: minimă tensiune,\ncel mai devreme {tc_min * 1e3:.0f} ms", fontsize=7.5, color=TEXT2)
a2.set_xlabel("t [s]")
a2.set_ylabel("|ΔU| [u.r.]")
a2.set_ylim(0, 2.0)
a2.set_title("Tensiunea pe întrerupătorul de rezervă |1 − Ur·e^(−jθ)|")
virgula(a2)
fig.tight_layout()
salveaza(fig, "f07-6-aar")

# --- Figura 7.7: protecția la refuzul întrerupătorului – logica și timpii ----------
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.4), gridspec_kw=dict(width_ratios=[1.3, 1]))
a1.axis("off")
a1.set_xlim(-0.2, 10.1)
a1.set_ylim(-0.3, 6.3)
bloc(a1, 0.0, 4.2, 2.8, 0.9, "comandă de declanșare\nde la protecții", C1, fs=8)
bloc(a1, 0.0, 2.4, 2.8, 0.9, r"$I > I_{\mathrm{BF}}$" + "\n(curentul nu a dispărut)", C1, fs=8)
bloc(a1, 3.3, 3.3, 0.9, 0.9, "ȘI", C5)
bloc(a1, 4.7, 3.3, 1.6, 0.9, "temporizare\n" + r"$t_{\mathrm{BF}}$", C4, fs=8.5)
bloc(a1, 6.8, 3.05, 3.2, 1.4, "declanșarea\nîntrerupătoarelor vecine\n(prin protecția barelor\nsau GOOSE)", C2, fs=8)
bloc(a1, 4.7, 4.95, 3.6, 0.8, "redeclanșare imediată\n(bobina a 2-a)", C3, fs=8)
bloc(a1, 6.8, 1.25, 3.2, 1.2, "declanșare la distanță\n(capătul opus al liniei)\nprin teleprotecție", C2, fs=8)
bloc(a1, 3.0, 0.0, 3.3, 0.95, "blocarea reanclanșării\n(releul de blocare 86)", C5, fs=8)
legatura(a1, (2.8, 4.65), (3.3, 3.95))
legatura(a1, (2.8, 2.85), (3.3, 3.55))
legatura(a1, (4.2, 3.75), (4.7, 3.75))
legatura(a1, (6.3, 3.75), (6.8, 3.75))
legatura(a1, (2.8, 4.95), (4.7, 5.35))
legatura(a1, (8.4, 3.05), (8.4, 2.45))
legatura(a1, (5.5, 3.3), (5.0, 0.95))
a1.text(1.4, 0.45, "logica de principiu\n(ANSI 50BF)", ha="center", va="center", fontsize=8.5, color=TEXT2)
t_prot, t_BF, t_aux, t_cbr, t_z2 = 0.03, 0.12, 0.01, 0.06, 0.30
bare = [("protecția de bază\n+ întrerupătorul", [(0, t_prot, C1), (t_prot, t_cbr, C3)]),
        ("refuz → 50BF\n+ întrerupătoarele vecine", [(0, t_prot, C1), (t_prot, t_BF, C4), (t_prot + t_BF, t_aux, C5),
                                                    (t_prot + t_BF + t_aux, t_cbr, C3)]),
        ("refuz → rezerva\nde la distanță", [(0, t_prot, C1), (t_prot, t_z2, C2), (t_prot + t_z2, t_cbr, C3)])]
for i, (nume, seg) in enumerate(bare):
    for s0, ds, c in seg:
        a2.barh(2 - i, ds, left=s0, color=c, height=0.5, edgecolor=FUNDAL)
    a2.text(sum(seg[-1][:2]) + 0.01, 2 - i, f"{sum(seg[-1][:2]) * 1e3:.0f} ms", va="center", fontsize=8.5)
a2.axvline(tcr, color=C2, lw=1.4, ls="--")
a2.text(tcr + 0.005, 2.55, f"tcr = {tcr * 1e3:.0f} ms", fontsize=8.5, color=C2)
from matplotlib.patches import Patch  # noqa: E402
a2.legend(handles=[Patch(color=C1, label="măsurarea protecției"), Patch(color=C4, label=r"temporizarea $t_{\mathrm{BF}}$"),
                   Patch(color=C5, label="relee intermediare"), Patch(color=C2, label="treapta a 2-a (capătul opus)"),
                   Patch(color=C3, label="întreruperea curentului")],
          loc="upper center", bbox_to_anchor=(0.45, -0.18), ncol=3, fontsize=7.5)
a2.set_yticks([2, 1, 0], [b[0] for b in bare], fontsize=8.5)
a2.set_xlim(0, 0.52)
a2.set_ylim(-0.6, 2.9)
a2.set_xlabel("t [s]")
a2.set_title("Timpul de eliminare a defectului")
a2.grid(axis="y", visible=False)
virgula(a2, "x")
fig.tight_layout()
salveaza(fig, "f07-7-refuz-intrerupator")
