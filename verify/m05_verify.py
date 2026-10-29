"""Verificarea independentă a motorului din modulul 05 (punerea la pământ în rețelele MT).

1) Capacitatea homopolară a LEA din geometria folosită în M01 (coeficienți de potențial, metoda imaginilor),
   cu verificarea C1 față de valoarea din biblioteca pandapower.
2) Pentru fiecare tratare a neutrului (izolat, compensat, rezistor), defect pe fiecare plecare, trei poziții și
   cinci rezistențe de defect: analiză nodală în coordonate de fază (sursa cu stea izolată, neutrul ca element
   numai homopolar, capacitățile plecărilor, linia defectă ca matrice 3×3); se compară U0 și 3I0 pe fiecare plecare.
3) Relații de control: în rețeaua izolată plecarea defectă vede curentul capacitiv al celorlalte plecări,
   în urma lui U0 cu 90° (conduce −3U0 cu 90°); U0/Uf ≈ 1/|1 + 3R_f·Y0| (relația din pagină).
4) Reglajele automate recalculate (51N, 67N, sin φ, cos φ, admitanță) și absența declanșărilor simpatice.

Rulare: python3 verify/m05_verify.py
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ENG = (ROOT / "site/m05/engine.js").as_posix()
W = 2 * math.pi * 50
a = np.exp(2j * math.pi / 3)
A = np.array([[1, 1, 1], [1, a * a, a], [1, a, a * a]])
Ainv = np.linalg.inv(A)
bad = 0


def js(code):
    return json.loads(subprocess.run(["node", "-e", f"const M=require('{ENG}');" + code], capture_output=True, text=True, check=True).stdout)


cz = lambda z: complex(z["re"], z["im"])

# [1] capacitatea LEA -----------------------------------------------------
eps0 = 8.854187817e-12


def line_caps(r, gmd, h=10.0):
    pos = [(-gmd / 2, h), (gmd / 2, h), (0.0, h + gmd * math.sqrt(3) / 2)]
    P = np.zeros((3, 3))
    for i, (xi, yi) in enumerate(pos):
        for j, (xj, yj) in enumerate(pos):
            if i == j:
                P[i, j] = math.log(2 * yi / r) / (2 * math.pi * eps0)
            else:
                P[i, j] = math.log(math.hypot(xi - xj, yi + yj) / math.hypot(xi - xj, yi - yj)) / (2 * math.pi * eps0)
    Cs = Ainv @ np.linalg.inv(P) @ A
    return Cs[0, 0].real * 1e3, Cs[1, 1].real * 1e3   # F/km


# raza și distanța medie geometrică din verify/m01_line_params.py (reproduc X1 = 0,36 Ω/km)
r70, gmr = 11.7e-3 / 2, 0.809 * 11.7e-3 / 2
gmd = gmr * math.exp(0.36 / (W * 2e-4))
c0, c1 = line_caps(r70, gmd)
eng_c0 = js("console.log(JSON.stringify(M.TYPES.ol70.C0))")
ok = abs(c0 - eng_c0) / c0 < 0.005 and abs(c1 - 9.7e-9) / 9.7e-9 < 0.06
bad += not ok
print(f"[1] LEA 70/12: C0 = {c0*1e9:.2f} nF/km (motor {eng_c0*1e9:.2f}), C1 = {c1*1e9:.2f} nF/km (pandapower 9,70; diferență {100*(c1/9.7e-9-1):+.1f} %) {'✓' if ok else '✗'}")

# [2] analiză nodală ------------------------------------------------------
cases = js("""const out=[];for(const neutral of ['I','L','R'])for(const f of M.DEFAULTS.feeders)for(const xf of [0.1,0.5,1])for(const Rf of [0,10,100,1000,5000]){
const p={...M.DEFAULTS,neutral,fault:f.id,x:f.km*xf,Rf};const r=M.compute(p);
out.push({p,E:r.E,U0:r.U0,zsrc:require('%s').source(require('%s').DEFAULTS,'max').z1bus,yN:r.ad.yN,fd:r.ad.fd.map(g=>({id:g.id,y:g.y,type:g.type,km:g.km,Ic:g.Ic})),I3:r.feeders.map(g=>g.I3),phi:r.feeders.map(g=>g.phi),u0:r.u0,IF:r.IF});}
console.log(JSON.stringify(out));""" % ((ROOT / "site/m01/engine.js").as_posix(), (ROOT / "site/m01/engine.js").as_posix()))
types = js("console.log(JSON.stringify(M.TYPES))")


def nodal(c):
    p = c["p"]
    E = cz(c["E"]) * np.array([1, a * a, a])
    zs = cz(c["zsrc"])
    # noduri: B 0-2 (bare), F 3-5 (locul defectului), S 6 (steaua sursei, izolată)
    n = 7
    Y = np.zeros((n, n), dtype=complex)
    I = np.zeros(n, dtype=complex)
    for k in range(3):
        y = 1 / zs
        Y[k, k] += y; Y[6, 6] += y; Y[k, 6] -= y; Y[6, k] -= y
        I[k] += E[k] * y; I[6] -= E[k] * y
    J = np.ones((3, 3)) / 3
    Y[0:3, 0:3] += cz(c["yN"]) * J
    for g in c["fd"]:
        Y[0:3, 0:3] += cz(g["y"]) * J
    t = types[p["feeders"][[f["id"] for f in p["feeders"]].index(p["fault"])]["type"]]
    x = p["x"]
    if x > 0:
        z1, z0 = complex(t["R1"], t["X1"]) * x, complex(t["R0"], t["X0"]) * x
        Zs_, Zm_ = (z0 + 2 * z1) / 3, (z0 - z1) / 3
        Yl = np.linalg.inv(np.full((3, 3), Zm_) + np.eye(3) * (Zs_ - Zm_))
    else:
        Yl = np.eye(3) * 1e9
    Y[0:3, 0:3] += Yl; Y[3:6, 3:6] += Yl; Y[0:3, 3:6] -= Yl; Y[3:6, 0:3] -= Yl
    shorts = []
    if p["Rf"] > 0:
        Y[3, 3] += 1 / p["Rf"]
    else:
        shorts.append(3)
    m = len(shorts)
    M_ = np.zeros((n + m, n + m), dtype=complex)
    M_[:n, :n] = Y
    for k, i in enumerate(shorts):
        M_[i, n + k] = 1; M_[n + k, i] = 1
    V = np.linalg.solve(M_, np.concatenate([I, np.zeros(m)]))[:n]
    Vb = V[0:3]
    U0 = Vb.sum() / 3
    I3 = []
    for g in c["fd"]:
        ish = (cz(g["y"]) * J) @ Vb
        tot = ish.sum()
        if g["id"] == p["fault"]:
            tot += (Yl @ (Vb - V[3:6])).sum()
        I3.append(tot)
    return U0, np.array(I3)


worst = 0
for c in cases:
    U0, I3 = nodal(c)
    I3j = np.array([cz(z) for z in c["I3"]])
    worst = max(worst, abs(U0 - cz(c["U0"])) / abs(cz(c["E"])), np.max(np.abs(I3 - I3j)) / max(1.0, np.max(np.abs(I3))))
ok = worst < 1e-6
bad += not ok
print(f"[2] {len(cases)} cazuri (3 tratări × 6 plecări × 3 poziții × 5 R_f): abaterea maximă U0 și 3I0 față de analiza nodală {worst:.1e} {'✓' if ok else '✗'}")

# [3] relații de control --------------------------------------------------
iso = [c for c in cases if c["p"]["neutral"] == "I" and c["p"]["Rf"] == 0 and abs(c["p"]["x"] - c["p"]["feeders"][0]["km"] * 0.5) < 1e-9 and c["p"]["fault"] == "F1"][0]
k = [g["id"] for g in iso["fd"]].index("F1")
IcTot = sum(g["Ic"] for g in iso["fd"])
I3 = abs(cz(iso["I3"][k]))
expect = (IcTot - iso["fd"][k]["Ic"]) * iso["u0"] * abs(cz(iso["E"])) / (20000 / math.sqrt(3))
ok = abs(I3 - expect) / expect < 0.03 and abs(iso["phi"][k] - 90) < 3 and all(abs(ph + 90) < 3 for i, ph in enumerate(iso["phi"]) if i != k)
bad += not ok
print(f"[3] izolat, defect franc pe F1: 3I0(F1) = {I3:.2f} A ≈ (I_C,tot − I_C,F1)·U0/U_n,f = {expect:.2f} A; φ(F1) = {iso['phi'][k]:.1f}° (≈ +90°), φ(sănătoase) ≈ −90° {'✓' if ok else '✗'}")
wu = 0
for c in cases:
    if c["p"]["neutral"] in ("I", "L") and c["p"]["x"] == 0.1 * [f["km"] for f in c["p"]["feeders"] if f["id"] == c["p"]["fault"]][0]:
        ua = js(f"console.log(JSON.stringify(M.u0Approx({json.dumps(c['p'])},{c['p']['Rf']})))")
        wu = max(wu, abs(ua - c["u0"]))
# relația neglijează impedanțele serie (sursa, Z1, Z2 și linia până la defect, până la 30 km de LEA):
# o folosim ca aproximare de calcul manual; cerem ca abaterea să rămână sub 2 puncte procentuale din Uf
ok = wu < 0.02
bad += not ok
print(f"[3] U0/Uf = 1/|1 + 3R_f·Y0| față de calculul complet (izolat și compensat): abatere maximă {100*wu:.2f} puncte procentuale (aproximare fără impedanțele serie) {'✓' if ok else '✗'}")

# [4] reglaje ----------------------------------------------------------------
for neutral in ("I", "L", "R"):
    s = js(f"const p={{...M.DEFAULTS,neutral:'{neutral}'}};console.log(JSON.stringify(M.autoSettings(p)))")
    fd = js(f"const p={{...M.DEFAULTS,neutral:'{neutral}'}};console.log(JSON.stringify(M.admittances(p,require('{(ROOT/'site/m01/engine.js').as_posix()}').DEFAULTS).fd))")
    for g in fd:
        exp = max(s["Imin"], math.ceil(s["kSig"] * g["Ic"]))
        ok = s["feeders"][g["id"]]["I0"] == exp
        bad += not ok
        if not ok:
            print("   51N diferit", neutral, g["id"])
    # nicio plecare sănătoasă nu declanșează, pentru defect franc pe oricare plecare (orice metodă)
    sym = js(f"""const p={{...M.DEFAULTS,neutral:'{neutral}'}};const s=M.autoSettings(p);const st={{U0start:s.U0start,rcaN:s.rcaN,feeders:s.feeders}};
let wrong=0,miss=0;for(const f of p.feeders)for(const Rf of [0,50,200]){{const r=M.compute({{...p,fault:f.id,Rf,x:f.km/2}});const d=M.decide(r,st);
d.forEach(x=>{{for(const [m,v] of Object.entries(x.d)){{if(v&&x.id!==f.id)wrong++;}}}});}}console.log(JSON.stringify({{wrong}}));""")
    ok = sym["wrong"] == 0
    bad += not ok
    print(f"[4] neutru {neutral}: pragurile 51N = max(I_min, ⌈k_sig·I_C,proprie⌉) ✓; declanșări simpatice (18 defecte × 5 metode × 5 plecări sănătoase): {sym['wrong']} {'✓' if ok else '✗'}")

print("\nREZULTAT:", "TOATE VERIFICĂRILE AU TRECUT" if bad == 0 else f"{bad} ABATERI")
sys.exit(1 if bad else 0)
