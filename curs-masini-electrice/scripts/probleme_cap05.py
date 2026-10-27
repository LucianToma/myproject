"""Capitolul 5 – Acționări electrice: rezolvarea și verificarea problemelor."""

import numpy as np
from scipy.integrate import solve_ivp, quad
from scipy.optimize import brentq
from modele import G, fmt, verifica, kloss, sk_din_catalog, motor_M15

# Motorul M15 din capitolul 2 (date de catalog)
Pn, nn, lam, J_m = 15e3, 1466, 3.1, 0.10
Wn = 2 * np.pi * nn / 60
Mn = Pn / Wn
sn = (1500 - nn) / 1500
sk = sk_din_catalog(sn, lam)
Mmax = lam * Mn
W1 = 2 * np.pi * 1500 / 60

print("Problema 5.1 – troliu: raportarea cuplului, a puterii și a momentului de inerție la arborele motorului")
m, D, i, eta_t, J_tambur = 2000.0, 0.4, 60.0, 0.90, 5.0
W_t = Wn / i
v = W_t * D / 2
M_t = m * G * D / 2
M_r = M_t / (i * eta_t)                 # ridicare: puterea curge de la motor spre sarcină
M_r_cob = M_t * eta_t / i               # coborâre: puterea curge de la sarcină spre motor
P_r = M_r * Wn
P_r_b = m * G * v / eta_t
J_masa = m * (v / Wn) ** 2
J_t_raportat = J_tambur / i**2
J_tot = J_m + J_t_raportat + J_masa
print(f"  Ωm = {fmt(Wn, 2)} rad/s, Ωt = {fmt(W_t, 4)} rad/s, v = {fmt(v, 4)} m/s")
print(f"  cuplul la tambur = {fmt(M_t, 1)} N·m; raportat la motor: ridicare {fmt(M_r, 2)} N·m, coborâre {fmt(M_r_cob, 2)} N·m")
print(f"  puterea la ridicare = {fmt(P_r / 1e3, 3)} kW; Mn motor = {fmt(Mn, 2)} N·m → încărcare {fmt(100 * M_r / Mn, 1)} %")
print(f"  J: motor {fmt(J_m, 4)}, tambur raportat {fmt(J_t_raportat, 5)}, masa raportată {fmt(J_masa, 5)}, total {fmt(J_tot, 4)} kg·m²")
verifica("P = M·Ω vs m·g·v/η", P_r, P_r_b)
verifica("energia cinetică: ½J_masa Ω² = ½ m v²", 0.5 * J_masa * Wn**2, 0.5 * m * v**2)
# Timpul de accelerare la ridicare cu cuplu motor constant 1,5·Mn (convertor cu limitare de curent)
M_acc = 1.5 * Mn
t_a = J_tot * Wn / (M_acc - M_r)
sol = solve_ivp(lambda t, w: [(M_acc - M_r) / J_tot], (0, 2), [0.0], dense_output=True, max_step=1e-3,
                events=lambda t, w: w[0] - Wn)
print(f"  accelerare cu M = 1,5·Mn = {fmt(M_acc, 1)} N·m: t = {fmt(t_a, 4)} s (analitic), {fmt(sol.t_events[0][0], 4)} s (numeric)")
verifica("timp de accelerare analitic vs numeric", t_a, sol.t_events[0][0], rtol=1e-4)

print("\nProblema 5.2 – accelerarea unui ventilator (Mr = k·Ω²) cu cuplu motor constant")
J = 0.10 + 0.90       # motor + rotorul ventilatorului
M = 1.2 * Mn
Mr_n = 0.8 * Mn       # cuplul ventilatorului la viteza Ωn
k = Mr_n / Wn**2
# Soluția analitică: t = J/√(Mk) · artanh(Ω √(k/M))
t_an = J / np.sqrt(M * k) * np.arctanh(Wn * np.sqrt(k / M))
t_quad, _ = quad(lambda w: J / (M - k * w**2), 0, Wn)
sol = solve_ivp(lambda t, w: [(M - k * w[0] ** 2) / J], (0, 10), [0.0], max_step=1e-3,
                events=lambda t, w: w[0] - Wn, rtol=1e-9, atol=1e-9)
t_num = sol.t_events[0][0]
t_cst = J * Wn / (M - Mr_n)
print(f"  k = {k:.5f} N·m·s², M = {fmt(M, 2)} N·m, Mr(Ωn) = {fmt(Mr_n, 2)} N·m")
print(f"  t analitic = {fmt(t_an, 4)} s; prin cuadratură = {fmt(t_quad, 4)} s; prin integrare în timp = {fmt(t_num, 4)} s")
print(f"  (dacă s-ar presupune Mr constant = Mr(Ωn): t = {fmt(t_cst, 3)} s – supraestimare)")
verifica("t analitic vs cuadratură", t_an, t_quad, rtol=1e-6)
verifica("t analitic vs integrare ODE", t_an, t_num, rtol=1e-4)

print("\nProblema 5.3 – alegerea motorului pentru un ciclu de sarcină (metoda cuplului echivalent)")
Mi = np.array([120.0, 60.0, 20.0])
ti = np.array([10.0, 30.0, 20.0])
M_ech = np.sqrt(np.sum(Mi**2 * ti) / ti.sum())
M_med = np.sum(Mi * ti) / ti.sum()
print(f"  M_ech = {fmt(M_ech, 2)} N·m; media aritmetică (greșit pentru încălzire) = {fmt(M_med, 2)} N·m")
Mn11 = 11e3 / (2 * np.pi * 1460 / 60)
print(f"  motor 11 kW, 1460 rot/min: Mn = {fmt(Mn11, 2)} N·m ≥ M_ech → acceptat termic;")
print(f"  verificarea la suprasarcină: Mmax cerut ≥ {fmt(120 / 0.9**2, 1)} N·m (cu U = 0,9·Un); motorul are ≈ {fmt(2.8 * Mn11, 0)} N·m (λ = 2,8)")
# Calea a doua: model termic de ordinul 1. Pierderi = Pc + Pv,n (M/Mn)^2, τ = 20 min
Pc, Pvn, Rth, tau = 350.0, 700.0, 0.08, 1200.0       # W, W, K/W, s
pierderi = lambda Mx: Pc + Pvn * (Mx / Mn11) ** 2
T_ciclu = ti.sum()
t_grid, dt = [], 0.05
Pl = np.concatenate([np.full(int(t / dt), pierderi(Mx)) for Mx, t in zip(Mi, ti)])
theta, istoric = 0.0, []
for _ in range(150):                   # 150 cicluri ≈ 2,5 h ≫ τ → regim periodic stabilizat
    for P in Pl:
        theta += dt * (P * Rth - theta) / tau
    istoric.append(theta)
th_ciclu = []
for P in Pl:
    theta += dt * (P * Rth - theta) / tau
    th_ciclu.append(theta)
th_mediu = np.mean(th_ciclu)
th_ech = pierderi(M_ech) * Rth
print(f"  model termic: supratemperatura medie în regim periodic = {fmt(th_mediu, 2)} K (oscilație {fmt(max(th_ciclu) - min(th_ciclu), 2)} K);"
      f" cu M_ech constant = {fmt(th_ech, 2)} K; cu M_med constant = {fmt(pierderi(M_med) * Rth, 2)} K")
verifica("încălzire ciclu vs M_ech constant", th_mediu, th_ech, rtol=5e-3)

print("\nProblema 5.4 – ventilator: reglaj prin clapetă vs convertor de frecvență")
P_n_vent = 30.0      # kW la debit nominal
q = 0.7              # debit relativ
P_clapeta = 0.80 * P_n_vent       # dată a problemei (citită de pe caracteristica ventilatorului)
eta_conv = 0.97
P_vsd = P_n_vent * q**3 / eta_conv
# Calea a doua: legile de similitudine aplicate separat (Q ∝ n, H ∝ n², P = Q·H/η)
Q_r, H_r = q, q**2
P_vsd_b = P_n_vent * Q_r * H_r / eta_conv
ore = 6000
print(f"  clapetă: {fmt(P_clapeta, 2)} kW; convertor: {fmt(P_vsd, 2)} kW; economie = {fmt(P_clapeta - P_vsd, 2)} kW"
      f" → {fmt((P_clapeta - P_vsd) * ore, 0)} kWh/an la {ore} h/an")
verifica("P ∝ n³ vs Q·H", P_vsd, P_vsd_b)

print("\nProblema 5.5 – stabilitatea punctelor de funcționare (Kloss, Mr = constant)")
Mr = 2.0 * Mn
s_a = brentq(lambda s: kloss(s, Mmax, sk) - Mr, 1e-6, sk)
s_b = brentq(lambda s: kloss(s, Mmax, sk) - Mr, sk, 1.0)
# Soluția analitică a ecuației lui Kloss: s = sk (λ' ± √(λ'² - 1)), λ' = Mmax/Mr
lp = Mmax / Mr
s_a2, s_b2 = sk * (lp - np.sqrt(lp**2 - 1)), sk * (lp + np.sqrt(lp**2 - 1))
for nume, s in (("A", s_a), ("B", s_b)):
    h = 1e-6
    dM_ds = (kloss(s + h, Mmax, sk) - kloss(s - h, Mmax, sk)) / (2 * h)
    dM_dW = -dM_ds / W1          # Ω = (1 - s) Ω1  →  dΩ = -Ω1 ds
    stabil = dM_dW < 0           # dMr/dΩ = 0 pentru cuplu rezistent constant
    print(f"  punctul {nume}: s = {fmt(s, 4)}, n = {fmt(1500 * (1 - s), 1)} rot/min, dM/dΩ = {fmt(dM_dW, 2)} N·m·s → {'STABIL' if stabil else 'INSTABIL'}")
verifica("s_A numeric vs analitic", s_a, s_a2, rtol=1e-8)
verifica("s_B numeric vs analitic", s_b, s_b2, rtol=1e-8)

print("\nProblema 5.6 – punctul de funcționare al ventilatorului pe caracteristica motorului M15")
k_v = 0.9 * Mn / Wn**2            # ventilatorul cere 0,9·Mn la viteza nominală
s_v = brentq(lambda s: kloss(s, Mmax, sk) - k_v * ((1 - s) * W1) ** 2, 1e-6, sk)
n_v = 1500 * (1 - s_v)
M_v = kloss(s_v, Mmax, sk)
# Calea a doua: aproximarea liniară a caracteristicii în zona stabilă (M ≈ Mn·s/sn), ecuație de gradul 2
#   Mn (s/sn) = k_v W1² (1 - s)²
a, b, c = k_v * W1**2, -(2 * k_v * W1**2 + Mn / sn), k_v * W1**2
s_lin = (-b - np.sqrt(b**2 - 4 * a * c)) / (2 * a)
print(f"  Kloss: s = {fmt(s_v, 5)}, n = {fmt(n_v, 1)} rot/min, M = {fmt(M_v, 2)} N·m, P = {fmt(M_v * (1 - s_v) * W1 / 1e3, 2)} kW")
print(f"  aproximare liniară: s = {fmt(s_lin, 5)}, n = {fmt(1500 * (1 - s_lin), 1)} rot/min")
verifica("viteza: Kloss vs liniar", n_v, 1500 * (1 - s_lin), rtol=1e-3)

print("\nProblema 5.7 – energia pierdută în rotor la pornirea directă în gol")
MD = motor_M15(colivie_dubla=True)
J0 = 0.10
W_teoretic = 0.5 * J0 * MD.W1**2
# Integrare numerică: dΩ/dt = Me/J (fără sarcină), dW/dt = PCu2 = s·Pδ


def deriv(t, y):
    s = max(1 - y[0] / MD.W1, 1e-6)
    p = MD.punct(s)
    return [p["Me"] / J0, p["PCu2"]]


ev = lambda t, y: (1 - y[0] / MD.W1) - 1e-3
ev.terminal = True
sol = solve_ivp(deriv, (0, 5), [0.0, 0.0], events=ev, max_step=1e-3, rtol=1e-8, atol=1e-8)
W_num = sol.y[1, -1]
s_fin = 1 - sol.y[0, -1] / MD.W1
print(f"  ½·J·Ω1² = {fmt(W_teoretic, 1)} J; integrare numerică (până la s = {s_fin:.4f}): {fmt(W_num, 1)} J;"
      f" durata pornirii ≈ {fmt(sol.t[-1], 3)} s")
verifica("energia în rotor: ½JΩ1² vs integrare", W_teoretic * (1 - s_fin**2), W_num, rtol=5e-3)
