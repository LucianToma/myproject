"""Verificarea independentă a motorului din modulul 03 (protecția maximală de curent).

1) Curbele: formulele IEC 60255-151 / IEEE C37.112 rescrise aici, comparate cu motorul pe o grilă de multipli,
   plus valorile de referință cunoscute la 10·I_s (SI 2,97 s; VI 1,50 s; EI 0,808 s; LTI 13,3 s).
2) Reglajele automate: curentul de pornire, sensibilitatea, I>> și reach-ul recalculate cu curenții
   de scurtcircuit din pandapower (IEC 60909-0), nu din motorul paginii.
3) Selectivitatea: pentru defecte 3F și 2F, regim maxim și minim, la fiecare 0,25 km pe linie și pe bare,
   se calculează timpii tuturor releelor și se verifică (a) că declanșează primul releul cel mai apropiat
   din amonte și (b) că următorul releu are marja de cel puțin CTI.
4) Minimalitatea TMS: scăzând TMS-ul unui releu cu 0,01, apare o încălcare a marjei (sau TMS e deja minim).

Rulare: python3 verify/m03_verify.py
"""
import json
import math
import subprocess
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]

CURVES = {
    "IEC-SI": ("IEC", 0.14, 0.02, 0.0), "IEC-VI": ("IEC", 13.5, 1.0, 0.0), "IEC-EI": ("IEC", 80.0, 2.0, 0.0), "IEC-LTI": ("IEC", 120.0, 1.0, 0.0),
    "IEEE-MI": ("IEEE", 0.0515, 0.02, 0.114), "IEEE-VI": ("IEEE", 19.61, 2.0, 0.491), "IEEE-EI": ("IEEE", 28.2, 2.0, 0.1217),
}


def t_curve(curve, M):
    fam, k, a, b = CURVES[curve]
    M = min(M, 20.0)
    return k / (M ** a - 1) + b


def trip(s, I, t_own):
    t = math.inf
    if s["Is"] > 0:
        M = I / s["Is"]
        if s["curve"] == "DT":
            if M >= 1:
                t = max(s["tms"], t_own)
        elif M >= 1.1:
            t = max(s["tms"] * t_curve(s["curve"], M), t_own)
    if s["Ih"] > 0 and I >= s["Ih"]:
        t = min(t, max(s["th"], t_own))
    return t


def js(code):
    return json.loads(subprocess.run(["node", "-e", code], capture_output=True, text=True, check=True).stdout)


ENG = (ROOT / "site/m03/engine.js").as_posix()
bad = 0

# [1] curbe -------------------------------------------------------------
Ms = [1.15, 1.5, 2, 3, 5, 7.5, 10, 15, 20, 30]
jt = js(f"const M=require('{ENG}');const o={{}};for(const c of Object.keys(M.CURVES)){{if(c==='DT')continue;o[c]={json.dumps(Ms)}.map(m=>M.curveTime(c,m));}}console.log(JSON.stringify(o));")
worst = 0
for c, vals in jt.items():
    for m, v in zip(Ms, vals):
        worst = max(worst, abs(v - t_curve(c, m)) / t_curve(c, m))
ref = {"IEC-SI": 2.97, "IEC-VI": 1.50, "IEC-EI": 0.808, "IEC-LTI": 13.33,
       # valorile IEEE din tabelul paginii (tab-ul Teorie), recalculate aici
       "IEEE-MI": 1.21, "IEEE-VI": 0.689, "IEEE-EI": 0.407}
for c, r in ref.items():
    v = t_curve(c, 10)
    ok = abs(v - r) / r < 0.005
    bad += not ok
    print(f"[1] {c} la 10·I_s, TMS = 1: {v:.3f} s (referință {r} s) {'✓' if ok else '✗'}")
print(f"[1] motor vs formule, {len(jt)} curbe × {len(Ms)} multipli: abatere maximă {worst:.1e}")
bad += worst > 1e-12

# [2] reglaje automate --------------------------------------------------
out = js(f"const M=require('{ENG}');const d=M.DEFAULTS,n=M.NET;const a=M.autoSettings(n,d);console.log(JSON.stringify({{a,d,n,coord:M.coordination(n,d,a.S)}}));")
A, D, N = out["a"], out["d"], out["n"]
S = A["S"]

import pandapower as pp
import pandapower.shortcircuit as sc

net = pp.create_empty_network()
b110 = pp.create_bus(net, 110)
b20 = pp.create_bus(net, 20)
pp.create_ext_grid(net, b110, s_sc_max_mva=N["SkQmax"], s_sc_min_mva=N["SkQmin"], rx_max=N["rxQ"], rx_min=N["rxQ"])
pp.create_transformer(net, b110, b20, std_type="25 MVA 110/20 kV")
step = 0.25
xs = [round(i * step, 4) for i in range(1, int(N["L"] / step) + 1)]
bus_at = {0.0: b20}
prev, last = b20, 0.0
for x in xs:
    nb = pp.create_bus(net, 20)
    pp.create_line_from_parameters(net, prev, nb, x - last, r_ohm_per_km=N["R1"], x_ohm_per_km=N["X1"], c_nf_per_km=0, max_i_ka=1, endtemp_degree=N["thetaE"])
    bus_at[x] = nb
    prev, last = nb, x
I = {}
for case in ("max", "min"):
    for fault in ("3ph", "2ph"):
        sc.calc_sc(net, case=case, fault=fault)
        I[(case, fault)] = {x: net.res_bus_sc.ikss_ka[b] * 1000 for x, b in bus_at.items()}
sc.calc_sc(net, case="max", fault="3ph")
Ihv_bus = net.res_bus_sc.ikss_ka[b110] * 1000

Ir_lv = N["Sr"] * 1e6 / (math.sqrt(3) * N["UrLV"] * 1e3)
Ir_hv = N["Sr"] * 1e6 / (math.sqrt(3) * N["UrHV"] * 1e3)
load = {"R4": D["R4"]["Iload"], "R3": D["R3"]["Iload"], "R2": Ir_lv, "R1": Ir_hv}
k = N["UrLV"] / N["UrHV"]
grade_ratio = {"R3": 1.0, "R2": 1.0, "R1": k * 2 / math.sqrt(3)}   # față de releul din aval
prev_Is = None
for r in ("R4", "R3", "R2", "R1"):
    raw = D["kSig"] * D["kP"] * load[r] / D["kRev"]
    st = D[r]["ct"] * 0.01
    Is = math.ceil(raw / st - 1e-9) * st
    note = ""
    if prev_Is is not None and prev_Is * grade_ratio[r] > Is + 1e-9:
        Is = math.ceil(prev_Is * grade_ratio[r] / st - 1e-9) * st
        note = " — ridicat de eșalonarea pragurilor"
    prev_Is = Is
    ok = abs(Is - S[r]["Is"]) < 1e-9
    bad += not ok
    print(f"[2] {r}: I> = {S[r]['Is']:.2f} A (recalculat {Is:.2f} A, regula de sarcină dă {raw:.2f} A{note}) {'✓' if ok else '✗'}")

hv2min_bus = I[("min", "2ph")][0.0] * k * 2 / math.sqrt(3)
checks = [
    ("R4 sens. capăt linie", I[("min", "2ph")][N["L"]] / S["R4"]["Is"], A["rep"]["R4"]["sensMain"]["k"]),
    ("R3 sens. la R4", I[("min", "2ph")][D["x4"]] / S["R3"]["Is"], A["rep"]["R3"]["sensMain"]["k"]),
    ("R3 sens. capăt linie", I[("min", "2ph")][N["L"]] / S["R3"]["Is"], A["rep"]["R3"]["sensBack"]["k"]),
    ("R2 sens. bare", I[("min", "2ph")][0.0] / S["R2"]["Is"], A["rep"]["R2"]["sensMain"]["k"]),
    ("R1 sens. bare 20 kV (2F, max pe faze ÎT)", hv2min_bus / S["R1"]["Is"], A["rep"]["R1"]["sensMain"]["k"]),
    ("R3 I>> bază = I″k3 max la R4", I[("max", "3ph")][D["x4"]], A["rep"]["R3"]["IhBase"]),
    ("R1 I>> bază = I″k3 max bare 20 kV pe ÎT", I[("max", "3ph")][0.0] * k, A["rep"]["R1"]["IhBase"]),
]
for name, py, jv in checks:
    ok = abs(py - jv) <= 1e-4 * abs(py)
    bad += not ok
    print(f"[2] {name}: pandapower {py:.3f}, motor {jv:.3f} {'✓' if ok else '✗'}")
# reach-ul treptei I>> din R3 (interpolare pe grila pandapower)
ih = S["R3"]["Ih"]
xr = max([x for x, v in I[("max", "3ph")].items() if v >= ih], default=0.0)
okr = abs(xr - A["rep"]["R3"]["reach"]) <= step
bad += not okr
print(f"[2] R3 I>> = {ih:.0f} A ajunge până la {A['rep']['R3']['reach']:.2f} km (grila pandapower: între {xr:.2f} și {xr+step:.2f} km) {'✓' if okr else '✗'}")

# [3] selectivitate pe scenarii fizice ----------------------------------
CTI, TOWN = D["cti"], D["tOwn"]


def scenario_times(Sx, case, fault, loc):
    """loc: 'B20' sau x km. Întoarce timpii releelor care văd defectul."""
    x = 0.0 if loc == "B20" else loc
    If = I[(case, fault)][x]
    Ih = If * k * (2 / math.sqrt(3) if fault == "2ph" else 1.0)
    seen = {"R2": If, "R1": Ih}
    if loc != "B20":
        seen["R3"] = If
        if x >= D["x4"]:
            seen["R4"] = If
    return {r: trip(Sx[r], i, TOWN) for r, i in seen.items()}


def check_all(Sx, verbose=False):
    viol = []
    order = ["R4", "R3", "R2", "R1"]
    for case in ("max", "min"):
        for fault in ("3ph", "2ph"):
            for loc in ["B20"] + [0.0] + xs:
                T = scenario_times(Sx, case, fault, loc)
                chain = [r for r in order if r in T]
                first = min(T, key=T.get)
                if not math.isfinite(T[first]):
                    viol.append((case, fault, loc, "niciun releu nu acționează"))
                    continue
                if T[chain[0]] == math.inf:
                    # releul principal nu vede defectul: trebuie să acționeze rezerva
                    continue
                if first != chain[0] and T[first] < T[chain[0]] - 1e-9:
                    viol.append((case, fault, loc, f"{first} înaintea lui {chain[0]}"))
                for dn, up in zip(chain, chain[1:]):
                    if math.isfinite(T[dn]) and T[up] - T[dn] < CTI - 1e-6:
                        viol.append((case, fault, loc, f"marja {dn}–{up} = {T[up]-T[dn]:.3f} s"))
    return viol


viol = check_all(S)
n_sc = 4 * (len(xs) + 2)
print(f"[3] {n_sc} scenarii de defect (3F/2F, max/min, bare + linie la fiecare {step} km): {len(viol)} încălcări")
for v in viol[:8]:
    print("    ", v)
bad += len(viol) > 0
# eșalonarea pragurilor, recalculată independent: raportul curenților văzuți de releul din amonte și cel din aval
ratios = {("R4", "R3"): 1.0, ("R3", "R2"): 1.0, ("R2", "R1"): k * 2 / math.sqrt(3)}
for (dn, up), rt in ratios.items():
    ok = S[up]["Is"] / rt >= S[dn]["Is"] * (1 - 1e-9)
    bad += not ok
    print(f"[3] prag {up} raportat = {S[up]['Is']/rt:.1f} A ≥ prag {dn} = {S[dn]['Is']:.1f} A {'✓' if ok else '✗'}")
# comparație cu verificarea internă a motorului
for pair, r in out["coord"].items():
    print(f"[3] motor: marja minimă {pair} = {r['margin']:.3f} s {'✓' if r['ok'] else '✗'}")
    bad += not r["ok"]

# [4] minimalitatea TMS -------------------------------------------------
for r in ("R3", "R2", "R1"):
    if S[r]["tms"] <= D["tmsMin"] + 1e-9:
        print(f"[4] {r}: TMS = {S[r]['tms']:.2f} (minimul permis)")
        continue
    S2 = json.loads(json.dumps(S))
    S2[r]["tms"] = round(S[r]["tms"] - 0.01, 2)
    v2 = check_all(S2)
    ok = len(v2) > 0
    # motorul baleiază și curenții intermediari (defecte rezistive); dacă scenariile fizice nu găsesc încălcare,
    # verificăm direct baleierea motorului
    if not ok:
        r2 = js(f"const M=require('{ENG}');const S={json.dumps(S2)};console.log(JSON.stringify(M.coordination(M.NET,M.DEFAULTS,S)));")
        ok = any(not x["ok"] for x in r2.values())
    bad += not ok
    print(f"[4] {r}: TMS = {S[r]['tms']:.2f}; cu {S2[r]['tms']:.2f} apare încălcarea marjei: {'da ✓' if ok else 'nu ✗'}")

print("\nREZULTAT:", "TOATE VERIFICĂRILE AU TRECUT" if bad == 0 else f"{bad} ABATERI")
sys.exit(1 if bad else 0)
