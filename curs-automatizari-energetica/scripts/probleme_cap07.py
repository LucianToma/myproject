"""Capitolul 7 – Automatizări de rețea: rezolvarea și verificarea problemelor."""

import numpy as np
from scipy.optimize import brentq
from scipy.integrate import solve_ivp
from modele import (W0, F0, GEN, MOTOR, fmt, verifica, verifica_adevarat, unghi_critic, timp_critic,
                    retea_referinta, timp_invers, timp_integrator)
from calcul_cap07 import (XD_T, XT, XL, XS, H, P0, ZB_IT, L_LINIE, X_LINIE_KM, x_retea, punct_functionare, pmax,
                          simuleaza, stabil, delta_max_arii, potential, remanenta_analitic, remanenta_ode,
                          diferenta_tensiune, S_MOT, P_SARC, T0_REM, H_MOT)

print("Problema 7.1 – punctul de funcționare al lui G1 și timpul critic de eliminare a unui defect")
op = punct_functionare()
E, d0 = op["E"], op["delta0"]
print(f"  baza: Sb = {fmt(GEN['Sn'] / 1e6, 0)} MVA, Ub = {fmt(GEN['UT2'] / 1e3, 0)} kV → Zb = {fmt(ZB_IT, 1)} Ω")
print(f"  x'd = {fmt(XD_T, 2)}; xT = {fmt(XT, 3)}; un circuit al liniei duble: {fmt(X_LINIE_KM, 2)}·{fmt(L_LINIE, 0)} km"
      f" = {fmt(X_LINIE_KM * L_LINIE, 0)} Ω = {fmt(XL, 4)} u.r.; xs = {fmt(XS, 2)}")
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
# Calea 2: integrarea numerică a ecuației mișcării cu Pe = 0 până când δ atinge δcr


def atinge(t, s):
    return s[0] - dcr


atinge.terminal = True
sol = solve_ivp(lambda t, s: [s[1], W0 / (2 * H) * P0], (0, 1), [d0, 0.0], events=atinge, rtol=1e-12, atol=1e-12)
t_num = sol.t_events[0][0]
print(f"  integrare numerică: δ atinge δcr la t = {fmt(t_num * 1e3, 1)} ms")
verifica("tcr analitic vs integrare numerică", tcr, t_num)
# Calea 3: criteriul ariilor verificat prin simulare – stabil sub tcr, instabil peste
for k, verdict in ((0.98, True), (1.02, False)):
    t, d, _, _ = simuleaza([(k * tcr, 0.0), (3.0, Pmax2)], d0)
    print(f"  eliminare la {fmt(k, 2)}·tcr = {fmt(k * tcr * 1e3, 1)} ms: "
          f"{'stabil' if stabil(d) else 'instabil'} (δmax = {fmt(np.degrees(d.max()), 1) if stabil(d) else '> 180'}°)")
    verifica_adevarat(f"eliminare la {k}·tcr – {'stabil' if verdict else 'instabil'}", stabil(d) == verdict)
# Ariile la eliminarea în tcr: accelerare = frânare
A_acc = P0 * (dcr - d0)
du = np.pi - d0
A_fr = Pmax2 * (np.cos(dcr) - np.cos(du)) - P0 * (du - dcr)
print(f"  aria de accelerare = {fmt(A_acc, 4)}; aria de frânare disponibilă = {fmt(A_fr, 4)} (u.r.·rad)")
verifica("la δcr aria de accelerare = aria de frânare", A_acc, A_fr)
for nume, t_el in (("protecția de bază (30 ms) + întrerupătorul (60 ms)", 0.09),
                   ("rezerva de la distanță: treapta a 2-a (350 ms) + întrerupătorul (60 ms)", 0.41)):
    t, d, _, _ = simuleaza([(t_el, 0.0), (3.0, Pmax2)], d0)
    print(f"  {nume}: t = {fmt(t_el * 1e3, 0)} ms → {'stabil' if stabil(d) else 'instabil'}")
    verifica_adevarat(f"concluzia simulării concordă cu t {'<' if t_el < tcr else '>'} tcr", stabil(d) == (t_el < tcr))

print("\nProblema 7.2 – ciclul de reanclanșare pe fiderul F1 de 20 kV (releul R1 din problema 3.2)")
# Reglajele lui R1 din problema 3.2 (citite din rezolvarea capitolului 3, aceeași sursă de adevăr)
import contextlib, io, runpy  # noqa: E401,E402
from pathlib import Path  # noqa: E402
with contextlib.redirect_stdout(io.StringIO()):
    _P3 = runpy.run_path(str(Path(__file__).with_name("probleme_cap03.py")))
Is, TMS, I_inst, t_inst = _P3["relee"]["R1"]["Is"], _P3["relee"]["R1"]["TMS"], _P3["I_inst_R1"], _P3["T_INST"]
r = retea_referinta(cu_capacitati=False)
I_def = abs(r.scurtcircuit_secvente("P1", "3f")["I_faza"][0])
t_r = float(timp_invers(I_def, Is, TMS)) if I_def < I_inst else t_inst
t_cb, t_inch = 0.06, 0.08          # timpul de deschidere și de închidere al întrerupătorului
t_m = [0.5, 15.0]                  # pauzele de RAR (prima rapidă, a doua lentă)
t_acc = 0.04                       # accelerarea după reanclanșare (declanșare fără temporizare dacă I > Is)
t_rev = 30.0                       # timpul de revenire (blocare a numărării)
print(f"  defect trifazat permanent la capătul tronsonului B2–P1: I = {fmt(I_def, 0)} A < I>> = {fmt(I_inst, 0)} A"
      f" → treapta temporizată: t = {fmt(t_r, 3)} s")


def ciclu_analitic(permanent, accelerare):
    """Durata totală a curentului de defect și momentul final (blocare sau revenire)."""
    pe = [t_r + t_cb]
    t = t_r + t_cb
    if not permanent:          # defect trecător, dispare în prima pauză
        return dict(t_curent=t, t_final=t + t_m[0] + t_inch + t_rev, blocare=False,
                    intrerupere=t_m[0] + t_inch)
    for tm in t_m:
        t += tm + t_inch
        dur = (t_acc if accelerare else t_r) + t_cb
        pe.append(dur)
        t += dur
    return dict(t_curent=sum(pe), t_final=t, blocare=True, intrerupere=None)


def ciclu_simulat(permanent, accelerare, dt=1e-3, t_max=60.0):
    """Calea 2: automat cu stări (închis / pauză / blocat) simulat pas cu pas; releul
    temporizat este modelat prin integrator (se resetează la deschiderea întrerupătorului)."""
    stare, t, acc_rel, ceas, impuls = "inchis", 0.0, 0.0, 0.0, 0
    defect = True
    t_curent, t_ultim_inch = 0.0, 0.0
    cmd_desc, cmd_inch = None, None
    jurnal = []
    while t < t_max:
        curent = defect and stare in ("inchis",)
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
    print("     simulare:", "; ".join(f"{e} {fmt(tt, 3)} s" for e, tt in s["jurnal"]))
    verifica(f"{nume}: durata curentului, analitic vs automat simulat", a["t_curent"], s["t_curent"], atol=3e-3, rtol=0)
    verifica(f"{nume}: momentul final, analitic vs automat simulat", a["t_final"], s["t_final"], atol=5e-3, rtol=0)
    I2t = I_def**2 * a["t_curent"]
    print(f"     I²t = {fmt(I2t / 1e6, 2)}·10⁶ A²s (cablul de 185 mm² Al admite (k·S)² = {fmt((94 * 185)**2 / 1e6, 0)}·10⁶ A²s)")
    verifica_adevarat(f"{nume}: I²t sub limita adiabatică a cablului", I2t < (94 * 185)**2)

print("\nProblema 7.3 – RAR trifazată pe linia dublă C–sistem: reușită și pe defect permanent")
Pmax1 = pmax(1)
print(f"  Pmax: ambele circuite {fmt(Pmax2, 4)}; un circuit {fmt(Pmax1, 4)}; defect lângă C: 0")
t_c, t_c2 = 0.12, 0.12      # eliminarea defectului inițial și a celui de după reanclanșare (date de problemă)
cazuri = []
for tm in (0.5, 0.8):
    for permanent in (False, True):
        if permanent:
            etape = [(t_c, 0.0), (tm, Pmax1), (t_c2, 0.0), (6.0, Pmax1)]
        else:
            etape = [(t_c, 0.0), (tm, Pmax1), (6.0, Pmax2)]
        t, d, w, start = simuleaza(etape, d0, t_final=6.0)
        # verificare 1: în etapele cu Pe = 0 unghiul crește parabolic (soluție analitică)
        for (t0, ds, ws, Pk), (dur, _) in zip(start, etape):
            if Pk == 0.0:
                d_an = ds + ws * dur + W0 * P0 / (4 * H) * dur**2
                d_num = np.interp(t0 + dur, t, d)
                verifica(f"t_m = {tm} s, {'permanent' if permanent else 'trecător'}: δ la sfârșitul defectului, "
                         f"analitic vs numeric", d_num, d_an, rtol=1e-4)
        # verificare 2: bilanțul de energie (criteriul ariilor) pentru ultima etapă
        t0, ds, ws, Pf = start[-1]
        dmax_ar = delta_max_arii(ds, ws, Pf)
        st = stabil(d)
        if st:
            dmax_sim = d[t >= t0].max()
            verifica(f"t_m = {tm} s, {'permanent' if permanent else 'trecător'}: δmax simulare vs criteriul ariilor",
                     dmax_sim, dmax_ar, rtol=2e-3)
        else:
            verifica_adevarat(f"t_m = {tm} s, permanent: instabil și după criteriul ariilor", dmax_ar is None)
        cazuri.append((tm, permanent, st, np.degrees(d.max()) if st else None))
        tr, dr, wr, _ = start[2]
        print(f"  pauză {fmt(tm, 1)} s, defect {'permanent' if permanent else 'trecător'}: la reanclanșare (t = "
              f"{fmt(tr, 2)} s) δ = {fmt(np.degrees(dr), 1)}°, rotorul se mișcă {'înainte' if wr > 0 else 'înapoi'} "
              f"(Δω = {fmt(wr, 2)} rad/s) → "
              f"{'stabil, δmax = ' + fmt(np.degrees(d.max()), 1) + '°' if st else 'INSTABIL (G1 iese din sincronism)'}")
        if permanent:
            tf, df_, wf, _ = start[3]
            print(f"     după eliminarea celui de-al doilea defect (t = {fmt(tf, 2)} s): δ = {fmt(np.degrees(df_), 1)}°, "
                  f"Δω = {fmt(wf, 2)} rad/s; criteriul ariilor: "
                  f"{'δmax = ' + fmt(np.degrees(dmax_ar), 1) + '°' if dmax_ar is not None else 'aria de frânare nu ajunge'}")
t, d, _, _ = simuleaza([(t_c, 0.0), (6.0, Pmax1)], d0, t_final=6.0)
print(f"  fără RAR (linia rămâne deschisă): stabil = {stabil(d)}, δmax = {fmt(np.degrees(d.max()), 1)}°")
verifica_adevarat("fără RAR sistemul rămâne stabil", stabil(d))
verifica_adevarat("RAR reușită este stabilă pentru ambele pauze", all(c[2] for c in cazuri if not c[1]))
verifica_adevarat("reanclanșarea pe defect permanent după 0,8 s este instabilă, după 0,5 s stabilă",
                  [c[2] for c in cazuri if c[1]] == [True, False])
# Explorarea pauzei: pentru ce pauze reanclanșarea pe defect permanent este instabilă?
tms = np.round(np.arange(0.2, 1.601, 0.02), 2)
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
print("  pauze (pas 0,02 s) pentru care reanclanșarea pe defect permanent este instabilă: " +
      "; ".join(f"{fmt(a, 2)}…{fmt(b, 2)} s" for a, b in grupe))
verifica_adevarat("instabilitatea apare în ferestre separate de o perioadă de oscilație",
                  len(grupe) >= 2 and 0.6 < grupe[1][0] - grupe[0][0] < 0.9)
# Perioada oscilațiilor mici după deschiderea unui circuit (explică dependența de pauză)
de1 = np.arcsin(P0 / Pmax1)
fn = np.sqrt(W0 * Pmax1 * np.cos(de1) / (2 * H)) / (2 * np.pi)
print(f"  oscilațiile mici cu un circuit: δe = {fmt(np.degrees(de1), 2)}°, f = {fmt(fn, 3)} Hz, perioada {fmt(1 / fn, 3)} s")
t, d, w, _ = simuleaza([(t_c, 0.0), (6.0, Pmax1)], d0, t_final=6.0)
i_max = [i for i in range(1, len(w)) if w[i - 1] > 0 >= w[i]]      # maxime: Δω trece din + în −
T_sim = t[i_max[1]] - t[i_max[0]]
print(f"  perioada din simulare (oscilație mare, neliniară) = {fmt(T_sim, 3)} s")
verifica_adevarat("perioada oscilației mari este mai lungă decât cea a oscilațiilor mici", T_sim > 1 / fn)
# Unghiul pe întrerupătorul deschis al circuitului 1 (pentru controlul sincronismului)
de_s = np.arcsin(P0 * (XD_T + x_retea(1)) / abs(E))
I1 = (abs(E) * np.exp(1j * de_s) - 1.0) / (1j * (XD_T + x_retea(1)))
UC = 1.0 + 1j * (XL + XS) * I1
print(f"  regim staționar cu un circuit: unghiul dintre bara C și capătul îndepărtat al circuitului deschis = "
      f"{fmt(np.degrees(np.angle(UC)), 2)}° (|UC| = {fmt(abs(UC), 4)})")
verifica("unghiul pe întrerupătorul deschis: fazori vs P = UC·V·sin θ/(xL + xs)",
         np.angle(UC), np.arcsin(P0 * (XL + XS) / abs(UC)))

print("\nProblema 7.4 – sincronizarea lui G1: unghiul de avans al comenzii de închidere")
df, t_close = 0.10, 0.08
alfa = 360 * df * t_close
print(f"  Δf = {fmt(df, 2)} Hz, timpul de închidere (releu + întrerupător) = {fmt(t_close * 1e3, 0)} ms → "
      f"α = 360°·Δf·t = {fmt(alfa, 2)}°")
# Calea 2: simulare – unghiul dintre tensiuni crește liniar; comanda la −α; închiderea după t_close
dt = 1e-5
t = np.arange(0, 12, dt)
phi = -180 + 360 * df * t
i_cmd = np.argmax(phi >= -alfa)
phi_inchidere = phi[min(i_cmd + int(round(t_close / dt)), len(t) - 1)]
print(f"  simulare: comanda la φ = {fmt(phi[i_cmd], 3)}°, închiderea la φ = {fmt(phi_inchidere, 3)}°")
verifica("unghiul la închidere ≈ 0", phi_inchidere, 0.0, atol=360 * df * dt * 2, rtol=0)
# Cu accelerație: alunecarea crește cu a = 0,05 Hz/s; sincronizatorul calculează continuu
# α(t) = 360°·(Δf(t)·t_î + a·t_î²/2) și dă comanda când φ(t) ajunge la −α(t)
a_f = 0.05
f_t = 0.02 + a_f * t                               # alunecarea pornește de la 0,02 Hz
phi_a = -180 + 360 * np.concatenate(([0.0], np.cumsum((f_t[1:] + f_t[:-1]) / 2) * dt))
alfa_t = 360 * (f_t * t_close + 0.5 * a_f * t_close**2)
i_cmd = np.argmax(phi_a >= -alfa_t)
phi_inch_a = phi_a[i_cmd + int(round(t_close / dt))]
print(f"  cu accelerație {fmt(a_f, 2)} Hz/s: comanda la Δf = {fmt(f_t[i_cmd], 4)} Hz, α = 360°·(Δf·t + a·t²/2) = "
      f"{fmt(alfa_t[i_cmd], 3)}° (fără termenul a·t²/2 ar fi {fmt(360 * f_t[i_cmd] * t_close, 3)}°); "
      f"închiderea la φ = {fmt(phi_inch_a, 4)}°")
verifica("unghiul la închidere ≈ 0 (cu accelerație)", phi_inch_a, 0.0, atol=0.01, rtol=0)
phi_fara = phi_a[np.argmax(phi_a >= -360 * f_t * t_close) + int(round(t_close / dt))]
print(f"  dacă sincronizatorul ignoră accelerația, închiderea se face la φ = {fmt(phi_fara, 3)}°")
verifica("eroarea fără termenul de accelerație ≈ 360°·a·t²/2", phi_fara, 360 * 0.5 * a_f * t_close**2, atol=0.01, rtol=0)
# Curentul de egalizare la o închidere greșită
x_tot = GEN["xd_s"] + XT + XL / 2 + XS
print(f"  curentul la închiderea cu decalaj (x\"d + xT + xL/2 + xs = {fmt(x_tot, 4)} u.r.):")
for phi_e in (alfa, 10.0, 30.0, 90.0, 180.0):
    dU = 2 * np.sin(np.radians(phi_e) / 2)
    I_f = abs(np.exp(1j * np.radians(phi_e)) - 1.0) / x_tot
    print(f"    φ = {fmt(phi_e, 2)}°: |ΔU| = 2·sin(φ/2) = {fmt(dU, 3)} u.r. → I = {fmt(I_f, 2)} u.r.·In "
          f"(scurtcircuit la borne: 1/x\"d = {fmt(1 / GEN['xd_s'], 1)} u.r.)")
    verifica(f"|ΔU| formulă vs fazori la {phi_e:g}°", dU, abs(np.exp(1j * np.radians(phi_e)) - 1.0))

print("\nProblema 7.5 – AAR pe bara de 6 kV a motoarelor (transfer rapid și transfer la tensiune remanentă)")
print(f"  date: S_motoare = {fmt(S_MOT / 1e6, 1)} MVA, sarcina mecanică p = {fmt(P_SARC, 2)} u.r. (cuplu ∝ ω²), "
      f"H = {fmt(H_MOT, 2)} s, constanta de timp a fluxului T0 = {fmt(T0_REM, 2)} s")
t_ev = np.linspace(0, 2.0, 20001)
w_a, U_a, th_a = remanenta_analitic(t_ev)
w_o, U_o, th_o = remanenta_ode(t_ev)
for tt in (0.05, 0.1, 0.2, 0.5, 1.0):
    i = int(round(tt / (t_ev[1] - t_ev[0])))
    print(f"  t = {fmt(tt, 2)} s: n = {fmt(w_a[i], 4)}·n0 (f = {fmt(F0 * w_a[i], 2)} Hz), U = {fmt(U_a[i], 3)} u.r., "
          f"θ = {fmt(np.degrees(th_a[i]), 1)}°, |ΔU| = {fmt(diferenta_tensiune(U_a[i], th_a[i]), 3)} u.r.")
verifica("turația: analitic vs integrare numerică", w_a, w_o, rtol=1e-6)
verifica("tensiunea remanentă: analitic vs integrare numerică", U_a, U_o, rtol=1e-6)
verifica("unghiul: analitic vs integrare numerică", th_a, th_o, rtol=1e-5, atol=1e-6)
# Fereastra transferului rapid: |ΔU| ≤ 1 u.r. (curentul de reconectare cel mult egal cu cel de pornire)
f_dU = lambda tt: diferenta_tensiune(*remanenta_analitic(tt)[1:]) - 1.0  # noqa: E731
dU_a = diferenta_tensiune(U_a, th_a)
i1 = np.argmax(dU_a >= 1.0)                       # primul pas al grilei peste 1 u.r.
t_fer = brentq(f_dU, t_ev[i1 - 1], t_ev[i1])      # rafinare analitică în intervalul găsit
dU_o = diferenta_tensiune(U_o, th_o)
t_fer_o = t_ev[np.argmax(dU_o >= 1.0)]
print(f"  fereastra transferului rapid (|ΔU| ≤ 1 u.r.) se închide la t = {fmt(t_fer * 1e3, 1)} ms "
      f"(din integrarea numerică: {fmt(t_fer_o * 1e3, 1)} ms); θ = {fmt(np.degrees(remanenta_analitic(t_fer)[2]), 1)}°")
verifica("sfârșitul ferestrei rapide: analitic vs numeric", t_fer, t_fer_o, atol=2e-4, rtol=0)
t_desc, t_inch_r, t_aux = 0.05, 0.08, 0.01
pauze = {"simultan (comenzile de deschidere și închidere date deodată)": max(0.0, t_inch_r - t_desc),
         "secvențial (închiderea după confirmarea deschiderii)": t_desc + t_aux + t_inch_r}
for nume, tp in pauze.items():
    _, Up, thp = remanenta_analitic(np.array(tp))
    dUp = diferenta_tensiune(Up, thp)
    admis = bool(dUp <= 1.0)
    print(f"  transfer {nume}: pauza = {fmt(tp * 1e3, 0)} ms, θ = {fmt(np.degrees(thp), 1)}°, |ΔU| = {fmt(dUp, 3)} u.r."
          f" → {'admis' if admis else 'NEADMIS (se trece la transferul la tensiune remanentă)'}")
    verifica_adevarat(f"transfer {nume.split()[0]}: comparația cu fereastra concordă cu |ΔU| calculat",
                      (tp < t_fer) == admis)
# Transferul la tensiune remanentă: se așteaptă U ≤ 0,25 u.r.
U_prag = 0.25
t_rem = brentq(lambda tt: remanenta_analitic(tt)[1] - U_prag, 0.01, 5.0)
t_rem_o = t_ev[np.argmax(U_o <= U_prag)]
w_rem, _, th_rem = remanenta_analitic(np.array(t_rem))
print(f"  tensiunea remanentă scade la {fmt(U_prag, 2)} u.r. după {fmt(t_rem, 3)} s (numeric {fmt(t_rem_o, 3)} s); "
      f"turația a scăzut la {fmt(w_rem, 3)}·n0, θ = {fmt(np.degrees(th_rem) % 360, 0)}° (mod 360°)")
verifica("momentul U = 0,25 u.r.: analitic vs numeric", t_rem, t_rem_o, atol=2e-4, rtol=0)
dU_rem = diferenta_tensiune(U_prag, th_rem)
print(f"  la acest moment |ΔU| = {fmt(dU_rem, 3)} u.r. ≤ 1 + U_prag = {fmt(1 + U_prag, 2)} u.r. oricare ar fi unghiul")
verifica_adevarat("|ΔU| ≤ 1 + U_prag", dU_rem <= 1 + U_prag + 1e-12)

print("\nProblema 7.6 – protecția la refuzul întrerupătorului (50BF): reglajul temporizării și timpul total")
t_prot, t_cb, t_reset, marja, t_aux = 0.03, 0.06, 0.015, 0.04, 0.01
t_BF_min = t_cb + t_reset + marja
t_BF = np.ceil(t_BF_min * 100) / 100
t_total_BF = t_prot + t_BF + t_aux + t_cb
print(f"  t_BF ≥ t_întrerupere + t_revenire detector + marjă = {fmt(t_cb, 3)} + {fmt(t_reset, 3)} + {fmt(marja, 3)} = "
      f"{fmt(t_BF_min, 3)} s → reglat {fmt(t_BF, 2)} s")
print(f"  eliminarea la refuzul întrerupătorului: t_prot + t_BF + t_relee + t_întrerupătoare vecine = "
      f"{fmt(t_prot, 2)} + {fmt(t_BF, 2)} + {fmt(t_aux, 2)} + {fmt(t_cb, 2)} = {fmt(t_total_BF, 2)} s (tcr = {fmt(tcr, 3)} s, "
      f"rezervă {fmt((tcr - t_total_BF) * 1e3, 0)} ms)")
t_BF_max = tcr - (t_prot + t_aux + t_cb)
print(f"  temporizarea maximă compatibilă cu stabilitatea: t_BF ≤ tcr − (t_prot + t_relee + t_întrerupător) = "
      f"{fmt(t_BF_max * 1e3, 0)} ms")
for nume, t_el in (("refuz de întrerupător, eliminat de 50BF", t_total_BF),
                   ("refuz de întrerupător, eliminat de rezerva de la distanță (treapta a 2-a, 0,35 s)", 0.35 + t_cb)):
    t, d, _, _ = simuleaza([(t_el, 0.0), (3.0, Pmax2)], d0)
    print(f"  {nume}: {fmt(t_el, 2)} s → {'stabil' if stabil(d) else 'instabil'}")
    verifica_adevarat(f"{nume}: simularea concordă cu comparația cu tcr", stabil(d) == (t_el < tcr))
