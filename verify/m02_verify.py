"""Verificarea independentă a motorului din modulul 02 (transformatorul de curent).

1) Dimensionarea: sarcina, F_a, verificările — recalculate din formule.
2) Regimul tranzitoriu: ecuația TC integrată din nou cu scipy (Radau, metodă implicită de ordin 5),
   cu aceeași curbă de magnetizare; se compară curentul secundar cu cel din motor (Euler înapoi).
3) Timpul până la saturație: formula IEEE C37.110 față de momentul în care fluxul „ideal”
   (fără curent de magnetizare) atinge fluxul limită — calculat numeric pentru mai multe X/R și K_s.
4) Calibrarea curbei: eroarea compusă la ALF pe sarcina nominală ≈ 5 % (5P) și ≈ 10 % (10P).
5) Filtrul Fourier: pe o sinusoidă nesaturată dă exact valoarea efectivă după o perioadă.

Rulare: python3 verify/m02_verify.py
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
ENG = (ROOT / "site/m02/engine.js").as_posix()
W = 2 * math.pi * 50


def js(code):
    return json.loads(subprocess.run(["node", "-e", f"const M=require('{ENG}');" + code], capture_output=True, text=True, check=True).stdout)


bad = 0
data = js("""const p=M.DEFAULTS,c=M.context(p),s=M.sizing(p,c),mg=M.magnet(p);
const sim=M.simulate(p,c);const d=M.dft(sim);
console.log(JSON.stringify({p,c,s,mg:{a:mg.a,b:mg.b,n:mg.n,lamAl:mg.lamAl,Eal:mg.Eal,Ek:mg.Ek},sim:{t:sim.t,i2:sim.i2,i1:sim.i1,tSat:sim.tSat,R:sim.R,n:sim.n},d}));""")
p, c, s, mg = data["p"], data["c"], data["s"], data["mg"]

# [1] dimensionare -------------------------------------------------------
Rbn = p["Sn"] / p["Isn"] ** 2
Rl = 0.0175 * p["lead"] / p["leadA"]
Rr = p["Srelay"] / p["Isn"] ** 2
Fa1 = p["alf"] * (p["Rct"] + Rbn) / (p["Rct"] + Rl + Rr)
Fa2 = p["alf"] * (p["Rct"] + Rbn) / (p["Rct"] + 2 * Rl + Rr)
for name, a, b in (("R_b (3F)", Rl + Rr, s["Rb1"]), ("F_a (3F)", Fa1, s["Fa1"]), ("F_a (nesimetric)", Fa2, s["Fa2"]),
                   ("20·I>/I_pn", 20 * c["Is"] / p["Ipn"], s["needIDMT"]), ("I>>/I_pn", c["Ih"] / p["Ipn"], s["needHigh"]),
                   ("I″k/I_pn", c["If"] / p["Ipn"], s["kF"]), ("E_al", p["alf"] * p["Isn"] * (p["Rct"] + Rbn), s["Eal"])):
    ok = abs(a - b) <= 1e-9 * max(1, abs(a))
    bad += not ok
    print(f"[1] {name}: {b:.4f} (recalculat {a:.4f}) {'✓' if ok else '✗'}")

# [2] tranzitoriu cu scipy ----------------------------------------------
a_, b_, n_ = mg["a"], mg["b"], mg["n"]
im = lambda l: a_ * l + b_ * np.sign(l) * np.abs(l) ** n_
dim = lambda l: a_ + b_ * n_ * np.abs(l) ** (n_ - 1)
R = data["sim"]["R"]
nr = data["sim"]["n"]
If, xr = c["If"], c["xr"]
T1 = xr / W
ipk = math.sqrt(2) * If
i1 = lambda t: ipk * (-math.cos(W * t) + math.exp(-t / T1))
f = lambda t, y: [R * (i1(t) / nr - im(y[0]))]
jac = lambda t, y: [[-R * dim(y[0])]]
t = np.array(data["sim"]["t"])
sol = solve_ivp(f, (0, t[-1]), [p["rem"] * mg["lamAl"]], method="Radau", t_eval=t, jac=jac, rtol=1e-9, atol=1e-12, max_step=2e-4)
i2_py = np.array([i1(tt) / nr for tt in t]) - im(sol.y[0])
i2_js = np.array(data["sim"]["i2"])
peak = ipk / nr
err = np.max(np.abs(i2_py - i2_js)) / peak
rms = math.sqrt(np.mean((i2_py - i2_js) ** 2)) / peak
ok = rms < 0.01 and err < 0.05
bad += not ok
print(f"[2] curent secundar, motor (Euler înapoi, dt = {p['dt']*1e6:.0f} µs) vs scipy Radau: abatere RMS {100*rms:.3f} % din vârf, maximă {100*err:.2f} % {'✓' if ok else '✗'}")
lam_py = sol.y[0]
idx = np.argmax(np.abs(lam_py) >= mg["lamAl"])
tsat_py = t[idx] if np.abs(lam_py[idx]) >= mg["lamAl"] else None
ok = tsat_py is not None and abs(tsat_py - data["sim"]["tSat"]) <= 2 * p["dt"] + 1e-12
bad += not ok
print(f"[2] fluxul atinge λ_al: motor {data['sim']['tSat']*1000:.2f} ms, scipy {tsat_py*1000:.2f} ms {'✓' if ok else '✗'}")

# [3] formula timpului până la saturație --------------------------------
print("[3] formula IEEE C37.110 vs fluxul ideal integrat numeric:")
worst = 0
for xr_ in (5, 10, 20, 40):
    for Ks in (1.5, 3, 6, 12):
        if Ks >= 1 + xr_:
            continue
        T = xr_ / W
        tt = np.linspace(0, 0.5, 200001)
        # flux ideal (în unități ale vârfului fluxului simetric): integrala curentului complet asimetric
        lam = xr_ * (1 - np.exp(-tt / T)) - np.sin(W * tt)
        k = np.argmax(lam >= Ks)
        t_num = tt[k] if lam[k] >= Ks else math.inf
        t_for = js(f"console.log(JSON.stringify(M.timeToSat({Ks},{xr_})))")
        d = abs(t_num - t_for)
        worst = max(worst, d)
        print(f"     X/R = {xr_:2d}, K_s = {Ks:4.1f}: formula {t_for*1000:6.2f} ms, numeric {t_num*1000:6.2f} ms, diferență {d*1000:5.2f} ms")
ok = worst <= 0.0101   # anvelopa ignoră termenul sinusoidal: diferența rămâne sub o jumătate de perioadă
bad += not ok
print(f"[3] diferența maximă {worst*1000:.2f} ms (sub o jumătate de perioadă, 10 ms) {'✓' if ok else '✗'}")

# [4] calibrarea curbei ---------------------------------------------------
for cls, target in (("5P", 0.05), ("10P", 0.10)):
    e = js(f"const p={{...M.DEFAULTS,cls:'{cls}'}};console.log(JSON.stringify(M.compositeError(p,p.alf,p.Sn/p.Isn**2)))")
    ok = abs(e - target) <= 0.01
    bad += not ok
    print(f"[4] {cls}: eroarea compusă la ALF, sarcina nominală = {100*e:.2f} % (ținta {100*target:.0f} %) {'✓' if ok else '✗'}")

# [5] filtrul Fourier -----------------------------------------------------
d5 = js("""const p={...M.DEFAULTS};const c={If:300,xr:10};const sim=M.simulate(p,c,{offset:0,If:300,Rb:0.45});const d=M.dft(sim);
console.log(JSON.stringify(d.I.slice(-50)));""")
exp = 300 / 300  # 1 A secundar efectiv
dev = max(abs(v - exp) for v in d5) / exp
ok = dev < 0.01
bad += not ok
print(f"[5] filtrul Fourier pe sinusoidă de 1 A efectiv (fără saturație): abatere maximă {100*dev:.3f} % {'✓' if ok else '✗'}")

print("\nREZULTAT:", "TOATE VERIFICĂRILE AU TRECUT" if bad == 0 else f"{bad} ABATERI")
sys.exit(1 if bad else 0)
