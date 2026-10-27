"""Capitolul 8 – Reglajul automat al frecvenței și al tensiunii: rezolvarea și verificarea problemelor."""

import numpy as np
from modele import GEN, DATE, SQRT3, W0, fmt, verifica, verifica_adevarat, retea_referinta
from calcul_cap08 import (M_inertie, K_statism, izolat_ode, izolat_lti, nadir, ce_simulare, ce_nadir_analitic,
                          dasf_simulare, doua_zone, jacobian_numeric, tensiune_secundar,
                          tensiune_secundar_iterativ, regulator_ploturi, rat_ode, rat_lti, rat_analitic)

F0 = 50.0

# ---------------------------------------------------------------------------
print("Problema 8.1 – pierderea unui grup într-un sistem izolat")
S_rest = 875.0          # puterea nominală a grupurilor rămase în funcțiune [MW]
H, s_st = 5.0, 0.05     # constanta de inerție (baza S_rest) și statismul
D = 16.0                # efectul de autoreglare al sarcinii [MW/Hz] (dată de problemă)
Tg, Tt = 0.2, 2.0       # constantele de timp ale regulatorului și ale turbinei [s]
dP = 100.0              # puterea pierdută [MW]
M = M_inertie(H, S_rest)
K = K_statism(S_rest, s_st)
print(f"  M = 2·H·S/f0 = {fmt(M, 1)} MW·s/Hz; panta regulatoarelor K = S/(s·f0) = {fmt(K, 1)} MW/Hz")
rocof0 = -dP / M
df_ss = -dP / (K + D)
df_ss_fara = -dP / D
print(f"  RoCoF inițial = −ΔP/M = {fmt(rocof0, 3)} Hz/s")
print(f"  abaterea staționară cu regulatoare: Δf = −ΔP/(K + D) = {fmt(df_ss * 1e3, 1)} mHz")
print(f"  fără regulatoare: Δf = −ΔP/D = {fmt(df_ss_fara, 2)} Hz, cu constanta de timp M/D = {fmt(M / D, 2)} s")
t, df, Pm = izolat_ode(dP, M, D, K, Tg, Tt, 120.0, n=12001)
df_lti = izolat_lti(dP, M, D, K, Tg, Tt, t)
tn, dfn = nadir(t, df)
tn2, dfn2 = nadir(t, df_lti)
rocof_num = (df[1] - df[0]) / (t[1] - t[0])
k500 = np.searchsorted(t, 0.5)
rocof_500 = df[k500] / t[k500]
print(f"  simulare: nadir Δf = {fmt(dfn * 1e3, 1)} mHz la t = {fmt(tn, 2)} s (funcția de transfer: "
      f"{fmt(dfn2 * 1e3, 1)} mHz la {fmt(tn2, 2)} s); Δf(120 s) = {fmt(df[-1] * 1e3, 1)} mHz")
print(f"  RoCoF mediu pe primele 500 ms = {fmt(rocof_500, 3)} Hz/s (inițial {fmt(rocof0, 3)} Hz/s)")
verifica("RoCoF inițial: analitic vs simulare (primul pas)", rocof0, rocof_num, rtol=2e-3)
verifica("Δf staționar: analitic vs simulare", df_ss, df[-1], rtol=1e-3)
verifica("nadir: solve_ivp vs funcția de transfer", dfn, dfn2, rtol=1e-3)
verifica("momentul nadirului: solve_ivp vs funcția de transfer", tn, tn2, atol=0.02, rtol=0)
verifica("ΔPm final = K·|Δf| (bilanțul regulatoarelor)", Pm[-1], -K * df[-1], rtol=1e-3)
print(f"  în regim staționar: turbinele dau {fmt(Pm[-1], 1)} MW, sarcina scade cu D·|Δf| = {fmt(-D * df[-1], 1)} MW")
verifica("bilanțul staționar: ΔPm + D·|Δf| = ΔP", Pm[-1] - D * df[-1], dP, rtol=1e-3)
t2, df2, _ = izolat_ode(dP, M, D, K, Tg, Tt, 200.0, cu_regulator=False)
print(f"  fără regulatoare, după 10 s: Δf = {fmt(df2[np.searchsorted(t2, 10.0)], 2)} Hz "
      f"(analitic {fmt(df_ss_fara * (1 - np.exp(-10 * D / M)), 2)} Hz)")
verifica("fără regulatoare: Δf(10 s) analitic vs simulare", df_ss_fara * (1 - np.exp(-10 * D / M)),
         df2[np.searchsorted(t2, 10.0)], rtol=2e-3)
for Tt_ in (0.5, 5.0):
    tt, dd, _ = izolat_ode(dP, M, D, K, Tg, Tt_, 200.0, n=20001)
    print(f"  cu Tt = {fmt(Tt_, 1)} s: nadir {fmt(nadir(tt, dd)[1] * 1e3, 0)} mHz la {fmt(nadir(tt, dd)[0], 2)} s "
          f"(staționar neschimbat: {fmt(dd[-1] * 1e3, 1)} mHz)")
    verifica(f"Tt = {Tt_} s: staționarul nu depinde de Tt", dd[-1], df_ss, rtol=2e-3)

# ---------------------------------------------------------------------------
print("\nProblema 8.2 – incidentul de referință în Europa continentală (3000 MW)")
P_inc, Pfcr, df_fcr = 3000.0, 3000.0, 0.200       # SOGL: incident de referință, FCR total, abaterea la activare completă
lam = Pfcr / df_fcr
S_ce, H_ce = 300e3, 4.0                            # date de problemă: sarcina 300 GW, H = 4 s
D_ce = 0.01 * S_ce                                 # date de problemă: 1 % din sarcină pe Hz
M_ce = M_inertie(H_ce, S_ce)
viteza = Pfcr / 30.0                               # cea mai lentă creștere admisă: liniar, 100 % în 30 s
df_ce = -P_inc / (lam + D_ce)
print(f"  caracteristica FCR λ = {fmt(Pfcr, 0)} MW / {fmt(df_fcr * 1e3, 0)} mHz = {fmt(lam, 0)} MW/Hz; "
      f"D = {fmt(D_ce, 0)} MW/Hz; M = {fmt(M_ce, 0)} MW·s/Hz")
print(f"  abaterea staționară Δf = −ΔP/(λ + D) = {fmt(df_ce * 1e3, 1)} mHz; FCR livrează {fmt(-lam * df_ce, 0)} MW,"
      f" sarcina scade cu {fmt(-D_ce * df_ce, 0)} MW")
print(f"  RoCoF inițial = −ΔP/M = {fmt(-P_inc / M_ce * 1e3, 1)} mHz/s")
t, dfc, Pc = ce_simulare(P_inc, M_ce, D_ce, lam, Pfcr, viteza, 200.0, dt=2e-3)
tn, dfn = nadir(t, dfc)
tn_a, dfn_a = ce_nadir_analitic(P_inc, M_ce, D_ce, viteza)
print(f"  nadir: simulare {fmt(dfn * 1e3, 1)} mHz la {fmt(tn, 2)} s; analitic (faza cu FCR limitat de viteză) "
      f"{fmt(dfn_a * 1e3, 1)} mHz la {fmt(tn_a, 2)} s")
verifica("nadir CE: analitic vs simulare", dfn_a, dfn, rtol=1e-3)
verifica("momentul nadirului CE: analitic vs simulare", tn_a, tn, atol=0.02, rtol=0)
verifica_adevarat("la nadir FCR este încă limitat de viteză (ipoteza formulei analitice)",
                  viteza * tn_a < lam * abs(dfn_a) and viteza * tn_a < Pfcr)
verifica("Δf staționar CE: analitic vs simulare", df_ce, dfc[-1], rtol=1e-3)
verifica_adevarat("abaterea maximă instantanee < 800 mHz (SOGL)", abs(dfn) < 0.800)
verifica_adevarat("abaterea staționară ≤ 200 mHz (SOGL)", abs(dfc[-1]) <= 0.200)
P15 = Pc[np.searchsorted(t, 15.0)]
print(f"  FCR la 15 s = {fmt(P15, 0)} MW ({fmt(100 * P15 / Pfcr, 1)} % din 3000 MW)")
# Fără efectul de autoreglare al sarcinii (D = 0): FCR crește liniar 30 s, timp în care deficitul
# scade de la 3000 MW la 0; frecvența se oprește la Δf(30 s) = −(ΔP·T − r·T²/2)/M și rămâne acolo,
# deoarece FCR este saturat exact la valoarea deficitului (nu mai există putere care să o readucă).
t0, dfc0, _ = ce_simulare(P_inc, M_ce, 1e-9, lam, Pfcr, viteza, 200.0, dt=2e-3)
T_fcr = Pfcr / viteza
df30 = -(P_inc * T_fcr - viteza * T_fcr**2 / 2) / M_ce
print(f"  dacă D = 0: frecvența coboară până la Δf(30 s) = −(ΔP·T − r·T²/2)/M = {fmt(df30 * 1e3, 1)} mHz și rămâne acolo "
      f"(simulare: nadir {fmt(nadir(t0, dfc0)[1] * 1e3, 1)} mHz, Δf(200 s) = {fmt(dfc0[-1] * 1e3, 1)} mHz)")
verifica("D = 0: Δf(30 s) analitic vs simulare", df30, dfc0[np.searchsorted(t0, T_fcr)], rtol=1e-3)
verifica("D = 0: frecvența nu mai revine (Δf(200 s) = Δf(30 s))", dfc0[-1], df30, rtol=1e-3)
verifica_adevarat("D = 0 cu FCR la viteza minimă: limita de 800 mHz ar fi depășită", abs(df30) > 0.800)

# ---------------------------------------------------------------------------
print("\nProblema 8.3 – descărcarea automată a sarcinii (DASF) într-o insulă cu deficit de 30 %")
PL0 = 600.0                      # sarcina insulei [MW]
S_g, H_g = 500.0, 4.0            # grupurile din insulă
rez = 80.0                       # rezerva turnantă a grupurilor [MW]
dP3 = 180.0                      # importul pierdut la separarea insulei [MW] (30 % din sarcină)
D3 = 0.02 * PL0                  # 2 % din sarcină pe Hz (dată de problemă)
M3 = M_inertie(H_g, S_g)
K3 = K_statism(S_g, 0.05)
t_int = 0.15                     # temporizare + timp de deconectare [s]
# Schema: 9 trepte egale de 5 %, între 49,0 și 48,0 Hz
praguri = [49.0 - 0.125 * i for i in range(9)]
cote = [0.05] * 9
trepte = [(f, c * PL0) for f, c in zip(praguri, cote)]
# Verificarea cerințelor NC ER (Europa continentală). Banda de implementare de ±7 % este interpretată ca
# abaterea admisă a scării cumulate față de dreapta dintre (49,0 Hz; 5 %) și (48,0 Hz; 45 %).
fgrila = np.linspace(48.0, 49.0, 100001)
dreapta = 0.05 + 0.40 * (49.0 - fgrila)


def abatere_exacta(praguri_, cote_):
    """Calea 1: extremele abaterii apar chiar la pragurile treptelor – imediat după acționarea treptei k
    (cumulat C_k) și imediat înainte (cumulat C_{k−1}, cu frecvența tinzând spre prag de sus)."""
    C = np.cumsum(cote_)
    ab = []
    for k, fk in enumerate(praguri_):
        L = 0.05 + 0.40 * (49.0 - fk)
        ab.append(C[k] - L)
        if k > 0:
            ab.append(C[k - 1] - L)
    return max(ab, key=abs)


def abatere_grila(praguri_, cote_):
    """Calea 2: scara evaluată pe o grilă fină de frecvențe între 48,0 și 49,0 Hz."""
    sc = np.zeros_like(fgrila)
    for f, c in zip(praguri_, cote_):
        sc += np.where(fgrila <= f + 1e-12, c, 0.0)
    d = sc - dreapta
    return d[np.argmax(np.abs(d))]


def verifica_schema(nume, praguri_, cote_):
    C = np.cumsum(cote_)
    ab_e = abatere_exacta(praguri_, cote_)
    ab_g = abatere_grila(praguri_, cote_)
    conditii = {
        "prima treaptă la 49,0 Hz": praguri_[0] == 49.0,
        "cumulat la 49,0 Hz în 5 % ± 7 %": abs(C[0] - 0.05) <= 0.07 + 1e-12,
        "45 % cumulat la 48,0 Hz": praguri_[-1] == 48.0 and abs(C[-1] - 0.45) < 1e-12,
        "cel puțin 6 trepte": len(praguri_) >= 6,
        "cel mult 10 % pe treaptă": max(cote_) <= 0.10 + 1e-12,
        "abaterea față de dreaptă ≤ 7 puncte": abs(ab_e) <= 0.07 + 1e-12,
    }
    print(f"  {nume}: " + "; ".join(f"{fmt(f, 3)} Hz → {fmt(100 * c, 1)} %" for f, c in zip(praguri_, cote_)))
    print(f"     abaterea maximă față de dreapta 5 % → 45 %: {fmt(100 * ab_e, 2)} puncte (grilă fină: "
          f"{fmt(100 * ab_g, 2)}); condiții neîndeplinite: "
          f"{', '.join(k for k, v in conditii.items() if not v) or 'niciuna'}")
    verifica(f"{nume}: abaterea maximă – calcul exact la praguri vs grilă fină", ab_e, ab_g, rtol=0, atol=1e-4)
    return all(conditii.values()), ab_e


ok9, ab9 = verifica_schema("schema aleasă, 9 × 5 %", praguri, cote)
verifica_adevarat("schema aleasă respectă toate condițiile NC ER (cu interpretarea benzii)", ok9)
# Două scheme cu 6 trepte la câte 0,2 Hz
praguri6 = [49.0, 48.8, 48.6, 48.4, 48.2, 48.0]
cote6e = [0.075] * 6
cote6n = [0.10, 0.08, 0.08, 0.08, 0.08, 0.03]
ok6e, ab6e = verifica_schema("6 trepte egale de 7,5 %", praguri6, cote6e)
verifica_adevarat("6 trepte egale de 7,5 % depășesc banda (cu 0,5 puncte, chiar înainte de 48,0 Hz)",
                  (not ok6e) and abs(abs(ab6e) - 0.075) < 1e-12)
ok6n, ab6n = verifica_schema("6 trepte inegale 10/8/8/8/8/3 %", praguri6, cote6n)
verifica_adevarat("6 trepte inegale 10/8/8/8/8/3 % respectă toate condițiile", ok6n)
# Simulări
t, f_cu, Pm_cu, desc, act = dasf_simulare(dP3, M3, D3, K3, Tg=0.2, Tt=1.0, rezerva=rez, trepte=trepte,
                                         t_intarziere=t_int, t_end=40.0, dt=1e-3)
_, f_fara, _, _, _ = dasf_simulare(dP3, M3, D3, K3, Tg=0.2, Tt=1.0, rezerva=rez, trepte=[],
                                   t_intarziere=t_int, t_end=40.0, dt=1e-3)
print(f"  RoCoF inițial = −ΔP/M = {fmt(-dP3 / M3, 2)} Hz/s (M = {fmt(M3, 0)} MW·s/Hz)")
for (i, ta, fp, Pd) in act:
    print(f"    treapta {i + 1} ({fmt(fp, 3)} Hz) deconectează {fmt(Pd, 0)} MW la t = {fmt(ta, 3)} s")
n_tr = len(act)
shed = desc[-1]
rest = dP3 - shed
# frecvența finală analitică: regulatoarele nesaturate dacă K·|Δf| < rezervă
df_fin = -rest / (K3 + D3)
if K3 * abs(df_fin) > rez:
    df_fin = -(rest - rez) / D3
print(f"  deficitul rămas {fmt(rest, 0)} MW → Δf = {fmt(df_fin, 3)} Hz")
print(f"  cu DASF: frecvența minimă {fmt(f_cu.min(), 3)} Hz la t = {fmt(t[np.argmin(f_cu)], 2)} s; "
      f"au acționat {n_tr} trepte ({fmt(shed, 0)} MW); frecvența finală {fmt(f_cu[-1], 3)} Hz "
      f"(analitic {fmt(F0 + df_fin, 3)} Hz)")
verifica("frecvența finală cu DASF: analitic vs simulare", F0 + df_fin, f_cu[-1], rtol=1e-5)
verifica_adevarat("cu DASF frecvența rămâne peste 48,0 Hz", f_cu.min() > 48.0)
# Aceeași insulă cu schema de 6 trepte inegale (trepte mai mari)
trepte6 = [(f, c * PL0) for f, c in zip(praguri6, cote6n)]
_, f6, _, desc6, act6 = dasf_simulare(dP3, M3, D3, K3, Tg=0.2, Tt=1.0, rezerva=rez, trepte=trepte6,
                                      t_intarziere=t_int, t_end=40.0, dt=1e-3)
rest6 = dP3 - desc6[-1]
df6 = -rest6 / (K3 + D3)
if K3 * abs(df6) > rez:
    df6 = -(rest6 - rez) / D3
print(f"  cu schema de 6 trepte inegale: au acționat {len(act6)} trepte ({fmt(desc6[-1], 0)} MW), minimul "
      f"{fmt(f6.min(), 3)} Hz, frecvența finală {fmt(f6[-1], 3)} Hz (analitic {fmt(F0 + df6, 3)} Hz)")
verifica("schema de 6 trepte inegale: frecvența finală analitic vs simulare", F0 + df6, f6[-1], rtol=1e-5)
print(f"  surplusul deconectat față de deficitul neacoperit de rezervă (100 MW): 9 × 5 %: {fmt(shed - (dP3 - rez), 0)} MW;"
      f" 6 trepte inegale: {fmt(desc6[-1] - (dP3 - rez), 0)} MW")
t475 = t[np.argmax(f_fara < 47.5)]
df_fin_fara = -(dP3 - rez) / D3
print(f"  fără DASF: frecvența scade sub 47,5 Hz după {fmt(t475, 2)} s; staționarul teoretic ar fi "
      f"{fmt(F0 + df_fin_fara, 2)} Hz (regulatoare saturate) – practic insula se prăbușește")
verifica_adevarat("fără DASF se coboară sub 47,5 Hz", f_fara.min() < 47.5)
_, f_lung, _, _, _ = dasf_simulare(dP3, M3, D3, K3, Tg=0.2, Tt=1.0, rezerva=rez, trepte=[], t_intarziere=t_int,
                                   t_end=120.0, dt=5e-3)
verifica("fără DASF: staționar analitic vs simulare (120 s)", F0 + df_fin_fara, f_lung[-1], rtol=1e-5)
# Timpul până la primul prag, cu RoCoF inițial (aproximare) vs simulare
t49_sim = t[np.argmax(f_cu < 49.0)]
print(f"  frecvența atinge 49,0 Hz la t = {fmt(t49_sim, 3)} s (estimare cu RoCoF constant: {fmt(1.0 / (dP3 / M3), 3)} s)")
verifica_adevarat("estimarea cu RoCoF constant dă un timp mai scurt (regulatoarele și sarcina frânează căderea)",
                  1.0 / (dP3 / M3) <= t49_sim)

# ---------------------------------------------------------------------------
print("\nProblema 8.4 – două zone interconectate, reglaj primar și secundar")
z1 = dict(M=M_inertie(5.0, 12e3), D=200.0, K=K_statism(12e3, 0.05), Tg=0.2, Tt=0.3)
z2 = dict(M=M_inertie(5.0, 24e3), D=400.0, K=K_statism(24e3, 0.05), Tg=0.2, Tt=0.3)
for z in (z1, z2):
    z["B"] = z["K"] + z["D"]          # factorul K al zonei ales egal cu caracteristica naturală
    z["Ki"] = 0.02                    # câștigul integral al regulatorului secundar [1/s]
Ps = 1000.0                           # puterea sincronizantă a interconexiunii [MW/rad]
dPL1 = 300.0
b1, b2 = z1["K"] + z1["D"], z2["K"] + z2["D"]
df_p = -dPL1 / (b1 + b2)
Ptie_p = -dPL1 * b2 / (b1 + b2)
print(f"  caracteristicile zonelor: β1 = {fmt(b1, 0)} MW/Hz, β2 = {fmt(b2, 0)} MW/Hz")
print(f"  numai reglaj primar: Δf = −ΔPL1/(β1 + β2) = {fmt(df_p * 1e3, 1)} mHz; "
      f"ΔPint12 = −ΔPL1·β2/(β1 + β2) = {fmt(Ptie_p, 1)} MW (zona 2 ajută zona 1)")
t, Y, fun = doua_zone(z1, z2, Ps, dPL1, 600.0, cu_secundar=False)
verifica("numai primar: Δf1 final analitic vs simulare", df_p, Y[0, -1], rtol=1e-3)
verifica("numai primar: Δf2 = Δf1 în regim staționar", Y[1, -1], Y[0, -1], rtol=1e-3)
verifica("numai primar: ΔPint12 final analitic vs simulare", Ptie_p, Y[2, -1], rtol=1e-3)
t, Y, fun = doua_zone(z1, z2, Ps, dPL1, 900.0, cu_secundar=True)
print(f"  cu reglaj secundar, după 900 s: Δf1 = {fmt(Y[0, -1] * 1e3, 3)} mHz, ΔPint12 = {fmt(Y[2, -1], 2)} MW, "
      f"ΔPm1 = {fmt(Y[4, -1], 1)} MW, ΔPm2 = {fmt(Y[6, -1], 2)} MW")
verifica("secundar: Δf → 0", Y[0, -1], 0.0, atol=1e-4, rtol=0)
verifica("secundar: ΔPint → 0 (programul de schimb este refăcut)", Y[2, -1], 0.0, atol=0.5, rtol=0)
verifica("secundar: zona 1 preia toată creșterea de sarcină", Y[4, -1], dPL1, rtol=2e-3)
verifica("secundar: zona 2 revine la puterea programată", Y[6, -1], 0.0, atol=0.5, rtol=0)
J = jacobian_numeric(fun, 9)
ev = np.linalg.eigvals(J)
print(f"  valorile proprii ale sistemului liniar: partea reală maximă = {fmt(np.max(ev.real), 4)} 1/s")
verifica_adevarat("sistemul cu reglaj secundar este stabil (toate valorile proprii în semiplanul stâng)",
                  np.max(ev.real) < 0)
osc = ev[np.argmax(np.abs(ev.imag))]
print(f"  modul oscilant dintre zone (cu regulatoare): σ = {fmt(osc.real, 3)} 1/s, ω = {fmt(abs(osc.imag), 3)} rad/s "
      f"(f = {fmt(abs(osc.imag) / (2 * np.pi), 3)} Hz)")
# Verificarea modelului interconexiunii: fără regulatoare și cu D/M egal în cele două zone, mișcarea relativă
# este un oscilator amortizat cu σ = −D/(2M) și ω = √(2π·Ps·(1/M1 + 1/M2) − σ²)
z1n, z2n = dict(z1, K=0.0), dict(z2, K=0.0)
_, _, fun_n = doua_zone(z1n, z2n, Ps, dPL1, 1.0, cu_secundar=False, n=11)
ev_n = np.linalg.eigvals(jacobian_numeric(fun_n, 9))
osc_n = ev_n[np.argmax(ev_n.imag)]
sig_a = -z1["D"] / (2 * z1["M"])
om_a = np.sqrt(2 * np.pi * Ps * (1 / z1["M"] + 1 / z2["M"]) - sig_a**2)
print(f"  fără regulatoare: valori proprii σ = {fmt(osc_n.real, 4)} 1/s, ω = {fmt(osc_n.imag, 4)} rad/s; "
      f"analitic σ = −D/(2M) = {fmt(sig_a, 4)} 1/s, ω = {fmt(om_a, 4)} rad/s")
verifica("modul interconexiunii fără regulatoare: σ valori proprii vs analitic", osc_n.real, sig_a, rtol=1e-4)
verifica("modul interconexiunii fără regulatoare: ω valori proprii vs analitic", osc_n.imag, om_a, rtol=1e-4)
# Contraexemplu: turbine mai lente și interconexiune mai puternică
z1b, z2b = dict(z1, Tt=1.0), dict(z2, Tt=1.0)
_, _, fun_b = doua_zone(z1b, z2b, 2000.0, dPL1, 1.0, cu_secundar=True, n=11)
ev_b = np.linalg.eigvals(jacobian_numeric(fun_b, 9))
print(f"  cu Tt = 1 s și Ps = 2000 MW/rad: partea reală maximă = {fmt(np.max(ev_b.real), 4)} 1/s → oscilație neamortizată")
verifica_adevarat("contraexemplu: modelul devine instabil (amortizare negativă a modului de interconexiune)",
                  np.max(ev_b.real) > 0)
kn = np.argmin(Y[0])
print(f"  nadirul în zona 1: {fmt(Y[0, kn] * 1e3, 1)} mHz la t = {fmt(t[kn], 2)} s; "
      f"Δf1 revine sub 1 mHz după {fmt(t[np.where(np.abs(Y[0]) > 1e-3)[0][-1]], 0)} s")

# ---------------------------------------------------------------------------
print("\nProblema 8.5 – regulatorul automat de ploturi al transformatorului T1 (110 ± 8 × 1,25 % / 20 kV)")
ZT_mod = DATE["ukT"] * DATE["U20"]**2 / DATE["ST"]
RT = DATE["PkT"] * DATE["U20"]**2 / DATE["ST"]**2
XT = np.sqrt(ZT_mod**2 - RT**2)
pas = 0.0125
print(f"  impedanța lui T1 raportată la 20 kV: RT = {fmt(RT, 4)} Ω, XT = {fmt(XT, 4)} Ω")
# (a) tensiunea la sarcină: ecuația de gradul 4 (bicuadratică) vs iterații fazoriale vs formula aproximativă
P_, Q_ = 20e6, 20e6 * np.tan(np.arccos(0.9))
E_ = 113e3 / (110 / 20)
print(f"  t.e.m. raportată la 20 kV (plotul 0): E = 113/5,5 = {fmt(E_ / 1e3, 3)} kV")
U_q = tensiune_secundar(E_, P_, Q_, RT, XT)
U_i = tensiune_secundar_iterativ(E_, P_, Q_, RT, XT)
U_ap = E_ - (RT * P_ + XT * Q_) / E_
print(f"  la 113 kV și 20 MW, cos φ = 0,9: U2 = {fmt(U_q / 1e3, 4)} kV (ecuația bicuadratică), "
      f"{fmt(U_i / 1e3, 4)} kV (iterații), {fmt(U_ap / 1e3, 4)} kV (ΔU ≈ (RP + XQ)/U)")
verifica("U2: ecuația bicuadratică vs iterații fazoriale", U_q, U_i, rtol=1e-9)
print(f"  formula aproximativă (numai componenta longitudinală a căderii) greșește cu {fmt(100 * (U_ap / U_q - 1), 2)} %")
verifica("U2: formula aproximativă (abatere sub 1 %)", U_ap, U_q, rtol=1e-2)
# (b) pasul de tensiune al unui plot și regula benzii
pasi = [1 - (1 + pas * n) / (1 + pas * (n + 1)) for n in range(-8, 8)]
print(f"  un plot schimbă tensiunea secundară cu {fmt(100 * min(pasi), 2)} … {fmt(100 * max(pasi), 2)} %")
U_ref = 20.5e3
T_int = 30.0
t_h = np.arange(0, 3600.0, 1.0)
U_IT_c = np.full(len(t_h), 113e3)
Pc_ = np.full(len(t_h), 15e6)
Qc_ = Pc_ * np.tan(np.arccos(0.9))
rezultate = {}
for banda_pct in (0.5, 1.0):
    banda = banda_pct / 100 * U_ref
    Ub, Us, Ur, poz, nc = regulator_ploturi(t_h, U_IT_c, Pc_, Qc_, RT, XT, U_ref, banda, T_int, pas)
    dupa = np.sum(np.abs(np.diff(poz[600:])) > 0)
    rezultate[banda_pct] = dupa
    pendulare_prezisa = 2 * banda_pct / 100 < min(pasi)
    print(f"  banda ±{fmt(banda_pct, 1)} % (lățime {fmt(2 * banda_pct, 1)} %): {nc} comutări într-o oră la sarcină constantă,"
          f" din care {dupa} după primele 10 minute → {'pendulare' if dupa > 0 else 'fără pendulare'}"
          f" (regula 2·bandă < pas prezice {'pendulare' if pendulare_prezisa else 'stabilitate'})")
    verifica_adevarat(f"banda ±{banda_pct} %: simularea confirmă regula lățimii benzii", (dupa > 0) == pendulare_prezisa)
# (c) o zi întreagă, cu sarcina și tensiunea de 110 kV variabile
t_d = np.arange(0, 86400.0, 1.0)
ora = t_d / 3600
P_d = 1e6 * (14 - 5 * np.cos(2 * np.pi * (ora - 4) / 24) + 3 * np.exp(-((ora - 19.5) / 1.5)**2))
Q_d = P_d * np.tan(np.arccos(0.9))
U_IT_d = 1e3 * (113.5 + 1.5 * np.cos(2 * np.pi * (ora - 3) / 24))
banda = 0.01 * U_ref


def zi(**kw):
    """Simulează o zi pornind din poziția plotului de la sfârșitul zilei precedente (regim periodic)."""
    n_start = regulator_ploturi(t_d, U_IT_d, P_d, Q_d, RT, XT, U_ref, banda, T_int, pas, **kw)[3][-1]
    return regulator_ploturi(t_d, U_IT_d, P_d, Q_d, RT, XT, U_ref, banda, T_int, pas, n0=int(n_start), **kw)


Ub, Us, Ur, poz, nc = zi()
in_banda = np.mean(np.abs(Ur - U_ref) <= banda)
print(f"  o zi: sarcina {fmt(P_d.min() / 1e6, 1)} … {fmt(P_d.max() / 1e6, 1)} MW, U(110 kV) {fmt(U_IT_d.min() / 1e3, 1)} … "
      f"{fmt(U_IT_d.max() / 1e3, 1)} kV; {nc} comutări; plotul între {poz.min()} și {poz.max()}; "
      f"tensiunea în bandă {fmt(100 * in_banda, 2)} % din timp; abaterea maximă {fmt(100 * np.max(np.abs(Ur / U_ref - 1)), 2)} %")
verifica_adevarat("tensiunea reglată este în bandă peste 99 % din timp", in_banda > 0.99)
verifica("numărul de comutări = numărul de schimbări ale poziției", nc, int(np.sum(np.abs(np.diff(poz)))), rtol=0)
# fără reglaj (plot fix la poziția medie)
Ub0, _, _, _, _ = regulator_ploturi(t_d, U_IT_d, P_d, Q_d, RT, XT, U_ref, 1e9, T_int, pas, n0=int(np.round(np.mean(poz))))
print(f"  cu plotul blocat în poziția {int(np.round(np.mean(poz)))}: tensiunea variază între {fmt(Ub0.min() / 1e3, 3)} și "
      f"{fmt(Ub0.max() / 1e3, 3)} kV ({fmt(100 * (Ub0.max() - Ub0.min()) / U_ref, 2)} % din U_ref)")
# (d) compensarea căderii de tensiune (LDC) până la centrul de sarcină
Zl = (DATE["z1_cablu"] * DATE["l_cablu_F1"] + DATE["z1_lea20"] * DATE["l_lea_F1a"]) / 4
print(f"  centrul de sarcină: patru fidere ca F1a în paralel, Zl = {fmt(Zl.real, 3)} + j{fmt(Zl.imag, 3)} Ω")
Ub_f, Us_f, Ur_f, poz_f, nc_f = zi(Zl=Zl)
Ub_l, Us_l, Ur_l, poz_l, nc_l = zi(Zl=Zl, Zc=Zl)
print(f"  fără LDC: tensiunea în centrul de sarcină {fmt(Us_f.min() / 1e3, 3)} … {fmt(Us_f.max() / 1e3, 3)} kV "
      f"({nc_f} comutări)")
print(f"  cu LDC (Zc = Zl): tensiunea în centrul de sarcină {fmt(Us_l.min() / 1e3, 3)} … {fmt(Us_l.max() / 1e3, 3)} kV, "
      f"pe bara de 20 kV {fmt(Ub_l.min() / 1e3, 3)} … {fmt(Ub_l.max() / 1e3, 3)} kV ({nc_l} comutări)")
verifica("LDC: tensiunea estimată de regulator = tensiunea calculată în centrul de sarcină", Ur_l, Us_l, rtol=1e-9)
verifica_adevarat("LDC: tensiunea în centrul de sarcină rămâne în bandă peste 99 % din timp",
                  np.mean(np.abs(Us_l - U_ref) <= banda) > 0.99)
verifica_adevarat("fără LDC, tensiunea în centrul de sarcină iese din bandă mai mult de 10 % din timp",
                  np.mean(np.abs(Us_f - U_ref) <= banda) < 0.9)
print(f"  timpul în bandă al tensiunii din centrul de sarcină: fără LDC {fmt(100 * np.mean(np.abs(Us_f - U_ref) <= banda), 1)} %,"
      f" cu LDC {fmt(100 * np.mean(np.abs(Us_l - U_ref) <= banda), 1)} %")
verifica_adevarat("fără LDC, tensiunea minimă în centrul de sarcină este mai mică decât cu LDC", Us_f.min() < Us_l.min())

# (e) o treaptă de baterie de condensatoare pe bara B2: creșterea de tensiune
Qb = 2e6                                   # puterea treptei la 20 kV [var]
r_b = retea_referinta(c=1.0, cu_capacitati=False)
Zth = r_b.scurtcircuit_secvente("B2", "3f")["Zth"][1]
U0_B2 = 20e3
dU_aprox = Qb * Zth.imag / U0_B2**2
Cb = Qb / (W0 * U0_B2**2)                  # capacitatea pe fază (conexiune în stea) [F]
Zcb = 1 / (1j * W0 * Cb)                   # impedanța pe fază
E_th = U0_B2 / SQRT3
dU_exact = abs(E_th * Zcb / (Zth + Zcb)) / E_th - 1
# a treia cale: rețeaua de referință în coordonate de fază, cu condensatorul ca element concentrat
r_c = retea_referinta(c=1.0, cu_capacitati=False)
V_fara = abs(r_c.tensiuni_faze(r_c.rezolva_faze([]), "B2")[0])
r_c.capacitate("BC", "B2", Cb, Cb)
V_cu = abs(r_c.tensiuni_faze(r_c.rezolva_faze([]), "B2")[0])
dU_retea = V_cu / V_fara - 1
print(f"  treaptă de condensatoare de {fmt(Qb / 1e6, 0)} Mvar pe B2 (X_Th = {fmt(Zth.imag, 3)} Ω): ΔU/U ≈ Q·X/U² = "
      f"{fmt(100 * dU_aprox, 3)} %; exact (divizor de tensiune) {fmt(100 * dU_exact, 3)} %; rețeaua în coordonate de fază "
      f"{fmt(100 * dU_retea, 3)} %")
verifica("treapta de condensatoare: divizor Thevenin vs rețeaua în coordonate de fază", dU_exact, dU_retea, rtol=1e-3)
verifica("treapta de condensatoare: formula aproximativă (abatere relativă sub 3 %)", dU_aprox, dU_exact, rtol=3e-2)
verifica_adevarat("lățimea benzii regulatorului (2 %) depășește efectul unei trepte (fără pendulare)",
                  2 * 0.01 > dU_exact)

# ---------------------------------------------------------------------------
print("\nProblema 8.6 – regulatorul automat de tensiune al generatorului G1 (în gol)")
Td0 = GEN["Td0_t"]
TA = 0.02
dU = 0.01
for KA in (50.0, 200.0, 400.0):
    wn, zeta, er, supra, tp = rat_analitic(KA, TA, Td0)
    t, dE, dEfd = rat_ode(KA, TA, Td0, dU, 2.0)
    dE_lti = rat_lti(KA, TA, Td0, dU, t)
    yss = dU * KA / (1 + KA)
    # răspunsul analitic al sistemului de ordinul 2 (polii rădăcini ale lui TA·Td0·s² + (TA + Td0)·s + 1 + KA)
    p1, p2 = np.roots([TA * Td0, TA + Td0, 1 + KA])
    y_an = yss * np.real(1 - (p2 * np.exp(p1 * t) - p1 * np.exp(p2 * t)) / (p2 - p1))
    er_sim = 1 - dE[-1] / dU
    t90 = t[np.argmax(dE >= 0.9 * yss)]
    txt = f"  KA = {fmt(KA, 0)}: ωn = {fmt(wn, 1)} rad/s, ζ = {fmt(zeta, 3)}; eroarea staționară 1/(1 + KA) = " \
          f"{fmt(100 * er, 2)} % (simulare {fmt(100 * er_sim, 2)} %); 90 % din valoarea finală după {fmt(t90 * 1e3, 0)} ms"
    verifica(f"KA = {KA:g}: eroarea staționară analitic vs simulare", er, er_sim, rtol=1e-3)
    verifica(f"KA = {KA:g}: solve_ivp vs funcția de transfer", dE, dE_lti, rtol=0, atol=1e-7)
    verifica(f"KA = {KA:g}: solve_ivp vs soluția analitică", dE, y_an, rtol=0, atol=1e-7)
    if zeta < 1:
        kmax = np.argmax(dE)
        supra_sim = dE[kmax] / yss - 1
        txt += f"; suprareglarea {fmt(100 * supra, 1)} % (simulare {fmt(100 * supra_sim, 1)} %), timpul de vârf " \
               f"{fmt(tp * 1e3, 0)} ms (simulare {fmt(t[kmax] * 1e3, 0)} ms)"
        verifica(f"KA = {KA:g}: suprareglarea analitic vs simulare", supra, supra_sim, rtol=5e-3, atol=1e-4)
        verifica(f"KA = {KA:g}: timpul de vârf analitic vs simulare", tp, t[kmax], atol=1e-3, rtol=0)
    else:
        txt += "; răspuns aperiodic (ζ ≥ 1), fără suprareglare"
        verifica_adevarat(f"KA = {KA:g}: fără suprareglare în simulare", np.max(dE) <= yss * (1 + 1e-9))
    print(txt + f"; comanda inițială KA·ΔUref = {fmt(KA * dU, 2)} u.r., ΔEfd maxim (simulare) = {fmt(np.max(dEfd), 2)} u.r."
          f" = {fmt(np.max(dEfd) / dEfd[-1], 0)} × ΔEfd final ({fmt(dEfd[-1], 4)} u.r.)")
    verifica(f"KA = {KA:g}: ΔEfd final = ΔU final (generator în gol)", dEfd[-1], dE[-1], rtol=1e-4)
# fără regulator: constanta de timp Td0' (răspunsul la o treaptă a tensiunii de excitație)
t, dE, _ = rat_ode(1e-9, TA, Td0, 0.0, 1.0)
print(f"  comparație: fără regulator, tensiunea urmează excitația cu constanta de timp Td0' = {fmt(Td0, 1)} s;"
      f" cu KA = 200 timpul de vârf este de {fmt(rat_analitic(200.0, TA, Td0)[4] * 1e3, 0)} ms")
