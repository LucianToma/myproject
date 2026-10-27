"""Verificări pentru Modulul 6 - Invertoare.

Metode folosite (independente de formulele din curs):
  * FFT pe forma de undă eșantionată (2^18 puncte pe perioada fundamentalei);
  * pentru PWM sinusoidal: calculul exact al coeficienților Fourier din
    momentele de comutație (găsite prin bisecție), fără eșantionare;
  * comparație cu soluția analitică a PWM-ului cu eșantionare naturală
    (funcții Bessel), calculată independent prin integrare numerică.
"""
import math

import numpy as np

from comun import (armonici, bessel_j, efectiv, esantioane_perioada, thd, titlu,
                   verifica, verifica_conditie)

N = 2 ** 18
VDC = 400.0


def purtatoare(theta, mf):
    """Purtătoare triunghiulară între -1 și +1, mf perioade pe 2*pi."""
    u = (mf * theta / (2 * np.pi)) % 1.0
    return 1.0 - 4.0 * np.abs(u - 0.5)


def unda_dreptunghiulara():
    titlu("Invertor în semipunte, comandă în undă dreptunghiulară")
    th = esantioane_perioada(N)
    v = np.where(th < np.pi, VDC / 2, -VDC / 2)
    a = armonici(v, 15)
    verifica("V1 = (4/pi)(Vdc/2)", a[1], 4 / math.pi * VDC / 2, tol_rel=1e-5)
    for h in [3, 5, 7]:
        verifica(f"V{h} = V1/{h}", a[h], a[1] / h, tol_rel=1e-4)
    verifica_conditie("armonicile pare lipsesc", max(a[[2, 4, 6]]) < 1e-9 * a[1])
    verifica("THD = sqrt(pi^2/8 - 1) = 48,34 %", thd(v), math.sqrt(math.pi ** 2 / 8 - 1),
             tol_rel=1e-4)

    titlu("Punte H cu defazare (undă cvasi-dreptunghiulară de lățime delta)")
    for delta_grd in [180, 150, 120]:
        d = math.radians(delta_grd)
        v = np.where(np.abs(th - np.pi / 2) < d / 2, VDC,
                     np.where(np.abs(th - 3 * np.pi / 2) < d / 2, -VDC, 0.0))
        a = armonici(v, 9)
        verifica(f"delta = {delta_grd} grade: V1 = (4Vdc/pi) sin(delta/2)", a[1],
                 4 * VDC / math.pi * math.sin(d / 2), tol_rel=1e-4)
        verifica(f"delta = {delta_grd} grade: V3 = (4Vdc/(3pi)) |sin(3 delta/2)|", a[3],
                 4 * VDC / (3 * math.pi) * abs(math.sin(3 * d / 2)), tol_rel=1e-3,
                 tol_abs=1e-2)


# ---------------------------------------------------------------------------
# PWM sinusoidal: coeficienți Fourier exacți din fronturi
# ---------------------------------------------------------------------------

def fronturi_spwm(ma, mf, defazaj=0.0):
    """Momentele de comutație ale comparației ma*sin(theta - defazaj) vs.
    purtătoare, pe [0, 2*pi). Pe fiecare semi-perioadă a purtătoarei
    diferența este monotonă (panta purtătoarei 2*mf/pi > ma), deci există
    cel mult o intersecție, găsită prin bisecție."""
    fronturi = []
    pas = np.pi / mf
    f = lambda x: ma * math.sin(x - defazaj) - float(purtatoare(np.array(x), mf))
    for k in range(2 * mf):
        a, b = k * pas, (k + 1) * pas
        fa, fb = f(a + 1e-15), f(b - 1e-15)
        if fa * fb > 0:
            continue
        for _ in range(100):
            m = 0.5 * (a + b)
            if f(m) * fa > 0:
                a = m
            else:
                b = m
        fronturi.append(0.5 * (a + b))
    return np.array(fronturi)


def fourier_din_fronturi(ma, mf, h, defazaj=0.0):
    """Amplitudinea armonicii h a undei +/-Vdc/2, calculată exact pe segmente."""
    fr = fronturi_spwm(ma, mf, defazaj)
    limite = np.concatenate([[0.0], fr, [2 * np.pi]])
    an = bn = 0.0
    for t0, t1 in zip(limite[:-1], limite[1:]):
        mijloc = 0.5 * (t0 + t1)
        sus = ma * math.sin(mijloc - defazaj) > float(purtatoare(np.array(mijloc), mf))
        V = VDC / 2 if sus else -VDC / 2
        an += V * (math.sin(h * t1) - math.sin(h * t0)) / h
        bn += V * (math.cos(h * t0) - math.cos(h * t1)) / h
    return math.hypot(an, bn) / math.pi


def spwm_picior(ma, mf, defazaj=0.0, th=None, referinta=None):
    if th is None:
        th = esantioane_perioada(N)
    ref = ma * np.sin(th - defazaj) if referinta is None else referinta(th - defazaj)
    return np.where(ref > purtatoare(th, mf), VDC / 2, -VDC / 2)


def spwm_semipunte():
    titlu("PWM sinusoidal, semipunte (bipolar), ma = 0,8, mf = 21")
    ma, mf = 0.8, 21
    v = spwm_picior(ma, mf)
    a = armonici(v, 3 * mf)
    V1_fronturi = fourier_din_fronturi(ma, mf, 1)
    verifica("V1 = ma Vdc/2 (FFT pe eșantioane)", a[1], ma * VDC / 2, tol_rel=1e-4)
    verifica("V1 = ma Vdc/2 (Fourier exact din fronturi)", V1_fronturi, ma * VDC / 2,
             tol_rel=1e-6)
    x = math.pi * ma / 2
    verifica("V_mf = (2Vdc/pi) J0(pi ma/2) (FFT)", a[mf], 2 * VDC / math.pi * bessel_j(0, x),
             tol_rel=1e-3)
    verifica("V_mf = (2Vdc/pi) J0(pi ma/2) (fronturi)", fourier_din_fronturi(ma, mf, mf),
             2 * VDC / math.pi * bessel_j(0, x), tol_rel=1e-5)
    for h in [mf - 2, mf + 2]:
        verifica(f"V_{h} = (2Vdc/pi) J2(pi ma/2)", fourier_din_fronturi(ma, mf, h),
                 2 * VDC / math.pi * bessel_j(2, x), tol_rel=1e-4)
    for h, n in [(2 * mf - 1, 1), (2 * mf + 1, 1), (2 * mf - 3, 3), (2 * mf + 3, 3)]:
        verifica(f"V_{h} = (Vdc/pi) J{n}(pi ma)", fourier_din_fronturi(ma, mf, h),
                 VDC / math.pi * abs(bessel_j(n, 2 * x)), tol_rel=1e-3)
    joase = a[2:mf - 4]
    verifica_conditie("nu există armonici de ordin mic (2 ... mf-5)",
                      joase.max() < 1e-3 * a[1], f"max = {joase.max():.2e} V")
    verifica_conditie("mf impar => armonicile pare lipsesc",
                      max(a[2:3 * mf:2]) < 1e-3 * a[1])
    verifica_conditie("V1 nu depinde de mf (mf = 9, 15, 51)",
                      all(abs(fourier_din_fronturi(ma, m, 1) - ma * VDC / 2) < 1e-6 * VDC
                          for m in [9, 15, 51]))


def supramodulatie():
    titlu("Supramodulație (ma > 1): pierderea liniarității")
    mf = 21
    th = esantioane_perioada(N)
    limita = 4 / math.pi * VDC / 2
    for ma in [1.0, 1.5, 3.0, 20.0]:
        v = spwm_picior(ma, mf, th=th)
        V1 = armonici(v, 1)[1]
        print(f"  ma = {ma:5.1f}: V1 = {V1:7.2f} V,  ma*Vdc/2 = {ma * VDC / 2:7.1f} V, "
              f"limită (4/pi)Vdc/2 = {limita:.2f} V")
        if ma > 1:
            # V1 <= (4/pi)Vdc/2 este o teoremă (unda dreptunghiulară maximizează
            # fundamentala); toleranța 1e-6 acoperă doar eroarea de eșantionare.
            verifica_conditie(f"ma = {ma}: V1 < ma Vdc/2 și V1 <= (4/pi)Vdc/2",
                              V1 < ma * VDC / 2 and V1 <= limita * (1 + 1e-6))
    verifica("ma -> infinit: V1 -> (4/pi)Vdc/2 (undă dreptunghiulară)",
             armonici(spwm_picior(1000.0, mf, th=th), 1)[1], 4 / math.pi * VDC / 2,
             tol_rel=2e-3)


def punte_unipolara():
    titlu("Punte H: PWM bipolar vs. unipolar (ma = 0,8, mf = 20)")
    ma, mf = 0.8, 20
    th = esantioane_perioada(N)
    vA = spwm_picior(ma, mf, th=th)
    vB = spwm_picior(ma, mf, th=th, referinta=lambda x: -ma * np.sin(x))
    uni = vA - vB
    bip = 2 * vA
    au, ab = armonici(uni, 3 * mf), armonici(bip, 3 * mf)
    verifica("unipolar: V1 = ma Vdc", au[1], ma * VDC, tol_rel=1e-4)
    verifica("bipolar:  V1 = ma Vdc", ab[1], ma * VDC, tol_rel=1e-4)
    verifica_conditie("unipolar: armonicile din jurul lui mf dispar",
                      au[mf - 3:mf + 4].max() < 1e-3 * au[1],
                      f"max(V_{mf - 3}..V_{mf + 3}) = {au[mf - 3:mf + 4].max():.2e} V")
    print(f"  bipolar:  cea mai mare armonică {np.argmax(ab[2:]) + 2} "
          f"({ab[2:].max():.0f} V); unipolar: armonica {np.argmax(au[2:]) + 2} "
          f"({au[2:].max():.0f} V)")
    verifica_conditie("unipolar: primul grup de armonici apare la 2mf +/- 1",
                      np.argmax(au[2:]) + 2 in (2 * mf - 1, 2 * mf + 1))


def trifazat():
    titlu("Invertor trifazat (punte cu 6 comutatoare)")
    th = esantioane_perioada(N)
    ma, mf = 0.8, 21
    va = spwm_picior(ma, mf, th=th)
    vb = spwm_picior(ma, mf, 2 * np.pi / 3, th=th)
    vab = va - vb
    a = armonici(vab, 3 * mf)
    verifica("SPWM: V_LL1 (amplitudine) = (sqrt3/2) ma Vdc", a[1],
             math.sqrt(3) / 2 * ma * VDC, tol_rel=1e-4)
    verifica("SPWM: V_LL1 (efectivă) = 0,612 ma Vdc", a[1] / math.sqrt(2),
             math.sqrt(3) / (2 * math.sqrt(2)) * ma * VDC, tol_rel=1e-4)
    verifica_conditie("mf multiplu de 3 => armonica mf dispare din tensiunea de linie",
                      a[mf] < 1e-3 * a[1], f"V_LL,{mf} = {a[mf]:.2e} V "
                      f"(în tensiunea de fază: {armonici(va, mf)[mf]:.1f} V)")

    titlu("Injecția armonicii a 3-a (1/6): extinderea zonei liniare")
    g = esantioane_perioada(200001)
    vmax = np.max(np.sin(g) + np.sin(3 * g) / 6)
    verifica("max(sin x + sin 3x / 6) = sqrt(3)/2", vmax, math.sqrt(3) / 2, tol_rel=1e-8)
    ma = 1.15  # < 2/sqrt(3) = 1,1547
    ref = lambda x: ma * (np.sin(x) + np.sin(3 * x) / 6)
    va = spwm_picior(ma, mf, th=th, referinta=ref)
    vb = spwm_picior(ma, mf, 2 * np.pi / 3, th=th, referinta=ref)
    V1_inj = armonici(va - vb, 1)[1]
    verifica("cu injecție, ma = 1,15: V_LL1 = (sqrt3/2) ma Vdc (încă liniar)", V1_inj,
             math.sqrt(3) / 2 * ma * VDC, tol_rel=1e-4)
    va = spwm_picior(ma, mf, th=th)
    vb = spwm_picior(ma, mf, 2 * np.pi / 3, th=th)
    V1_fara = armonici(va - vb, 1)[1]
    verifica_conditie("fără injecție, ma = 1,15: supramodulație, V_LL1 mai mic",
                      V1_fara < 0.995 * math.sqrt(3) / 2 * ma * VDC,
                      f"{V1_fara:.1f} V < {math.sqrt(3) / 2 * ma * VDC:.1f} V")

    titlu("Comandă în șase trepte (six-step)")
    va = np.where(th < np.pi, VDC / 2, -VDC / 2)
    vb = np.where(((th - 2 * np.pi / 3) % (2 * np.pi)) < np.pi, VDC / 2, -VDC / 2)
    a = armonici(va - vb, 13)
    verifica("V_LL1 (efectivă) = (sqrt6/pi) Vdc = 0,78 Vdc", a[1] / math.sqrt(2),
             math.sqrt(6) / math.pi * VDC, tol_rel=1e-4)
    verifica_conditie("tensiunea de linie nu conține armonici multiplu de 3",
                      max(a[[3, 6, 9, 12]]) < 1e-3 * a[1])
    for h in [5, 7, 11, 13]:
        verifica(f"V_LL{h} = V_LL1/{h}", a[h], a[1] / h, tol_rel=1e-3)


def main():
    unda_dreptunghiulara()
    spwm_semipunte()
    supramodulatie()
    punte_unipolara()
    trifazat()


if __name__ == "__main__":
    main()
