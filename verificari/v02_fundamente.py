"""Verificări pentru Modulul 2 - Mărimi și relații fundamentale.

Fiecare formulă închisă (medie, valoare efectivă, putere, factor de putere)
este comparată cu integrarea numerică directă a formei de undă.
"""
import math

import numpy as np

from comun import (armonici, efectiv, esantioane_perioada, faza_armonica, medie,
                   thd, titlu, verifica)

N = 2 ** 20


def medii_si_efective():
    titlu("Valori medii și efective ale formelor de undă uzuale")
    th = esantioane_perioada(N)
    u = th / (2 * np.pi)  # timpul normat t/T in [0, 1)

    Vm = 100.0
    verifica("sinusoidă: V_rms = Vm/sqrt2", efectiv(Vm * np.sin(th)), Vm / math.sqrt(2),
             tol_rel=1e-9)

    I, D = 10.0, 0.3
    puls = np.where(u < D, I, 0.0)
    verifica("dreptunghi (I, D): medie = D I", medie(puls), D * I, tol_rel=1e-5)
    verifica("dreptunghi (I, D): rms = I sqrt(D)", efectiv(puls), I * math.sqrt(D),
             tol_rel=1e-5)

    Ipk = 6.0
    tri = Ipk * (1 - np.abs(2 * u - 1))  # triunghi simetric 0 -> Ipk -> 0
    dinte = Ipk * u  # dinte de fierăstrău
    verifica("triunghi 0..Ipk: rms = Ipk/sqrt3", efectiv(tri), Ipk / math.sqrt(3), tol_rel=1e-6)
    verifica("dinte de fierăstrău 0..Ipk: rms = Ipk/sqrt3", efectiv(dinte), Ipk / math.sqrt(3),
             tol_rel=1e-5)

    I0, dI = 10.0, 3.0
    ond = I0 + dI * (np.abs(2 * u - 1) - 0.5)  # c.c. + triunghi vârf-vârf dI
    verifica("c.c. + ondulație triunghiulară: rms = sqrt(I^2 + dI^2/12)", efectiv(ond),
             math.sqrt(I0 ** 2 + dI ** 2 / 12), tol_rel=1e-9)

    # curentul tranzistorului dintr-un buck: trapez pe intervalul D, zero în rest
    D = 0.25
    trapez = np.where(u < D, I0 - dI / 2 + dI * u / D, 0.0)
    verifica("trapez (comutator buck): medie = D I", medie(trapez), D * I0, tol_rel=1e-5)
    verifica("trapez (comutator buck): rms = sqrt(D (I^2 + dI^2/12))", efectiv(trapez),
             math.sqrt(D * (I0 ** 2 + dI ** 2 / 12)), tol_rel=1e-5)

    # Parseval: valoarea efectivă a unei sume de armonici
    v = 10 + 50 * np.sin(th) + 20 * np.sin(3 * th + 0.4) + 7 * np.cos(5 * th)
    verifica("Parseval: rms = sqrt(V0^2 + sum(Vn^2/2))", efectiv(v),
             math.sqrt(10 ** 2 + (50 ** 2 + 20 ** 2 + 7 ** 2) / 2), tol_rel=1e-12)


def puteri():
    titlu("Puterea activă și factorul de putere")
    th = esantioane_perioada(N)
    V, I, phi = 230.0, 10.0, math.acos(0.8)
    v = math.sqrt(2) * V * np.sin(th)
    i = math.sqrt(2) * I * np.sin(th - phi)
    P = medie(v * i)
    verifica("regim sinusoidal: P = V I cos(phi)", P, V * I * math.cos(phi), tol_rel=1e-9)
    verifica("regim sinusoidal: PF = cos(phi)", P / (efectiv(v) * efectiv(i)), math.cos(phi),
             tol_rel=1e-9)

    # tensiune sinusoidală, curent deformat: doar fundamentala transportă P
    i = (math.sqrt(2) * 10 * np.sin(th - 0.3) + math.sqrt(2) * 4 * np.sin(3 * th + 1.0)
         + math.sqrt(2) * 2 * np.sin(5 * th - 0.5))
    P = medie(v * i)
    verifica("curent deformat: P = V I1 cos(phi1) (armonicile nu aduc putere)", P,
             V * 10 * math.cos(0.3), tol_rel=1e-9)
    I1 = armonici(i, 1)[1] / math.sqrt(2)
    phi1 = faza_armonica(i, 1) - faza_armonica(v, 1)
    PF = P / (efectiv(v) * efectiv(i))
    verifica("curent deformat: PF = (I1/I) cos(phi1)", PF,
             I1 / efectiv(i) * math.cos(phi1), tol_rel=1e-9)
    verifica("curent deformat: I1/I = 1/sqrt(1 + THD^2)", I1 / efectiv(i),
             1 / math.sqrt(1 + thd(i, 50) ** 2), tol_rel=1e-9)

    # curent dreptunghiular în fază cu tensiunea (ex. redresor cu L foarte mare)
    i = np.where(th < np.pi, 1.0, -1.0)
    PF = medie(v * i) / (efectiv(v) * efectiv(i))
    verifica("curent dreptunghiular în fază: PF = 2 sqrt2/pi = 0,900", PF,
             2 * math.sqrt(2) / math.pi, tol_rel=1e-6)


def bobina_si_condensator():
    titlu("Bobina și condensatorul în regim periodic")
    # Dacă media tensiunii pe bobină NU este zero, curentul crește la fiecare
    # perioadă cu <v_L>*T/L: regim permanent periodic => <v_L> = 0.
    L, T = 100e-6, 10e-6
    n = 10000
    h = T / n
    u = np.arange(n) / n
    vL = np.where(u < 0.5, 12.0, -11.0)  # media = +0,5 V
    di = np.sum(vL) * h / L
    verifica("creșterea lui i_L pe perioadă = <v_L> T / L", di, medie(vL) * T / L, tol_rel=1e-12)
    vL = np.where(u < 0.5, 12.0, -12.0)
    verifica("<v_L> = 0 => i_L revine la valoarea inițială", np.sum(vL) * h / L, 0.0,
             tol_abs=1e-12)
    # Energia înmagazinată: W = L I^2 / 2 = integrala lui v*i
    I = 5.0
    t = np.linspace(0, 1e-3, 100001)
    i = I * t / t[-1]  # rampă de curent
    v = L * np.gradient(i, t)
    verifica("energia bobinei: integrala(v i dt) = L I^2/2", np.trapezoid(v * i, t),
             L * I ** 2 / 2, tol_rel=1e-6)
    C, V = 47e-6, 24.0
    vC = V * t / t[-1]
    iC = C * np.gradient(vC, t)
    verifica("energia condensatorului: integrala(v i dt) = C V^2/2", np.trapezoid(vC * iC, t),
             C * V ** 2 / 2, tol_rel=1e-6)


def main():
    medii_si_efective()
    puteri()
    bobina_si_condensator()


if __name__ == "__main__":
    main()
