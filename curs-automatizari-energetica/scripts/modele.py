"""Modele de calcul comune pentru cursul de automatizări în energetică.

Toate mărimile sunt în SI (V, A, Ω, s), cu excepția locurilor în care se
spune altfel. Fazorii sunt numere complexe cu valori efective.

Rețeaua se poate rezolva pe două căi independente:
  * în componente simetrice (rețelele de secvență directă, inversă și
    homopolară, cu matricea impedanțelor nodale Zbus) – calea „de manual”;
  * direct în coordonate de fază (fiecare bară are trei noduri a, b, c;
    transformatoarele sunt modelate ca trei unități monofazate conectate
    fizic în stea sau în triunghi) – calea de verificare.
Cele două căi au în comun numai datele de intrare.
"""

import numpy as np

SQRT3 = np.sqrt(3.0)
F0 = 50.0                      # frecvența nominală [Hz]
W0 = 2 * np.pi * F0            # pulsația nominală [rad/s]
a_op = np.exp(2j * np.pi / 3)  # operatorul a = 1∠120°

# Matricea transformării în componente simetrice: V_abc = A · [V0, V1, V2]
A = np.array([[1, 1, 1], [1, a_op**2, a_op], [1, a_op, a_op**2]])
A_INV = np.linalg.inv(A)

# IEC 60909-0: factorul de tensiune c pentru rețele cu Un > 1 kV
C_MAX, C_MIN = 1.10, 1.00


# ---------------------------------------------------------------------------
# Utilitare
# ---------------------------------------------------------------------------

def fmt(x, n=2):
    """Formatează un număr cu virgulă zecimală (convenția românească)."""
    return f"{x:.{n}f}".replace(".", ",")


def verifica(nume, a, b, rtol=1e-3, atol=0.0):
    """Verifică faptul că două căi de calcul dau același rezultat."""
    ok = np.allclose(a, b, rtol=rtol, atol=atol)
    stare = "OK" if ok else "EROARE"
    if np.ndim(a) == 0 and np.ndim(b) == 0:
        print(f"  [verificare {stare}] {nume}: {complex(a) if np.iscomplexobj(a) else a:.6g} vs "
              f"{complex(b) if np.iscomplexobj(b) else b:.6g}")
    else:
        print(f"  [verificare {stare}] {nume}")
    assert ok, f"Verificarea '{nume}' a eșuat: {a} != {b}"


def verifica_adevarat(nume, conditie):
    """Verifică o condiție logică (de exemplu o inegalitate cerută de reglaj)."""
    stare = "OK" if conditie else "EROARE"
    print(f"  [verificare {stare}] {nume}")
    assert conditie, f"Verificarea '{nume}' a eșuat"


def polar(z, n=2):
    return f"{fmt(abs(z), n)} ∠ {fmt(np.degrees(np.angle(z)), n)}°"


def seq_la_faza(Z0, Z1, Z2=None):
    """Matricea 3×3 în coordonate de fază pentru un element simetric."""
    Z2 = Z1 if Z2 is None else Z2
    return A @ np.diag([Z0, Z1, Z2]) @ A_INV


def faza_la_seq(v_abc):
    return A_INV @ np.asarray(v_abc)


def sistem_direct(V):
    """Tensiunile de fază ale unui sistem direct (succesiunea a, b, c)."""
    return V * np.array([1, a_op**2, a_op])


# ---------------------------------------------------------------------------
# IEC 60909-0: factori de corecție și curentul de șoc
# ---------------------------------------------------------------------------

def kappa(R, X):
    """Factorul κ pentru curentul de șoc ip = κ·√2·I"k (IEC 60909-0)."""
    return 1.02 + 0.98 * np.exp(-3 * R / X)


def K_T(xT, cmax=C_MAX):
    """Factorul de corecție al impedanței transformatoarelor de rețea (IEC 60909-0)."""
    return 0.95 * cmax / (1 + 0.6 * xT)


# ---------------------------------------------------------------------------
# Rețeaua: date comune și cele două căi de rezolvare
# ---------------------------------------------------------------------------

class Retea:
    """Rețea trifazată descrisă prin elemente. Impedanțele sunt în Ω, pe
    nivelul de tensiune al elementului; capacitățile în F (pe toată lungimea)."""

    def __init__(self, f=F0):
        self.f = f
        self.w = 2 * np.pi * f
        self.bare = {}          # nume -> Un [V]
        self.elemente = []

    # --- descrierea rețelei ------------------------------------------------
    def bara(self, nume, Un):
        self.bare[nume] = Un

    def sursa(self, nume, bara, Z1, Z0, E=None):
        """Sursă echivalentă (rețea de alimentare): t.e.m. de fază E în spatele
        impedanțelor de secvență Z1 (= Z2) și Z0. Implicit E = c_max·Un/√3."""
        if E is None:
            E = C_MAX * self.bare[bara] / SQRT3
        self.elemente.append(dict(tip="sursa", nume=nume, bara=bara, Z1=Z1, Z0=Z0, E=E))

    def linie(self, nume, b1, b2, Z1, Z0, C1=0.0, C0=0.0):
        self.elemente.append(dict(tip="linie", nume=nume, b1=b1, b2=b2, Z1=Z1, Z0=Z0, C1=C1, C0=C0))

    def transformator(self, nume, bIT, bJT, Sn, UIT, UJT, uk, Pk=0.0, conexiune="YNd11", Zn=0.0):
        """Transformator cu două înfășurări. Impedanța de scurtcircuit este
        raportată la partea de înaltă tensiune: Zt = uk·UIT²/Sn, Rt = Pk·UIT²/Sn².
        conexiune: 'YNd11', 'YNd1', 'Dyn11', 'Dyn1' (prima literă: înfășurarea IT).
        Zn: impedanța dintre neutrul înfășurării în stea și pământ (None = neutru izolat)."""
        Zt_mod = uk * UIT**2 / Sn
        Rt = Pk * UIT**2 / Sn**2
        Zt = Rt + 1j * np.sqrt(Zt_mod**2 - Rt**2)
        ora = int(conexiune[3:]) if conexiune.startswith("YN") else int(conexiune[3:])
        self.elemente.append(dict(tip="trafo", nume=nume, b1=bIT, b2=bJT, Zt=Zt, U1=UIT, U2=UJT,
                                  conexiune=conexiune[:3], ora=ora, Zn=Zn, Sn=Sn))

    def bobina_neutru(self, nume, bara, Z0):
        """Element care închide numai calea homopolară (bobină de formare a
        neutrului, eventual cu rezistor sau bobină de stingere în neutru).
        Z0 este impedanța homopolară totală pe fază (inclusiv 3·Z_neutru)."""
        self.elemente.append(dict(tip="neutru", nume=nume, bara=bara, Z0=Z0))

    def capacitate(self, nume, bara, C1, C0):
        """Capacitate concentrată față de pământ (de exemplu cablurile rețelei)."""
        self.elemente.append(dict(tip="cap", nume=nume, bara=bara, C1=C1, C0=C0))

    def element(self, nume):
        for e in self.elemente:
            if e["nume"] == nume:
                return e
        raise KeyError(nume)

    # --- calea 1: componente simetrice --------------------------------------
    def _raport(self, e, s):
        """Raportul complex a (V_IT = a·V_JT) pentru secvența s (1 sau 2)."""
        r = (e["U1"] / e["U2"])
        unghi = np.radians(30 * e["ora"])
        return r * np.exp(1j * unghi) if s == 1 else r * np.exp(-1j * unghi)

    def ybus_secventa(self, s):
        nume = list(self.bare)
        idx = {b: i for i, b in enumerate(nume)}
        n = len(nume)
        Y = np.zeros((n, n), complex)
        J = np.zeros(n, complex)
        for e in self.elemente:
            t = e["tip"]
            if t == "sursa":
                Z = e["Z0"] if s == 0 else e["Z1"]
                i = idx[e["bara"]]
                Y[i, i] += 1 / Z
                if s == 1:
                    J[i] += e["E"] / Z
            elif t == "linie":
                Z = e["Z0"] if s == 0 else e["Z1"]
                C = e["C0"] if s == 0 else e["C1"]
                i, j = idx[e["b1"]], idx[e["b2"]]
                y = 1 / Z
                Y[i, i] += y + 1j * self.w * C / 2
                Y[j, j] += y + 1j * self.w * C / 2
                Y[i, j] -= y
                Y[j, i] -= y
            elif t == "trafo":
                i, j = idx[e["b1"]], idx[e["b2"]]
                if s == 0:
                    # numai înfășurarea YN conduce curent homopolar spre pământ
                    if e["Zn"] is None:
                        continue
                    if e["conexiune"] == "YNd":
                        Y[i, i] += 1 / (e["Zt"] + 3 * e["Zn"])
                    else:  # Dyn: impedanța raportată la JT
                        Y[j, j] += 1 / (e["Zt"] * (e["U2"] / e["U1"])**2 + 3 * e["Zn"])
                    continue
                y = 1 / e["Zt"]
                a = self._raport(e, s)
                Y[i, i] += y
                Y[i, j] += -y * a
                Y[j, i] += -y * np.conj(a)
                Y[j, j] += y * abs(a)**2
            elif t == "neutru":
                if s == 0:
                    i = idx[e["bara"]]
                    Y[i, i] += 1 / e["Z0"]
            elif t == "cap":
                i = idx[e["bara"]]
                Y[i, i] += 1j * self.w * (e["C0"] if s == 0 else e["C1"])
        return Y, J, idx

    def scurtcircuit_secvente(self, bara, tip="3f", Zf=0.0):
        """Defect la bara dată, calculat cu rețelele de secvență.
        tip: '3f' trifazat, '1f' faza a – pământ, '2f' fazele b–c, '2fp' fazele b–c – pământ.
        Întoarce un dicționar cu curenții de secvență la defect (ieșind din rețea),
        tensiunile de secvență la toate barele și impedanțele Thevenin."""
        Ys = {}
        Z = {}
        for s in (0, 1, 2):
            Y, J, idx = self.ybus_secventa(s)
            Ys[s] = (Y, J)
            if s == 0 and np.allclose(Y, 0):
                Z[s] = None
            else:
                Z[s] = np.linalg.inv(Y) if not (s == 0 and np.linalg.matrix_rank(Y) < len(Y)) else None
        k = idx[bara]
        V_pre1 = Z[1] @ Ys[1][1]
        Vf = V_pre1[k]
        Z1, Z2 = Z[1][k, k], Z[2][k, k]
        Z0 = Z[0][k, k] if Z[0] is not None else np.inf
        if tip == "3f":
            I1 = Vf / (Z1 + Zf)
            I = np.array([0, I1, 0])
        elif tip == "1f":
            I0 = Vf / (Z1 + Z2 + Z0 + 3 * Zf)
            I = np.array([I0, I0, I0])
        elif tip == "2f":
            I1 = Vf / (Z1 + Z2 + Zf)
            I = np.array([0, I1, -I1])
        elif tip == "2fp":
            Zp = Z2 * (Z0 + 3 * Zf) / (Z2 + Z0 + 3 * Zf)
            I1 = Vf / (Z1 + Zp)
            I2 = -I1 * (Z0 + 3 * Zf) / (Z2 + Z0 + 3 * Zf)
            I0 = -I1 * Z2 / (Z2 + Z0 + 3 * Zf)
            I = np.array([I0, I1, I2])
        else:
            raise ValueError(tip)
        V = {}
        for s in (0, 1, 2):
            pre = V_pre1 if s == 1 else np.zeros(len(idx), complex)
            V[s] = pre - (Z[s][:, k] * I[s] if Z[s] is not None else 0)
        return dict(I_seq=I, I_faza=A @ I, V_seq=V, idx=idx, Zth=(Z0, Z1, Z2), Vf=Vf, Zbus=Z)

    def curenti_ramura_secvente(self, rez, nume, capat=1):
        """Curenții de fază care intră în elementul `nume` la capătul dat (1 sau 2),
        calculați din tensiunile de secvență ale rezultatului `rez`."""
        e = self.element(nume)
        idx, V = rez["idx"], rez["V_seq"]
        Iseq = np.zeros(3, complex)
        for s in (0, 1, 2):
            if e["tip"] == "linie":
                Z = e["Z0"] if s == 0 else e["Z1"]
                C = e["C0"] if s == 0 else e["C1"]
                i, j = idx[e["b1"]], idx[e["b2"]]
                if capat == 2:
                    i, j = j, i
                Iseq[s] = (V[s][i] - V[s][j]) / Z + 1j * self.w * C / 2 * V[s][i]
            elif e["tip"] == "trafo":
                i, j = idx[e["b1"]], idx[e["b2"]]
                if s == 0:
                    if e["Zn"] is None:
                        continue
                    if e["conexiune"] == "YNd" and capat == 1:
                        Iseq[s] = V[s][i] / (e["Zt"] + 3 * e["Zn"])
                    elif e["conexiune"] == "Dyn" and capat == 2:
                        Iseq[s] = V[s][j] / (e["Zt"] * (e["U2"] / e["U1"])**2 + 3 * e["Zn"])
                    continue
                a = self._raport(e, s)
                I_IT = (V[s][i] - a * V[s][j]) / e["Zt"]
                Iseq[s] = I_IT if capat == 1 else -np.conj(a) * I_IT
            elif e["tip"] == "sursa":
                Z = e["Z0"] if s == 0 else e["Z1"]
                i = idx[e["bara"]]
                Es = e["E"] if s == 1 else 0
                Iseq[s] = (V[s][i] - Es) / Z      # curent care intră în sursă din bară
            elif e["tip"] == "neutru":
                if s == 0:
                    Iseq[s] = V[s][idx[e["bara"]]] / e["Z0"]
        return A @ Iseq

    # --- calea 2: coordonate de fază -----------------------------------------
    def _construieste_faze(self):
        noduri = {}
        for b in self.bare:
            for k, f in enumerate("abc"):
                noduri[(b, f)] = len(noduri)
        stampe = []   # (nume, lista de noduri globale (-1 = pământ), Y local, J local)

        def nod(b, k):
            return noduri[(b, "abc"[k])]

        for e in self.elemente:
            t = e["tip"]
            if t == "sursa":
                Zp = seq_la_faza(e["Z0"], e["Z1"])
                Yp = np.linalg.inv(Zp)
                n = [nod(e["bara"], k) for k in range(3)]
                J = Yp @ sistem_direct(e["E"])
                stampe.append((e["nume"], n, Yp, J))
            elif t == "linie":
                Yser = np.linalg.inv(seq_la_faza(e["Z0"], e["Z1"]))
                Ysh = seq_la_faza(1j * self.w * e["C0"] / 2, 1j * self.w * e["C1"] / 2)
                n = [nod(e["b1"], k) for k in range(3)] + [nod(e["b2"], k) for k in range(3)]
                Yl = np.block([[Yser + Ysh, -Yser], [-Yser, Yser + Ysh]])
                stampe.append((e["nume"], n, Yl, np.zeros(6, complex)))
            elif t == "trafo":
                # trei unități monofazate; noduri locale: IT a,b,c, JT a,b,c, neutru
                Zt = e["Zt"]
                conex, ora = e["conexiune"], e["ora"]
                if conex == "YNd":
                    UwIT, UwJT = e["U1"] / SQRT3, e["U2"]
                    Zw = Zt                     # impedanța înfășurării în stea (raportată la IT)
                else:
                    UwIT, UwJT = e["U1"], e["U2"] / SQRT3
                    Zw = 3 * Zt                 # înfășurarea în triunghi, raportată la IT
                tr = UwIT / UwJT
                yw = 1 / Zw
                Yu = yw * np.array([[1, -tr], [-tr, tr**2]])   # [i_IT, i_JT] = Yu [v_IT, v_JT]
                loc = [nod(e["b1"], k) for k in range(3)] + [nod(e["b2"], k) for k in range(3)]
                # nodul neutrului înfășurării în stea
                if e["Zn"] is None or e["Zn"] != 0:
                    neutru = ("N", e["nume"])
                    noduri[neutru] = len(noduri)
                    loc.append(noduri[neutru])
                    if e["Zn"] is not None:
                        stampe.append((e["nume"] + "_Zn", [noduri[neutru]], np.array([[1 / e["Zn"]]]),
                                       np.zeros(1, complex)))
                    iN = 6
                else:
                    iN = -1                      # neutru legat direct la pământ
                nl = len(loc)
                Yt = np.zeros((nl, nl), complex)
                for k in range(3):
                    # înfășurarea în stea: între faza k și neutru; în triunghi: între două faze
                    if conex == "YNd":
                        pIT, qIT = k, iN
                        pJT, qJT = (3 + k, 3 + (k + 2) % 3) if ora == 11 else (3 + k, 3 + (k + 1) % 3)
                    else:
                        pIT, qIT = (k, (k + 1) % 3) if ora == 11 else (k, (k + 2) % 3)
                        pJT, qJT = 3 + k, iN
                    inc = np.zeros((2, nl))
                    for r, (p, q) in enumerate(((pIT, qIT), (pJT, qJT))):
                        if p >= 0:
                            inc[r, p] += 1
                        if q >= 0:
                            inc[r, q] -= 1
                    Yt += inc.T @ Yu @ inc
                stampe.append((e["nume"], loc, Yt, np.zeros(nl, complex)))
            elif t == "neutru":
                Yp = np.ones((3, 3)) / (3 * e["Z0"])
                stampe.append((e["nume"], [nod(e["bara"], k) for k in range(3)], Yp, np.zeros(3, complex)))
            elif t == "cap":
                Yp = seq_la_faza(1j * self.w * e["C0"], 1j * self.w * e["C1"])
                stampe.append((e["nume"], [nod(e["bara"], k) for k in range(3)], Yp, np.zeros(3, complex)))
        return noduri, stampe

    def rezolva_faze(self, defecte=()):
        """Rezolvă rețeaua în coordonate de fază.
        defecte: listă de (bara, faza1, faza2_sau_None, R) – admitanță 1/R între
        faza1 și faza2 (sau pământ, dacă faza2 este None)."""
        noduri, stampe = self._construieste_faze()
        n = len(noduri)
        Y = np.zeros((n, n), complex)
        J = np.zeros(n, complex)
        for _, loc, Yl, Jl in stampe:
            for r, gr in enumerate(loc):
                if gr < 0:
                    continue
                J[gr] += Jl[r]
                for c, gc in enumerate(loc):
                    if gc >= 0:
                        Y[gr, gc] += Yl[r, c]
        Yd = []
        for (b, f1, f2, R) in defecte:
            g = 1 / R
            i = noduri[(b, f1)]
            Y[i, i] += g
            if f2 is not None:
                j = noduri[(b, f2)]
                Y[j, j] += g
                Y[i, j] -= g
                Y[j, i] -= g
            Yd.append((i, None if f2 is None else noduri[(b, f2)], g))
        V = np.linalg.solve(Y, J)
        return dict(V=V, noduri=noduri, stampe=stampe, defecte=Yd)

    def tensiuni_faze(self, rez, bara):
        return np.array([rez["V"][rez["noduri"][(bara, f)]] for f in "abc"])

    def curenti_ramura_faze(self, rez, nume, capat=1):
        """Curenții de fază care intră în elementul `nume` la capătul dat."""
        for nm, loc, Yl, Jl in rez["stampe"]:
            if nm == nume:
                Vloc = np.array([rez["V"][g] if g >= 0 else 0 for g in loc])
                I = Yl @ Vloc - Jl
                return I[0:3] if capat == 1 else I[3:6]
        raise KeyError(nume)

    def curent_defect_faze(self, rez):
        """Curentul prin fiecare admitanță de defect (de la faza1 spre faza2/pământ)."""
        V = rez["V"]
        return [(V[i] - (V[j] if j is not None else 0)) * g for i, j, g in rez["defecte"]]


R_BOLTED = 1e-4   # rezistența folosită în calea de fază pentru un defect metalic [Ω]


def defect_faze(bara, tip, Rf=0.0):
    """Traduce tipul de defect în lista de admitanțe pentru calea de fază."""
    R = max(Rf, R_BOLTED)
    if tip == "3f":
        return [(bara, "a", None, R_BOLTED), (bara, "b", None, R_BOLTED), (bara, "c", None, R_BOLTED)]
    if tip == "1f":
        return [(bara, "a", None, R)]
    if tip == "2f":
        return [(bara, "b", "c", R)]
    if tip == "2fp":
        return [(bara, "b", None, R_BOLTED), (bara, "c", None, R_BOLTED)]
    raise ValueError(tip)


# ---------------------------------------------------------------------------
# Rețeaua de referință a cursului
# ---------------------------------------------------------------------------

# Datele sunt construite pentru curs, cu valori în domeniile uzuale;
# nu reproduc o instalație reală.
DATE = dict(
    U110=110e3, U20=20e3,
    SkA=3000e6, SkC=1500e6, XR_sursa=10.0,          # puterile de scurtcircuit ale surselor echivalente
    z1_110=0.12 + 0.40j, z0_110=0.30 + 1.20j,       # LEA 110 kV [Ω/km]
    lL1=40.0, lL2=30.0,                             # lungimile liniilor L1 (A–B) și L2 (B–C) [km]
    ST=25e6, ukT=0.11, PkT=120e3,                   # transformatorul T1 110/20 kV, YNd11
    z1_cablu=0.164 + 0.12j, z0_cablu=0.66 + 0.40j, c_cablu=0.26e-6,   # cablu 20 kV, 185 mm² Al [Ω/km, F/km]
    z1_lea20=0.413 + 0.36j, z0_lea20=0.56 + 1.55j, c1_lea20=0.0095e-6, c0_lea20=0.005e-6,  # LEA 20 kV 70 mm²
    l_cablu_F1=3.0, l_lea_F1a=7.0, l_lea_F1b=8.0,  # fiderul F1: B2–P1 = 3 km cablu + 7 km LEA; P1–P2 = 8 km LEA
    l_cablu_rest=37.0, l_lea_rest=60.0,             # restul rețelei de 20 kV alimentate din B2 (pentru capacități)
    IN_rezistor=300.0,                              # curentul limitat de rezistorul de neutru [A]
)


# Generatorul G1 al centralei hidroelectrice racordate la bara C (capitolele 6, 7 și 8).
# Contribuția lui la curenții de scurtcircuit din capitolul 1 este inclusă în sursa echivalentă QC.
GEN = dict(
    Sn=50e6, Un=10.5e3, cosphi=0.85,            # 50 MVA, 10,5 kV
    xd=1.00, xq=0.65, xd_t=0.30, xd_s=0.20, x2=0.22,   # reactanțe în u.r. (baza Sn, Un)
    Td0_t=5.0,                                  # constanta de timp tranzitorie în gol [s]
    H=3.5,                                      # constanta de inerție [s] (baza Sn)
    P_motor=0.015,                              # puterea absorbită în regim de motor, din catalog [u.r. din Pn]
    I2_cont=0.08, K2=20.0,                      # curentul invers admis permanent [u.r.] și (I2/In)²·t admis [s]
    ST=50e6, UT1=10.5e3, UT2=115e3, ukT=0.12,   # transformatorul bloc TB, YNd11
)

# Motorul asincron M1 de 6 kV (capitolele 6 și 7)
MOTOR = dict(
    Pn=800e3, Un=6e3, eta=0.955, cosphi=0.87,
    Ip_In=6.0,                # curentul de pornire raportat la cel nominal
    t_pornire=6.0,            # durata pornirii cu mașina de lucru cuplată [s]
    t_blocat_cald=12.0,       # timpul admis cu rotorul blocat, pornind din regim cald [s]
    t_blocat_rece=18.0,       # idem, pornind din stare rece [s]
    tau=1800.0,               # constanta de timp termică la încălzire [s]
    H=0.6,                    # constanta de inerție a grupului motor + mașină de lucru [s]
)


def impedanta_sursa(Sk, Un, XR=10.0, c=C_MAX):
    """Impedanța sursei echivalente: |Z| = c·Un²/S"k, cu raportul X/R dat."""
    Zm = c * Un**2 / Sk
    R = Zm / np.sqrt(1 + XR**2)
    return R + 1j * XR * R


def RN_rezistor(Un, I_lim):
    """Rezistența de neutru care limitează curentul de punere la pământ la I_lim
    (neglijând celelalte impedanțe): I = Uf / RN."""
    return Un / SQRT3 / I_lim


def retea_referinta(neutru20="rezistor", c=C_MAX, cu_capacitati=True, Zn_bobina=None, kR20=1.0, KT=1.0):
    """Construiește rețeaua de referință (figura 0.x din curs).

    neutru20: 'rezistor' (rezistor în neutrul bobinei de formare a neutrului),
              'izolat' sau 'bobina' (bobină de stingere; Zn_bobina = reactanța ei pe fază, în Ω).
    c: factorul de tensiune folosit pentru t.e.m. surselor (c_max sau c_min).
    kR20: multiplicator pentru rezistențele liniilor de 20 kV (încălzirea conductoarelor).
    KT: factorul de corecție aplicat impedanței transformatorului T1 (IEC 60909-0).
    """
    d = DATE
    r = Retea()
    r.bara("A", d["U110"])
    r.bara("B", d["U110"])
    r.bara("C", d["U110"])
    r.bara("B2", d["U20"])
    r.bara("P1", d["U20"])
    r.bara("P2", d["U20"])
    ZA = impedanta_sursa(d["SkA"], d["U110"], d["XR_sursa"])
    ZC = impedanta_sursa(d["SkC"], d["U110"], d["XR_sursa"])
    E = c * d["U110"] / SQRT3
    r.sursa("QA", "A", ZA, ZA, E=E)
    r.sursa("QC", "C", ZC, ZC, E=E)
    r.linie("L1", "A", "B", d["z1_110"] * d["lL1"], d["z0_110"] * d["lL1"])
    r.linie("L2", "B", "C", d["z1_110"] * d["lL2"], d["z0_110"] * d["lL2"])
    r.transformator("T1", "B", "B2", d["ST"], d["U110"], d["U20"], d["ukT"] * KT, d["PkT"] * KT, "YNd11", Zn=0.0)
    # fiderul F1, cu capacitățile tronsoanelor
    lc, la, lb = d["l_cablu_F1"], d["l_lea_F1a"], d["l_lea_F1b"]
    def kR(z):
        return kR20 * z.real + 1j * z.imag
    Z1a = kR(d["z1_cablu"]) * lc + kR(d["z1_lea20"]) * la
    Z0a = kR(d["z0_cablu"]) * lc + kR(d["z0_lea20"]) * la
    C1a = (d["c_cablu"] * lc + d["c1_lea20"] * la) if cu_capacitati else 0.0
    C0a = (d["c_cablu"] * lc + d["c0_lea20"] * la) if cu_capacitati else 0.0
    r.linie("F1a", "B2", "P1", Z1a, Z0a, C1a, C0a)
    r.linie("F1b", "P1", "P2", kR(d["z1_lea20"]) * lb, kR(d["z0_lea20"]) * lb,
            d["c1_lea20"] * lb if cu_capacitati else 0.0, d["c0_lea20"] * lb if cu_capacitati else 0.0)
    if cu_capacitati:
        r.capacitate("Crest", "B2", d["c_cablu"] * d["l_cablu_rest"] + d["c1_lea20"] * d["l_lea_rest"],
                     d["c_cablu"] * d["l_cablu_rest"] + d["c0_lea20"] * d["l_lea_rest"])
    if neutru20 == "rezistor":
        RN = RN_rezistor(d["U20"], d["IN_rezistor"])
        r.bobina_neutru("BPN", "B2", 3 * RN + 0j)
    elif neutru20 == "bobina":
        r.bobina_neutru("BPN", "B2", 3j * Zn_bobina)
    elif neutru20 != "izolat":
        raise ValueError(neutru20)
    return r


# ---------------------------------------------------------------------------
# Protecția maximală de curent: caracteristicile IEC 60255-151
# ---------------------------------------------------------------------------

CURBE = {
    # nume: (k, alfa, c)  –  t = TMS·[k/((I/Is)^alfa − 1) + c]
    "SI": (0.14, 0.02, 0.0),       # normal invers (Standard Inverse)
    "VI": (13.5, 1.0, 0.0),        # foarte invers
    "EI": (80.0, 2.0, 0.0),        # extrem de invers
    "MI-IEEE": (0.0515, 0.02, 0.114),
    "VI-IEEE": (19.61, 2.0, 0.491),
    "EI-IEEE": (28.2, 2.0, 0.1217),
}


def timp_invers(I, Is, TMS, curba="SI"):
    """Timpul de acționare al unei protecții maximale cu caracteristică dependentă."""
    k, alfa, c = CURBE[curba]
    G = np.asarray(I, float) / Is
    with np.errstate(divide="ignore", invalid="ignore"):
        t = TMS * (k / (G**alfa - 1) + c)
    return np.where(G > 1, t, np.inf)


def TMS_necesar(t, I, Is, curba="SI"):
    """Multiplicatorul de timp care dă timpul t la curentul I."""
    k, alfa, c = CURBE[curba]
    return t / (k / ((I / Is)**alfa - 1) + c)


def timp_integrator(i_t, dt, Is, TMS, curba="SI"):
    """Calea de verificare: releul numeric integrează 1/t(I) cât timp I > Is și
    declanșează când integrala ajunge la 1 (formularea „integrală” a timpului dependent).
    i_t: valorile efective ale curentului la fiecare pas dt. Întoarce timpul de declanșare."""
    acc = 0.0
    for n, I in enumerate(i_t):
        if I > Is:
            acc += dt / float(timp_invers(I, Is, TMS, curba))
            if acc >= 1.0:
                # interpolare liniară în ultimul pas
                exces = (acc - 1.0) / (dt / float(timp_invers(I, Is, TMS, curba)))
                return (n + 1 - exces) * dt
    return np.inf


# ---------------------------------------------------------------------------
# Modelul termic (IEC 60255-149) și modelul I2²t
# ---------------------------------------------------------------------------

def timp_termic(I, IB, k, tau, Ip=0.0):
    """t = τ·ln[(I² − Ip²)/(I² − (k·IB)²)] – timpul de declanșare al protecției
    termice cu memorie, pornind de la curentul anterior Ip (regim staționar)."""
    Ith = k * IB
    if I <= Ith:
        return np.inf
    return tau * np.log((I**2 - Ip**2) / (I**2 - Ith**2))


def timp_termic_ode(I, IB, k, tau, Ip=0.0, dt=1e-3, tmax=1e5):
    """Calea de verificare: integrează τ·dθ/dt + θ = (I/(k·IB))², cu θ(0) = (Ip/(k·IB))²,
    până la θ = 1 (metoda exactă pe pas pentru o ecuație liniară de ordinul întâi)."""
    th = (Ip / (k * IB))**2
    tinta = (I / (k * IB))**2
    t = 0.0
    q = np.exp(-dt / tau)
    while th < 1.0 and t < tmax:
        th_nou = tinta + (th - tinta) * q
        if th_nou >= 1.0:
            # fracțiunea de pas la care se atinge pragul
            frac = np.log((tinta - th) / (tinta - 1.0)) * tau
            return t + frac
        th = th_nou
        t += dt
    return np.inf


# ---------------------------------------------------------------------------
# Transformatorul de curent: fluxul în miez la un curent de scurtcircuit cu componentă aperiodică
# ---------------------------------------------------------------------------

def flux_tc(t, I_sec_ef, R2, T1, w=W0):
    """Fluxul înlănțuit [V·s] al miezului unui TC ideal (fără curent de magnetizare)
    pentru i2(t) = √2·I·(e^{−t/T1} − cos ωt) printr-o sarcină rezistivă totală R2:
    ψ(t) = R2·√2·I·[T1(1 − e^{−t/T1}) − sin(ωt)/ω]."""
    Im = np.sqrt(2) * I_sec_ef
    return R2 * Im * (T1 * (1 - np.exp(-t / T1)) - np.sin(w * t) / w)


def tc_neliniar(t, I_sec_ef, R2, T1, psi_sat, i_m_sat=0.05, raport_pante=2000, w=W0):
    """Curentul secundar al unui TC cu miez saturabil (model pentru figuri și verificare).
    Curba de magnetizare este liniară pe porțiuni: până la ψsat curentul de magnetizare
    crește liniar până la i_m_sat [A]; peste ψsat panta inductivității scade de `raport_pante` ori.
    Curentul primar (raportat la secundar) este √2·I·(e^{−t/T1} − cos ωt)."""
    Lm = psi_sat / i_m_sat
    L_sat = Lm / raport_pante

    def i_mag(psi):
        a = abs(psi)
        im = a / Lm if a <= psi_sat else psi_sat / Lm + (a - psi_sat) / L_sat
        return np.sign(psi) * im

    dt = t[1] - t[0]
    psi = 0.0
    i2 = np.empty_like(t)
    for n, tn in enumerate(t):
        i1 = np.sqrt(2) * I_sec_ef * (np.exp(-tn / T1) - np.cos(w * tn))
        # Euler implicit: ψ_nou = ψ + dt·R2·(i1 − im(ψ_nou)), rezolvat prin bisecție (funcție monotonă)
        lo, hi = psi - 1.0, psi + 1.0
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if mid - psi - dt * R2 * (i1 - i_mag(mid)) > 0:
                hi = mid
            else:
                lo = mid
        psi = 0.5 * (lo + hi)
        i2[n] = i1 - i_mag(psi)
    return i2


# ---------------------------------------------------------------------------
# Ecuația mișcării (stabilitate tranzitorie, criteriul ariilor egale)
# ---------------------------------------------------------------------------

def unghi_critic(delta0):
    """Unghiul critic de eliminare pentru un defect cu Pe = 0 pe durata defectului
    și aceeași caracteristică Pmax·sin δ înainte și după defect."""
    return np.arccos((np.pi - 2 * delta0) * np.sin(delta0) - np.cos(delta0))


def timp_critic(delta0, H, Pm, f=F0):
    """Timpul critic corespunzător (Pe = 0 în timpul defectului): δ crește parabolic."""
    dcr = unghi_critic(delta0)
    return np.sqrt(4 * H * (dcr - delta0) / (2 * np.pi * f * Pm))
