"""Capitolul 3 – Generatorul sincron: rezolvarea și verificarea problemelor."""

import numpy as np
from scipy.optimize import brentq
from modele import SQRT3, fmt, verifica, polar, generator_E0

print("Problema 3.1 – numărul de poli")
for nume, n, f in (("turbogenerator", 3000, 50), ("hidrogenerator", 125, 50), ("hidrogenerator", 150, 60),
                   ("generator diesel", 1500, 50)):
    p = 60 * f / n
    print(f"  {nume}: n = {n} rot/min, f = {f} Hz → p = {fmt(p, 0)} perechi, 2p = {fmt(2 * p, 0)} poli")
    verifica("f = p n / 60", p * n / 60, f)

print("\nProblema 3.2 – reactanța sincronă din încercările de gol și scurtcircuit")
Sn, Un, cos_n = 10e6, 6300.0, 0.8
In = Sn / (SQRT3 * Un)
Uf = Un / SQRT3
Zb = Un**2 / Sn
# Încercări: la Ie = 200 A, U0 = 6300 V (de linie) în gol; Isc = 830 A în scurtcircuit
Ie0, U0_linie, Isc = 200.0, 6300.0, 830.0
Xs = (U0_linie / SQRT3) / Isc
xs = Xs / Zb
# Ie la care Isc = In (din caracteristica de scurtcircuit, liniară)
Ie_sc_n = Ie0 * In / Isc
SCR = Ie0 / Ie_sc_n
print(f"  In = {fmt(In, 1)} A, Uf = {fmt(Uf, 1)} V, Zb = {fmt(Zb, 3)} Ω")
print(f"  Xs = {fmt(Xs, 3)} Ω = {fmt(xs, 3)} u.r.; Ie pentru Isc = In: {fmt(Ie_sc_n, 1)} A; SCR = {fmt(SCR, 3)}")
verifica("SCR = 1/xs", SCR, 1 / xs)

print("\nProblema 3.3 – funcționare la sarcină nominală, cos φ = 0,8 inductiv (R neglijat)")
phi = np.arccos(cos_n)
E0, Iz = generator_E0(Uf, In, phi, Xs)
delta = np.angle(E0)
P_1 = 3 * Uf * In * cos_n
P_2 = 3 * Uf * abs(E0) * np.sin(delta) / Xs
Q_1 = 3 * Uf * In * np.sin(phi)
Q_2 = 3 * (Uf * abs(E0) * np.cos(delta) - Uf**2) / Xs
print(f"  I = {polar(Iz, 2)} A; jXs·I = {polar(1j * Xs * Iz, 1)} V = {fmt((1j * Xs * Iz).real, 1)} + j{fmt((1j * Xs * Iz).imag, 1)} V")
print(f"  E0 = {fmt(E0.real, 1)} + j{fmt(E0.imag, 1)} V = {polar(E0, 2)} V (fază) → {fmt(abs(E0) * SQRT3, 0)} V (linie), δ = {fmt(np.degrees(delta), 2)}°")
print(f"  P = {fmt(P_1 / 1e6, 4)} MW (din U, I) = {fmt(P_2 / 1e6, 4)} MW (din E0, δ)")
print(f"  Q = {fmt(Q_1 / 1e6, 4)} Mvar (din U, I) = {fmt(Q_2 / 1e6, 4)} Mvar (din E0, δ)")
verifica("P din U,I vs din E0,δ", P_1, P_2)
verifica("Q din U,I vs din E0,δ", Q_1, Q_2)
Pmax = 3 * Uf * abs(E0) / Xs
print(f"  Pmax = {fmt(Pmax / 1e6, 2)} MW; rezerva de stabilitate statică = {fmt(Pmax / P_1, 2)}·Pn")
Ie_n = Ie0 * abs(E0) / Uf
print(f"  curentul de excitație necesar (caracteristică liniară) ≈ {fmt(Ie_n, 0)} A")
print(f"  la deconectarea bruscă a sarcinii (Ie neschimbat): U → E0, creștere de {fmt(100 * (abs(E0) / Uf - 1), 1)} %")
# Comparație cu sarcina rezistivă și capacitivă la același curent
for nume, ph in (("cos φ = 1", 0.0), ("cos φ = 0,8 capacitiv", -phi)):
    E, _ = generator_E0(Uf, In, ph, Xs)
    print(f"  {nume}: E0 = {fmt(abs(E), 0)} V (fază), δ = {fmt(np.degrees(np.angle(E)), 2)}°")

print("\nProblema 3.4 – generator conectat la rețea (U = ct), P = 8 MW, se modifică excitația")
P = 8e6
# Excitația pentru cos φ = 1 la P = 8 MW
I1 = P / (3 * Uf)
E_u = abs(Uf + 1j * Xs * I1)
E_u2 = np.sqrt(Uf**2 + (Xs * I1) ** 2)
print(f"  pentru cos φ = 1: I = {fmt(I1, 1)} A, E0 = {fmt(E_u, 1)} V")
verifica("E0 la cosφ=1 fazorial vs Pitagora", E_u, E_u2)
for E0_f in (4000.0, E_u, abs(E0), 8000.0):
    d = np.arcsin(P * Xs / (3 * Uf * E0_f))
    E = E0_f * np.exp(1j * d)
    I = (E - Uf) / (1j * Xs)
    S = 3 * Uf * np.conj(I)
    Q_b = 3 * (Uf * E0_f * np.cos(d) - Uf**2) / Xs
    regim = ("supraexcitat (livrează Q)" if S.imag > 1e3 else
             "subexcitat (absoarbe Q)" if S.imag < -1e3 else "excitație normală (Q = 0)")
    print(f"  E0 = {fmt(E0_f, 0)} V: δ = {fmt(np.degrees(d), 2)}°, I = {fmt(abs(I), 1)} A, cos φ = {fmt(S.real / abs(S), 3)},"
          f" Q = {fmt(S.imag / 1e6, 3)} Mvar → {regim}")
    verifica("P păstrat", S.real, P)
    verifica("Q din curent vs din E0,δ", S.imag, Q_b, atol=1.0)
# Limita de stabilitate la P = 8 MW: E0 minim pentru δ = 90°
E_min = P * Xs / (3 * Uf)
print(f"  excitația minimă (δ = 90°): E0 = {fmt(E_min, 1)} V")

print("\nProblema 3.5 – împărțirea sarcinii între două generatoare cu statism")
f_n = 50.0
P1n, s1 = 100.0, 0.04
P2n, s2 = 50.0, 0.05
dP = 12.0
K1 = P1n / (s1 * f_n)
K2 = P2n / (s2 * f_n)
df = dP / (K1 + K2)
dP1, dP2 = K1 * df, K2 * df
print(f"  K1 = {fmt(K1, 1)} MW/Hz, K2 = {fmt(K2, 1)} MW/Hz, Δf = {fmt(-df, 4)} Hz → f = {fmt(f_n - df, 4)} Hz")
print(f"  ΔP1 = {fmt(dP1, 3)} MW, ΔP2 = {fmt(dP2, 3)} MW")
# Calea a doua: sistem liniar cu necunoscutele (ΔP1, ΔP2, Δf)
A = np.array([[1, 1, 0], [1, 0, K1], [0, 1, K2]], dtype=float)
b = np.array([dP, 0, 0])
x = np.linalg.solve(A, b)
verifica("ΔP1 formulă vs sistem liniar", dP1, x[0])
verifica("ΔP2 formulă vs sistem liniar", dP2, x[1])
verifica("Δf formulă vs sistem liniar", -df, x[2])
