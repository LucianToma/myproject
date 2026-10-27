"""Capitolul 2 – Transformatoare de măsură: rezolvarea și verificarea problemelor."""

import numpy as np
from scipy.optimize import brentq
from modele import (SQRT3, W0, DATE, fmt, verifica, verifica_adevarat, retea_referinta, defect_faze,
                    flux_tc, tc_neliniar, polar)

d = DATE
r = retea_referinta(cu_capacitati=False)
s_B2 = r.scurtcircuit_secvente("B2", "3f")
Ik = abs(s_B2["I_faza"][0])
Z1 = s_B2["Zth"][1]

print("Problema 2.1 – verificarea TC al fiderului F1 (400/1 A, 5P20, 5 VA, Rct = 1,5 Ω)")
In1, In2 = 400.0, 1.0
ALF, Sn, Rct = 20, 5.0, 1.5
Rn = Sn / In2**2
rho_cu = 0.0178          # Ω·mm²/m la 20 °C
l_cond, S_cond = 10.0, 2.5   # lungimea traseului (dus) [m], secțiunea [mm²]
R_cond = rho_cu * 2 * l_cond / S_cond     # bucla dus–întors (defect între faze)
R_releu = 0.1 / In2**2                      # releu numeric: 0,1 VA la 1 A
Rb = R_cond + R_releu
ALF_ef = ALF * (Rct + Rn) / (Rct + Rb)
I_cerut = Ik / In1
print(f"  Rn = Sn/In² = {fmt(Rn, 1)} Ω; conductoare {fmt(R_cond, 3)} Ω + releu {fmt(R_releu, 2)} Ω = Rb = {fmt(Rb, 3)} Ω")
print(f"  ALF efectiv = ALF·(Rct + Rn)/(Rct + Rb) = {fmt(ALF_ef, 1)}; curentul maxim = {fmt(Ik, 0)} A = {fmt(I_cerut, 2)}·In")
# Calea a doua: comparația tensiunilor electromotoare secundare
E_ALF = ALF * In2 * (Rct + Rn)
E_nec = I_cerut * In2 * (Rct + Rb)
print(f"  t.e.m. disponibilă la limita de precizie E_ALF = {fmt(E_ALF, 1)} V; t.e.m. necesară = {fmt(E_nec, 2)} V")
verifica("rezerva: ALF_ef/(Ik/In) = E_ALF/E_nec", ALF_ef / I_cerut, E_ALF / E_nec)
verifica_adevarat("TC nu se saturează la curentul simetric maxim", ALF_ef > I_cerut)

print("\nProblema 2.2 – saturația TC sub componenta aperiodică (conductoare lungi: 2 × 100 m, 2,5 mm²)")
R_cond2 = rho_cu * 2 * 100 / S_cond
R2 = Rct + R_cond2 + R_releu
T1 = Z1.imag / (W0 * Z1.real)
I2 = Ik / In1 * In2
psi_sat = np.sqrt(2) * E_ALF / W0
psi_sim = R2 * np.sqrt(2) * I2 / W0
Ktf = 1 + W0 * T1
print(f"  sarcina totală R2 = Rct + Rconductoare + Rreleu = {fmt(R2, 3)} Ω; T1 = X/(ωR) = {fmt(T1 * 1e3, 1)} ms")
print(f"  fluxul de saturație ≈ √2·E_ALF/ω = {fmt(psi_sat, 3)} V·s; fluxul maxim în regim simetric = {fmt(psi_sim, 3)} V·s")
print(f"  factorul tranzitoriu Ktf = 1 + ωT1 = {fmt(Ktf, 1)} → fluxul maxim cu deplasare completă ≈ "
      f"{fmt(psi_sim * Ktf, 2)} V·s ({fmt(psi_sim * Ktf / psi_sat, 1)}× fluxul de saturație)")
verifica_adevarat("regimul simetric nu saturează miezul", psi_sim < psi_sat)
verifica_adevarat("regimul cu componentă aperiodică saturează miezul", psi_sim * Ktf > psi_sat)
# Timpul până la saturație: calea 1 – expresia analitică a fluxului și rădăcina ecuației ψ(t) = ψsat
t_sat = brentq(lambda t: flux_tc(t, I2, R2, T1) - psi_sat, 1e-4, 0.05)
# calea 2 – integrarea numerică a tensiunii secundare R2·i2(t)
dt = 1e-6
t = np.arange(0, 0.05, dt)
i2 = np.sqrt(2) * I2 * (np.exp(-t / T1) - np.cos(W0 * t))
psi_num = np.concatenate(([0.0], np.cumsum((R2 * i2[1:] + R2 * i2[:-1]) / 2 * dt)))
t_sat_num = t[np.argmax(psi_num >= psi_sat)]
print(f"  timpul până la saturație: analitic {fmt(t_sat * 1e3, 2)} ms; integrare numerică {fmt(t_sat_num * 1e3, 2)} ms")
verifica("timpul până la saturație: analitic vs numeric", t_sat, t_sat_num, atol=2e-5, rtol=0)
# Cât de mică trebuie să fie sarcina pentru a nu se satura deloc (ψmax ≤ ψsat cu deplasare completă)?
R2_max = psi_sat / (np.sqrt(2) * I2 / W0 * Ktf)
print(f"  pentru a evita complet saturația ar trebui R2 ≤ {fmt(R2_max, 3)} Ω (sau un TC dimensionat pentru regimul tranzitoriu)")
# Calea a treia: modelul neliniar al TC (curba de magnetizare liniară pe porțiuni)
i2_nl = tc_neliniar(t, I2, R2, T1, psi_sat)
eroare = np.abs(i2_nl - i2) / (np.sqrt(2) * I2)
t_dev = t[np.argmax(eroare > 0.10)]
print(f"  modelul neliniar: curentul secundar se abate cu peste 10 % (din valoarea de vârf simetrică) la {fmt(t_dev * 1e3, 2)} ms")
verifica("începutul distorsiunii (model neliniar) vs timpul analitic de saturație", t_dev, t_sat, atol=1.5e-3, rtol=0)

print("\nProblema 2.3 – tensiunea homopolară la triunghiul deschis al TT (20 kV, 20/√3 : 0,1/√3 : 0,1/3 kV)")
n_TT = (d["U20"] / SQRT3) / (100 / 3)          # raportul înfășurării pentru triunghiul deschis
Uf = d["U20"] / SQRT3
# Calea 1: teoria – la punere metalică în rețea izolată, U0 = −Uf, deci 3·U0/n = 3·Uf/n
U_td_teorie = 3 * Uf / n_TT
# Calea 2: tensiunile de fază calculate în rețea (coordonate de fază), însumate în triunghiul deschis
for nume, net in (("neutru izolat", retea_referinta("izolat", c=1.0)),
                  ("rezistor 300 A", retea_referinta("rezistor", c=1.0))):
    for Rf in (0.0, 50.0, 200.0):
        p = net.rezolva_faze(defect_faze("B2", "1f", Rf))
        V = net.tensiuni_faze(p, "B2")
        U_td = abs(np.sum(V)) / n_TT
        s = net.scurtcircuit_secvente("B2", "1f", Zf=Rf)
        U0_s = abs(s["V_seq"][0][s["idx"]["B2"]])
        print(f"  {nume}, Rf = {fmt(Rf, 0)} Ω: U triunghi deschis = {fmt(U_td, 1)} V (din secvențe: {fmt(3 * U0_s / n_TT, 1)} V)")
        verifica(f"3U0 la triunghiul deschis: fază vs secvențe ({nume}, Rf = {Rf:g} Ω)", U_td, 3 * U0_s / n_TT)
        if nume == "neutru izolat" and Rf == 0.0:
            verifica("teorie (100 V) vs calcul exact (abatere sub 3 %)", U_td_teorie, U_td, rtol=3e-2)
print(f"  teorie: 3·Uf/n = {fmt(U_td_teorie, 1)} V")

print("\nProblema 2.4 – impedanța văzută în secundar de protecția de distanță a liniei L1 (TC 600/1 A, TT 110/0,1 kV)")
nTC, nTT = 600 / 1, 110e3 / 100
k_sec = nTC / nTT
ZL1 = d["z1_110"] * d["lL1"]
print(f"  Zsec = Zprim·nTC/nTT = Zprim·{fmt(k_sec, 4)}; ZL1 = {polar(ZL1, 2)} Ω primar → {polar(ZL1 * k_sec, 3)} Ω secundar")
# Calea 2: raportul tensiune/curent secundar la un defect trifazat la capătul B al liniei
rB = retea_referinta(cu_capacitati=False)
p = rB.rezolva_faze(defect_faze("B", "3f"))
VA = rB.tensiuni_faze(p, "A")[0] / nTT
IA = rB.curenti_ramura_faze(p, "L1", 1)[0] / nTC
print(f"  la defect trifazat în B: U = {fmt(abs(VA), 2)} V, I = {fmt(abs(IA), 3)} A în secundar → Z = {polar(VA / IA, 3)} Ω")
verifica("Zsec din conversie vs din mărimile secundare simulate", VA / IA, ZL1 * k_sec, atol=2e-3, rtol=1e-4)
