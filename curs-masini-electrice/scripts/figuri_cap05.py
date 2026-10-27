"""Figurile capitolului 5 – Acționări electrice."""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
import schemdraw
import schemdraw.elements as elm
from schemdraw.segments import SegmentCircle
from comun import C1, C2, C3, C4, C5, TEXT, TEXT2, GRILA, FUNDAL, FIGURI, salveaza, virgula
from modele import kloss, sk_din_catalog, motor_M15, verifica

schemdraw.use("matplotlib")
schemdraw.config(fontsize=12, bgcolor=FUNDAL, lw=1.6)

Pn, nn, lam = 15e3, 1466, 3.1
Wn = 2 * np.pi * nn / 60
Mn = Pn / Wn
sn = (1500 - nn) / 1500
sk = sk_din_catalog(sn, lam)
Mmax = lam * Mn
W1 = 2 * np.pi * 25

# --- Caracteristicile mecanice ale mașinilor de lucru -----------------------
w = np.linspace(0.001, 1.2, 300)
fig, ax = plt.subplots(figsize=(6.8, 4.0))
ax.plot(w, np.ones_like(w), color=C1, label="M = const (macara, transportor, compresor cu piston)")
ax.plot(w, w, color=C2, label="M ∝ Ω (frecare vâscoasă, generator pe rezistență)")
ax.plot(w, w**2, color=C3, label="M ∝ Ω² (ventilator, pompă centrifugă)")
m = w > 0.3
ax.plot(w[m], 1 / w[m], color=C4, label="P = const, M ∝ 1/Ω (bobinator, strung la viteză mare)")
ax.set_xlim(0, 1.2)
ax.set_ylim(0, 2.0)
ax.set_xlabel("Ω/Ωₙ")
ax.set_ylabel("M$_r$/M$_{rn}$")
ax.set_title("Caracteristici mecanice tipice ale mașinilor de lucru")
ax.legend(loc="upper center", fontsize=8.5, bbox_to_anchor=(0.5, -0.17), ncol=1)
virgula(ax)
salveaza(fig, "f05-1-caracteristici-sarcina")

# --- Cele patru cadrane ------------------------------------------------------
fig, ax = plt.subplots(figsize=(6.4, 5.6))
ax.axhline(0, color=TEXT, lw=1.2)
ax.axvline(0, color=TEXT, lw=1.2)
ax.annotate("", xy=(1.15, 0), xytext=(1.0, 0), arrowprops=dict(arrowstyle="-|>", color=TEXT))
ax.annotate("", xy=(0, 1.15), xytext=(0, 1.0), arrowprops=dict(arrowstyle="-|>", color=TEXT))
ax.text(1.12, -0.09, "M", color=TEXT, fontsize=12)
ax.text(0.04, 1.1, "Ω", color=TEXT, fontsize=12)
cadrane = [(0.55, 0.55, "I – MOTOR\nsens direct", "M > 0, Ω > 0, P = MΩ > 0\nex.: ridicarea sarcinii", C1),
           (-0.55, 0.55, "II – FRÂNĂ (generator)\nsens direct", "M < 0, Ω > 0, P < 0\nex.: oprire rapidă, coborâre\npe pantă a unui vehicul", C2),
           (-0.55, -0.55, "III – MOTOR\nsens invers", "M < 0, Ω < 0, P > 0\nex.: coborârea forțată\na cârligului gol", C3),
           (0.55, -0.55, "IV – FRÂNĂ (generator)\nsens invers", "M > 0, Ω < 0, P < 0\nex.: coborârea sarcinii grele\n(energia poate fi recuperată)", C4)]
for x, y, t, d, c in cadrane:
    ax.add_patch(plt.Rectangle((x - 0.47, y - 0.36), 0.94, 0.72, facecolor=FUNDAL, edgecolor=c, lw=2))
    ax.text(x, y + 0.2, t, ha="center", va="center", color=TEXT, fontsize=9, fontweight="bold")
    ax.text(x, y - 0.13, d, ha="center", va="center", color=TEXT, fontsize=8.5)
ax.set_xlim(-1.1, 1.25)
ax.set_ylim(-1.05, 1.2)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Cadranele de funcționare ale unei acționări (exemplu: troliu de macara)")
salveaza(fig, "f05-2-cadrane")

# --- Stabilitatea punctelor de funcționare -----------------------------------
n = np.linspace(0, 1499.5, 800)
s = (1500 - n) / 1500
Mr = 2.0 * Mn
fig, ax = plt.subplots(figsize=(6.8, 4.0))
ax.plot(n, kloss(s, Mmax, sk), color=C1, label="motor (formula lui Kloss)")
ax.axhline(Mr, color=C2, lw=2, label="sarcină M$_r$ = 2·Mₙ = const")
lp = Mmax / Mr
for nume, sx, txt, xt in (("A", sk * (lp - np.sqrt(lp**2 - 1)), "A – stabil", (1150, 120)),
                          ("B", sk * (lp + np.sqrt(lp**2 - 1)), "B – instabil", (650, 120))):
    ax.plot([1500 * (1 - sx)], [Mr], "o", color=TEXT, ms=8, mec=FUNDAL, mew=2)
    ax.annotate(f"{txt}\nn = {1500 * (1 - sx):.0f} rot/min", xy=(1500 * (1 - sx), Mr), xytext=xt,
                color=TEXT, fontsize=9, arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
ax.set_xlabel("n [rot/min]")
ax.set_ylabel("M [N·m]")
ax.set_title("Criteriul de stabilitate: dM/dΩ < dM$_r$/dΩ")
ax.legend(loc="upper left")
virgula(ax)
salveaza(fig, "f05-3-stabilitate")

# --- Accelerarea unui ventilator cu cuplu motor constant (problema 5.2) ---------
J, M = 1.0, 1.2 * Mn
k = 0.8 * Mn / Wn**2
t_an = J / np.sqrt(M * k) * np.arctanh(Wn * np.sqrt(k / M))
t = np.linspace(0, t_an, 400)
W_an = np.sqrt(M / k) * np.tanh(t * np.sqrt(M * k) / J)
sol = solve_ivp(lambda t_, y: [(M - k * y[0] ** 2) / J], (0, t_an), [0.0], t_eval=np.arange(0, t_an, 0.15),
                rtol=1e-9, atol=1e-9)
verifica("Ω(t) analitic vs numeric (max abatere)", np.max(np.abs(np.interp(sol.t, t, W_an) - sol.y[0])), 0.0, atol=0.05)
fig, ax = plt.subplots(figsize=(6.8, 3.9))
ax.plot(t, W_an * 30 / np.pi, color=C1, label="soluția analitică Ω = Ω$_∞$·tanh(t√(Mk)/J)")
ax.plot(sol.t, sol.y[0] * 30 / np.pi, "o", color=C2, ms=6, mec=FUNDAL, mew=1.5, label="integrare numerică")
ax.plot([t_an, 4.2], [nn, nn], color=C1, lw=1.2)
ax.text(1.95, nn + 45, "apoi regulatorul menține n = nₙ", color=TEXT2, fontsize=9)
t_c = J * Wn / (M - 0.8 * Mn)
ax.plot([0, t_c], [0, nn], color=C3, label="ipoteza (greșită) M$_r$ = const = M$_r$(Ωₙ)")
ax.axvline(t_an, color=TEXT2, lw=0.8)
ax.text(t_an + 0.04, 900, f"t = {t_an:.2f} s".replace(".", ","), color=TEXT, fontsize=9)
ax.annotate(f"t = {t_c:.2f} s".replace(".", ","), xy=(t_c, nn), xytext=(3.3, 650), color=TEXT, fontsize=9,
            arrowprops=dict(arrowstyle="-", color=TEXT2, lw=0.8))
ax.set_xlim(0, 4.2)
ax.set_ylim(0, 1700)
ax.set_xlabel("t [s]")
ax.set_ylabel("n [rot/min]")
ax.set_title("Pornirea unui ventilator cu cuplu motor constant 1,2·Mₙ")
ax.legend(loc="lower right", fontsize=8.5)
virgula(ax)
salveaza(fig, "f05-4-accelerare-ventilator")

# --- Pornirea directă a motorului M15 cu ventilator (model cvasistaționar) ------
MD = motor_M15(colivie_dubla=True)
kv = 0.8 * Mn / Wn**2
Jt = 1.0


def deriv(t_, y):
    Wx = min(y[0], W1 * 0.99999)
    sx = 1 - Wx / W1
    return [(MD.cuplu(sx) - kv * Wx**2) / Jt]


sol = solve_ivp(deriv, (0, 2.0), [0.0], max_step=2e-3)
tt = sol.t
WW = sol.y[0]
II = [abs(MD.punct(max(1 - x / W1, 1e-5))["I1"]) for x in WW]
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.8, 5.2), sharex=True)
a1.plot(tt, WW * 30 / np.pi, color=C1)
a1.set_ylabel("n [rot/min]")
a1.set_title("Pornire directă: motor M15 + ventilator, J = 1 kg·m² (model cvasistaționar)", fontsize=10)
a2.plot(tt, II, color=C2)
a2.axhline(27.6, color=TEXT2, lw=0.8)
a2.text(1.5, 32, "Iₙ = 27,6 A", color=TEXT2, fontsize=9)
a2.set_ylabel("I [A]")
a2.set_xlabel("t [s]")
for a in (a1, a2):
    virgula(a)
salveaza(fig, "f05-5-pornire-directa")
t_porn = tt[np.argmax(WW * 30 / np.pi > 0.95 * 1470)]
print(f"  pornire directă: n atinge 95 % din viteza finală după ≈ {t_porn:.2f} s")

# --- Ciclul de sarcină și încălzirea (problema 5.3) -----------------------------
Mi = np.array([120.0, 60.0, 20.0])
ti = np.array([10.0, 30.0, 20.0])
M_ech = np.sqrt(np.sum(Mi**2 * ti) / ti.sum())
M_med = np.sum(Mi * ti) / ti.sum()
Mn11 = 11e3 / (2 * np.pi * 1460 / 60)
Pc, Pvn, Rth, tau = 350.0, 700.0, 0.08, 1200.0
pierderi = lambda Mx: Pc + Pvn * (Mx / Mn11) ** 2
dt = 0.5
Pl = np.concatenate([np.full(int(tt_ / dt), pierderi(Mx)) for Mx, tt_ in zip(Mi, ti)])
th, istoric = 0.0, []
for _ in range(150):
    for P in Pl:
        th += dt * (P * Rth - th) / tau
        istoric.append(th)
timp = np.arange(len(istoric)) * dt / 60
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.8, 5.6))
tc = np.concatenate([[0], np.cumsum(np.tile(ti, 3))])
Mc = np.tile(Mi, 3)
a1.step(tc, np.concatenate([Mc, [Mc[-1]]]), where="post", color=C1, label="cuplul cerut M(t)")
a1.axhline(M_ech, color=C2, lw=1.6, label=f"M$_{{ech}}$ = {M_ech:.1f} N·m".replace(".", ","))
a1.axhline(M_med, color=C3, lw=1.6, label=f"media aritmetică = {M_med:.1f} N·m".replace(".", ","))
a1.set_xlabel("t [s]")
a1.set_ylabel("M [N·m]")
a1.set_title("Ciclul de sarcină (trei perioade)", fontsize=10)
a1.set_ylim(0, 135)
a1.legend(loc="upper center", fontsize=8.5, ncol=3, bbox_to_anchor=(0.5, -0.22))
a2.plot(timp, istoric, color=C1, label="ciclul real")
tlin = np.linspace(0, timp[-1], 300)
a2.plot(tlin, pierderi(M_ech) * Rth * (1 - np.exp(-tlin * 60 / tau)), color=C2, label="M$_{ech}$ constant")
a2.plot(tlin, pierderi(M_med) * Rth * (1 - np.exp(-tlin * 60 / tau)), color=C3, label="media aritmetică constantă")
a2.set_xlabel("t [min]")
a2.set_ylabel("Δθ [K]")
a2.set_title("Supratemperatura înfășurării (model termic de ordinul 1, τ = 20 min)", fontsize=10)
a2.legend(loc="lower right", fontsize=8.5)
for a in (a1, a2):
    virgula(a)
fig.tight_layout()
salveaza(fig, "f05-6-ciclu-incalzire")

# --- Structura convertorului de frecvență (schemă bloc) ------------------------
fig, ax = plt.subplots(figsize=(10, 3.4))
blocuri = [(0.0, "Rețea\n3 × 400 V\n50 Hz", "#f3f2ee"), (2.2, "Redresor\n(6 diode)\nc.a. → c.c.", "#cde2fb"),
           (4.4, "Circuit intermediar\nc.c. (condensator)\nU$_d$ ≈ 540 V", "#cde2fb"),
           (6.6, "Invertor PWM\n(6 tranzistoare IGBT)\nc.c. → c.a.", "#cde2fb"),
           (8.8, "Motor\nasincron 3~\nf, U variabile", "#f3f2ee")]
for x, t, c in blocuri:
    ax.add_patch(plt.Rectangle((x, 0), 1.8, 1.3, facecolor=c, edgecolor=C1, lw=1.4))
    ax.text(x + 0.9, 0.65, t, ha="center", va="center", color=TEXT, fontsize=9)
for x in (1.8, 4.0, 6.2, 8.4):
    ax.annotate("", xy=(x + 0.4, 0.65), xytext=(x, 0.65), arrowprops=dict(arrowstyle="-|>", color=TEXT, lw=1.4))
ax.add_patch(plt.Rectangle((6.6, 2.0), 1.8, 0.9, facecolor=FUNDAL, edgecolor=C2, lw=1.4))
ax.text(7.5, 2.45, "Comandă\n(U/f sau vectorială)", ha="center", va="center", color=TEXT, fontsize=9)
ax.annotate("", xy=(7.5, 1.3), xytext=(7.5, 2.0), arrowprops=dict(arrowstyle="-|>", color=C2, lw=1.4))
ax.add_patch(plt.Rectangle((4.4, 2.0), 1.8, 0.9, facecolor=FUNDAL, edgecolor=C3, lw=1.4))
ax.text(5.3, 2.45, "Chopper + rezistor\nde frânare (opțional)", ha="center", va="center", color=TEXT, fontsize=9)
ax.plot([5.3, 5.3], [1.3, 2.0], color=C3, lw=1.4)
ax.text(5.3, -0.35, "Redresorul cu diode nu poate trimite energie înapoi în rețea: la frânare,\n"
                    "energia se disipă în rezistor sau se folosește un redresor activ (recuperare).",
        ha="center", va="top", color=TEXT2, fontsize=8.5)
ax.set_xlim(-0.1, 10.7)
ax.set_ylim(-1.2, 3.0)
ax.axis("off")
salveaza(fig, "f05-7-convertor-frecventa")

# --- Modulația PWM sinus–triunghi -------------------------------------------
f1, fc, ma, Ud = 50.0, 750.0, 0.8, 540.0
t = np.linspace(0, 1 / f1, 20001)[:-1]
ref = ma * np.sin(2 * np.pi * f1 * t)
tri = 2 / np.pi * np.arcsin(np.sin(2 * np.pi * fc * t + np.pi / 2))
u = np.where(ref > tri, Ud / 2, -Ud / 2)
fund = 2 * np.mean(u * np.sin(2 * np.pi * f1 * t))
verifica("amplitudinea fundamentalei PWM = m_a·U_d/2", fund, ma * Ud / 2, rtol=0.02)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 5.0), sharex=True)
a1.plot(t * 1e3, tri, color=TEXT2, lw=1.0, label="purtătoare triunghiulară (750 Hz)")
a1.plot(t * 1e3, ref, color=C1, label="referință sinusoidală (50 Hz, m$_a$ = 0,8)")
a1.set_ylabel("u relativ")
a1.set_ylim(-1.1, 1.75)
a1.legend(loc="upper center", fontsize=8.5, ncol=2)
a2.plot(t * 1e3, u, color=C2, lw=1.0, label="tensiunea de ieșire a unui braț (±U$_d$/2)")
a2.plot(t * 1e3, fund * np.sin(2 * np.pi * f1 * t), color=C1, label=f"fundamentala: amplitudine {fund:.0f} V".replace(".", ","))
a2.set_ylabel("u [V]")
a2.set_xlabel("t [ms]")
a2.set_ylim(-300, 500)
a2.legend(loc="upper center", fontsize=8.5, ncol=2)
a1.set_title("Modulația în lățime a impulsurilor (PWM sinus–triunghi)", fontsize=10)
for a in (a1, a2):
    virgula(a)
salveaza(fig, "f05-8-pwm")

# --- Ventilator: clapetă vs convertor de frecvență (problema 5.4) ------------------
q = np.linspace(0.3, 1.0, 100)
fig, ax = plt.subplots(figsize=(6.8, 3.9))
ax.plot(q, q**3 / 0.97, color=C1, label="convertor de frecvență: P ∝ n³ (η$_{conv}$ = 97 %)")
ax.plot([0.7], [0.80], "s", color=C2, ms=8, mec=FUNDAL, mew=2, label="clapetă la 70 % debit (dată a problemei)")
ax.plot([0.7], [0.7**3 / 0.97], "o", color=C1, ms=8, mec=FUNDAL, mew=2)
ax.annotate("", xy=(0.7, 0.7**3 / 0.97 + 0.02), xytext=(0.7, 0.78),
            arrowprops=dict(arrowstyle="<->", color=TEXT2, lw=1))
ax.text(0.715, 0.55, "economie ≈ 13,4 kW\n(din 30 kW nominali)", color=TEXT, fontsize=9)
ax.set_xlabel("debit relativ Q/Qₙ = n/nₙ")
ax.set_ylabel("P/Pₙ")
ax.set_title("Puterea absorbită de un ventilator la debit redus")
ax.legend(loc="upper left", fontsize=8.5)
virgula(ax)
salveaza(fig, "f05-9-ventilator")

# --- Schema de forță a pornirii directe ------------------------------------
class Cerc(elm.Element):
    """Cerc simplu (simbolul motorului trifazat)."""

    def __init__(self, r=0.95, **kw):
        super().__init__(**kw)
        self.segments.append(SegmentCircle((0, 0), r))



with schemdraw.Drawing(show=False) as d:
    xs = [0, 1.2, 2.4]
    for x, L in zip(xs, ("L1", "L2", "L3")):
        d.add(elm.Line().at((x, 10)).to((x, 9.4)))
        d.add(elm.Label().at((x, 10.25)).label(L))
        d.add(elm.Fuse().at((x, 9.4)).to((x, 8.0)))
        d.add(elm.Line().at((x, 8.0)).to((x, 7.6)))
        d.add(elm.Switch().at((x, 7.6)).to((x, 6.2)))
        d.add(elm.Line().at((x, 6.2)).to((x, 5.4)))
        d.add(elm.Switch().at((x, 5.4)).to((x, 4.0)))
        d.add(elm.Line().at((x, 4.0)).to((x, 3.6)))
        d.add(elm.Resistor().at((x, 3.6)).to((x, 2.2)))
    d.add(elm.Line().at((-0.1, 6.95)).to((2.6, 6.95)).linestyle("--").color(TEXT2))
    d.add(elm.Line().at((-0.1, 4.75)).to((2.6, 4.75)).linestyle("--").color(TEXT2))
    d.add(elm.Line().at((-0.1, 2.9)).to((2.6, 2.9)).linestyle("--").color(TEXT2))
    for y, t in ((8.7, "F1 – siguranțe fuzibile\n(protecție la scurtcircuit)"),
                 (6.9, "Q1 – separator / întrerupător"),
                 (4.7, "K1 – contactele principale\nale contactorului"),
                 (2.9, "F2 – releu termic\n(protecție la suprasarcină)")):
        d.add(elm.Label().at((3.2, y)).label(t, halign="left", fontsize=10))
    for x, b in zip(xs, ("U", "V", "W")):
        d.add(elm.Line().at((x, 2.2)).to((1.2 + (x - 1.2) * 0.35, 1.25)))
        d.add(elm.Label().at((x - 0.25, 1.85)).label(b, fontsize=10))
    d.add(Cerc().at((1.2, 0.3)))
    d.add(elm.Label().at((1.2, 0.3)).label("M\n3~"))
    d.save(str(FIGURI / "f05-10-schema-pornire-directa.svg"))
print("  figura f05-10-schema-pornire-directa.svg")
