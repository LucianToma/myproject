"""Capitolul 1 – Regimuri de defect: rezolvarea și verificarea problemelor."""

import numpy as np
from modele import (SQRT3, W0, C_MAX, C_MIN, DATE, fmt, polar, verifica, verifica_adevarat, kappa, K_T,
                    impedanta_sursa, retea_referinta, defect_faze, RN_rezistor)

d = DATE
U110, U20 = d["U110"], d["U20"]

print("Problema 1.1 – unități relative și curentul de scurtcircuit trifazat la bara B2 (20 kV)")
Sb = 100e6
Zb110, Zb20 = U110**2 / Sb, U20**2 / Sb
Ib110, Ib20 = Sb / (SQRT3 * U110), Sb / (SQRT3 * U20)
print(f"  Sb = 100 MVA; Zb(110 kV) = {fmt(Zb110, 1)} Ω, Zb(20 kV) = {fmt(Zb20, 1)} Ω; "
      f"Ib(110 kV) = {fmt(Ib110, 1)} A, Ib(20 kV) = {fmt(Ib20, 1)} A")
ZQA = impedanta_sursa(d["SkA"], U110, d["XR_sursa"])
ZQC = impedanta_sursa(d["SkC"], U110, d["XR_sursa"])
zQA, zQC = ZQA / Zb110, ZQC / Zb110
zL1, zL2 = d["z1_110"] * d["lL1"] / Zb110, d["z1_110"] * d["lL2"] / Zb110
ZT_ohm = d["ukT"] * U110**2 / d["ST"]
RT_ohm = d["PkT"] * U110**2 / d["ST"]**2
zT = (RT_ohm + 1j * np.sqrt(ZT_ohm**2 - RT_ohm**2)) / Zb110
print(f"  zQA = {fmt(zQA.real, 4)} + j{fmt(zQA.imag, 4)}; zQC = {fmt(zQC.real, 4)} + j{fmt(zQC.imag, 4)}")
print(f"  zL1 = {fmt(zL1.real, 4)} + j{fmt(zL1.imag, 4)}; zL2 = {fmt(zL2.real, 4)} + j{fmt(zL2.imag, 4)}")
print(f"  zT = {fmt(zT.real, 4)} + j{fmt(zT.imag, 4)} (|zT| = {fmt(abs(zT), 3)})")
verifica("|zT| = uk·Sb/Sn", abs(zT), d["ukT"] * Sb / d["ST"])
z_B = 1 / (1 / (zQA + zL1) + 1 / (zQC + zL2))
z_B2 = z_B + zT
zF1a = (d["z1_cablu"] * d["l_cablu_F1"] + d["z1_lea20"] * d["l_lea_F1a"]) / Zb20
zF1b = d["z1_lea20"] * d["l_lea_F1b"] / Zb20
z_P1, z_P2 = z_B2 + zF1a, z_B2 + zF1a + zF1b
mana = {}
for nume, z, Ib in (("B", z_B, Ib110), ("B2", z_B2, Ib20), ("P1", z_P1, Ib20), ("P2", z_P2, Ib20)):
    mana[nume] = C_MAX / abs(z) * Ib
    print(f"  z({nume}) = {fmt(z.real, 4)} + j{fmt(z.imag, 4)} u.r. → I\"k3 = c/|z|·Ib = {fmt(mana[nume] / 1e3, 3)} kA")

r = retea_referinta(cu_capacitati=False)
for nume in mana:
    s = r.scurtcircuit_secvente(nume, "3f")
    p = r.rezolva_faze(defect_faze(nume, "3f"))
    I_s = abs(s["I_faza"][0])
    I_p = abs(r.curent_defect_faze(p)[0])
    verifica(f"I\"k3({nume}): unități relative vs rețele de secvență (Ω)", mana[nume], I_s)
    verifica(f"I\"k3({nume}): rețele de secvență vs coordonate de fază", I_s, I_p)

print("\nProblema 1.2 – curenții de scurtcircuit maximi și minimi la toate barele")
r_min = retea_referinta(c=C_MIN, cu_capacitati=False)
r_min80 = retea_referinta(c=C_MIN, cu_capacitati=False, kR20=1 + 0.004 * (80 - 20))
tabel = {}
for b in ("A", "B", "C", "B2", "P1", "P2"):
    s_max = r.scurtcircuit_secvente(b, "3f")
    I3 = abs(s_max["I_faza"][0])
    I3min = abs(r_min.scurtcircuit_secvente(b, "3f")["I_faza"][0])
    I2min = abs(r_min.scurtcircuit_secvente(b, "2f")["I_faza"][1])
    I2min80 = abs(r_min80.scurtcircuit_secvente(b, "2f")["I_faza"][1])
    Z1 = s_max["Zth"][1]
    Un = r.bare[b]
    Sk = SQRT3 * Un * I3
    tabel[b] = dict(I3=I3, I3min=I3min, I2min=I2min, I2min80=I2min80, Z1=Z1)
    print(f"  {b}: Z1 = {fmt(Z1.real, 3)} + j{fmt(Z1.imag, 3)} Ω; I\"k3max = {fmt(I3 / 1e3, 3)} kA (S\"k = {fmt(Sk / 1e6, 0)} MVA);"
          f" I\"k3min = {fmt(I3min / 1e3, 3)} kA; I\"k2min = {fmt(I2min / 1e3, 3)} kA"
          f" (cu R la 80 °C pe 20 kV: {fmt(I2min80 / 1e3, 3)} kA)")
    verifica(f"I\"k3min/I\"k3max = c_min/c_max la {b}", I3min / I3, C_MIN / C_MAX)
    verifica(f"I\"k2 = (√3/2)·I\"k3 la {b} (Z2 = Z1)", I2min, SQRT3 / 2 * I3min)
    p2 = r_min.rezolva_faze(defect_faze(b, "2f"))
    verifica(f"I\"k2min la {b}: secvențe vs fază", I2min, abs(r_min.curent_defect_faze(p2)[0]))

print("\nProblema 1.3 – defectul monofazat în rețeaua de 110 kV")
for b in ("A", "B", "C"):
    s1 = r.scurtcircuit_secvente(b, "1f")
    Z0, Z1, _ = s1["Zth"]
    I1 = abs(s1["I_faza"][0])
    raport = I1 / tabel[b]["I3"]
    raport_formula = abs(3 / (2 + Z0 / Z1))
    p = r.rezolva_faze(defect_faze(b, "1f"))
    print(f"  {b}: Z0 = {fmt(Z0.real, 3)} + j{fmt(Z0.imag, 3)} Ω, Z0/Z1 = {polar(Z0 / Z1, 3)}; "
          f"I\"k1 = {fmt(I1 / 1e3, 3)} kA; I\"k1/I\"k3 = {fmt(raport, 3)}")
    verifica(f"I\"k1/I\"k3 = |3/(2 + Z0/Z1)| la {b}", raport, raport_formula)
    verifica(f"I\"k1 la {b}: secvențe vs fază", I1, abs(r.curent_defect_faze(p)[0]))
    # tensiunile fazelor sănătoase la locul defectului (coeficientul de punere la pământ)
    Vab = r.tensiuni_faze(p, b)
    k_pp = max(abs(Vab[1]), abs(Vab[2])) / (C_MAX * U110 / SQRT3)
    print(f"     tensiunea maximă pe fazele sănătoase = {fmt(k_pp, 3)}·(c·Un/√3)")

print("\nProblema 1.4 – curentul de șoc ip la barele B2 și A")
for b in ("B2", "A"):
    Z1 = tabel[b]["Z1"]
    R, X = Z1.real, Z1.imag
    kap = kappa(R, X)
    ip = kap * np.sqrt(2) * tabel[b]["I3"]
    # Calea a doua: maximul curentului într-un circuit R-L echivalent, căutat după unghiul de conectare
    w = W0
    tau = X / (w * R)
    phi = np.arctan2(X, R)
    t = np.linspace(0, 0.03, 30001)
    best = 0.0
    for al in np.radians(np.arange(0, 180.01, 0.25)):
        i = np.sin(w * t + al - phi) - np.sin(al - phi) * np.exp(-t / tau)
        best = max(best, np.max(np.abs(i)))
    print(f"  {b}: R/X = {fmt(R / X, 4)}; κ = 1,02 + 0,98·e^(−3R/X) = {fmt(kap, 3)}; ip = {fmt(ip / 1e3, 2)} kA;"
          f" maximul exact al circuitului R-L: κ = {fmt(best, 3)}")
    verifica(f"κ IEC vs maximul exact R-L la {b} (aproximare sub 1 %)", kap, best, rtol=1e-2)

print("\nProblema 1.5 – factorul de corecție K_T al transformatorului T1")
xT = d["ukT"]
KT = K_T(xT)
I_cu = abs(retea_referinta(cu_capacitati=False, KT=KT).scurtcircuit_secvente("B2", "3f")["I_faza"][0])
print(f"  K_T = 0,95·c_max/(1 + 0,6·x_T) = 0,95·1,1/(1 + 0,6·{fmt(xT, 2)}) = {fmt(KT, 4)}")
print(f"  I\"k3(B2) fără K_T = {fmt(tabel['B2']['I3'] / 1e3, 3)} kA; cu K_T = {fmt(I_cu / 1e3, 3)} kA "
      f"(+{fmt(100 * (I_cu / tabel['B2']['I3'] - 1), 2)} %)")
verifica("K_T formula", KT, 0.95 * 1.1 / (1 + 0.6 * 0.11))
verifica_adevarat("efectul lui K_T la B2 este sub 2 %", abs(I_cu / tabel["B2"]["I3"] - 1) < 0.02)

print("\nProblema 1.6 – punerea la pământ în rețeaua de 20 kV, cu trei moduri de tratare a neutrului")
Uf = U20 / SQRT3
C0_tot = (d["c_cablu"] * (d["l_cablu_F1"] + d["l_cablu_rest"]) +
          d["c0_lea20"] * (d["l_lea_F1a"] + d["l_lea_F1b"] + d["l_lea_rest"]))
Ic = 3 * W0 * C0_tot * Uf
print(f"  C0 total = {fmt(C0_tot * 1e6, 3)} µF/fază (cabluri {fmt(d['l_cablu_F1'] + d['l_cablu_rest'], 0)} km, "
      f"LEA {fmt(d['l_lea_F1a'] + d['l_lea_F1b'] + d['l_lea_rest'], 0)} km)")
print(f"  curentul capacitiv de punere la pământ Ic = 3ωC0·Uf = {fmt(Ic, 1)} A")
# Formulele de manual neglijează impedanțele longitudinale (Z1 + Z2) și creșterea de tensiune
# produsă de capacitățile rețelei în gol; calculul exact (secvențe și fază) le include.
def exact(rr_):
    s_ = rr_.scurtcircuit_secvente("B2", "1f")
    p_ = rr_.rezolva_faze(defect_faze("B2", "1f"))
    I_s = abs(s_["I_faza"][0])
    I_p = abs(rr_.curent_defect_faze(p_)[0])
    verifica("curentul de defect: secvențe vs coordonate de fază", I_s, I_p)
    return I_p, rr_.tensiuni_faze(p_, "B2"), s_


# (a) neutru izolat
ri = retea_referinta("izolat", c=1.0)
If_iz, Vabc, si = exact(ri)
V0 = np.mean(Vabc)
print(f"  (a) neutru izolat: calcul exact I_defect = {fmt(If_iz, 1)} A (formula de manual: {fmt(Ic, 1)} A, "
      f"diferență {fmt(100 * (If_iz / Ic - 1), 1)} %)")
print(f"      tensiunile fazelor sănătoase = {fmt(abs(Vabc[1]) / Uf, 3)}·Uf și {fmt(abs(Vabc[2]) / Uf, 3)}·Uf "
      f"(manual: √3 = 1,732); |U0| = {fmt(abs(V0) / Uf, 3)}·Uf")
Z0, Z1, Z2 = si["Zth"]
print(f"      motive: tensiunea dinaintea defectului = {fmt(abs(si['Vf']) / Uf, 4)}·Uf (efect capacitiv), "
      f"|Z0| = {fmt(abs(Z0), 1)} Ω față de |Z0 + Z1 + Z2| = {fmt(abs(Z0 + Z1 + Z2), 1)} Ω")
verifica("formula de manual Ic vs calcul exact (abatere sub 3 %)", Ic, If_iz, rtol=3e-2)
verifica("formula cu Vf și Z1 + Z2 incluse vs calcul exact", 3 * abs(si["Vf"]) / abs(Z0 + Z1 + Z2), If_iz)
verifica("faza sănătoasă ≈ √3·Uf (abatere sub 3 %)", abs(Vabc[1]) / Uf, SQRT3, rtol=3e-2)
# (b) bobină de stingere supracompensată cu 10 %
v = 0.10
XN = 1 / ((1 + v) * 3 * W0 * C0_tot)
rb = retea_referinta("bobina", c=1.0, Zn_bobina=XN)
If_b, Vb, sb = exact(rb)
IL = Uf / XN
print(f"  (b) bobină de stingere (acord +10 %): X_N = 1/(1,1·3ωC0) = {fmt(XN, 2)} Ω, L = {fmt(XN / W0, 4)} H, "
      f"I_L = Uf/X_N = {fmt(IL, 1)} A")
print(f"      curentul rezidual la locul defectului: exact {fmt(If_b, 2)} A; manual I_L − Ic = {fmt(IL - Ic, 2)} A")
verifica("curent rezidual: manual vs exact (abatere sub 5 %)", IL - Ic, If_b, rtol=5e-2)
verifica_adevarat("curentul rezidual este de peste 8 ori mai mic decât Ic", If_b < Ic / 8)
# (c) rezistor de neutru care limitează curentul la 300 A
RN = RN_rezistor(U20, d["IN_rezistor"])
rr = retea_referinta("rezistor", c=1.0)
If_r, Vr, sr = exact(rr)
If_r_formula = abs(Uf / RN + 1j * Ic)
print(f"  (c) rezistor de neutru: RN = Uf/300 A = {fmt(RN, 2)} Ω; I_defect exact = {fmt(If_r, 1)} A "
      f"(manual √(IR² + Ic²) = √({fmt(Uf / RN, 0)}² + {fmt(Ic, 0)}²) = {fmt(If_r_formula, 1)} A)")
verifica("I_defect rezistor: manual vs exact (abatere sub 3 %)", If_r_formula, If_r, rtol=3e-2)
for nume, V in (("izolat", Vabc), ("bobină", Vb), ("rezistor", Vr)):
    print(f"     {nume}: tensiunea fazei b = {fmt(abs(V[1]) / Uf, 3)}·Uf, a fazei c = {fmt(abs(V[2]) / Uf, 3)}·Uf")
