"""Capitolul 3 – Protecția maximală de curent: rezolvarea și verificarea problemelor."""

import numpy as np
from scipy.optimize import brentq
from modele import (SQRT3, W0, C_MAX, C_MIN, DATE, z_fider, retea_cu_bara_pe_F1, retea_fara, fmt, verifica, verifica_adevarat, retea_referinta, defect_faze,
                    timp_invers, TMS_necesar, timp_integrator, CURBE, polar)

d = DATE
DT_TREAPTA = 0.3      # treapta de timp aleasă (marja de selectivitate) între două protecții [s]
# Componentele treptei de timp (date de problemă): timpul de întrerupere al întrerupătorului din aval,
# depășirea (overshoot) releului din amonte, eroarea de timp a releelor (±5 %) și o rezervă de siguranță.
T_CB, T_OVERSHOOT, E_TIMP, T_SIGURANTA = 0.06, 0.02, 0.05, 0.05


def treapta_minima(t_jos, t_sus):
    """Cel mai defavorabil caz: releul din aval întârzie cu E·t_jos, cel din amonte grăbește cu E·t_sus.
    Diferența nominală trebuie să acopere și întreruperea, depășirea și rezerva."""
    return T_CB + T_OVERSHOOT + T_SIGURANTA + E_TIMP * (t_jos + t_sus)

print("Problema 3.1 – timpii de acționare pentru caracteristicile IEC și IEEE")
for curba in ("SI", "VI", "EI"):
    k, a, c = CURBE[curba]
    linie = []
    for G in (2, 5, 10, 20):
        t_f = float(timp_invers(G, 1.0, 0.1, curba))
        # calea 2: releul numeric cu integrator, curent constant, pas de 0,1 ms
        t_i = timp_integrator(np.full(int(t_f / 1e-4) + 50, float(G)), 1e-4, 1.0, 0.1, curba)
        verifica(f"{curba}, I = {G}·Is: formula vs integrator", t_f, t_i, rtol=0, atol=2e-4)
        linie.append(f"{G}·Is: {fmt(t_f, 3)} s")
    print(f"  {curba} (k = {k:g}, α = {a:g}), TMS = 0,1: " + "; ".join(linie))
for curba in ("MI-IEEE", "VI-IEEE", "EI-IEEE"):
    print(f"  {curba}, TMS = 1: " + "; ".join(f"{G}·Is: {fmt(float(timp_invers(G, 1.0, 1.0, curba)), 3)} s"
                                         for G in (2, 5, 10, 20)))

print("\nProblema 3.2 – coordonarea protecțiilor maximale pe fiderul F1")
r = retea_referinta(cu_capacitati=False)
KR80 = 1 + 0.004 * (80 - 20)
r_min = retea_referinta(c=C_MIN, cu_capacitati=False, kR20=KR80)
I3 = {b: abs(r.scurtcircuit_secvente(b, "3f")["I_faza"][0]) for b in ("B2", "P1", "P2")}
# Curentul minim: configurația normală și configurațiile cu o linie de 110 kV scoasă din funcțiune
configuratii = {"normală": r_min,
                "fără L1": retea_fara(["L1"], c=C_MIN, cu_capacitati=False, kR20=KR80),
                "fără L2": retea_fara(["L2"], c=C_MIN, cu_capacitati=False, kR20=KR80)}
I2min_conf = {k: {b: abs(rc.scurtcircuit_secvente(b, "2f")["I_faza"][1]) for b in ("B2", "P1", "P2")}
              for k, rc in configuratii.items()}
I2min = {b: min(I2min_conf[k][b] for k in configuratii) for b in ("B2", "P1", "P2")}
for b in I3:
    detalii = "; ".join(f"{k}: {fmt(I2min_conf[k][b], 0)} A" for k in configuratii)
    print(f"  {b}: I\"k2min = {fmt(I2min[b], 0)} A ({detalii}); I\"k3max = {fmt(I3[b], 0)} A")
    # verificare: curentul minim în configurația cea mai slabă, calculat și în coordonate de fază
    k_slab = min(configuratii, key=lambda k: I2min_conf[k][b])
    rc = configuratii[k_slab]
    pf = rc.rezolva_faze(defect_faze(b, "2f"))
    verifica(f"I\"k2min({b}), configurația {k_slab}: secvențe vs fază", I2min[b], abs(rc.curent_defect_faze(pf)[0]))
# Datele releelor: nume, sarcina maximă [A], raportul TC, curentul de pornire ales [A]
IT1n = d["ST"] / (SQRT3 * d["U20"])
relee = {
    "R3": dict(Isarc=50.0, TC=100, Is=80.0),
    "R2": dict(Isarc=110.0, TC=200, Is=160.0),
    "R1": dict(Isarc=180.0, TC=400, Is=300.0),
    "R0": dict(Isarc=IT1n, TC=1000, Is=1000.0),
}
for nume, rl in relee.items():
    minim = 1.3 * rl["Isarc"] / 0.95
    print(f"  {nume}: I_sarcină,max = {fmt(rl['Isarc'], 0)} A → Is ≥ 1,3·I/0,95 = {fmt(minim, 0)} A; ales Is = "
          f"{fmt(rl['Is'], 0)} A ({fmt(rl['Is'] / rl['TC'], 2)}·In TC, TC {rl['TC']}/1 A)")
    verifica_adevarat(f"{nume}: curentul de pornire depășește sarcina maximă cu marjă", rl["Is"] >= minim)
# Sensibilitatea: zona proprie (≥ 1,5) și zona de rezervă (≥ 1,3) la curentul minim
sens = [("R3", "P2", 1.5), ("R2", "P2", 1.5), ("R1", "P1", 1.5), ("R1", "P2", 1.3), ("R0", "B2", 1.5),
        ("R0", "P1", 1.3)]
for nume, b, kmin in sens:
    ks = I2min[b] / relee[nume]["Is"]
    print(f"  sensibilitatea {nume} la defect bifazat minim în {b}: {fmt(ks, 2)} (cerut ≥ {fmt(kmin, 1)})")
    verifica_adevarat(f"sensibilitate {nume} în {b}", ks >= kmin)
# Treapta instantanee a lui R1: peste curentul maxim la capătul zonei (P1), cu marjă 1,3
I_inst_R1 = 1.3 * I3["P1"]
I_inst_R1 = np.ceil(I_inst_R1 / 100) * 100
print(f"  R1, treapta instantanee (I>>): 1,3·I\"k3max(P1) = {fmt(1.3 * I3['P1'], 0)} A → aleasă {fmt(I_inst_R1, 0)} A")
# Selectivitatea în timp, caracteristica SI
TMS = {"R3": 0.05}
puncte = [("R2", "R3", I3["P2"]), ("R1", "R2", I3["P1"]), ("R0", "R1", I_inst_R1)]
for sus, jos, I in puncte:
    t_jos = float(timp_invers(I, relee[jos]["Is"], TMS[jos]))
    TMS[sus] = TMS_necesar(t_jos + DT_TREAPTA, I, relee[sus]["Is"])
    TMS[sus] = np.ceil(TMS[sus] * 100) / 100          # rotunjire în sus la pasul de 0,01
    t_sus = float(timp_invers(I, relee[sus]["Is"], TMS[sus]))
    # calea a doua: TMS găsit numeric din condiția t_sus − t_jos = Δt
    TMS_num = brentq(lambda m: float(timp_invers(I, relee[sus]["Is"], m)) - t_jos - DT_TREAPTA, 1e-3, 2)
    print(f"  {sus} față de {jos} la I = {fmt(I, 0)} A: t({jos}) = {fmt(t_jos, 3)} s → TMS({sus}) = {fmt(TMS[sus], 2)}"
          f" (exact {fmt(TMS_num, 4)}), t({sus}) = {fmt(t_sus, 3)} s")
    verifica(f"TMS {sus}: formula inversă vs rădăcina numerică", TMS_necesar(t_jos + DT_TREAPTA, I, relee[sus]["Is"]),
             TMS_num)
    verifica_adevarat(f"marja {sus}–{jos} ≥ {DT_TREAPTA} s", t_sus - t_jos >= DT_TREAPTA - 1e-9)
    t_min = treapta_minima(t_jos, t_sus)
    print(f"    treapta minimă din componente: {fmt(T_CB, 2)} + {fmt(T_OVERSHOOT, 2)} + {fmt(T_SIGURANTA, 2)} + "
          f"{fmt(E_TIMP, 2)}·({fmt(t_jos, 3)} + {fmt(t_sus, 3)}) = {fmt(t_min, 3)} s ≤ marja realizată {fmt(t_sus - t_jos, 3)} s")
    verifica_adevarat(f"marja {sus}–{jos} acoperă cazul cel mai defavorabil al erorilor", t_sus - t_jos >= t_min)
for nume in relee:
    relee[nume]["TMS"] = TMS[nume]
# Calea de verificare independentă: defecte simulate în coordonate de fază, relee modelate cu integrator
T_INST = 0.04       # timpul propriu al treptei instantanee [s]
print("  verificare prin simulare (defecte trifazate, relee cu integrator):")
for b, protejat_de in (("P2", "R3"), ("P1", "R2"), ("B2", "R1")):
    p = r.rezolva_faze(defect_faze(b, "3f"))
    # curentul prin fider (F1a la B2) și prin T1 pe partea de 20 kV; pentru defect în B2 simulăm defectul
    # imediat după R1 (la începutul fiderului), adică la bara B2
    I_T1 = abs(r.curenti_ramura_faze(p, "T1", 2)[0])
    timpi = {}
    for nume in ("R3", "R2", "R1", "R0"):
        rl = relee[nume]
        if nume == "R3" and b != "P2":
            continue
        if nume == "R2" and b == "B2":
            continue
        I = I_T1                                 # rețea radială: același curent prin toate releele din amonte
        t_r = timp_integrator(np.full(200000, I), 1e-4, rl["Is"], rl["TMS"])
        if nume == "R1" and I >= I_inst_R1:
            t_r = min(t_r, T_INST)
        timpi[nume] = t_r
    ordine = sorted(timpi, key=timpi.get)
    txt = ", ".join(f"{n}: {fmt(timpi[n], 3)} s" for n in ordine)
    print(f"    defect în {b} (I = {fmt(I_T1, 0)} A): {txt}")
    verifica_adevarat(f"defect în {b}: acționează întâi {protejat_de}", ordine[0] == protejat_de)
    verifica_adevarat(f"defect în {b}: marja față de următorul ≥ {DT_TREAPTA} s",
                      timpi[ordine[1]] - timpi[ordine[0]] >= DT_TREAPTA - 1e-3)
# Acoperirea treptei instantanee a lui R1 pe tronsonul B2–P1. Traseul are 3 km de cablu și 7 km de LEA,
# cu impedanțe pe km diferite, deci distanța se calculează cu impedanța reală a traseului.
L_F1a = d["l_cablu_F1"] + d["l_lea_F1a"]
Zsrc = r.scurtcircuit_secvente("B2", "3f")["Zth"][1]
Zsrc_min = r_min.scurtcircuit_secvente("B2", "3f")["Zth"][1]
x_inst = brentq(lambda x: C_MAX * d["U20"] / SQRT3 / abs(Zsrc + z_fider(x)) - I_inst_R1, 0.0, L_F1a)
x_inst_min = brentq(lambda x: C_MIN * d["U20"] / 2 / abs(Zsrc_min + z_fider(x, KR80)) - I_inst_R1, 0.0, L_F1a)
print(f"  treapta instantanee a lui R1 acoperă {fmt(x_inst, 2)} km ({fmt(100 * x_inst / L_F1a, 0)} %) din B2–P1 la "
      f"defect trifazat maxim și {fmt(x_inst_min, 2)} km ({fmt(100 * x_inst_min / L_F1a, 0)} %) la defect bifazat minim"
      f" (R la 80 °C)")
# verificare: rețeaua cu o bară intermediară pusă la distanța găsită, rezolvată în componente simetrice și în fază
for x, kw, tip, k_faza in ((x_inst, dict(cu_capacitati=False), "3f", 0),
                           (x_inst_min, dict(c=C_MIN, cu_capacitati=False, kR20=KR80), "2f", 1)):
    rx = retea_cu_bara_pe_F1(x, **kw)
    I_s = abs(rx.scurtcircuit_secvente("X", tip)["I_faza"][k_faza])
    I_p = abs(rx.curent_defect_faze(rx.rezolva_faze(defect_faze("X", tip)))[0])
    verifica(f"curentul la limita treptei instantanee ({tip}, bară la {x:.2f} km) = I>> (secvențe)", I_s, I_inst_R1)
    verifica(f"curentul la limita treptei instantanee ({tip}): secvențe vs fază", I_s, I_p)
# cu o linie de 110 kV scoasă din funcțiune, acoperirea la defect bifazat minim scade
Zsrc_slab = min((configuratii[k].scurtcircuit_secvente("B2", "3f")["Zth"][1] for k in configuratii), key=lambda z: -abs(z))
x_inst_slab = brentq(lambda x: C_MIN * d["U20"] / 2 / abs(Zsrc_slab + z_fider(x, KR80)) - I_inst_R1, 0.0, L_F1a)
print(f"  în configurația cea mai slabă (o linie de 110 kV scoasă), la defect bifazat minim: {fmt(x_inst_slab, 2)} km "
      f"({fmt(100 * x_inst_slab / L_F1a, 0)} %)")
verifica_adevarat("acoperirea scade de la regimul maxim la cel minim", x_inst > x_inst_min >= x_inst_slab)
TMS_R = {k: v["TMS"] for k, v in relee.items()}
print("  reglaje finale:", "; ".join(f"{k}: Is = {fmt(v['Is'], 0)} A, TMS = {fmt(v['TMS'], 2)}" for k, v in relee.items()))

print("\nProblema 3.3 – logica de blocare a protecției barelor de 20 kV (protecția barelor prin blocare)")
t_R0_bara = float(timp_invers(I3["B2"], relee["R0"]["Is"], relee["R0"]["TMS"]))
t_blocare = 0.10     # treapta rapidă a lui R0, blocată de pornirea oricărui releu de fider
t_cb = 0.06          # timpul de întrerupere al întrerupătorului (date de problemă)
print(f"  fără logică de blocare, defectul pe bara B2 este eliminat de R0 (IDMT) în {fmt(t_R0_bara, 3)} s + "
      f"{fmt(t_cb, 2)} s = {fmt(t_R0_bara + t_cb, 3)} s")
print(f"  cu treapta rapidă blocată de pornirea releelor de fider: {fmt(t_blocare, 2)} s + {fmt(t_cb, 2)} s = "
      f"{fmt(t_blocare + t_cb, 2)} s")
verifica_adevarat("treapta rapidă reduce timpul de eliminare de cel puțin 3 ori", (t_R0_bara + t_cb) / (t_blocare + t_cb) >= 3)

print("\nProblema 3.4 – protecția homopolară (51N) a fiderului F1, neutru tratat prin rezistor (300 A)")
rr = retea_referinta("rezistor", c=1.0)
Uf = d["U20"] / SQRT3
C0_F1 = d["c_cablu"] * d["l_cablu_F1"] + d["c0_lea20"] * (d["l_lea_F1a"] + d["l_lea_F1b"])
I_cap_F1 = 3 * W0 * C0_F1 * Uf
# defect pe bara B2 (exterior fiderului): F1 vede doar curentul capacitiv propriu
p = rr.rezolva_faze(defect_faze("B2", "1f"))
I_res_ext = abs(np.sum(rr.curenti_ramura_faze(p, "F1a", 1)))
print(f"  C0(F1) = {fmt(C0_F1 * 1e6, 3)} µF; curentul capacitiv propriu 3ωC0·Uf = {fmt(I_cap_F1, 2)} A; "
      f"3I0 văzut de R1 la defect exterior (simulare) = {fmt(I_res_ext, 2)} A")
verifica("3I0 la defect exterior: formulă vs simulare (abatere sub 5 %)", I_cap_F1, I_res_ext, rtol=5e-2)
I0_set = 20.0
print(f"  reglaj ales: 3I0> = {fmt(I0_set, 0)} A primar (de {fmt(I0_set / I_res_ext, 1)} ori curentul capacitiv propriu)")
verifica_adevarat("reglajul depășește de cel puțin 2 ori curentul capacitiv propriu", I0_set >= 2 * I_res_ext)


def I_res_R1(Rf, bara="P2"):
    pp = rr.rezolva_faze(defect_faze(bara, "1f", Rf))
    return abs(np.sum(rr.curenti_ramura_faze(pp, "F1a", 1)))


# Calea 1: componente simetrice (curentul homopolar la locul defectului, mai puțin curentul capacitiv din aval)
def I_res_R1_seq(Rf, bara="P2"):
    s = rr.scurtcircuit_secvente(bara, "1f", Zf=Rf)
    Ifs = rr.curenti_ramura_secvente(s, "F1a", 1)
    return abs(np.sum(Ifs))


Rf_max = brentq(lambda R: I_res_R1(R) - I0_set, 1.0, 5000.0)
Rf_max_seq = brentq(lambda R: I_res_R1_seq(R) - I0_set, 1.0, 5000.0)
print(f"  rezistența de defect maximă detectată la capătul fiderului (P2): {fmt(Rf_max, 0)} Ω "
      f"(din secvențe: {fmt(Rf_max_seq, 0)} Ω)")
verifica("Rf maxim: coordonate de fază vs secvențe", Rf_max, Rf_max_seq)
# estimare de mână: I ≈ Uf/(RN + Rf), neglijând capacitățile și impedanțele liniilor
Rf_mana = Uf / I0_set - Uf / d["IN_rezistor"]
print(f"  estimare de mână Uf/(RN + Rf) = 3I0> → Rf ≈ {fmt(Rf_mana, 0)} Ω")
verifica("estimarea de mână vs calculul exact (abatere sub 5 %)", Rf_mana, Rf_max, rtol=5e-2)

print("\nProblema 3.5 – direcția curentului homopolar: fider defect vs fider sănătos")
C0_rest = d["c_cablu"] * d["l_cablu_rest"] + d["c0_lea20"] * d["l_lea_rest"]
RN = Uf / d["IN_rezistor"]
for neutru in ("izolat", "rezistor"):
    net = retea_referinta(neutru, c=1.0)
    for loc, descriere in (("P1", "defect pe F1 (interior)"), ("B2", "defect pe bară/alt fider (exterior)")):
        # calea 1: coordonate de fază
        pp = net.rezolva_faze(defect_faze(loc, "1f"))
        I3I0 = np.sum(net.curenti_ramura_faze(pp, "F1a", 1))    # curentul rezidual care intră în F1 de la bară
        U0 = np.mean(net.tensiuni_faze(pp, "B2"))
        unghi = np.degrees(np.angle(I3I0 / U0))
        # calea 2: componente simetrice (curentul homopolar al ramurii, din tensiunile de secvență)
        sq = net.scurtcircuit_secvente(loc, "1f")
        I3I0_s = np.sum(net.curenti_ramura_secvente(sq, "F1a", 1))
        U0_s = sq["V_seq"][0][sq["idx"]["B2"]]
        print(f"  neutru {neutru}, {descriere}: 3I0 = {fmt(abs(I3I0), 1)} A, unghiul față de U0 = {fmt(unghi, 1)}°, "
              f"|U0| = {fmt(abs(U0) / Uf, 3)}·Uf")
        verifica(f"3I0 ({neutru}, defect în {loc}): fază vs secvențe", I3I0, I3I0_s, rtol=1e-3, atol=1e-3)
        verifica(f"U0 ({neutru}, defect în {loc}): fază vs secvențe", U0, U0_s, rtol=1e-3)
        if loc == "B2":
            verifica_adevarat(f"fider sănătos ({neutru}): 3I0 înaintea lui U0 cu 90° ± 1°", abs(unghi - 90.0) < 1.0)
        elif neutru == "izolat":
            verifica_adevarat("fider defect (izolat): 3I0 în urma lui U0 cu 90° ± 1°", abs(unghi + 90.0) < 1.0)
            # bilanțul de curenți la bara B2 (verificare de consistență): fiderul defect conduce curentul
            # capacitiv al restului rețelei, cu U0 real (mai mare decât Uf)
            print(f"     formula de manual cu U0 = Uf: 3ωC0,rest·Uf = {fmt(3 * W0 * C0_rest * Uf, 1)} A; "
                  f"cu U0 simulat: {fmt(3 * W0 * C0_rest * abs(U0), 1)} A")
            verifica("bilanț la bara B2: |3I0| = 3ωC0,rest·|U0|", abs(I3I0), 3 * W0 * C0_rest * abs(U0), rtol=5e-3)
        else:
            I_bilant = -(U0 / RN + 1j * 3 * W0 * C0_rest * U0)
            verifica("bilanț la bara B2 (rezistor): 3I0 = −(U0/RN + j3ωC0,rest·U0)", I3I0, I_bilant, rtol=5e-3)
