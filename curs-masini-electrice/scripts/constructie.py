"""Exemple numerice pentru secțiunile de construcție (cap. 1–5), verificate pe două căi."""

import numpy as np
from modele import SQRT3, fmt, verifica, arie_trepte, trepte_optime

print("Construcție 1 – cupru sau aluminiu pentru aceeași rezistență")
RHO_CU, RHO_AL = 1.7241e-8, 1.7241e-8 / 0.61       # Ω·m la 20 °C (100 % și 61 % IACS)
D_CU, D_AL = 8.89e3, 2.70e3                         # kg/m³
raport_arie = RHO_AL / RHO_CU
raport_masa = raport_arie * D_AL / D_CU
# Calea a doua: dimensionăm efectiv un conductor de 100 m cu R = 10 mΩ din fiecare metal
L, R = 100.0, 0.010
A_cu, A_al = RHO_CU * L / R, RHO_AL * L / R
m_cu, m_al = A_cu * L * D_CU, A_al * L * D_AL
print(f"  ρ_Al = {RHO_AL * 1e8:.3f}·10⁻⁸ Ω·m; aria Al / aria Cu = {fmt(raport_arie, 3)};"
      f" masa Al / masa Cu = {fmt(raport_masa, 3)}")
print(f"  conductor de 100 m, 10 mΩ: Cu {fmt(A_cu * 1e6, 1)} mm², {fmt(m_cu, 1)} kg; Al {fmt(A_al * 1e6, 1)} mm², {fmt(m_al, 1)} kg")
# (verificări aritmetice ale exemplului, nu căi independente)
verifica("exemplu vs raportul ariilor", A_al / A_cu, raport_arie)
verifica("exemplu vs raportul maselor", m_al / m_cu, raport_masa)

print("\nConstrucție 2 – factorul de umplere al secțiunii în trepte a coloanei")


factori = {}
for n in range(1, 10):
    k1 = trepte_optime(n, "L-BFGS-B")[1]
    k2 = trepte_optime(n, "Nelder-Mead")[1]
    factori[n] = k1
    print(f"  n = {n} trepte: factor de umplere = {fmt(k1, 4)}")
    verifica(f"n={n}: L-BFGS-B vs Nelder-Mead", k1, k2, rtol=2e-4)
verifica("o treaptă: 2/π (pătrat înscris)", factori[1], 2 / np.pi, rtol=1e-6)

print("\nConstrucție 3 – miezul transformatorului de 400 kVA, 20/0,4 kV, Dyn11")
f, B, k_fe, n_trepte = 50.0, 1.55, 0.95, 7
U2f, U1f = 400 / SQRT3, 20000.0
N2 = 22                                   # spire JT (alegere de exemplu)
e_t = U2f / N2                            # tensiunea pe spiră
Phi = e_t / (np.sqrt(2) * np.pi * f)
A_net = Phi / B
A_brut = A_net / k_fe
D = np.sqrt(4 * A_brut / (np.pi * factori[n_trepte]))
N1 = round(U1f / e_t)
print(f"  tensiunea pe spiră e = {fmt(e_t, 3)} V; Φmax = {fmt(Phi * 1e3, 2)} mWb")
print(f"  aria netă de fier = {fmt(A_net * 1e4, 1)} cm², aria brută = {fmt(A_brut * 1e4, 1)} cm²,"
      f" diametrul cercului circumscris (7 trepte) = {fmt(D * 1e3, 0)} mm")
print(f"  N1 = {N1} spire; raportul spirelor = {fmt(N1 / N2, 3)} (cerut: {fmt(U1f / U2f, 3)},"
      f" abatere {fmt(100 * (N1 / N2 / (U1f / U2f) - 1), 3)} %)")
# Calea a doua: fluxul calculat din partea de ÎT, cu N1 rotunjit
Phi_b = U1f / (np.sqrt(2) * np.pi * f * N1)
B_b = Phi_b / A_net
print(f"  din ÎT: Φmax = {fmt(Phi_b * 1e3, 2)} mWb, B = {fmt(B_b, 4)} T")
verifica("flux din JT vs din ÎT", Phi, Phi_b, rtol=5e-4)
verifica("aria brută reconstituită din D", np.pi * D**2 / 4 * factori[n_trepte], A_brut)

print("\nConstrucție 4 – de ce rotoarele turbogeneratoarelor sunt lungi și subțiri")
# Viteza periferică v = π D n / 60. La aceeași viteză periferică admisă, D_max ∝ 1/n.
for n in (3000, 1500, 150):
    print(f"  n = {n} rot/min: D pentru v = 100 m/s este {fmt(60 * 100 / (np.pi * n), 3)} m")
raport = (60 * 100 / (np.pi * 150)) / (60 * 100 / (np.pi * 3000))
verifica("raportul diametrelor admise = raportul inverse al turațiilor", raport, 3000 / 150)
# Tensiunea într-un inel subțire care se rotește: σ = ρ v² (independentă de grosime)
rho_otel = 7850.0
for v in (100, 150, 200):
    print(f"  inel subțire de oțel la v = {v} m/s: σ = ρv² = {fmt(rho_otel * v**2 / 1e6, 0)} MPa")
# Calea a doua pentru σ = ρ v²: echilibrul unui element de inel (forța centrifugă = 2 T sin(dθ/2))
r, dth, A_s = 0.5, 1e-4, 1e-4
v = 150.0
dm = rho_otel * A_s * r * dth
F_c = dm * v**2 / r
T = F_c / (2 * np.sin(dth / 2))
verifica("σ = ρv² vs echilibrul elementului de inel", T / A_s, rho_otel * v**2, rtol=1e-6)

print("\nConstrucție 5 – efectul temperaturii asupra magneților permanenți")
for nume, Br20, alfa in (("NdFeB", 1.30, -0.11e-2), ("SmCo", 1.05, -0.04e-2), ("ferită", 0.40, -0.20e-2)):
    Br120 = Br20 * (1 + alfa * 100)
    print(f"  {nume}: Br(20 °C) = {fmt(Br20, 2)} T → Br(120 °C) = {fmt(Br120, 3)} T ({fmt(100 * alfa * 100, 0)} %)")

print("\nConstrucție 6 – frâna de menținere a troliului din problema 5.1")
m, g_, D_t, i, eta_t = 2000.0, 9.81, 0.4, 60, 0.90
J_tot = 0.1 + 5 / i**2 + m * (D_t / 2 / i) ** 2      # kg·m² raportat la arborele motorului
Om = 2 * np.pi * 1466 / 60
v = Om / i * D_t / 2
M_t = m * g_ * D_t / 2
M_static = M_t / i                     # cuplul static al sarcinii la arborele frânei, fără frecări
M_ridicare = M_t / (i * eta_t)         # cuplul de ridicare la sarcina nominală (cu pierderile din reductor)
M_coborare = M_t * eta_t / i           # sarcina antrenează motorul prin reductor
print(f"  cuplul de ridicare la arborele frânei {fmt(M_ridicare, 2)} N·m; 125 % = {fmt(1.25 * M_ridicare, 2)} N·m")
M_b = 100.0                            # frâna aleasă din catalog
print(f"  cuplul static al sarcinii (fără frecări) M_t/i = {fmt(M_static, 2)} N·m;"
      f" rezerva frânei de {fmt(M_b, 0)} N·m la menținere = {fmt(M_b / M_static, 2)}")
t_op = J_tot * Om / (M_b - M_coborare)
theta = Om * t_op / 2                  # unghiul parcurs de arborele motorului (decelerare uniformă)
s_op = v * t_op / 2
E_b = M_b * theta
print(f"  oprirea sarcinii care coboară cu v = {fmt(v, 3)} m/s, frână de {fmt(M_b, 0)} N·m:"
      f" t = {fmt(t_op, 3)} s, distanța = {fmt(s_op * 1e3, 0)} mm, energia disipată = {fmt(E_b, 0)} J")
# Calea a doua: integrarea numerică a ecuației mișcării J dΩ/dt = M_coborare - M_b
from scipy.integrate import solve_ivp
oprit = lambda t, y: y[0]
oprit.terminal = True
sol = solve_ivp(lambda t, y: [(M_coborare - M_b) / J_tot, y[0]], (0, 5), [Om, 0.0], events=oprit,
                max_step=1e-3, rtol=1e-10, atol=1e-12)
t_num, theta_num = sol.t_events[0][0], sol.y_events[0][0][1]
verifica("timpul de oprire: formulă vs integrare (verificare aritmetică)", t_op, t_num, rtol=1e-6)
verifica("distanța de oprire: formulă vs integrare (verificare aritmetică)", s_op, theta_num / i * D_t / 2, rtol=1e-6)
# Calea a doua, pe partea sarcinii, cu vitezele fizice ale fiecărui corp (verifică și raportarea la arbore):
# energia frânei = energia cinetică a motorului, tamburului și masei + lucrul greutății pe distanța de oprire,
# diminuat cu pierderile din reductor (η_t, ca în problema 5.1)
Om_t = Om / i
E_cin = 0.5 * 0.1 * Om**2 + 0.5 * 5 * Om_t**2 + 0.5 * m * v**2
E_grav = eta_t * m * g_ * s_op
print(f"  pe partea sarcinii: energie cinetică {fmt(E_cin, 0)} J + lucrul greutății {fmt(E_grav, 0)} J"
      f" = {fmt(E_cin + E_grav, 0)} J")
verifica("energia frânei: M_b·θ (arborele motorului) vs bilanțul pe partea sarcinii", E_b, E_cin + E_grav)
# Ipoteza vitezei de coborâre: alimentat direct de la rețea, motorul coboară sarcina ca generator (s < 0)
from modele import motor_M15, kloss, sk_din_catalog
Mn = 15000 / Om
s_kloss = -(34 / 1500) * M_coborare / Mn                     # zona liniară a caracteristicii
mot = motor_M15()
from scipy.optimize import brentq
s_model = brentq(lambda x: mot.punct(x)["P2"] / ((1 - x) * mot.W1) + M_coborare, -0.1, -1e-5)
n_gen = 1500 * (1 - s_model)
v_gen = 2 * np.pi * n_gen / 60 / i * D_t / 2
t_gen = J_tot * (2 * np.pi * n_gen / 60) / (M_b - M_coborare)
print(f"  coborâre cu motorul alimentat direct: n = {fmt(n_gen, 0)} rot/min (Kloss liniar: {fmt(1500 * (1 - s_kloss), 0)}),"
      f" v = {fmt(v_gen, 3)} m/s, t_op = {fmt(t_gen, 3)} s, s_op = {fmt(v_gen * t_gen / 2 * 1e3, 0)} mm")
# Kloss liniarizat ignoră pierderile mecanice (P0), care la generator se scad din cuplul la arbore;
# de aceea cele două estimări diferă cu câteva rot/min – suficient pentru „circa 1520 rot/min”.
verifica("turația de coborâre: schema echivalentă vs Kloss liniar", n_gen, 1500 * (1 - s_kloss), rtol=3e-3)

print("\nConstrucție 7 – autoblocarea angrenajului melcat")
# η (melcul antrenează) = tg γ / tg(γ + ρ); η' (roata antrenează) = tg(γ - ρ) / tg γ; autoblocare: η' ≤ 0 ⇔ γ ≤ ρ
for mu in (0.03, 0.05, 0.08):
    rho = np.arctan(mu)
    eta_lim = np.tan(rho) / np.tan(2 * rho)
    gam = np.linspace(1e-4, np.radians(45), 200001)
    eta = np.tan(gam) / np.tan(gam + rho)
    eta_inv = np.tan(gam - rho) / np.tan(gam)
    eta_max_auto = eta[eta_inv <= 0].max()       # cel mai bun randament al unui melc încă autoblocant
    print(f"  μ = {fmt(mu, 2)}: ρ = {fmt(np.degrees(rho), 2)}°, la limita autoblocării η = {fmt(100 * eta_lim, 2)} %"
          f"; la γ = 20°: η = {fmt(100 * np.tan(np.radians(20)) / np.tan(np.radians(20) + rho), 1)} %")
    verifica(f"μ={mu}: limita formulă vs căutare numerică", eta_lim, eta_max_auto, rtol=1e-4)
    verifica(f"μ={mu}: η_lim = (1 - tg²ρ)/2 < 0,5", eta_lim, (1 - mu**2) / 2, rtol=1e-12)
    # Calea a doua pentru retroantrenare: relația aproximativă din catalogul [W19], η' ≈ 2 - 1/η (unghiuri mici)
    g = np.radians(20)
    e_d, e_i = np.tan(g) / np.tan(g + rho), np.tan(g - rho) / np.tan(g)
    verifica(f"μ={mu}, γ = 20°: η' exact vs 2 - 1/η [W19]", e_i, 2 - 1 / e_d, rtol=2e-2)

print("\nConstrucție 8 – reductor cu roți dințate: randamentul pe trepte")
for z in (1, 2, 3):
    print(f"  {z} {'treaptă' if z == 1 else 'trepte'} cu 98 % fiecare: η = {fmt(100 * 0.98**z, 1)} %")
verifica("3 trepte ≈ 94 % (valoarea din catalogul [W19])", 0.98**3, 0.94, rtol=2e-3)

print("\nConstrucție 9 – rezistența termică a ceramicii substratului DBC (1 cm², flux unidimensional)")
A = 1e-4
for nume, t_c, k in (("Al₂O₃, 0,38 mm", 0.38e-3, 24.0), ("AlN, 0,63 mm", 0.63e-3, 170.0)):
    R_th = t_c / (k * A)
    print(f"  {nume}: R_th = {fmt(R_th, 4)} K/W; la 100 W, ΔT = {fmt(100 * R_th, 1)} K")

print("\nConstrucție 10 – durata de viață a condensatoarelor electrolitice (regula celor 10 °C)")
L0, T0 = 5000.0, 105.0
for T_c in (105, 85, 65, 55):
    L = L0 * 2 ** ((T0 - T_c) / 10)
    print(f"  la {T_c} °C în miez: L = {fmt(L, 0)} h = {fmt(L / 8760, 1)} ani de funcționare continuă")
# Calea a doua: tabelul din nota Würth SN008 [W22] (2000 h la 105 °C → 8000 h la 85 °C, 32000 h la 65 °C)
verifica("regula vs tabelul [W22], 85 °C", 2000 * 2 ** ((105 - 85) / 10), 8000)
verifica("regula vs tabelul [W22], 65 °C", 2000 * 2 ** ((105 - 65) / 10), 32000)
verifica("forma exponențială exp(ln2·ΔT/10)", L0 * np.exp(np.log(2) * 4), L0 * 2**4)
