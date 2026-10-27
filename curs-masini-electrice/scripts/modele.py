"""Modele de calcul comune pentru curs (transformator, mașina asincronă, mașina sincronă).

Toate mărimile sunt în SI. Fazorii sunt numere complexe cu valori efective.
Funcțiile sunt scrise cât mai aproape de formulele din curs, ca să poată fi
urmărite pas cu pas de un student.
"""

import numpy as np

SQRT3 = np.sqrt(3.0)
G = 9.81  # m/s^2


def fmt(x, n=2):
    """Formatează un număr cu virgulă zecimală (convenția românească)."""
    return f"{x:.{n}f}".replace(".", ",")


def verifica(nume, a, b, rtol=1e-3, atol=0.0):
    """Verifică faptul că două căi de calcul dau același rezultat."""
    ok = np.isclose(a, b, rtol=rtol, atol=atol)
    stare = "OK" if ok else "EROARE"
    print(f"  [verificare {stare}] {nume}: {a:.6g} vs {b:.6g}")
    assert ok, f"Verificarea '{nume}' a eșuat: {a} != {b}"


def polar(z, n=2):
    return f"{fmt(abs(z), n)} ∠ {fmt(np.degrees(np.angle(z)), n)}°"


# ---------------------------------------------------------------------------
# Transformator
# ---------------------------------------------------------------------------

def parametri_gol(U0, I0, P0):
    """Parametrii ramurii de magnetizare din încercarea de mers în gol."""
    cos_phi0 = P0 / (U0 * I0)
    sin_phi0 = np.sqrt(1 - cos_phi0**2)
    Ia = I0 * cos_phi0          # componenta activă (pierderi în fier)
    Imu = I0 * sin_phi0         # componenta de magnetizare
    return dict(cos_phi0=cos_phi0, Ia=Ia, Imu=Imu, RFe=U0 / Ia, Xm=U0 / Imu)


def parametri_scurtcircuit(Usc, Isc, Psc):
    """Parametrii longitudinali din încercarea de scurtcircuit."""
    Zsc = Usc / Isc
    Rsc = Psc / Isc**2
    Xsc = np.sqrt(Zsc**2 - Rsc**2)
    return dict(Zsc=Zsc, Rsc=Rsc, Xsc=Xsc, cos_phisc=Psc / (Usc * Isc))


def tensiune_secundar_exacta(U1, I2r, cos_phi2, Rsc, Xsc, inductiv=True):
    """Tensiunea secundară raportată U2' pentru schema simplificată (fără ramura
    de magnetizare), când primarul e alimentat la U1 și sarcina absoarbe I2'.

    Ecuația fazorială: U1 = U2' + (Rsc + jXsc) I2', cu U2' pe axa reală.
    """
    sin_phi2 = np.sqrt(1 - cos_phi2**2) * (1 if inductiv else -1)
    a = I2r * (Rsc * cos_phi2 + Xsc * sin_phi2)
    b = I2r * (Xsc * cos_phi2 - Rsc * sin_phi2)
    return np.sqrt(U1**2 - b**2) - a


def cadere_tensiune_aprox(beta, uR, uX, cos_phi2, inductiv=True):
    """ΔU% ≈ β (uR cos φ2 + uX sin φ2)  (uR, uX în %)."""
    sin_phi2 = np.sqrt(1 - cos_phi2**2) * (1 if inductiv else -1)
    return beta * (uR * cos_phi2 + uX * sin_phi2)


def randament_transformator(beta, Sn, cos_phi2, P0, Psc_n):
    P2 = beta * Sn * cos_phi2
    return P2 / (P2 + P0 + beta**2 * Psc_n)


# ---------------------------------------------------------------------------
# Mașina asincronă (schema echivalentă în T, pe fază, conexiune stea)
# ---------------------------------------------------------------------------

class MotorAsincron:
    """Schema echivalentă în T, cu ramura de magnetizare doar reactivă (Xm).

    Pierderile în fier și cele mecanice sunt grupate în P0 ("pierderi
    constante"), determinate din încercarea de mers în gol.

    Opțional, `colivie_dubla = (X2c, Ra, Xa, Rb, Xb)` înlocuiește rotorul cu
    o colivie dublă (reactanța comună X2c în serie cu două ramuri paralele
    Ra/s + jXa și Rb/s + jXb) – modelul simplu al efectului de refulare.
    """

    def __init__(self, U_linie, f, p, R1, X1, R2, X2, Xm, P0, colivie_dubla=None):
        self.U = U_linie / SQRT3   # tensiunea de fază (stea echivalentă)
        self.f, self.p = f, p
        self.R1, self.X1, self.R2, self.X2, self.Xm, self.P0 = R1, X1, R2, X2, Xm, P0
        self.colivie_dubla = colivie_dubla
        self.n1 = 60 * f / p
        self.W1 = 2 * np.pi * f / p    # viteza unghiulară de sincronism

    def la_frecventa(self, f, U_linie):
        """Aceeași mașină alimentată la altă frecvență: reactanțele ∝ f."""
        k = f / self.f
        cd = None
        if self.colivie_dubla is not None:
            X2c, Ra, Xa, Rb, Xb = self.colivie_dubla
            cd = (X2c * k, Ra, Xa * k, Rb, Xb * k)
        return MotorAsincron(U_linie, f, self.p, self.R1, self.X1 * k, self.R2,
                             self.X2 * k, self.Xm * k, self.P0, cd)

    def impedanta_rotor(self, s):
        if self.colivie_dubla is None:
            return self.R2 / s + 1j * self.X2
        X2c, Ra, Xa, Rb, Xb = self.colivie_dubla
        Za, Zb = Ra / s + 1j * Xa, Rb / s + 1j * Xb
        return 1j * X2c + Za * Zb / (Za + Zb)

    def punct(self, s):
        Z1 = self.R1 + 1j * self.X1
        Z2 = self.impedanta_rotor(s)
        Zm = 1j * self.Xm
        Z = Z1 + Z2 * Zm / (Z2 + Zm)
        I1 = self.U / Z
        E = self.U - I1 * Z1
        I2 = E / Z2
        P1 = 3 * (self.U * np.conj(I1)).real
        Q1 = 3 * (self.U * np.conj(I1)).imag
        PCu1 = 3 * abs(I1) ** 2 * self.R1
        Pd = 3 * (E * np.conj(I2)).real             # puterea electromagnetică (= 3 I2'² R2'/s)
        PCu2 = s * Pd
        Pmi = (1 - s) * Pd                         # puterea mecanică internă
        Me = Pd / self.W1                          # cuplul electromagnetic
        W = (1 - s) * self.W1
        P2 = Pmi - self.P0
        return dict(s=s, n=(1 - s) * self.n1, W=W, Z=Z, I1=I1, I2=I2, E=E,
                    P1=P1, Q1=Q1, PCu1=PCu1, Pd=Pd, PCu2=PCu2, Pmi=Pmi,
                    Me=Me, P2=P2, M2=P2 / W if W > 0 else np.nan,
                    eta=P2 / P1, cos_phi=P1 / (3 * self.U * abs(I1)))

    def cuplu(self, s):
        return self.punct(s)["Me"]

    def cuplu_maxim(self):
        from scipy.optimize import minimize_scalar
        s_grid = np.linspace(1e-3, 1.0, 400)
        s0 = s_grid[np.argmax([self.cuplu(x) for x in s_grid])]
        r = minimize_scalar(lambda s: -self.cuplu(s), bounds=(max(1e-4, s0 - 0.01), min(1.0, s0 + 0.01)),
                            method="bounded", options=dict(xatol=1e-10))
        return r.x, -r.fun


# Motorul de referință M15 (15 kW, 400 V Δ, 50 Hz, 2p = 4) – parametrii stelei echivalente.
# Modelul cu colivie simplă reproduce punctul nominal și cuplul maxim; modelul cu
# colivie dublă reproduce în plus cuplul și curentul de pornire din catalog.
M15_PARAMETRI = dict(U_linie=400, f=50, p=2, R1=0.25, X1=0.60, R2=0.20, X2=0.75, Xm=19.0, P0=330.0)
M15_COLIVIE_DUBLA = (0.23, 0.51, 0.21, 0.33, 1.39)


def motor_M15(colivie_dubla=False):
    return MotorAsincron(**M15_PARAMETRI, colivie_dubla=M15_COLIVIE_DUBLA if colivie_dubla else None)


def kloss(s, Mmax, sk):
    """Formula lui Kloss: M = 2 Mmax / (s/sk + sk/s)."""
    return 2 * Mmax / (s / sk + sk / s)


def sk_din_catalog(sn, lam):
    """Alunecarea critică din alunecarea nominală și capacitatea de supraîncărcare λ."""
    return sn * (lam + np.sqrt(lam**2 - 1))


# ---------------------------------------------------------------------------
# Mașina sincronă cu poli înecați, nesaturată, R neglijat (mărimi pe fază)
# ---------------------------------------------------------------------------

def generator_E0(U, I, phi, Xs, R=0.0):
    """Generator: E0 = U + (R + jXs) I, cu U pe axa reală; φ>0 = sarcină inductivă."""
    Iz = I * np.exp(-1j * phi)
    return U + (R + 1j * Xs) * Iz, Iz


def motor_E0(U, I, phi, Xs):
    """Motor (convenția de receptor): E0 = U - jXs I; φ>0 = curent defazat înainte
    (capacitiv, motor supraexcitat), φ<0 = curent defazat în urmă (subexcitat)."""
    Iz = I * np.exp(1j * phi)
    return U - 1j * Xs * Iz, Iz
