"""Simulator exact (pe porțiuni liniare) pentru convertoarele buck, boost și
buck-boost, cu comutatoare ideale și diodă ideală.

Metoda (independentă de formulele din curs):
  * în fiecare topologie circuitul este liniar: dx/dt = A x + b, cu
    x = [i_L, v_C] (v_C = mărimea tensiunii de ieșire, pozitivă);
  * soluția pe un interval de durată h este exactă:
        [x(h); 1] = expm([[A, b], [0, 0]] * h) @ [x(0); 1];
  * pornim din repaus (x = 0) și simulăm perioadă cu perioadă până când
    starea de la începutul perioadei nu se mai schimbă (regim permanent);
  * dacă în intervalul OFF curentul prin bobină ajunge la zero, dioda se
    blochează (regim de conducție discontinuă, DCM); momentul anulării se
    găsește cu metoda Newton aplicată soluției exacte.

Nu se folosește nicio formulă de tip V_o = D*V_in: acestea sunt doar
comparate, ulterior, cu rezultatul simulării.
"""
import numpy as np

from comun import expm


class Topologie:
    def __init__(self, nume, A, b):
        self.nume = nume
        self.A = np.asarray(A, float)
        self.b = np.asarray(b, float)
        M = np.zeros((3, 3))
        M[:2, :2] = self.A
        M[:2, 2] = self.b
        self._M = M

    def derivata(self, x):
        return self.A @ x + self.b

    def harta(self, h):
        """Returnează (Phi, gamma) cu x(h) = Phi @ x(0) + gamma."""
        E = expm(self._M * h)
        return E[:2, :2], E[:2, 2]

    def propaga(self, x, h):
        Phi, g = self.harta(h)
        return Phi @ x + g


def topologii(tip, Vin, L, C, R, RL=0.0):
    """Ecuațiile de stare ale celor trei topologii (ON, OFF, DCM).

    RL este rezistența serie (opțională) a bobinei: v_L include -RL*i_L.
    """
    a = -1.0 / (R * C)
    r = -RL / L
    if tip == "buck":
        # ON: v_L = Vin - v_C ; OFF (dioda conduce): v_L = -v_C
        on = Topologie("on", [[r, -1 / L], [1 / C, a]], [Vin / L, 0])
        off = Topologie("off", [[r, -1 / L], [1 / C, a]], [0, 0])
    elif tip == "boost":
        # ON: v_L = Vin, C alimentează sarcina ; OFF: v_L = Vin - v_C
        on = Topologie("on", [[r, 0], [0, a]], [Vin / L, 0])
        off = Topologie("off", [[r, -1 / L], [1 / C, a]], [Vin / L, 0])
    elif tip == "buck-boost":
        # ON: v_L = Vin ; OFF: v_L = -v_C (ieșire inversată, |v_o| = v_C)
        on = Topologie("on", [[r, 0], [0, a]], [Vin / L, 0])
        off = Topologie("off", [[r, -1 / L], [1 / C, a]], [0, 0])
    else:
        raise ValueError(tip)
    # DCM: comutator și diodă blocate, i_L = 0, C se descarcă pe R
    dcm = Topologie("dcm", [[0, 0], [0, a]], [0, 0])
    return on, off, dcm


def curent_intrare(tip, topo, iL):
    """Curentul absorbit de la sursa Vin în topologia dată."""
    if tip == "boost":
        return iL if topo != "dcm" else 0.0 * iL
    return iL if topo == "on" else 0.0 * iL


def _anulare_curent(off, x0, durata):
    """Momentul tau din (0, durata) la care i_L se anulează în topologia OFF.

    i_L este monoton descrescător în OFF (v_L < 0 în regim permanent), deci
    rădăcina este unică. Newton protejat de un interval de încadrare.
    """
    stanga, dreapta = 0.0, durata
    panta = off.derivata(x0)[0]
    tau = min(max(-x0[0] / panta, 0.0), durata) if panta < 0 else durata / 2
    for _ in range(100):
        x = off.propaga(x0, tau)
        if x[0] > 0:
            stanga = tau
        else:
            dreapta = tau
        d = off.derivata(x)[0]
        nou = tau - x[0] / d if d < 0 else 0.5 * (stanga + dreapta)
        if not (stanga < nou < dreapta):
            nou = 0.5 * (stanga + dreapta)
        if abs(nou - tau) < 1e-18 + 1e-15 * durata:
            tau = nou
            break
        tau = nou
    return tau


def simuleaza(tip, Vin, D, L, C, R, fs, perioade_max=200000, tol=1e-12,
              puncte_perioada=4000, RL=0.0):
    """Simulează convertorul până la regim permanent.

    Returnează un dicționar cu segmentele ultimei perioade (pentru medii,
    valori efective și grafice) și informații despre convergență.
    """
    Ts = 1.0 / fs
    on, off, dcm = topologii(tip, Vin, L, C, R, RL)
    t_on, t_off = D * Ts, (1 - D) * Ts
    Phi_on, g_on = on.harta(t_on)
    Phi_off, g_off = off.harta(t_off)

    def o_perioada(x):
        x = Phi_on @ x + g_on
        x_cap = Phi_off @ x + g_off
        if x_cap[0] >= 0:
            return x_cap, None
        tau = _anulare_curent(off, x, t_off)
        xc = off.propaga(x, tau)
        xc[0] = 0.0
        x_fin = dcm.propaga(xc, t_off - tau)
        if tip == "boost" and x_fin[1] < Vin:
            raise RuntimeError("model DCM boost invalid: v_C < Vin")
        return x_fin, tau

    x = np.zeros(2)
    tau = None
    reziduu = np.inf
    for k in range(1, perioade_max + 1):
        x_nou, tau = o_perioada(x)
        reziduu = np.max(np.abs(x_nou - x)) / max(1e-30, np.max(np.abs(x_nou)))
        x = x_nou
        if reziduu < tol:
            break
    else:
        raise RuntimeError(f"nu s-a atins regimul permanent (reziduu {reziduu:.2e})")

    # Eșantionare fină a ultimei perioade, pe segmente cu topologie fixă.
    segmente = []
    intervale = [(on, 0.0, t_on)]
    if tau is None:
        intervale.append((off, t_on, Ts))
    else:
        intervale.append((off, t_on, t_on + tau))
        intervale.append((dcm, t_on + tau, Ts))
    xs = x.copy()
    for topo, t0, t1 in intervale:
        n = max(50, int(round(puncte_perioada * (t1 - t0) / Ts)))
        h = (t1 - t0) / n
        Phi, g = topo.harta(h)
        stari = np.empty((n + 1, 2))
        stari[0] = xs
        for i in range(n):
            stari[i + 1] = Phi @ stari[i] + g
        if topo.nume == "off" and tau is not None:
            stari[-1, 0] = 0.0
        segmente.append({"topo": topo.nume, "t": np.linspace(t0, t1, n + 1),
                         "x": stari, "topologie": topo, "L": L, "C": C})
        xs = stari[-1].copy()

    return {"tip": tip, "Vin": Vin, "D": D, "L": L, "C": C, "R": R, "fs": fs,
            "Ts": Ts, "perioade": k, "reziduu": reziduu, "segmente": segmente,
            "tau_dcm": tau}


# ---------------------------------------------------------------------------
# Post-procesare
# ---------------------------------------------------------------------------

def medie_perioada(rez, f):
    """Media pe perioadă a mărimii f(segment) -> vector de valori, calculată
    pe fiecare segment cu metoda trapezelor (discontinuitățile dintre
    segmente sunt tratate corect)."""
    total = 0.0
    for s in rez["segmente"]:
        total += np.trapezoid(f(s), s["t"])
    return total / rez["Ts"]


def iL(s):
    return s["x"][:, 0]


def vC(s):
    return s["x"][:, 1]


def vL(s):
    """Tensiunea pe bobină: L * di_L/dt din ecuația de stare."""
    topo = s["topologie"]
    return s["L"] * np.array([topo.derivata(x)[0] for x in s["x"]])


def iC(s):
    """Curentul prin condensator: C * dv_C/dt din ecuația de stare."""
    topo = s["topologie"]
    return s["C"] * np.array([topo.derivata(x)[1] for x in s["x"]])


def concateneaza(rez, f):
    t = np.concatenate([s["t"] for s in rez["segmente"]])
    y = np.concatenate([f(s) for s in rez["segmente"]])
    return t, y
