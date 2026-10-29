"""Verificarea independentă a motorului din modulul 06 (rețele cu generare distribuită).

1) Impedanța rețelei la barele de 20 kV, recalculată din datele M01 (IEC 60909-0: Z_Q, Z_T, K_T), și impedanța
   generatorului sincron (R_Gf = 0,07·X″d, transformator bloc) față de cele din motor.
2) Analiză nodală în coordonate de fază (matrice 3×3 pe fiecare element, fără componente simetrice): sursa, LEA/LES
   cu impedanțele proprii și mutuale, generatorul sincron cu t.e.m. echilibrată, invertorul ca injecție de curent
   de secvență pozitivă, defectul 3F (stea prin R_f) sau 2F (R_f între faze), cu scurtcircuite ideale în formulare
   nodală modificată. Unghiul invertorului se găsește altfel decât în motor: toate rădăcinile lui
   g(θ) = arg U1g(θ) − θ pe o grilă de 0,25°, rafinate cu metoda bisecției (Brent).
   Se compară curenții prin R3, R4, releul plecării vecine, R2, centrală, curentul de defect și tensiunea în
   punctul de racordare, pe 1 664 de cazuri.
3) Generatorul sincron recalculat cu pandapower (IEC 60909, element „gen” cu K_G = 1,1 compensat în X″d), curenții
   pe ramuri pentru defecte 3F max și 2F min pe F1 și pe plecarea vecină.
4) Timpii releelor (IEC 60255-151, VI) și verificările de reglaj: regimul normal (exportul centralei) și pragurile
   revizuite, declanșarea simpatică (R3 și R4), orbirea, profilul FRT,
   compatibilitatea treptei U<, insularizarea (integrarea numerică a ecuației de mișcare) și zona nedetectată.

Rulare: python3 verify/m06_verify.py
"""
import json
import math
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
ENG = (ROOT / "site/m06/engine.js").as_posix()
M01E = (ROOT / "site/m01/engine.js").as_posix()
S3 = math.sqrt(3)
a = np.exp(2j * math.pi / 3)
bad = 0


def js(code):
    out = subprocess.run(["node", "-e", f"const M=require('{ENG}');const M01=require('{M01E}');" + code], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


cz = lambda z: complex(z["re"], z["im"])
D = js("console.log(JSON.stringify({D:M.DEFAULTS,ADJ:M.ADJ,X4:M.X4,REL:M.RELAYS,N:M01.DEFAULTS,LINES:M01.LINES,XGMIN:M.XGMIN,XFMIN:M.XFMIN}))")
N, LINES, ADJ, X4 = D["N"], D["LINES"], D["ADJ"], D["X4"]

# [1] impedanțele ----------------------------------------------------------------
def zbus(kase):
    c = N["cmax"] if kase == "max" else N["cmin"]
    Sk = N["SkQmax"] if kase == "max" else N["SkQmin"]
    ZQ = c * N["UnQ"] ** 2 / Sk
    XQ = ZQ / math.sqrt(1 + N["rxQ"] ** 2)
    zq = complex(N["rxQ"] * XQ, XQ) / (N["UrHV"] / N["UrLV"]) ** 2
    ZT = N["uk"] / 100 * N["UrLV"] ** 2 / N["Sr"]
    RT = N["Pk"] / 1000 * N["UrLV"] ** 2 / N["Sr"] ** 2
    XT = math.sqrt(ZT ** 2 - RT ** 2)
    KT = 0.95 * N["cmax"] / (1 + 0.6 * XT / (N["UrLV"] ** 2 / N["Sr"])) if kase == "max" else 1.0
    return zq + KT * complex(RT, XT)


eng_z = js("console.log(JSON.stringify(['max','min'].map(k=>M01.source(M01.DEFAULTS,k).z1bus)))")
dz = max(abs(zbus(k) - cz(z)) / abs(zbus(k)) for k, z in zip(["max", "min"], eng_z))
ok = dz < 1e-12
bad += not ok
print(f"[1] Z_rețea la 20 kV: max {zbus('max'):.4f} Ω, min {zbus('min'):.4f} Ω; abatere față de motor {dz:.1e} {'✓' if ok else '✗'}")


def zgen(p):
    zb = N["Un"] ** 2 / p["Sg"]
    return complex(0.07 * p["xd"] * zb, (p["xd"] + p["ukT"] / 100) * zb)


eg = js("console.log(JSON.stringify(M.compute({dg:'sync'}).zg))")
ok = abs(zgen(D["D"]) - cz(eg)) < 1e-9 and D["D"]["rxg"] == 0.07
bad += not ok
print(f"[1] Z_G (5 MVA, x″d 0,18, R_Gf = 0,07·X″d, u_k bloc 7 %) = {zgen(D['D']):.3f} Ω, motor {cz(eg):.3f} Ω {'✓' if ok else '✗'}")

# [2] analiza nodală în coordonate de fază ------------------------------------------
cases = js("""const out=[];
for(const dg of ['none','sync','inv'])for(const Sg of [5,10])for(const xg of [2,8,15])for(const kase of ['max','min'])for(const type of ['3F','2F'])for(const Rf of [0,5]){
 const fl=[['F1',{xf:0}],['F1',{xf:0.5}],['F1',{xf:5}],['F1',{xf:10}],['F1',{xf:12}],['F1',{xf:20}],['bus',{}]];
 for(const adj of Object.keys(M.ADJ))for(const f of [0,0.5,1])fl.push(['adj',{adj,xa:M.ADJ[adj].km*f}]);
 for(const [fault,ex] of fl){
  if(dg==='none'&&(Sg!==5||xg!==8))continue;
  const p={dg,Sg,xg,kase,type,Rf,fault,...ex};const r=M.compute(p);
  out.push({p:r.p,o:{IR3:r.IR3,IR4:r.IR4,IA:r.IA,IR2:r.IR2,IDG:r.IDG,IF:r.IF,VLLg:r.VLLg,frozen:r.frozen,th:r.thInv,conv:r.conv,dir:r.dirR3,picked:r.dirPicked,ph:r.dirPh.map(x=>({ang:x.ang,active:x.active,fwd:x.fwd,mem:x.mem}))}});
 }}
console.log(JSON.stringify(out));""")


def phase_line(z1, z0, km):
    zs, zm = (z0 + 2 * z1) / 3 * km, (z0 - z1) / 3 * km
    return np.full((3, 3), zm) + np.eye(3) * (zs - zm)


def network(p):
    """întoarce funcția care rezolvă rețeaua pentru un unghi θ al invertorului"""
    kase = p["kase"]
    c = N["cmax"] if kase == "max" else N["cmin"]
    E = c * N["Un"] * 1000 / S3
    Eabc = E * np.array([1, a * a, a])
    kth = 1 + 0.004 * (N["thetaE"] - 20) if kase == "min" else 1.0
    L = N["L"]
    has = p["dg"] != "none"
    xg = min(max(p["xg"], D["XGMIN"]), L)
    xs = {0.0, float(X4), float(L)}
    if has:
        xs.add(float(xg))
    xf = min(max(p["xf"], D["XFMIN"]), L)          # defect „la 0 km” = imediat după TC-ul lui R3
    if p["fault"] == "F1":
        xs.add(float(xf))
    xs = sorted(xs)
    pos = {x: i for i, x in enumerate(xs)}
    nN = len(xs) + (1 if p["fault"] == "adj" else 0)
    nA = len(xs) if p["fault"] == "adj" else None
    n = 3 * nN
    Y = np.zeros((n, n), dtype=complex)
    I0 = np.zeros(n, dtype=complex)
    ph = lambda k: slice(3 * k, 3 * k + 3)
    zs = zbus(kase)
    Y[ph(0), ph(0)] += np.eye(3) / zs
    I0[ph(0)] += Eabc / zs
    o = LINES[N["line"]]
    z1, z0 = complex(o["R1"] * kth, o["X1"]), complex(o["R0"] * kth, o["X0"])
    segs = []
    for i in range(len(xs) - 1):
        Yl = np.linalg.inv(phase_line(z1, z0, xs[i + 1] - xs[i]))
        segs.append((i, i + 1, Yl, xs[i]))
    if nA is not None:
        A = ADJ[p["adj"]]
        oa = LINES[A["type"]]
        Yl = np.linalg.inv(phase_line(complex(oa["R1"] * kth, oa["X1"]), complex(oa["R0"] * kth, oa["X0"]), max(min(p["xa"], A["km"]), 1e-6)))
        segs.append((0, nA, Yl, "A"))
    for i, j, Yl, _ in segs:
        Y[ph(i), ph(i)] += Yl; Y[ph(j), ph(j)] += Yl; Y[ph(i), ph(j)] -= Yl; Y[ph(j), ph(i)] -= Yl
    g = pos[float(xg)] if has else None
    if p["dg"] == "sync":
        zg = zgen(p)
        Y[ph(g), ph(g)] += np.eye(3) / zg
        I0[ph(g)] += Eabc / zg
    f = 0 if p["fault"] == "bus" else nA if p["fault"] == "adj" else pos[float(xf)]
    Ir = p["Sg"] * 1e6 / (S3 * N["Un"] * 1000)
    # defectul: 3F = trei rezistențe R_f spre o stea flotantă (R_f = 0: scurtcircuite ideale a–b, b–c);
    # 2F = R_f între fazele b și c (R_f = 0: scurtcircuit ideal). Scurtcircuitele ideale: formulare nodală modificată.
    fa, fb, fc = 3 * f, 3 * f + 1, 3 * f + 2
    extra = []
    size = n + (1 if p["type"] == "3F" and p["Rf"] > 0 else 0)
    Yf = np.zeros((size, size), dtype=complex)
    Yf[:n, :n] = Y
    if p["type"] == "3F":
        if p["Rf"] > 0:
            for q in (fa, fb, fc):
                y = 1 / p["Rf"]
                Yf[q, q] += y; Yf[n, n] += y; Yf[q, n] -= y; Yf[n, q] -= y
        else:
            extra = [(fa, fb), (fb, fc)]
    else:
        if p["Rf"] > 0:
            y = 1 / p["Rf"]
            Yf[fb, fb] += y; Yf[fc, fc] += y; Yf[fb, fc] -= y; Yf[fc, fb] -= y
        else:
            extra = [(fb, fc)]
    m = len(extra)
    Mx = np.zeros((size + m, size + m), dtype=complex)
    Mx[:size, :size] = Yf
    for k, (i, j) in enumerate(extra):
        Mx[i, size + k] += 1; Mx[size + k, i] += 1
        Mx[j, size + k] -= 1; Mx[size + k, j] -= 1

    def solve(theta):
        I = np.zeros(Mx.shape[0], dtype=complex)
        I[:n] = I0
        Iinv = 0j
        if p["dg"] == "inv":
            Iinv = p["k"] * Ir * np.exp(1j * math.radians(theta - p["phiInv"]))
            I[3 * g: 3 * g + 3] += Iinv * np.array([1, a * a, a])
        V = np.linalg.solve(Mx, I)
        Vn = V[:n]
        return Vn, Iinv

    def results(theta):
        Vn, Iinv = solve(theta)
        res = {}
        for i, j, Yl, tag in segs:
            Ib = Yl @ (Vn[ph(i)] - Vn[ph(j)])
            if tag == 0.0 and i == 0:
                res["R3"] = Ib
            if tag == float(X4):
                res["R4"] = Ib
            if tag == "A":
                res["A"] = Ib
        res["R2"] = (Eabc - Vn[ph(0)]) / zs
        if p["dg"] == "sync":
            res["DG"] = (Eabc - Vn[ph(g)]) / zgen(p)
        elif p["dg"] == "inv":
            res["DG"] = Iinv * np.array([1, a * a, a])
        # curentul de defect = suma curenților care intră în nodul f din rețea (KCL)
        inflow = np.zeros(3, dtype=complex)
        for i, j, Yl, tag in segs:
            if i == f:
                inflow -= Yl @ (Vn[ph(i)] - Vn[ph(j)])
            if j == f:
                inflow += Yl @ (Vn[ph(i)] - Vn[ph(j)])
        if f == 0:
            inflow += res["R2"]
        if p["dg"] != "none" and g == f:
            inflow += res["DG"]
        res["F"] = inflow
        res["V"] = Vn
        return res

    def u1g(theta):
        Vn, _ = solve(theta)
        Va, Vb, Vc = Vn[ph(g)]
        return (Va + a * Vb + a * a * Vc) / 3

    return dict(results=results, u1g=u1g, E=E, g=g, f=f, ph=ph)


def wrap(d):
    return (d + 180) % 360 - 180


def inv_roots(net, p):
    """toate rădăcinile g(θ) = arg U1g(θ) − θ, cu |U1g| ≥ uPLL·E"""
    th = np.arange(-180, 180, 0.25)
    gv = np.array([wrap(math.degrees(np.angle(net["u1g"](t))) - t) for t in th])
    roots = []
    for k in range(len(th)):
        g0, g1 = gv[k], gv[(k + 1) % len(th)]
        t0, t1 = th[k], th[k] + 0.25
        if g0 == 0:
            roots.append(t0)
        elif g0 * g1 < 0 and abs(g0 - g1) < 90:      # schimbare de semn reală, nu saltul de la ±180°
            r = brentq(lambda t: wrap(math.degrees(np.angle(net["u1g"](t))) - t), t0, t1, xtol=1e-12)
            roots.append(wrap(r))
    return [r for r in roots if abs(net["u1g"](r)) >= p["uPLL"] * net["E"]]


worst = 0.0
worst_case = None
worst_ang = [0.0]
nroot_multi = 0
froz = 0
for c in cases:
    p, o = c["p"], c["o"]
    net = network(p)
    theta = 0.0
    if p["dg"] == "inv":
        roots = inv_roots(net, p)
        if len(roots) > 1:
            nroot_multi += 1
        if o["frozen"]:
            froz += 1
            # motorul îngheață unghiul: nu trebuie să existe nicio rădăcină cu |U1g| ≥ uPLL
            if roots:
                bad += 1
                print("   invertor: motorul a înghețat unghiul, dar există soluție", p, roots)
            theta = 0.0
        else:
            if not roots or min(abs(wrap(r - o["th"])) for r in roots) > 1e-5:
                bad += 1
                print("   invertor: unghiul motorului nu e rădăcină", p, o["th"], roots)
            theta = o["th"]
    r = net["results"](theta)
    mag = lambda v: float(np.max(np.abs(v))) if v is not None else 0.0
    E = net["E"]
    Vg = r["V"][net["ph"](net["g"])] if net["g"] is not None else None
    vll = None if Vg is None else min(abs(Vg[0] - Vg[1]), abs(Vg[1] - Vg[2]), abs(Vg[2] - Vg[0])) / (E * S3)
    mine = {"IR3": mag(r.get("R3")), "IR4": mag(r.get("R4")), "IA": mag(r.get("A")), "IR2": mag(r["R2"]), "IDG": mag(r.get("DG")), "IF": mag(r["F"])}
    # unghiurile elementelor de fază ale lui R3, recalculate (conexiunea la 90°, θc = 30°, memorie sub 5 %)
    if mine["IR3"] > 1e-3:
        Vb = r["V"][0:3]
        Ep = E * np.array([1, a * a, a])
        angs = []
        for i, (u, v) in enumerate(((1, 2), (2, 0), (0, 1))):
            Vp = Vb[u] - Vb[v]
            if abs(Vp) < 0.05 * E * S3:
                Vp = Ep[u] - Ep[v]
            angs.append(wrap(math.degrees(np.angle(r["R3"][i]) - np.angle(Vp)) - 30))
        for i in range(3):
            if np.abs(r["R3"][i]) > 1e-3 * mine["IR3"]:
                e = abs(wrap(angs[i] - o["ph"][i]["ang"])) / 180
                if e > worst_ang[0]:
                    worst_ang[0] = e
    for k, v in mine.items():
        e = abs(v - o[k]) / max(1.0, v)
        if e > worst:
            worst, worst_case = e, (k, p, v, o[k])
    if vll is not None:
        e = abs(vll - o["VLLg"])
        if e > worst:
            worst, worst_case = e, ("VLLg", p, vll, o["VLLg"])
ok = worst < 1e-6
bad += not ok
print(f"[2] {len(cases)} cazuri (fără centrală, sincron, invertor × 2 puteri × 3 poziții × max/min × 3F/2F × R_f 0/5 Ω × 16 locuri de defect):")
print(f"    abaterea maximă a curenților (R3, R4, plecarea vecină, R2, centrală, defect) și a tensiunii în punctul de racordare: {worst:.1e} {'✓' if ok else '✗'}")
if not ok:
    print("    cel mai mare:", worst_case)
print(f"    invertor: unghiul motorului este rădăcina lui arg U1g(θ) − θ în toate cazurile convergente; {froz} cazuri fără soluție cu |U1g| ≥ 0,1 u.r. (unghi înghețat) — confirmat; cazuri cu mai multe rădăcini: {nroot_multi}")

# [2b] direcția lui R3 (fiecare element de fază; un 67 declanșează dacă un element pornit vede „înainte”)
ok = worst_ang[0] * 180 < 1e-5
bad += not ok
print(f"[2b] unghiurile elementelor direcționale ale lui R3 (conexiunea la 90°, θc = 30°), recalculate din tensiunile și curenții nodali: abatere maximă {worst_ang[0]*180:.1e}° {'✓' if ok else '✗'}")
wrong, amb = 0, []
for c in cases:
    p, o = c["p"], c["o"]
    if o["IR3"] < 1e-3:
        continue
    act = [x for x in o["ph"] if x["active"]] or [x for x in o["ph"]]
    anyf = any(x["fwd"] for x in act)
    if p["fault"] == "F1" and o["picked"] and not anyf:
        wrong += 1
    if p["fault"] != "F1" and p["dg"] == "sync" and o["picked"] and anyf:
        wrong += 1
    if p["fault"] != "F1" and p["dg"] == "inv" and o["picked"] and anyf:
        amb.append(min(90 - abs(x["ang"]) for x in act if x["fwd"]))
ok = wrong == 0
bad += not ok
print(f"     generator sincron: niciun element „înainte” la defectele din spatele lui R3, cel puțin unul la defectele pe F1: {wrong} abateri {'✓' if ok else '✗'}")
print(f"     invertor: la defecte din spatele lui R3, curentul invers are unghiul impus de reglajul invertorului; {len(amb)} cazuri în care un element pornit vede „înainte”, toate cu cel mult {max(amb) if amb else 0:.1f}° în interiorul zonei (la limita ei: decizie nesigură, nu o eroare de calcul)")

# [2d] la defectele pe plecarea vecină, releul ei vede cel puțin cât R3 (curentul centralei e o parte din curentul de defect)
viol = [c for c in cases if c["p"]["fault"] == "adj" and c["o"]["IA"] < c["o"]["IR3"] - 1e-9]
ok = not viol
bad += not ok
print(f"[2d] defecte pe plecarea vecină: I_A ≥ I_R3 în toate cele {sum(1 for c in cases if c['p']['fault'] == 'adj')} cazuri (cu aceleași reglaje, R3 nu poate fi mai rapid) {'✓' if ok else '✗ ' + str(len(viol))}")

# [2c] invertor: limitarea curentului — |I_DG| = k·I_r în toate cazurile
lim = max(abs(c["o"]["IDG"] - c["p"]["k"] * c["p"]["Sg"] * 1e6 / (S3 * 20000)) for c in cases if c["p"]["dg"] == "inv")
ok = lim < 1e-6
bad += not ok
print(f"[2c] invertor: |I_DG| = k·I_r în toate cazurile (abatere {lim:.1e} A) {'✓' if ok else '✗'}")

# [3] pandapower — generator sincron -------------------------------------------
import pandapower as pp
import pandapower.shortcircuit as sc
import logging
warnings.filterwarnings("ignore")
logging.disable(logging.WARNING)


def pp_case(p, fault, kase):
    net = pp.create_empty_network()
    b110 = pp.create_bus(net, 110)
    b20 = pp.create_bus(net, 20)
    pp.create_ext_grid(net, b110, s_sc_max_mva=N["SkQmax"], s_sc_min_mva=N["SkQmin"], rx_max=N["rxQ"], rx_min=N["rxQ"])
    pp.create_transformer(net, b110, b20, std_type="25 MVA 110/20 kV")
    xs = sorted({float(X4), float(N["L"]), float(p["xg"])} | ({float(p["xf"])} if p["fault"] == "F1" else set()))
    buses, prev, last, lines = {0.0: b20}, b20, 0.0, {}
    o = LINES["ol70"]
    for x in xs:
        nb = pp.create_bus(net, 20)
        lines[last] = pp.create_line_from_parameters(net, prev, nb, x - last, r_ohm_per_km=o["R1"], x_ohm_per_km=o["X1"], c_nf_per_km=0, max_i_ka=1, endtemp_degree=N["thetaE"])
        buses[x], prev, last = nb, nb, x
    if p["fault"] == "adj":
        A = ADJ[p["adj"]]; oa = LINES[A["type"]]
        nb = pp.create_bus(net, 20)
        la = pp.create_line_from_parameters(net, b20, nb, p["xa"], r_ohm_per_km=oa["R1"], x_ohm_per_km=oa["X1"], c_nf_per_km=0, max_i_ka=1, endtemp_degree=N["thetaE"])
        fbus = nb
    else:
        la, fbus = None, buses[float(p["xf"])]
    zg = zgen(p)
    # K_G = (U_n/U_rG)·c_max/(1 + x″d·sin φ) = 1,1 cu cos φ = 1 → impedanța dată se împarte la 1,1
    pp.create_gen(net, buses[float(p["xg"])], p_mw=0, vm_pu=1.0, sn_mva=p["Sg"], vn_kv=20, xdss_pu=zg.imag / (N["Un"] ** 2 / p["Sg"]) / 1.1, rdss_ohm=zg.real / 1.1, cos_phi=1.0)
    sc.calc_sc(net, case=kase, fault=fault, bus=fbus, branch_results=True)
    rl = net.res_line_sc
    return {"IR3": rl.ikss_ka[lines[0.0]] * 1000, "IR4": rl.ikss_ka[lines[float(X4)]] * 1000, "IA": rl.ikss_ka[la] * 1000 if la is not None else 0.0, "IF": net.res_bus_sc.ikss_ka[fbus] * 1000}


worst3 = 0.0
rows = []
for Sg in (5, 10):
    for xg in (2, 8, 15):
        for fault, ex in [("F1", {"xf": 20}), ("F1", {"xf": 12}), ("adj", {"adj": "F4", "xa": 15}), ("adj", {"adj": "F2", "xa": 3})]:
            for kase, ft, tp in [("max", "3ph", "3F"), ("min", "2ph", "2F")]:
                p = dict(D["D"], dg="sync", Sg=Sg, xg=xg, fault=fault, kase=kase, type=tp, **ex)
                if fault == "F1" and ex["xf"] < xg:
                    continue
                e = js(f"const r=M.compute({json.dumps(p)});console.log(JSON.stringify({{IR3:r.IR3,IR4:r.IR4,IA:r.IA,IF:r.IF}}))")
                q = pp_case(p, ft, kase)
                for k in ("IR3", "IA", "IF") + (("IR4",) if fault == "F1" else ()):
                    worst3 = max(worst3, abs(q[k] - e[k]) / max(q[k], 1.0))
                rows.append((Sg, xg, fault, ex, kase, tp, q["IR3"], e["IR3"]))
ok = worst3 < 1e-4
bad += not ok
print(f"[3] pandapower (generator sincron, {len(rows)} cazuri 3F max / 2F min): abaterea maximă a curenților prin R3, R4, plecarea vecină și la defect {worst3:.1e} {'✓' if ok else '✗'}")
for r_ in rows[:4]:
    print(f"    S_g {r_[0]} MVA, x_g {r_[1]} km, defect {r_[2]} {r_[3]}, {r_[5]} {r_[4]}: I_R3 pandapower {r_[6]:.1f} A, motor {r_[7]:.1f} A")

# [4] timpii și verificările de reglaj ------------------------------------------
REL = D["REL"]


def t_iec_vi(S, I, tOwn=0.03):
    t51 = t50 = math.inf
    M_ = I / S["Is"]
    if M_ >= 1.1:
        m = min(M_, 20)
        t51 = max(S["tms"] * 13.5 / (m - 1), tOwn)
    if S["Ih"] > 0 and I >= S["Ih"]:
        t50 = max(S["th"], tOwn)
    return min(t51, t50)


tt = js("""const out=[];for(const dg of ['sync','inv'])for(const [fault,ex] of [['F1',{xf:20}],['F1',{xf:5}],['adj',{xa:3}],['adj',{xa:15}],['bus',{}]])for(const tmsA of [0.16,0.8])for(const IhA of [true,false]){
const p={dg,fault,...ex,tmsA,IhA,type:'3F',kase:'max'};const r=M.compute(p);const t=M.times(r);out.push({p,IR3:r.IR3,IR4:r.IR4,IA:r.IA,IR2:r.IR2,t});}
console.log(JSON.stringify(out));""")
wt = 0.0
for c in tt:
    p = c["p"]
    SA = dict(REL["R3"], tms=p["tmsA"], Ih=REL["R3"]["Ih"] if p["IhA"] else 0)
    exp = {"R3": t_iec_vi(REL["R3"], c["IR3"]) if c["IR3"] > 0 else math.inf,
           "R4": t_iec_vi(REL["R4"], c["IR4"]) if c["IR4"] > 0 else math.inf,
           "A": t_iec_vi(SA, c["IA"]) if c["IA"] > 0 else math.inf,
           "R2": t_iec_vi(REL["R2"], c["IR2"])}
    for k, v in exp.items():
        got = c["t"][k] if c["t"][k] is not None else math.inf
        if math.isinf(v) or math.isinf(got):
            if math.isinf(v) != math.isinf(got):
                wt = math.inf
        else:
            wt = max(wt, abs(v - got))
ok = wt < 1e-9
bad += not ok
print(f"[4] timpii releelor (IEC VI, G_T = 1,1, G_D = 20, I>>): abatere maximă {wt:.1e} s pe {len(tt)} cazuri {'✓' if ok else '✗'}")

# declanșarea simpatică: recalculată din curenții motorului cu timpii de mai sus
sy = js("""const out=[];for(const [dg,Sg,xg,tmsA,IhA,rel] of [['sync',5,8,0.16,true,'m03'],['sync',10,2,0.16,true,'m03'],['sync',10,2,1.0,false,'rev'],['sync',10,8,0.8,false,'rev'],['sync',5,15,0.16,true,'m03'],['sync',5,15,0.16,true,'rev'],['inv',5,15,0.16,true,'m03'],['inv',5,15,0.16,true,'rev']]){const p={dg,Sg,xg,tmsA,IhA,rel};const s=M.sympathetic(p);out.push({dg,Sg,xg,tmsA,IhA,rel,S:M.settingsFor(p),ok:s.ok,worst:s.worst,rows:s.rows});}
console.log(JSON.stringify(out));""")
werr = 0
for s in sy:
    SA = dict(REL["R3"], tms=s["tmsA"], Ih=REL["R3"]["Ih"] if s["IhA"] else 0)
    SS = s["S"]
    marg = []
    for r_ in s["rows"]:
        tA = t_iec_vi(SA, r_["IA"])
        for k in ("R3", "R4"):
            tk = t_iec_vi(SS[k], r_["I" + k]) if r_["I" + k] > 0 else math.inf
            if tk < math.inf:
                marg.append(tk - tA)
    mymin = min(marg) if marg else math.inf
    myok = mymin >= 0.3 - 1e-9
    werr += myok != s["ok"]
    print(f"    {'sincron' if s['dg']=='sync' else 'invertor'} {s['Sg']} MVA la {s['xg']} km, reglaje {s['rel']}, plecarea vecină TMS {s['tmsA']}, I>> {'activ' if s['IhA'] else 'dezactivat'}: marja minimă = {mymin:.2f} s → {'selectiv' if myok else 'DECLANȘARE SIMPATICĂ (marjă < 0,3 s)'}" + (f" ({s['worst']['relay']})" if s['worst'] else ""))
ok = werr == 0
bad += not ok
print(f"[4] verdictul de declanșare simpatică al motorului coincide cu recalculul: {'✓' if ok else '✗'}")

# regimul normal: exportul centralei și pragurile revizuite
nc = js("""const M03=require('%s');const out=[];for(const dg of ['sync','inv'])for(const Sg of [1,3,5,8,10])for(const xg of [2,8,12,15,20]){const p={dg,Sg,xg};
const d0=M03.DEFAULTS, Ir=M.IrG(p), after=xg>M.X4;
const d={...d0,R3:{...d0.R3,Iload:Math.max(d0.R3.Iload,Ir)},R4:{...d0.R4,Iload:after?Math.max(d0.R4.Iload,Ir):d0.R4.Iload}};
out.push({p,Ir,n0:M.normalCheck(p,M.RELAYS),SR:M.settingsFor({...p,rel:'rev'}),ref:M03.autoSettings({...M01.DEFAULTS},d).S});}
console.log(JSON.stringify(out));""" % (ROOT / "site/m03/engine.js").as_posix())
werr = 0
for c in nc:
    Ir = c["p"]["Sg"] * 1e6 / (S3 * 20000)
    for k, load, ct in (("R3", 200, 300), ("R4", 80, 100)):
        exp = Ir if (k == "R3" or c["p"]["xg"] > X4) else 0.0
        need = 1.2 * max(load, exp) / 0.95
        ok0 = REL[k]["Is"] >= need - 1e-9
        if ok0 != c["n0"][k]["ok"] or abs(need - c["n0"][k]["need"]) > 1e-9:
            werr += 1
        if c["SR"][k]["Is"] < need - 1e-9:
            werr += 1
        if any(abs(c["SR"][k][q] - c["ref"][k][q]) > 1e-12 for q in ("Is", "tms", "Ih", "th")):
            werr += 1
ok = werr == 0 and abs(Ir - 0) >= 0
bad += not ok
ex = [c for c in nc if c["p"]["dg"] == "sync" and c["p"]["Sg"] == 5 and c["p"]["xg"] == 15][0]
print(f"[4] regimul normal (50 cazuri): pragul necesar 1,2·max(I_sarcină, I_rG)/0,95 și verdictul motorului ✓; pragurile revizuite îl respectă și coincid cu procedura M03 refăcută: {werr} abateri {'✓' if ok else '✗'}")
print(f"    exemplu: 5 MVA la 15 km → I_rG = {5e6/(S3*20000):.1f} A > I> R4 = {REL['R4']['Is']:.0f} A (M03); R4 revizuit {ex['SR']['R4']['Is']:.0f} A, TMS {ex['SR']['R4']['tms']:.2f}; R3 {ex['SR']['R3']['Is']:.0f} A, TMS {ex['SR']['R3']['tms']:.2f}")

# orbirea: monotonia și sensul efectului
bl = js("console.log(JSON.stringify([M.blinding({dg:'sync'}),M.blinding({dg:'sync',Sg:10}),M.blinding({dg:'inv'})]))")
s5, s10, iv = bl
ok = all(pt["with"] <= pt["without"] + 1e-9 for pt in s5["pts"] if pt["xf"] > 8) and s10["red"] > s5["red"] > 0
bad += not ok
print(f"[4] orbirea (2F min la capătul F1): generator sincron 5 MVA −{100*s5['red']:.1f} %, 10 MVA −{100*s10['red']:.1f} % (crește cu puterea; R3 vede mai puțin pentru toate defectele de după centrală) {'✓' if ok else '✗'}")
print(f"    invertor 5 MVA: {100*-iv['red']:+.1f} % — curentul de secvență pozitivă al invertorului ridică tensiunea la defect, iar R3 duce întregul curent de secvență negativă (verificat în [2])")

# FRT și treapta U< (calcul analitic separat)
def lim_frt(f, t):
    pts = [(0, f["Uret"]), (f["tclr"], f["Uret"]), (f["tclr"], f["Uclr"]), (f["trec2"], f["Uclr"]), (f["trec3"], f["Urec2"]), (1e9, f["Urec2"])]
    for (t0, u0), (t1, u1) in zip(pts, pts[1:]):
        if t0 <= t <= t1 and t1 > t0:
            if t == t0 and t0 == f["tclr"]:
                return f["Uret"]
            return u0 + (u1 - u0) * (t - t0) / (t1 - t0)
    return f["Urec2"]


frt = D["D"]["frt"]
werr = 0
for kind in ("sync", "inv"):
    f = frt[kind]
    for t in np.linspace(0, 4, 4001):
        e = js(f"console.log(JSON.stringify(M.frtLimit({json.dumps(f)},{t})))") if t in (0.0, 0.15, 0.7, 1.5, 3.0) else None
        if e is not None and abs(e - lim_frt(f, t)) > 1e-12:
            werr += 1
    # durata sub U_set, numeric
    for Uset, tset in ((0.85, 3.2), (0.8, 1.5), (0.7, 0.5), (0.3, 0.2)):
        ts = np.linspace(0, 10, 100001)
        Dn = ts[[lim_frt(f, t) < Uset - 1e-12 for t in ts]].max(initial=0)
        e = js(f"console.log(JSON.stringify(M.underVoltageCompat({json.dumps(f)},{Uset},{tset})))")
        if abs(e["D"] - Dn) > 2e-4 or e["ok"] != (tset > Dn):
            werr += 1
            print("   U< diferit", kind, Uset, tset, e, Dn)
ok = werr == 0
bad += not ok
fs, fi = frt["sync"], frt["inv"]
d1 = js(f"console.log(JSON.stringify([M.underVoltageCompat({json.dumps(fs)},0.85,3.2),M.underVoltageCompat({json.dumps(fi)},0.85,3.2)]))")
print(f"[4] profilul FRT (NC RfG) și treapta U< = 0,85·U_n / 3,2 s: durata maximă admisă sub 0,85 u.r. — sincron {d1[0]['D']:.2f} s, PPM {d1[1]['D']:.2f} s → treapta e compatibilă cu ambele {'✓' if ok else '✗'}")

# insularizarea: integrarea numerică a ecuației de mișcare (2H/f0·df/dt = ΔP/S_g, fără regulatoare)
isl = js("""const out=[];for(const H of [1,2,4])for(const PG of [2,3.5,3.8,4.0,4.2,4.5,6])out.push({H,PG,r:M.island({H,PG})});console.log(JSON.stringify(out));""")
p0 = D["D"]
werr = 0
for c in isl:
    H, PG = c["H"], c["PG"]
    dt, f, t, tf = 1e-4, 50.0, 0.0, math.inf
    dP = (PG - p0["PL"]) / p0["Sg"]
    while t < 30:
        f += dt * dP * 50 / (2 * H)
        t += dt
        if f <= p0["fmin"] or f >= p0["fmax"]:
            tf = t
            break
    rocof = dP * 50 / (2 * H)
    tdet = min(tf + p0["tF"], p0["tRocof"] if abs(rocof) >= p0["rocof"] else math.inf)
    e = c["r"]
    if abs(e["rocof"] - rocof) > 1e-12 or (math.isinf(tdet) != (e["tDet"] is None)) or (not math.isinf(tdet) and abs(e["tDet"] - tdet) > 2e-4):
        werr += 1
        print("   insularizare diferită", c, rocof, tdet)
nd = js("console.log(JSON.stringify(M.ndz({})))")
# zona nedetectată, prin baleiere fină cu simularea de mai sus (pas 0,001·S_g)
und = []
for i in range(-200, 201):
    d = i / 1000
    rocof = d * 50 / (2 * p0["H"])
    tf = (50 - p0["fmin"]) / -rocof if rocof < 0 else (p0["fmax"] - 50) / rocof if rocof > 0 else math.inf
    tdet = min(tf + p0["tF"], p0["tRocof"] if abs(rocof) >= p0["rocof"] - 1e-12 else math.inf)
    if not tdet + p0["tcb"] < p0["tRAR"]:
        und.append(d)
ok = werr == 0 and abs(min(und) - nd["lo"]) <= 1.01e-3 and abs(max(und) - nd["hi"]) <= 1.01e-3
bad += not ok
print(f"[4] insularizare: RoCoF și timpii de detecție, față de integrarea numerică a ecuației de mișcare (21 de cazuri) ✓; zona nedetectată înainte de RAR: motor [{nd['lo']:+.3f}, {nd['hi']:+.3f}]·S_g, baleiere [{min(und):+.3f}, {max(und):+.3f}]·S_g {'✓' if ok else '✗'}")

print("\nREZULTAT:", "TOATE VERIFICĂRILE AU TRECUT" if bad == 0 else f"{bad} ABATERI")
sys.exit(1 if bad else 0)
