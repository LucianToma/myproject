"""Calcule comune pentru capitolul 6 – Protecția generatoarelor și a motoarelor."""

import numpy as np
from modele import SQRT3, W0, GEN, MOTOR

# ---------------------------------------------------------------------------
# Motorul M1
# ---------------------------------------------------------------------------
M = MOTOR
IN_M = M["Pn"] / (SQRT3 * M["Un"] * M["eta"] * M["cosphi"])   # curentul nominal [A]
K_TERMIC = 1.05          # reglaj: curentul admis permanent = 1,05·IB
IB_M = IN_M              # curentul de bază al modelului termic = curentul nominal al motorului


def termic_rk4(I_de_t, tau, IB, k, theta0=0.0, dt=0.01, tmax=4000.0):
    """Integrează τ·dθ/dt = (I(t)/(k·IB))² − θ cu Runge–Kutta 4 și întoarce (t_declanșare, t, θ).
    I_de_t: funcție de timp (curentul efectiv). Declanșare la θ = 1 (interpolare liniară în ultimul pas)."""
    def f(t, th):
        return ((I_de_t(t) / (k * IB))**2 - th) / tau
    t, th = 0.0, theta0
    ts, ths = [0.0], [theta0]
    while t < tmax:
        k1 = f(t, th)
        k2 = f(t + dt / 2, th + dt / 2 * k1)
        k3 = f(t + dt / 2, th + dt / 2 * k2)
        k4 = f(t + dt, th + dt * k3)
        th_nou = th + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        if th_nou >= 1.0 > th:
            tt = t + dt * (1.0 - th) / (th_nou - th)
            ts.append(tt)
            ths.append(1.0)
            return tt, np.array(ts), np.array(ths)
        t += dt
        th = th_nou
        ts.append(t)
        ths.append(th)
    return np.inf, np.array(ts), np.array(ths)


# ---------------------------------------------------------------------------
# Generatorul G1
# ---------------------------------------------------------------------------
G = GEN
IN_G = G["Sn"] / (SQRT3 * G["Un"])
ZB_G = G["Un"]**2 / G["Sn"]
TC_G, TT_G = 3000 / 1, 10.5e3 / 100      # TC 3000/1 A, TT 10,5/0,1 kV
K_SEC_G = TC_G / TT_G                     # Zsec = Zprim·nTC/nTT


def cerc_pierdere_excitatie(xd=G["xd"], xd_t=G["xd_t"]):
    """Caracteristica mho cu decalaj: diametrul pe axa −jX, de la −j·x'd/2 la −j(x'd/2 + xd) [u.r.]."""
    sus = -1j * xd_t / 2
    jos = -1j * (xd_t / 2 + xd)
    return sus, jos, (sus + jos) / 2, xd / 2


def in_cerc_geometric(Z, sus, jos):
    c, r = (sus + jos) / 2, abs(sus - jos) / 2
    return abs(Z - c) <= r


def in_cerc_comparator(Z, sus, jos):
    """Comparatorul de fază: punctul este în cerc dacă unghiul dintre (Z − sus) și (Z − jos) este ≥ 90°
    (teorema lui Thales), adică Re[(Z − sus)·conj(Z − jos)] ≤ 0."""
    return np.real((Z - sus) * np.conj(Z - jos)) <= 0


def impedanta_borne(E, delta, xd, xe, V=1.0):
    """Generator cu poli înecați (t.e.m. E în spatele lui xd) legat la o rețea de putere infinită
    prin reactanța externă xe. Întoarce Z = Ub/I la bornele generatorului (I ieșind din generator)."""
    I = (E * np.exp(1j * delta) - V) / (1j * (xd + xe))
    Ub = V + 1j * xe * I
    return Ub / I, Ub, I


def tensiune_neutru(x, Rf, RN, C, Ef):
    """Tensiunea neutrului generatorului la o punere la pământ pe faza a, la fracțiunea x din înfășurare
    (măsurată de la neutru), prin rezistența Rf; neutrul legat la pământ prin RN, capacitatea C pe fază
    concentrată la borne. Formula obținută din teorema lui Kirchhoff pentru curenți (vezi § 6.8)."""
    Y = 1 / RN + 3j * W0 * C + 1 / Rf
    return -(x * Ef / Rf) / Y


def tensiune_neutru_mna(x, Rf, RN, C, Ef):
    """Aceeași mărime prin analiza nodală modificată: noduri N, A, B, C (borne) și P (punctul de defect),
    cu surse de tensiune ideale între noduri. Necunoscute: potențialele și curenții surselor."""
    a = np.exp(2j * np.pi / 3)
    E = [Ef, Ef * a**2, Ef * a]
    # noduri: 0 = N, 1 = A, 2 = B, 3 = C, 4 = P;  surse: N→P (x·Ea), P→A ((1−x)·Ea), N→B, N→C
    n_nod, surse = 5, [(0, 4, x * E[0]), (4, 1, (1 - x) * E[0]), (0, 2, E[1]), (0, 3, E[2])]
    n = n_nod + len(surse)
    Mx = np.zeros((n, n), complex)
    b = np.zeros(n, complex)
    Mx[0, 0] += 1 / RN
    for k in (1, 2, 3):
        Mx[k, k] += 1j * W0 * C
    Mx[4, 4] += 1 / Rf
    for s, (p, q, e) in enumerate(surse):
        js = n_nod + s
        # curentul sursei iese din nodul q (borna +) și intră în nodul p
        Mx[p, js] += 1
        Mx[q, js] -= 1
        Mx[js, q] = 1
        Mx[js, p] = -1
        b[js] = e
    v = np.linalg.solve(Mx, b)
    return v[0]
