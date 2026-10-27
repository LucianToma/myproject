"""Verificarea răspunsurilor la exercițiile din curs/08-exercitii.md.

Pentru fiecare exercițiu: (1) se calculează răspunsul cu formulele din curs,
(2) unde este posibil, se confirmă independent prin simulare.
"""
import math

import numpy as np

from comun import armonici, titlu, verifica, verifica_conditie
from simulator_dcdc import iL, medie_perioada, simuleaza, vC
from v04_redresoare import filtru_ideal, punte_trifazata, simuleaza_filtru
from v06_invertoare import VDC, spwm_picior
from comun import esantioane_perioada


def ex1():
    titlu("Ex. 1 - Curentul prin tranzistorul unui buck")
    Io, dI, D, R = 5.0, 2.0, 0.4, 20e-3
    Imed = D * Io
    Irms = math.sqrt(D * (Io ** 2 + dI ** 2 / 12))
    P = Irms ** 2 * R
    print(f"  I_med = {Imed:.3f} A, I_rms = {Irms:.4f} A, P_cond = {P * 1e3:.1f} mW")
    u = np.arange(2 ** 20) / 2 ** 20
    i = np.where(u < D, Io - dI / 2 + dI * u / D, 0.0)
    verifica("I_rms (integrare numerică)", float(np.sqrt(np.mean(i ** 2))), Irms, tol_rel=1e-5)
    return Irms, P


def ex2():
    titlu("Ex. 2 - Punte monofazată cu sarcină rezistivă")
    Vs, R = 230.0, 100.0
    Vm = math.sqrt(2) * Vs
    Vdc = 2 * Vm / math.pi
    print(f"  V_dc = {Vdc:.2f} V, I_dc = {Vdc / R:.3f} A, I_rms = {Vs / R:.2f} A, "
          f"P = {Vs ** 2 / R:.0f} W, I_D,med = {Vdc / R / 2:.3f} A, V_RRM >= {Vm:.1f} V")
    th = esantioane_perioada(2 ** 20)
    v = np.abs(Vm * np.sin(th))
    verifica("V_dc (numeric)", float(np.mean(v)), Vdc, tol_rel=1e-9)
    verifica("P = V_rms^2/R (numeric)", float(np.mean(v ** 2)) / R, Vs ** 2 / R, tol_rel=1e-9)


def ex3():
    titlu("Ex. 3 - Dimensionarea filtrului capacitiv")
    Vs, f, Io, dV = 18.0, 50.0, 1.0, 2.0
    Vm = math.sqrt(2) * Vs
    C_min = Io / (2 * f * dV)
    C = 5600e-6
    R = 24.0
    ex = filtru_ideal(Vm, f, R, C)
    print(f"  Vm = {Vm:.2f} V, C_min = {C_min * 1e6:.0f} uF -> aleg {C * 1e6:.0f} uF")
    print(f"  cu R = {R} ohm: Delta V exact = {ex['dV']:.3f} V, V_dc exact = {ex['Vdc']:.2f} V, "
          f"I_o = {ex['Vdc'] / R:.3f} A")
    verifica_conditie("ondulația exactă respectă cerința (<= 2 V)", ex["dV"] <= dV)
    sim = simuleaza_filtru(Vm, f, R, C, Rs=0.01)
    verifica("simularea confirmă Delta V", float(sim["vC"].max() - sim["vC"].min()), ex["dV"],
             tol_rel=2e-2)


def ex4():
    titlu("Ex. 4 - Punte trifazată comandată")
    VLL, Vdc = 400.0, 400.0
    V0 = 3 * math.sqrt(2) / math.pi * VLL
    alfa = math.acos(Vdc / V0)
    PF = 3 / math.pi * math.cos(alfa)
    print(f"  V_d0 = {V0:.2f} V, alfa = {math.degrees(alfa):.2f} grade, PF = {PF:.4f}")
    th, vo, ia, va = punte_trifazata(VLL, alfa)
    verifica("V_dc din construcția numerică", float(np.mean(vo)), Vdc, tol_rel=1e-4)


def ex5():
    titlu("Ex. 5 - Proiectarea unui buck 12 V -> 5 V / 2 A, 200 kHz")
    Vin, Vo, Io, fs = 12.0, 5.0, 2.0, 200e3
    D = Vo / Vin
    L_min = Vo * (1 - D) / (fs * 0.3 * Io)
    L = 27e-6
    dI = Vo * (1 - D) / (fs * L)
    C_min = dI / (8 * fs * 0.05)
    C = 10e-6
    dV = dI / (8 * fs * C)
    R = Vo / Io
    Lcrit = (1 - D) * R / (2 * fs)
    print(f"  D = {D:.4f}; L_min = {L_min * 1e6:.2f} uH -> L = 27 uH; Delta i_L = {dI:.4f} A")
    print(f"  C_min = {C_min * 1e6:.2f} uF -> C = 10 uF; Delta v_o = {dV * 1e3:.1f} mV")
    print(f"  L_crit = {Lcrit * 1e6:.2f} uH; I_o,limită CCM = Delta i_L/2 = {dI / 2:.3f} A")
    rez = simuleaza("buck", Vin, D, L, C, R, fs)
    i = np.concatenate([iL(s) for s in rez["segmente"]])
    v = np.concatenate([vC(s) for s in rez["segmente"]])
    verifica("simulare: Vo", medie_perioada(rez, vC), Vo, tol_rel=1e-6)
    verifica("simulare: Delta i_L", float(i.max() - i.min()), dI, tol_rel=5e-3)
    verifica("simulare: Delta v_o", float(v.max() - v.min()), dV, tol_rel=3e-2)
    return D, L, dI


def ex6():
    titlu("Ex. 6 - Boost 5 V -> 12 V / 0,5 A, 500 kHz")
    Vin, Vo, Io, fs, L = 5.0, 12.0, 0.5, 500e3, 10e-6
    D = 1 - Vin / Vo
    IL = Io / (1 - D)
    dI = Vin * D / (L * fs)
    C_min = Io * D / (fs * 0.06)
    print(f"  D = {D:.4f}, I_L = {IL:.3f} A, Delta i_L = {dI:.4f} A, "
          f"I_L,max = {IL + dI / 2:.3f} A, C_min = {C_min * 1e6:.2f} uF")
    rez = simuleaza("boost", Vin, D, L, 10e-6, Vo / Io, fs)
    verifica("simulare: Vo", medie_perioada(rez, vC), Vo, tol_rel=2e-3)
    verifica("simulare: I_L", medie_perioada(rez, iL), IL, tol_rel=2e-3)
    v = np.concatenate([vC(s) for s in rez["segmente"]])
    verifica_conditie("simulare: Delta v_o <= 60 mV cu C = 10 uF",
                      v.max() - v.min() <= 0.06, f"{(v.max() - v.min()) * 1e3:.1f} mV")


def ex7(D, L):
    titlu("Ex. 7 - Buck-ul de la Ex. 5 la sarcină mică (Io = 0,1 A)")
    Vin, fs, R = 12.0, 200e3, 50.0
    K = 2 * L * fs / R
    M = 2 / (1 + math.sqrt(1 + 4 * K / D ** 2))
    M_dorit = 5.0 / 12.0
    D_nou = M_dorit * math.sqrt(K / (1 - M_dorit))
    print(f"  K = {K:.3f} < 1-D = {1 - D:.4f} => DCM; Vo (D neschimbat) = {M * Vin:.3f} V")
    print(f"  D necesar pentru 5 V în DCM: {D_nou:.4f}")
    r = simuleaza("buck", Vin, D, L, 10e-6, R, fs)
    verifica_conditie("simulare: DCM", r["tau_dcm"] is not None)
    verifica("simulare: Vo cu D neschimbat", medie_perioada(r, vC), M * Vin, tol_rel=2e-3)
    r = simuleaza("buck", Vin, D_nou, L, 10e-6, R, fs)
    verifica("simulare: Vo cu D corectat", medie_perioada(r, vC), 5.0, tol_rel=2e-3)


def ex8():
    titlu("Ex. 8 - Invertor monofazat în punte H")
    V1 = 230.0
    for Vdc in [400.0, 350.0]:
        ma = math.sqrt(2) * V1 / Vdc
        print(f"  Vdc = {Vdc:.0f} V -> ma = {ma:.4f}")
    print(f"  maxim (undă dreptunghiulară) la 400 V: V1,rms = {4 / math.pi * 400 / math.sqrt(2):.1f} V")
    ma = math.sqrt(2) * V1 / VDC
    th = esantioane_perioada(2 ** 18)
    vA = spwm_picior(ma, 20, th=th)
    vB = spwm_picior(ma, 20, th=th, referinta=lambda x: -ma * np.sin(x))
    verifica("SPWM unipolar simulat: V1,rms = 230 V", armonici(vA - vB, 1)[1] / math.sqrt(2),
             V1, tol_rel=1e-4)


def ex9():
    titlu("Ex. 9 - Invertor trifazat alimentat la 600 V")
    Vdc = 600.0
    k = math.sqrt(3) / (2 * math.sqrt(2))
    print(f"  SPWM, ma = 1: {k * Vdc:.1f} V; cu injecție (ma = 2/sqrt3): "
          f"{k * 2 / math.sqrt(3) * Vdc:.1f} V; six-step: {math.sqrt(6) / math.pi * Vdc:.1f} V")
    ma = 400.0 / (k * Vdc)
    print(f"  pentru 400 V: ma = {ma:.4f} (> 1, dar < 2/sqrt3 = 1,1547)")
    th = esantioane_perioada(2 ** 18)
    ref = lambda x: ma * (np.sin(x) + np.sin(3 * x) / 6)
    sc = Vdc / VDC  # spwm_picior lucrează cu VDC = 400 V; scalăm
    va = spwm_picior(ma, 21, th=th, referinta=ref) * sc
    vb = spwm_picior(ma, 21, 2 * np.pi / 3, th=th, referinta=ref) * sc
    verifica("simulare cu injecție: V_LL1,rms = 400 V", armonici(va - vb, 1)[1] / math.sqrt(2),
             400.0, tol_rel=1e-4)


def ex10():
    titlu("Ex. 10 - Alegerea radiatorului")
    P, Rjc, Rcs, Ta, Tj = 3.0, 1.2, 0.3, 50.0, 125.0
    Rsa = (Tj - Ta) / P - Rjc - Rcs
    print(f"  R_th,sa <= {Rsa:.1f} K/W")
    verifica("verificare inversă: Tj cu R_sa calculat", Ta + P * (Rjc + Rcs + Rsa), Tj,
             tol_rel=1e-12)


def ex11(Irms_ex1, P_cond):
    titlu("Ex. 11 - Frecvența la care pierderile de comutație egalează conducția")
    V, Io, dI, tc = 12.0, 5.0, 2.0, 20e-9
    k = 0.5 * V * ((Io - dI / 2) * tc + (Io + dI / 2) * tc)  # J pe perioadă
    fs = P_cond / k
    print(f"  E_sw = {k * 1e6:.3f} uJ/perioadă, f_s = {fs / 1e3:.1f} kHz")
    verifica("verificare inversă: P_sw(f_s) = P_cond", k * fs, P_cond, tol_rel=1e-12)


def main():
    Irms, P = ex1()
    ex2()
    ex3()
    ex4()
    D, L, dI = ex5()
    ex6()
    ex7(D, L)
    ex8()
    ex9()
    ex10()
    ex11(Irms, P)


if __name__ == "__main__":
    main()
