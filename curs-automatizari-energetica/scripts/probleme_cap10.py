"""Îndrumarul de laborator – valorile așteptate pentru lucrările L1 și L2 (verificate pe două căi)."""

import contextlib
import io
import runpy
from pathlib import Path

import numpy as np
from modele import fmt, verifica, verifica_adevarat, timp_invers, timp_integrator

with contextlib.redirect_stdout(io.StringIO()):
    P3 = runpy.run_path(str(Path(__file__).with_name("probleme_cap03.py")))
R1 = P3["relee"]["R1"]
I_inst = P3["I_inst_R1"]

print("L1 – încercarea releului R1 prin injecție secundară")
n = R1["TC"]
Is_sec = R1["Is"] / n
Iinst_sec = I_inst / n
print(f"  reglaje în secundar: Is = {fmt(R1['Is'], 0)} A / {n} = {fmt(Is_sec, 3)} A; TMS = {fmt(R1['TMS'], 2)} (SI); "
      f"I>> = {fmt(I_inst, 0)} A / {n} = {fmt(Iinst_sec, 2)} A")
for G in (2, 4, 6, 8):
    I = G * Is_sec
    t_f = float(timp_invers(I, Is_sec, R1["TMS"]))
    t_i = timp_integrator(np.full(int(t_f / 1e-4) + 50, I), 1e-4, Is_sec, R1["TMS"])
    print(f"  injecție {fmt(I, 2)} A ({G}·Is): timp așteptat {fmt(t_f, 3)} s")
    verifica(f"L1: G = {G}: formulă vs integrator", t_f, t_i, rtol=0, atol=2e-4)
    verifica_adevarat(f"L1: injecția de {G}·Is este sub pragul treptei instantanee", I < Iinst_sec)
# Treapta instantanee: sub prag (0,9·I>>) acționează treapta temporizată, peste prag (1,2·I>>) cea instantanee
for f_ in (0.9, 1.2):
    I = f_ * Iinst_sec
    t_f = float(timp_invers(I, Is_sec, R1["TMS"]))
    tip = "temporizată" if I < Iinst_sec else "instantanee"
    print(f"  injecție {fmt(I, 2)} A ({fmt(f_, 1)}·I>>): acționează treapta {tip}"
          + (f" după {fmt(t_f, 3)} s" if I < Iinst_sec else ""))
verifica_adevarat("L1: 0,9·I>> rămâne sub prag, 1,2·I>> îl depășește", 0.9 * Iinst_sec < Iinst_sec < 1.2 * Iinst_sec)

print("\nL2 – verificarea TC (400/1 A, 5P20, 5 VA)")
# date măsurate de exemplu (pentru ilustrarea calculului; în laborator se folosesc valorile măsurate)
Rct_mas, Rb_mas = 1.5, 0.242
ALF_ef = 20 * (1.5 + 5.0) / (Rct_mas + Rb_mas)
E_ALF = 20 * 1.0 * (1.5 + 5.0)
print(f"  cu Rct = {fmt(Rct_mas, 2)} Ω și Rb = {fmt(Rb_mas, 3)} Ω măsurate: ALF_ef = {fmt(ALF_ef, 1)} "
      f"(problema 2.1); t.e.m. la limita de precizie ≈ {fmt(E_ALF, 0)} V")
verifica("L2: ALF_ef ca în problema 2.1", ALF_ef, 74.6, rtol=1e-3)
for Ip in (100.0, 200.0, 400.0):
    print(f"  injecție primară {fmt(Ip, 0)} A → curent secundar așteptat {fmt(Ip / 400, 3)} A")
