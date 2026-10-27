"""Capitolul 4 – Protecția diferențială: rezolvarea și verificarea problemelor."""

import numpy as np
from modele import (SQRT3, W0, C_MIN, DATE, fmt, polar, verifica, verifica_adevarat, retea_referinta,
                    defect_faze, faza_la_seq, A)
from calcul_cap04 import (IN_IT, IN_JT, TC_IT, TC_JT, M_YND11, marimi_releu, prag_diferential, IDIFF_MIN,
                          K1, K2, IB2, IDIFF_NEFRANAT, ARMONICA2, INRUSH, parametri_inrush, simuleaza_inrush,
                          armonici_dft, sinus_trunchiat_analitic, raport_armonica2_alunecator)

d = DATE
n_T = d["U110"] / d["U20"]
r = retea_referinta(cu_capacitati=False)


def curenti_T1(retea, bara, tip, Rf=0.0):
    """Curenții primari care intră în T1 pe cele două părți: calea de fază (rețeaua în coordonate de fază)."""
    p = retea.rezolva_faze(defect_faze(bara, tip, Rf))
    return retea.curenti_ramura_faze(p, "T1", 1), retea.curenti_ramura_faze(p, "T1", 2), p


def curenti_T1_secvente(retea, bara, tip, Rf=0.0, U1=d["U110"]):
    """Calea 1: componentele simetrice ale curentului de 110 kV din rețelele de secvență; curentul de
    20 kV se obține din teoria transformatorului YNd11 (raport n, defazaj +30° în sistemul direct,
    −30° în cel invers, fără componentă homopolară în liniile triunghiului)."""
    s = retea.scurtcircuit_secvente(bara, tip, Zf=Rf)
    I_IT = retea.curenti_ramura_secvente(s, "T1", 1)
    I0, I1, I2 = faza_la_seq(I_IT)
    n = U1 / d["U20"]
    J1 = -n * np.exp(1j * np.pi / 6) * I1
    J2 = -n * np.exp(-1j * np.pi / 6) * I2
    return I_IT, A @ np.array([0, J1, J2]), (I0, I1, I2)


print("Problema 4.1 – adaptarea de amplitudine și compensarea grupei de conexiuni YNd11")
print(f"  In(110 kV) = {fmt(IN_IT, 1)} A, In(20 kV) = {fmt(IN_JT, 1)} A; TC {TC_IT:g}/1 A și {TC_JT:g}/1 A")
print(f"  factori de adaptare: 110 kV: {TC_IT:g}/{fmt(IN_IT, 1)} = {fmt(TC_IT / IN_IT, 4)}; "
      f"20 kV: {TC_JT:g}/{fmt(IN_JT, 1)} = {fmt(TC_JT / IN_JT, 4)}")
verifica("produsul factorilor = raportul curenților nominali ai TC raportat la n", (TC_IT / IN_IT) / (TC_JT / IN_JT),
         TC_IT / TC_JT * n_T)
cazuri = [("P1", "3f", "defect trifazat în P1 (20 kV, exterior)"),
          ("B", "1f", "defect monofazat pe bara B de 110 kV (exterior)"),
          ("P1", "1f", "defect monofazat în P1 (20 kV, neutru prin rezistor, exterior)")]
for bara, tip, descriere in cazuri:
    I_IT, I_JT, _ = curenti_T1(r, bara, tip)
    S_IT, S_JT, (I0, I1, I2) = curenti_T1_secvente(r, bara, tip)
    Id, Ib, c_IT, c_JT = marimi_releu(I_IT, I_JT)
    Id_s, Ib_s, _, _ = marimi_releu(S_IT, S_JT)
    Id_fara, Ib_fara, _, _ = marimi_releu(I_IT, I_JT, elimina_I0=False)
    print(f"  {descriere}:")
    print(f"    110 kV: |I| = {', '.join(fmt(abs(x), 1) for x in I_IT)} A (I0 = {fmt(abs(I0), 1)} A); "
          f"20 kV: |I| = {', '.join(fmt(abs(x), 1) for x in I_JT)} A")
    print(f"    secundar: {', '.join(fmt(abs(x) / TC_IT, 3) for x in I_IT)} A și "
          f"{', '.join(fmt(abs(x) / TC_JT, 3) for x in I_JT)} A")
    print(f"    după adaptare și compensare: Id = {', '.join(fmt(x, 3) for x in Id)}·In; "
          f"Ib = {', '.join(fmt(x, 3) for x in Ib)}·In")
    print(f"    fără eliminarea homopolarei: Id = {', '.join(fmt(x, 3) for x in Id_fara)}·In")
    verifica(f"{bara} {tip}: curenții de 20 kV – teoria YNd11 vs coordonate de fază", S_JT, I_JT, rtol=0,
             atol=1e-3 * max(1, np.max(np.abs(I_JT))))
    verifica(f"{bara} {tip}: Ib din secvențe vs din fază", Ib_s, Ib, rtol=1e-4, atol=1e-6)
    verifica_adevarat(f"{bara} {tip}: Id < 1 % din In (cu eliminarea homopolarei)", np.max(Id) < 0.01)
    if tip == "1f" and bara == "B":
        verifica("Id fără eliminare = |I0|/In(110 kV) pe fiecare fază", Id_fara, np.full(3, abs(I0) / IN_IT),
                 rtol=1e-4)
        verifica_adevarat("fără eliminarea homopolarei protecția ar acționa (Id > prag)",
                          np.all(Id_fara > prag_diferential(Ib_fara)))

print("\nProblema 4.2 – comutatorul de ploturi în poziție extremă (110 kV ± 10 %)")
Ib_puncte = []
for t in (1.10, 0.90):
    rt = retea_referinta(cu_capacitati=False)
    rt.element("T1")["U1"] = d["U110"] * t        # raportul real; impedanța în Ω pe 110 kV păstrată
    for bara in ("P1", "B2"):
        I_IT, I_JT, _ = curenti_T1(rt, bara, "3f")
        Id, Ib, _, _ = marimi_releu(I_IT, I_JT)     # releul este adaptat pentru raportul nominal
        raport = Id[0] / Ib[0]
        raport_teorie = abs(1 - 1 / t) / ((1 + 1 / t) / 2)
        Ib_puncte.append((t, bara, Ib[0], Id[0]))
        print(f"  plot {'+' if t > 1 else '−'}10 %, defect trifazat în {bara}: Ib = {fmt(Ib[0], 3)}·In, "
              f"Id = {fmt(Id[0], 3)}·In, Id/Ib = {fmt(raport, 4)} (teorie |1 − 1/t|/((1 + 1/t)/2) = {fmt(raport_teorie, 4)});"
              f" prag = {fmt(float(prag_diferential(Ib[0])), 3)}·In")
        verifica(f"Id/Ib la plotul {t:g}, defect în {bara}: rețea vs teorie", raport, raport_teorie, rtol=1e-4)
        verifica_adevarat("punctul de funcționare rămâne sub caracteristică", Id[0] < prag_diferential(Ib[0]))
# Cel mai defavorabil caz: plot extrem și erori opuse de 5 % ale TC (eroarea compusă a clasei 5P)
eps = 0.05
pire = []
for t in (1.10, 0.90):
    for s in (+1, -1):
        iIT = (1 / t) * (1 + s * eps)
        iJT = 1 * (1 - s * eps)
        pire.append(abs(iIT - iJT) / ((iIT + iJT) / 2))
pire_max = max(pire)
print(f"  cu erori opuse de ±5 % ale TC: Id/Ib maxim = {fmt(pire_max, 4)} (panta k1 = {fmt(K1, 2)}, "
      f"rezervă {fmt(K1 / pire_max, 2)})")
verifica_adevarat("panta k1 acoperă plotul extrem și erorile TC", pire_max < K1)
# a doua cale: căutare numerică pe o grilă de erori și ploturi
grila = [abs((1 / t) * (1 + e1) - (1 + e2)) / (((1 / t) * (1 + e1) + (1 + e2)) / 2)
         for t in np.linspace(0.9, 1.1, 41) for e1 in np.linspace(-eps, eps, 21) for e2 in np.linspace(-eps, eps, 21)]
verifica("maximul Id/Ib: analiza cazurilor extreme vs grilă", pire_max, max(grila), rtol=1e-6)

print("\nProblema 4.3 – defecte interioare zonei protejate")
# (a) defect trifazat la bornele de 20 kV ale lui T1, între transformator și TC de 20 kV:
#     curentul vine numai dinspre 110 kV; TC de 20 kV nu văd curent (pe 20 kV nu există surse)
I_IT, _, _ = curenti_T1(r, "B2", "3f")
Id, Ib, _, _ = marimi_releu(I_IT, np.zeros(3))
Ik_B2 = abs(r.scurtcircuit_secvente("B2", "3f")["I_faza"][0])
prag = float(prag_diferential(Ib[0]))
print(f"  (a) trifazat la bornele de 20 kV: Id = {fmt(Id[0], 3)}·In, Ib = {fmt(Ib[0], 3)}·In, prag = {fmt(prag, 3)}·In "
      f"→ rezervă {fmt(Id[0] / prag, 2)}; treapta nefrânată ({fmt(IDIFF_NEFRANAT, 0)}·In) nu este atinsă")
verifica("Id = I\"k3(B2)/In(20 kV) (capitolul 1)", Id[0], Ik_B2 / IN_JT)
verifica_adevarat("acționează treapta frânată", Id[0] > prag and Id[0] < IDIFF_NEFRANAT)
# (b) defect trifazat la bornele de 110 kV, în zona protejată: tot curentul de defect din rețeaua de 110 kV
pB = r.rezolva_faze(defect_faze("B", "3f"))
I_IT_b = -(r.curenti_ramura_faze(pB, "L1", 2) + r.curenti_ramura_faze(pB, "L2", 1))   # curentul spre defect
Id_b, Ib_b, _, _ = marimi_releu(I_IT_b, np.zeros(3))
Ik_B = abs(r.scurtcircuit_secvente("B", "3f")["I_faza"][0])
print(f"  (b) trifazat la bornele de 110 kV: Id = {fmt(Id_b[0], 2)}·In → treapta nefrânată (> {fmt(IDIFF_NEFRANAT, 0)}·In)")
verifica("Id = I\"k3(B)/In(110 kV) (capitolul 1)", Id_b[0], Ik_B / IN_IT)
verifica_adevarat("acționează treapta nefrânată", Id_b[0] > IDIFF_NEFRANAT)
# (c) punere la pământ la bornele de 20 kV (în zonă), rețea cu rezistor de 300 A:
#     componentele directă și inversă vin prin T1, componenta homopolară vine de la BPN, prin TC de 20 kV
for c_fact, eticheta in ((1.10, "c = 1,1"), (C_MIN, "c = 1,0")):
    rr = retea_referinta("rezistor", c=c_fact, cu_capacitati=False)
    I_IT_c, _, pc = curenti_T1(rr, "B2", "1f")
    I_BPN = -rr.curenti_ramura_faze(pc, "BPN", 1)          # curentul care iese din BPN spre bară
    I_TC_JT = I_BPN                                       # trece prin TC de 20 kV spre transformator
    If = abs(rr.curent_defect_faze(pc)[0])
    Id_cu, Ib_cu, _, _ = marimi_releu(I_IT_c, I_TC_JT)
    Id_fara, _, _, _ = marimi_releu(I_IT_c, I_TC_JT, I0_pe_JT=True)
    print(f"  (c) punere la pământ la bornele de 20 kV, {eticheta}: I_defect = {fmt(If, 1)} A = {fmt(If / IN_JT, 3)}·In;"
          f" Id (faza defectă) = {fmt(Id_cu[0], 3)}·In dacă homopolara de pe 20 kV este păstrată,"
          f" {fmt(Id_fara[0], 3)}·In dacă este eliminată (prag {fmt(IDIFF_MIN, 2)}·In)")
    verifica("Id cu homopolara păstrată = I_defect/In", Id_cu[0], If / IN_JT, rtol=1e-3)
    verifica("Id fără homopolară = (2/3)·I_defect/In (calea componentelor simetrice)", Id_fara[0], 2 / 3 * If / IN_JT,
             rtol=1e-3)
verifica_adevarat("la c = 1,0 și homopolara eliminată, defectul nu este sesizat (de aici protecția de neutru)",
                  Id_fara[0] < IDIFF_MIN)

print("\nProblema 4.4 – curentul de magnetizare la conectarea lui T1 și blocarea la armonica a doua")
psi_n, Lm, L_aer = parametri_inrush()
p = INRUSH
psi_s = p["k_sat"] * psi_n
i_s = psi_s / Lm
Lr = p["X_retea"] / W0
print(f"  ψn = Vm/ω = {fmt(psi_n, 1)} V·s; Lm = {fmt(Lm, 0)} H; L(saturat) = {fmt(L_aer, 4)} H; L(rețea) = {fmt(Lr, 4)} H")
# Calea 1: vârful fără rezistențe, din conservarea fluxului: Lr·i + ψ = ψrem + 2ψn la ωt = π
i_varf_R0 = (p["psi_rem"] * psi_n + 2 * psi_n - psi_s + i_s * L_aer) / (Lr + L_aer)
p0 = dict(p, R_inf=0.0, R_retea=0.0)
t0, i0, _ = simuleaza_inrush(0.025, 2e-6, p0)
print(f"  fără rezistențe: vârf analitic = {fmt(i_varf_R0, 1)} A; simulare = {fmt(i0.max(), 1)} A")
verifica("vârful curentului (R = 0): analitic vs simulare Runge–Kutta", i_varf_R0, i0.max(), rtol=2e-3)
t, i, psi = simuleaza_inrush(0.4, 2e-6)
In_varf = np.sqrt(2) * IN_IT
N = int(round(0.02 / (t[1] - t[0])))
h = armonici_dft(i[:N], 5)
print(f"  cu rezistențe: vârf = {fmt(i.max(), 1)} A = {fmt(i.max() / In_varf, 2)}·(√2·In); în prima perioadă: "
      f"componenta fundamentală = {fmt(h[1] / In_varf, 3)}·In (valoare efectivă), armonica 2 = "
      f"{fmt(100 * h[2] / h[1], 1)} %, componenta continuă = {fmt(h[0] / In_varf * np.sqrt(2), 3)}·In")
tt, r2, i1 = raport_armonica2_alunecator(t, i)
print(f"  raportul I(2f)/I(f) pe fereastră alunecătoare: minim {fmt(100 * r2.min(), 1)} %, la 0,4 s {fmt(100 * r2[-1], 1)} %;"
      f" fundamentala maximă {fmt(i1.max() / In_varf, 3)}·In")
verifica_adevarat("curentul de conectare depășește pragul minim (fără blocare ar acționa)", h[1] / In_varf > IDIFF_MIN)
verifica_adevarat("fundamentala curentului de conectare rămâne sub treapta nefrânată", i1.max() / In_varf < IDIFF_NEFRANAT)
verifica_adevarat(f"armonica a doua rămâne peste pragul de blocare de {ARMONICA2:.0%}", r2.min() > ARMONICA2)
# Verificarea metodei de calcul al armonicilor pe un impuls sinusoidal trunchiat (serie Fourier analitică)
for alfa_g in (60, 90, 120):
    alfa = np.radians(alfa_g)
    Nn = 3600
    th = 2 * np.pi * np.arange(Nn) / Nn - np.pi
    x = np.where(np.abs(th) <= alfa, np.cos(th) - np.cos(alfa), 0.0)
    num = armonici_dft(x, 5)
    an = sinus_trunchiat_analitic(alfa, 5)
    print(f"  impuls cu unghi de conducție {2 * alfa_g}°: I2/I1 analitic = {fmt(100 * an[2] / an[1], 2)} %, "
          f"TFD = {fmt(100 * num[2] / num[1], 2)} %; I0/I1 = {fmt(an[0] / an[1], 3)}")
    verifica(f"coeficienții Fourier, impuls {2 * alfa_g}°: analitic vs TFD", num, an, rtol=0, atol=2e-4)
# Curentul de defect interior cu componentă aperiodică maximă: armonica 2 în prima perioadă
raport_def = {}
for loc, Zth in (("20 kV (bornele de JT)", r.scurtcircuit_secvente("B2", "3f")["Zth"][1]),
                 ("110 kV (bornele de IT)", r.scurtcircuit_secvente("B", "3f")["Zth"][1])):
    T = Zth.imag / (W0 * Zth.real)
    tt_ = np.arange(N) * (t[1] - t[0])
    x = np.exp(-tt_ / T) - np.cos(W0 * tt_)
    hh = armonici_dft(x, 2)
    raport_def[loc[:2]] = hh[2] / hh[1]
    print(f"  defect interior la {loc}: R/X = {fmt(Zth.real / Zth.imag, 4)}, armonica 2 în prima perioadă = "
          f"{fmt(100 * hh[2] / hh[1], 1)} %")
    if loc.startswith("20"):
        verifica_adevarat("defectul de la bornele de 20 kV nu este blocat", hh[2] / hh[1] < ARMONICA2)
    else:
        verifica_adevarat("la 110 kV raportul depășește pragul în prima perioadă – acționează treapta nefrânată",
                          hh[2] / hh[1] > ARMONICA2 and Id_b[0] > IDIFF_NEFRANAT)
# Sensibilitatea la fluxul remanent și la cotul de saturație
print("  sensibilitatea (simulări de 0,1 s):")
for nume, cheie, valori in (("flux remanent", "psi_rem", (0.0, 0.4, 0.8)), ("cot de saturație", "k_sat", (1.1, 1.2, 1.3))):
    for v in valori:
        pv = dict(INRUSH)
        pv[cheie] = v
        tv, iv, _ = simuleaza_inrush(0.1, 4e-6, pv)
        _, r2v, _ = raport_armonica2_alunecator(tv, iv)
        print(f"    {nume} = {fmt(v, 1)}: vârf = {fmt(iv.max() / In_varf, 2)}·(√2·In), armonica 2 minimă = "
              f"{fmt(100 * r2v.min(), 1)} %")

print("\nProblema 4.5 – protecția diferențială de bare de impedanță mare (bara B de 110 kV)")
# curentul maxim care traversează un singur TC la un defect exterior imediat după el
pB = r.rezolva_faze(defect_faze("B", "3f"))
I_dinspre_A = abs(r.curenti_ramura_faze(pB, "L1", 2)[0])
I_dinspre_C = abs(r.curenti_ramura_faze(pB, "L2", 1)[0])
I_trec = max(I_dinspre_A, I_dinspre_C)
nTC, Rct, RL = 1200.0, 4.0, 1.5
I_sec = I_trec / nTC
Vs_min = I_sec * (Rct + 2 * RL)
Vs = np.ceil(1.2 * Vs_min / 5) * 5
I_R = 0.1                       # curentul de acționare al releului [A]
R_R = Vs / I_R
print(f"  aporturi la defect pe bara B: dinspre A {fmt(I_dinspre_A, 0)} A, dinspre C {fmt(I_dinspre_C, 0)} A → "
      f"curentul maxim printr-un TC = {fmt(I_trec, 0)} A ({fmt(I_sec, 3)} A secundar)")
print(f"  Vs ≥ I·(Rct + 2RL) = {fmt(I_sec, 3)}·({fmt(Rct, 1)} + 2·{fmt(RL, 1)}) = {fmt(Vs_min, 1)} V → ales {fmt(Vs, 0)} V "
      f"(≥ 1,2·Vs_min, rotunjit la 5 V); R releu = Vs/I_R = {fmt(R_R, 0)} Ω")
# Calea 2: circuitul cu un TC complet saturat (numai Rct), celelalte TC surse de curent ideale
G = np.array([[1 / R_R + 1 / (Rct + 2 * RL)]])
V = np.linalg.solve(G, np.array([I_sec]))[0]
print(f"  tensiunea pe releu în circuitul cu TC saturat: {fmt(V, 2)} V (formula: {fmt(Vs_min, 2)} V, "
      f"cu {fmt(100 * (1 - V / Vs_min), 1)} % mai mare)")
verifica("circuit vs formula corectată cu divizorul R_R/(R_R + Rct + 2RL)", V,
         Vs_min * R_R / (R_R + Rct + 2 * RL), rtol=1e-9)
verifica_adevarat("formula Vs ≥ I·(Rct + 2RL) este acoperitoare (V ≤ Vs_min)", V <= Vs_min + 1e-9)
verifica_adevarat("releul rămâne stabil la defectul exterior", V < Vs)
Ie_Vs = 0.03                    # curentul de magnetizare al unui TC la tensiunea Vs (curba TC)
n_TC = 3
I_op = nTC * (I_R + n_TC * Ie_Vs)
I1f_min = abs(retea_referinta(c=C_MIN, cu_capacitati=False).scurtcircuit_secvente("B", "1f")["I_faza"][0])
print(f"  curentul primar minim de acționare = {fmt(nTC, 0)}·({fmt(I_R, 2)} + {n_TC}·{fmt(Ie_Vs, 2)}) = {fmt(I_op, 0)} A;"
      f" defectul monofazat minim pe bară = {fmt(I1f_min, 0)} A (sensibilitate {fmt(I1f_min / I_op, 1)})")
verifica_adevarat("sensibilitatea la defectul interior minim ≥ 2", I1f_min / I_op >= 2)

print("\nLucrarea de laborator L3 – valorile așteptate la încercarea prin injecție secundară")
from modele import sistem_direct  # noqa: E402
# (1) pragul minim, injecție monofazată pe o singură parte
Isec_IT = IDIFF_MIN * SQRT3 * IN_IT / TC_IT      # pe 110 kV: compensarea împarte curentul la √3
Isec_JT = IDIFF_MIN * IN_JT / TC_JT
Id1, _, _, _ = marimi_releu(np.array([Isec_IT * TC_IT, 0, 0]), np.zeros(3))
Id2, _, _, _ = marimi_releu(np.zeros(3), np.array([Isec_JT * TC_JT, 0, 0]))
print(f"  pragul minim, injecție pe faza a: 110 kV {fmt(Isec_IT, 4)} A (Id apare pe fazele a și c), 20 kV {fmt(Isec_JT, 4)} A")
verifica("prag 110 kV: Id calculat de modelul releului = 0,30", np.max(Id1), IDIFF_MIN)
verifica("prag 20 kV: Id calculat de modelul releului = 0,30", np.max(Id2), IDIFF_MIN)
# (2) stabilitate: curenți trifazați egali, cu defazajul transformatorului (20 kV la 180° + 30° față de 110 kV)
k = 1.0
I_IT_t = sistem_direct(k * IN_IT)
I_JT_t = sistem_direct(k * IN_JT) * np.exp(1j * np.radians(180 + 30))
Idt, Ibt, _, _ = marimi_releu(I_IT_t, I_JT_t)
print(f"  stabilitate: 110 kV {fmt(k * IN_IT / TC_IT, 4)} A ∠0°, 20 kV {fmt(k * IN_JT / TC_JT, 4)} A ∠210° → "
      f"Id = {fmt(np.max(Idt), 4)}·In, Ib = {fmt(Ibt[0], 3)}·In")
verifica_adevarat("injecția de stabilitate dă Id ≈ 0", np.max(Idt) < 1e-9)
# (3) puncte pe caracteristică: 20 kV fix (b), se crește curentul de 110 kV (a) până la acționare
from scipy.optimize import brentq  # noqa: E402
lab_puncte = []
for b in (1.0, 2.0, 4.0, 6.0):
    a = brentq(lambda a: (a - b) - float(prag_diferential((a + b) / 2)), b, 10 * b + 5)
    I_IT_p = sistem_direct(a * IN_IT)
    I_JT_p = sistem_direct(b * IN_JT) * np.exp(1j * np.radians(210))
    Idp, Ibp, _, _ = marimi_releu(I_IT_p, I_JT_p)
    lab_puncte.append((b, a, Ibp[0], Idp[0]))
    print(f"  20 kV {fmt(b * IN_JT / TC_JT, 3)} A ({fmt(b, 1)}·In) → acționare la 110 kV {fmt(a * IN_IT / TC_IT, 3)} A "
          f"({fmt(a, 3)}·In): Ib = {fmt(Ibp[0], 3)}·In, Id = {fmt(Idp[0], 3)}·In")
    verifica(f"punctul de acționare pentru b = {b:g}: Id = pragul la Ib", Idp[0], float(prag_diferential(Ibp[0])), rtol=1e-6)
