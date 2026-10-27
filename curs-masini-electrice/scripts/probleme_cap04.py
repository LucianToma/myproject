"""Capitolul 4 – Motorul sincron: rezolvarea și verificarea problemelor.

Motorul de referință MS1000: 1000 kW (putere utilă), 6 kV, Y, 50 Hz, 2p = 8,
η = 96 %, cos φ = 0,9 capacitiv (supraexcitat), Xs = 36 Ω pe fază, R neglijat.
"""

import numpy as np
from scipy.optimize import brentq
from modele import SQRT3, fmt, verifica, polar, motor_E0

Un, P2n, eta, cos_n, Xs, p, f = 6000.0, 1000e3, 0.96, 0.9, 36.0, 4, 50.0
Uf = Un / SQRT3
P1 = P2n / eta
In = P1 / (SQRT3 * Un * cos_n)
n1 = 60 * f / p
W1 = 2 * np.pi * n1 / 60
Mn = P2n / W1

print("Problema 4.1 – punctul nominal (supraexcitat, cos φ = 0,9 capacitiv)")
phi = np.arccos(cos_n)
E0, Iz = motor_E0(Uf, In, phi, Xs)
delta = np.angle(E0)
P_b = 3 * Uf * abs(E0) * np.sin(-delta) / Xs
print(f"  P1 = {fmt(P1 / 1e3, 1)} kW, In = {fmt(In, 2)} A, n1 = {fmt(n1, 0)} rot/min, Mn = {fmt(Mn, 0)} N·m")
print(f"  I = {polar(Iz, 2)} A, jXs·I = {fmt((1j * Xs * Iz).real, 1)} + j{fmt((1j * Xs * Iz).imag, 1)} V")
print(f"  E0 = {fmt(E0.real, 1)} {fmt(E0.imag, 1)}j V = {polar(E0, 2)} V (fază) → {fmt(abs(E0) * SQRT3, 0)} V (linie)")
print(f"  P din E0, δ = {fmt(P_b / 1e3, 1)} kW")
verifica("P1 din U,I vs din E0,δ", P1, P_b)
Q = -3 * Uf * In * np.sin(phi)   # convenția de receptor: Q < 0 înseamnă că motorul livrează Q inductiv
Q_b = 3 * (Uf**2 - Uf * abs(E0) * np.cos(delta)) / Xs
print(f"  Q absorbit = {fmt(Q / 1e3, 1)} kvar (negativ → motorul furnizează {fmt(-Q / 1e3, 1)} kvar rețelei)")
verifica("Q din U,I vs din E0,δ", Q, Q_b)
Pmax = 3 * Uf * abs(E0) / Xs
print(f"  P1max = {fmt(Pmax / 1e3, 0)} kW → Mmax ≈ {fmt(Pmax / W1, 0)} N·m (pierderile neglijate) = {fmt(Pmax / P1, 2)}·M la sarcină nominală")

print("\nProblema 4.2 – excitația pentru cos φ = 1 și curbele în V")
I_u = P1 / (3 * Uf)
E_u = abs(Uf - 1j * Xs * I_u)
print(f"  cos φ = 1: I = {fmt(I_u, 2)} A, E0 = {fmt(E_u, 1)} V, δ = {fmt(np.degrees(np.angle(Uf - 1j * Xs * I_u)), 2)}°")
verifica("E0 la cos φ=1 fazorial vs Pitagora", E_u, np.hypot(Uf, Xs * I_u))


def curent_la(P, E0f):
    """Curentul absorbit la putere P și tensiune electromotoare E0 dată (U = ct)."""
    d = np.arcsin(P * Xs / (3 * Uf * E0f))
    E = E0f * np.exp(-1j * d)
    I = (Uf - E) / (1j * Xs)
    return I, np.degrees(d)


for E0f in (4000.0, E_u, 5500.0, abs(E0), 7000.0):
    I, d = curent_la(P1, E0f)
    S = 3 * Uf * np.conj(I)
    print(f"  P1 = {fmt(P1 / 1e3, 1)} kW, E0 = {fmt(E0f, 0)} V: |I| = {fmt(abs(I), 1)} A, cos φ = {fmt(S.real / abs(S), 3)}"
          f" {'(inductiv)' if S.imag > 1 else '(capacitiv)' if S.imag < -1 else ''}, δ = {fmt(d, 2)}°")
    verifica("P păstrată", S.real, P1)

print("\nProblema 4.3 – îmbunătățirea factorului de putere al unei fabrici")
P_f, cos_f = 2000e3, 0.7
Q_f = P_f * np.tan(np.arccos(cos_f))
Q_sm = -3 * Uf * In * np.sin(phi)          # motorul supraexcitat: Q negativ (furnizat)
P_t = P_f + P1
Q_t = Q_f + Q_sm
cos_t = P_t / np.hypot(P_t, Q_t)
# Calea a doua: suma fazorială a curenților la 6 kV
I_f = P_f / (SQRT3 * Un * cos_f) * np.exp(-1j * np.arccos(cos_f))
I_sm = In * np.exp(1j * phi)
I_t = I_f + I_sm
print(f"  fabrica: Q = {fmt(Q_f / 1e3, 1)} kvar; motorul: Q = {fmt(Q_sm / 1e3, 1)} kvar")
print(f"  total: P = {fmt(P_t / 1e3, 1)} kW, Q = {fmt(Q_t / 1e3, 1)} kvar, cos φ = {fmt(cos_t, 4)}")
print(f"  curenți: fabrica {fmt(abs(I_f), 1)} A, motor {fmt(abs(I_sm), 1)} A, total {fmt(abs(I_t), 1)} A (suma aritmetică ar fi {fmt(abs(I_f) + abs(I_sm), 1)} A)")
verifica("cos φ total prin puteri vs prin fazori", cos_t, np.cos(np.angle(I_t)))
# Ce Q ar trebui pentru cos φ = 0,95?
Q_tinta = P_t * np.tan(np.arccos(0.95))
Q_nec = Q_f - Q_tinta
I_nec = np.hypot(P1, Q_nec) / (SQRT3 * Un)
print(f"  pentru cos φ = 0,95: Q total admis = {fmt(Q_tinta / 1e3, 1)} kvar → motorul ar trebui să dea {fmt(Q_nec / 1e3, 1)} kvar")
print(f"  curentul motorului ar fi {fmt(I_nec, 1)} A > In = {fmt(In, 1)} A → nu este admisibil în regim permanent")
I_n_chk, _ = curent_la(P1, abs(motor_E0(Uf, I_nec, np.arctan(Q_nec / P1), Xs)[0]))
verifica("curentul recalculat din E0 necesar", abs(I_n_chk), I_nec)

print("\nProblema 4.4 – scăderea tensiunii rețelei cu 20 % (excitație neschimbată)")
U2 = 0.8 * Uf
Pmax2 = 3 * U2 * abs(E0) / Xs
d2 = np.degrees(np.arcsin(P1 / Pmax2))
print(f"  Pmax = {fmt(Pmax2 / 1e3, 0)} kW (era {fmt(Pmax / 1e3, 0)} kW), δ = {fmt(d2, 2)}° (era {fmt(np.degrees(-delta), 2)}°) → rămâne stabil")
verifica("Pmax ∝ U", Pmax2 / Pmax, 0.8)

print("\nProblema 4.5 – motor sincron cu magneți permanenți alimentat de la convertor")
p_pm = 4
for f_pm in (50, 200, 800):
    print(f"  2p = 8, f = {f_pm} Hz → n = {fmt(60 * f_pm / p_pm, 0)} rot/min")
n_dorit = 12000
print(f"  pentru {n_dorit} rot/min este necesară f = {fmt(n_dorit * p_pm / 60, 0)} Hz")
