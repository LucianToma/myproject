"""Capitolul 7 – Automatizări de rețea: rezolvarea și verificarea problemelor."""

import numpy as np
from scipy.optimize import brentq
from scipy.integrate import solve_ivp
from modele import (W0, F0, GEN, SQRT3, fmt, verifica, verifica_adevarat, unghi_critic, timp_critic,
                    retea_referinta)
from calcul_cap07 import (XD_T, XT, XL, XS, H, P0, ZB_IT, L_LINIE, X_LINIE_KM, x_retea, punct_functionare, pmax,
                          simuleaza, stabil, delta_max_arii, remanenta_analitic, remanenta_ode,
                          diferenta_tensiune, S_MOT, P_SARC, T0_REM, H_MOT, reglaje_R1, momente_aar,
                          T_DESC, T_AUX, T_INCH_R, T_MINU, U_PRAG)

T_PROT, T_CB, T_RELEU_INT = 0.03, 0.06, 0.01   # protecția de bază, întrerupătorul, releele intermediare [s]
T_Z2 = 0.30                                      # temporizarea treptei a 2-a a protecției de distanță (cap. 5) [s]

print("Problema 7.1 – punctul de funcționare al lui G1 și timpul critic de eliminare a unui defect")
op = punct_functionare()
E, d0 = op["E"], op["delta0"]
print(f"  baza: Sb = {fmt(GEN['Sn'] / 1e6, 0)} MVA, Ub = {fmt(GEN['UT2'] / 1e3, 0)} kV → Zb = {fmt(ZB_IT, 1)} Ω")
print(f"  x'd = {fmt(XD_T, 2)}; xT = {fmt(XT, 3)}; un circuit al liniei duble: {fmt(X_LINIE_KM, 2)}·{fmt(L_LINIE, 0)} km"
      f" = {fmt(X_LINIE_KM * L_LINIE, 0)} Ω = {fmt(XL, 4)} u.r.; xs = {fmt(XS, 2)}")
# Schema de studiu este separată de rețeaua de referință: comparăm puterile de scurtcircuit la C
Sk_studiu = GEN["Sn"] * (1 / (GEN["xd_s"] + XT) + 1 / (XL / 2 + XS))
r_ref = retea_referinta(cu_capacitati=False)
Sk_ref = SQRT3 * 110e3 * abs(r_ref.scurtcircuit_secvente("C", "3f")["I_faza"][0])
print(f"  S\"k la bara C în schema de studiu (E = 1, G1 + sistem) = {fmt(Sk_studiu / 1e6, 0)} MVA; "
      f"în rețeaua de referință (problema 1.2) = {fmt(Sk_ref / 1e6, 0)} MVA")
xI = XD_T + x_retea(2)
print(f"  reactanța borne G1 – sistem (ambele circuite) xT + xL/2 + xs = {fmt(x_retea(2), 4)} u.r.")
print(f"  reactanța totală (ambele circuite) = {fmt(xI, 4)} u.r.; Ut = 1 ∠ {fmt(np.degrees(op['theta_t']), 2)}°, "
      f"Q = {fmt(op['Q'], 4)} u.r.")
print(f"  E' = {fmt(abs(E), 4)} ∠ {fmt(np.degrees(d0), 2)}° (δ0 = {fmt(np.degrees(d0), 2)}°)")
P_din_E = abs(E) * 1.0 * np.sin(d0) / xI
verifica("P din E', δ0 și reactanța totală = P0", P_din_E, P0)
Pmax2 = pmax(2)
print(f"  Pmax = E'·V/x = {fmt(Pmax2, 4)} u.r. (rezerva statică Pmax/P0 = {fmt(Pmax2 / P0, 2)})")
dcr = unghi_critic(d0)
tcr = timp_critic(d0, H, P0)
print(f"  defect trifazat lângă bara C pe o plecare radială (Pe = 0 în timpul defectului, aceeași caracteristică după):")
print(f"  δcr = arccos[(π − 2δ0)·sin δ0 − cos δ0] = {fmt(np.degrees(dcr), 2)}°; tcr = √(4H(δcr − δ0)/(ω0·Pm)) = "
      f"{fmt(tcr * 1e3, 1)} ms")
print(f"  (în radiani: δ0 = {fmt(d0, 4)}, δcr = {fmt(dcr, 4)})")
# Calea independentă: bisecție pe timpul de eliminare, cu simularea completă (stabil / instabil)
lo, hi = 0.20, 0.27
verifica_adevarat("bisecția pornește dintr-un interval stabil–instabil",
                  stabil(simuleaza([(lo, 0.0), (5.0, Pmax2)], d0, t_final=5.0)[1]) and
                  not stabil(simuleaza([(hi, 0.0), (5.0, Pmax2)], d0, t_final=5.0)[1]))
while hi - lo > 1e-6:
    m = 0.5 * (lo + hi)
    if stabil(simuleaza([(m, 0.0), (5.0, Pmax2)], d0, t_final=5.0)[1]):
        lo = m
    else:
        hi = m
t_bis = 0.5 * (lo + hi)
print(f"  bisecție pe simularea completă: timpul critic = {fmt(t_bis * 1e3, 2)} ms")
verifica("tcr: formula criteriului ariilor vs bisecție pe simularea completă", tcr, t_bis, atol=5e-6, rtol=0)
# Verificări de consecvență (aceleași identități ca formula): parabola și egalitatea ariilor


def atinge(t, s):
    return s[0] - dcr


atinge.terminal = True
sol = solve_ivp(lambda t, s: [s[1], W0 / (2 * H) * P0], (0, 1), [d0, 0.0], events=atinge, rtol=1e-12, atol=1e-12)
t_num = sol.t_events[0][0]
print(f"  consecvență: integrarea cu Pe = 0 atinge δcr la {fmt(t_num * 1e3, 1)} ms")
verifica("tcr analitic vs integrare cu Pe = 0 (aceeași parabolă)", tcr, t_num)
A_acc = P0 * (dcr - d0)
du = np.pi - d0
A_fr = Pmax2 * (np.cos(dcr) - np.cos(du)) - P0 * (du - dcr)
print(f"  consecvență: aria de accelerare = {fmt(A_acc, 4)}; aria de frânare disponibilă = {fmt(A_fr, 4)} (u.r.·rad)")
verifica("la δcr aria de accelerare = aria de frânare (identitate)", A_acc, A_fr)
for k, verdict in ((0.98, True), (1.02, False)):
    t, d, _, _ = simuleaza([(k * tcr, 0.0), (3.0, Pmax2)], d0)
    print(f"  eliminare la {fmt(k, 2)}·tcr = {fmt(k * tcr * 1e3, 1)} ms: "
          f"{'stabil' if stabil(d) else 'instabil'} (δmax = {fmt(np.degrees(d.max()), 1) if stabil(d) else '> 180'}°)")
    verifica_adevarat(f"eliminare la {k}·tcr – {'stabil' if verdict else 'instabil'}", stabil(d) == verdict)
t_baza = T_PROT + T_CB
t_dist = T_PROT + T_Z2 + T_CB
for nume, t_el in ((f"protecția de bază ({fmt(T_PROT * 1e3, 0)} ms) + întrerupătorul ({fmt(T_CB * 1e3, 0)} ms)", t_baza),
                   (f"rezerva de la distanță: măsurare ({fmt(T_PROT * 1e3, 0)} ms) + treapta a 2-a "
                    f"({fmt(T_Z2 * 1e3, 0)} ms) + întrerupătorul ({fmt(T_CB * 1e3, 0)} ms), rețea presupusă intactă",
                    t_dist)):
    t, d, _, _ = simuleaza([(t_el, 0.0), (3.0, Pmax2)], d0)
    print(f"  {nume}: t = {fmt(t_el * 1e3, 0)} ms → {'stabil' if stabil(d) else 'instabil'}")
    verifica_adevarat(f"concluzia simulării concordă cu t {'<' if t_el < tcr else '>'} tcr", stabil(d) == (t_el < tcr))
# Cât de bună este ipoteza E' constant? Scăderea lui E' în timpul defectului (fără regulator de tensiune)
I0 = op["I"]
Eq0 = abs(op["Ut"] + 1j * GEN["xd"] * I0)
Td_t = GEN["Td0_t"] * (XD_T + XT) / (GEN["xd"] + XT)
E_inf = Eq0 * (XD_T + XT) / (GEN["xd"] + XT)
scadere = (abs(E) - E_inf) * (1 - np.exp(-tcr / Td_t)) / abs(E)
print(f"  E' constant – estimare: Eq0 = {fmt(Eq0, 3)}, T'd (defect în C) = T'd0·(x'd + xT)/(xd + xT) = {fmt(Td_t, 3)} s, "
      f"E'∞ = {fmt(E_inf, 3)} → până la tcr E' scade cu {fmt(100 * scadere, 1)} %")
# verificare: integrarea numerică a ecuației T'd·dE'/dt = E'∞ − E'
solE = solve_ivp(lambda t, e: [(E_inf - e[0]) / Td_t], (0, tcr), [abs(E)], rtol=1e-10, atol=1e-12)
verifica("scăderea lui E' până la tcr: formulă vs integrare", scadere, (abs(E) - solE.y[0, -1]) / abs(E))

print("\nProblema 7.2 – ciclul de reanclanșare pe fiderul F1 de 20 kV (releul R1 din problema 3.2)")
R1 = reglaje_R1()          # reglajele lui R1, citite din rezolvarea capitolului 3
I_def, t_r = R1["I_def"], R1["t_r"]
t_cb, t_inch = 0.06, 0.08          # timpul de deschidere și de închidere al întrerupătorului
t_m = [0.5, 15.0]                  # pauzele reglate (de la deschidere la comanda de închidere)
t_acc = 0.04                       # accelerarea după reanclanșare (declanșare fără temporizare dacă I > Is)
t_rev = 30.0                       # timpul de revenire
print(f"  R1: Is = {fmt(R1['Is'], 0)} A, TMS = {fmt(R1['TMS'], 2)}, I>> = {fmt(R1['I_inst'], 0)} A")
print(f"  defect trifazat permanent la capătul tronsonului B2–P1: I = {fmt(I_def, 0)} A < I>> = {fmt(R1['I_inst'], 0)} A"
      f" → treapta temporizată: t = {fmt(t_r, 4)} s; declanșare completă t + t_întrerupător = {fmt(t_r + t_cb, 4)} s")
print(f"  pauza reglată {fmt(t_m[0], 1)} s → pauza de tensiune (linia fără tensiune) = {fmt(t_m[0] + t_inch, 2)} s")


def ciclu_analitic(permanent, accelerare):
    """Momentele evenimentelor și durata totală a curentului de defect."""
    ev = [("deschis", t_r + t_cb)]
    pe = [t_r + t_cb]
    t = t_r + t_cb
    if not permanent:          # defect trecător, dispare în prima pauză
        t += t_m[0] + t_inch
        ev.append(("închis", t))
        ev.append(("revenire", t + t_rev))
        return dict(t_curent=sum(pe), t_final=t + t_rev, blocare=False, intrerupere=t_m[0] + t_inch, ev=ev)
    for tm in t_m:
        t += tm + t_inch
        ev.append(("închis", t))
        dur = (t_acc if accelerare else t_r) + t_cb
        pe.append(dur)
        t += dur
        ev.append(("deschis", t))
    ev.append(("blocat", t))
    return dict(t_curent=sum(pe), t_final=t, blocare=True, intrerupere=None, ev=ev)


def ciclu_simulat(permanent, accelerare, dt=1e-3, t_max=60.0):
    """Verificarea logicii (succesiunii): automat cu stări (închis / pauză / blocat) simulat pas
    cu pas; temporizarea releului este aceeași funcție ca în calculul analitic."""
    stare, t, acc_rel, ceas, impuls = "inchis", 0.0, 0.0, 0.0, 0
    defect = True
    t_curent, t_ultim_inch = 0.0, 0.0
    cmd_desc, cmd_inch = None, None
    jurnal = []
    while t < t_max:
        curent = defect and stare == "inchis"
        if curent:
            t_curent += dt
            if cmd_desc is None:
                if impuls > 0 and accelerare and t - t_ultim_inch <= t_rev:
                    acc_rel += dt / t_acc
                else:
                    acc_rel += dt / t_r
                if acc_rel >= 1.0 - 1e-9:
                    cmd_desc = t + dt
        if cmd_desc is not None and t + dt >= cmd_desc + t_cb - 1e-9 and stare == "inchis":
            stare, ceas, acc_rel, cmd_desc = "pauza", 0.0, 0.0, None
            jurnal.append(("deschis", round(t + dt, 3)))
            if not permanent:
                defect = False
            if impuls >= len(t_m):
                stare = "blocat"
                jurnal.append(("blocat", round(t + dt, 3)))
                break
        elif stare == "pauza":
            ceas += dt
            if ceas >= t_m[impuls] - 1e-9 and cmd_inch is None:
                cmd_inch = t + dt
            if cmd_inch is not None and t + dt >= cmd_inch + t_inch - 1e-9:
                stare, cmd_inch = "inchis", None
                impuls += 1
                t_ultim_inch = t + dt
                jurnal.append(("închis", round(t + dt, 3)))
        elif stare == "inchis" and not defect and t - t_ultim_inch >= t_rev - 1e-9 and impuls > 0:
            jurnal.append(("revenire", round(t, 3)))
            break
        t += dt
    return dict(t_curent=t_curent, t_final=jurnal[-1][1], jurnal=jurnal)


for permanent, accelerare, nume in ((False, False, "defect trecător"), (True, False, "defect permanent, fără accelerare"),
                                    (True, True, "defect permanent, cu accelerare după reanclanșare")):
    a = ciclu_analitic(permanent, accelerare)
    s = ciclu_simulat(permanent, accelerare)
    txt = f"  {nume}: curentul de defect circulă în total {fmt(a['t_curent'], 3)} s; "
    txt += ("blocare la t = " if a["blocare"] else "ciclu încheiat (revenire) la t = ") + f"{fmt(a['t_final'], 3)} s"
    if a["intrerupere"]:
        txt += f"; consumatorii sunt întrerupți {fmt(a['intrerupere'], 2)} s"
    print(txt)
    print("     analitic:", "; ".join(f"{e} {fmt(tt, 3)} s" for e, tt in a["ev"]))
    print("     simulare (pas 1 ms):", "; ".join(f"{e} {fmt(tt, 3)} s" for e, tt in s["jurnal"]))
    verifica_adevarat(f"{nume}: aceeași succesiune de evenimente", [e for e, _ in a["ev"]] == [e for e, _ in s["jurnal"]])
    verifica(f"{nume}: durata curentului, analitic vs automat simulat", a["t_curent"], s["t_curent"], atol=3e-3, rtol=0)
    verifica(f"{nume}: momentul final, analitic vs automat simulat", a["t_final"], s["t_final"], atol=5e-3, rtol=0)
    I2t = I_def**2 * a["t_curent"]
    print(f"     I²t = {fmt(I2t / 1e6, 2)}·10⁶ A²s (cablul de 185 mm² Al admite (k·S)² = {fmt((94 * 185)**2 / 1e6, 0)}·10⁶ A²s)")
    verifica_adevarat(f"{nume}: I²t sub limita adiabatică a cablului", I2t < (94 * 185)**2)

print("\nProblema 7.3 – RAR trifazată pe linia dublă C–sistem: reușită și pe defect permanent")
Pmax1 = pmax(1)
print(f"  Pmax: ambele circuite {fmt(Pmax2, 4)}; un circuit {fmt(Pmax1, 4)}; defect lângă C: 0")
t_c, t_c2 = 0.12, 0.12      # eliminarea defectului inițial și a celui de după reanclanșare (date de problemă)


def analiza_rar(tm, permanent, t2=t_c2, afiseaza=True, t_final=6.0):
    """tm = pauza de tensiune (circuitul deschis la ambele capete, reanclanșare simultană – idealizare)."""
    etape = [(t_c, 0.0), (tm, Pmax1), (t2, 0.0), (t_final, Pmax1)] if permanent else \
        [(t_c, 0.0), (tm, Pmax1), (t_final, Pmax2)]
    t, d, w, start = simuleaza(etape, d0, t_final=t_final)
    eticheta = f"t_m = {tm} s, {'permanent' if permanent else 'trecător'}" + (f", t2 = {t2} s" if permanent else "")
    # verificare 1: în etapele cu Pe = 0 unghiul crește parabolic (soluție analitică)
    for (t0, ds, ws, Pk), (dur, _) in zip(start, etape):
        if Pk == 0.0 and t0 + dur <= t[-1]:
            d_an = ds + ws * dur + W0 * P0 / (4 * H) * dur**2
            verifica(f"{eticheta}: δ la sfârșitul defectului, parabolă vs integrare numerică",
                     np.interp(t0 + dur, t, d), d_an, rtol=1e-4)
    # verificare 2: bilanțul de energie (criteriul ariilor) pentru ultima etapă
    t0f, dsf, wsf, Pf = start[-1]
    dmax_ar = delta_max_arii(dsf, wsf, Pf)
    st = stabil(d)
    if st:
        verifica(f"{eticheta}: δmax în ultima etapă, simulare vs bilanțul de energie", d[t >= t0f].max(), dmax_ar,
                 rtol=2e-3)
    else:
        verifica_adevarat(f"{eticheta}: instabil și după bilanțul de energie", dmax_ar is None)
    tr = start[2][0]
    dmax_dupa = d[t >= tr].max() if st else None
    return dict(st=st, start=start, dmax_dupa=dmax_dupa, dmax_ar=dmax_ar)


cazuri = {}
for tm in (0.5, 0.8):
    for permanent in (False, True):
        rz = analiza_rar(tm, permanent)
        cazuri[(tm, permanent)] = rz
        tr, dr, wr, _ = rz["start"][2]
        print(f"  pauză {fmt(tm, 1)} s, defect {'permanent' if permanent else 'trecător'}: la reanclanșare (t = "
              f"{fmt(tr, 2)} s) δ = {fmt(np.degrees(dr), 1)}°, rotorul se mișcă {'înainte' if wr > 0 else 'înapoi'} "
              f"(Δω = {fmt(wr, 2)} rad/s) → "
              f"{'stabil, δmax după reanclanșare = ' + fmt(np.degrees(rz['dmax_dupa']), 1) + '°' if rz['st'] else 'INSTABIL (G1 iese din sincronism)'}")
        if permanent:
            tf, df_, wf, _ = rz["start"][3]
            print(f"     după eliminarea celui de-al doilea defect (t = {fmt(tf, 2)} s): δ = {fmt(np.degrees(df_), 1)}°, "
                  f"Δω = {fmt(wf, 2)} rad/s; bilanțul de energie: "
                  f"{'δmax = ' + fmt(np.degrees(rz['dmax_ar']), 1) + '°' if rz['dmax_ar'] is not None else 'aria de frânare nu ajunge'}")
t, d, _, _ = simuleaza([(t_c, 0.0), (6.0, Pmax1)], d0, t_final=6.0)
print(f"  fără RAR (circuitul rămâne deschis): stabil = {stabil(d)}, δmax = {fmt(np.degrees(d.max()), 1)}° (prima oscilație)")
verifica_adevarat("fără RAR sistemul rămâne stabil", stabil(d))
verifica_adevarat("RAR reușită este stabilă pentru ambele pauze", all(v["st"] for k, v in cazuri.items() if not k[1]))
verifica_adevarat("reanclanșarea pe defect permanent după 0,8 s este instabilă, după 0,5 s stabilă",
                  cazuri[(0.5, True)]["st"] and not cazuri[(0.8, True)]["st"])
# Durata celui de-al doilea defect (pauza 0,5 s, defect permanent)
for t2 in (0.30, 0.35):
    rz = analiza_rar(0.5, True, t2=t2)
    print(f"  pauză 0,5 s, defect permanent, al doilea defect eliminat în {fmt(t2, 2)} s: "
          f"{'stabil, δmax după reanclanșare = ' + fmt(np.degrees(rz['dmax_dupa']), 1) + '°' if rz['st'] else 'INSTABIL'}")
verifica_adevarat("eliminarea lentă (0,35 s) a celui de-al doilea defect duce la instabilitate",
                  analiza_rar(0.5, True, t2=0.30)["st"] and not analiza_rar(0.5, True, t2=0.35)["st"])
# Explorarea pauzei: pentru ce pauze reanclanșarea pe defect permanent este instabilă?
tms = np.round(np.arange(0.2, 1.801, 0.02), 2)
instabil = []
for tm in tms:
    t, d, _, _ = simuleaza([(t_c, 0.0), (tm, Pmax1), (t_c2, 0.0), (5.0, Pmax1)], d0, t_final=5.0)
    if not stabil(d):
        instabil.append(tm)
grupe = []
for tm in instabil:
    if grupe and abs(tm - grupe[-1][1] - 0.02) < 1e-9:
        grupe[-1][1] = tm
    else:
        grupe.append([tm, tm])
print("  pauze (pas 0,02 s, între 0,2 și 1,8 s) pentru care reanclanșarea pe defect permanent este instabilă: " +
      "; ".join(f"{fmt(a, 2)}…{fmt(b, 2)} s" for a, b in grupe))
verifica_adevarat("instabilitatea apare în ferestre separate de aproximativ o perioadă de oscilație",
                  len(grupe) >= 2 and 0.6 < grupe[1][0] - grupe[0][0] < 0.9)
verifica_adevarat("a doua fereastră este cuprinsă complet în intervalul explorat", grupe[1][1] < tms[-1])
# Perioada oscilațiilor mici după deschiderea unui circuit (explică dependența de pauză)
de1 = np.arcsin(P0 / Pmax1)
fn = np.sqrt(W0 * Pmax1 * np.cos(de1) / (2 * H)) / (2 * np.pi)
print(f"  oscilațiile mici cu un circuit: δe = {fmt(np.degrees(de1), 2)}°, f = {fmt(fn, 3)} Hz, perioada {fmt(1 / fn, 3)} s")
t, d, w, _ = simuleaza([(t_c, 0.0), (6.0, Pmax1)], d0, t_final=6.0)
i_max = [i for i in range(1, len(w)) if w[i - 1] > 0 >= w[i]]      # maxime: Δω trece din + în −
T_sim = t[i_max[1]] - t[i_max[0]]
print(f"  perioada din simulare (oscilație mare, neliniară, neamortizată) = {fmt(T_sim, 3)} s")
verifica_adevarat("perioada oscilației mari este mai lungă decât cea a oscilațiilor mici", T_sim > 1 / fn)
# Unghiul pe întrerupătorul deschis al circuitului 1 (pentru controlul sincronismului):
# între bara C și bara stației îndepărtate R (capătul circuitului), adică peste reactanța xL
de_s = np.arcsin(P0 * (XD_T + x_retea(1)) / abs(E))
I1 = (abs(E) * np.exp(1j * de_s) - 1.0) / (1j * (XD_T + x_retea(1)))
UR = 1.0 + 1j * XS * I1
UC = UR + 1j * XL * I1
theta_CR = np.angle(UC / UR)
print(f"  regim staționar cu un circuit: |UC| = {fmt(abs(UC), 4)}, |UR| = {fmt(abs(UR), 4)}; unghiul pe întrerupătorul "
      f"deschis (între bara C și bara stației îndepărtate) = {fmt(np.degrees(theta_CR), 2)}°")
verifica("unghiul pe întrerupătorul deschis: fazori vs P = UC·UR·sin θ/xL",
         theta_CR, np.arcsin(P0 * XL / (abs(UC) * abs(UR))))

print("\nProblema 7.4 – sincronizarea lui G1: unghiul de avans al comenzii de închidere")
df, t_close, a_f = 0.10, 0.08, 0.05
alfa = 360 * df * t_close
alfa_a = 360 * (df * t_close + 0.5 * a_f * t_close**2)
print(f"  (a) Δf = {fmt(df, 2)} Hz, t_î = {fmt(t_close * 1e3, 0)} ms → α = 360°·Δf·t_î = {fmt(alfa, 3)}°")
print(f"  (b) cu accelerația a = {fmt(a_f, 2)} Hz/s: α = 360°·(Δf·t_î + a·t_î²/2) = {fmt(alfa_a, 4)}° "
      f"(termenul de accelerație: {fmt(360 * 0.5 * a_f * t_close**2, 4)}°)")
# Verificarea de consecvență pentru (a): legea liniară eșantionată cu pas de 10 µs
dt = 1e-5
t = np.arange(0, 12, dt)
phi = -180 + 360 * df * t
i_cmd = np.argmax(phi >= -alfa)
phi_inchidere = phi[min(i_cmd + int(round(t_close / dt)), len(t) - 1)]
print(f"  (a) simulare: comanda la φ = {fmt(phi[i_cmd], 3)}°, închiderea la φ = {fmt(phi_inchidere, 3)}°")
verifica("(a) unghiul la închidere ≈ 0", phi_inchidere, 0.0, atol=360 * df * dt * 2, rtol=0)
# (b) frecvența de alunecare crește liniar de la 0,02 Hz; unghiul inițial este ales astfel încât
# sincronizatorul să dea comanda când alunecarea este 0,10 Hz; unghiul se obține integrând numeric frecvența
f0s = 0.02
t_star = (df - f0s) / a_f
phi0 = -alfa_a - 360 * (f0s * t_star + 0.5 * a_f * t_star**2)
f_t = f0s + a_f * t
phi_a = phi0 + 360 * np.concatenate(([0.0], np.cumsum((f_t[1:] + f_t[:-1]) / 2) * dt))
alfa_t = 360 * (f_t * t_close + 0.5 * a_f * t_close**2)
i_cmd = np.argmax(phi_a >= -alfa_t)
phi_inch_a = phi_a[i_cmd + int(round(t_close / dt))]
print(f"  (b) simulare: alunecarea crește de la {fmt(f0s, 2)} Hz cu {fmt(a_f, 2)} Hz/s, unghiul inițial {fmt(phi0, 2)}°; "
      f"comanda la t = {fmt(t[i_cmd], 4)} s, Δf = {fmt(f_t[i_cmd], 4)} Hz; închiderea la φ = {fmt(phi_inch_a, 4)}°")
verifica("(b) comanda se dă la alunecarea de 0,10 Hz", f_t[i_cmd], df, atol=1e-4, rtol=0)
verifica("(b) unghiul la închidere ≈ 0 (integrarea numerică a frecvenței)", phi_inch_a, 0.0, atol=0.01, rtol=0)
phi_fara = phi_a[np.argmax(phi_a >= -360 * f_t * t_close) + int(round(t_close / dt))]
print(f"  (b) dacă sincronizatorul ignoră accelerația, închiderea se face la φ = {fmt(phi_fara, 3)}°")
verifica("(b) eroarea fără termenul de accelerație ≈ 360°·a·t_î²/2", phi_fara, 360 * 0.5 * a_f * t_close**2,
         atol=0.01, rtol=0)
x_tot = GEN["xd_s"] + XT + XL / 2 + XS
print(f"  (c) curentul de egalizare la închiderea cu decalaj (x\"d + xT + xL/2 + xs = {fmt(x_tot, 4)} u.r.):")
for phi_e in (alfa, 10.0, 30.0, 90.0, 180.0):
    dU = 2 * np.sin(np.radians(phi_e) / 2)
    I_f = abs(np.exp(1j * np.radians(phi_e)) - 1.0) / x_tot
    print(f"    φ = {fmt(phi_e, 2)}°: |ΔU| = 2·sin(φ/2) = {fmt(dU, 3)} u.r. → I = {fmt(I_f, 2)} u.r.·In "
          f"(scurtcircuit la borne: 1/x\"d = {fmt(1 / GEN['xd_s'], 1)} u.r.)")
    verifica(f"|ΔU|: 2·sin(φ/2) vs |1 − e^(jφ)| la {phi_e:g}° (identitate)", dU, abs(np.exp(1j * np.radians(phi_e)) - 1.0))

print("\nProblema 7.5 – AAR pe bara de 6 kV a motoarelor (transfer rapid și transfer la tensiune remanentă)")
print(f"  date (baza S_motoare = {fmt(S_MOT / 1e6, 1)} MVA): sarcina mecanică p = {fmt(P_SARC, 2)} u.r. (cuplu ∝ ω²), "
      f"H = {fmt(H_MOT, 2)} s, T0 = {fmt(T0_REM, 2)} s; la t = 0: Ur = 1 u.r., alunecare nulă")
t_ev = np.linspace(0, 2.0, 20001)
w_a, U_a, th_a = remanenta_analitic(t_ev)
w_o, U_o, th_o = remanenta_ode(t_ev)
for tt in (0.05, 0.1, 0.2, 0.5, 1.0):
    i = int(round(tt / (t_ev[1] - t_ev[0])))
    print(f"  t = {fmt(tt, 2)} s: n = {fmt(w_a[i], 4)}·n0 (f = {fmt(F0 * w_a[i], 2)} Hz), U = {fmt(U_a[i], 3)} u.r., "
          f"θ = {fmt(np.degrees(th_a[i]), 1)}°, |ΔU| = {fmt(diferenta_tensiune(U_a[i], th_a[i]), 3)} u.r.")
verifica("turația: formulă vs integrarea numerică a ecuațiilor diferențiale", w_a, w_o, rtol=1e-6)
verifica("tensiunea remanentă: formulă vs integrare numerică", U_a, U_o, rtol=1e-6)
verifica("unghiul: formulă vs integrare numerică", th_a, th_o, rtol=1e-5, atol=1e-6)
# Fereastra transferului rapid: |ΔU| ≤ 1 u.r. (curentul de reconectare cel mult egal cu cel de pornire)
f_dU = lambda tt: diferenta_tensiune(*remanenta_analitic(tt)[1:]) - 1.0  # noqa: E731
dU_a = diferenta_tensiune(U_a, th_a)
i1 = np.argmax(dU_a >= 1.0)
t_fer = brentq(f_dU, t_ev[i1 - 1], t_ev[i1])
dU_o = diferenta_tensiune(U_o, th_o)
t_fer_o = t_ev[np.argmax(dU_o >= 1.0)]
print(f"  fereastra transferului rapid (|ΔU| ≤ 1 u.r.) se închide la t = {fmt(t_fer * 1e3, 1)} ms "
      f"(din integrarea numerică: {fmt(t_fer_o * 1e3, 1)} ms); θ = {fmt(np.degrees(remanenta_analitic(t_fer)[2]), 1)}°")
verifica("sfârșitul ferestrei rapide: formulă vs integrare numerică", t_fer, t_fer_o, atol=2e-4, rtol=0)
nume_pornire = {"a": "comanda de declanșare a întrerupătorului de lucru (t = 0 la deschiderea lui)",
                "b": "pierderea alimentării în amonte, semnal de pornire imediat",
                "c": f"protecția de minimă tensiune, temporizare {fmt(T_MINU, 2)} s"}
momente = momente_aar()
for (pornire, mod), tp in momente.items():
    if pornire == "c":
        continue
    _, Up, thp = remanenta_analitic(np.array(tp))
    dUp = diferenta_tensiune(Up, thp)
    i = int(round(tp / (t_ev[1] - t_ev[0])))
    dUp_o = diferenta_tensiune(U_o[i], th_o[i])
    admis = bool(dUp <= 1.0)
    print(f"  ({pornire}) {nume_pornire[pornire]}, transfer {mod}: închiderea rezervei la t = {fmt(tp * 1e3, 0)} ms, "
          f"θ = {fmt(np.degrees(thp), 1)}°, Ur = {fmt(Up, 3)}, |ΔU| = {fmt(dUp, 3)} u.r. → "
          f"{'admis' if admis else 'NEADMIS'}")
    verifica(f"({pornire}, {mod}) |ΔU|: formulă vs integrare numerică", dUp, dUp_o, rtol=1e-5)
    verifica_adevarat(f"({pornire}, {mod}) comparația cu fereastra concordă cu |ΔU| calculat", (tp < t_fer) == admis)
# (c) pornirea de la minimă tensiune: AAR poate închide cel mai devreme la momente[("c", ...)]
tc_min = momente[("c", "secvențial")]
fer = (t_ev >= tc_min - 0.05) & (t_ev <= tc_min + 0.05)
print(f"  (c) {nume_pornire['c']}: închiderea ar fi posibilă cel mai devreme la t = {fmt(tc_min * 1e3, 0)} ms, după "
      f"închiderea ferestrei rapide; între {fmt((tc_min - 0.05) * 1e3, 0)} și {fmt((tc_min + 0.05) * 1e3, 0)} ms "
      f"|ΔU| variază între {fmt(dU_a[fer].min(), 3)} și {fmt(dU_a[fer].max(), 3)} u.r. "
      f"(alunecarea ≈ {fmt(F0 * (1 - remanenta_analitic(tc_min)[0]), 1)} Hz) → fără măsurarea unghiului "
      f"se așteaptă Ur ≤ {fmt(U_PRAG, 2)} u.r.")
verifica_adevarat("(c) în jurul momentului posibil |ΔU| trece de ambele părți ale lui 1 u.r. (închidere la întâmplare)",
                  dU_a[fer].min() < 1.0 < dU_a[fer].max())
verifica_adevarat("(c) momentul posibil este după fereastra rapidă", tc_min > t_fer)
# Transferul în fază: prima trecere a unghiului prin 360°
t_faza = brentq(lambda tt: remanenta_analitic(tt)[2] - 2 * np.pi, 0.05, 1.0)
w_f, U_f, _ = remanenta_analitic(np.array(t_faza))
alun = F0 * (1 - w_f)
avans = np.degrees(remanenta_analitic(np.array(t_faza))[2] - remanenta_analitic(np.array(t_faza - T_INCH_R))[2])
t_faza_o = t_ev[np.argmax(th_o >= 2 * np.pi)]
print(f"  transfer în fază: prima coincidență de fază la t = {fmt(t_faza * 1e3, 0)} ms (numeric {fmt(t_faza_o * 1e3, 0)} ms), "
      f"Ur = {fmt(U_f, 3)} u.r., alunecarea = {fmt(alun, 2)} Hz; comanda de închidere trebuie dată cu "
      f"{fmt(avans, 0)}° înainte (pentru {fmt(T_INCH_R * 1e3, 0)} ms)")
verifica("prima coincidență de fază: formulă vs integrare numerică", t_faza, t_faza_o, atol=2e-4, rtol=0)
# Transferul fără măsurarea unghiului: se așteaptă Ur ≤ U_prag; atunci |ΔU| ≤ 1 + U_prag pentru orice unghi
t_rem = brentq(lambda tt: remanenta_analitic(tt)[1] - U_PRAG, 0.01, 5.0)
t_rem_o = t_ev[np.argmax(U_o <= U_PRAG)]
w_rem, _, _ = remanenta_analitic(np.array(t_rem))
t_inch_rem = max(t_rem, T_MINU + T_DESC + T_AUX) + T_INCH_R
_, U_ir, th_ir = remanenta_analitic(np.array(t_inch_rem))
print(f"  Ur scade la {fmt(U_PRAG, 2)} u.r. după {fmt(t_rem, 3)} s (numeric {fmt(t_rem_o, 3)} s), la turația "
      f"{fmt(w_rem, 3)}·n0; închiderea rezervei la {fmt(t_inch_rem, 3)} s: Ur = {fmt(U_ir, 3)} u.r., "
      f"|ΔU| = {fmt(diferenta_tensiune(U_ir, th_ir), 3)} u.r. (garantat ≤ {fmt(1 + U_PRAG, 2)} u.r. oricare ar fi unghiul)")
verifica("momentul Ur = U_prag: formulă vs integrare numerică", t_rem, t_rem_o, atol=2e-4, rtol=0)
verifica_adevarat("|ΔU| ≤ 1 + U_prag", diferenta_tensiune(U_ir, th_ir) <= 1 + U_PRAG + 1e-12)
for prag in (0.25,):
    t_p = brentq(lambda tt: remanenta_analitic(tt)[1] - prag, 0.01, 5.0)
    print(f"  pentru comparație, cu pragul {fmt(prag, 2)} u.r.: t = {fmt(t_p, 3)} s, |ΔU| poate ajunge la {fmt(1 + prag, 2)} u.r.")

print("\nProblema 7.6 – protecția la refuzul întrerupătorului (50BF): reglajul temporizării și timpul total")
t_reset, marja = 0.015, 0.04
# comanda protecției de bază ajunge direct la bobina de declanșare (contactele de ieșire ale terminalului);
# comenzile 50BF spre întrerupătoarele vecine trec prin relee intermediare (T_RELEU_INT)
t_BF_min = T_CB + t_reset + marja
t_BF = np.ceil(t_BF_min * 100) / 100
t_total_BF = T_PROT + t_BF + T_RELEU_INT + T_CB
print(f"  t_BF ≥ t_întrerupere + t_revenire detector + marjă = {fmt(T_CB, 3)} + {fmt(t_reset, 3)} + {fmt(marja, 3)} = "
      f"{fmt(t_BF_min, 3)} s → reglat {fmt(t_BF, 2)} s")
print(f"  eliminarea la refuzul întrerupătorului: t_prot + t_BF + t_relee + t_întrerupătoare vecine = "
      f"{fmt(T_PROT, 2)} + {fmt(t_BF, 2)} + {fmt(T_RELEU_INT, 2)} + {fmt(T_CB, 2)} = {fmt(t_total_BF, 2)} s "
      f"(tcr = {fmt(tcr, 3)} s, rezervă {fmt((tcr - t_total_BF) * 1e3, 0)} ms)")
t_BF_max = tcr - (T_PROT + T_RELEU_INT + T_CB)
print(f"  temporizarea maximă compatibilă cu stabilitatea: t_BF ≤ tcr − (t_prot + t_relee + t_întrerupător) = "
      f"{fmt(t_BF_max * 1e3, 0)} ms")
t_BF_int = np.ceil((T_RELEU_INT + T_CB + t_reset + marja) * 100) / 100
print(f"  dacă și comanda de bază ar trece printr-un releu intermediar: t_BF ≥ {fmt(T_RELEU_INT + T_CB + t_reset + marja, 3)} s"
      f" → {fmt(t_BF_int, 2)} s, iar timpul total ar fi {fmt(T_PROT + t_BF_int + T_RELEU_INT + T_CB, 2)} s")
for nume, t_el in (("refuz de întrerupător, eliminat de 50BF", t_total_BF),
                   (f"refuz de întrerupător, rezerva de la distanță ({fmt(T_PROT, 2)} + {fmt(T_Z2, 2)} + {fmt(T_CB, 2)} s), "
                    f"rețea presupusă intactă", t_dist)):
    t, d, _, _ = simuleaza([(t_el, 0.0), (3.0, Pmax2)], d0)
    print(f"  {nume}: {fmt(t_el, 2)} s → {'stabil' if stabil(d) else 'instabil'}")
    verifica_adevarat(f"{nume}: simularea concordă cu comparația cu tcr", stabil(d) == (t_el < tcr))
