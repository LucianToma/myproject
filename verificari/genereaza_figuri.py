"""Generează figurile cursului (în directorul figuri/) din aceleași simulări
folosite la verificări. Necesită matplotlib.

Utilizare (din rădăcina depozitului):
    python3 verificari/genereaza_figuri.py
"""
import math
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from comun import armonici, esantioane_perioada  # noqa: E402
from simulator_dcdc import concateneaza, iL, simuleaza, vC  # noqa: E402
from v04_redresoare import punte_trifazata, simuleaza_filtru, simuleaza_tiristoare  # noqa: E402
from v06_invertoare import VDC, purtatoare, spwm_picior  # noqa: E402

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figuri")
C1, C2, C3, C4 = "#1f77b4", "#d62728", "#2ca02c", "#7f7f7f"

plt.rcParams.update({"figure.dpi": 110, "savefig.dpi": 110, "font.size": 10,
                     "axes.grid": True, "grid.alpha": 0.3, "axes.spines.top": False,
                     "axes.spines.right": False})


def salveaza(fig, nume):
    fig.tight_layout()
    fig.savefig(os.path.join(DIR, nume))
    plt.close(fig)
    print("  scris:", nume)


def fig_forme_unda():
    th = esantioane_perioada(4000)
    u = th / (2 * np.pi)
    fig, ax = plt.subplots(1, 3, figsize=(11, 3.2))
    ax[0].plot(u, 100 * np.sin(th), C1)
    ax[0].axhline(100 / math.sqrt(2), color=C2, ls="--", label="RMS = Vm/√2")
    ax[0].set_title("Sinusoidă, Vm = 100 V")
    ax[0].set_ylim(-110, 140)
    D = 0.3
    ax[1].plot(u, np.where(u < D, 10, 0), C1)
    ax[1].axhline(10 * D, color=C3, ls="--", label="medie = D·I")
    ax[1].axhline(10 * math.sqrt(D), color=C2, ls="--", label="RMS = I·√D")
    ax[1].set_title("Puls dreptunghiular, I = 10 A, D = 0,3")
    ond = 10 + 3 * (np.abs(2 * u - 1) - 0.5)
    ax[2].plot(u, ond, C1)
    ax[2].axhline(10, color=C3, ls="--", label="medie = I")
    ax[2].axhline(math.sqrt(100 + 9 / 12), color=C2, ls="--", label="RMS = √(I²+ΔI²/12)")
    ax[2].set_title("C.c. + ondulație, I = 10 A, ΔI = 3 A")
    ax[2].set_ylim(7, 13)
    for a in ax:
        a.set_xlabel("t / T")
        a.legend(fontsize=8, loc="upper right")
    ax[1].set_ylim(-0.5, 14)
    salveaza(fig, "02_forme_unda.png")


def fig_redresoare():
    th = np.linspace(0, 4 * np.pi, 2000)
    Vm = math.sqrt(2) * 230
    v = Vm * np.sin(th)
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.2), sharey=True)
    for a, y, titlu_, med in [(ax[0], np.maximum(v, 0), "Monoalternanță", Vm / math.pi),
                              (ax[1], np.abs(v), "Dublă alternanță (punte)", 2 * Vm / math.pi)]:
        a.plot(np.degrees(th), v, color=C4, lw=0.8, label="v_s")
        a.plot(np.degrees(th), y, C1, lw=1.8, label="v_o")
        a.axhline(med, color=C2, ls="--", label=f"V_dc = {med:.1f} V")
        a.set_title(titlu_ + ", Vs = 230 V")
        a.set_xlabel("ωt [grade]")
        a.legend(fontsize=8, loc="lower left")
    ax[0].set_ylabel("tensiune [V]")
    salveaza(fig, "04_redresoare_R.png")


def fig_filtru():
    Vm = math.sqrt(2) * 12
    sim = simuleaza_filtru(Vm, 50.0, 20.0, 4700e-6, Rs=0.5, perioade=20, pasi=8000)
    t = (sim["t"] - sim["t"][0]) * 1e3
    fig, ax = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
    ax[0].plot(t, np.abs(sim["vs"]), color=C4, lw=0.8, label="|v_s|")
    ax[0].plot(t, sim["vC"], C1, lw=1.8, label="v_C = v_o")
    ax[0].set_ylabel("tensiune [V]")
    ax[0].set_ylim(10, 18)
    ax[0].legend(fontsize=8, loc="lower right")
    ax[0].set_title("Punte cu filtru capacitiv: 12 V / 50 Hz, C = 4700 µF, R = 20 Ω, Rs = 0,5 Ω")
    ax[1].plot(t, sim["is"], C2, lw=1.5)
    ax[1].set_ylabel("curent de rețea i_s [A]")
    ax[1].set_xlabel("t [ms]")
    salveaza(fig, "04_filtru_capacitiv.png")


def fig_tiristoare():
    fig, ax = plt.subplots(2, 2, figsize=(10, 5), sharex=True)
    for col, (L, titlu_) in enumerate([(1.0, "L = 1 H (conducție continuă)"),
                                       (0.02, "L = 20 mH (conducție discontinuă)")]):
        sim = simuleaza_tiristoare(230.0, 50.0, 10.0, L, math.radians(60), perioade=60,
                                   pasi=4000)
        g = np.degrees(sim["th"])
        ax[0, col].plot(g, sim["vs"], color=C4, lw=0.8, label="v_s")
        ax[0, col].plot(g, sim["vo"], C1, lw=1.5, label="v_o")
        ax[0, col].axhline(np.mean(sim["vo"]), color=C2, ls="--",
                           label=f"V_dc = {np.mean(sim['vo']):.0f} V")
        ax[0, col].set_title("α = 60°, " + titlu_)
        ax[0, col].legend(fontsize=8, loc="lower left")
        ax[1, col].plot(g, sim["io"], C3, lw=1.5)
        ax[1, col].set_xlabel("ωt [grade]")
    ax[0, 0].set_ylabel("tensiune [V]")
    ax[1, 0].set_ylabel("i_o [A]")
    salveaza(fig, "04_tiristoare.png")


def fig_trifazat():
    th, vo, ia, va = punte_trifazata(400.0, 0.0, n=3600)
    g = np.degrees(th)
    Vm = 400 * math.sqrt(2) / math.sqrt(3)
    fig, ax = plt.subplots(2, 1, figsize=(8, 5), sharex=True)
    for k, nume in enumerate(["v_a", "v_b", "v_c"]):
        ax[0].plot(g, Vm * np.sin(th - 2 * np.pi * k / 3), lw=0.8, label=nume)
    ax[0].plot(g, vo, "k", lw=1.8, label="v_o (linie)")
    ax[0].axhline(np.mean(vo), color=C2, ls="--", label=f"V_dc = {np.mean(vo):.0f} V")
    ax[0].set_ylabel("tensiune [V]")
    ax[0].set_ylim(-560, 640)
    ax[0].legend(fontsize=8, ncol=5, loc="lower center")
    ax[0].set_title("Punte trifazată cu diode, VLL = 400 V")
    ax[1].plot(g, ia, C2, lw=1.5)
    ax[1].set_ylabel("i_a / I_d")
    ax[1].set_xlabel("ωt [grade]")
    salveaza(fig, "04_punte_trifazata.png")


def fig_buck():
    rez = simuleaza("buck", 24.0, 0.5, 100e-6, 47e-6, 6.0, 100e3)
    t, i = concateneaza(rez, iL)
    _, v = concateneaza(rez, vC)
    Ts = rez["Ts"]
    T = np.concatenate([t + k * Ts for k in range(3)]) * 1e6
    I = np.tile(i, 3)
    V = np.tile(v, 3)
    sw = (np.concatenate([t + k * Ts for k in range(3)]) % Ts) < 0.5 * Ts
    fig, ax = plt.subplots(3, 1, figsize=(8, 6), sharex=True)
    ax[0].plot(T, sw.astype(float), C4, drawstyle="steps-post")
    ax[0].set_ylabel("comandă S")
    ax[0].set_yticks([0, 1])
    ax[0].set_title("Buck 24 V → 12 V, D = 0,5, L = 100 µH, C = 47 µF, R = 6 Ω, 100 kHz")
    ax[1].plot(T, I, C1, lw=1.5)
    ax[1].set_ylabel("i_L [A]")
    ax[2].plot(T, V * 1e3 - 12000, C2, lw=1.5)
    ax[2].set_ylabel("v_o − 12 V [mV]")
    ax[2].set_xlabel("t [µs]")
    salveaza(fig, "05_buck_forme_unda.png")


def fig_caracteristici():
    D = np.linspace(0.01, 0.9, 300)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(D, D, C1, lw=2, label="buck: D")
    ax.plot(D, 1 / (1 - D), C2, lw=2, label="boost: 1/(1−D)")
    ax.plot(D, D / (1 - D), C3, lw=2, label="buck-boost: D/(1−D)")
    ax.set_ylim(0, 6)
    ax.set_xlabel("factorul de umplere D")
    ax.set_ylabel("M = |V_o| / V_in")
    ax.set_title("Caracteristici ideale în CCM")
    ax.legend()
    salveaza(fig, "05_caracteristici_M_D.png")


def fig_dcm():
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.2), sharey=True)
    for a, L, titlu_ in [(ax[0], 100e-6, "CCM: L = 100 µH"), (ax[1], 10e-6, "DCM: L = 10 µH")]:
        rez = simuleaza("buck", 24.0, 0.5, L, 470e-6, 6.0, 100e3)
        t, i = concateneaza(rez, iL)
        Ts = rez["Ts"]
        a.plot(np.concatenate([t + k * Ts for k in range(2)]) * 1e6, np.tile(i, 2), C1, lw=1.5)
        a.set_title(f"Buck 24 V, D = 0,5, R = 6 Ω — {titlu_}")
        a.set_xlabel("t [µs]")
    ax[0].set_ylabel("i_L [A]")
    salveaza(fig, "05_ccm_dcm.png")


def fig_spwm():
    ma, mf = 0.8, 21
    th = esantioane_perioada(2 ** 16)
    v = spwm_picior(ma, mf, th=th)
    g = np.degrees(th)
    fig, ax = plt.subplots(3, 1, figsize=(8, 7))
    ax[0].plot(g, purtatoare(th, mf), C4, lw=0.8, label="purtătoare")
    ax[0].plot(g, ma * np.sin(th), C1, lw=1.8, label="referință (ma = 0,8)")
    ax[0].legend(fontsize=8, loc="upper right")
    ax[0].set_title("PWM sinusoidal, semipunte, Vdc = 400 V, mf = 21")
    ax[1].plot(g, v, C2, lw=0.8)
    ax[1].plot(g, ma * VDC / 2 * np.sin(th), "k--", lw=1.2, label="fundamentala")
    ax[1].set_ylabel("v_o [V]")
    ax[1].set_xlabel("θ = ωt [grade]")
    ax[1].legend(fontsize=8, loc="upper right")
    a = armonici(v, 70)
    ax[2].bar(np.arange(1, 71), a[1:], color=C1, width=0.7)
    ax[2].set_xlabel("ordinul armonicii h")
    ax[2].set_ylabel("amplitudine [V]")
    ax[2].set_title("Spectru: fundamentala (160 V) + grupuri în jurul lui mf, 2mf, 3mf")
    salveaza(fig, "06_spwm.png")


def fig_bip_unip():
    ma, mf = 0.8, 20
    th = esantioane_perioada(2 ** 16)
    vA = spwm_picior(ma, mf, th=th)
    vB = spwm_picior(ma, mf, th=th, referinta=lambda x: -ma * np.sin(x))
    fig, ax = plt.subplots(2, 2, figsize=(10, 5))
    g = np.degrees(th)
    for col, (v, titlu_) in enumerate([(2 * vA, "bipolar"), (vA - vB, "unipolar")]):
        ax[0, col].plot(g, v, C2, lw=0.7)
        ax[0, col].set_title(f"Punte H, PWM {titlu_}, ma = 0,8, mf = 20")
        ax[0, col].set_xlabel("θ [grade]")
        a = armonici(v, 70)
        ax[1, col].bar(np.arange(1, 71), a[1:], color=C1, width=0.7)
        ax[1, col].set_xlabel("ordinul armonicii h")
        ax[1, col].set_ylim(0, 350)
    ax[0, 0].set_ylabel("v_o [V]")
    ax[1, 0].set_ylabel("amplitudine [V]")
    salveaza(fig, "06_bipolar_unipolar.png")


def fig_comutatie():
    V, I = 48.0, 10.0
    t_ri, t_fv, t_on, t_rv, t_fi = 20, 30, 150, 30, 20
    t = np.linspace(0, t_ri + t_fv + t_on + t_rv + t_fi + 40, 4000)
    t0 = 20
    a, b = t0 + t_ri, t0 + t_ri + t_fv
    c = b + t_on
    d, e = c + t_rv, c + t_rv + t_fi
    i = np.interp(t, [0, t0, a, c, d, e, t[-1]], [0, 0, I, I, I, 0, 0])
    v = np.interp(t, [0, a, b, c, d, t[-1]], [V, V, 0, 0, V, V])
    fig, ax = plt.subplots(2, 1, figsize=(8, 4.8), sharex=True)
    ax[0].plot(t, v, C1, lw=1.8, label="v_DS [V]")
    ax[0].plot(t, i * 4, C2, lw=1.8, label="i_D × 4 [A]")
    ax[0].legend(fontsize=8, loc="center right")
    ax[0].set_title("Comutație dură pe sarcină inductivă (modele liniare)")
    ax[1].fill_between(t, v * i, color=C3, alpha=0.6)
    ax[1].set_ylabel("p = v·i [W]")
    ax[1].set_xlabel("t [ns]")
    ax[1].set_ylim(0, V * I * 1.35)
    ax[1].annotate("E_on = ½·V·I·(t_ri + t_fv)", (5, V * I * 1.12), fontsize=9)
    ax[1].annotate("E_off = ½·V·I·(t_rv + t_fi)", (160, V * I * 1.12), fontsize=9)
    salveaza(fig, "07_pierderi_comutatie.png")


def main():
    os.makedirs(DIR, exist_ok=True)
    fig_forme_unda()
    fig_redresoare()
    fig_filtru()
    fig_tiristoare()
    fig_trifazat()
    fig_buck()
    fig_caracteristici()
    fig_dcm()
    fig_spwm()
    fig_bip_unip()
    fig_comutatie()


if __name__ == "__main__":
    main()
