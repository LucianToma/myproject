"""Verificarea independentă a motorului din modulul 04 (protecția direcțională).

1) Partea A: curenții și tensiunile la releu, pentru toate tipurile de defect, înainte și înapoi, cu sau fără
   sursă homopolară la capătul B, în regim maxim și minim — recalculate prin analiză nodală în coordonate
   de fază (surse și linie ca matrice 3×3, defectul cu legături ideale); apoi deciziile direcționale.
2) Partea B: reglajele buclei recalculate cu inelul deschis la sursă (curentul radial E/|Z_S + ΣZ_L|),
   apoi secvența de declanșare în bucla închisă simulată independent (rezolvare numpy, integrarea 1/t(I))
   pentru defecte la fiecare 5 % din fiecare linie, regim maxim și minim; se compară cu motorul și se
   verifică izolarea corectă a liniei defecte.

Rulare: python3 verify/m04_verify.py
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ENG = (ROOT / "site/m04/engine.js").as_posix()
a = np.exp(2j * math.pi / 3)
A = np.array([[1, 1, 1], [1, a * a, a], [1, a, a * a]])
Ainv = np.linalg.inv(A)
S3 = math.sqrt(3)


def js(code):
    return json.loads(subprocess.run(["node", "-e", f"const M=require('{ENG}');const X=require('{(ROOT/'site/assets/cx.js').as_posix()}');" + code], capture_output=True, text=True, check=True).stdout)


cz = lambda z: complex(z["re"], z["im"]) if z is not None else None
bad = 0

# ---------------------------------------------------------------- partea A
cases = js("""const out=[];for(const type of ['3F','2F','1F','2FE'])for(const dir of ['fwd','rev'])for(const gB of [false,true])for(const kase of ['max','min'])for(const m of [0.2,0.7])for(const Rf of [0,10]){
const p={...M.DEF_A,type,dir,gB,kase,m,Rf};const r=M.partA(p);
out.push({p,zSA:r.zSA,zSB:r.zSB,zL:r.zL,E:r.E,Iabc:r.Iabc,Vabc:r.Vabc,dirs:{phase:r.dirs.phase,ground:r.dirs.ground,ph:r.dirs.ph.map(x=>({ang:x.ang,active:x.active,mem:x.mem})),gnd:{ang:r.dirs.gnd.ang,active:r.dirs.gnd.active}}});}
console.log(JSON.stringify(out));""")


def yseq(z0, z1, z2):
    """matricea de admitanțe 3×3 a unui element cu impedanțe de secvență (z0 None → fără cale homopolară)"""
    y = np.diag([0 if z0 is None else 1 / z0, 1 / z1, 1 / z2])
    return A @ y @ Ainv


def solve_partA(c):
    p = c["p"]
    zSA = [cz(z) for z in c["zSA"]]
    zSB = [cz(z) for z in c["zSB"]]
    zL = [cz(z) for z in c["zL"]]
    E = cz(c["E"]) * np.array([1, a * a, a])
    fwd = p["dir"] == "fwd"
    m = min(max(p["m"], 0.001), 0.999)
    # noduri: A 0-2, B 3-5, F 6-8, P 9 (punctul comun al defectului)
    n = 10
    Y = np.zeros((n, n), dtype=complex)
    Ii = np.zeros(n, dtype=complex)
    YA = yseq(zSA[0], zSA[1], zSA[2])
    YB = yseq(zSB[0], zSB[1], zSB[2])
    Y[0:3, 0:3] += YA
    Ii[0:3] += YA @ E
    Y[3:6, 3:6] += YB
    Ii[3:6] += YB @ E

    def line(i, j, k):
        Yl = yseq(zL[0] * k, zL[1] * k, zL[2] * k)
        Y[i:i + 3, i:i + 3] += Yl
        Y[j:j + 3, j:j + 3] += Yl
        Y[i:i + 3, j:j + 3] -= Yl
        Y[j:j + 3, i:i + 3] -= Yl
        return Yl

    if fwd:
        YAF = line(0, 6, m)
        line(6, 3, 1 - m)
        fn = [6, 7, 8]
    else:
        YAB = line(0, 3, 1.0)
        fn = [0, 1, 2]
        Y[6:9, 6:9] += np.eye(3) * 1e-9
    Rf, typ = p["Rf"], p["type"]
    shorts = []

    def conn(i, j):
        if Rf > 0:
            y = 1 / Rf
            Y[i, i] += y
            if j is not None:
                Y[j, j] += y
                Y[i, j] -= y
                Y[j, i] -= y
        else:
            shorts.append((i, j))

    if typ == "3F":
        for k in range(3):
            conn(fn[k], 9)
    elif typ == "2F":
        conn(fn[1], fn[2])
    elif typ == "1F":
        conn(fn[0], None)
    else:
        shorts.append((fn[1], 9)); shorts.append((fn[2], 9))
        if Rf > 0:
            Y[9, 9] += 1 / Rf
        else:
            shorts.append((9, None))
    Y[9, 9] += 1e-12
    mm = len(shorts)
    M_ = np.zeros((n + mm, n + mm), dtype=complex)
    M_[:n, :n] = Y
    rhs = np.concatenate([Ii, np.zeros(mm)])
    for k, (i, j) in enumerate(shorts):
        M_[i, n + k] += 1; M_[n + k, i] = 1
        if j is not None:
            M_[j, n + k] -= 1; M_[n + k, j] = -1
    V = np.linalg.solve(M_, rhs)[:n]
    VA = V[0:3]
    Irel = YAF @ (VA - V[6:9]) if fwd else YAB @ (VA - V[3:6])
    return Irel, VA, E


def wrap(d):
    return ((d + 180) % 360 + 360) % 360 - 180


worst = 0
dir_bad = 0
for c in cases:
    Ipy, Vpy, E = solve_partA(c)
    Ij = np.array([cz(z) for z in c["Iabc"]])
    Vj = np.array([cz(z) for z in c["Vabc"]])
    scale_ = max(np.max(np.abs(Ipy)), 1.0)
    d = max(np.max(np.abs(Ipy - Ij)) / scale_, np.max(np.abs(Vpy - Vj)) / abs(E[0]))
    worst = max(worst, d)
    # deciziile direcționale, recalculate
    p = c["p"]
    pol = [(1, 2), (2, 0), (0, 1)]
    act = []
    for i, (u, v) in enumerate(pol):
        Vp = Vpy[u] - Vpy[v]
        if abs(Vp) < 0.05 * abs(E[0]) * S3:
            Vp = E[u] - E[v]
        ang = wrap(math.degrees(np.angle(Ipy[i]) - np.angle(Vp)) - p["rca"])
        if abs(Ipy[i]) >= p["Is"]:
            act.append(math.cos(math.radians(ang)) > 0)
    phase = "none" if not act else "fwd" if all(act) else "rev" if not any(act) else "mixed"
    I0 = Ipy.sum()
    V0n = -Vpy.sum()
    angN = wrap(math.degrees(np.angle(I0) - np.angle(V0n)) - p["rcaN"])
    ground = "none" if not (abs(I0) >= p["IsN"] and abs(V0n) > 0.01 * abs(E[0])) else ("fwd" if math.cos(math.radians(angN)) > 0 else "rev")
    if phase != c["dirs"]["phase"] or ground != c["dirs"]["ground"]:
        dir_bad += 1
        if dir_bad < 5:
            print("  decizie diferită:", p["type"], p["dir"], p["gB"], p["kase"], p["m"], p["Rf"], phase, c["dirs"]["phase"], ground, c["dirs"]["ground"])
ok = worst < 1e-6 and dir_bad == 0
bad += not ok
print(f"[A] {len(cases)} cazuri: abaterea relativă maximă a curenților și tensiunilor de la releu {worst:.1e}; decizii direcționale diferite: {dir_bad} {'✓' if ok else '✗'}")
# corectitudinea fizică a deciziilor: defectele înainte nu sunt văzute înapoi și invers
wrong = [c for c in cases if (c["p"]["dir"] == "fwd" and ("rev" in (c["dirs"]["phase"], c["dirs"]["ground"]))) or (c["p"]["dir"] == "rev" and ("fwd" in (c["dirs"]["phase"], c["dirs"]["ground"])))]
mixed = [c for c in cases if c["dirs"]["phase"] == "mixed"]
print(f"[A] decizii greșite de sens (fără cazurile „mixte”): {len(wrong)}; cazuri „mixte” ale elementelor de fază: {len(mixed)} (numai la defecte cu pământul: {all(c['p']['type'] in ('1F','2FE') for c in mixed)})")
bad += len(wrong) > 0 or not all(c["p"]["type"] in ("1F", "2FE") for c in mixed)

# ---------------------------------------------------------------- partea B
dump = js("""const d=M.DEF_B;const st=M.ringSettings(d);const net=M.NET;
const sMax=require('%s').source(net,'max'), sMin=require('%s').source(net,'min');
const seq=[];for(const kase of ['max','min'])for(const l of d.lines)for(let i=1;i<20;i++){const m=i/20;const r=M.ringSequence(d,st.S,kase,{line:l.id,m});seq.push({kase,line:l.id,m,events:r.events,correct:r.correct,margin:r.margin});}
console.log(JSON.stringify({d,S:st.S,rep:st.rep,zS:{max:sMax.z1bus,min:sMin.z1bus},E:{max:1.1*20000/Math.sqrt(3),min:1.0*20000/Math.sqrt(3)},seq}));""" % ((ROOT / "site/m01/engine.js").as_posix(), (ROOT / "site/m01/engine.js").as_posix()))
d, S, rep = dump["d"], dump["S"], dump["rep"]
zl = {l["id"]: complex(d["R1"] * l["km"], d["X1"] * l["km"]) for l in d["lines"]}
CURV = {"IEC-SI": (0.14, 0.02), "IEC-VI": (13.5, 1.0), "IEC-EI": (80.0, 2.0)}


def ttrip(s, I):
    k, al = CURV[s["curve"]]
    M_ = I / s["Is"]
    if M_ < 1.1:
        return math.inf
    return max(s["tms"] * k / (min(M_, 20) ** al - 1), d["tOwn"])


# [B1] reglajele, cu inelul deschis
chains = {"cw": ["DA@D", "CD@C", "BC@B", "AB@A"], "ccw": ["AB@B", "BC@C", "CD@D", "DA@A"]}
path = {"cw": ["AB", "BC", "CD", "DA"], "ccw": ["DA", "CD", "BC", "AB"]}
zS = complex(dump["zS"]["max"]["re"], dump["zS"]["max"]["im"])
Emax = dump["E"]["max"]
Is = math.ceil(d["kSig"] * d["kP"] * d["Iload"] / d["kRev"] / (d["ct"] * 0.01) - 1e-9) * d["ct"] * 0.01
ok = abs(Is - rep["Is"]) < 1e-9
bad += not ok
print(f"[B1] pragul I> = {rep['Is']:.0f} A (recalculat {Is:.0f} A) {'✓' if ok else '✗'}")
Spy = {r: {"curve": d["curve"], "Is": Is, "tms": d["tmsMin"]} for r in S}
for dr in ("cw", "ccw"):
    ch = chains[dr]
    for i in range(1, len(ch)):
        dn, up = ch[i - 1], ch[i]
        # inelul deschis: curentul e același prin tot lanțul; defectul imediat după releul din aval
        # releul dn e pe linia path[dr][len(ch)-i] (numărând de la sursă)
        nlines = len(ch) - i + 1        # câte linii sunt între sursă și defect (inclusiv cea a lui dn, aproape de capătul ei)
        ztot = zS + sum(zl[l] for l in path[dr][:nlines - 1]) + zl[path[dr][nlines - 1]] * 0.001
        Imax = Emax / abs(ztot)
        lo = 1.1 * max(Spy[dn]["Is"], Spy[up]["Is"]) * 1.0001
        need = 0
        for k in range(161):
            Ii = lo * (Imax / lo) ** (k / 160)
            tdn = ttrip(Spy[dn], Ii)
            if not math.isfinite(tdn):
                continue
            kk, al = CURV[d["curve"]]
            need = max(need, (tdn + d["cti"]) / (kk / (min(Ii / Is, 20) ** al - 1)))
        Spy[up]["tms"] = max(d["tmsMin"], math.ceil(need * 100 - 1e-9) / 100)
        jr = next(x for x in rep["chains"][dr] if x["up"] == up)
        ok = abs(Spy[up]["tms"] - S[up]["tms"]) < 1e-9 and abs(Imax - jr["Imax"]) <= 1e-6 * Imax
        bad += not ok
        print(f"[B1] {dr:3s} {dn} → {up}: I_max = {jr['Imax']:.1f} A (recalculat {Imax:.1f}), TMS = {S[up]['tms']:.2f} (recalculat {Spy[up]['tms']:.2f}) {'✓' if ok else '✗'}")

# [B2] secvența în bucla închisă, simulată independent
idx = {"A": 0, "B": 1, "C": 2, "D": 3}


def solve_ring(kase, fline, m, open_):
    zs = complex(dump["zS"][kase]["re"], dump["zS"][kase]["im"])
    E = dump["E"][kase]
    Y = np.zeros((4, 4), dtype=complex)
    I = np.zeros(4, dtype=complex)
    Y[0, 0] += 1 / zs
    I[0] = E / zs
    segs = []
    for l in d["lines"]:
        oa, ob = f"{l['id']}@{l['a']}" in open_, f"{l['id']}@{l['b']}" in open_
        z = zl[l["id"]]
        if l["id"] == fline:
            if not oa:
                Y[idx[l["a"]], idx[l["a"]]] += 1 / (z * m); segs.append((l["id"], l["a"], None, z * m))
            if not ob:
                Y[idx[l["b"]], idx[l["b"]]] += 1 / (z * (1 - m)); segs.append((l["id"], l["b"], None, z * (1 - m)))
        elif not oa and not ob:
            i, j = idx[l["a"]], idx[l["b"]]
            Y[i, i] += 1 / z; Y[j, j] += 1 / z; Y[i, j] -= 1 / z; Y[j, i] -= 1 / z
            segs += [(l["id"], l["a"], l["b"], z), (l["id"], l["b"], l["a"], z)]
    for i in range(4):
        if Y[i, i] == 0:
            Y[i, i] = 1e-9
    V = np.linalg.solve(Y, I)
    cur = {}
    for (lid, bus, other, z) in segs:
        Vo = 0 if other is None else V[idx[other]]
        cur[f"{lid}@{bus}"] = ((V[idx[bus]] - Vo) / z, V[idx[bus]])
    If = sum(cur[f"{lid}@{bus}"][0] for (lid, bus, other, z) in segs if other is None)
    return cur, If, E


def fwd(I, V, E):
    V1 = E if abs(V) < 0.05 * E else V
    Vp = V1 * (-1j * S3)
    ang = wrap(math.degrees(np.angle(I) - np.angle(Vp)) - d["rca"])
    return math.cos(math.radians(ang)) > 0


relays = [f"{l['id']}@{l['a']}" for l in d["lines"]] + [f"{l['id']}@{l['b']}" for l in d["lines"]]
mism = 0
incorrect = 0
min_margin = math.inf
for sc in dump["seq"]:
    open_, prog, t, ev = set(), {r: 0.0 for r in relays}, 0.0, []
    last_top = None
    for _ in range(8):
        cur, If, E = solve_ring(sc["kase"], sc["line"], sc["m"], open_)
        if abs(If) < 1:
            break
        top = {}
        for r in relays:
            if r in open_ or r not in cur:
                top[r] = math.inf
                continue
            I, V = cur[r]
            top[r] = ttrip(S[r], abs(I)) if fwd(I, V, E) else math.inf
        cand = [r for r in relays if math.isfinite(top[r])]
        if not cand:
            break
        dt = min((1 - prog[r]) * top[r] for r in cand)
        t += dt
        for r in relays:
            prog[r] = prog[r] + dt / top[r] if math.isfinite(top[r]) else 0.0
        for r in cand:
            if prog[r] >= 1 - 1e-9:
                open_.add(r)
                ev.append((r, t))
        last_top = top
    je = [(e["relay"], e["t"]) for e in sc["events"]]
    same = len(je) == len(ev) and all(x[0] == y[0] and abs(x[1] - y[1]) < 1e-9 for x, y in zip(je, ev))
    mism += not same
    fl = next(l for l in d["lines"] if l["id"] == sc["line"])
    need = {f"{fl['id']}@{fl['a']}", f"{fl['id']}@{fl['b']}"}
    cur, If, _ = solve_ring(sc["kase"], sc["line"], sc["m"], open_)
    good = abs(If) < 1 and all(r in need for r, _ in ev)
    incorrect += not good
    if last_top:
        for r in relays:
            if r not in open_ and math.isfinite(last_top[r]):
                min_margin = min(min_margin, (1 - prog[r]) * last_top[r])
ok = mism == 0 and incorrect == 0
bad += not ok
print(f"[B2] {len(dump['seq'])} defecte în bucla închisă (fiecare 5 % din fiecare linie, max și min): secvențe diferite de motor {mism}, izolări greșite {incorrect} {'✓' if ok else '✗'}")
print(f"[B2] cea mai mică rezervă de timp a unui releu care n-a declanșat, la momentul izolării: {min_margin:.3f} s")
okm = min_margin >= d["cti"] - 1e-6
bad += not okm
print(f"[B2] rezerva ≥ Δt = {d['cti']} s {'✓' if okm else '✗'}")

print("\nREZULTAT:", "TOATE VERIFICĂRILE AU TRECUT" if bad == 0 else f"{bad} ABATERI")
sys.exit(1 if bad else 0)
