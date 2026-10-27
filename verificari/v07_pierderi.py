"""Verificări pentru Modulul 3 (dispozitive) și Modulul 7 (pierderi, termic,
aspecte practice).

Metode: integrarea numerică a lui p(t) = v(t) i(t) pe formele de undă de
comutație liniarizate; simularea convertorului buck pentru valorile
efective folosite în bilanțul de pierderi; integrarea în timp a rețelei
termice.
"""
import math

import numpy as np

from comun import titlu, verifica, verifica_conditie
from simulator_dcdc import iL, medie_perioada, simuleaza, vC


def energie_comutatie():
    titlu("Energia de comutație: modelul cu variații liniare")
    V, I = 48.0, 10.0
    t_ri, t_fv = 20e-9, 30e-9  # pornire: crește curentul, apoi scade tensiunea
    n = 200001
    # Sarcină inductivă cu diodă de regim liber (tensiune "clampată"):
    # 1) i crește 0 -> I la v = V (dioda conduce încă); 2) v scade V -> 0 la i = I.
    t1 = np.linspace(0, t_ri, n)
    E1 = np.trapezoid(V * (I * t1 / t_ri), t1)
    t2 = np.linspace(0, t_fv, n)
    E2 = np.trapezoid((V * (1 - t2 / t_fv)) * I, t2)
    verifica("sarcină inductivă: E_on = V I (t_ri + t_fv)/2", E1 + E2,
             V * I * (t_ri + t_fv) / 2, tol_rel=1e-9)
    # Sarcină rezistivă: v și i se schimbă simultan, v = V(1 - t/tc), i = I t/tc
    tc = t_ri + t_fv
    t = np.linspace(0, tc, n)
    E_rez = np.trapezoid(V * (1 - t / tc) * I * t / tc, t)
    verifica("sarcină rezistivă: E_on = V I tc/6", E_rez, V * I * tc / 6, tol_rel=1e-9)
    verifica_conditie("sarcina inductivă 'clampată' comută de 3 ori mai greu decât cea "
                      "rezistivă (la același tc)", abs((E1 + E2) / E_rez - 3) < 1e-6)


def bilant_buck():
    titlu("Bilanț de pierderi: buck 48 V -> 12 V, 10 A, 100 kHz")
    Vin, Vo, Io, fs = 48.0, 12.0, 10.0, 100e3
    D = Vo / Vin
    dI = 3.0
    L = Vo * (1 - D) / (fs * dI)
    print(f"  D = {D}, L = Vo(1-D)/(fs dI) = {L * 1e6:.1f} uH pentru dI = {dI} A")
    rez = simuleaza("buck", Vin, D, L, 100e-6, Vo / Io, fs)
    # valorile efective ale curenților prin tranzistor și diodă, din simulare
    I2_T = medie_perioada(rez, lambda s: iL(s) ** 2 if s["topo"] == "on" else 0 * iL(s))
    I2_D = medie_perioada(rez, lambda s: iL(s) ** 2 if s["topo"] == "off" else 0 * iL(s))
    Imed_D = medie_perioada(rez, lambda s: iL(s) if s["topo"] == "off" else 0 * iL(s))
    verifica("I_T,rms^2 = D (Io^2 + dI^2/12)", I2_T, D * (Io ** 2 + dI ** 2 / 12), tol_rel=1e-3)
    verifica("I_D,rms^2 = (1-D)(Io^2 + dI^2/12)", I2_D, (1 - D) * (Io ** 2 + dI ** 2 / 12),
             tol_rel=1e-3)
    verifica("I_D,med = (1-D) Io", Imed_D, (1 - D) * Io, tol_rel=1e-4)

    R_on, VF, rD = 10e-3, 0.7, 10e-3
    t_ri, t_fv, t_rv, t_fi = 20e-9, 30e-9, 30e-9, 20e-9
    Qg, Vg = 50e-9, 10.0
    P_cond_T = R_on * D * (Io ** 2 + dI ** 2 / 12)
    I_on, I_off = Io - dI / 2, Io + dI / 2  # curentul la pornire (vale) și la blocare (vârf)
    P_sw = 0.5 * Vin * fs * (I_on * (t_ri + t_fv) + I_off * (t_rv + t_fi))
    P_D = VF * (1 - D) * Io + rD * (1 - D) * (Io ** 2 + dI ** 2 / 12)
    P_g = Qg * Vg * fs
    P_sync = R_on * (1 - D) * (Io ** 2 + dI ** 2 / 12)
    Po = Vo * Io
    total = P_cond_T + P_sw + P_D + P_g
    total_sync = P_cond_T + P_sw + P_sync + 2 * P_g
    print(f"  conducție tranzistor   {P_cond_T:6.3f} W")
    print(f"  comutație tranzistor   {P_sw:6.3f} W")
    print(f"  diodă (VF={VF} V)       {P_D:6.3f} W")
    print(f"  comandă grilă          {P_g:6.3f} W")
    print(f"  TOTAL                  {total:6.3f} W  -> randament {100 * Po / (Po + total):.1f} %")
    print(f"  cu redresare sincronă  {total_sync:6.3f} W  -> randament "
          f"{100 * Po / (Po + total_sync):.1f} %")
    verifica("P_cond,T", P_cond_T, 0.251875, tol_rel=1e-9)
    verifica("P_sw", P_sw, 2.4, tol_rel=1e-9)
    verifica("P_dioda", P_D, 6.005625, tol_rel=1e-9)
    return P_cond_T + P_sw


def termic(P):
    titlu("Calcul termic în regim staționar și tranzitoriu")
    Ta, Rjc, Rcs, Rsa = 40.0, 0.8, 0.5, 10.0
    Tj = Ta + P * (Rjc + Rcs + Rsa)
    print(f"  P = {P:.3f} W, Rth total = {Rjc + Rcs + Rsa} K/W -> Tj = {Tj:.1f} grade C")
    # Rețea Cauer simplă: jonctiune - capsulă - radiator - ambiant, cu
    # capacități termice; integrare Euler implicită până la regim staționar.
    Cj, Cc, Cs = 0.05, 2.0, 40.0  # J/K (valori ilustrative)
    T = np.array([Ta, Ta, Ta])
    h = 0.5  # Euler implicit: stabil și pentru constanta rapidă Rjc*Cj = 0,04 s
    G = np.array([[1 / Rjc, -1 / Rjc, 0],
                  [-1 / Rjc, 1 / Rjc + 1 / Rcs, -1 / Rcs],
                  [0, -1 / Rcs, 1 / Rcs + 1 / Rsa]])
    Cm = np.diag([Cj, Cc, Cs])
    sursa = np.array([P, 0, Ta / Rsa])
    A = Cm / h + G
    for _ in range(20000):  # 10000 s = 25 x constanta de timp lentă (~Rsa*Cs = 400 s)
        T = np.linalg.solve(A, Cm @ T / h + sursa)
    verifica("simularea termică tranzitorie converge la Ta + P*sum(Rth)", T[0], Tj, tol_rel=1e-3)
    verifica("temperatura radiatorului = Ta + P Rsa", T[2], Ta + P * Rsa, tol_rel=1e-3)


def supratensiune():
    titlu("Supratensiunea pe inductanța parazită: v = L di/dt")
    Lp, dI, dt = 10e-9, 10.0, 10e-9
    t = np.linspace(0, dt, 10001)
    i = dI * t / dt
    v = Lp * np.gradient(i, t)
    verifica("v = L di/dt (10 nH, 10 A în 10 ns)", float(np.mean(v)), Lp * dI / dt,
             tol_rel=1e-9)


def regulator_liniar():
    titlu("Regulator liniar vs. convertor în comutație (Modulul 1)")
    Vin, Vo, Io = 12.0, 5.0, 1.0
    P_lin = (Vin - Vo) * Io
    eta_lin = Vo * Io / (Vin * Io)
    verifica("regulator liniar: randament = Vo/Vin", eta_lin, 5 / 12, tol_rel=1e-12)
    verifica("regulator liniar: pierderi = (Vin - Vo) Io", P_lin, 7.0, tol_rel=1e-12)
    eta_sw = 0.90
    P_sw = Vo * Io * (1 / eta_sw - 1)
    verifica("convertor cu randament 90 %: pierderi = Po(1/eta - 1)", P_sw, 5 / 9, tol_rel=1e-12)
    # convertor ideal: buck simulat, tranzistor/dioda ideale => fără pierderi
    rez = simuleaza("buck", Vin, Vo / Vin, 100e-6, 100e-6, Vo / Io, 100e3)
    Pin = Vin * medie_perioada(rez, lambda s: iL(s) if s["topo"] == "on" else 0 * iL(s))
    Pout = medie_perioada(rez, lambda s: vC(s) ** 2 / (Vo / Io))
    verifica("comutatoare ideale: randament 100 % (simulare)", Pout / Pin, 1.0, tol_rel=1e-6)


def main():
    regulator_liniar()
    energie_comutatie()
    P = bilant_buck()
    termic(P)
    supratensiune()


if __name__ == "__main__":
    main()
