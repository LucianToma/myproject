"""Verificarea independentă a motorului din modulul 01.

1) Pentru toate tipurile de defect, toate tratările neutrului, toate tipurile de linie, ambele cazuri (max/min),
   trei poziții și două rezistențe de defect: soluție NODALĂ ÎN COORDONATE DE FAZĂ (abc), fără formulele
   de conectare a rețelelor de secvență folosite în pagină. Se compară curenții și tensiunile pe faze.
2) Curenții 3F (max) și 2F (min) la bare și pe linie: pandapower (implementare IEC 60909-0).
3) Curenții pe partea de 110 kV pentru defecte pe 20 kV: tiparul 1-1-2 (2F) și 1-1-0 (1F) din literatură.

Rulare: python3 verify/m01_verify.py   (cere node, numpy, pandapower)
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
raw = subprocess.run(["node", str(ROOT / "verify/m01_engine_dump.cjs")], capture_output=True, text=True, check=True).stdout
data = json.loads(raw)
cases, last = data[:-1], data[-1]
W = 2 * math.pi * 50
S3 = math.sqrt(3)
a = np.exp(2j * math.pi / 3)


def zsrc(p, kase):
    """Impedanța sursei (rețea + T1) raportată la 20 kV — scrisă din nou, direct din IEC 60909-0."""
    c = p["cmax"] if kase == "max" else p["cmin"]
    Sk = p["SkQmax"] if kase == "max" else p["SkQmin"]
    ZQ = c * p["UnQ"] ** 2 / Sk
    XQ = ZQ / math.sqrt(1 + p["rxQ"] ** 2)
    zQ = complex(p["rxQ"] * XQ, XQ) / (p["UrHV"] / p["UrLV"]) ** 2
    ZT = p["uk"] / 100 * p["UrLV"] ** 2 / p["Sr"]
    RT = p["Pk"] / 1000 * p["UrLV"] ** 2 / p["Sr"] ** 2
    XT = math.sqrt(ZT ** 2 - RT ** 2)
    KT = 0.95 * p["cmax"] / (1 + 0.6 * XT / (p["UrLV"] ** 2 / p["Sr"])) if kase == "max" else 1.0
    return zQ + KT * complex(RT, XT), c


def y_neutral(p):
    """Admitanța homopolară a echipamentului de tratare a neutrului (fără capacități)."""
    Uph = p["Un"] * 1000 / S3
    n = p["neutral"]
    if n == "R":
        return 1 / complex(3 * Uph / p["Ilim"], p["Z0bpn"])
    if n == "L":
        IL = p["Ic"] * (1 + p["v"])
        return 1 / complex(0, p["Z0bpn"] + 3 * Uph / IL) + p["d"] * p["Ic"] / (3 * Uph)
    if n == "S":
        return 1 / complex(0, p["Z0bpn"])
    return 0j


def solve_abc(c, cap_pos_seq=False):
    p, kase, typ, x, Rf = c["p"], c["kase"], c["type"], c["x"], c["Rf"]
    zs, cf = zsrc(p, kase)
    Uph = p["Un"] * 1000 / S3
    E = cf * p["Un"] * 1000 / S3 * np.array([1, a ** 2, a])
    kth = 1 + 0.004 * (p["thetaE"] - 20) if kase == "min" else 1.0
    z1 = complex(p["R1"] * kth, p["X1"]) * x
    z0 = complex(p["R0"] * kth, p["X0"]) * x
    # noduri: 0-2 bare B (a,b,c), 3-5 defect F, 6 steaua sursei S (izolată), 7 punctul comun P al defectului
    n = 8
    Y = np.zeros((n, n), dtype=complex)
    I = np.zeros(n, dtype=complex)

    def branch(i, j, y):
        Y[i, i] += y
        if j is not None:
            Y[j, j] += y
            Y[i, j] -= y
            Y[j, i] -= y

    # sursă: E_k în serie cu z_s, între S și B_k (echivalent Norton)
    for k in range(3):
        y = 1 / zs
        branch(k, 6, y)
        I[k] += E[k] * y
        I[6] -= E[k] * y
    # tratarea neutrului: element numai homopolar, Y = y0N/3·J (fazele B → pământ)
    y0N = y_neutral(p)
    Y[0:3, 0:3] += y0N / 3 * np.ones((3, 3))
    # capacitățile homopolare: jωC0 pe fiecare fază față de pământ
    if p["Ic"] > 0:
        yC = 1j * p["Ic"] / (3 * Uph)
        # modelul paginii: capacitățile numai în secvența zero (Y0 = jωC0, Y1 = Y2 = 0 → yC/3·J);
        # varianta fizică completă (fiecare fază la pământ) se folosește doar pentru a cuantifica ipoteza
        Y[0:3, 0:3] += (np.eye(3) * yC) if cap_pos_seq else (yC / 3 * np.ones((3, 3)))
    # linia B–F, matrice de fază cu impedanțe proprii și mutuale
    if x > 0:
        Zs_, Zm_ = (z0 + 2 * z1) / 3, (z0 - z1) / 3
        Zabc = np.full((3, 3), Zm_) + np.eye(3) * (Zs_ - Zm_)
        Yl = np.linalg.inv(Zabc)
        Y[0:3, 0:3] += Yl
        Y[3:6, 3:6] += Yl
        Y[0:3, 3:6] -= Yl
        Y[3:6, 0:3] -= Yl
    shorts = []  # legături ideale (0 Ω), rezolvate exact prin analiza nodală modificată
    if x == 0:
        shorts += [(k, 3 + k) for k in range(3)]
    f = [3, 4, 5]
    fault_br = []   # (i, j, y) ramuri rezistive ale defectului
    fault_sh = []   # indicii legăturilor ideale care aparțin defectului

    def conn(i, j):
        """Rezistența de defect R_f între i și j; legătură ideală dacă R_f = 0."""
        if Rf > 0:
            branch(i, j, 1 / Rf)
            fault_br.append((i, j, 1 / Rf))
        else:
            fault_sh.append(len(shorts))
            shorts.append((i, j))

    if typ == "3F":
        for k in range(3):
            conn(f[k], 7)
    elif typ == "2F":
        conn(f[1], f[2])
    elif typ == "1F":
        conn(f[0], None)
    elif typ == "2FE":
        fault_sh.append(len(shorts)); shorts.append((f[1], 7))
        fault_sh.append(len(shorts)); shorts.append((f[2], 7))
        if Rf > 0:
            branch(7, None, 1 / Rf)
        else:
            shorts.append((7, None))
    Y[7, 7] += 1e-12   # nodul P, dacă nu e folosit
    m = len(shorts)
    M_ = np.zeros((n + m, n + m), dtype=complex)
    M_[:n, :n] = Y
    rhs = np.concatenate([I, np.zeros(m, dtype=complex)])
    for k, (i, j) in enumerate(shorts):
        M_[i, n + k] += 1; M_[n + k, i] = 1
        if j is not None:
            M_[j, n + k] -= 1; M_[n + k, j] = -1
    sol = np.linalg.solve(M_, rhs)
    V = sol[:n]
    If = np.zeros(3, dtype=complex)
    items = [(i, j, (V[i] - (V[j] if j is not None else 0)) * y) for (i, j, y) in fault_br]
    items += [(shorts[k][0], shorts[k][1], sol[n + k]) for k in fault_sh]
    for (i, j, cur) in items:
        If[i - 3] += cur
        if j is not None and 3 <= j <= 5:   # ramură între două faze (2F): curentul iese din faza j
            If[j - 3] -= cur
    return If, V[3:6]


def cmp(a_, b_, tol_rel=2e-4, tol_abs=1e-3):
    return abs(a_ - b_) <= max(tol_rel * max(abs(a_), abs(b_)), tol_abs)


bad = 0
worst = 0.0
for c in cases:
    If, Vf = solve_abc(c)
    Ij = np.array([complex(*z) for z in c["Iabc"]])
    Vj = np.array([complex(*z) for z in c["Vabc"]])
    for k in range(3):
        for A_, B_ in ((If[k], Ij[k]), (Vf[k], Vj[k])):
            d = abs(A_ - B_) / max(abs(A_), abs(B_), 1.0)
            worst = max(worst, d)
            if not cmp(A_, B_, tol_abs=0.01):
                bad += 1
                if bad < 6:
                    print("ABATERE", c["p"]["neutral"], c["p"]["line"], c["kase"], c["type"], c["x"], c["Rf"], k, A_, B_)
print(f"[1] soluție nodală abc vs motor: {len(cases)} cazuri × 3 faze × (I, U): {bad} abateri; abaterea relativă maximă {worst:.2e}")
# efectul ipotezei „capacități neglijate în secvența pozitivă/negativă” (IEC 60909-0): cât schimbă curenții de defect
eff = 0.0
for c in cases:
    if c["p"]["neutral"] in ("R", "S"):
        If1, _ = solve_abc(c)
        If2, _ = solve_abc(c, cap_pos_seq=True)
        m = max(abs(If1))
        eff = max(eff, max(abs(If1 - If2)) / m)
print(f"[1b] efectul capacităților în secvența pozitivă asupra curenților de defect (neutru R/S): max {100*eff:.2f} %")

# [2] pandapower -------------------------------------------------------
import pandapower as pp
import pandapower.shortcircuit as sc
import warnings
warnings.filterwarnings("ignore")

p = last["p"]
bad2 = 0
for line in ("ol70", "cab185"):
    net = pp.create_empty_network()
    b110 = pp.create_bus(net, 110)
    b20 = pp.create_bus(net, 20)
    pp.create_ext_grid(net, b110, s_sc_max_mva=p["SkQmax"], s_sc_min_mva=p["SkQmin"], rx_max=p["rxQ"], rx_min=p["rxQ"])
    pp.create_transformer(net, b110, b20, std_type="25 MVA 110/20 kV")
    L = {"ol70": (0.4132, 0.36), "cab185": (0.161, 0.117)}[line]
    prev = b20
    xs = [5.0, 10.0, 15.0, 20.0]
    buses = {0.0: b20}
    last_x = 0.0
    for xx in xs:
        nb = pp.create_bus(net, 20)
        pp.create_line_from_parameters(net, prev, nb, xx - last_x, r_ohm_per_km=L[0], x_ohm_per_km=L[1], c_nf_per_km=0, max_i_ka=1, endtemp_degree=p["thetaE"])
        buses[xx] = nb
        prev, last_x = nb, xx
    sc.calc_sc(net, case="max", fault="3ph")
    r3 = net.res_bus_sc.ikss_ka.copy()
    sc.calc_sc(net, case="min", fault="2ph")
    r2 = net.res_bus_sc.ikss_ka.copy()
    # motorul, cu aceeași linie (fără secvență zero, nu contează pentru 3F/2F)
    for xx, bus in buses.items():
        pj = dict(p, line=line, R1=L[0], X1=L[1])
        out = json.loads(subprocess.run(["node", "-e", f"""
const M=require('{(ROOT/'site/m01/engine.js').as_posix()}');
const p={json.dumps(pj)};
console.log(JSON.stringify([M.compute(p,'max','3F',{xx},0).Ik, M.compute(p,'min','2F',{xx},0).Ik]));
"""], capture_output=True, text=True, check=True).stdout)
        pp3, pp2 = r3[bus] * 1000, r2[bus] * 1000
        ok3, ok2 = cmp(pp3, out[0], 1e-4), cmp(pp2, out[1], 1e-4)
        bad2 += (not ok3) + (not ok2)
        print(f"[2] {line:6s} x = {xx:4.1f} km  I″k3 max: pandapower {pp3:8.1f} A, motor {out[0]:8.1f} A {'✓' if ok3 else '✗'} | I″k2 min: pandapower {pp2:8.1f} A, motor {out[1]:8.1f} A {'✓' if ok2 else '✗'}")
# barele de 110 kV
hv = last["hv"]
print(f"[2] bare 110 kV: I″k3 max = {hv['max']['Ik3']:.1f} kA (= S″kQ/(√3·U_nQ) = {p['SkQmax']/(S3*p['UnQ']):.1f}), min = {hv['min']['Ik3']:.1f} kA")

# [3] curenții pe 110 kV ------------------------------------------------
bad3 = 0
for c in cases:
    if c["x"] != 7.5 or c["Rf"] != 0 or c["kase"] != "max" or c["p"]["line"] != "ol70":
        continue
    Ih = sorted(abs(complex(*z)) for z in c["Ihv"])
    k = c["p"]["UrLV"] / c["p"]["UrHV"]
    if c["type"] == "2F":
        # 1-1-2: cel mai mare = 2/√3·I2F·k = I3F·k
        Ik2 = c["Ik"]
        exp = [Ik2 * k / S3, Ik2 * k / S3, 2 * Ik2 * k / S3]
    elif c["type"] == "1F" and c["p"]["neutral"] in ("R", "S"):
        Ik1 = c["Ik"]
        exp = [0.0, Ik1 * k / S3, Ik1 * k / S3]
    else:
        continue
    ok = all(abs(u - v) < 1e-6 * max(1, v) for u, v in zip(Ih, sorted(exp)))
    bad3 += not ok
    print(f"[3] {c['type']:3s} neutru {c['p']['neutral']}: curenți 110 kV {[round(v,2) for v in Ih]} A, așteptat {[round(v,2) for v in sorted(exp)]} {'✓' if ok else '✗'}")

total = bad + bad2 + bad3
print("\nREZULTAT:", "TOATE VERIFICĂRILE AU TRECUT" if total == 0 else f"{total} ABATERI")
sys.exit(1 if total else 0)
