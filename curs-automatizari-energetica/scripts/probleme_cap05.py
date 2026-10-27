"""Capitolul 5 – Protecția de distanță: rezolvarea și verificarea problemelor."""

import itertools
import numpy as np
from scipy.optimize import brentq
from modele import SQRT3, C_MAX, DATE, fmt, polar, verifica, verifica_adevarat, defect_faze, retea_referinta
from calcul_cap05 import (ZL1, ZL2, Z0L1, K0, FI_L, K_SEC, ERORI, K1, K2, T_ZONE, Z_ZONE, R_ZONE,
                          factor_supraacoperire, factor_subacoperire, mho_interior, mho_comparator, poligon,
                          poligon_interior, poligon_interior_path, retea_cu_bara_pe_linie, bucle, masuratori_faze,
                          masuratori_secvente, impedante_pendulatie, z_pendulatie)

d = DATE


def in_poligon(Z, V, nume):
    """Apartenența la poligon, pe două căi independente (care trebuie să coincidă)."""
    a, b = poligon_interior(Z, V), poligon_interior_path(Z, V)
    verifica_adevarat(f"{nume}: test de apartenență – cele două algoritme coincid", a == b)
    return a


def in_mho(Z, Zr, nume):
    a, b = mho_interior(Z, Zr), mho_comparator(Z, Zr)
    verifica_adevarat(f"{nume}: cerc mho – distanța la centru și comparatorul de fază coincid", a == b)
    return a


POL = [poligon(Z.imag, R) for Z, R in zip(Z_ZONE, R_ZONE)]

print("Problema 5.1 – reglajele zonelor protecției de distanță din A (linia L1)")
print(f"  ZL1 = {fmt(ZL1.real, 2)} + j{fmt(ZL1.imag, 2)} Ω = {polar(ZL1, 2)} Ω; ZL2 = {polar(ZL2, 2)} Ω; "
      f"Z0L1 = {polar(Z0L1, 2)} Ω")
k0_km = (d["z0_110"] - d["z1_110"]) / (3 * d["z1_110"])
print(f"  k0 = (Z0 − Z1)/(3·Z1) = {fmt(K0.real, 4)} + j{fmt(K0.imag, 4)} = {polar(K0, 3)}")
verifica("k0 din impedanțele totale vs din valorile pe km", K0, k0_km)
f_sup, f_sub = factor_supraacoperire(), factor_subacoperire()
print(f"  erori (date): linie ±{fmt(100 * ERORI['linie'], 0)} %, TT ±{fmt(100 * ERORI['TT'], 0)} %, "
      f"TC ±{fmt(100 * ERORI['TC'], 0)} %, releu ±{fmt(100 * ERORI['releu'], 0)} %")
# Calea 2: toate cele 16 combinații de semne ale erorilor
fact = []
for sl, su, si, sr in itertools.product((-1, 1), repeat=4):
    Zreal = 1 + sl * ERORI["linie"]                       # impedanța reală a liniei (la 1 u.r. din datele de calcul)
    Zmas = Zreal * (1 + su * ERORI["TT"]) / (1 + si * ERORI["TC"])   # impedanța „măsurată” prin TT și TC
    fact.append((1 + sr * ERORI["releu"]) / Zmas)       # acoperirea efectivă raportată la acoperirea reglată
print(f"  factorul maxim de supraacoperire = {fmt(f_sup, 4)} (16 combinații: {fmt(max(fact), 4)}); "
      f"de subacoperire = {fmt(f_sub, 4)} (16 combinații: {fmt(1 / min(fact), 4)})")
verifica("supraacoperirea maximă: formulă vs enumerarea combinațiilor", f_sup, max(fact))
verifica("subacoperirea maximă: formulă vs enumerarea combinațiilor", f_sub, 1 / min(fact))
k1_max = 1 / f_sup
print(f"  zona 1: k1 ≤ 1/{fmt(f_sup, 4)} = {fmt(k1_max, 3)} → ales k1 = {fmt(K1, 2)}; Z1 = {polar(Z_ZONE[0], 2)} Ω")
verifica_adevarat("zona 1 nu depășește bara B nici în cazul cel mai defavorabil", K1 * f_sup < 1)
f_sup5 = factor_supraacoperire(dict(ERORI, TC=0.05))
print(f"  (întrebarea 3) cu eroarea TC de 5 %: f_sup = {fmt(f_sup5, 4)}, k1 ≤ {fmt(1 / f_sup5, 3)}")
verifica("f_sup cu TC 5 %: funcție vs calcul direct", f_sup5, 1.05 * 1.05 / (0.95 * 0.97))
print(f"  zona 2: k2 ≥ {fmt(f_sub, 3)} (acoperă sigur bara B) → ales k2 = {fmt(K2, 2)}; Z2 = {polar(Z_ZONE[1], 2)} Ω")
verifica_adevarat("zona 2 acoperă sigur bara B", K2 / f_sub > 1)
# selectivitatea zonei 2 a lui A cu zona 1 a releului din B pe L2 (defect trifazat: nu există alimentare intermediară)
pat_A = (K2 * abs(ZL1) * f_sup - abs(ZL1)) / abs(ZL2)
pat_B = K1 / f_sub
print(f"  zona 2 din A pătrunde pe L2 cel mult {fmt(100 * pat_A, 1)} %; zona 1 din B acoperă cel puțin {fmt(100 * pat_B, 1)} % din L2")
verifica_adevarat("zona 2 din A rămâne în interiorul zonei 1 din B (selectivitate)", pat_A < pat_B)
# Impedanța văzută din A la un defect trifazat pe bara de 20 kV (prin T1); cazul minim: sursa C deconectată
r_fara_C = retea_referinta(cu_capacitati=False)
r_fara_C.elemente.remove(r_fara_C.element("QC"))
V, I, _ = masuratori_faze(r_fara_C, defect_faze("B2", "3f"), linie_releu="L1")
ZT1 = d["ukT"] * d["U110"]**2 / d["ST"]
RT1 = d["PkT"] * d["U110"]**2 / d["ST"]**2
ZT1c = RT1 + 1j * np.sqrt(ZT1**2 - RT1**2)
Z_B2 = V[0] / I[0]
print(f"  defect trifazat pe bara de 20 kV, sursa C deconectată: Z văzută din A = {polar(Z_B2, 2)} Ω "
      f"(ZL1 + ZT1 = {polar(ZL1 + ZT1c, 2)} Ω)")
verifica("Z până la bara de 20 kV: simulare vs ZL1 + ZT1", Z_B2, ZL1 + ZT1c)
# defect monofazat la capătul liniei L2 (alimentare homopolară prin neutrul lui T1) – cerința pentru zona 3
r = retea_cu_bara_pe_linie("L2", 0.999)
V, I, _ = masuratori_faze(r, defect_faze("F", "1f"), linie_releu="L1")
Z_capat_L2 = bucle(V, I)["a-p"]
Z3_min = f_sub * abs(Z_capat_L2)
print(f"  defect monofazat la capătul L2: Z văzută din A = {polar(Z_capat_L2, 2)} Ω → zona 3 ≥ {fmt(f_sub, 3)}·|Z| = "
      f"{fmt(Z3_min, 2)} Ω → aleasă Z3 = {polar(Z_ZONE[2], 2)} Ω ({fmt(abs(Z_ZONE[2]) / abs(ZL1 + ZL2), 3)}·(ZL1 + ZL2))")
verifica("zona 3 = cerința rotunjită în sus la 0,5 Ω", abs(Z_ZONE[2]), np.ceil(Z3_min * 2) / 2)
verifica_adevarat("zona 3 nu ajunge la bara de 20 kV nici cu supraacoperire maximă", abs(Z_ZONE[2]) * f_sup < abs(Z_B2))
print("  reglajele (primar → secundar, cu nTC/nTT = 600/1100):")
r_reach = retea_cu_bara_pe_linie("L1", K1)
for k, (Z, t, R) in enumerate(zip(Z_ZONE, T_ZONE, R_ZONE), start=1):
    print(f"    zona {k}: |Z| = {fmt(abs(Z), 2)} Ω → {fmt(abs(Z) * K_SEC, 3)} Ω sec; X = {fmt(Z.imag, 2)} Ω → "
          f"{fmt(Z.imag * K_SEC, 3)} Ω sec; R (poligon) = {fmt(R, 1)} Ω → {fmt(R * K_SEC, 2)} Ω sec; t = {fmt(t, 1)} s")
z_km = abs(d["z1_110"])
print("  acoperirea zonelor în km de linie de același tip (defecte trifazate metalice): " +
      ", ".join(f"zona {k + 1}: {fmt(abs(Z) / z_km, 1)} km" for k, Z in enumerate(Z_ZONE)) +
      f" (A–B = {fmt(d['lL1'], 0)} km, A–C = {fmt(d['lL1'] + d['lL2'], 0)} km)")
print(f"  zona 3 cu supraacoperire maximă: {fmt(abs(Z_ZONE[2]) * f_sup, 2)} Ω < {fmt(abs(Z_B2), 2)} Ω (bara de 20 kV)")
V, I, _ = masuratori_faze(r_reach, defect_faze("F", "3f"))
Zsec = (V[0] / (d["U110"] / 100)) / (I[0] / 600)
verifica("zona 1 în secundar: conversie vs U/I secundare la defect la limita zonei", Zsec, Z_ZONE[0] * K_SEC)

print("\nProblema 5.2 – defect monofazat (faza a) la 70 % din L1, metalic")
x = 0.7
r = retea_cu_bara_pe_linie("L1", x)
Vp, Ip, _ = masuratori_faze(r, defect_faze("F", "1f"))
Vs, Is, s = masuratori_secvente(r, "F", "1f")
verifica("tensiunile la A: secvențe vs fază", Vs, Vp, rtol=1e-4, atol=1.0)
verifica("curenții prin L1 la A: secvențe vs fază", Is, Ip, rtol=1e-4, atol=0.5)
Zp = bucle(Vp, Ip)
I_comp = Ip[0] + K0 * np.sum(Ip)
print(f"  curenții la A: Ia = {polar(Ip[0], 1)} A, 3I0 = {polar(np.sum(Ip), 1)} A; tensiunea Ua = {polar(Vp[0] / 1e3, 3)} kV")
print(f"  bucla a–pământ cu compensare: Z = Ua/(Ia + k0·3I0) = {polar(Zp['a-p'], 3)} Ω; 0,7·ZL1 = {polar(x * ZL1, 3)} Ω")
verifica("bucla compensată = 0,7·ZL1 (teorie)", Zp["a-p"], x * ZL1, rtol=1e-4)
Z_fara = Vp[0] / Ip[0]
Z_fara_formula = x * ZL1 * (1 + K0 * np.sum(Is) / Is[0])
print(f"  fără compensare: Z = Ua/Ia = {polar(Z_fara, 3)} Ω (formula 0,7·ZL1·(1 + k0·3I0/Ia) = {polar(Z_fara_formula, 3)} Ω)"
      f" → apare la {fmt(100 * abs(Z_fara) / abs(ZL1), 1)} % din linie")
verifica("bucla necompensată: formulă (secvențe) vs fază", Z_fara, Z_fara_formula, rtol=1e-4)
print("  toate cele șase bucle:")
for nume, z in Zp.items():
    ins = in_poligon(z, POL[0], f"bucla {nume}")
    txt = polar(z, 2) + " Ω" if abs(z) < 1e6 else "foarte mare (curentul buclei este practic nul)"
    print(f"    {nume}: {txt} → {'în zona 1' if ins else 'în afara zonei 1'}")
verifica_adevarat("numai bucla a–pământ este în zona 1", [n for n, z in Zp.items() if poligon_interior(z, POL[0])] == ["a-p"])

print("\nProblema 5.3 – rezistența de defect și alimentarea de la capătul opus (Rf = 10 Ω)")
Rf = 10.0
rez = {}
for x in (0.7, 1.0):
    for dC in (-15.0, 0.0, 15.0):
        xx = min(x, 0.999)
        r = retea_cu_bara_pe_linie("L1", xx, dC)
        # transferul de putere dinaintea defectului
        p0 = r.rezolva_faze([])
        V0, I0 = r.tensiuni_faze(p0, "A"), r.curenti_ramura_faze(p0, "L1a", 1)
        P0 = 3 * np.real(V0[0] * np.conj(I0[0]))
        Vp, Ip, _ = masuratori_faze(r, defect_faze("F", "1f", Rf))
        Zap = bucle(Vp, Ip)["a-p"]
        # calea 1: formula Z = x·ZL1 + Rf·IF/(Ia + k0·3I0), cu curenții din rețelele de secvență
        Vs, Is, s = masuratori_secvente(r, "F", "1f", Rf)
        IF = s["I_faza"][0]
        Icomp = Is[0] + K0 * np.sum(Is)
        Z_formula = xx * ZL1 + Rf * IF / Icomp
        beta = np.degrees(np.angle(IF / Icomp))
        ins = in_poligon(Zap, POL[0], f"x = {x}, δ = {dC}")
        rez[(x, dC)] = (Zap, beta, ins)
        print(f"  x = {fmt(100 * x, 0)} %, δ_C = {fmt(dC, 0)}° (P_A→ = {fmt(P0 / 1e6, 1)} MW): Z = {polar(Zap, 2)} Ω = "
              f"{fmt(Zap.real, 2)} + j{fmt(Zap.imag, 2)}; |IF/Icomp| = {fmt(abs(IF / Icomp), 3)}, unghiul β = {fmt(beta, 2)}° "
              f"→ {'ÎN zona 1' if ins else 'în afara zonei 1'}")
        verifica(f"Z aparentă x = {x}, δ = {dC}: formulă (secvențe) vs fază", Z_formula, Zap, rtol=1e-4)
verifica_adevarat("defectul la 70 % rămâne în zona 1 pentru toate cele trei regimuri",
                  all(rez[(0.7, dC)][2] for dC in (-15.0, 0.0, 15.0)))
verifica_adevarat("defectul la capătul liniei (bara B) prin 10 Ω intră în zona 1 la capătul care exportă (supraacoperire)",
                  rez[(1.0, 15.0)][2] and not rez[(1.0, 0.0)][2])
beta_max = max(-rez[(x, 15.0)][1] for x in (0.7, 1.0))
incl = np.radians(np.ceil(beta_max) + 2)
POL1_incl = poligon(Z_ZONE[0].imag, R_ZONE[0], inclinare=incl)
print(f"  unghiul maxim cu care rezistența de defect „coboară” la capătul exportator: {fmt(beta_max, 2)}° → latura "
      f"de sus se înclină cu {fmt(np.degrees(incl), 0)}° (cu 2° rezervă)")
# verificare: cu latura înclinată, defectele la capătul liniei (Rf = 0…10 Ω, δ = −15…15°) nu mai intră în zona 1
ok_capat = True
for dC in (-15.0, 0.0, 15.0):
    for Rf_ in np.linspace(0, 10, 11):
        r = retea_cu_bara_pe_linie("L1", 0.999, dC)
        Vp, Ip, _ = masuratori_faze(r, defect_faze("F", "1f", Rf_))
        ok_capat &= not poligon_interior(bucle(Vp, Ip)["a-p"], POL1_incl)
verifica_adevarat("cu latura înclinată: niciun defect la bara B (Rf ≤ 10 Ω) în zona 1", ok_capat)


def interior_70(Rf_, dC, V):
    r = retea_cu_bara_pe_linie("L1", 0.7, dC)
    Vp, Ip, _ = masuratori_faze(r, defect_faze("F", "1f", Rf_))
    return poligon_interior(bucle(Vp, Ip)["a-p"], V)


# prețul înclinării: acoperirea rezistivă la 70 % din linie, pentru fiecare regim
for dC in (-15.0, 0.0, 15.0):
    acop = {}
    for nume, V in (("orizontală", POL[0]), ("înclinată", POL1_incl)):
        # calea 1: bisecție pe Rf; calea 2: baleiere cu pasul 0,05 Ω
        lo, hi = 0.0, 40.0
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if interior_70(mid, dC, V) else (lo, mid)
        grila = np.arange(0, 40, 0.05)
        ultim = max(R for R in grila if interior_70(R, dC, V))
        verifica(f"acoperirea rezistivă δ = {dC}°, latura {nume}: bisecție vs baleiere", lo, ultim, atol=0.06, rtol=0)
        acop[nume] = lo
    print(f"  defect la 70 %, δ_C = {fmt(dC, 0)}°: Rf maxim acoperit = {fmt(acop['orizontală'], 1)} Ω (latura orizontală),"
          f" {fmt(acop['înclinată'], 1)} Ω (latura înclinată)")
    rez[("acop", dC)] = acop
verifica_adevarat("la capătul care exportă și fără transfer, înclinarea păstrează acoperirea de 10 Ω la 70 %",
                  rez[("acop", 15.0)]["înclinată"] >= 10 and rez[("acop", 0.0)]["înclinată"] >= 10)

print("\nProblema 5.4 – defect bifazat (fazele b–c) la 70 % din L1")
r = retea_cu_bara_pe_linie("L1", 0.7)
Vp, Ip, _ = masuratori_faze(r, defect_faze("F", "2f"))
Vs, Is, _ = masuratori_secvente(r, "F", "2f")
Zp = bucle(Vp, Ip)
Zs = bucle(Vs, Is)
for nume, z in Zp.items():
    txt = polar(z, 2) + " Ω" if abs(z) < 1e6 else "foarte mare (curentul buclei este practic nul)"
    print(f"    {nume}: {txt} → {'în zona 1' if poligon_interior(z, POL[0]) else 'în afara zonei 1'}")
verifica("bucla b–c = 0,7·ZL1 (teorie)", Zp["bc"], 0.7 * ZL1, rtol=1e-4)
I0x3 = abs(np.sum(Ip))
print(f"  3I0 la A = {fmt(I0x3, 3)} A (față de |Ib| = {fmt(abs(Ip[1]), 0)} A): buclele fază–pământ nu sunt eliberate "
      f"de selecția fazelor (criteriul 3I0 > prag), deși b–p și c–p cad în poligon")
verifica_adevarat("la defect bifazat fără pământ 3I0 este practic nul", I0x3 < 1e-3 * abs(Ip[1]))
verifica("bucla b–c: secvențe vs fază", Zs["bc"], Zp["bc"], rtol=1e-4)
verifica_adevarat("bucla b–c este în zona 1 (mho și poligon)",
                  in_mho(Zp["bc"], Z_ZONE[0], "bc") and in_poligon(Zp["bc"], POL[0], "bc"))

print("\nProblema 5.5 – defecte pe linia L2 văzute din A; direcția")
print("  x (din B) | 3f: Z văzut | ZL1 + x·ZL2 | 1f: Z văzut | raport 1f/ideal | zona releului A")
for x in (0.25, 0.5, 0.75, 0.999):
    r = retea_cu_bara_pe_linie("L2", x)
    V3, I3, _ = masuratori_faze(r, defect_faze("F", "3f"), linie_releu="L1")
    Z3 = bucle(V3, I3)["ab"]
    V1, I1, _ = masuratori_faze(r, defect_faze("F", "1f"), linie_releu="L1")
    Z1f = bucle(V1, I1)["a-p"]
    # calea 1: Z = ZL1 + x·ZL2·(IL2,comp/IA,comp), curenții din rețelele de secvență
    Vs, IsA, s = masuratori_secvente(r, "F", "1f", linie_releu="L1")
    IsL2 = r.curenti_ramura_secvente(s, "L2a", 1)
    Z1f_formula = ZL1 + x * ZL2 * (IsL2[0] + K0 * np.sum(IsL2)) / (IsA[0] + K0 * np.sum(IsA))
    verifica(f"3f la {x}: simulare vs ZL1 + x·ZL2", Z3, ZL1 + x * ZL2, rtol=1e-4)
    verifica(f"1f la {x}: formula cu alimentarea homopolară vs simulare", Z1f_formula, Z1f, rtol=1e-4)
    zona = next((k + 1 for k in range(3) if mho_interior(Z1f, Z_ZONE[k])), None)
    print(f"  {fmt(100 * x, 0)} % | {polar(Z3, 2)} | {polar(ZL1 + x * ZL2, 2)} | {polar(Z1f, 2)} | "
          f"{fmt(abs(Z1f) / abs(ZL1 + x * ZL2), 3)} | {zona}")
# curentul homopolar „intermediar”: neutrul lui T1
r = retea_cu_bara_pe_linie("L2", 0.5)
_, IsA, s = masuratori_secvente(r, "F", "1f", linie_releu="L1")
IT1 = r.curenti_ramura_secvente(s, "T1", 1)
print(f"  la defect la 50 % din L2: 3I0 prin L1 = {fmt(abs(np.sum(IsA)), 0)} A, 3I0 prin neutrul lui T1 = "
      f"{fmt(abs(np.sum(IT1)), 0)} A")
# direcția: releul din B pentru linia L1 (privește spre A) vede defectul de pe L2 în spate
V, I, _ = masuratori_faze(retea_cu_bara_pe_linie("L2", 0.5), defect_faze("F", "3f"), linie_releu="L1", bara_releu="B")
r_ = retea_cu_bara_pe_linie("L2", 0.5)
p = r_.rezolva_faze(defect_faze("F", "3f"))
VB = r_.tensiuni_faze(p, "B")
IB_L1 = r_.curenti_ramura_faze(p, "L1", 2)          # curentul care intră în L1 dinspre B
ZB = VB[0] / IB_L1[0]
print(f"  releul din B pentru L1 (privește spre A) vede defectul de pe L2 la Z = {polar(ZB, 2)} Ω (cadranul III)")
verifica_adevarat("defect în spate: unghi între −180° și −90°", -180 < np.degrees(np.angle(ZB)) < -90)
verifica_adevarat("defect în spate: în afara tuturor zonelor (poligon)", not any(poligon_interior(ZB, P) for P in POL))
# teorie: în B nu există alimentare intermediară la secvența directă, deci UB = 0,5·ZL2·I, iar curentul măsurat
# (care intră în L1 dinspre B) este −I: Z = −0,5·ZL2
verifica("Z defect în spate = −x·ZL2", ZB, -0.5 * ZL2, rtol=1e-4)
ZSA, ZSC, ZT = impedante_pendulatie()

print("\nProblema 5.6 – sarcina maximă și zona 3 (încălcarea de sarcină)")
I_max, U_min, phi_max = 600.0, 0.9 * d["U110"], np.radians(30.0)
Zs_min = U_min / (SQRT3 * I_max)
print(f"  Zsarcină,min = 0,9·Un/(√3·Imax) = {fmt(Zs_min, 2)} Ω (primar) = {fmt(Zs_min * K_SEC, 2)} Ω secundar, |φ| ≤ 30°")
# distanța până la limita caracteristicii pe direcția φ = 30°
Z3 = Z_ZONE[2]
mho_30 = abs(Z3) * np.cos(FI_L - phi_max)
V3 = POL[2]
s_pol = brentq(lambda s: poligon_interior(s * np.exp(1j * phi_max), V3) - 0.5, 1.0, 200.0)
# calea analitică pentru poligon: dreapta din dreapta R3 + X·cot φL intersectată cu direcția 30°
s_pol_an = R_ZONE[2] / (np.cos(phi_max) - np.sin(phi_max) / np.tan(FI_L))
print(f"  pe direcția 30°: limita mho a zonei 3 la {fmt(mho_30, 2)} Ω, a poligonului la {fmt(s_pol_an, 2)} Ω "
      f"(căutare numerică {fmt(s_pol, 2)} Ω)")
verifica("limita poligonului pe direcția 30°: analitic vs numeric", s_pol, s_pol_an, rtol=1e-3)
verifica_adevarat("sarcina minimă este în afara zonei 3 (mho și poligon) cu rezervă de peste 20 %",
                  Zs_min > 1.2 * max(mho_30, s_pol_an))
nr_interior = 0
for ph in np.radians(np.linspace(-30, 30, 61)):
    for zm in np.linspace(Zs_min, 3 * Zs_min, 30):
        z = zm * np.exp(1j * ph)
        nr_interior += any(poligon_interior(z, P) for P in POL) + any(mho_interior(z, Zz) for Zz in Z_ZONE)
verifica_adevarat("niciun punct din domeniul de sarcină nu intră în vreo zonă (1830 de puncte)", nr_interior == 0)
R3_max = Zs_min / 1.2 * (np.cos(phi_max) - np.sin(phi_max) / np.tan(FI_L))
print(f"  acoperirea rezistivă maximă a zonei 3 cu rezervă de 20 %: R3 ≤ {fmt(R3_max, 1)} Ω (reglat {fmt(R_ZONE[2], 1)} Ω)")

print("\nProblema 5.7 – pendulații: locul impedanței și timpul de traversare a benzii de blocare")
print(f"  ZSA = {polar(ZSA, 3)} Ω, ZSC = {polar(ZSC, 3)} Ω, ZT = ZSA + ZL1 + ZL2 + ZSC = {polar(ZT, 3)} Ω")
r = retea_referinta(cu_capacitati=False)
qc = r.element("QC")
E0 = qc["E"]


def z_simulat(delta):
    qc["E"] = E0 * np.exp(-1j * delta)
    p = r.rezolva_faze([])
    return r.tensiuni_faze(p, "A")[0] / r.curenti_ramura_faze(p, "L1", 1)[0]


for dd in (60, 90, 120, 150, 180):
    zf, zs = z_pendulatie(np.radians(dd)), z_simulat(np.radians(dd))
    print(f"  δ = {dd}°: Z = {polar(zf, 2)} Ω (simulare {polar(zs, 2)} Ω)")
    verifica(f"locul impedanței la δ = {dd}°: formulă vs rețea", zf, zs, rtol=1e-4)
# t.e.m. de mărimi diferite (|EC| = 0,85·|EA|): locul devine un cerc; aceeași verificare formulă vs rețea
for dd in (90, 150):
    qc["E"] = 0.85 * E0 * np.exp(-1j * np.radians(dd))
    p = r.rezolva_faze([])
    zs = r.tensiuni_faze(p, "A")[0] / r.curenti_ramura_faze(p, "L1", 1)[0]
    verifica(f"locul la |EC| = 0,85·|EA|, δ = {dd}°: formulă vs rețea", z_pendulatie(np.radians(dd), 0.85), zs, rtol=1e-4)
qc["E"] = E0
Zc = ZT / 2 - ZSA
print(f"  centrul electric (δ = 180°): ZT/2 − ZSA = {polar(Zc, 2)} Ω = {fmt(abs(Zc) / abs(ZL1) * 100, 1)} % din |ZL1|")
verifica("centrul electric = Z(180°)", z_pendulatie(np.pi), Zc)
# benzile de blocare: drepte paralele cu linia, prin R = 45 Ω (exterioară) și 35 Ω (interioară)
R_ext, R_int = 45.0, 35.0


def r_fata_de_dreapta(Z, R0):
    """Abaterea (pe axa R) a punctului Z față de dreapta R0 + t·e^{jφL}."""
    return Z.real - (R0 + Z.imag / np.tan(FI_L))


d_ext = brentq(lambda dl: r_fata_de_dreapta(z_pendulatie(dl), R_ext), np.radians(10), np.radians(179))
d_int = brentq(lambda dl: r_fata_de_dreapta(z_pendulatie(dl), R_int), np.radians(10), np.radians(179))
print(f"  δ la traversarea benzii: exterioară {fmt(np.degrees(d_ext), 2)}°, interioară {fmt(np.degrees(d_int), 2)}°")
T_PSB = 0.030
fs_max = np.degrees(d_int - d_ext) / 360 / T_PSB
print(f"  cu temporizarea de detecție {fmt(T_PSB * 1e3, 0)} ms se recunosc pendulațiile cu alunecarea până la "
      f"{fmt(fs_max, 2)} Hz")
# calea 2: simulare în timp, rețeaua rezolvată la fiecare 0,1 ms, alunecare 1 Hz
fs = 1.0
dt = 1e-4
t_ext = t_int = None
prev = None
for n in range(int(0.5 / dt)):
    t = n * dt
    dl = np.radians(20) + 2 * np.pi * fs * t
    z = z_simulat(dl)
    if prev is not None:
        if t_ext is None and r_fata_de_dreapta(prev, R_ext) > 0 >= r_fata_de_dreapta(z, R_ext):
            t_ext = t
        if t_int is None and r_fata_de_dreapta(prev, R_int) > 0 >= r_fata_de_dreapta(z, R_int):
            t_int = t
            break
    prev = z
dt_an = (d_int - d_ext) / (2 * np.pi * fs)
print(f"  alunecare 1 Hz: timpul între benzi = {fmt(dt_an * 1e3, 1)} ms (simulare în timp: {fmt((t_int - t_ext) * 1e3, 1)} ms)")
verifica("timpul de traversare: analitic vs simulare în timp", dt_an, t_int - t_ext, atol=2e-4, rtol=0)
# Cât stă locul în zona 2 (mho) la o pendulație lentă de 0,5 Hz?
fs = 0.5
d_in = brentq(lambda dl: abs(z_pendulatie(dl) - Z_ZONE[1] / 2) - abs(Z_ZONE[1]) / 2, np.radians(90), np.pi)
d_out = 2 * np.pi - d_in
t_z2 = (d_out - d_in) / (2 * np.pi * fs)
print(f"  locul intră în zona 2 la δ = {fmt(np.degrees(d_in), 1)}° și iese la {fmt(np.degrees(d_out), 1)}°; "
      f"la alunecarea de {fmt(fs, 1)} Hz rămâne în zona 2 {fmt(t_z2 * 1e3, 0)} ms (temporizarea zonei 2: {fmt(T_ZONE[1] * 1e3, 0)} ms)")
# calea 2: baleierea locului calculat cu rețeaua, cu comparatorul de fază al caracteristicii mho
grila_d = np.radians(np.arange(90, 180, 0.01))
d_in_sim = next(dl for dl in grila_d if mho_comparator(z_simulat(dl), Z_ZONE[1]))
verifica("δ la intrarea în zona 2: rădăcină (formula închisă) vs baleiere (rețea, comparator)",
         np.degrees(d_in), np.degrees(d_in_sim), atol=0.011, rtol=0)
verifica_adevarat("fără blocare la pendulații, zona 2 ar declanșa la o pendulație de 0,5 Hz", t_z2 > T_ZONE[1])
verifica_adevarat("locul nu intră în zona 1 (centrul electric este dincolo de acoperirea zonei 1)",
                  not mho_interior(Zc, Z_ZONE[0]) and abs(Zc) > abs(Z_ZONE[0]))

print("\nProblema 5.8 – câștigul de timp cu teleprotecție (defect la 90 % din L1)")
t_rel, t_can, t_cb, t_coord = 0.025, 0.010, 0.060, 0.020    # date de problemă [s]
ZA = 0.9 * ZL1
ZB_ = 0.1 * ZL1
zona_A = next(k + 1 for k in range(3) if mho_interior(ZA, Z_ZONE[k]))
zona_B = 1 if mho_interior(ZB_, K1 * ZL1) else None
print(f"  A vede {polar(ZA, 2)} Ω → zona {zona_A}; B vede {polar(ZB_, 2)} Ω → zona {zona_B}")
verifica_adevarat("A în zona 2, B în zona 1", zona_A == 2 and zona_B == 1)
formule = {
    "fără teleprotecție": T_ZONE[1] + t_rel,
    "PUTT/POTT (permisiv)": max(t_rel, t_rel + t_can),
    "blocare": t_rel + t_coord,
}
# calea 2: simularea logicii pe o grilă de 1 ms
grila = np.arange(0, 1.0, 1e-3)
zA2 = grila >= t_rel                       # zona 2 din A a pornit (măsurătoare încheiată)
zB1 = grila >= t_rel                       # zona 1 din B a pornit
perm_primit = grila >= t_rel + t_can       # semnalul permisiv de la B ajunge în A
bloc_primit = np.zeros_like(grila, bool)   # B nu trimite blocare (defectul e în fața lui)
sim = {
    "fără teleprotecție": grila[np.argmax(zA2 & (grila >= t_rel + T_ZONE[1]))],
    "PUTT/POTT (permisiv)": grila[np.argmax(zA2 & perm_primit)],
    "blocare": grila[np.argmax(zA2 & ~bloc_primit & (grila >= t_rel + t_coord))],
}
for k in formule:
    print(f"  {k}: A comandă declanșarea la {fmt(formule[k] * 1e3, 0)} ms; defectul este eliminat la "
          f"{fmt((formule[k] + t_cb) * 1e3, 0)} ms")
    verifica(f"{k}: formulă vs simularea logicii", formule[k], sim[k], atol=1.1e-3, rtol=0)
