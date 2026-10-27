"""Modelele capitolului 8 – reglajul automat al frecvenței și al tensiunii.

Funcțiile sunt folosite atât de probleme_cap08.py (rezolvare și verificare),
cât și de figuri_cap08.py (figuri), ca figurile să arate exact rezultatele verificate.

Convenții pentru modelul de frecvență (sistem agregat, „o singură bară”):
  M·dΔf/dt = ΔPm − ΔP_dezechilibru − D·Δf,   M = 2·H·S/f0  [MW·s/Hz]
puterile sunt în MW, abaterea de frecvență Δf în Hz, D în MW/Hz.
"""

import numpy as np
from scipy.integrate import solve_ivp
from scipy import signal

F0 = 50.0


def M_inertie(H, S, f0=F0):
    """Coeficientul de inerție M = 2·H·S/f0 [MW·s/Hz] (H în s, S în MW)."""
    return 2 * H * S / f0


def K_statism(Pn, s, f0=F0):
    """Panta regulatorului de viteză: ΔP = −(Pn/(s·f0))·Δf [MW/Hz], statismul s în u.r."""
    return Pn / (s * f0)


# ---------------------------------------------------------------------------
# Sistem izolat: inerție + regulatoare de viteză (două constante de timp) + sarcină
# ---------------------------------------------------------------------------

def izolat_ode(dP, M, D, K, Tg, Tt, t_end, cu_regulator=True, n=4001):
    """Calea 1: integrarea numerică a ecuațiilor de stare (solve_ivp, RK45).
    Stări: Δf [Hz], x – ieșirea regulatorului [MW], ΔPm – puterea turbinei [MW]."""
    Kr = K if cu_regulator else 0.0

    def f(t, y):
        df, x, Pm = y
        return [(Pm - dP - D * df) / M, (-Kr * df - x) / Tg, (x - Pm) / Tt]

    t = np.linspace(0, t_end, n)
    sol = solve_ivp(f, (0, t_end), [0.0, 0.0, 0.0], t_eval=t, rtol=1e-10, atol=1e-12, method="RK45")
    return t, sol.y[0], sol.y[2]


def izolat_lti(dP, M, D, K, Tg, Tt, t, cu_regulator=True):
    """Calea 2: funcția de transfer Δf(s)/ΔP(s) = −(1+sTg)(1+sTt) / [(Ms + D)(1+sTg)(1+sTt) + K],
    răspunsul la treaptă calculat cu scipy.signal (altă metodă numerică decât solve_ivp)."""
    Kr = K if cu_regulator else 0.0
    num = -np.polymul([Tg, 1], [Tt, 1])
    den = np.polyadd(np.polymul([M, D], np.polymul([Tg, 1], [Tt, 1])), [Kr])
    _, y = signal.step(signal.lti(num, den), T=t)
    return dP * y


def nadir(t, df):
    k = int(np.argmin(df))
    return t[k], df[k]


# ---------------------------------------------------------------------------
# Incidentul de referință în Europa continentală: FCR cu limită de viteză
# ---------------------------------------------------------------------------

def ce_simulare(dP, M, D, lam, P_fcr_max, viteza, t_end, dt=1e-3):
    """Simulare cu pas fix (RK4 pentru Δf; puterea FCR urmează ținta min(λ·|Δf|, Pmax)
    cu viteza de creștere limitată la `viteza` [MW/s]). Întoarce t, Δf, P_FCR."""
    N = int(round(t_end / dt)) + 1
    t = np.arange(N) * dt
    df = np.zeros(N)
    P = np.zeros(N)
    for k in range(N - 1):
        tinta = min(lam * max(-df[k], 0.0), P_fcr_max)
        dPk = np.clip(tinta - P[k], -viteza * dt, viteza * dt)
        Pk, Pn = P[k], P[k] + dPk
        Pm = 0.5 * (Pk + Pn)

        def g(x, p):
            return (p - dP - D * x) / M

        x = df[k]
        k1 = g(x, Pk)
        k2 = g(x + dt / 2 * k1, Pm)
        k3 = g(x + dt / 2 * k2, Pm)
        k4 = g(x + dt * k3, Pn)
        df[k + 1] = x + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        P[k + 1] = Pn
    return t, df, P


def ce_nadir_analitic(dP, M, D, viteza):
    """Faza în care FCR crește cu viteza maximă r: M·dΔf/dt = −ΔP + r·t − D·Δf.
    Soluția: Δf(t) = A·(1 − e^{−at}) + B·t, cu a = D/M, B = r/D, A = −ΔP/D − r·M/D².
    Minimul (nadirul) este la dΔf/dt = 0: e^{−a·t*} = −B/(A·a)."""
    a = D / M
    B = viteza / D
    A = -dP / D - viteza * M / D**2
    t_star = -np.log(-B / (A * a)) / a
    return t_star, A * (1 - np.exp(-a * t_star)) + B * t_star


# ---------------------------------------------------------------------------
# Insulă cu deficit mare de putere și descărcare automată a sarcinii (DASF)
# ---------------------------------------------------------------------------

def dasf_simulare(dP, M, D, K, Tg, Tt, rezerva, trepte, t_intarziere, t_end, dt=1e-3, f0=F0):
    """Simulare cu pas fix (RK4) a insulei. trepte: listă de (frecvența de pornire [Hz], MW deconectați).
    O treaptă pornește când f scade sub prag și deconectează sarcina după t_intarziere
    (releu + întrerupător). Puterea suplimentară a turbinelor este limitată la `rezerva`.
    Întoarce t, f, ΔPm, puterea deconectată cumulată, lista momentelor de deconectare."""
    N = int(round(t_end / dt)) + 1
    t = np.arange(N) * dt
    y = np.zeros(3)          # Δf, x, ΔPm
    f = np.full(N, f0)
    Pm = np.zeros(N)
    desc = np.zeros(N)
    pornite = [None] * len(trepte)
    actionari = []
    shed = 0.0

    def deriv(y, shed):
        df, x, P = y
        x_tinta = min(-K * df, rezerva)        # limita de rezervă a regulatoarelor
        return np.array([(P - dP + shed - D * df) / M, (x_tinta - x) / Tg, (x - P) / Tt])

    for k in range(N - 1):
        fk = f0 + y[0]
        for i, (fp, Pd) in enumerate(trepte):
            if pornite[i] is None and fk < fp:
                pornite[i] = t[k] + t_intarziere
        for i, (fp, Pd) in enumerate(trepte):
            if pornite[i] is not None and pornite[i] <= t[k] and i not in [a[0] for a in actionari]:
                shed += Pd
                actionari.append((i, t[k], fp, Pd))
        k1 = deriv(y, shed)
        k2 = deriv(y + dt / 2 * k1, shed)
        k3 = deriv(y + dt / 2 * k2, shed)
        k4 = deriv(y + dt * k3, shed)
        y = y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        f[k + 1] = f0 + y[0]
        Pm[k + 1] = y[2]
        desc[k + 1] = shed
    return t, f, Pm, desc, actionari


# ---------------------------------------------------------------------------
# Două zone interconectate cu reglaj secundar (ACE)
# ---------------------------------------------------------------------------

def doua_zone(z1, z2, Ps, dPL1, t_end, cu_secundar=True, n=6001):
    """Stări: Δf1, Δf2, ΔPtie12 (export din zona 1), x1, Pm1, x2, Pm2, c1, c2 (consemnele secundare).
    z = dict(M, D, K, Tg, Tt, B, Ki). Ps – puterea sincronizantă a liniei de interconexiune [MW/rad]."""
    T = 2 * np.pi * Ps

    def f(t, y):
        f1, f2, Pt, x1, P1, x2, P2, c1, c2 = y
        ace1 = Pt + z1["B"] * f1
        ace2 = -Pt + z2["B"] * f2
        Ki1 = z1["Ki"] if cu_secundar else 0.0
        Ki2 = z2["Ki"] if cu_secundar else 0.0
        return [
            (P1 - dPL1 - Pt - z1["D"] * f1) / z1["M"],
            (P2 + Pt - z2["D"] * f2) / z2["M"],
            T * (f1 - f2),
            (c1 - z1["K"] * f1 - x1) / z1["Tg"],
            (x1 - P1) / z1["Tt"],
            (c2 - z2["K"] * f2 - x2) / z2["Tg"],
            (x2 - P2) / z2["Tt"],
            -Ki1 * ace1,
            -Ki2 * ace2,
        ]

    t = np.linspace(0, t_end, n)
    sol = solve_ivp(f, (0, t_end), np.zeros(9), t_eval=t, rtol=1e-9, atol=1e-9, method="LSODA")
    return t, sol.y, f


def jacobian_numeric(f, n, eps=1e-6):
    J = np.zeros((n, n))
    y0 = np.zeros(n)
    f0 = np.array(f(0, y0))
    for j in range(n):
        y = y0.copy()
        y[j] = eps
        J[:, j] = (np.array(f(0, y)) - f0) / eps
    return J


# ---------------------------------------------------------------------------
# Transformatorul cu reglaj sub sarcină (ANSI 90)
# ---------------------------------------------------------------------------

def tensiune_secundar(E, P, Q, R, X):
    """Tensiunea de linie U2 la bornele unei sarcini de putere constantă P + jQ (trifazat, W și var),
    alimentată de t.e.m. E (de linie) prin impedanța R + jX pe fază:
    U2⁴ − (E² − 2(RP + XQ))·U2² + (R² + X²)(P² + Q²) = 0 (soluția stabilă, cea mai mare)."""
    b = E**2 - 2 * (R * P + X * Q)
    return np.sqrt((b + np.sqrt(b**2 - 4 * (R**2 + X**2) * (P**2 + Q**2))) / 2)


def tensiune_secundar_iterativ(E, P, Q, R, X, n_iter=200):
    """Calea de verificare: iterații pe ecuația fazorială pe fază U = E − Z·conj(S/(3U)) (U de fază)."""
    Ef = E / np.sqrt(3)
    U = Ef + 0j
    Z = R + 1j * X
    for _ in range(n_iter):
        I = np.conj((P + 1j * Q) / (3 * U))
        U = Ef - Z * I
    return abs(U) * np.sqrt(3)


def regulator_ploturi(t, U_IT, P, Q, R, X, U_ref, banda, T_int, pas, n0=0, n_min=-8, n_max=8,
                      raport0=110.0 / 20.0, Zc=0j, Zl=0j):
    """Simularea regulatorului automat de ploturi (pas de timp constant).
    U_IT – tensiunea pe partea de 110 kV [V] (vector); P, Q – sarcina [W, var] (vectori).
    Raportul de transformare la poziția n este raport0·(1 + pas·n): ploturile sunt pe partea IT,
    deci o poziție n mai mare dă o tensiune secundară mai mică.
    R, X – impedanța transformatorului raportată la JT [Ω]; Zl – impedanța dintre bara de 20 kV și
    centrul de sarcină (unde este concentrată sarcina); Zc – impedanța compensării căderii de
    tensiune (LDC). Regulatorul compară Ureg = |U_bară − √3·Zc·I| cu U_ref ± banda și comută un plot
    dacă abaterea persistă T_int secunde (temporizatorul se resetează când tensiunea revine în bandă).
    Întoarce U_bară, U_sarcină, Ureg, poziția plotului și numărul de comutări."""
    dt = t[1] - t[0]
    n = n0
    timer = 0.0
    N = len(t)
    U_bara, U_sarc, Ureg = np.zeros(N), np.zeros(N), np.zeros(N)
    pozitie = np.zeros(N, int)
    comutari = 0
    for k in range(N):
        E = U_IT[k] / (raport0 * (1 + pas * n))
        U_sarc[k] = tensiune_secundar(E, P[k], Q[k], R + Zl.real, X + Zl.imag)
        I = np.conj((P[k] + 1j * Q[k]) / (np.sqrt(3) * U_sarc[k]))     # curentul de fază (U_sarc pe axa reală)
        Ub = U_sarc[k] + np.sqrt(3) * Zl * I
        U_bara[k] = abs(Ub)
        Ureg[k] = abs(Ub - np.sqrt(3) * Zc * I)
        pozitie[k] = n
        abatere = Ureg[k] - U_ref
        if abs(abatere) > banda:
            timer += dt
            if timer >= T_int:
                n_nou = n + (1 if abatere > 0 else -1)
                if n_min <= n_nou <= n_max:
                    n = n_nou
                    comutari += 1
                timer = 0.0
        else:
            timer = 0.0
    return U_bara, U_sarc, Ureg, pozitie, comutari


# ---------------------------------------------------------------------------
# Regulatorul automat de tensiune al generatorului (în gol)
# ---------------------------------------------------------------------------

def rat_ode(KA, TA, Td0, dUref, t_end, n=4001):
    """Generator în gol: Td0'·dE/dt = Efd − E; excitație statică: TA·dEfd/dt = KA·(Uref − E) − Efd.
    Mărimi în abateri (u.r.), treaptă dUref la t = 0. Întoarce t, ΔU (= ΔE), ΔEfd."""
    def f(t, y):
        E, Efd = y
        return [(Efd - E) / Td0, (KA * (dUref - E) - Efd) / TA]

    t = np.linspace(0, t_end, n)
    sol = solve_ivp(f, (0, t_end), [0.0, 0.0], t_eval=t, rtol=1e-10, atol=1e-12)
    return t, sol.y[0], sol.y[1]


def rat_lti(KA, TA, Td0, dUref, t):
    """Calea 2: funcția de transfer în buclă închisă KA / [(1 + sTA)(1 + sTd0') + KA]."""
    den = np.polyadd(np.polymul([TA, 1], [Td0, 1]), [KA])
    _, y = signal.step(signal.lti([KA], den), T=t)
    return dUref * y


def rat_analitic(KA, TA, Td0):
    """Parametrii sistemului de ordinul 2: ωn, ζ, eroarea staționară, suprareglarea, timpul de vârf."""
    wn = np.sqrt((1 + KA) / (TA * Td0))
    zeta = (TA + Td0) / (2 * np.sqrt(TA * Td0 * (1 + KA)))
    eroare = 1 / (1 + KA)
    supra = np.exp(-np.pi * zeta / np.sqrt(1 - zeta**2)) if zeta < 1 else 0.0
    tp = np.pi / (wn * np.sqrt(1 - zeta**2)) if zeta < 1 else np.inf
    return wn, zeta, eroare, supra, tp
