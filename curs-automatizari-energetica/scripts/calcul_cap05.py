"""Capitolul 5 – Protecția de distanță: modelele comune problemelor și figurilor.

Releul de distanță 21 este în stația A, pe linia L1 (A–B); releul din stația B
protejează linia L2 (B–C). TC 600/1 A, TT 110/0,1 kV.
"""

import numpy as np
from matplotlib.path import Path
from modele import SQRT3, C_MAX, DATE, retea_referinta, A as A_SIM

d = DATE
ZL1 = d["z1_110"] * d["lL1"]
Z0L1 = d["z0_110"] * d["lL1"]
ZL2 = d["z1_110"] * d["lL2"]
Z0L2 = d["z0_110"] * d["lL2"]
K0 = (Z0L1 - ZL1) / (3 * ZL1)        # factorul de compensare homopolară (același tip de linie pe L1 și L2)
FI_L = np.angle(ZL1)                                          # unghiul liniei [rad]
N_TC, N_TT = 600 / 1, 110e3 / 100
K_SEC = N_TC / N_TT                                           # Zsec = Zprim·nTC/nTT

# Bugetul de erori: datele liniei și releul – date de problemă; TT – clasa 3P (±3 %);
# TC – clasa 5P: singura garanție la curenții de defect este eroarea compusă de 5 % la ALF·In
ERORI = dict(linie=0.05, TT=0.03, TC=0.05, releu=0.05)


def factor_supraacoperire(e=ERORI):
    """Cât de mult poate „vedea” releul mai departe decât reglajul (cel mai defavorabil caz):
    impedanța reală a liniei mai mică, tensiunea măsurată mai mică, curentul măsurat mai mare,
    releul cu eroare în plus."""
    return (1 + e["TC"]) * (1 + e["releu"]) / ((1 - e["linie"]) * (1 - e["TT"]))


def factor_subacoperire(e=ERORI):
    return (1 + e["linie"]) * (1 + e["TT"]) / ((1 - e["TC"]) * (1 - e["releu"]))


# Reglajele zonelor releului din A (impedanțe primare, la unghiul liniei)
K1 = 0.82                    # zona 1: fracțiunea din ZL1 (≤ 1/f_sup = 0,836, problema 5.1)
K2 = 1.20                    # zona 2: fracțiunea din ZL1 (≥ f_sub = 1,198)
Z3_MOD = 41.5                # zona 3 [Ω primar]: rezultă din problema 5.1 (defect monofazat la capătul L2 cu sursa C
                             # deconectată, mărit de alimentarea homopolară prin neutrul lui T1, înmulțit cu f_sub)
T_ZONE = (0.0, 0.3, 0.6)     # temporizările zonelor [s] (date de problemă, treapta de 0,3 s din cap. 3)
Z_ZONE = (K1 * ZL1, K2 * ZL1, Z3_MOD * np.exp(1j * np.angle(ZL1)))
R_ZONE = (15.0, 20.0, 30.0)  # acoperirea rezistivă a poligoanelor (date de problemă) [Ω primar]
UNGHI_DIR = np.radians(-15.0)    # dreapta direcțională (cadranul IV) – dată de problemă
UNGHI_STG = np.radians(115.0)    # limita stângă (cadranul II) – dată de problemă

# Problema 5.3: unghiul maxim de transfer înainte de defect și rezistența de defect (date de problemă)
DELTA_MAX = 20.0             # [grade] – curentul de sarcină rămâne sub 600 A (problema 5.6)
RF_53 = 10.0                 # [Ω]
# Blocarea la pendulații (date de problemă): benzile paralele cu linia și temporizarea de detecție
R_BANDA_EXT, R_BANDA_INT, T_PSB = 45.0, 35.0, 0.030


# ---------------------------------------------------------------------------
# Caracteristici
# ---------------------------------------------------------------------------

def mho_interior(Z, Zr):
    """Cerc mho prin origine, cu diametrul Zr: |Z − Zr/2| ≤ |Zr|/2."""
    return abs(Z - Zr / 2) <= abs(Zr) / 2


def mho_comparator(Z, Zr):
    """A doua cale: comparatorul de fază – punctul e în interior dacă unghiul
    dintre (Zr − Z) și Z este cel mult 90° (în cerc, unghiul subîntins de diametru este 90°)."""
    if abs(Z) < 1e-12:
        return True
    return np.cos(np.angle((Zr - Z) / Z)) >= 0


def poligon(X, R, fi=FI_L, inclinare=0.0):
    """Vârfurile poligonului (caracteristica patrulateră) în planul R-X, ordine trigonometrică.
    X – acoperirea reactivă; R – acoperirea rezistivă (dreapta din dreapta, paralelă cu linia);
    inclinare – unghiul cu care latura de sus coboară spre dreapta [rad]."""
    # dreapta din dreapta: R0 + t·e^{jφ}; dreapta direcțională: s·e^{jθd}
    e_fi = np.exp(1j * fi)
    e_d = np.exp(1j * UNGHI_DIR)
    # intersecția R + t·e_fi = s·e_d
    M = np.array([[e_fi.real, -e_d.real], [e_fi.imag, -e_d.imag]])
    t, s = np.linalg.solve(M, [-R, 0.0])
    V2 = s * e_d
    # latura de sus: trece prin punctul liniei de la acoperirea X (Rp + jXp = X·cot φ + jX),
    # cu panta −tan(inclinare): Im z = Xp − (Re z − Rp)·tan(inclinare)
    Rp, Xp = X / np.tan(fi), X
    ta = np.tan(inclinare)
    t3 = (Xp - (R - Rp) * ta) / (np.sin(fi) + np.cos(fi) * ta)
    V3 = R + t3 * e_fi
    e_s = np.exp(1j * UNGHI_STG)
    s4 = (Xp + Rp * ta) / (e_s.imag + e_s.real * ta)
    V4 = s4 * e_s
    return np.array([0 + 0j, V2, V3, V4])


def poligon_interior(Z, V):
    """Calea 1: poligon convex – punctul e la stânga fiecărei laturi orientate."""
    if not np.isfinite(Z):
        return False
    for k in range(len(V)):
        a, b = V[k], V[(k + 1) % len(V)]
        cross = (b - a).real * (Z - a).imag - (b - a).imag * (Z - a).real
        if cross < -1e-9:
            return False
    return True


def poligon_interior_path(Z, V):
    """Calea 2: algoritmul general de apartenență la un poligon (matplotlib.path)."""
    return Path(np.column_stack([V.real, V.imag])).contains_point((Z.real, Z.imag), radius=1e-9)


# ---------------------------------------------------------------------------
# Rețeaua cu defect în interiorul unei linii și mărimile văzute de releu
# ---------------------------------------------------------------------------

def retea_cu_bara_pe_linie(linie="L1", x=0.7, delta_C=0.0, c=C_MAX):
    """Rețeaua de referință cu bara F la distanța x (fracțiune) de capătul b1 al liniei.
    delta_C – unghiul cu care t.e.m. sursei QC rămâne în urma celei din A (transfer A → C) [grade]."""
    r = retea_referinta(c=c, cu_capacitati=False)
    e = r.element(linie)
    r.elemente.remove(e)
    r.bara("F", r.bare[e["b1"]])
    r.linie(linie + "a", e["b1"], "F", e["Z1"] * x, e["Z0"] * x)
    r.linie(linie + "b", "F", e["b2"], e["Z1"] * (1 - x), e["Z0"] * (1 - x))
    qc = r.element("QC")
    qc["E"] = qc["E"] * np.exp(-1j * np.radians(delta_C))
    return r


def bucle(V, I, k0=K0):
    """Impedanțele celor șase bucle măsurate de releu (3 fază–pământ cu compensare, 3 fază–fază)."""
    I0x3 = np.sum(I)
    Z = {}
    with np.errstate(divide="ignore", invalid="ignore"):   # bucla fără curent: impedanță infinită
        for k, f in enumerate("abc"):
            Z[f + "-p"] = V[k] / (I[k] + k0 * I0x3)
        for (i, j) in ((0, 1), (1, 2), (2, 0)):
            Z["abc"[i] + "abc"[j]] = (V[i] - V[j]) / (I[i] - I[j])
    return Z


def masuratori_faze(r, defecte, linie_releu="L1a", bara_releu="A"):
    """Tensiunile la bara releului și curenții care intră în linie, din calculul în coordonate de fază."""
    p = r.rezolva_faze(defecte)
    V = r.tensiuni_faze(p, bara_releu)
    I = r.curenti_ramura_faze(p, linie_releu, 1)
    return V, I, p


def masuratori_secvente(r, bara_defect, tip, Rf=0.0, linie_releu="L1a", bara_releu="A"):
    """Aceleași mărimi, calculate cu rețelele de secvență."""
    s = r.scurtcircuit_secvente(bara_defect, tip, Zf=Rf)
    k = s["idx"][bara_releu]
    V = A_SIM @ np.array([s["V_seq"][q][k] for q in (0, 1, 2)])
    I = r.curenti_ramura_secvente(s, linie_releu, 1)
    return V, I, s


# ---------------------------------------------------------------------------
# Pendulații: sistemul cu două surse echivalente
# ---------------------------------------------------------------------------

def impedante_pendulatie():
    r = retea_referinta(cu_capacitati=False)
    ZSA = r.element("QA")["Z1"]
    ZSC = r.element("QC")["Z1"]
    return ZSA, ZSC, ZSA + ZL1 + ZL2 + ZSC


def z_pendulatie(delta, raport_E=1.0):
    """Impedanța văzută de releul din A când t.e.m. din A este înaintea celei din C cu δ
    (formula închisă): Z = E_A·Z_T/(E_A − E_C) − Z_SA."""
    ZSA, ZSC, ZT = impedante_pendulatie()
    EA = 1.0
    EC = raport_E * np.exp(-1j * delta)
    return EA * ZT / (EA - EC) - ZSA


def beta_rf(x, delta_C, Rf=RF_53):
    """Unghiul β = arg(IF/IA,comp) pentru un defect a–p prin Rf la distanța x pe L1 [grade]."""
    r = retea_cu_bara_pe_linie("L1", x, delta_C)
    _, I, s = masuratori_secvente(r, "F", "1f", Rf)
    IF = s["I_faza"][0]
    return np.degrees(np.angle(IF / (I[0] + K0 * np.sum(I))))


def inclinare_latura_sus(delta_max=DELTA_MAX, rezerva=2.0):
    """Înclinarea laturii de sus a poligonului zonei 1: |β| maxim la capătul care exportă
    (defect la 70 % și la bara B), rotunjit în sus la grad, plus rezerva. Întoarce (|β|max, înclinarea) în grade."""
    beta_max = max(-beta_rf(x, delta_max) for x in (0.7, 0.999))
    return beta_max, np.ceil(beta_max) + rezerva
