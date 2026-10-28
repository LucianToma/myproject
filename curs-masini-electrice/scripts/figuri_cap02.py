"""Figurile capitolului 2 – Mașina asincronă."""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq
import schemdraw
import schemdraw.elements as elm
from comun import C1, C2, C3, C4, C5, TEXT, TEXT2, GRILA, FUNDAL, FIGURI, salveaza, virgula, salveaza_schema
from modele import motor_M15, kloss, sk_din_catalog, verifica

schemdraw.use("matplotlib")
schemdraw.config(fontsize=12, bgcolor=FUNDAL, lw=1.6)
M = motor_M15()
MD = motor_M15(colivie_dubla=True)
Pn, nn, In = 15e3, 1466, 27.6
Mn = Pn / (2 * np.pi * nn / 60)
ALBASTRU = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"]   # rampă secvențială (ordinală)

# --- Secțiune transversală prin motorul asincron cu rotor în colivie ---------
fig, ax = plt.subplots(figsize=(6.6, 5.0))
ax.add_patch(plt.Circle((0, 0), 1.0, color="#d9d8d3", ec=TEXT2, lw=1))
ax.add_patch(plt.Circle((0, 0), 0.62, color=FUNDAL, ec=TEXT2, lw=1))
for k in range(36):
    a = 2 * np.pi * k / 36
    ax.add_patch(plt.Rectangle((0.64, -0.03), 0.17, 0.06, angle=np.degrees(a), rotation_point=(0, 0),
                               color=C2, ec=FUNDAL, lw=0.5))
ax.add_patch(plt.Circle((0, 0), 0.595, color="#c9c8c2", ec=TEXT2, lw=1))
for k in range(28):
    a = 2 * np.pi * (k + 0.5) / 28
    ax.add_patch(plt.Circle((0.53 * np.cos(a), 0.53 * np.sin(a)), 0.035, color=C1, ec=FUNDAL, lw=0.5))
ax.add_patch(plt.Circle((0, 0), 0.15, color=TEXT2, ec=TEXT, lw=1))
etichete = [((0.75, 0.75), (1.12, 1.05), "stator (tole) și carcasă", "left"),
            ((0.78, 0.20), (1.12, 0.40), "înfășurare statorică\nîn crestături", "left"),
            ((0.607, -0.12), (1.12, -0.30), "întrefier (zecimi de mm)", "left"),
            ((0.37, -0.38), (1.12, -0.85), "bare ale coliviei", "left"),
            ((-0.3, -0.3), (-1.25, -1.05), "rotor (tole)", "center"),
            ((-0.1, 0.1), (-1.3, 0.95), "arbore", "center")]
for xy, xt, t, ha in etichete:
    ax.annotate(t, xy=xy, xytext=xt, color=TEXT, fontsize=9, ha=ha, va="center",
                arrowprops=dict(arrowstyle="-", color=TEXT, lw=0.8))
ax.set_xlim(-1.6, 2.4)
ax.set_ylim(-1.3, 1.25)
ax.set_aspect("equal")
ax.axis("off")
salveaza(fig, "f02-2-sectiune")

# --- Colivia rotorică (schiță) ---------------------------------------------
fig, ax = plt.subplots(figsize=(5.0, 2.6))
t = np.linspace(0, 2 * np.pi, 200)
for x0 in (0, 3):
    ax.plot(x0 + 0.25 * np.cos(t), np.sin(t), color=C2, lw=4)
for k in range(16):
    a = 2 * np.pi * k / 16
    y, xo = np.sin(a), 0.25 * np.cos(a)
    vizibil = np.cos(a) >= 0
    ax.plot([xo, 3 + xo], [y, y], color=C1 if vizibil else "#b7d3f6", lw=2.2 if vizibil else 1.4,
            zorder=3 if vizibil else 1)
ax.text(1.5, -1.35, "bare (Al sau Cu) scurtcircuitate la capete de inele", ha="center", color=TEXT, fontsize=9)
ax.text(-0.4, 1.15, "inel", color=TEXT2, fontsize=9)
ax.text(2.9, 1.15, "inel", color=TEXT2, fontsize=9)
ax.set_xlim(-0.6, 3.6)
ax.set_ylim(-1.55, 1.35)
ax.set_aspect("equal")
ax.axis("off")
salveaza(fig, "f02-5-colivie")

# --- Schema echivalentă pe fază ---------------------------------------------
H = 4.5
with schemdraw.Drawing(show=False) as d:
    d.add(elm.Dot(open=True).at((0, 0)))
    d.add(elm.Line().right(0.8).label("$\\underline{I}_1$ →", loc="top"))
    d.add(elm.Resistor().right().label("$R_1$"))
    d.add(elm.Inductor2(loops=3).right().label("$X_{1\\sigma}$"))
    d.add(elm.Line().right(1.0))
    nod = d.add(elm.Dot())
    d.add(elm.Line().right(1.0))
    d.add(elm.Inductor2(loops=3).right().label("$X'_{2\\sigma}$"))
    d.add(elm.Resistor().right().label("$R'_2$"))
    d.add(elm.Line().right(0.8).label("$\\underline{I}'_2$ →", loc="top"))
    colt = d.here
    d.add(elm.Resistor().down(H).label("$R'_2\\,\\dfrac{1-s}{s}$", loc="bottom", ofst=0.15))
    d.add(elm.Line().left(colt[0]))
    xn = nod.center.x
    d.add(elm.Inductor2(loops=3).at((xn, 0)).to((xn, -H)).label("$X_m$", loc="bottom"))
    d.add(elm.Dot().at((xn, -H)))
    d.add(elm.Dot(open=True).at((0, -H)))
    d.add(elm.Gap().at((0, 0)).to((0, -H)).label(["+", "$\\underline{U}_1$", "–"]))
    d.add(elm.Label().at((colt[0] + 1.6, -H / 2 - 0.9)).label("rezistența\nde sarcină\n(putere mecanică)",
                                                             fontsize=10, color=TEXT2))
    salveaza_schema(d, "f02-6-schema-echivalenta")

# --- Bilanțul puterilor (punctul din problema 2.2) ---------------------------
s = (1500 - 1466) / 1500
r = M.punct(s)
fig, ax = plt.subplots(figsize=(9.0, 3.6))
ax.add_patch(plt.Polygon([(0, 0), (9.2, 0), (9.2, -0.25), (9.9, 0.5), (9.2, 1.25), (9.2, 1.0), (0, 1.0)],
                         facecolor="#cde2fb", edgecolor=C1, lw=1.2))
statii = [(2.3, "stator", f"P$_{{Cu1}}$ = {r['PCu1']:.0f} W\n(Joule, stator)"),
          (5.0, "rotor", f"P$_{{Cu2}}$ = s·P$_δ$ = {r['PCu2']:.0f} W\n(Joule, rotor)"),
          (7.7, "", f"P₀ = P$_{{Fe}}$ + P$_{{mec}}$ = {M.P0:.0f} W\n(fier, frecări, ventilație)")]
for x, _, t in statii:
    ax.annotate("", xy=(x, -0.85), xytext=(x, 0.0), arrowprops=dict(arrowstyle="-|>", color=C2, lw=2.2,
                                                                   mutation_scale=16))
    ax.text(x, -0.95, t, ha="center", va="top", color=TEXT, fontsize=9)
etape = [(0.9, f"P₁ = {r['P1'] / 1e3:.2f} kW"), (3.65, f"P$_δ$ = {r['Pd'] / 1e3:.2f} kW"),
         (6.35, f"P$_{{mi}}$ = {r['Pmi'] / 1e3:.2f} kW"), (9.05, f"P₂ = {r['P2'] / 1e3:.2f} kW")]
for x, t in etape:
    ax.text(x, 0.5, t.replace(".", ","), ha="center", va="center", color=TEXT, fontsize=10)
ax.text(0.9, 1.15, "absorbită din rețea", ha="center", color=TEXT2, fontsize=8.5)
ax.text(3.65, 1.15, "electromagnetică\n(trece prin întrefier)", ha="center", color=TEXT2, fontsize=8.5)
ax.text(6.35, 1.15, "mecanică internă", ha="center", color=TEXT2, fontsize=8.5)
ax.text(9.05, 1.35, "utilă la arbore", ha="center", color=TEXT2, fontsize=8.5)
ax.set_xlim(-0.2, 10.1)
ax.set_ylim(-1.85, 1.75)
ax.axis("off")
ax.set_title(f"Bilanțul puterilor – motorul M15 la n = 1466 rot/min (η = {100 * r['eta']:.1f} %)".replace(".", ","),
             color=TEXT)
salveaza(fig, "f02-7-bilant-puteri")

# --- Caracteristica mecanică completă: regimuri de funcționare ---------------
n = np.linspace(-900, 3000, 1500)
s_ = (1500 - n) / 1500
s_[np.abs(s_) < 1e-6] = 1e-6
Mc = np.array([M.cuplu(x) for x in s_])
fig, ax = plt.subplots(figsize=(7.4, 4.2))
ax.axvspan(-900, 0, color="#f3f2ee", lw=0)
ax.axvspan(1500, 3000, color="#f3f2ee", lw=0)
ax.plot(n, Mc, color=C1)
ax.axhline(0, color=TEXT2, lw=0.8)
ax.axvline(0, color=TEXT2, lw=0.8)
ax.axvline(1500, color=TEXT2, lw=0.8)
ax.text(-450, 290, "FRÂNĂ\n(contracurent)\ns > 1", ha="center", va="top", color=TEXT, fontsize=9)
ax.text(750, -120, "MOTOR\n0 < s < 1", ha="center", va="top", color=TEXT, fontsize=9)
ax.text(2250, 290, "GENERATOR\ns < 0", ha="center", va="top", color=TEXT, fontsize=9)
sk_m, Mmax_m = M.cuplu_maxim()
ax.plot([1500 * (1 - sk_m)], [Mmax_m], "o", color=C1, ms=8, mec=FUNDAL, mew=2)
ax.annotate(f"M$_{{max}}$, s$_k$ = {sk_m:.3f}".replace(".", ","), xy=(1500 * (1 - sk_m), Mmax_m),
            xytext=(250, 250), color=TEXT, arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
ax.plot([nn], [r["Me"]], "o", color=C2, ms=8, mec=FUNDAL, mew=2)
ax.annotate("punct nominal", xy=(nn, r["Me"]), xytext=(1700, 120), color=TEXT,
            arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
ax.text(1480, -440, "n₁ = 1500", color=TEXT2, fontsize=9, ha="right")
ax.set_xlim(-900, 3000)
ax.set_xlabel("n [rot/min]")
ax.set_ylabel("M [N·m]")
ax.set_title("Caracteristica mecanică M(n) – schema echivalentă a motorului M15")
virgula(ax)
salveaza(fig, "f02-8-regimuri")

# --- Modelul cu parametri constanți vs colivia dublă vs catalog ---------------
n = np.linspace(0, 1499, 600)
s_ = (1500 - n) / 1500
sn = (1500 - nn) / 1500
sk = sk_din_catalog(sn, 3.1)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.9))
a1.plot(n, [M.cuplu(x) for x in s_], color=C1, label="colivie simplă (parametri constanți)")
a1.plot(n, [MD.cuplu(x) for x in s_], color=C2, label="colivie dublă (refulare)")
a1.plot(n, kloss(s_, 3.1 * Mn, sk), color=C3, label="formula lui Kloss (din catalog)")
a1.plot([0, 1500 * (1 - sk), nn], [2.3 * Mn, 3.1 * Mn, Mn], "o", color=TEXT, ms=6, label="date de catalog")
a1.set_xlabel("n [rot/min]")
a1.set_ylabel("M [N·m]")
a1.set_title("Cuplul")
a2.plot(n, [abs(M.punct(x)["I1"]) for x in s_], color=C1)
a2.plot(n, [abs(MD.punct(x)["I1"]) for x in s_], color=C2)
a2.plot([0, nn], [6.8 * In, In], "o", color=TEXT, ms=6)
a2.set_xlabel("n [rot/min]")
a2.set_ylabel("I [A] (curent de linie)")
a2.set_title("Curentul absorbit")
fig.legend(*a1.get_legend_handles_labels(), loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.07))
for a in (a1, a2):
    virgula(a)
salveaza(fig, "f02-12-model-vs-catalog")

# --- Caracteristicile de funcționare ----------------------------------------
s_ = np.linspace(0.0015, 0.04, 300)
pts = [MD.punct(x) for x in s_]
P2 = np.array([p["P2"] for p in pts]) / Pn
masca = (P2 > 0.05) & (P2 < 1.3)
fig, axs = plt.subplots(2, 2, figsize=(9, 5.6), sharex=True)
date = [("η [%]", [100 * p["eta"] for p in pts], C1), ("cos φ", [p["cos_phi"] for p in pts], C1),
        ("I [A]", [abs(p["I1"]) for p in pts], C1), ("n [rot/min]", [p["n"] for p in pts], C1)]
for ax, (et, y, c) in zip(axs.flat, date):
    ax.plot(P2[masca], np.array(y)[masca], color=c)
    ax.axvline(1.0, color=TEXT2, lw=0.8)
    ax.set_title(et, fontsize=10, loc="left")
    virgula(ax)
for ax in axs[1]:
    ax.set_xlabel("P₂/Pₙ")
fig.suptitle("Caracteristicile de funcționare ale motorului M15 (U = Uₙ, f = fₙ)", color=TEXT, fontsize=11)
fig.tight_layout()
salveaza(fig, "f02-9-caracteristici-functionare")

# --- Influența rezistenței rotorice -------------------------------------------
n = np.linspace(0, 1499, 600)
s_ = (1500 - n) / 1500
fig, ax = plt.subplots(figsize=(6.8, 4.0))
for kR, c in ((1, C1), (3, C2), (6, C3)):
    m = motor_M15()
    m.R2 *= kR
    ax.plot(n, [m.cuplu(x) for x in s_], color=c, label=f"R'₂ × {kR}" if kR > 1 else "R'₂ (rotor scurtcircuitat)")
ax.set_xlabel("n [rot/min]")
ax.set_ylabel("M [N·m]")
ax.set_title("Rezistență rotorică mărită: s$_k$ crește, M$_{max}$ rămâne același")
ax.legend(loc="lower left")
virgula(ax)
salveaza(fig, "f02-11-rezistenta-rotorica")

# --- Familia de caracteristici la U/f = constant -------------------------------
fig, ax = plt.subplots(figsize=(7.4, 4.2))
for f, c in zip((10, 20, 30, 40, 50), ALBASTRU):
    m = MD.la_frecventa(f, 400 * f / 50)
    n1 = 30 * f
    nn_ = np.linspace(0, n1 * 0.9999, 400)
    ax.plot(nn_, [m.cuplu((n1 - x) / n1) for x in nn_], color=c)
    ax.text(n1 + 15, 15, f"{f} Hz", color=TEXT, fontsize=9)
ax.axhline(Mn, color=C2, lw=1.6)
ax.text(30, Mn + 8, "cuplu de sarcină constant Mₙ", color=TEXT, fontsize=9)
ax.set_xlim(0, 1650)
ax.set_xlabel("n [rot/min]")
ax.set_ylabel("M [N·m]")
ax.set_title("Alimentare de la convertor cu U/f = constant (fără compensarea R₁)")
virgula(ax)
salveaza(fig, "f02-13-familie-uf")

# --- Pornirea stea-triunghi ---------------------------------------------------
n = np.linspace(0, 1499, 600)
s_ = (1500 - n) / 1500
# În stea, fiecare înfășurare (impedanța 3·Z a stelei echivalente) primește U/√3.
# Echivalent: aceeași stea echivalentă Z alimentată la U_f/√3 dă același cuplu, iar
# curentul de linie real este I/√3 (vezi problema 2.4: raportul curenților este 1/3).
MY = motor_M15(colivie_dubla=True)
MY.U = MD.U / np.sqrt(3)
verifica("Ip_Y = Ip_Δ/3", abs(MY.punct(1.0)["I1"]) / np.sqrt(3), abs(MD.punct(1.0)["I1"]) / 3)
verifica("Mp_Y = Mp_Δ/3", MY.cuplu(1.0), MD.cuplu(1.0) / 3)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.9))
a1.plot(n, [MD.cuplu(x) for x in s_], color=C1, label="Δ (pornire directă)")
a1.plot(n, [MY.cuplu(x) for x in s_], color=C2, label="Y (U/√3 pe fază)")
a1.plot(n, 0.1 * Mn + 0.8 * Mn * (n / nn) ** 2, color=C3, label="ventilator")
a1.plot(n, np.full_like(n, Mn), color=C4, label="transportor (M ≈ Mₙ)")
a1.set_xlabel("n [rot/min]")
a1.set_ylabel("M [N·m]")
a1.set_title("Cuplul")
a2.plot(n, [abs(MD.punct(x)["I1"]) for x in s_], color=C1)
a2.plot(n, [abs(MY.punct(x)["I1"]) / np.sqrt(3) for x in s_], color=C2)
a2.set_xlabel("n [rot/min]")
a2.set_ylabel("I [A] (curent de linie)")
a2.set_title("Curentul de linie")
fig.legend(*a1.get_legend_handles_labels(), loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.07))
for a in (a1, a2):
    virgula(a)
salveaza(fig, "f02-10-stea-triunghi")
