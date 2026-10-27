"""Capitolul 1 – Transformatorul: rezolvarea și verificarea problemelor."""

import numpy as np
from modele import (SQRT3, fmt, verifica, polar, parametri_gol, parametri_scurtcircuit,
                    tensiune_secundar_exacta, cadere_tensiune_aprox, randament_transformator)

print("Problema 1.1 – transformator ideal 230/12 V")
U1, U2, N1, f, P_bec = 230.0, 12.0, 1150, 50.0, 60.0
k = U1 / U2
N2 = N1 / k
I2 = P_bec / U2
R = U2 / I2
I1 = I2 / k
R_raportat = k**2 * R
Phi_max = U1 / (4.44 * f * N1)
print(f"  k = {fmt(k, 3)}, N2 = {fmt(N2, 1)} spire, I2 = {fmt(I2, 2)} A, R = {fmt(R, 2)} Ω")
print(f"  I1 = {fmt(I1, 4)} A, R' = k²R = {fmt(R_raportat, 1)} Ω, Φmax = {fmt(Phi_max * 1e3, 3)} mWb,"
      f" A_fe la 1,2 T = {fmt(Phi_max / 1.2 * 1e4, 2)} cm²")
verifica("I1 = I2/k vs U1/R'", I1, U1 / R_raportat)
verifica("conservarea puterii U1 I1 = U2 I2", U1 * I1, U2 * I2)

print("\nProblema 1.2 – transformator monofazat 20 kVA, 2400/240 V – parametri din încercări")
Sn, U1n, U2n = 20e3, 2400.0, 240.0
k = U1n / U2n
I1n, I2n = Sn / U1n, Sn / U2n
# Încercarea de gol (pe JT): U0 = 240 V, I0 = 2,0 A, P0 = 120 W
U0, I0, P0 = 240.0, 2.0, 120.0
g = parametri_gol(U0, I0, P0)
print(f"  I1n = {fmt(I1n, 3)} A, I2n = {fmt(I2n, 2)} A")
print(f"  gol: cosφ0 = {fmt(g['cos_phi0'], 3)}, Ia = {fmt(g['Ia'], 3)} A, Iμ = {fmt(g['Imu'], 3)} A,"
      f" RFe = {fmt(g['RFe'], 1)} Ω, Xm = {fmt(g['Xm'], 1)} Ω (raportate la JT);"
      f" la ÎT: RFe = {fmt(g['RFe'] * k**2 / 1e3, 1)} kΩ, Xm = {fmt(g['Xm'] * k**2 / 1e3, 2)} kΩ")
print(f"  i0 = {fmt(100 * I0 / I2n, 2)} %")
# Încercarea de scurtcircuit (pe ÎT): Usc = 96 V, Isc = I1n, Psc = 300 W
Usc, Isc, Psc = 96.0, I1n, 300.0
sc = parametri_scurtcircuit(Usc, Isc, Psc)
usc = 100 * Usc / U1n
uR = 100 * Psc / Sn
uX = np.sqrt(usc**2 - uR**2)
print(f"  scurtcircuit: Zsc = {fmt(sc['Zsc'], 3)} Ω, Rsc = {fmt(sc['Rsc'], 3)} Ω, Xsc = {fmt(sc['Xsc'], 3)} Ω,"
      f" cosφsc = {fmt(sc['cos_phisc'], 3)}")
print(f"  usc = {fmt(usc, 2)} %, uR = {fmt(uR, 3)} %, uX = {fmt(uX, 3)} %")
verifica("uR din Rsc vs din Psc", 100 * sc['Rsc'] * I1n / U1n, uR)
verifica("uX din Xsc vs din usc,uR", 100 * sc['Xsc'] * I1n / U1n, uX)

# Funcționare la sarcină nominală, cos φ2 = 0,8 inductiv, U1 = U1n
cos2 = 0.8
U2r = tensiune_secundar_exacta(U1n, I1n, cos2, sc['Rsc'], sc['Xsc'])
dU_exact = 100 * (U1n - U2r) / U1n
dU_aprox = cadere_tensiune_aprox(1.0, uR, uX, cos2)
sin2 = 0.6
dU_aprox2 = dU_aprox + (uX * cos2 - uR * sin2) ** 2 / 200
print(f"  sarcină nominală cos φ2 = 0,8 ind.: U2' = {fmt(U2r, 1)} V → U2 = {fmt(U2r / k, 2)} V,"
      f" ΔU exact = {fmt(dU_exact, 3)} %, ΔU aprox = {fmt(dU_aprox, 3)} %,"
      f" cu termenul de ordinul 2 = {fmt(dU_aprox2, 3)} %")
verifica("ΔU exact vs formula cu termen de ordinul 2", dU_exact, dU_aprox2, rtol=2e-3)
# Verificare suplimentară prin ecuația fazorială directă
U2_fazor = U2r + 0j
I2_fazor = I1n * np.exp(-1j * np.arccos(cos2))
U1_fazor = U2_fazor + (sc['Rsc'] + 1j * sc['Xsc']) * I2_fazor
print(f"  U1 recalculat din fazori = {polar(U1_fazor, 2)} V")
verifica("|U1| recalculat = U1n", abs(U1_fazor), U1n)

eta_n = randament_transformator(1.0, Sn, cos2, P0, Psc)
beta_opt = np.sqrt(P0 / Psc)
eta_max = randament_transformator(beta_opt, Sn, cos2, P0, Psc)
betas = np.linspace(0.01, 1.5, 150001)
etas = randament_transformator(betas, Sn, cos2, P0, Psc)
print(f"  η(β=1, cosφ=0,8) = {fmt(100 * eta_n, 2)} %; β_opt = {fmt(beta_opt, 3)}; η_max = {fmt(100 * eta_max, 2)} %")
verifica("β_opt formulă vs scanare numerică", beta_opt, betas[np.argmax(etas)], rtol=1e-3)
verifica("η_max formulă vs scanare numerică", eta_max, etas.max(), rtol=1e-6)

# Randamentul prin calculul complet al schemei în T (calea a doua), raportat la ÎT
RFe_HT, Xm_HT = g['RFe'] * k**2, g['Xm'] * k**2
R1 = R2r = sc['Rsc'] / 2
X1 = X2r = sc['Xsc'] / 2
U2t = U1n * 0.97   # pornim de la o estimare și iterăm până când U1 = U1n
for _ in range(50):
    I2t = I1n * np.exp(-1j * np.arccos(cos2))
    E = U2t + (R2r + 1j * X2r) * I2t
    I0t = E / RFe_HT + E / (1j * Xm_HT)
    I1t = I2t + I0t
    U1t = E + (R1 + 1j * X1) * I1t
    U2t *= U1n / abs(U1t)
P1t = (U1t * np.conj(I1t)).real
P2t = (U2t * np.conj(I2t)).real
print(f"  schema în T: U2' = {fmt(abs(U2t), 1)} V, P1 = {fmt(P1t, 1)} W, P2 = {fmt(P2t, 1)} W,"
      f" pierderi = {fmt(P1t - P2t, 1)} W, η = {fmt(100 * P2t / P1t, 2)} %, |I1| = {fmt(abs(I1t), 3)} A")
# Randamentul convențional folosește P2 la tensiunea nominală; la aceeași P2 reală
# cele două căi trebuie să dea același randament.
eta_conv_P2real = P2t / (P2t + P0 + Psc)
print(f"  η convențional cu P2 real = {fmt(100 * eta_conv_P2real, 2)} %")
verifica("pierderi P0+Psc vs schema în T", P0 + Psc, P1t - P2t, rtol=1e-2)
verifica("η convențional (P2 real) vs schema în T", eta_conv_P2real, P2t / P1t, rtol=1e-4)
verifica("ΔU schema simplificată vs schema în T", U2r, abs(U2t), rtol=1e-3)

print("\nProblema 1.3 – transformator trifazat de distribuție 400 kVA, 20/0,4 kV, Dyn11")
Sn, U1n, U2n = 400e3, 20e3, 400.0
usc, P0, Psc = 4.0, 430.0, 4600.0
I1n, I2n = Sn / (SQRT3 * U1n), Sn / (SQRT3 * U2n)
I1f = I1n / SQRT3            # înfășurarea ÎT în triunghi
U1f, U2f = U1n, U2n / SQRT3  # tensiuni de fază: ÎT triunghi, JT stea
k_linie, k_faza = U1n / U2n, U1f / U2f
print(f"  I1n = {fmt(I1n, 2)} A (de linie), curentul în înfășurarea ÎT = {fmt(I1f, 2)} A, I2n = {fmt(I2n, 1)} A")
print(f"  raportul tensiunilor de linie = {fmt(k_linie, 1)}, raportul spirelor (tensiuni de fază) = {fmt(k_faza, 2)}")
uR = 100 * Psc / Sn
uX = np.sqrt(usc**2 - uR**2)
print(f"  uR = {fmt(uR, 3)} %, uX = {fmt(uX, 3)} %")
# Sarcina: 300 kW la cos φ = 0,9 inductiv
P_s, cos2 = 300e3, 0.9
S_s = P_s / cos2
beta = S_s / Sn
dU = cadere_tensiune_aprox(beta, uR, uX, cos2)
eta = randament_transformator(beta, Sn, cos2, P0, Psc)
# Calea a doua: schema pe fază (stea echivalentă JT) și ecuația fazorială exactă
Zb = U2n**2 / Sn
Rsc_JT = uR / 100 * Zb
Xsc_JT = uX / 100 * Zb
U2_exact = tensiune_secundar_exacta(U2f, beta * I2n, cos2, Rsc_JT, Xsc_JT)
dU_ex = 100 * (U2f - U2_exact) / U2f
Pierderi = P0 + 3 * (beta * I2n) ** 2 * Rsc_JT
eta2 = beta * Sn * cos2 / (beta * Sn * cos2 + Pierderi)
sin2 = np.sqrt(1 - cos2**2)
dU_2 = dU + (beta * (uX * cos2 - uR * sin2)) ** 2 / 200
print(f"  β = {fmt(beta, 4)}, ΔU aprox = {fmt(dU, 3)} %, cu termenul de ordinul 2 = {fmt(dU_2, 3)} %,"
      f" ΔU exact = {fmt(dU_ex, 3)} %, U2 = {fmt(U2_exact * SQRT3, 1)} V")
print(f"  pierderi = {fmt(Pierderi, 0)} W, η = {fmt(100 * eta, 3)} %")
print(f"  Rsc = {Rsc_JT * 1e3:.3f} mΩ, Xsc = {Xsc_JT * 1e3:.3f} mΩ (pe fază, JT)")
verifica("ΔU aprox (ordinul 2) vs exact", dU_2, dU_ex, rtol=1e-3)
verifica("η prin pierderi raportate vs pe fază", eta, eta2, rtol=1e-9)
beta_opt = np.sqrt(P0 / Psc)
print(f"  β_opt = {fmt(beta_opt, 3)} → S = {fmt(beta_opt * Sn / 1e3, 1)} kVA;"
      f" η_max(cosφ=0,9) = {fmt(100 * randament_transformator(beta_opt, Sn, cos2, P0, Psc), 3)} %")
print(f"  η la β=1, cosφ=0,9 = {fmt(100 * randament_transformator(1, Sn, cos2, P0, Psc), 3)} %")
# Curentul de scurtcircuit permanent la bornele JT (rețea de putere infinită)
Isc_JT = I2n * 100 / usc
print(f"  curentul de scurtcircuit trifazat la bornele JT ≈ {fmt(Isc_JT / 1e3, 2)} kA")
verifica("Isc prin impedanță vs prin usc", Isc_JT, U2f / np.hypot(Rsc_JT, Xsc_JT))

print("\nProblema 1.4 – funcționarea în paralel a două transformatoare")
S1n, usc1 = 630e3, 6.0
S2n, usc2 = 400e3, 4.0
S_tot = 1000e3
den = S1n / usc1 + S2n / usc2
S1 = S_tot * (S1n / usc1) / den
S2 = S_tot * (S2n / usc2) / den
# Calea a doua: impedanțele în ohmi raportate la 0,4 kV, curenții se împart invers proporțional
Z1 = usc1 / 100 * 400**2 / S1n
Z2 = usc2 / 100 * 400**2 / S2n
S1b = S_tot * Z2 / (Z1 + Z2)
S2b = S_tot * Z1 / (Z1 + Z2)
print(f"  S1 = {fmt(S1 / 1e3, 1)} kVA ({fmt(100 * S1 / S1n, 1)} % din S1n), S2 = {fmt(S2 / 1e3, 1)} kVA ({fmt(100 * S2 / S2n, 1)} % din S2n)")
print(f"  Z1 = {Z1 * 1e3:.3f} mΩ, Z2 = {Z2 * 1e3:.3f} mΩ")
S_max = S2n * den / (S2n / usc2)
print(f"  sarcina totală maximă fără suprasarcină = {fmt(S_max / 1e3, 1)} kVA din {fmt((S1n + S2n) / 1e3, 0)} kVA instalați"
      f" ({fmt(100 * S_max / (S1n + S2n), 1)} %)")
verifica("S1 formula usc vs impedanțe", S1, S1b)
verifica("S2 formula usc vs impedanțe", S2, S2b)

print("\nProblema 1.5 – autotransformator 230/200 V, 2 kVA")
U1, U2, S = 230.0, 200.0, 2000.0
I1, I2 = S / U1, S / U2
Ic = I2 - I1
S_em_1 = S * (1 - U2 / U1)
S_em_2 = U2 * Ic
S_em_3 = (U1 - U2) * I1
print(f"  I1 = {fmt(I1, 3)} A, I2 = {fmt(I2, 3)} A, curentul în porțiunea comună = {fmt(Ic, 3)} A")
print(f"  puterea transferată electromagnetic = {fmt(S_em_1, 1)} VA ({fmt(100 * S_em_1 / S, 1)} % din S)")
verifica("S_em formulă vs U2·Ic", S_em_1, S_em_2)
verifica("S_em formulă vs (U1-U2)·I1", S_em_1, S_em_3)
