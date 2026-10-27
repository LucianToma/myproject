"""Figurile capitolului 8 – Reglajul automat al frecvenței și al tensiunii."""

import numpy as np
import matplotlib.pyplot as plt
from comun import C1, C2, C3, C4, C5, TEXT, TEXT2, GRILA, FUNDAL, ZONA, salveaza, virgula, bloc, legatura
from modele import GEN, DATE
from modele import fmt
from calcul_cap08 import (M_inertie, K_statism, izolat_ode, nadir, ce_simulare, ce_nadir_analitic, dasf_simulare,
                          doua_zone, regulator_ploturi, rat_ode, profil_liniar, profil_patratic, profil_intarziat)

F0 = 50.0


def mn(x, n=0):
    """Număr cu virgulă zecimală și semnul minus tipografic."""
    return fmt(x, n).replace("-", "−")


# --- Figura 8.1: răspunsul frecvenței la pierderea unui grup (problema 8.1) ---------------
S_rest, H, D, dP = 875.0, 5.0, 16.0, 100.0
M = M_inertie(H, S_rest)
K = K_statism(S_rest, 0.05)
t, df, Pm = izolat_ode(dP, M, D, K, 0.2, 2.0, 30.0, n=3001)
t0, df0, _ = izolat_ode(dP, M, D, K, 0.2, 2.0, 30.0, cu_regulator=False, n=3001)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.0))
a1.plot(t, df * 1e3, color=C1, label="cu regulatoare de viteză (statism 5 %)")
a1.plot(t0, df0 * 1e3, color=C2, ls="--", label="fără regulatoare (numai inerție și sarcină)")
tr = np.linspace(0, 2.8, 10)
a1.plot(tr, -dP / M * tr * 1e3, color=TEXT, lw=1.3, ls=(0, (1, 1.5)), zorder=5,
        label=r"tangenta inițială: $\mathrm{RoCoF}_0 = -\Delta P/M$")
tn, dn = nadir(t, df)
a1.plot([tn], [dn * 1e3], "o", color=C1, ms=7, mec=FUNDAL, mew=2)
a1.annotate(f"nadir {mn(dn * 1e3)} mHz\nla {mn(tn, 1)} s", xy=(tn, dn * 1e3), xytext=(6, -900),
            color=TEXT, fontsize=9, arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
dss = -dP / (K + D)
a1.axhline(dss * 1e3, color=C1, lw=0.9, ls=":")
a1.text(29.5, dss * 1e3 - 45, r"staționar $-\Delta P/(K_\mathrm{reg} + D)$ = " + f"{mn(dss * 1e3)} mHz", ha="right",
        va="top", color=TEXT, fontsize=9)
a1.set_ylim(-1600, 100)
a1.set_xlabel("t [s]")
a1.set_ylabel("Δf [mHz]")
a1.set_title("Abaterea de frecvență")
a1.legend(loc="lower right", fontsize=8.5)
virgula(a1)
a2.plot(t, Pm, color=C1, label=r"puterea suplimentară a turbinelor $\Delta P_m$")
a2.plot(t, -D * df, color=C3, label="scăderea puterii sarcinii D·|Δf|")
a2.plot(t, Pm - D * df, color=TEXT2, ls="--", lw=1.2, label="total")
a2.axhline(dP, color=C2, lw=1.0, ls=":")
a2.text(29.5, dP + 22, "ΔP = 100 MW (grupul pierdut)", ha="right", color=TEXT, fontsize=9)
a2.set_xlabel("t [s]")
a2.set_ylabel("P [MW]")
a2.set_title("Cine acoperă deficitul")
a2.legend(loc="center right", fontsize=8.5, bbox_to_anchor=(1.0, 0.27))
a2.set_ylim(0, 165)
virgula(a2)
fig.tight_layout()
salveaza(fig, "f08-1-raspuns-frecventa")

# --- Figura 8.2: nivelurile de reglaj (schematic) ------------------------------------------
# Fracțiunile din deficit acoperite de fiecare mecanism; suma lor este 1 în orice moment.
ts = np.logspace(-1, np.log10(3600), 240)
r = 1 - np.exp(-np.clip(ts - 30, 0, None) / 180)          # partea preluată de rezervele de restabilire
m = 1 - np.exp(-np.clip(ts - 300, 0, None) / 250)         # din aceasta, partea mFRR / RR
urcare = np.clip(ts / 30, 0, 1) ** 0.8                     # creșterea FCR + autoreglarea sarcinii
fcr = 0.85 * (1 - r) * urcare
autoreg = 0.15 * (1 - r) * urcare
inertie = (1 - r) * (1 - urcare)
afrr = r * (1 - m)
mfrr = r * m
fig, ax = plt.subplots(figsize=(10, 4.2))
ax.stackplot(ts, inertie, autoreg, fcr, afrr, mfrr, colors=[C5, "#9a9890", C1, C3, C4], alpha=0.9,
             labels=["energia cinetică a maselor în rotație (inerția)", "autoreglarea sarcinii",
                     "FCR – reglaj primar", "aFRR – reglaj secundar automat",
                     "mFRR / RR – rezerve activate manual (terțiar)"])
ax.set_xscale("log")
for x, txt, ha in ((30, " FCR activată complet\n în 30 s (SOGL)", "left"), (900, "frecvența refăcută \nîn 15 min (SOGL) ", "right")):
    ax.axvline(x, color=TEXT, lw=1.0, ls="--")
    ax.text(x, 1.035, txt, va="bottom", ha=ha, fontsize=8.5, color=TEXT)
ax.set_xticks([0.1, 1, 10, 30, 60, 300, 900, 3600])
ax.set_xticklabels(["0,1 s", "1 s", "10 s", "30 s", "1 min", "5 min", "15 min", "1 h"])
ax.set_yticks([0, 0.5, 1])
ax.set_yticklabels(["0", "50 %", "100 %"])
ax.set_xlim(0.1, 3600)
ax.set_ylim(0, 1.18)
ax.set_xlabel("timpul de la incident (scară logaritmică)")
ax.set_ylabel("partea din deficit acoperită")
ax.set_title("Cine acoperă deficitul după pierderea unui grup (schematic)")
ax.legend(loc="center left", fontsize=8, bbox_to_anchor=(1.0, 0.5))
ax.grid(False)
salveaza(fig, "f08-2-niveluri-reglaj")

# --- Figura 8.3: incidentul de referință în Europa continentală (problema 8.2) -------------
P_inc, Pfcr = 3000.0, 3000.0
lam_fcr = Pfcr / 0.2
M_ce = M_inertie(4.0, 300e3)
D_ce = 3000.0
curbe = []
for prof, culoare, stil, eticheta in ((profil_liniar, C1, "-", "liniar: 50 % la 15 s, 100 % la 30 s"),
                                      (profil_patratic, C3, "-.", "pătratic până la 50 % la 15 s"),
                                      (profil_intarziat, C4, "--", "nimic până la 15 s, apoi 50 % și liniar")):
    t, dfc, Pc = ce_simulare(P_inc, M_ce, D_ce, lam_fcr, Pfcr, prof, 120.0, dt=5e-3)
    curbe.append((t, dfc, Pc, culoare, stil, eticheta))
t0, dfc0, Pc0 = ce_simulare(P_inc, M_ce, 1e-9, lam_fcr, Pfcr, profil_liniar, 120.0, dt=5e-3)
tn_a, dn_a = ce_nadir_analitic(P_inc, M_ce, D_ce, Pfcr / 30)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.3))
for t, dfc, Pc, culoare, stil, eticheta in curbe:
    a1.plot(t, dfc * 1e3, color=culoare, ls=stil, label=eticheta)
    a2.plot(t, Pc, color=culoare, ls=stil, label=eticheta)
a1.plot(t0, dfc0 * 1e3, color=C2, ls=":", lw=1.6, label="liniar, fără autoreglarea sarcinii (D = 0)")
a2.plot(t0, Pc0, color=C2, ls=":", lw=1.6, label="liniar, D = 0")
a1.plot([tn_a], [dn_a * 1e3], "o", color=C1, ms=7, mec=FUNDAL, mew=2, zorder=5)
a1.annotate(f"nadir {mn(dn_a * 1e3)} mHz la {mn(tn_a, 1)} s\n(profil liniar, formula analitică)",
            xy=(tn_a, dn_a * 1e3), xytext=(40, -470), fontsize=9, color=TEXT,
            arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
for y, txt in ((-200, "abaterea staționară maximă 200 mHz"), (-800, "abaterea instantanee maximă 800 mHz")):
    a1.axhline(y, color=TEXT2, lw=0.9, ls=":")
    a1.text(119, y - 15, txt, ha="right", va="top", fontsize=8.5, color=TEXT)
a1.set_ylim(-1000, 50)
a1.set_xlabel("t [s]")
a1.set_ylabel("Δf [mHz]")
a1.set_title("Abaterea de frecvență")
a1.legend(loc="upper right", fontsize=8)
virgula(a1)
a2.set_xlabel("t [s]")
a2.set_ylabel(r"$P_\mathrm{FCR}$ [MW]")
a2.set_title("Puterea de reglaj primar")
a2.legend(loc="lower right", fontsize=8)
a2.set_ylim(0, 3400)
virgula(a2)
fig.tight_layout()
salveaza(fig, "f08-3-incident-referinta")

# --- Figura 8.4: două zone interconectate (problema 8.4) ---------------------------------
z1 = dict(M=M_inertie(5.0, 12e3), D=200.0, K=K_statism(12e3, 0.05), Tg=0.2, Tt=0.3)
z2 = dict(M=M_inertie(5.0, 24e3), D=400.0, K=K_statism(24e3, 0.05), Tg=0.2, Tt=0.3)
for z in (z1, z2):
    z["B"] = z["K"] + z["D"]
    z["Ki"] = 0.02
tp_, Yp, _ = doua_zone(z1, z2, 1000.0, 300.0, 600.0, cu_secundar=False, n=60001)
ts_, Ys, _ = doua_zone(z1, z2, 1000.0, 300.0, 600.0, cu_secundar=True, n=60001)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.0))
a1.plot(tp_[1:], Yp[0, 1:] * 1e3, color=C2, ls="--", label="numai reglaj primar (zona 1)")
a1.plot(ts_[1:], Ys[0, 1:] * 1e3, color=C1, label="primar + secundar (zona 1)")
a1.plot(ts_[1:], Ys[1, 1:] * 1e3, color=C3, lw=1.3, label="primar + secundar (zona 2)")
a1.set_xscale("log")
a1.set_xlim(0.1, 600)
a1.set_xlabel("t [s] (scară logaritmică)")
a1.set_ylabel("Δf [mHz]")
a1.set_title("Frecvența")
a1.legend(loc="lower right", fontsize=8.5)
a1.set_ylim(-60, 5)
a2.plot(ts_[1:], Ys[4, 1:], color=C1, label=r"$\Delta P_{m1}$ (zona cu incidentul)")
a2.plot(ts_[1:], Ys[6, 1:], color=C3, label=r"$\Delta P_{m2}$ (zona vecină)")
a2.plot(ts_[1:], Ys[2, 1:], color=C4, label=r"$\Delta P_{int,12}$ (export din zona 1)")
a2.plot(tp_[1:], Yp[2, 1:], color=C4, ls="--", lw=1.2, label=r"$\Delta P_{int,12}$, numai reglaj primar")
a2.axhline(0, color=TEXT2, lw=0.8)
a2.set_xscale("log")
a2.set_xlim(0.1, 600)
a2.set_xlabel("t [s] (scară logaritmică)")
a2.set_ylabel("P [MW]")
a2.set_title("Puterile (sarcina crește cu 300 MW în zona 1)")
a2.legend(loc="upper left", fontsize=8.5)
a2.set_ylim(-300, 420)
for ax in (a1, a2):
    ax.set_xticks([0.1, 1, 10, 100, 600])
    ax.set_xticklabels(["0,1", "1", "10", "100", "600"])
virgula(a2, "y")
virgula(a1, "y")
fig.tight_layout()
salveaza(fig, "f08-4-doua-zone")

# --- Figura 8.5: schema DASF față de cerințele NC ER --------------------------------------
praguri = [49.0 - 0.125 * i for i in range(9)]
cote = [0.05] * 9
praguri6 = [49.0, 48.8, 48.6, 48.4, 48.2, 48.0]
cote6e = [0.075] * 6
cote6n = [0.10, 0.08, 0.08, 0.08, 0.08, 0.03]
fg = np.linspace(47.9, 49.2, 2601)


def scara(pr, ct):
    return np.array([100 * np.sum([c for f, c in zip(pr, ct) if f >= x]) for x in fg])


fig, ax = plt.subplots(figsize=(8.5, 4.2))
fl = np.linspace(48.0, 49.0, 50)
dr = 5 + 40 * (49.0 - fl)
ax.fill_between(fl, dr - 7, dr + 7, color=ZONA, label="dreapta 5 % → 45 % cu banda ±7 %")
ax.plot(fl, dr, color=TEXT2, lw=1.0)
ax.step(fg, scara(praguri, cote), where="post", color=C1, label="schema aleasă: 9 trepte × 5 %")
ax.step(fg, scara(praguri6, cote6n), where="post", color=C3, ls="-.", lw=1.3,
        label="6 trepte inegale 10/8/8/8/8/3 % (respectă banda)")
ax.step(fg, scara(praguri6, cote6e), where="post", color=C2, ls="--", lw=1.3,
        label="6 trepte egale de 7,5 % (ies din bandă înainte de 48,0 Hz)")
ax.invert_xaxis()
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: fmt(v, 1)))
ax.set_xlabel("frecvența [Hz]")
ax.set_ylabel("sarcina deconectată cumulat [%]")
ax.set_title("Descărcarea automată a sarcinii la scăderea frecvenței")
ax.legend(loc="upper left", fontsize=8.5)
ax.set_ylim(-2, 55)
virgula(ax, "y")
salveaza(fig, "f08-5-schema-dasf")

# --- Figura 8.6: simularea insulei cu și fără DASF (problema 8.3) ------------------------
PL0, dP3 = 600.0, 180.0
M3, K3, D3 = M_inertie(4.0, 500.0), K_statism(500.0, 0.05), 12.0
trepte = [(f, c * PL0) for f, c in zip(praguri, cote)]
t, f_cu, Pm_cu, desc, act = dasf_simulare(dP3, M3, D3, K3, 0.2, 1.0, 80.0, trepte, 0.15, 12.0, dt=1e-3)
_, f_fara, Pm_fara, _, _ = dasf_simulare(dP3, M3, D3, K3, 0.2, 1.0, 80.0, [], 0.15, 12.0, dt=1e-3)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.0))
a1.plot(t, f_cu, color=C1, label="cu DASF")
a1.plot(t, f_fara, color=C2, ls="--", label="fără DASF")
for fp in praguri:
    a1.axhline(fp, color=GRILA, lw=0.8, zorder=0)
a1.axhline(47.5, color=TEXT2, lw=1.0, ls=":")
a1.text(11.8, 47.55, "47,5 Hz", ha="right", fontsize=8.5, color=TEXT)
for (i, ta, fp, Pd) in act:
    a1.plot([ta], [np.interp(ta, t, f_cu)], "v", color=C1, ms=6)
a1.set_xlim(0, 12)
a1.set_ylim(46.0, 50.2)
a1.set_xlabel("t [s]")
a1.set_ylabel("f [Hz]")
a1.set_title("Frecvența insulei (deficit 180 MW = 30 %)")
a1.legend(loc="lower right", fontsize=8.5)
virgula(a1)
a2.plot(t, desc, color=C1, label="sarcina deconectată de DASF")
a2.plot(t, Pm_cu, color=C3, label="ΔPm al grupurilor (rezervă 80 MW)")
a2.plot(t, -D3 * (f_cu - F0), color=C4, label="autoreglarea sarcinii D·|Δf|")
a2.axhline(dP3, color=C2, lw=1.0, ls=":")
a2.text(11.8, dP3 + 3, "deficitul de 180 MW", ha="right", fontsize=8.5, color=TEXT)
a2.set_xlim(0, 12)
a2.set_ylim(0, 200)
a2.set_xlabel("t [s]")
a2.set_ylabel("P [MW]")
a2.set_title("Acoperirea deficitului, cu DASF")
a2.legend(loc="center right", fontsize=8.5)
virgula(a2)
fig.tight_layout()
salveaza(fig, "f08-6-simulare-dasf")

# --- Figura 8.7: schema bloc a reglajului de tensiune al generatorului ---------------------
fig, ax = plt.subplots(figsize=(10, 3.6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 3.6)
ax.axis("off")
ax.add_patch(plt.Circle((1.6, 2.2), 0.22, fc=FUNDAL, ec=TEXT2, lw=1.3))
ax.text(1.6, 2.2, "Σ", ha="center", va="center", fontsize=12, color=TEXT)
ax.text(0.15, 2.45, r"$U_\mathrm{ref}$", fontsize=11, color=TEXT)
legatura(ax, (0.6, 2.2), (1.38, 2.2))
ax.text(1.2, 2.32, "+", fontsize=10, color=TEXT)
bloc(ax, 2.35, 1.75, 2.15, 0.9, "regulator +\nexcitație statică\n" + r"$K_A/(1 + sT_A)$", C1)
legatura(ax, (1.82, 2.2), (2.35, 2.2))
ax.text(1.95, 2.32, "ε", fontsize=10, color=TEXT)
bloc(ax, 5.3, 1.75, 1.9, 0.9, "generatorul în gol\n" + r"$1/(1 + sT'_{d0})$", C3)
legatura(ax, (4.5, 2.2), (5.3, 2.2))
ax.text(4.68, 2.32, r"$E_\mathrm{fd}$", fontsize=11, color=TEXT)
legatura(ax, (7.2, 2.2), (9.6, 2.2))
ax.text(9.0, 2.32, r"$U_t$", fontsize=11, color=TEXT)
bloc(ax, 5.3, 0.45, 1.9, 0.6, "traductor de tensiune", TEXT2)
legatura(ax, (8.4, 2.2), (8.4, 0.75), sageata_la_capat=False)
legatura(ax, (8.4, 0.75), (7.2, 0.75))
legatura(ax, (5.3, 0.75), (1.6, 0.75), sageata_la_capat=False)
legatura(ax, (1.6, 0.75), (1.6, 1.98))
ax.text(1.68, 1.75, "−", fontsize=12, color=TEXT)
bloc(ax, 0.2, 3.0, 2.5, 0.5, "limitatoare: OEL, UEL, V/Hz", C2, fs=8.5)
legatura(ax, (1.45, 3.0), (1.6, 2.42), stil="-|>")
bloc(ax, 3.0, 3.0, 2.0, 0.5, "stabilizator PSS (Δω, ΔP)", C5, fs=8.5)
legatura(ax, (3.0, 3.1), (1.78, 2.36))
ax.text(0.2, 0.15, "Semnalele limitatoarelor și ale stabilizatorului se adaugă la intrarea sumatorului; "
        "în problema 8.6 ele lipsesc (răspuns liniar, mic semnal).", fontsize=8.5, color=TEXT2)
salveaza(fig, "f08-7-schema-rat")

# --- Figura 8.8: răspunsul reglajului de tensiune (problema 8.6) ---------------------------
Td0, TA, dU = GEN["Td0_t"], 0.02, 0.01
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 3.9))
for KA, c in ((50.0, C3), (200.0, C1), (400.0, C2)):
    t, dE, dEfd = rat_ode(KA, TA, Td0, dU, 0.5, n=2001)
    a1.plot(t * 1e3, dE / dU * 100, color=c, label=f"KA = {KA:.0f}")
    a2.plot(t * 1e3, dEfd, color=c, label=f"KA = {KA:.0f}")
a1.axhline(100, color=TEXT2, lw=0.9, ls=":")
a1.set_xlabel("t [ms]")
a1.set_ylabel(r"$\Delta U_t\,/\,\Delta U_\mathrm{ref}$ [%]")
a1.set_title("Tensiunea la borne (treaptă de 1 % a consemnului)")
a1.legend(loc="lower right", fontsize=8.5)
virgula(a1)
a2.set_xlabel("t [ms]")
a2.set_ylabel(r"$\Delta E_\mathrm{fd}$ [u.r.]")
a2.set_title("Tensiunea de excitație")
a2.legend(loc="upper right", fontsize=8.5)
virgula(a2)
fig.tight_layout()
salveaza(fig, "f08-8-raspuns-rat")

# --- Figura 8.9: regulatorul automat de ploturi (problema 8.5) -----------------------------
ZT_mod = DATE["ukT"] * DATE["U20"]**2 / DATE["ST"]
RT = DATE["PkT"] * DATE["U20"]**2 / DATE["ST"]**2
XT = np.sqrt(ZT_mod**2 - RT**2)
U_ref, pas, T_int = 20.5e3, 0.0125, 30.0
t_d = np.arange(0, 86400.0, 1.0)
ora = t_d / 3600
P_d = 1e6 * (14 - 5 * np.cos(2 * np.pi * (ora - 4) / 24) + 3 * np.exp(-((ora - 19.5) / 1.5)**2))
Q_d = P_d * np.tan(np.arccos(0.9))
U_IT_d = 1e3 * (113.5 + 1.5 * np.cos(2 * np.pi * (ora - 3) / 24))
n_start = regulator_ploturi(t_d, U_IT_d, P_d, Q_d, RT, XT, U_ref, 0.01 * U_ref, T_int, pas)[3][-1]
Ub, Us, Ur, poz, nc = regulator_ploturi(t_d, U_IT_d, P_d, Q_d, RT, XT, U_ref, 0.01 * U_ref, T_int, pas,
                                        n0=int(n_start))
n_fix = int(np.round(np.mean(poz)))
Ub0, _, _, _, _ = regulator_ploturi(t_d, U_IT_d, P_d, Q_d, RT, XT, U_ref, 1e9, T_int, pas, n0=n_fix)
t_h = np.arange(0, 1800.0, 1.0)
Pc = np.full(len(t_h), 15e6)
Uh, _, _, pozh, _ = regulator_ploturi(t_h, np.full(len(t_h), 113e3), Pc, Pc * np.tan(np.arccos(0.9)), RT, XT, U_ref,
                                      0.005 * U_ref, T_int, pas)


def rarefiere(poz, pas_s=60):
    """Indicii eșantioanelor păstrate pentru desen: unul la `pas_s` secunde, plus eșantioanele
    din jurul fiecărei comutări (ca salturile de tensiune să rămână verticale)."""
    k = set(range(0, len(poz), pas_s)) | {len(poz) - 1}
    for j in np.nonzero(np.diff(poz))[0]:
        k |= {j, j + 1}
    return np.array(sorted(k))


kz = rarefiere(poz)
k0 = np.arange(0, len(t_d), 60)
kh = rarefiere(pozh, pas_s=10)
kp = np.concatenate(([0], np.nonzero(np.diff(poz))[0] + 1, [len(poz) - 1]))
fig = plt.figure(figsize=(10.5, 6.2))
g = fig.add_gridspec(2, 2, width_ratios=[2.2, 1], height_ratios=[1.4, 1])
a1 = fig.add_subplot(g[0, 0])
a1.fill_between([0, 24], (U_ref * 0.99) / 1e3, (U_ref * 1.01) / 1e3, color=ZONA, label=r"banda $U_\mathrm{ref}$ ± 1 %")
a1.plot(ora[k0], Ub0[k0] / 1e3, color=TEXT2, lw=1.0, ls="--", label=f"plot blocat în poziția {mn(n_fix)}")
a1.plot(ora[kz], Ub[kz] / 1e3, color=C1, lw=1.4, label="cu regulator de ploturi")
a1.set_xlim(0, 24)
a1.set_ylabel("U pe bara de 20 kV [kV]")
a1.set_title("O zi de funcționare (sarcina 9 … 20 MW, U pe 110 kV 112 … 115 kV)")
a1.legend(loc="lower left", fontsize=8.5)
virgula(a1)
a3 = fig.add_subplot(g[1, 0], sharex=a1)
a3.step(ora[kp], poz[kp], where="post", color=C2)
a3.set_xlabel("ora")
a3.set_ylabel("poziția plotului")
a3.set_xticks(range(0, 25, 3))
a3.set_title(f"{nc} comutări pe zi", fontsize=10)
a3.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: mn(v)))
a2 = fig.add_subplot(g[:, 1])
a2.fill_between([0, t_h[-1] / 60], (U_ref * 0.995) / 1e3, (U_ref * 1.005) / 1e3, color=ZONA)
a2.plot(t_h[kh] / 60, Uh[kh] / 1e3, color=C2, lw=1.2)
a2.set_xlabel("t [min]")
a2.set_ylabel("U [kV]")
a2.set_title("Lățimea benzii 1 % < pasul de 1,14–1,39 %:\npendulare (sarcină constantă)", fontsize=10)
virgula(a2)
fig.tight_layout()
salveaza(fig, "f08-9-ploturi")
