"""Capitolul 0 – Introducere: rezolvarea și verificarea problemelor."""

import numpy as np
from modele import fmt, verifica, verifica_adevarat, retea_referinta, C_MAX

print("Problema 0.1 – cât timp suportă cablul de 20 kV curentul de scurtcircuit")
S = 185.0                 # secțiunea conductorului [mm²], aluminiu, izolație XLPE
k_tabel = 94.0            # IEC 60364-5-54: Al/XLPE, 90 °C → 250 °C [A·s^0,5/mm²]
# Calea a doua: k din constantele de material (forma generală din IEC 60364-5-54 / IEC 60949)
Qc, beta, rho20 = 2.5e-3, 228.0, 28.264e-6      # J/(K·mm³), K, Ω·mm – aluminiu
K_mat = np.sqrt(Qc * (beta + 20) / rho20)
k_calc = K_mat * np.sqrt(np.log((beta + 250) / (beta + 90)))
print(f"  K (aluminiu) = {fmt(K_mat, 1)} A·s^0,5/mm²; k (90 → 250 °C) = {fmt(k_calc, 2)} față de {fmt(k_tabel, 0)} din tabel")
verifica("k tabelat vs k din constantele de material", k_tabel, k_calc, rtol=1e-2)
# Același calcul pentru cupru, ca a doua verificare a formulei
Kcu = np.sqrt(3.45e-3 * (234.5 + 20) / 17.241e-6)
kcu = Kcu * np.sqrt(np.log((234.5 + 250) / (234.5 + 90)))
print(f"  pentru cupru: K = {fmt(Kcu, 1)}, k = {fmt(kcu, 1)} (în tabel: 143)")
verifica("k cupru tabelat vs calculat", 143.0, kcu, rtol=1e-2)
I1s = k_tabel * S
r = retea_referinta(cu_capacitati=False)
Ik = abs(r.scurtcircuit_secvente("B2", "3f")["I_faza"][0])
tmax = (k_tabel * S / Ik) ** 2
print(f"  curentul admisibil 1 s: I = k·S = {fmt(I1s / 1e3, 2)} kA")
print(f"  la bara B2: I\"k3 = {fmt(Ik / 1e3, 2)} kA → t_max = (k·S/I)² = {fmt(tmax, 2)} s")
# Temperatura finală pentru câțiva timpi de eliminare (ecuația adiabatică inversată)
for t in (0.1, 0.5, 1.0, 2.0, tmax):
    theta_f = (beta + 90) * np.exp(Ik**2 * t / (K_mat * S) ** 2) - beta
    print(f"  t = {fmt(t, 2)} s: temperatura finală a conductorului ≈ {fmt(theta_f, 0)} °C")
    if t == tmax:
        # cu k rotunjit în jos (94 < 94,55), la t_max conductorul rămâne puțin sub 250 °C
        verifica_adevarat("la t_max temperatura finală este între 245 și 250 °C", 245 < theta_f <= 250)
verifica_adevarat("eliminarea în 1 s este admisibilă", tmax > 1.0)
# Componenta aperiodică (deplasare maximă) adaugă energia ∫(√2·I·e^{−t/T})² dt = I²·T·(1 − e^{−2t/T})
from scipy.optimize import brentq  # noqa: E402
from modele import W0  # noqa: E402
Z1 = r.scurtcircuit_secvente("B2", "3f")["Zth"][1]
T = Z1.imag / (W0 * Z1.real)
for t in (0.1, 0.5, 1.0):
    frac = T * (1 - np.exp(-2 * t / T)) / t
    print(f"  la t = {fmt(t, 1)} s, componenta aperiodică adaugă {fmt(100 * frac, 1)} % la I²t (T = {fmt(T * 1e3, 1)} ms)")
tmax_dc = brentq(lambda t: t + T * (1 - np.exp(-2 * t / T)) - tmax, 0.1, tmax)
# calea a doua: integrarea numerică a pătratului curentului real (cu deplasarea maximă)
phi = np.arctan2(Z1.imag, Z1.real)
al = phi - np.pi / 2
dt = 2e-5
tt = np.arange(0, tmax + 0.1, dt)
i = np.sqrt(2) * Ik * (np.sin(W0 * tt + al - phi) - np.sin(al - phi) * np.exp(-tt / T))
I2t = np.cumsum(i**2) * dt
tmax_num = tt[np.argmax(I2t >= (k_tabel * S) ** 2)]
print(f"  cu componenta aperiodică maximă: t_max = {fmt(tmax_dc, 3)} s (integrare numerică a lui i²: {fmt(tmax_num, 3)} s)")
# diferența rămasă (sub 5 ms) vine din termenii oscilanți ai lui i², care formula îi neglijează
verifica("t_max cu componenta aperiodică: formulă vs integrarea lui i²(t)", tmax_dc, tmax_num, rtol=0, atol=5e-3)

print("\nProblema 0.2 – redundanța protecțiilor: 1 din 2, 2 din 2, 2 din 3")
pf = 0.02    # probabilitatea ca o protecție să NU acționeze la un defect (refuz)
pu = 0.01    # probabilitatea ca o protecție să acționeze nedorit (declanșare intempestivă)
an = {
    "1 din 2": (pf**2, 1 - (1 - pu) ** 2),
    "2 din 2": (1 - (1 - pf) ** 2, pu**2),
    "2 din 3": (3 * pf**2 - 2 * pf**3, 3 * pu**2 - 2 * pu**3),
    "1 din 1": (pf, pu),
}
rng = np.random.default_rng(2026)
N = 2_000_000
refuz = rng.random((N, 3)) < pf     # True = protecția refuză
nedorit = rng.random((N, 3)) < pu   # True = protecția acționează nedorit
mc = {
    "1 din 2": (np.mean(refuz[:, 0] & refuz[:, 1]), np.mean(nedorit[:, 0] | nedorit[:, 1])),
    "2 din 2": (np.mean(refuz[:, 0] | refuz[:, 1]), np.mean(nedorit[:, 0] & nedorit[:, 1])),
    "2 din 3": (np.mean(refuz.sum(axis=1) >= 2), np.mean(nedorit.sum(axis=1) >= 2)),
    "1 din 1": (np.mean(refuz[:, 0]), np.mean(nedorit[:, 0])),
}
for k in ("1 din 1", "1 din 2", "2 din 2", "2 din 3"):
    (a1, a2), (m1, m2) = an[k], mc[k]
    print(f"  {k}: P(refuz) = {a1:.2e} (simulare {m1:.2e}); P(acționare nedorită) = {a2:.2e} (simulare {m2:.2e})")
    # toleranța: 5 abateri standard ale estimatorului binomial
    for nume, x, y in (("refuz", a1, m1), ("nedorit", a2, m2)):
        tol = 5 * np.sqrt(x * (1 - x) / N)
        verifica(f"{k} – P({nume}) analitic vs Monte Carlo", y, x, rtol=0, atol=tol)
verifica_adevarat("2 din 3 are refuz mai mic decât 1 din 1 și acționări nedorite mai puține decât 1 din 2",
                  an["2 din 3"][0] < an["1 din 1"][0] and an["2 din 3"][1] < an["1 din 2"][1])
