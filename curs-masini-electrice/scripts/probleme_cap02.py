"""Capitolul 2 – Mașina asincronă: rezolvarea și verificarea problemelor.

Motorul de referință M15 (folosit și în capitolul 5):
  15 kW, 400 V Δ, 50 Hz, 2p = 4; parametrii stelei echivalente:
  R1 = 0,25 Ω, X1σ = 0,60 Ω, R2' = 0,20 Ω, X2σ' = 0,75 Ω, Xm = 19 Ω, P0 = 330 W.
"""

import numpy as np
from scipy.optimize import brentq
from modele import SQRT3, fmt, verifica, polar, motor_M15, kloss, sk_din_catalog

M15 = motor_M15()
M15_CD = motor_M15(colivie_dubla=True)

print("Problema 2.1 – alunecare, frecvența rotorică")
n1 = M15.n1
for n in (1466, 0, 1530):
    s = (n1 - n) / n1
    print(f"  n = {n} rot/min: s = {fmt(s, 5)} ({fmt(100 * s, 2)} %), f2 = |s|·f1 = {fmt(abs(s) * 50, 3)} Hz,"
          f" viteza câmpului față de rotor = {fmt(n1 - n, 0)} rot/min")

print("\nProblema 2.2 – motorul M15 la n = 1466 rot/min, din schema echivalentă")
s = (1500 - 1466) / 1500
r = M15.punct(s)
Z2 = M15.R2 / s + 1j * M15.X2
Zm = 1j * M15.Xm
Zp = Z2 * Zm / (Z2 + Zm)
print(f"  s = {s:.6f}; R2'/s = {fmt(M15.R2 / s, 4)} Ω")
print(f"  Z2' = {fmt(Z2.real, 4)} + j{fmt(Z2.imag, 2)} Ω; Z_paralel = {fmt(Zp.real, 4)} + j{fmt(Zp.imag, 4)} Ω")
print(f"  Z = {fmt(r['Z'].real, 4)} + j{fmt(r['Z'].imag, 4)} Ω = {polar(r['Z'], 3)} Ω")
print(f"  U = {fmt(M15.U, 2)} V; I1 = {polar(r['I1'], 3)} A; cos φ = {fmt(r['cos_phi'], 4)}")
print(f"  E = {polar(r['E'], 2)} V; I2' = {polar(r['I2'], 2)} A; Iμ = {fmt(abs(r['E']) / M15.Xm, 2)} A")
print(f"  curentul de linie (motor în Δ alimentat la 400 V) = {fmt(abs(r['I1']), 2)} A;"
      f" curentul prin fiecare fază a triunghiului = {fmt(abs(r['I1']) / SQRT3, 2)} A")
print(f"  P1 = {fmt(r['P1'], 1)} W, Q1 = {fmt(r['Q1'], 1)} var")
print(f"  PCu1 = {fmt(r['PCu1'], 1)} W, Pδ = {fmt(r['Pd'], 1)} W, PCu2 = {fmt(r['PCu2'], 1)} W,"
      f" Pmi = {fmt(r['Pmi'], 1)} W, P0 = {fmt(M15.P0, 0)} W, P2 = {fmt(r['P2'], 1)} W")
print(f"  Ω1 = {fmt(M15.W1, 3)} rad/s, Ω = {fmt(r['W'], 3)} rad/s; Me = {fmt(r['Me'], 2)} N·m, M2 = {fmt(r['M2'], 2)} N·m")
print(f"  η = {fmt(100 * r['eta'], 2)} %")
# Verificări: bilanț de puteri; cuplul pe două căi; puterea activă pe fază
verifica("bilanț P1 = P2 + ΣP", r['P1'], r['P2'] + r['PCu1'] + r['PCu2'] + M15.P0, rtol=1e-9)
verifica("Me = Pδ/Ω1 vs Pmi/Ω", r['Me'], r['Pmi'] / r['W'], rtol=1e-9)
verifica("P1 = 3 U I cosφ vs 3 Re(U I*)", r['P1'], 3 * M15.U * abs(r['I1']) * r['cos_phi'], rtol=1e-9)
verifica("PCu2 = s·Pδ vs 3 I2'^2 R2'", r['PCu2'], 3 * abs(r['I2'])**2 * M15.R2, rtol=1e-9)
verifica("P1 = PCu1 + Pδ", r['P1'], r['PCu1'] + r['Pd'], rtol=1e-9)

sk_m, Mmax_m = M15.cuplu_maxim()
st = M15.punct(1.0)
print(f"  model: sk = {fmt(sk_m, 4)}, Mmax = {fmt(Mmax_m, 1)} N·m ({fmt(Mmax_m / r['M2'], 2)}·M2),"
      f" Mp = {fmt(st['Me'], 1)} N·m ({fmt(st['Me'] / r['M2'], 2)}·M2), Ip = {fmt(abs(st['I1']), 1)} A ({fmt(abs(st['I1']) / abs(r['I1']), 2)}·I)")
# Formula analitică a cuplului maxim pe schema simplificată (Γ) – a doua cale, aproximativă
R1, X1, R2, X2, Xm = M15.R1, M15.X1, M15.R2, M15.X2, M15.Xm
# Echivalentul Thévenin al rețelei văzute de rotor (calea exactă pentru Mmax)
Vth = M15.U * (1j * Xm) / (R1 + 1j * (X1 + Xm))
Zth = (1j * Xm) * (R1 + 1j * X1) / (R1 + 1j * (X1 + Xm))
sk_th = R2 / np.hypot(Zth.real, Zth.imag + X2)
Mmax_th = 3 * abs(Vth) ** 2 / (2 * M15.W1 * (Zth.real + np.hypot(Zth.real, Zth.imag + X2)))
print(f"  Thévenin: Vth = {fmt(abs(Vth), 2)} V, Zth = {fmt(Zth.real, 4)} + j{fmt(Zth.imag, 4)} Ω,"
      f" sk = {fmt(sk_th, 4)}, Mmax = {fmt(Mmax_th, 1)} N·m")
verifica("sk numeric vs Thévenin", sk_m, sk_th, rtol=1e-4)
verifica("Mmax numeric vs Thévenin", Mmax_m, Mmax_th, rtol=1e-6)
# Schema simplificată Γ (ramura de magnetizare la borne)
sk_G = R2 / np.hypot(R1, X1 + X2)
Mmax_G = 3 * M15.U**2 / (2 * M15.W1 * (R1 + np.hypot(R1, X1 + X2)))
print(f"  schema Γ (aproximativă): sk = {fmt(sk_G, 4)}, Mmax = {fmt(Mmax_G, 1)} N·m"
      f" (abatere {fmt(100 * (Mmax_G / Mmax_m - 1), 1)} %)")

print("\nProblema 2.3 – formula lui Kloss din datele de catalog")
Pn, nn, lam, mp_cat, ip_cat = 15e3, 1466, 3.1, 2.3, 6.8
sn = (1500 - nn) / 1500
Mn = Pn / (2 * np.pi * nn / 60)
sk = sk_din_catalog(sn, lam)
Mmax = lam * Mn
print(f"  sn = {fmt(sn, 5)}, Mn = {fmt(Mn, 2)} N·m, Mmax = {fmt(Mmax, 1)} N·m, sk = {fmt(sk, 4)}")
verifica("Kloss(sn) = Mn", kloss(sn, Mmax, sk), Mn, rtol=1e-9)
# (a) cuplul la s = 0,04 – Kloss vs schema echivalentă
s_a = 0.04
M_kloss = kloss(s_a, Mmax, sk)
# Kloss este calibrat pe cuplul util din catalog, deci se compară cu cuplul util M2 al modelului
M_model = M15.punct(s_a)["M2"]
print(f"  (a) s = 0,04 (n = {fmt(1500 * (1 - s_a), 0)} rot/min): Kloss = {fmt(M_kloss, 1)} N·m,"
      f" schema echivalentă: M2 = {fmt(M_model, 1)} N·m (Me = {fmt(M15.cuplu(s_a), 1)} N·m)")
verifica("Kloss vs schema echivalentă (M2) la s=0,04", M_kloss, M_model, rtol=0.03)
# (b) viteza la Mr = 0,5 Mn: din Kloss rezolvat analitic vs numeric
m = 0.5 * Mn / Mmax
s_b = sk * (1 / m - np.sqrt(1 / m**2 - 1))
s_b_num = brentq(lambda x: kloss(x, Mmax, sk) - 0.5 * Mn, 1e-6, sk)
print(f"  (b) Mr = 0,5·Mn = {fmt(0.5 * Mn, 2)} N·m: s = {fmt(s_b, 5)}, n = {fmt(1500 * (1 - s_b), 1)} rot/min")
verifica("s analitic vs numeric (Kloss inversat)", s_b, s_b_num, rtol=1e-8)
print(f"  aproximarea liniară s ≈ sn·M/Mn = {fmt(sn * 0.5, 5)}")
# (c) cuplul de pornire prezis de Kloss vs catalog
Mp_kloss = kloss(1.0, Mmax, sk)
print(f"  (c) Kloss la s = 1: Mp = {fmt(Mp_kloss, 1)} N·m = {fmt(Mp_kloss / Mn, 2)}·Mn; catalog: {fmt(mp_cat, 1)}·Mn = {fmt(mp_cat * Mn, 1)} N·m")
st_cd = M15_CD.punct(1.0)
sk_cd, Mmax_cd = M15_CD.cuplu_maxim()
s_cd = brentq(lambda x: M15_CD.punct(x)["P2"] - Pn, 1e-4, 0.2)
print(f"      modelul cu colivie dublă: Mp = {fmt(st_cd['Me'], 1)} N·m = {fmt(st_cd['Me'] / Mn, 2)}·Mn,"
      f" Ip = {fmt(abs(st_cd['I1']), 1)} A = {fmt(abs(st_cd['I1']) / 27.6, 2)}·In,"
      f" Mmax = {fmt(Mmax_cd, 1)} N·m = {fmt(Mmax_cd / Mn, 2)}·Mn, n la 15 kW = {fmt(1500 * (1 - s_cd), 1)} rot/min")
verifica("colivie dublă: Mp vs catalog", st_cd["Me"], mp_cat * Mn, rtol=0.02)
verifica("colivie dublă: Mmax vs catalog", Mmax_cd, lam * Mn, rtol=0.02)

print("\nProblema 2.4 – pornirea stea-triunghi a motorului M15")
In_cat = 27.6
Ip_D = ip_cat * In_cat
Mp_D = mp_cat * Mn
Ip_Y = Ip_D / 3
Mp_Y = Mp_D / 3
# Calea a doua: pe impedanța de fază a triunghiului la pornire, Zf (aceeași în ambele conexiuni)
Zf = 400 / (Ip_D / SQRT3)            # din curentul de linie la pornirea în Δ
Ip_Y_b = (400 / SQRT3) / Zf
Mp_Y_b = Mp_D * (1 / SQRT3) ** 2     # cuplul ∝ (tensiunea pe fază)²
print(f"  Δ: Ip = {fmt(Ip_D, 1)} A, Mp = {fmt(Mp_D, 1)} N·m; Y: Ip = {fmt(Ip_Y, 1)} A, Mp = {fmt(Mp_Y, 1)} N·m = {fmt(Mp_Y / Mn, 2)}·Mn")
print(f"  impedanța de fază la pornire Zf = {fmt(Zf, 2)} Ω")
verifica("Ip_Y prin 1/3 vs prin impedanță", Ip_Y, Ip_Y_b)
verifica("Mp_Y prin 1/3 vs prin (U/√3)²", Mp_Y, Mp_Y_b)
for nume, Mr0 in (("ventilator (Mr0 ≈ 0,1·Mn)", 0.1 * Mn), ("transportor (Mr ≈ Mn)", Mn)):
    print(f"  {nume}: Mr la pornire = {fmt(Mr0, 1)} N·m → {'pornește în Y' if Mp_Y > Mr0 else 'NU pornește în Y'}")

print("\nProblema 2.5 – alimentare de la convertor de frecvență cu U/f = constant, f = 30 Hz")
f2 = 30.0
n1_30 = 60 * f2 / 2
# Calea 1 (aproximativă): la U/f = ct și R1 neglijat, Δn la cuplu dat nu depinde de f
dn = 1500 - 1466
n_aprox = n1_30 - dn
# Calea 2: schema echivalentă la 30 Hz, U = 400·30/50 = 240 V, același cuplu electromagnetic
Me_n = r['Me']
M30 = M15.la_frecventa(f2, 400 * f2 / 50)
s30 = brentq(lambda x: M30.cuplu(x) - Me_n, 1e-5, 0.2)
n_model = (1 - s30) * n1_30
sk30, Mmax30 = M30.cuplu_maxim()
print(f"  n1 = {fmt(n1_30, 0)} rot/min; aproximativ n ≈ {fmt(n_aprox, 0)} rot/min;"
      f" schema echivalentă: s = {fmt(s30, 4)}, n = {fmt(n_model, 1)} rot/min")
print(f"  Mmax la 30 Hz = {fmt(Mmax30, 1)} N·m (la 50 Hz: {fmt(Mmax_m, 1)} N·m) – scade din cauza căderii pe R1")
verifica("viteza la 30 Hz: aproximare vs schema echivalentă", n_aprox, n_model, rtol=5e-3)
# Câtă tensiune suplimentară (boost) refacere Mmax la 30 Hz?
U_boost = brentq(lambda U: M15.la_frecventa(f2, U).cuplu_maxim()[1] - Mmax_m, 200, 400)
print(f"  tensiunea de linie necesară la 30 Hz pentru același Mmax ca la 50 Hz = {fmt(U_boost, 1)} V"
      f" (față de {fmt(400 * f2 / 50, 0)} V la U/f strict)")
for f_x in (50, 40, 30, 20, 10, 5):
    print(f"    f = {f_x} Hz, U = {fmt(400 * f_x / 50, 0)} V: Mmax = {fmt(M15.la_frecventa(f_x, 400 * f_x / 50).cuplu_maxim()[1], 1)} N·m")

print("\nProblema 2.6 – economia de energie IE3 față de IE2 (15 kW, 4 poli)")
eta_IE2, eta_IE3, ore = 0.906, 0.921, 4000
P1_IE2, P1_IE3 = 15 / eta_IE2, 15 / eta_IE3
dE = (P1_IE2 - P1_IE3) * ore
# Calea a doua: prin pierderi
pierderi_IE2 = 15 * (1 / eta_IE2 - 1)
pierderi_IE3 = 15 * (1 / eta_IE3 - 1)
print(f"  P1(IE2) = {fmt(P1_IE2, 3)} kW, P1(IE3) = {fmt(P1_IE3, 3)} kW, ΔP = {fmt(P1_IE2 - P1_IE3, 3)} kW,"
      f" ΔE = {fmt(dE, 0)} kWh/an")
print(f"  pierderi IE2 = {fmt(pierderi_IE2, 3)} kW, IE3 = {fmt(pierderi_IE3, 3)} kW (reducere {fmt(100 * (1 - pierderi_IE3 / pierderi_IE2), 1)} %)")
verifica("ΔP prin P1 vs prin pierderi", P1_IE2 - P1_IE3, pierderi_IE2 - pierderi_IE3, rtol=1e-12)
