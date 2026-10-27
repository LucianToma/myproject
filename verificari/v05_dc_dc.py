"""Verificări pentru Modulul 5 - Convertoare DC-DC (buck, boost, buck-boost).

Fiecare formulă din curs este comparată cu simularea exactă din
simulator_dcdc.py, care NU folosește formulele respective.
"""
import math

import numpy as np

from comun import titlu, verifica, verifica_conditie
from simulator_dcdc import (curent_intrare, iC, iL, medie_perioada, simuleaza,
                            vC, vL)


def extreme(rez, f):
    valori = np.concatenate([f(s) for s in rez["segmente"]])
    return float(valori.min()), float(valori.max())


def bilanturi(rez):
    """Verificări generale, valabile pentru orice convertor ideal în regim
    permanent: bilanțul volt-secundă, bilanțul de sarcină și conservarea
    puterii (comutatoare ideale => fără pierderi)."""
    tip, Vin, R = rez["tip"], rez["Vin"], rez["R"]
    Vo = medie_perioada(rez, vC)
    IL = medie_perioada(rez, iL)
    vL_med = medie_perioada(rez, vL)
    iC_med = medie_perioada(rez, iC)
    verifica_conditie(f"{tip}: media lui v_L ~ 0 (bilanț volt-secundă)",
                      abs(vL_med) < 1e-6 * Vin, f"<v_L> = {vL_med:.2e} V")
    verifica_conditie(f"{tip}: media lui i_C ~ 0 (bilanț de sarcină)",
                      abs(iC_med) < 1e-6 * IL, f"<i_C> = {iC_med:.2e} A")
    Pin = Vin * medie_perioada(rez, lambda s: curent_intrare(tip, s["topo"], iL(s)))
    Pout = medie_perioada(rez, lambda s: vC(s) ** 2 / R)
    verifica(f"{tip}: P_in = P_out (convertor ideal)", Pin, Pout, tol_rel=1e-6)
    return Vo, IL


def buck():
    titlu("BUCK - regim de conducție continuă (CCM)")
    Vin, D, L, C, R, fs = 24.0, 0.5, 100e-6, 47e-6, 6.0, 100e3
    rez = simuleaza("buck", Vin, D, L, C, R, fs)
    print(f"  regim permanent atins după {rez['perioade']} perioade")
    Vo, IL = bilanturi(rez)
    verifica("Vo = D*Vin", Vo, D * Vin, tol_rel=1e-6)
    verifica("I_L = Io = Vo/R", IL, Vo / R, tol_rel=1e-6)
    lo, hi = extreme(rez, iL)
    dIL = Vo * (1 - D) / (L * fs)
    verifica("Delta i_L = Vo(1-D)/(L fs)", hi - lo, dIL, tol_rel=5e-3)
    lo, hi = extreme(rez, vC)
    dVo = dIL / (8 * C * fs)
    verifica("Delta v_o = Delta i_L/(8 C fs)", hi - lo, dVo, tol_rel=2e-2)
    Lcrit = (1 - D) * R / (2 * fs)
    print(f"  L_crit = (1-D)R/(2fs) = {Lcrit * 1e6:.2f} uH  (L = {L * 1e6:.0f} uH > L_crit => CCM)")
    verifica_conditie("simularea confirmă CCM (i_L nu atinge zero)",
                      rez["tau_dcm"] is None and lo > 0)

    titlu("BUCK - limita CCM/DCM")
    for factor, asteptat_ccm in [(1.05, True), (0.95, False)]:
        r = simuleaza("buck", Vin, D, factor * Lcrit, C, R, fs)
        e_ccm = r["tau_dcm"] is None
        verifica_conditie(f"L = {factor:.2f} * L_crit -> "
                          f"{'CCM' if asteptat_ccm else 'DCM'}", e_ccm == asteptat_ccm)

    titlu("BUCK - regim de conducție discontinuă (DCM)")
    L = 10e-6
    K = 2 * L / (R / fs)
    M = 2 / (1 + math.sqrt(1 + 4 * K / D ** 2))
    print(f"  K = 2L/(R Ts) = {K:.4f} < K_crit = 1-D = {1 - D:.2f}  => DCM")
    for Cx, tol in [(47e-6, 3e-3), (470e-6, 3e-4)]:
        r = simuleaza("buck", Vin, D, L, Cx, R, fs)
        Vo = medie_perioada(r, vC)
        verifica(f"Vo = Vin*2/(1+sqrt(1+4K/D^2)), C = {Cx * 1e6:.0f} uF",
                 Vo, M * Vin, tol_rel=tol)
        D2 = r["tau_dcm"] * fs
        verifica(f"D2 = D(Vin-Vo)/Vo, C = {Cx * 1e6:.0f} uF", D2,
                 D * (Vin - M * Vin) / (M * Vin), tol_rel=10 * tol)
    print("  (formula DCM presupune ondulație mică a lui v_o; cu C mai mare,")
    print("   eroarea scade - vezi cele două rânduri de mai sus)")


def boost():
    titlu("BOOST - CCM")
    Vin, D, L, C, R, fs = 12.0, 0.5, 100e-6, 47e-6, 24.0, 100e3
    rez = simuleaza("boost", Vin, D, L, C, R, fs)
    print(f"  regim permanent atins după {rez['perioade']} perioade")
    Vo, IL = bilanturi(rez)
    verifica("Vo = Vin/(1-D)", Vo, Vin / (1 - D), tol_rel=1e-3)
    # I_L = Io/(1-D) este exactă doar pentru i_L perfect triunghiular;
    # ondulația lui v_C curbează ușor panta în OFF => eroare ~1e-4.
    verifica("I_L = Io/(1-D)", IL, (Vo / R) / (1 - D), tol_rel=1e-3)
    lo, hi = extreme(rez, iL)
    verifica("Delta i_L = Vin D/(L fs)", hi - lo, Vin * D / (L * fs), tol_rel=5e-3)
    lo, hi = extreme(rez, vC)
    verifica("Delta v_o = Io D/(C fs)", hi - lo, (Vo / R) * D / (C * fs), tol_rel=2e-2)
    Lcrit = D * (1 - D) ** 2 * R / (2 * fs)
    print(f"  L_crit = D(1-D)^2 R/(2fs) = {Lcrit * 1e6:.2f} uH")

    titlu("BOOST - DCM")
    L = 5e-6
    K = 2 * L / (R / fs)
    M = (1 + math.sqrt(1 + 4 * D ** 2 / K)) / 2
    print(f"  K = {K:.4f} < K_crit = D(1-D)^2 = {D * (1 - D) ** 2:.4f}  => DCM")
    r = simuleaza("boost", Vin, D, L, C, R, fs)
    verifica("Vo = Vin(1+sqrt(1+4D^2/K))/2", medie_perioada(r, vC), M * Vin, tol_rel=1e-3)


def boost_cu_rezistenta_bobinei():
    titlu("BOOST cu rezistența bobinei R_L: câștigul real este limitat")
    Vin, L, C, R, fs, RL = 12.0, 100e-6, 47e-6, 24.0, 100e3, 0.1
    for D in [0.5, 0.8, 0.9, 0.95]:
        r = simuleaza("boost", Vin, D, L, C, R, fs, RL=RL)
        Vo = medie_perioada(r, vC)
        M = 1 / (1 - D) / (1 + RL / (R * (1 - D) ** 2))
        verifica(f"D = {D:.2f}: Vo = Vin/(1-D) * 1/(1 + R_L/(R(1-D)^2))", Vo, M * Vin,
                 tol_rel=1e-3)
        Pin = Vin * medie_perioada(r, iL)
        verifica(f"D = {D:.2f}: randament = 1/(1 + R_L/(R(1-D)^2))", (Vo ** 2 / R) / Pin,
                 1 / (1 + RL / (R * (1 - D) ** 2)), tol_rel=1e-3)
    Dg = np.linspace(0.5, 0.999, 2000)
    Mg = 1 / (1 - Dg) / (1 + RL / (R * (1 - Dg) ** 2))
    D_opt = 1 - math.sqrt(RL / R)
    verifica("câștigul maxim apare la D = 1 - sqrt(R_L/R)", float(Dg[np.argmax(Mg)]), D_opt,
             tol_rel=1e-3)
    verifica("câștigul maxim = sqrt(R/R_L)/2", float(Mg.max()), 0.5 * math.sqrt(R / RL),
             tol_rel=1e-5)


def buck_boost():
    titlu("BUCK-BOOST - CCM")
    Vin, D, L, C, R, fs = 12.0, 0.4, 100e-6, 47e-6, 8.0, 100e3
    rez = simuleaza("buck-boost", Vin, D, L, C, R, fs)
    print(f"  regim permanent atins după {rez['perioade']} perioade")
    Vo, IL = bilanturi(rez)
    verifica("|Vo| = Vin D/(1-D)", Vo, Vin * D / (1 - D), tol_rel=1e-3)
    verifica("I_L = Io/(1-D)", IL, (Vo / R) / (1 - D), tol_rel=1e-3)
    lo, hi = extreme(rez, iL)
    verifica("Delta i_L = Vin D/(L fs)", hi - lo, Vin * D / (L * fs), tol_rel=5e-3)
    lo, hi = extreme(rez, vC)
    verifica("Delta v_o = Io D/(C fs)", hi - lo, (Vo / R) * D / (C * fs), tol_rel=2e-2)

    titlu("BUCK-BOOST - DCM")
    L = 5e-6
    K = 2 * L / (R / fs)
    print(f"  K = {K:.4f} < K_crit = (1-D)^2 = {(1 - D) ** 2:.4f}  => DCM")
    r = simuleaza("buck-boost", Vin, D, L, C, R, fs)
    verifica("|Vo| = Vin D/sqrt(K)", medie_perioada(r, vC), Vin * D / math.sqrt(K),
             tol_rel=1e-3)


def caracteristica_ccm():
    titlu("Caracteristica de transfer în CCM pentru mai multe valori ale lui D")
    fs, C = 100e3, 100e-6
    for D in [0.2, 0.35, 0.65, 0.8]:
        # L ales de 10 ori peste L_crit al fiecărei topologii => CCM sigur
        r = simuleaza("buck", 10.0, D, 10 * (1 - D) * 5 / (2 * fs), C, 5.0, fs)
        verifica(f"buck  D={D:.2f}: Vo/Vin = D", medie_perioada(r, vC) / 10, D, tol_rel=1e-6)
        r = simuleaza("boost", 10.0, D, 10 * D * (1 - D) ** 2 * 50 / (2 * fs), C, 50.0, fs)
        verifica(f"boost D={D:.2f}: Vo/Vin = 1/(1-D)", medie_perioada(r, vC) / 10,
                 1 / (1 - D), tol_rel=2e-3)
        r = simuleaza("buck-boost", 10.0, D, 10 * (1 - D) ** 2 * 20 / (2 * fs), C, 20.0, fs)
        verifica(f"b-b   D={D:.2f}: |Vo|/Vin = D/(1-D)", medie_perioada(r, vC) / 10,
                 D / (1 - D), tol_rel=2e-3)


def main():
    buck()
    boost()
    boost_cu_rezistenta_bobinei()
    buck_boost()
    caracteristica_ccm()


if __name__ == "__main__":
    main()
