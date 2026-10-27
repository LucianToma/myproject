"""Parametrii de secvență zero ai liniilor din modulul 01, pe două căi independente.

Calea A: formulele simplificate Carson (primul termen + adâncimea echivalentă De).
Calea B: integrala lui Carson evaluată numeric (formula completă, sol omogen), pentru o geometrie
         concretă care reproduce X1 din biblioteca pandapower.

Rulare: python3 verify/m01_line_params.py
"""
import cmath
import math
import numpy as np
from scipy.integrate import quad

F = 50.0
W = 2 * math.pi * F
MU0 = 4e-7 * math.pi
RHO = 100.0  # Ω·m, sol de rezistivitate medie (ipoteză declarată în pagină)

# Calea A ---------------------------------------------------------------
RE = W * MU0 / 8 * 1000                     # rezistența de retur prin pământ, Ω/km  (= π²·f·10⁻⁴)
DE = 1.85 / math.sqrt(W * MU0 / RHO)        # adâncimea echivalentă, m  (= 658,5·√(ρ/f))
K = W * MU0 / (2 * math.pi) * 1000          # Ω/km per unitate de ln  (= ω·2·10⁻⁴)

print(f"R_e = {RE:.5f} Ω/km (π²·f·1e-4 = {math.pi**2*F*1e-4:.5f})")
print(f"D_e = {DE:.1f} m (658,5·√(ρ/f) = {658.5*math.sqrt(RHO/F):.1f})")

# Conductoare: raza exterioară r (m), GMR = 0,809·r pentru Ol-Al 26/7 (aproximare uzuală pentru 26/7)
CONDS = {
    "ol70": dict(R1=0.4132, X1=0.36, r=11.7e-3 / 2),
    "ol120": dict(R1=0.2376, X1=0.344, r=15.5e-3 / 2),
}


def path_a(R1, X1, r):
    gmr = 0.809 * r
    gmd = gmr * math.exp(X1 / K)            # geometria medie care reproduce X1 din pandapower
    R0 = R1 + 3 * RE
    X0 = X1 + 3 * K * math.log(DE / gmd)
    return gmd, R0, X0


def carson_mutual(h1, h2, d):
    """Impedanța proprie/mutuală de retur prin pământ (Ω/km), integrala lui Carson evaluată numeric."""
    m = math.sqrt(W * MU0 / RHO)

    def integrand_re(lam):
        mu = cmath.sqrt(lam * lam + 1j * m * m)
        val = np.exp(-lam * (h1 + h2)) * np.cos(lam * d) * 2 / (lam + mu)
        return val.real

    def integrand_im(lam):
        mu = cmath.sqrt(lam * lam + 1j * m * m)
        val = np.exp(-lam * (h1 + h2)) * np.cos(lam * d) * 2 / (lam + mu)
        return val.imag

    jre, _ = quad(integrand_re, 0, np.inf, limit=400)
    jim, _ = quad(integrand_im, 0, np.inf, limit=400)
    J = jre + 1j * jim
    # termenul Carson: ΔZ = j·ω·μ0/(2π)·J   [Ω/m]
    return 1j * W * MU0 / (2 * math.pi) * J * 1000


def path_b(R1, X1, r):
    """Geometrie triunghiulară echilaterală la înălțimea medie de 10 m, cu latura = GMD de la calea A."""
    gmr = 0.809 * r
    gmd = gmr * math.exp(X1 / K)
    h = 10.0
    # trei faze: a, b pe orizontală, c deasupra (triunghi echilateral)
    pos = [(-gmd / 2, h), (gmd / 2, h), (0.0, h + gmd * math.sqrt(3) / 2)]
    Rc = R1  # rezistența conductorului (c.a., 20 °C) din pandapower
    Z = np.zeros((3, 3), dtype=complex)
    for i, (xi, yi) in enumerate(pos):
        for j, (xj, yj) in enumerate(pos):
            if i == j:
                Z[i, j] = Rc + 1j * K * math.log(2 * yi / gmr) + carson_mutual(yi, yi, 0.0)
            else:
                dij = math.hypot(xi - xj, yi - yj)
                Dij = math.hypot(xi - xj, yi + yj)
                Z[i, j] = 1j * K * math.log(Dij / dij) + carson_mutual(yi, yj, abs(xi - xj))
    a = np.exp(2j * math.pi / 3)
    A = np.array([[1, 1, 1], [1, a * a, a], [1, a, a * a]])
    Zs = np.linalg.inv(A) @ Z @ A
    return Zs[0, 0], Zs[1, 1]


for name, c in CONDS.items():
    gmd, R0a, X0a = path_a(**c)
    z0b, z1b = path_b(**c)
    print(f"\n{name}: GMD = {gmd:.3f} m")
    print(f"  calea A (Carson simplificat): R0 = {R0a:.4f} Ω/km, X0 = {X0a:.4f} Ω/km")
    print(f"  calea B (integrală numerică): R0 = {z0b.real:.4f} Ω/km, X0 = {z0b.imag:.4f} Ω/km; Z1 = {z1b.real:.4f} + j{z1b.imag:.4f}")
    print(f"  abatere A vs B: R0 {100*(R0a/z0b.real-1):+.2f} %, X0 {100*(X0a/z0b.imag-1):+.2f} %")

# Cablu NA2XS2Y 1×185, ecran Cu 25 mm², ecrane legate la ambele capete, retur numai prin ecrane:
# Z0 ≈ R_c + R_ecran (cele trei ecrane în paralel duc 3·I0), X0 ≈ X1 (câmpul închis între conductor și ecran)
R_screen = 0.0175 * 1000 / 25   # Ω/km, cupru la 20 °C (ρ = 0,0175 Ω·mm²/m)
print(f"\ncab185: R_ecran = {R_screen:.3f} Ω/km → R0 ≈ {0.161 + R_screen:.3f} Ω/km, X0 ≈ X1 = 0.117 Ω/km (estimare)")
