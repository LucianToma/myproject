"""Capitolul 6 – Protecția generatoarelor și a motoarelor: rezolvarea și verificarea problemelor."""

import numpy as np
from scipy.optimize import brentq
from modele import (SQRT3, W0, GEN, MOTOR, fmt, polar, verifica, verifica_adevarat, timp_termic, timp_termic_ode,
                    retea_referinta, seq_la_faza, faza_la_seq, sistem_direct)
from calcul_cap06 import (IN_M, K_TERMIC, IB_M, termic_rk4, IN_G, ZB_G, TC_G, TT_G, K_SEC_G,
                          cerc_pierdere_excitatie, in_cerc_geometric, in_cerc_comparator, impedanta_borne,
                          tensiune_neutru, tensiune_neutru_mna)

M = MOTOR
tau = M["tau"]

print("Problema 6.1 – modelul termic al motorului M1")
print(f"  In = Pn/(√3·Un·η·cos φ) = {fmt(IN_M, 2)} A; IB = In; k = {fmt(K_TERMIC, 2)}; τ = {fmt(tau, 0)} s")
for mult in (1.2, 1.5, 2.0, M["Ip_In"]):
    I = mult * IN_M
    rez = []
    for nume, Ip in (("rece", 0.0), ("caldă", IN_M)):
        t_f = timp_termic(I, IB_M, K_TERMIC, tau, Ip)
        t_o = timp_termic_ode(I, IB_M, K_TERMIC, tau, Ip, dt=0.01)
        t_r, _, _ = termic_rk4(lambda t: I, tau, IB_M, K_TERMIC, theta0=(Ip / (K_TERMIC * IB_M))**2,
                               dt=min(0.5, t_f / 200))
        verifica(f"I = {mult:g}·In, {nume}: formula vs pas exact", t_f, t_o, rtol=1e-6)
        verifica(f"I = {mult:g}·In, {nume}: formula vs Runge–Kutta", t_f, t_r, rtol=1e-4)
        rez.append(f"din starea {nume} {fmt(t_f, 1)} s")
    print(f"  I = {fmt(mult, 1)}·In: " + "; ".join(rez))

print("\nProblema 6.2 – pornirea motorului și blocarea repornirii")
Ip = M["Ip_In"] * IN_M
tp = M["t_pornire"]
th_inf = (Ip / (K_TERMIC * IB_M))**2
th_cald = (IN_M / (K_TERMIC * IB_M))**2
dth_exact = th_inf * (1 - np.exp(-tp / tau))
dth_aprox = th_inf * tp / tau
print(f"  la 6·In: θ∞ = (Ip/(k·IB))² = {fmt(th_inf, 2)}; o pornire de {fmt(tp, 0)} s din stare rece adaugă "
      f"Δθ = {fmt(dth_exact, 4)} (aproximativ θ∞·tp/τ = {fmt(dth_aprox, 4)})")
verifica("Δθ exact vs aproximația liniară (t ≪ τ)", dth_exact, dth_aprox, rtol=1e-2)
t_cald = timp_termic(Ip, IB_M, K_TERMIC, tau, IN_M)
print(f"  după funcționare îndelungată la In: θ = (1/k)² = {fmt(th_cald, 4)}; pornirea ar declanșa după {fmt(t_cald, 2)} s"
      f" < {fmt(tp, 0)} s → pornirea din stare caldă este blocată")
verifica_adevarat("pornirea din stare caldă nu se poate încheia", t_cald < tp)
# Starea termică maximă care permite o pornire completă, cu rezervă de 20 % în timp
th_lim = th_inf - (th_inf - 1) * np.exp(1.2 * tp / tau)
tau_r = 3 * tau            # motorul oprit se răcește mai încet (date de problemă)
t_astept = tau_r * np.log(th_cald / th_lim)
print(f"  starea termică admisă la pornire: θ ≤ {fmt(th_lim, 4)}; cu τ(oprit) = 3τ = {fmt(tau_r, 0)} s, "
      f"timpul de așteptare = τr·ln(θcald/θadm) = {fmt(t_astept, 0)} s")
# Calea 2: răcire simulată numeric, apoi pornire de 1,2·tp simulată cu Runge–Kutta
th = th_cald
dt = 0.5
t = 0.0
while th > th_lim:
    th += dt * (-th / tau_r)
    t += dt
t_dec, _, _ = termic_rk4(lambda s: Ip, tau, IB_M, K_TERMIC, theta0=th_lim, dt=0.005, tmax=60)
print(f"  simulare: răcire până la θadm în {fmt(t, 0)} s; din θadm, declanșarea la 6·In apare după {fmt(t_dec, 2)} s")
verifica("timpul de așteptare: formula vs răcire simulată", t_astept, t, rtol=2e-3)
verifica("din θadm declanșarea apare exact la 1,2·tp", t_dec, 1.2 * tp, rtol=1e-4)

print("\nProblema 6.3 – protecția la pornire prelungită și rotor blocat")
I_set = 3.0 * IN_M
t_set = 9.0
I_supr_max = 1.5 * IN_M
print(f"  reglaj: I> = 3·In = {fmt(I_set, 1)} A, t = {fmt(t_set, 0)} s")
verifica_adevarat("I> sub curentul de pornire și peste suprasarcinile lăsate protecției termice",
                  I_supr_max < I_set < Ip)
verifica_adevarat("t > 1,5·t_pornire și t ≤ 0,75·t_blocat_cald", t_set >= 1.5 * tp and t_set <= 0.75 * M["t_blocat_cald"])
t_rotor_rece = timp_termic(Ip, IB_M, K_TERMIC, tau, 0.0)
print(f"  cu rotorul blocat din stare rece, modelul termic ar declanșa după {fmt(t_rotor_rece, 1)} s > "
      f"{fmt(M['t_blocat_rece'], 0)} s admis → este necesară protecția separată de rotor blocat")
verifica_adevarat("modelul termic (τ de funcționare) nu protejează rotorul blocat", t_rotor_rece > M["t_blocat_rece"])


def simuleaza_motor(profil, theta0, tmax=40.0, dt=0.005):
    """Calea de verificare: protecția termică și protecția de rotor blocat rulate în paralel."""
    th, t, t_temp = theta0, 0.0, 0.0
    while t < tmax:
        I = profil(t)
        th += dt * ((I / (K_TERMIC * IB_M))**2 - th) / tau
        t_temp = t_temp + dt if I > I_set else 0.0
        t += dt
        if th >= 1.0:
            return "termică", t
        if t_temp >= t_set:
            return "rotor blocat", t
    return "nicio declanșare", None


scen = [("pornire normală din stare rece", lambda s: Ip if s < tp else IN_M, 0.0, "nicio declanșare"),
        ("rotor blocat din stare rece", lambda s: Ip, 0.0, "rotor blocat"),
        ("rotor blocat din stare caldă", lambda s: Ip, th_cald, "termică")]
for nume, prof, th0, astept in scen:
    cine, cand = simuleaza_motor(prof, th0)
    print(f"  {nume}: {cine}" + (f" după {fmt(cand, 2)} s" if cand else ""))
    verifica_adevarat(f"{nume}: rezultatul așteptat ({astept})", cine == astept)
    if cine == "rotor blocat":
        verifica("timpul de declanșare = temporizarea reglată", cand, t_set, atol=0.01, rtol=0)
        verifica_adevarat("sub timpul admis cu rotorul blocat (rece)", cand < M["t_blocat_rece"])
    if cine == "termică":
        verifica("declanșarea termică din stare caldă: simulare vs formula", cand, t_cald, atol=0.01, rtol=0)

G = GEN
Pn = G["Sn"] * G["cosphi"]
print("\nProblema 6.4 – protecția la putere inversă (32) a generatorului G1")
P_mot = G["P_motor"] * Pn
P_set = 0.5 * P_mot
P_sec = P_set / (TC_G * TT_G)
print(f"  Pn = {fmt(Pn / 1e6, 2)} MW; puterea de motor (catalog) = {fmt(100 * G['P_motor'], 1)} % Pn = "
      f"{fmt(P_mot / 1e6, 4)} MW; reglaj −P> = 50 % din ea = {fmt(P_set / 1e6, 4)} MW = "
      f"{fmt(100 * P_set / G['Sn'], 3)} % Sn")
print(f"  în secundar (TC {TC_G:g}/1 A, TT 10,5/0,1 kV): P = {fmt(P_set / 1e6, 4)}·10⁶/({TC_G:g}·{TT_G:g}) = {fmt(P_sec, 3)} W")
# Calea 2: mărimile secundare simulate pentru regimul de motor (Q = +0,3·Sn, generator supraexcitat)
Uf = G["Un"] / SQRT3
Q = 0.3 * G["Sn"]
S = -P_mot + 1j * Q
I_f = np.conj(S / (3 * Uf))
Vs_, Is_ = sistem_direct(Uf / TT_G), sistem_direct(I_f / TC_G)
P_mas = np.sum((Vs_ * np.conj(Is_)).real)
print(f"  regim de motor cu Q = 0,3·Sn: P secundar măsurat = {fmt(P_mas, 3)} W (= −P_motor/(nTC·nTT) = "
      f"{fmt(-P_mot / (TC_G * TT_G), 3)} W) → acționează (|P| > {fmt(P_sec, 3)} W)")
verifica("P secundar: fazori simulați vs conversie", P_mas, -P_mot / (TC_G * TT_G))
# Eroarea de unghi admisă: ΔP ≈ Q·ε trebuie să rămână sub 50 % din reglaj
eps_aprox = 0.5 * P_set / Q
eps_exact = brentq(lambda e: abs(S) * np.cos(np.angle(S) - e) - S.real - 0.5 * P_set, 0, 0.1)
print(f"  eroarea de unghi admisă (TC + TT + releu): ε ≈ 0,5·P_reglaj/Q = {fmt(np.degrees(eps_aprox), 3)}°"
      f" (exact {fmt(np.degrees(eps_exact), 3)}°) = {fmt(np.degrees(eps_aprox) * 60, 1)} minute de arc")
verifica("ε: aproximația ΔP = Q·ε vs ecuația exactă", eps_aprox, eps_exact, rtol=1e-2)

print("\nProblema 6.5 – protecția la pierderea excitației (40)")
sus, jos, centru, raza = cerc_pierdere_excitatie()
print(f"  Zb = Un²/Sn = {fmt(ZB_G, 3)} Ω; decalaj −x'd/2 = −{fmt(G['xd_t'] / 2, 2)} u.r. = −{fmt(G['xd_t'] / 2 * ZB_G, 3)} Ω;"
      f" diametru xd = {fmt(G['xd'], 2)} u.r. = {fmt(G['xd'] * ZB_G, 3)} Ω (primar)")
print(f"  în secundar (×nTC/nTT = {fmt(K_SEC_G, 2)}): decalaj {fmt(G['xd_t'] / 2 * ZB_G * K_SEC_G, 2)} Ω, "
      f"diametru {fmt(G['xd'] * ZB_G * K_SEC_G, 2)} Ω")
puncte = [("nominal, supraexcitat", 0.85, np.sqrt(1 - 0.85**2)), ("P = 0,85, Q = 0", 0.85, 0.0),
          ("P = 0,85, subexcitat Q = −0,3", 0.85, -0.3), ("P = 0,3, subexcitat Q = −0,4", 0.3, -0.4)]
for nume, P, Qp in puncte:
    Z = 1.0 / np.conj(P + 1j * Qp)          # U = 1 u.r.: Z = U²/S*
    g, c = in_cerc_geometric(Z, sus, jos), in_cerc_comparator(Z, sus, jos)
    print(f"  {nume}: Z = {fmt(Z.real, 3)} {'+' if Z.imag >= 0 else '−'} j{fmt(abs(Z.imag), 3)} u.r. → "
          f"{'în cerc' if g else 'în afara cercului'}")
    verifica_adevarat(f"{nume}: geometric și comparator dau același rezultat", g == c)
    verifica_adevarat(f"{nume}: regimul normal nu este în caracteristică", not g)
r = retea_referinta(c=1.0, cu_capacitati=False)
Sk_C = SQRT3 * r.bare["C"] * abs(r.scurtcircuit_secvente("C", "3f")["I_faza"][0])
xs = G["Sn"] / Sk_C
xe = G["ukT"] + xs
print(f"  rețeaua văzută din C: S\"k = {fmt(Sk_C / 1e6, 0)} MVA → xs = Sn/S\"k = {fmt(xs, 4)} u.r.; xe = xT + xs = {fmt(xe, 4)} u.r.")
P = 0.85
E_lim = P * (G["xd"] + xe)
Z90, _, _ = impedanta_borne(E_lim, np.pi / 2, G["xd"], xe)
print(f"  excitația scade la P = {fmt(P, 2)}: limita de stabilitate (δ = 90°) la E = {fmt(E_lim, 4)}, unde "
      f"Z = {fmt(Z90.real, 3)} − j{fmt(-Z90.imag, 3)} u.r. → {'în cerc' if in_cerc_geometric(Z90, sus, jos) else 'încă în afara cercului'}")
verifica_adevarat("la limita de stabilitate impedanța nu a intrat încă în cerc",
                  not in_cerc_geometric(Z90, sus, jos) and not in_cerc_comparator(Z90, sus, jos))
# regim asincron (alunecarea polilor) cu E = E_lim: δ parcurge 90°…270°
deltas = np.radians(np.linspace(90, 270, 3601))
Zs = np.array([impedanta_borne(E_lim, dd, G["xd"], xe)[0] for dd in deltas])
ing = in_cerc_geometric(Zs, sus, jos)
inc = in_cerc_comparator(Zs, sus, jos)
verifica_adevarat("alunecarea polilor: cele două metode coincid în toate punctele", np.all(ing == inc))
d_in = np.degrees(deltas[ing])
print(f"  la alunecarea polilor impedanța este în cerc pentru δ între {fmt(d_in.min(), 1)}° și {fmt(d_in.max(), 1)}°")
Z180, _, _ = impedanta_borne(E_lim, np.pi, G["xd"], xe)
Z180_teorie = 1j * xe - 1j * (G["xd"] + xe) * 1 / (E_lim + 1)       # Ub/I la δ = 180° (calcul direct)
verifica("Z la δ = 180°: funcția generală vs calcul de mână", Z180, Z180_teorie, rtol=1e-9)
# excitația complet pierdută: E = 0 → Z = −j·xd
Z0, _, _ = impedanta_borne(0.0, 0.0, G["xd"], xe)
print(f"  E = 0: Z = {fmt(Z0.real, 3)} − j{fmt(-Z0.imag, 3)} u.r. (teoria: −j·xd) → în cerc")
verifica("E = 0: Z = −j·xd", Z0, -1j * G["xd"], rtol=1e-9)
verifica_adevarat("E = 0: punctul este în caracteristică (ambele metode)",
                  in_cerc_geometric(Z0, sus, jos) and in_cerc_comparator(Z0, sus, jos))

print("\nProblema 6.6 – sarcina nesimetrică (46): consumul capabilității (I2/In)²·t = K")
K2, I2c = G["K2"], G["I2_cont"]
# defect bifazat pe bara C (110 kV), eliminat de protecția de rezervă după 1 s
z1g, z2g = 1j * (G["xd_s"] + G["ukT"]), 1j * (G["x2"] + G["ukT"])
zs = 1j * xs
z1 = z1g * zs / (z1g + zs)
z2 = z2g * zs / (z2g + zs)
I1 = 1.0 / (z1 + z2)
I2g = abs(-I1 * zs / (z2g + zs))
# Calea 2: rezolvare nodală în coordonate de fază (generator cu Z2 ≠ Z1, transformator, rețea, defect b–c)
Zg = seq_la_faza(1j * 0.1, z1g, z2g)                 # componenta homopolară nu intervine (defect fără pământ)
Zr = seq_la_faza(zs, zs, zs)
E = sistem_direct(1.0)
Yg, Yr = np.linalg.inv(Zg), np.linalg.inv(Zr)
Y = Yg + Yr
gf = 1e6
Y[1, 1] += gf
Y[2, 2] += gf
Y[1, 2] -= gf
Y[2, 1] -= gf
V = np.linalg.solve(Y, Yg @ E + Yr @ E)
I_gen = Yg @ (E - V)
I2g_faza = abs(faza_la_seq(I_gen)[2])
print(f"  xs = {fmt(xs, 4)}; contribuția generatorului la componenta inversă: I2 = {fmt(I2g, 3)} u.r. "
      f"(rezolvare în coordonate de fază: {fmt(I2g_faza, 3)} u.r.)")
verifica("I2 al generatorului: rețele de secvență vs coordonate de fază", I2g, I2g_faza, rtol=1e-4)
t_def = 1.0
cons = I2g**2 * t_def
t_max_def = K2 / I2g**2
print(f"  un defect de {fmt(t_def, 1)} s consumă (I2)²·t = {fmt(cons, 2)} s din K = {fmt(K2, 0)} s; "
      f"durata maximă admisă a defectului = K/I2² = {fmt(t_max_def, 2)} s")
# după eliminare rămâne o întrerupere de fază cu I2 = 0,15 u.r. (date de problemă)
I2_rest = 0.15
t_rest = (K2 - cons) / I2_rest**2
print(f"  dacă după defect rămâne I2 = {fmt(I2_rest, 2)} u.r. (> I2 admis permanent = {fmt(I2c, 2)}), "
      f"capabilitatea se epuizează după încă {fmt(t_rest, 0)} s")
# Calea 2: integrare numerică a lui (I2)² pe profilul de timp
dt = 0.01
tt = np.arange(0, t_def + t_rest + 50, dt)
i2 = np.where(tt < t_def, I2g, I2_rest)
cum = np.cumsum(i2**2) * dt
t_epuizare = tt[np.argmax(cum >= K2)]
verifica("momentul epuizării: calcul analitic vs integrare numerică", t_def + t_rest, t_epuizare, atol=2 * dt, rtol=0)

print("\nProblema 6.7 – protecția la punere la pământ a statorului (59N, 95 %)")
Ef = G["Un"] / SQRT3
C = 0.25e-6                    # capacitatea față de pământ pe fază: generator + bare + TB + condensatoare (date)
Ic = 3 * W0 * C * Ef
RN = 1 / (3 * W0 * C)          # rezistența de neutru (raportată la primar), aleasă cu I_R = Ic
UN_set = 0.05
print(f"  Uf = {fmt(Ef, 0)} V; Ic = 3ωC·Uf = {fmt(Ic, 3)} A; RN = 1/(3ωC) = {fmt(RN, 0)} Ω → I_R = {fmt(Ef / RN, 3)} A")
for x in (1.0, 0.5, 0.1, 0.06, 0.04):
    vf = abs(tensiune_neutru(x, 1e-3, RN, C, Ef)) / Ef
    vm = abs(tensiune_neutru_mna(x, 1e-3, RN, C, Ef)) / Ef
    print(f"  defect metalic la {fmt(100 * x, 0)} % de neutru: U_N = {fmt(vf, 4)}·Uf → "
          f"{'acționează' if vf >= UN_set - 1e-9 else 'nu acționează'}")
    verifica(f"U_N la x = {x:g}: formula vs analiza nodală", vf, vm, rtol=1e-9)
    verifica(f"U_N = x·Uf la defect metalic (x = {x:g})", vf, x, rtol=1e-5)
# rezistența de defect maximă detectată: |U_N| = 0,05·Uf → (Rf/RN + 1)² + (3ωC·Rf)² = (x/0,05)²
for x in (1.0, 0.5):
    a2 = (1 / RN)**2 + (3 * W0 * C)**2
    a1 = 2 / RN
    a0 = 1 - (x / UN_set)**2
    Rf_an = (-a1 + np.sqrt(a1**2 - 4 * a2 * a0)) / (2 * a2)
    Rf_num = brentq(lambda R: abs(tensiune_neutru_mna(x, R, RN, C, Ef)) / Ef - UN_set, 1.0, 1e7)
    print(f"  la x = {fmt(100 * x, 0)} %: rezistența de defect maximă detectată = {fmt(Rf_an / 1e3, 2)} kΩ")
    verifica(f"Rf maxim la x = {x:g}: ecuația de gradul 2 vs analiza nodală", Rf_an, Rf_num, rtol=1e-6)
n_TN = Ef / 240
print(f"  cu transformatorul de neutru {fmt(Ef, 0)}/240 V, reglajul în secundar = 0,05·240 = {fmt(0.05 * 240, 1)} V")
