"""Capitolul 0 – Noțiuni fundamentale: rezolvarea și verificarea problemelor."""

import numpy as np
from modele import SQRT3, fmt, verifica

MU0 = 4e-7 * np.pi

print("Problema 0.1 – tensiunea indusă într-o bobină")
f, N, Phi_max = 50.0, 500, 2e-3
E_formula = 4.44 * f * N * Phi_max
E_exact = np.pi * np.sqrt(2) * f * N * Phi_max
# Calea a doua: e(t) = -N dΦ/dt calculat numeric, apoi valoarea efectivă
t = np.linspace(0, 1 / f, 200001)
phi_t = Phi_max * np.sin(2 * np.pi * f * t)
e_t = -N * np.gradient(phi_t, t)
E_numeric = np.sqrt(np.mean(e_t[:-1] ** 2))
print(f"  E (4,44 f N Φmax) = {fmt(E_formula, 1)} V; E exact (π√2) = {fmt(E_exact, 2)} V;"
      f" E numeric = {fmt(E_numeric, 2)} V; e_max = {fmt(e_t.max(), 1)} V")
verifica("E formula vs numeric", E_exact, E_numeric, rtol=1e-4)

print("\nProblema 0.2 – circuit magnetic cu întrefier")
l_fe, A, N, B, mu_r, delta = 0.5, 10e-4, 200, 1.2, 2000, 1e-3
H_fe = B / (MU0 * mu_r)
H_d = B / MU0
Theta_1 = H_fe * l_fe + H_d * delta
Phi = B * A
R_fe = l_fe / (MU0 * mu_r * A)
R_d = delta / (MU0 * A)
Theta_2 = Phi * (R_fe + R_d)
I = Theta_1 / N
L = N * Phi / I
L2 = N**2 / (R_fe + R_d)
print(f"  H_fe = {fmt(H_fe, 1)} A/m, H_δ = {fmt(H_d, 0)} A/m")
print(f"  Θ_fe = {fmt(H_fe * l_fe, 1)} A, Θ_δ = {fmt(H_d * delta, 1)} A, Θ = {fmt(Theta_1, 1)} A")
print(f"  R_fe = {R_fe:.4e} A/Wb, R_δ = {R_d:.4e} A/Wb, Φ = {Phi * 1e3:.3f} mWb")
print(f"  I = {fmt(I, 2)} A, L = {fmt(L * 1e3, 1)} mH; ponderea întrefierului = {fmt(100 * H_d * delta / Theta_1, 1)} %")
verifica("Θ prin H·l vs prin reluctanțe", Theta_1, Theta_2)
verifica("L = NΦ/I vs N²/R", L, L2)

print("\nProblema 0.3 – curentul absorbit de un motor trifazat")
P2, U, eta, cos_phi = 11e3, 400.0, 0.90, 0.85
P1 = P2 / eta
I_a = P2 / (SQRT3 * U * eta * cos_phi)
S = P1 / cos_phi
I_b = S / (SQRT3 * U)
I_c = (P1 / 3) / ((U / SQRT3) * cos_phi)     # pe fază, conexiune stea
Q = np.sqrt(S**2 - P1**2)
print(f"  P1 = {fmt(P1, 0)} W, S = {fmt(S, 0)} VA, Q = {fmt(Q, 0)} var, I = {fmt(I_a, 2)} A")
verifica("I formula directă vs prin S", I_a, I_b)
verifica("I formula directă vs pe fază", I_a, I_c)

print("\nProblema 0.4 – aceeași sarcină în stea și în triunghi")
Z = 10 + 7.5j
U = 400.0
If_Y = (U / SQRT3) / abs(Z)
P_Y = 3 * If_Y**2 * Z.real
If_D = U / abs(Z)
IL_D = SQRT3 * If_D
P_D = 3 * If_D**2 * Z.real
P_D_b = SQRT3 * U * IL_D * Z.real / abs(Z)
print(f"  |Z| = {fmt(abs(Z), 1)} Ω, cos φ = {fmt(Z.real / abs(Z), 2)}")
print(f"  stea: If = IL = {fmt(If_Y, 2)} A, P = {fmt(P_Y, 0)} W")
print(f"  triunghi: If = {fmt(If_D, 2)} A, IL = {fmt(IL_D, 2)} A, P = {fmt(P_D, 0)} W")
print(f"  raport P_D/P_Y = {fmt(P_D / P_Y, 3)}, raport IL_D/IL_Y = {fmt(IL_D / If_Y, 3)}")
verifica("P triunghi pe fază vs √3·U·I·cosφ", P_D, P_D_b)
verifica("raport puteri = 3", P_D / P_Y, 3.0)

print("\nProblema 0.5 – viteze de sincronism la 50 Hz și 60 Hz")
for p in range(1, 7):
    print(f"  p = {p} (2p = {2 * p} poli): n1 = {60 * 50 / p:.0f} rot/min la 50 Hz, {60 * 60 / p:.0f} rot/min la 60 Hz")

print("\nProblema 0.6 – câmpul învârtitor (verificare numerică)")
# Trei bobine decalate la 120° în spațiu, parcurse de curenți decalați la 120° în timp.
Fm = 1.0
wt = np.linspace(0, 2 * np.pi, 721)
F = np.zeros_like(wt, dtype=complex)
for k in range(3):
    ax = np.exp(1j * 2 * np.pi * k / 3)              # direcția axei bobinei k
    F += Fm * np.cos(wt - 2 * np.pi * k / 3) * ax     # solenația pulsatorie a bobinei k
amp = np.abs(F)
unghi = np.unwrap(np.angle(F))
print(f"  amplitudinea rezultantei: min = {amp.min():.6f}, max = {amp.max():.6f} (teoretic 1,5·Fm)")
print(f"  unghiul rezultantei urmărește ωt: abatere maximă = {np.max(np.abs(unghi - wt)):.2e} rad")
verifica("amplitudine constantă = 1,5 Fm", amp.mean(), 1.5)
verifica("rotație sincronă cu ωt", np.max(np.abs(unghi - wt)), 0.0, atol=1e-9)
