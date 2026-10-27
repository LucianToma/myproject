"""Modelele de calcul ale capitolului 7 (automatizări de rețea), folosite de
probleme_cap07.py și figuri_cap07.py.

Schema de studiu (figura 7.1): generatorul G1 (modelul clasic: t.e.m. E' constantă
în spatele reactanței tranzitorii x'd) – transformatorul bloc TB – bara C – linia
dublă de 110 kV (două circuite identice) – sistemul (bară de putere infinită în
spatele reactanței x_s). Toate mărimile sunt în unități relative pe baza Sn(G1) = 50 MVA,
cu tensiunea de bază 115 kV pe partea de înaltă tensiune a lui TB.
"""

import numpy as np
from scipy.integrate import solve_ivp
from modele import GEN, MOTOR, F0, W0

# --- date ale schemei de studiu (date de problemă) --------------------------------
SB = GEN["Sn"]
UB_IT = GEN["UT2"]
ZB_IT = UB_IT**2 / SB
X_LINIE_KM = 0.40           # reactanța pe kilometru a unui circuit de 110 kV [Ω/km] (ca în rețeaua de referință)
L_LINIE = 80.0              # lungimea liniei duble C–sistem [km]
XD_T = GEN["xd_t"]
XT = GEN["ukT"] * SB / GEN["ST"]
XL = X_LINIE_KM * L_LINIE / ZB_IT      # un circuit
XS = 0.05                   # reactanța sistemului (≈ S"k = 1000 MVA la 50 MVA bază)
H = GEN["H"]
P0 = GEN["cosphi"]          # puterea activă la sarcina nominală: P = Sn·cos φ = 0,85 u.r.
UT = 1.0                    # tensiunea la bornele generatorului
V_INF = 1.0                 # tensiunea barei de putere infinită


def x_retea(circuite=2):
    """Reactanța dintre bornele lui G1 și bara de putere infinită (fără x'd)."""
    return XT + XL / circuite + XS


def punct_functionare():
    """Punctul de funcționare inițial: P = P0, |Ut| = |V∞| = 1.
    Întoarce E' (fazor, cu V∞ pe axa reală), δ0, curentul și puterea reactivă."""
    xe = x_retea(2)
    theta_t = np.arcsin(P0 * xe / (UT * V_INF))
    Ut = UT * np.exp(1j * theta_t)
    I = (Ut - V_INF) / (1j * xe)
    E = Ut + 1j * XD_T * I
    Q = (Ut * np.conj(I)).imag
    return dict(E=E, delta0=np.angle(E), I=I, Q=Q, Ut=Ut, theta_t=theta_t)


def pmax(circuite):
    """Puterea maximă transmisibilă în regimul cu `circuite` circuite în funcțiune
    (0 = defect trifazat lângă bara C, deci Pe = 0)."""
    if circuite == 0:
        return 0.0
    E = abs(punct_functionare()["E"])
    return E * V_INF / (XD_T + x_retea(circuite))


def simuleaza(etape, delta0, Pm=P0, H=H, t_final=3.0, max_step=1e-3):
    """Integrează ecuația mișcării (2H/ω0)·d²δ/dt² = Pm − Pmax_k·sin δ pe etape succesive.
    etape: listă de (durata [s], Pmax_k); ultima etapă durează până la t_final.
    Întoarce t, δ [rad], Δω [rad/s] și starea la începutul fiecărei etape."""
    y = np.array([delta0, 0.0])
    t0 = 0.0
    T, D, Wd, start = [], [], [], []
    for k, (durata, Pmax_k) in enumerate(etape):
        t1 = t_final if k == len(etape) - 1 else t0 + durata
        start.append((t0, y[0], y[1], Pmax_k))

        def f(t, s, Pmax_k=Pmax_k):
            return [s[1], W0 / (2 * H) * (Pm - Pmax_k * np.sin(s[0]))]

        # oprire dacă rotorul a ieșit din sincronism (δ > 180° și crește)
        def iesire(t, s):
            return s[0] - np.pi * 1.5
        iesire.terminal = True
        sol = solve_ivp(f, (t0, t1), y, max_step=max_step, rtol=1e-10, atol=1e-12, events=iesire,
                        dense_output=False)
        T.append(sol.t)
        D.append(sol.y[0])
        Wd.append(sol.y[1])
        y = sol.y[:, -1]
        t0 = sol.t[-1]
        if sol.status == 1:
            break
    return np.concatenate(T), np.concatenate(D), np.concatenate(Wd), start


def stabil(delta):
    """Stabil dacă unghiul rămâne sub 180° pe toată durata simulării."""
    return bool(np.max(delta) < np.pi)


def potential(delta, Pmax_k, Pm=P0):
    """Energia potențială a etapei k: V(δ) = −Pm·δ − Pmax_k·cos δ (diferențele ei sunt arii
    de sub caracteristicile P–δ: V(δ2) − V(δ1) = ∫(Pmax_k sin δ − Pm)dδ)."""
    return -Pm * delta - Pmax_k * np.cos(delta)


def delta_max_arii(delta_s, dw_s, Pmax_f, Pm=P0, H=H):
    """Calea de verificare (criteriul ariilor, scris ca bilanț de energie) pentru ultima etapă.
    Energia totală W = (H/ω0)·Δω² + V(δ) se conservă; rotorul se oprește (Δω = 0) acolo unde
    V(δmax) = W. Mișcarea este stabilă dacă W < V(δu), δu = π − arcsin(Pm/Pmax_f) fiind
    unghiul de echilibru instabil (aria de frânare disponibilă nu este depășită).
    Întoarce δmax sau None (instabil)."""
    from scipy.optimize import brentq
    W = H / W0 * dw_s**2 + potential(delta_s, Pmax_f, Pm)
    de = np.arcsin(Pm / Pmax_f)
    du = np.pi - de
    if W >= potential(du, Pmax_f, Pm):
        return None
    return brentq(lambda d: potential(d, Pmax_f, Pm) - W, de, du)


def energie(delta, dw, Pmax_k, Pm=P0, H=H):
    """Funcția de energie conservată pe o etapă: (H/ω0)·Δω² − Pm·δ − Pmax_k·cos δ."""
    return H / W0 * dw**2 - Pm * delta - Pmax_k * np.cos(delta)


# --- AAR: tensiunea remanentă a barei de motoare --------------------------------------
S_MOT = 5.0e6       # puterea aparentă nominală totală a motoarelor de pe bară [VA] (date de problemă)
P_SARC = 0.70       # puterea mecanică cerută la turația nominală, în u.r. din S_MOT
T0_REM = 0.60       # constanta de timp a scăderii fluxului motoarelor după deconectare [s]
H_MOT = MOTOR["H"]  # constanta de inerție a grupului de motoare [s]


def remanenta_analitic(t, p=P_SARC, Hm=H_MOT, T0=T0_REM, f0=F0):
    """Cuplul rezistent ∝ ω² (pompe, ventilatoare): ω(t) = 1/(1 + p·t/(2H));
    tensiunea remanentă U = ω·e^{−t/T0}; unghiul față de sursa de rezervă
    θ(t) = 2π f0 [t − (2H/p)·ln(1 + p·t/(2H))]."""
    w = 1.0 / (1.0 + p * t / (2 * Hm))
    U = w * np.exp(-t / T0)
    theta = 2 * np.pi * f0 * (t - 2 * Hm / p * np.log(1 + p * t / (2 * Hm)))
    return w, U, theta


def remanenta_ode(t_eval, p=P_SARC, Hm=H_MOT, T0=T0_REM, f0=F0):
    """Calea de verificare: integrarea numerică a ecuațiilor 2H·dω/dt = −p·ω²,
    dψ/dt = −ψ/T0, dθ/dt = 2π f0 (1 − ω); U = ω·ψ."""
    def f(t, s):
        w, psi, th = s
        return [-p * w**2 / (2 * Hm), -psi / T0, 2 * np.pi * f0 * (1 - w)]
    sol = solve_ivp(f, (0, t_eval[-1]), [1.0, 1.0, 0.0], t_eval=t_eval, rtol=1e-10, atol=1e-12)
    w, psi, th = sol.y
    return w, w * psi, th


def diferenta_tensiune(U, theta):
    """|ΔU| = |1 − U·e^{−jθ}| (tensiunea de rezervă 1∠0, tensiunea remanentă rămasă în urmă)."""
    return np.abs(1 - U * np.exp(-1j * theta))
