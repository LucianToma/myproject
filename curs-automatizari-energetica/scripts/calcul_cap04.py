"""Calcule comune pentru capitolul 4 – Protecția diferențială (folosite de probleme și de figuri)."""

import numpy as np
from modele import SQRT3, W0, DATE, A, A_INV

d = DATE
U1, U2, ST = d["U110"], d["U20"], d["ST"]
IN_IT = ST / (SQRT3 * U1)          # curentul nominal al lui T1 pe 110 kV
IN_JT = ST / (SQRT3 * U2)          # curentul nominal al lui T1 pe 20 kV
TC_IT, TC_JT = 150.0, 800.0        # rapoartele TC (secundar 1 A)

# Matricea de compensare a grupei YNd11, aplicată curenților părții în stea (110 kV):
# (IA − IB)/√3, (IB − IC)/√3, (IC − IA)/√3 – rotește sistemul direct cu +30°, sistemul invers cu −30°
# și elimină componenta homopolară.
M_YND11 = np.array([[1, -1, 0], [0, 1, -1], [-1, 0, 1]]) / SQRT3
I0_ELIM = np.eye(3) - np.ones((3, 3)) / 3      # I − I0 (eliminarea homopolarei fără rotire)

# Caracteristica cu frânare (date de reglaj ale cursului), în multipli ai curentului nominal al lui T1
IDIFF_MIN = 0.30      # pragul minim
K1, K2 = 0.30, 0.70   # pantele
IB2 = 3.0             # curentul de frânare la care începe panta a doua
IDIFF_NEFRANAT = 11.0  # treapta nefrânată (instantanee)
ARMONICA2 = 0.12      # pragul de blocare la armonica a doua (raport I2f/I1f), justificat în problema 4.4


def prag_diferential(Ib):
    """Curentul diferențial de acționare la curentul de frânare Ib (caracteristica cu două pante)."""
    Ib = np.asarray(Ib, float)
    p1 = np.maximum(IDIFF_MIN, K1 * Ib)
    p2 = K1 * IB2 + K2 * (Ib - IB2)
    return np.where(Ib <= IB2, p1, np.maximum(p1, p2))


def marimi_releu(I_IT, I_JT, elimina_I0=True, I0_pe_JT=False, raport_IT=TC_IT):
    """Curenții diferențiali și de frânare pe faze, în multipli ai curentului nominal al lui T1.

    I_IT, I_JT: curenții primari pe faze care INTRĂ în transformator (zona protejată) pe fiecare parte.
    elimina_I0: compensarea părții YN cu matricea M_YND11 (care elimină homopolara); altfel numai
                rotirea fazorilor (homopolara rămâne).
    I0_pe_JT: dacă se elimină și homopolara curenților de pe 20 kV.
    raport_IT: raportul TC de pe 110 kV (adaptarea se face pentru raportul nominal al transformatorului).
    """
    # secundar TC → multipli ai curentului nominal (adaptarea de amplitudine a releului)
    i_IT = np.asarray(I_IT) / raport_IT * (TC_IT / IN_IT)
    i_JT = np.asarray(I_JT) / TC_JT * (TC_JT / IN_JT)
    if elimina_I0:
        c_IT = M_YND11 @ i_IT
    else:
        # rotire cu +30° a sistemului direct și −30° a celui invers, homopolara păstrată
        s = A_INV @ i_IT
        c_IT = A @ np.array([s[0], s[1] * np.exp(1j * np.pi / 6), s[2] * np.exp(-1j * np.pi / 6)])
    c_JT = I0_ELIM @ i_JT if I0_pe_JT else i_JT
    Id = np.abs(c_IT + c_JT)
    Ib = (np.abs(c_IT) + np.abs(c_JT)) / 2
    return Id, Ib, c_IT, c_JT


# ---------------------------------------------------------------------------
# Curentul de magnetizare la conectare (model monofazat simplificat al unei faze a lui T1)
# ---------------------------------------------------------------------------

INRUSH = dict(
    Vm=np.sqrt(2) * U1 / SQRT3,      # amplitudinea tensiunii de fază [V]
    I0_proc=0.004,                   # curentul de mers în gol: 0,4 % din In (date de model)
    k_sat=1.20,                      # cotul de saturație la 1,2·ψn
    x_aer=0.30,                      # reactanța înfășurării de 110 kV cu miezul saturat [u.r., baza T1]
    R_inf=1.16,                      # rezistența înfășurării de 110 kV [Ω] (jumătate din Rk)
    R_retea=2.434, X_retea=10.314,   # impedanța rețelei la bara B (capitolul 1, problema 1.2) [Ω]
    psi_rem=0.8,                     # fluxul remanent [u.r. din ψn]
)


def parametri_inrush(p=INRUSH):
    psi_n = p["Vm"] / W0
    Zb = U1**2 / ST
    Lm = psi_n / (np.sqrt(2) * p["I0_proc"] * IN_IT)
    L_aer = p["x_aer"] * Zb / W0
    return psi_n, Lm, L_aer


def simuleaza_inrush(t_final=0.4, dt=2e-6, p=INRUSH, unghi=0.0):
    """Conectarea înfășurării de 110 kV (partea de 20 kV deschisă) la tensiunea Vm·sin(ωt + unghi).
    Ecuația: v = R·i + L_r·di/dt + dψ/dt, cu i = f(ψ) liniară pe porțiuni → dψ/dt = (v − R·i)/(1 + L_r·f'(ψ)).
    Integrare Runge–Kutta de ordinul 4 cu pas constant. Întoarce t, i, ψ."""
    psi_n, Lm, L_aer = parametri_inrush(p)
    psi_s = p["k_sat"] * psi_n
    R = p["R_inf"] + p["R_retea"]
    Lr = p["X_retea"] / W0

    def i_de_psi(psi):
        a = abs(psi)
        i = a / Lm if a <= psi_s else psi_s / Lm + (a - psi_s) / L_aer
        return np.copysign(i, psi)

    def panta(psi):
        return 1 / Lm if abs(psi) <= psi_s else 1 / L_aer

    def f(t, psi):
        v = p["Vm"] * np.sin(W0 * t + unghi)
        return (v - R * i_de_psi(psi)) / (1 + Lr * panta(psi))

    n = int(round(t_final / dt))
    t = np.arange(n + 1) * dt
    psi = np.empty(n + 1)
    psi[0] = p["psi_rem"] * psi_n
    for k in range(n):
        tk, y = t[k], psi[k]
        k1 = f(tk, y)
        k2 = f(tk + dt / 2, y + dt / 2 * k1)
        k3 = f(tk + dt / 2, y + dt / 2 * k2)
        k4 = f(tk + dt, y + dt * k3)
        psi[k + 1] = y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    i = np.array([i_de_psi(x) for x in psi])
    return t, i, psi


def armonici_dft(x, n_max=5):
    """Amplitudinile componentelor de frecvență k·f (k = 0…n_max) ale unei ferestre care conține
    exact o perioadă, calculate prin corelație directă (transformata Fourier discretă)."""
    N = len(x)
    th = 2 * np.pi * np.arange(N) / N
    rez = [np.mean(x)]
    for k in range(1, n_max + 1):
        rez.append(abs(2 / N * np.sum(x * np.exp(-1j * k * th))))
    return np.array(rez)


def sinus_trunchiat_analitic(alfa, n_max=5, Im=1.0):
    """Coeficienții Fourier (amplitudini) ai impulsului periodic i(θ) = Im(cos θ − cos α) pentru |θ| ≤ α,
    zero în rest (o dată pe perioadă) – forma idealizată a curentului de magnetizare la conectare."""
    rez = [Im / np.pi * (np.sin(alfa) - alfa * np.cos(alfa))]
    rez.append(Im / np.pi * (alfa - np.sin(2 * alfa) / 2))
    for n in range(2, n_max + 1):
        an = Im / np.pi * (np.sin((n - 1) * alfa) / (n - 1) + np.sin((n + 1) * alfa) / (n + 1)
                           - 2 * np.cos(alfa) * np.sin(n * alfa) / n)
        rez.append(abs(an))
    return np.array(rez)


def raport_armonica2_alunecator(t, i, f=50.0):
    """Raportul I(2f)/I(f) pe o fereastră alunecătoare de o perioadă (ca în releele numerice)."""
    dt = t[1] - t[0]
    N = int(round(1 / (f * dt)))
    pas = N // 20
    tt, r2, i1 = [], [], []
    for k in range(0, len(t) - N, pas):
        h = armonici_dft(i[k:k + N], 2)
        tt.append(t[k + N])
        i1.append(h[1])
        r2.append(h[2] / h[1] if h[1] > 0 else 0.0)
    return np.array(tt), np.array(r2), np.array(i1)
