"""Capitolul 9 – Automatizarea stațiilor: rezolvarea și verificarea problemelor."""

import numpy as np
from modele import SQRT3, DATE, fmt, verifica, verifica_adevarat, retea_referinta, timp_invers
from calcul_cap09 import (SUPLIMENT_FIR, unghi_din_timp, tve_faza, tve_dft, debit_sv, simuleaza_port,
                          momente_goose, sosire_dupa_pierderi, simuleaza_pierderi, detectie_pierdere_legatura,
                          indisponibilitate, intervale_defect, intersectie, reuniune_lungime)

f = 50.0
rng = np.random.default_rng(2026)

print("Problema 9.1 – eroarea de fază și TVE produse de o eroare de sincronizare a timpului")
for dt in (1e-6, 10e-6, 100e-6, 1e-3):
    th = unghi_din_timp(dt, f)
    tve = tve_faza(th)
    # calea 2: fazorul estimat cu TFD dintr-un semnal eșantionat cu ceasul decalat (4000 și 4800 eșantioane/s)
    for fs in (4000.0, 4800.0):
        tve_n, th_n = tve_dft(dt, f, fs)
        verifica(f"Δt = {dt * 1e6:g} µs, fs = {fs:g}/s: TVE formulă vs TFD", tve, tve_n, rtol=1e-6)
        verifica(f"Δt = {dt * 1e6:g} µs, fs = {fs:g}/s: unghi formulă vs TFD", th, th_n, rtol=1e-6)
    print(f"  Δt = {fmt(dt * 1e6, 0)} µs: eroarea de fază = {fmt(np.degrees(th), 4)}°, TVE = {fmt(100 * tve, 4)} %")
# Eroarea de timp admisibilă pentru un prag TVE dat (exemplu: 1 %)
tve_prag = 0.01
th_max = 2 * np.arcsin(tve_prag / 2)
dt_max = th_max / (2 * np.pi * f)
print(f"  pentru TVE ≤ 1 % (numai eroare de fază): θ ≤ {fmt(np.degrees(th_max), 3)}° → Δt ≤ {fmt(dt_max * 1e6, 2)} µs")
verifica("TVE la Δt_max = 1 % (calea TFD)", tve_dft(dt_max, f, 4000.0)[0], tve_prag, rtol=1e-6)
# Protecția diferențială de linie: eșantioanele celor două capete decalate cu Δt
I = 1000.0      # curentul care tranzitează linia [A]
for dt in (10e-6, 100e-6, 1e-3):
    Id_formula = 2 * I * np.sin(np.pi * f * dt)
    # calea 2: fazorii celor două capete calculați cu TFD; capătul B are ceasul decalat cu Δt
    _, thA = tve_dft(0.0, f, 4000.0, amplitudine=I)
    XA = I * np.exp(1j * (0.3 + thA))
    tveB, thB = tve_dft(dt, f, 4000.0, amplitudine=I)
    XB = I * np.exp(1j * (0.3 + thB))
    Id_num = abs(XA - XB)          # curentul intră la A și iese la B: Id = |I_A − I_B|
    print(f"  diferențiala de linie, I = {fmt(I, 0)} A, Δt = {fmt(dt * 1e6, 0)} µs: curent diferențial fals = "
          f"{fmt(Id_formula, 2)} A ({fmt(100 * Id_formula / I, 3)} % din I)")
    verifica(f"Id fals la Δt = {dt * 1e6:g} µs: formulă vs fazori TFD", Id_formula, Id_num, rtol=1e-6)
dt_dif = np.arcsin(0.02 / 2) / (np.pi * f)
print(f"  pentru un curent diferențial fals ≤ 2 % din I este nevoie de Δt ≤ {fmt(dt_dif * 1e6, 1)} µs")
verifica("Δt pentru 2 %: cele două formule (TVE și Id) coincid", dt_dif, 2 * np.arcsin(0.01) / (2 * np.pi * f))

print("\nProblema 9.2 – traficul de valori eșantionate pe magistrala de proces (100 Mbit/s)")
C = 100e6
cazuri = {
    "IEC 61850-9-2LE": dict(fs=4000.0, asdu=1, L=130),
    "IEC 61869-9 (4800/s)": dict(fs=4800.0, asdu=2, L=210),
}
rez92 = {}
for nume, c in cazuri.items():
    cadre, debit = debit_sv(c["fs"], c["asdu"], c["L"])
    spc = c["fs"] / f
    # verificare aritmetică: numărarea biților pe fir într-o secundă (preambul + cadru + pauză), cadru cu cadru
    biti = 0
    for _ in range(int(cadre)):
        biti += 8 * (8 + c["L"] + 12)
    verifica(f"{nume}: debit formulă vs numărare pe biți (verificare aritmetică)", debit, biti)
    rez92[nume] = (cadre, debit)
    print(f"  {nume}: {fmt(spc, 0)} eșantioane/ciclu, pas {fmt(1e6 / c['fs'], 2)} µs; {fmt(cadre, 0)} cadre/s × "
          f"({c['L']} + {SUPLIMENT_FIR}) octeți → {fmt(debit / 1e6, 3)} Mbit/s pe flux")
N = 8
print(f"  N = {N} unități de îmbinare pe același port:")
for nume, c in cazuri.items():
    cadre, debit = rez92[nume]
    inc = N * debit / C
    nmax = int(0.5 * C // debit)
    # calea 2: simularea pe evenimente a portului (fluxuri sincronizate = sosiri simultane)
    inc_sim, tmax_sim, t_cadru = simuleaza_port(N, cadre, c["L"], C)
    inc_rnd, tmax_rnd, _ = simuleaza_port(N, cadre, c["L"], C, decalaje=rng.random(N))
    print(f"    {nume}: încărcare {fmt(100 * inc, 1)} % (simulare {fmt(100 * inc_sim, 1)} %); "
          f"timp pe fir al unui cadru {fmt(t_cadru * 1e6, 1)} µs; întârziere maximă în coadă (inclusiv transmisia "
          f"cadrului propriu) {fmt(tmax_sim * 1e6, 1)} µs, față de intervalul dintre cadre {fmt(1e6 / cadre, 1)} µs "
          f"(fluxuri decalate aleator: {fmt(tmax_rnd * 1e6, 1)} µs); cel mult {nmax} fluxuri pentru încărcare ≤ 50 %")
    verifica(f"{nume}: încărcarea analitică vs simulare", inc, inc_sim, rtol=2e-3)
    verifica(f"{nume}: întârzierea maximă = N × timpul unui cadru", tmax_sim, N * t_cadru)
    verifica_adevarat(f"{nume}: coada se golește înainte de următorul set de cadre", N * t_cadru < 1 / cadre)
    verifica_adevarat(f"{nume}: întârzierea cu fluxuri decalate nu depășește cazul sincron", tmax_rnd <= tmax_sim + 1e-12)

print("\nProblema 9.3 – blocarea protecției barelor de 20 kV prin mesaje GOOSE (problema 3.3)")
t_porn = 0.020        # pornirea treptei de curent a releului de fider R1 după apariția defectului
t_R0 = 0.100          # momentul în care treapta rapidă a lui R0 ar comanda declanșarea (problema 3.3)
t_pub, t_sub = 0.001, 0.001     # prelucrarea în publicator și în abonat
t_ciclu = 0.001       # ciclul logicii lui R0 (întârzierea maximă până la aplicarea blocării)
L_goose = 150         # lungimea cadrului GOOSE [octeți]
hop = 3               # R1 → comutator 1 → comutator 2 → R0: cadrul e transmis de 3 ori (memorare și retransmitere)
t_comutator = 5e-6    # latența internă a unui comutator
t_fir = (L_goose + SUPLIMENT_FIR) * 8 / C
t_retea = hop * t_fir + (hop - 1) * t_comutator
t_transfer = t_pub + t_retea + t_sub
t_blocare = t_porn + t_transfer + t_ciclu
print(f"  rețeaua: {hop} × {fmt(t_fir * 1e6, 1)} µs + {hop - 1} × {fmt(t_comutator * 1e6, 0)} µs = {fmt(t_retea * 1e6, 1)} µs")
print(f"  timpul de transfer (publicator → abonat) = {fmt(t_transfer * 1e3, 3)} ms (clasa TT6: ≤ 3 ms)")
print(f"  blocarea devine efectivă la {fmt(t_blocare * 1e3, 2)} ms după apariția defectului; R0 ar declanșa la "
      f"{fmt(t_R0 * 1e3, 0)} ms → rezervă {fmt((t_R0 - t_blocare) * 1e3, 2)} ms")
verifica_adevarat("timpul de transfer ≤ 3 ms (TT6)", t_transfer <= 0.003)
# calea 2: simulare pe evenimente a lanțului (evenimente în ordine cronologică)
evenimente = [("defect", 0.0)]
evenimente.append(("pornire R1", evenimente[-1][1] + t_porn))
evenimente.append(("cadru GOOSE emis", evenimente[-1][1] + t_pub))
t = evenimente[-1][1]
for k in range(hop):
    t += t_fir                   # cadrul este recepționat complet de nodul următor
    if k < hop - 1:
        t += t_comutator         # comutatorul îl retransmite
evenimente.append(("cadru recepționat de R0", t))
evenimente.append(("informație disponibilă în R0", t + t_sub))
evenimente.append(("blocare aplicată (ciclul logicii)", t + t_sub + t_ciclu))
for nume, tt in evenimente:
    print(f"    {fmt(tt * 1e3, 4)} ms – {nume}")
verifica("momentul blocării: sumă analitică vs simulare pe evenimente", t_blocare, evenimente[-1][1], rtol=1e-12)
# Câte mesaje consecutive se pot pierde? (programul de retransmisie: 2 ms, apoi dublare până la 1 s)
termen = t_R0 - t_porn - t_pub - t_retea - t_sub - t_ciclu
emis = momente_goose()
k_max = int(np.max(np.nonzero(emis <= termen)[0]))
k_formula = int(np.floor(np.log2(1 + termen / 0.002)))
print(f"  momentele mesajelor după eveniment [ms]: {', '.join(fmt(x * 1e3, 0) for x in emis[:9])} …")
print(f"  se pot pierde cel mult {k_max} mesaje consecutive (al {k_max + 1}-lea sosește la "
      f"{fmt((t_porn + sosire_dupa_pierderi(k_max, t_pub, t_retea, t_sub) + t_ciclu) * 1e3, 2)} ms)")
verifica("k_max: căutare în programul de mesaje vs formula 2^k − 1 ≤ termen/T_min", k_max, k_formula)
# Monte Carlo cu pierderi independente (rețea foarte perturbată, p = 0,3, pentru a verifica formulele)
p = 0.3
n_inc = 1_000_000
sos = t_porn + simuleaza_pierderi(p, t_pub, t_retea, t_sub, n_inc, rng) + t_ciclu
P_intarziere = np.mean(sos > t_R0)
P_teorie = p ** (k_max + 1)
E_teorie = t_porn + t_pub + t_retea + t_sub + t_ciclu + sum(p**k * (1 - p) * emis[k] for k in range(len(emis)))
print(f"  p = {fmt(p, 1)}: P(blocare întârziată) = p^{k_max + 1} = {P_teorie:.2e} (Monte Carlo {P_intarziere:.2e}); "
      f"momentul mediu al blocării {fmt(E_teorie * 1e3, 3)} ms (Monte Carlo {fmt(np.mean(sos) * 1e3, 3)} ms)")
verifica("P(întârziere): analitic vs Monte Carlo", P_intarziere, P_teorie, rtol=0,
         atol=5 * np.sqrt(P_teorie * (1 - P_teorie) / n_inc))
verifica("momentul mediu: analitic vs Monte Carlo", np.mean(sos), E_teorie, rtol=2e-3)
# media condiționată: numai încercările în care blocarea sosește înainte ca R0 să declanșeze
baza = t_porn + t_pub + t_retea + t_sub + t_ciclu
E_cond = sum(p**k * (1 - p) * (baza + emis[k]) for k in range(k_max + 1)) / (1 - p ** (k_max + 1))
E_cond_mc = np.mean(sos[sos <= t_R0])
print(f"  media necondiționată (inclusiv sosirile după declanșarea lui R0) = {fmt(E_teorie * 1e3, 3)} ms; "
      f"media condiționată de sosirea la timp = {fmt(E_cond * 1e3, 3)} ms (Monte Carlo {fmt(E_cond_mc * 1e3, 3)} ms)")
verifica("momentul mediu condiționat: analitic vs Monte Carlo", E_cond_mc, E_cond, rtol=2e-3)
print(f"  pentru p = 10⁻³: P(blocare întârziată) = {0.001 ** (k_max + 1):.0e}")
# Supravegherea legăturii: intervalul de „bătaie de inimă” T0 = 1 s, TAL = 2 s (exemplu)
T0, TAL = 1.0, 2.0
t_cad = rng.uniform(0, 1000.0, 200_000)
det = detectie_pierdere_legatura(t_cad, T0, TAL)
# calea 2: simulare explicită – ultimul mesaj primit înainte de cădere, apoi primul moment fără mesaje timp de TAL
det2 = np.empty(2000)
for i, tc in enumerate(t_cad[:2000]):
    mesaje = np.arange(0.0, tc + 5 * T0, T0)
    ultim = mesaje[mesaje <= tc][-1]
    det2[i] = ultim + TAL - tc
verifica("întârzierea detecției: formulă vs simulare explicită", det[:2000], det2, rtol=1e-9)
print(f"  pierderea legăturii este detectată după {fmt(det.min(), 3)} … {fmt(det.max(), 3)} s "
      f"(medie {fmt(det.mean(), 3)} s; teorie: între TAL − T0 = {fmt(TAL - T0, 1)} s și TAL = {fmt(TAL, 1)} s, medie "
      f"{fmt(TAL - T0 / 2, 1)} s)")
verifica("întârzierea medie a detecției = TAL − T0/2", det.mean(), TAL - T0 / 2, rtol=5e-3)
verifica_adevarat("detecția este între TAL − T0 și TAL", det.min() >= TAL - T0 - 1e-12 and det.max() <= TAL + 1e-12)
# Ce se pierde dacă blocarea nu e disponibilă: R0 revine la treapta temporizată (problema 3.3)
r = retea_referinta(cu_capacitati=False)
Ik_B2 = abs(r.scurtcircuit_secvente("B2", "3f")["I_faza"][0])
# reglajele lui R0 se iau din rezolvarea capitolului 3 (aceeași sursă de adevăr)
import contextlib, io, runpy  # noqa: E401,E402
from pathlib import Path  # noqa: E402
with contextlib.redirect_stdout(io.StringIO()):
    _R0 = runpy.run_path(str(Path(__file__).with_name("probleme_cap03.py")))["relee"]["R0"]
t_IDMT = float(timp_invers(Ik_B2, _R0["Is"], _R0["TMS"]))
print(f"  dacă treapta rapidă e scoasă din funcțiune la pierderea legăturii, defectul de bară e eliminat de "
      f"treapta temporizată: {fmt(t_IDMT, 3)} s + 0,06 s = {fmt(t_IDMT + 0.06, 3)} s (față de 0,16 s)")

print("\nProblema 9.4 – disponibilitatea unei căi de comunicație simple și a uneia dublate")
ore_an = 8760.0
MTBF, MTTR = 10 * ore_an, 48.0          # o cale: comutator + fibre + porturi
MTBF_cc, MTTR_cc = 30 * ore_an, 8.0     # cauza comună: sursa de alimentare comună a comutatoarelor
U1 = indisponibilitate(MTBF, MTTR)
U2 = U1**2
Ucc = indisponibilitate(MTBF_cc, MTTR_cc)
Usist = 1 - (1 - Ucc) * (1 - U2)
for nume, U in (("cale simplă", U1), ("două căi independente", U2), ("două căi + sursă comună", Usist)):
    print(f"  {nume}: U = {U:.3e} → {fmt(U * ore_an * 60, 2)} min/an ({fmt(U * ore_an * 3600, 1)} s/an)")
# calea 2: Monte Carlo cu procese de reînnoire alternante (timpi exponențiali)
T = 5e6 * ore_an
a0, a1 = intervale_defect(MTBF, MTTR, T, rng)
b0, b1 = intervale_defect(MTBF, MTTR, T, rng)
c0, c1 = intervale_defect(MTBF_cc, MTTR_cc, T, rng)
U1_mc = np.sum(a1 - a0) / T
i0, i1 = intersectie(a0, a1, b0, b1)
U2_mc = np.sum(i1 - i0) / T
Usist_mc = reuniune_lungime(i0, i1, c0, c1) / T
print(f"  Monte Carlo pe {T / ore_an:.0e} ani: cale simplă {U1_mc:.3e}; două căi {U2_mc:.3e} "
      f"({len(i0)} suprapuneri de defecte); cu sursă comună {Usist_mc:.3e}")
verifica("U cale simplă: analitic vs Monte Carlo", U1_mc, U1, rtol=0.02)
verifica("U două căi: analitic vs Monte Carlo", U2_mc, U2, rtol=0.2)
verifica("U cu sursă comună: analitic vs Monte Carlo", Usist_mc, Usist, rtol=0.05)
verifica_adevarat("cauza comună domină indisponibilitatea sistemului dublat", Ucc > 10 * U2)
print(f"  cale simplă: {fmt(U1 * ore_an, 2)} h/an; dublarea reduce U de {fmt(U1 / U2, 0)} ori (= 1/U); "
      f"sursa comună o mărește de {fmt(Usist / U2, 1)} ori; abaterea Monte Carlo la două căi: "
      f"{fmt(100 * (U2_mc / U2 - 1), 1)} %")
verifica("raportul U1/U2 = 1/U1", U1 / U2, 1 / U1)
