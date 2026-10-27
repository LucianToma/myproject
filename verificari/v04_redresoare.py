"""Verificări pentru Modulul 4 - Redresoare.

Metode folosite (independente de formulele din curs):
  * integrarea numerică a formelor de undă ideale (medie, efectiv);
  * pentru filtrul capacitiv: soluția semi-analitică exactă cu diode ideale
    și o simulare în timp (Runge-Kutta 4) cu rezistență de sursă mică;
  * pentru redresorul comandat: simularea în timp a sarcinii R-L cu logica
    de conducție a tiristoarelor (aprindere la alfa, stingere la i = 0);
  * pentru puntea trifazată: construcția numerică a tensiunii de ieșire ca
    tensiunea de linie selectată de perechea de diode/tiristoare în
    conducție.
"""
import math

import numpy as np

from comun import (armonici, efectiv, esantioane_perioada, faza_armonica,
                   medie, thd, titlu, verifica, verifica_conditie)

N = 2 ** 20  # eșantioane pe perioadă pentru formele de undă ideale


def forme_ideale():
    titlu("Redresoare necomandate cu sarcină rezistivă: medie și valoare efectivă")
    Vs = 230.0
    Vm = math.sqrt(2) * Vs
    th = esantioane_perioada(N)
    v = Vm * np.sin(th)
    mono = np.maximum(v, 0)
    dubla = np.abs(v)
    verifica("monoalternanță: V_dc = Vm/pi", medie(mono), Vm / math.pi, tol_rel=1e-6)
    verifica("monoalternanță: V_rms = Vm/2", efectiv(mono), Vm / 2, tol_rel=1e-6)
    verifica("dublă alternanță: V_dc = 2Vm/pi = 0,9 Vs", medie(dubla), 2 * Vm / math.pi,
             tol_rel=1e-6)
    verifica("dublă alternanță: V_rms = Vs", efectiv(dubla), Vs, tol_rel=1e-6)
    FF = efectiv(dubla) / medie(dubla)
    verifica("dublă alternanță: factor de formă = pi/(2 sqrt2)", FF,
             math.pi / (2 * math.sqrt(2)), tol_rel=1e-6)
    verifica("dublă alternanță: factor de ondulație = sqrt(FF^2 - 1)",
             efectiv(dubla - medie(dubla)) / medie(dubla),
             math.sqrt(FF ** 2 - 1), tol_rel=1e-6)
    a = armonici(dubla, 8)
    verifica_conditie("dublă alternanță: frecvența ondulației = 2f (armonica 1 lipsește)",
                      a[1] < 1e-6 * a[2], f"A1 = {a[1]:.1e} V, A2 = {a[2]:.2f} V")
    verifica("dublă alternanță: A2 = 4Vm/(3pi)", a[2], 4 * Vm / (3 * math.pi), tol_rel=1e-6)


# ---------------------------------------------------------------------------
# Redresor în punte cu filtru capacitiv
# ---------------------------------------------------------------------------

def filtru_ideal(Vm, f, R, C, puncte=200001):
    """Soluția exactă pentru diode ideale și sursă fără impedanță.

    Conducția se oprește la theta_off = pi - atan(wRC), când panta lui |v_s|
    devine mai mică decât panta de descărcare; apoi v_C scade exponențial
    până întâlnește din nou |v_s| (theta_on, găsit prin bisecție).
    """
    w = 2 * math.pi * f
    wrc = w * R * C
    th_off = math.pi - math.atan(wrc)
    V_off = Vm * math.sin(th_off)

    def desc(th):
        return V_off * math.exp(-(th - th_off) / wrc)

    a, b = math.pi, 1.5 * math.pi
    for _ in range(200):
        m = 0.5 * (a + b)
        if Vm * math.sin(m - math.pi) < desc(m):
            a = m
        else:
            b = m
    th_on = 0.5 * (a + b)
    Vmin = desc(th_on)
    # media pe o semiperioadă [th_on - pi, th_on]
    th = np.linspace(th_on - math.pi, th_on, puncte)
    v = np.where(th <= th_off, Vm * np.sin(th),
                 V_off * np.exp(-(th - th_off) / wrc))
    Vdc = np.trapezoid(v, th) / math.pi
    # tensiunea medie pe intervalul de descărcare (exponențiala de la V_off la Vmin)
    durata = th_on - th_off
    V_med_desc = V_off * wrc / durata * (1 - math.exp(-durata / wrc))
    return {"th_off": th_off, "th_on": th_on, "Vmin": Vmin, "dV": Vm - Vmin, "Vdc": Vdc,
            "unghi_conductie": th_off - (th_on - math.pi), "V_off": V_off,
            "V_med_desc": V_med_desc}


def simuleaza_filtru(Vm, f, R, C, Rs, perioade=25, pasi=20000):
    """Punte de diode ideale + rezistență de sursă Rs, integrare RK4.

    C dv/dt = max(|v_s| - v, 0)/Rs - v/R.  Returnează ultima perioadă.
    """
    w = 2 * math.pi * f
    h = 1.0 / (f * pasi)

    def deriv(t, v):
        vs = abs(Vm * math.sin(w * t))
        i = (vs - v) / Rs if vs > v else 0.0
        return (i - v / R) / C

    v = 0.0
    t = 0.0
    tv = np.empty(pasi)
    vv = np.empty(pasi)
    for k in range(perioade):
        inceput = v
        for j in range(pasi):
            if k == perioade - 1:
                tv[j] = t
                vv[j] = v
            k1 = deriv(t, v)
            k2 = deriv(t + h / 2, v + h * k1 / 2)
            k3 = deriv(t + h / 2, v + h * k2 / 2)
            k4 = deriv(t + h, v + h * k3)
            v += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
            t += h
    vs = Vm * np.sin(w * tv)
    i_punte = np.where(np.abs(vs) > vv, (np.abs(vs) - vv) / Rs, 0.0)
    i_sursa = np.sign(vs) * i_punte
    return {"t": tv, "vC": vv, "vs": vs, "is": i_sursa,
            "periodicitate": abs(v - inceput)}


def filtru_capacitiv():
    titlu("Redresor în punte cu filtru capacitiv: ondulația tensiunii")
    Vs, f, R, C = 12.0, 50.0, 20.0, 4700e-6
    Vm = math.sqrt(2) * Vs
    aprox = Vm / (2 * f * R * C)
    ex = filtru_ideal(Vm, f, R, C)
    sim = simuleaza_filtru(Vm, f, R, C, Rs=0.01)
    dV_sim = sim["vC"].max() - sim["vC"].min()
    print(f"  Vm = {Vm:.3f} V; aproximare Vm/(2fRC) = {aprox:.4f} V")
    print(f"  soluție exactă (diode ideale): Delta V = {ex['dV']:.4f} V, "
          f"unghi de conducție = {math.degrees(ex['unghi_conductie']):.1f} grade")
    print(f"  simulare RK4 (Rs = 0,01 ohm):  Delta V = {dV_sim:.4f} V")
    verifica("simularea (Rs mic) reproduce soluția exactă: Delta V", dV_sim, ex["dV"],
             tol_rel=2e-2)
    verifica("simularea (Rs mic) reproduce soluția exactă: V_dc", medie(sim["vC"]),
             ex["Vdc"], tol_rel=5e-3)
    verifica_conditie("aproximarea Vm/(2fRC) este acoperitoare (>= valoarea exactă)",
                      aprox >= ex["dV"], f"{aprox:.4f} V >= {ex['dV']:.4f} V")
    print(f"  eroarea aproximării: {100 * (aprox / ex['dV'] - 1):+.1f} %")
    # Descompunerea exactă a erorii: pe descărcare C dv/dt = -v/R, deci
    # V_off - Vmin = V_med_desc * t_desc / (RC), cu t_desc = (T/2)(1 - unghi_cond/pi).
    # Față de aproximare apar doi factori: (a) durata descărcării < T/2 și
    # (b) curentul de descărcare V_med_desc/R < Vm/R.
    fa = 1 - ex["unghi_conductie"] / math.pi
    fb = ex["V_med_desc"] / Vm
    print(f"  factor (a) durata descărcării: {fa:.4f}  (aproximarea +{100 * (1 / fa - 1):.1f} %)")
    print(f"  factor (b) curentul mediu de descărcare: {fb:.4f}  "
          f"(aproximarea +{100 * (1 / fb - 1):.1f} %)")
    verifica("Vm/(2fRC) * (a) * (b) = V_off - Vmin (descompunere exactă)", aprox * fa * fb,
             ex["V_off"] - ex["Vmin"], tol_rel=1e-6)
    verifica("aproximarea V_dc = Vm - Delta V/2", Vm - aprox / 2, ex["Vdc"], tol_rel=2e-2)

    print("  Eroarea aproximării Vm/(2fRC) scade când ondulația relativă scade:")
    erori = []
    for Cx in [2200e-6, 4700e-6, 10000e-6, 47000e-6]:
        exx = filtru_ideal(Vm, f, R, Cx)
        apx = Vm / (2 * f * R * Cx)
        erori.append(apx / exx["dV"] - 1)
        print(f"    C = {Cx * 1e6:6.0f} uF: Delta V/Vm = {100 * exx['dV'] / Vm:5.2f} %, "
              f"aproximare {apx:.4f} V vs exact {exx['dV']:.4f} V "
              f"(eroare {100 * erori[-1]:+.1f} %)")
    verifica_conditie("eroarea scade monoton cu C și rămâne pozitivă (acoperitoare)",
                      all(e > 0 for e in erori) and all(a > b for a, b in zip(erori, erori[1:])))


def factor_putere_filtru():
    titlu("Redresor cu filtru capacitiv: factorul de putere al curentului absorbit")
    Vs, f, R, C, Rs = 12.0, 50.0, 20.0, 4700e-6, 0.5
    Vm = math.sqrt(2) * Vs
    sim = simuleaza_filtru(Vm, f, R, C, Rs)
    vs, i = sim["vs"], sim["is"]
    P = medie(vs * i)
    PF_direct = P / (efectiv(vs) * efectiv(i))
    a = armonici(i, 200)
    I1 = a[1] / math.sqrt(2)
    phi1 = faza_armonica(i, 1) - faza_armonica(vs, 1)
    DPF = math.cos(phi1)
    PF_factori = (I1 / efectiv(i)) * DPF
    THD = thd(i, 2000)
    print(f"  I_rms = {efectiv(i):.3f} A, I_1 = {I1:.3f} A, THD = {THD * 100:.1f} %, "
          f"cos(phi1) = {DPF:.4f}")
    verifica("PF = P/(V I) = cos(phi1) * I1/I", PF_direct, PF_factori, tol_rel=1e-4)
    verifica("I1/I = 1/sqrt(1+THD^2)", I1 / efectiv(i), 1 / math.sqrt(1 + THD ** 2),
             tol_rel=1e-4)
    P_sarcina = medie(sim["vC"] ** 2) / R
    P_Rs = medie(i ** 2) * Rs
    verifica("bilanț de putere: P_sursa = P_sarcina + P_Rs", P, P_sarcina + P_Rs, tol_rel=1e-3)
    verifica_conditie("curent puternic deformat: PF < 0,7", PF_direct < 0.7,
                      f"PF = {PF_direct:.3f}")


# ---------------------------------------------------------------------------
# Redresor monofazat comandat (punte cu tiristoare), sarcină R-L
# ---------------------------------------------------------------------------

def simuleaza_tiristoare(Vs, f, R, L, alfa, perioade=80, pasi=20000):
    """Integrator exponențial pentru L di/dt = v_o - R i.

    Perechea A (T1,T4) se aprinde la alfa și aplică v_o = v_s, perechea B
    (T2,T3) se aprinde la pi + alfa și aplică v_o = -v_s. O pereche se
    stinge când curentul se anulează. Comutație ideală (fără L de rețea).
    """
    Vm = math.sqrt(2) * Vs
    w = 2 * math.pi * f
    h = 1.0 / (f * pasi)
    a = math.exp(-h * R / L)
    i = 0.0
    pereche = 0  # 0 = niciuna, +1 = A, -1 = B
    rezultate = None
    for k in range(perioade):
        ultim = k == perioade - 1
        if ultim:
            vo_arr = np.empty(pasi)
            i_arr = np.empty(pasi)
            is_arr = np.empty(pasi)
        for j in range(pasi):
            th = (j + 0.5) * 2 * math.pi / pasi  # mijlocul pasului
            if j == int(round(alfa / (2 * math.pi) * pasi)):
                pereche = +1
            if j == int(round((math.pi + alfa) / (2 * math.pi) * pasi)):
                pereche = -1
            vs = Vm * math.sin(th)
            vo = pereche * vs if pereche != 0 else 0.0
            i_nou = i * a + vo / R * (1 - a)
            if pereche != 0 and i_nou <= 0:
                i_nou, pereche, vo = 0.0, 0, 0.0
            if ultim:
                vo_arr[j] = vo
                i_arr[j] = 0.5 * (i + i_nou)
                is_arr[j] = pereche * 0.5 * (i + i_nou)
            i = i_nou
    th = (np.arange(pasi) + 0.5) * 2 * math.pi / pasi
    return {"th": th, "vo": vo_arr, "io": i_arr, "is": is_arr, "vs": Vm * np.sin(th)}


def redresor_comandat():
    titlu("Punte monofazată cu tiristoare, sarcină R-L")
    Vs, f, R = 230.0, 50.0, 10.0
    Vm = math.sqrt(2) * Vs
    for alfa_grd in [30, 60]:
        alfa = math.radians(alfa_grd)
        sim = simuleaza_tiristoare(Vs, f, R, 1.0, alfa)
        verifica_conditie(f"alfa = {alfa_grd} grade, L = 1 H: conducție continuă",
                          sim["io"].min() > 0, f"i_min = {sim['io'].min():.2f} A")
        Vdc = medie(sim["vo"])
        verifica(f"alfa = {alfa_grd} grade: V_dc = 0,9 Vs cos(alfa)", Vdc,
                 2 * Vm / math.pi * math.cos(alfa), tol_rel=2e-3)
        PF = medie(sim["vs"] * sim["is"]) / (efectiv(sim["vs"]) * efectiv(sim["is"]))
        verifica(f"alfa = {alfa_grd} grade: PF ~ 0,9 cos(alfa) (L mare)", PF,
                 2 * math.sqrt(2) / math.pi * math.cos(alfa), tol_rel=1e-2)
    alfa = math.radians(60)
    sim = simuleaza_tiristoare(Vs, f, R, 0.02, alfa)
    verifica_conditie("alfa = 60 grade, L = 20 mH: conducție discontinuă",
                      sim["io"].min() == 0.0)
    Vdc = medie(sim["vo"])
    # unghiul de stingere beta: sfârșitul ultimului pas cu curent nenul în
    # intervalul [alfa, pi + alfa) (conducția perechii A)
    n = len(sim["th"])
    j0 = int(round(alfa / (2 * math.pi) * n))
    j1 = int(round((math.pi + alfa) / (2 * math.pi) * n))
    j_ultim = j0 + np.nonzero(sim["io"][j0:j1] > 0)[0].max()
    beta = (j_ultim + 1) * 2 * math.pi / n
    print(f"  unghi de stingere din simulare: beta = {math.degrees(beta):.2f} grade")
    verifica("discontinuu: V_dc = (Vm/pi)(cos alfa - cos beta)", Vdc,
             Vm / math.pi * (math.cos(alfa) - math.cos(beta)), tol_rel=2e-3)
    verifica_conditie("discontinuu: V_dc > 0,9 Vs cos(alfa)",
                      Vdc > 2 * Vm / math.pi * math.cos(alfa),
                      f"{Vdc:.1f} V > {2 * Vm / math.pi * math.cos(alfa):.1f} V")


# ---------------------------------------------------------------------------
# Punte trifazată (6 pulsuri)
# ---------------------------------------------------------------------------

def punte_trifazata(VLL, alfa, Id=1.0, n=2 ** 18):
    """Tensiunea de ieșire și curentul fazei a pentru puntea trifazată.

    La fiecare moment conduce perechea (sus, jos) care avea tensiunea de
    linie maximă la momentul theta - alfa (comutație naturală întârziată cu
    alfa); curentul de sarcină este considerat constant (L foarte mare).
    """
    Vm_f = VLL * math.sqrt(2) / math.sqrt(3)
    th = esantioane_perioada(n)
    faze = lambda x: np.array([np.sin(x), np.sin(x - 2 * np.pi / 3),
                               np.sin(x + 2 * np.pi / 3)]) * Vm_f
    v = faze(th)
    v_int = faze(th - alfa)
    perechi = [(p, q) for p in range(3) for q in range(3) if p != q]
    v_linie_int = np.array([v_int[p] - v_int[q] for p, q in perechi])
    idx = np.argmax(v_linie_int, axis=0)
    sus = np.array([perechi[k][0] for k in idx])
    jos = np.array([perechi[k][1] for k in idx])
    vo = v[sus, np.arange(n)] - v[jos, np.arange(n)]
    ia = Id * ((sus == 0).astype(float) - (jos == 0).astype(float))
    return th, vo, ia, v[0]


def redresor_trifazat():
    titlu("Punte trifazată cu diode/tiristoare (6 pulsuri)")
    VLL = 400.0
    for alfa_grd in [0, 30, 60]:
        alfa = math.radians(alfa_grd)
        th, vo, ia, va = punte_trifazata(VLL, alfa)
        verifica(f"alfa = {alfa_grd:2d} grade: V_dc = 1,35 VLL cos(alfa)", medie(vo),
                 3 * math.sqrt(2) / math.pi * VLL * math.cos(alfa), tol_rel=1e-4)
        I1 = armonici(ia, 1)[1] / math.sqrt(2)
        verifica(f"alfa = {alfa_grd:2d} grade: I1/I = 3/pi", I1 / efectiv(ia), 3 / math.pi,
                 tol_rel=1e-4)
        phi1 = faza_armonica(ia, 1) - faza_armonica(va, 1)
        verifica(f"alfa = {alfa_grd:2d} grade: cos(phi1) = cos(alfa)",
                 math.cos(phi1), math.cos(alfa), tol_rel=1e-4, tol_abs=1e-4)
    th, vo, ia, va = punte_trifazata(VLL, 0.0)
    verifica("curent 120 grade: THD = 31,08 %", thd(ia),
             math.sqrt(2 / 3 - 6 / math.pi ** 2) / (math.sqrt(6) / math.pi), tol_rel=1e-4)
    verifica("curent 120 grade: I_rms = sqrt(2/3) Id", efectiv(ia), math.sqrt(2 / 3),
             tol_rel=1e-4)
    a = armonici(vo, 40)
    multipli6 = [k for k in range(1, 41) if k % 6 == 0]
    altele = [k for k in range(1, 41) if k % 6 != 0]
    verifica_conditie("ieșirea conține doar armonici de ordin 6k (ondulație la 6f = 300 Hz)",
                      max(a[altele]) < 1e-3 * a[6],
                      f"max(A_non6k) = {max(a[altele]):.2e} V, A6 = {a[6]:.2f} V")
    # armonicile curentului: 6k +/- 1, cu amplitudini I1/h
    ai = armonici(ia, 25)
    for h in [5, 7, 11, 13]:
        verifica(f"curent: I_{h} = I_1/{h}", ai[h], ai[1] / h, tol_rel=2e-3)
    verifica_conditie("curent: armonicile 2, 3, 4, 6, 9 lipsesc",
                      max(ai[[2, 3, 4, 6, 9]]) < 1e-3 * ai[1])


def suprapunere_comutatie():
    titlu("Inductanța rețelei L_s: suprapunerea comutației (curent de sarcină Id constant)")
    Vs, f, Ls, Id = 230.0, 50.0, 2e-3, 20.0
    Vm = math.sqrt(2) * Vs
    w = 2 * math.pi * f
    # Punte monofazată: la theta = 0 curentul de rețea trebuie să treacă din -Id
    # în +Id; cât timp durează, toate cele 4 diode conduc, v_o = 0 și
    # L_s di/dt = v_s. Integrăm numeric până când i atinge +Id.
    n = 2 ** 20
    dth = math.pi / n
    th = (np.arange(n) + 0.5) * dth
    i = -Id + np.cumsum(Vm * np.sin(th) * dth) / (w * Ls)
    u = th[np.argmax(i >= Id)]
    vo = np.where(th < u, 0.0, Vm * np.sin(th))
    print(f"  monofazat: unghi de suprapunere u = {math.degrees(u):.2f} grade")
    verifica("monofazat: cos u = 1 - 2 w Ls Id / Vm", math.cos(u), 1 - 2 * w * Ls * Id / Vm,
             tol_rel=1e-4)
    verifica("monofazat: V_dc = 0,9 Vs - 2 w Ls Id / pi", float(np.mean(vo)),
             2 * Vm / math.pi - 2 * w * Ls * Id / math.pi, tol_rel=1e-4)
    # Punte trifazată (grupul de sus, comutație a -> b, alfa = 0): în timpul
    # suprapunerii v_o,sus = (v_a + v_b)/2 și L_s di_b/dt = (v_b - v_a)/2.
    VLL = 400.0
    Vmf = VLL * math.sqrt(2) / math.sqrt(3)
    th0 = 5 * math.pi / 6  # aici v_b devine mai mare decât v_a (comutație naturală)
    x = th0 + (np.arange(n) + 0.5) * dth
    va = Vmf * np.sin(x)
    vb = Vmf * np.sin(x - 2 * math.pi / 3)
    ib = np.cumsum((vb - va) / 2 * dth) / (w * Ls)
    k = np.argmax(ib >= Id)
    arie = np.sum(((vb - va) / 2)[:k]) * dth  # volți*radiani pierduți la o comutație
    verifica("trifazat: aria pierdută la o comutație = w Ls Id", arie, w * Ls * Id, tol_rel=1e-4)
    dV = 6 * arie / (2 * math.pi)
    verifica("trifazat: V_dc = 1,35 VLL - 3 w Ls Id / pi", 3 * math.sqrt(2) / math.pi * VLL - dV,
             3 * math.sqrt(2) / math.pi * VLL - 3 * w * Ls * Id / math.pi, tol_rel=1e-5)


def main():
    forme_ideale()
    filtru_capacitiv()
    factor_putere_filtru()
    redresor_comandat()
    redresor_trifazat()
    suprapunere_comutatie()


if __name__ == "__main__":
    main()
