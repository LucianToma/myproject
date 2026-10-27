/* Modulul 04 — motorul de calcul: protecția maximală direcțională (67/67N).
   Partea A: elementul direcțional pe linia A–B alimentată de la ambele capete (conexiunea la 90°, polarizarea homopolară).
   Partea B: bucla închisă de 20 kV cu o singură sursă: reglaje în sens orar și antiorar (inelul deschis la sursă)
             și simularea secvenței de declanșare în bucla închisă. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory(require("../assets/cx.js"), require("../m01/engine.js"), require("../m03/engine.js"));
  else root.M04 = factory(root.CX, root.M01, root.M03);
})(typeof self !== "undefined" ? self : this, function (X, M01, M03) {
  const { C, add, sub, mul, div, scale, abs, argDeg, polar, inv, seq2abc } = X;
  const S3 = Math.sqrt(3);
  const wrap = (d) => { let x = ((d + 180) % 360 + 360) % 360 - 180; return x; };

  /* ------------------------------------------------------------------ */
  /* rezolvarea unei rețele mici, pe secvențe, cu matrice de admitanțe   */
  function solveLinear(Y, I) {
    // eliminare Gauss cu pivotare, numere complexe
    const n = I.length, A = Y.map((r) => r.slice()), b = I.slice();
    for (let k = 0; k < n; k++) {
      let piv = k, best = abs(A[k][k]);
      for (let i = k + 1; i < n; i++) if (abs(A[i][k]) > best) { best = abs(A[i][k]); piv = i; }
      [A[k], A[piv]] = [A[piv], A[k]]; [b[k], b[piv]] = [b[piv], b[k]];
      for (let i = k + 1; i < n; i++) {
        const f = div(A[i][k], A[k][k]);
        for (let j = k; j < n; j++) A[i][j] = sub(A[i][j], mul(f, A[k][j]));
        b[i] = sub(b[i], mul(f, b[k]));
      }
    }
    const x = new Array(n).fill(C(0));
    for (let i = n - 1; i >= 0; i--) {
      let s = b[i];
      for (let j = i + 1; j < n; j++) s = sub(s, mul(A[i][j], x[j]));
      x[i] = div(s, A[i][i]);
    }
    return x;
  }
  const zeros = (n) => Array.from({ length: n }, () => Array.from({ length: n }, () => C(0)));
  function addBranch(Y, i, j, y) {
    if (i >= 0) Y[i][i] = add(Y[i][i], y);
    if (j >= 0) Y[j][j] = add(Y[j][j], y);
    if (i >= 0 && j >= 0) { Y[i][j] = sub(Y[i][j], y); Y[j][i] = sub(Y[j][i], y); }
  }
  /* coloana f a matricei de impedanțe (Y⁻¹·e_f) */
  function zcol(Y, f) { const e = Y.map((_, i) => C(i === f ? 1 : 0)); return solveLinear(Y, e); }

  /* ============================ PARTEA A ============================ */
  const NET = { ...M01.DEFAULTS };
  const DEF_A = {
    lenL: 5, R1: 0.161, X1: 0.117, R0: 0.861, X0: 0.117,      // linia A–B: LES Al 185 mm² (ca în M01)
    SkB: 100, rxB: 0.1, gB: false, k0B: 1,                      // sursa de la capătul B (exemplu: o centrală sau o altă alimentare)
    type: "2F", dir: "fwd", m: 0.5, Rf: 0, kase: "max",
    rca: 30, rcaN: 0,
    Is: 255, IsN: 40,                                            // pragurile I> (din M03, R3) și I0> (exemplu; reglajul lui e în M05)
  };

  function partA(p) {
    const net = { ...NET };
    const sA = M01.source(net, p.kase), zA0 = M01.zeroBus(net).z0bus;
    const c = p.kase === "max" ? net.cmax : net.cmin;
    const E = C((c * net.Un * 1000) / S3, 0);
    const zSA = [zA0, sA.z1bus, sA.z1bus];                                   // secvențele 0, 1, 2 (Z2 = Z1)
    const zB1 = X.zRX((c * net.Un * net.Un) / p.SkB, p.rxB);
    const zSB = [p.gB ? scale(zB1, p.k0B) : null, zB1, zB1];
    const zL = [C(p.R0 * p.lenL, p.X0 * p.lenL), C(p.R1 * p.lenL, p.X1 * p.lenL), C(p.R1 * p.lenL, p.X1 * p.lenL)];
    const fwd = p.dir === "fwd", m = Math.min(Math.max(p.m, 0.001), 0.999);
    // nodurile: 0 = A, 1 = B, 2 = F (numai pentru defectul înainte)
    const n = fwd ? 3 : 2, f = fwd ? 2 : 0;
    const Ys = [0, 1, 2].map((k) => {
      const Y = zeros(n);
      addBranch(Y, 0, -1, inv(zSA[k]));
      if (zSB[k]) addBranch(Y, 1, -1, inv(zSB[k]));
      if (fwd) { addBranch(Y, 0, 2, inv(scale(zL[k], m))); addBranch(Y, 2, 1, inv(scale(zL[k], 1 - m))); }
      else addBranch(Y, 0, 1, inv(zL[k]));
      return Y;
    });
    const Zc = Ys.map((Y) => zcol(Y, f));
    const zth = Zc.map((col) => col[f]);
    const fl = M01.solveFault(p.type, E, zth[1], zth[2], zth[0], p.Rf);
    const If = [fl.I0, fl.I1, fl.I2];
    const V = [0, 1, 2].map((k) => Zc[k].map((z, i) => sub(k === 1 ? E : C(0), mul(z, If[k]))));
    // curentul releului (de la A spre linie) și tensiunea la A, pe secvențe
    const Irel = [0, 1, 2].map((k) => fwd ? div(sub(V[k][0], V[k][2]), scale(zL[k], m)) : div(sub(V[k][0], V[k][1]), zL[k]));
    const Vrel = [0, 1, 2].map((k) => V[k][0]);
    const Iabc = seq2abc(Irel[0], Irel[1], Irel[2]);
    const Vabc = seq2abc(Vrel[0], Vrel[1], Vrel[2]);
    const Epre = seq2abc(C(0), E, C(0));
    return { E, zSA, zSB, zL, zth, fault: fl, Irel, Vrel, Iabc, Vabc, Epre, dirs: directional(Iabc, Vabc, Epre, Irel, Vrel, p), IfMag: Math.max(...fl.Iabc.map(abs)) };
  }

  /* Elementele direcționale: fază (conexiunea la 90°) și homopolar (−3U0) */
  function directional(Iabc, Vabc, Epre, Irel, Vrel, p) {
    const pol = [[1, 2], [2, 0], [0, 1]];                  // L1: U23, L2: U31, L3: U12
    const Unom = abs(Epre[0]) * S3;
    // un element contează numai dacă a pornit: curentul lui depășește pragul releului
    const ph = [0, 1, 2].map((i) => {
      const [a, b] = pol[i];
      let Vp = sub(Vabc[a], Vabc[b]), mem = false;
      if (abs(Vp) < 0.05 * Unom) { Vp = sub(Epre[a], Epre[b]); mem = true; }   // tensiune de memorie (dinainte de defect)
      const ang = wrap(argDeg(Iabc[i]) - argDeg(Vp) - p.rca);
      return { I: Iabc[i], Vp, mem, ang, fwd: Math.cos((ang * Math.PI) / 180) > 0, active: abs(Iabc[i]) >= p.Is };
    });
    const I0 = scale(Irel[0], 3), Vn = scale(Vrel[0], -3);
    const angN = wrap(argDeg(I0) - argDeg(Vn) - p.rcaN);
    // elementul homopolar cere și o tensiune de polarizare minimă (aici 1 % din tensiunea de fază)
    const gnd = { I: I0, Vp: Vn, ang: angN, fwd: Math.cos((angN * Math.PI) / 180) > 0, active: abs(I0) >= p.IsN && abs(Vn) > 0.01 * abs(Epre[0]) };
    const act = ph.filter((x) => x.active);
    const phase = act.length ? (act.every((x) => x.fwd) ? "fwd" : act.every((x) => !x.fwd) ? "rev" : "mixed") : "none";
    const ground = gnd.active ? (gnd.fwd ? "fwd" : "rev") : "none";
    return { ph, gnd, phase, ground };
  }

  /* unghiul caracteristic recomandat: cel al curentului de defect față de tensiunea de polarizare, pentru defecte înainte */
  function rcaStudy(p) {
    const out = [];
    ["3F", "2F"].forEach((type) => [0.1, 0.5, 0.9].forEach((m) => {
      const r = partA({ ...p, type, dir: "fwd", m, rca: 0, Is: 1 });
      r.dirs.ph.forEach((x, i) => { if (x.active) out.push({ type, m, ph: i, lead: x.ang }); });
    }));
    const r0 = partA({ ...p, type: "1F", dir: "fwd", m: 0.5, rcaN: 0, IsN: 1 });
    return { phase: out, groundLead: r0.dirs.gnd.ang, z0angle: argDeg(r0.zSA[0]) };
  }

  /* ============================ PARTEA B ============================ */
  const DEF_B = {
    R1: 0.161, X1: 0.117,                        // LES Al 185 mm²
    lines: [{ id: "AB", a: "A", b: "B", km: 4 }, { id: "BC", a: "B", b: "C", km: 3 }, { id: "CD", a: "C", b: "D", km: 3 }, { id: "DA", a: "D", b: "A", km: 5 }],
    Iload: 200, ct: 300, curve: "IEC-SI", kSig: 1.2, kRev: 0.95, kP: 1, cti: 0.3, tmsMin: 0.05, tOwn: 0.03, rca: 30,
  };
  const BUS = ["A", "B", "C", "D"];
  const relaysOf = (d) => d.lines.flatMap((l) => [`${l.id}@${l.a}`, `${l.id}@${l.b}`]);
  /* lanțurile de coordonare (inelul deschis la sursă): de la capătul îndepărtat spre sursă */
  const CHAINS = { cw: ["DA@D", "CD@C", "BC@B", "AB@A"], ccw: ["AB@B", "BC@C", "CD@D", "DA@A"] };

  /* soluția rețelei inelare pentru un defect trifazat pe linia L, la fracția m de la capătul a;
     open: mulțimea capetelor de linie deschise */
  function ringSolve(d, kase, fault, open) {
    const net = { ...NET };
    const s = M01.source(net, kase);
    const c = kase === "max" ? net.cmax : net.cmin;
    const E = C((c * net.Un * 1000) / S3, 0);
    const z = (l) => C(d.R1 * l.km, d.X1 * l.km);
    const idx = { A: 0, B: 1, C: 2, D: 3 };
    const n = 4;
    const Y = zeros(n), I = new Array(n).fill(C(0));
    const ys = inv(s.z1bus);
    addBranch(Y, 0, -1, ys); I[0] = mul(E, ys);
    const segs = [];  // {line, from(bus), to(bus|"F"), z}
    d.lines.forEach((l) => {
      const oa = open.has(`${l.id}@${l.a}`), ob = open.has(`${l.id}@${l.b}`);
      if (fault && fault.line === l.id) {
        const za = scale(z(l), fault.m), zb = scale(z(l), 1 - fault.m);
        // defectul franc: punctul F e la pământ
        if (!oa) { addBranch(Y, idx[l.a], -1, inv(za)); segs.push({ line: l.id, bus: l.a, other: "F", z: za }); }
        if (!ob) { addBranch(Y, idx[l.b], -1, inv(zb)); segs.push({ line: l.id, bus: l.b, other: "F", z: zb }); }
      } else if (!oa && !ob) {
        addBranch(Y, idx[l.a], idx[l.b], inv(z(l)));
        segs.push({ line: l.id, bus: l.a, other: l.b, z: z(l) }, { line: l.id, bus: l.b, other: l.a, z: z(l) });
      }
    });
    // nodurile izolate (fără nicio legătură) primesc o admitanță mică, ca sistemul să rămână rezolvabil
    for (let i = 0; i < n; i++) if (abs(Y[i][i]) === 0) Y[i][i] = C(1e-9);
    const V = solveLinear(Y, I);
    const Vb = (b) => (b === "F" ? C(0) : V[idx[b]]);
    const cur = {};
    segs.forEach((sg) => { cur[`${sg.line}@${sg.bus}`] = { I: div(sub(Vb(sg.bus), Vb(sg.other)), sg.z), V: Vb(sg.bus) }; });
    const Ifault = segs.filter((sg) => sg.other === "F").reduce((acc, sg) => add(acc, cur[`${sg.line}@${sg.bus}`].I), C(0));
    return { E, V, cur, Ifault, zS: s.z1bus };
  }

  /* direcția văzută de un releu de linie (conexiunea la 90°, fază L1, defect trifazat) */
  function ringDir(I, V, E, rca) {
    const V1 = abs(V) < 0.05 * abs(E) ? E : V;      // memorie de tensiune la defect apropiat
    const Vp = mul(V1, C(0, -S3));                  // U23 = −j√3·U1 pentru sistem simetric
    const ang = wrap(argDeg(I) - argDeg(Vp) - rca);
    return { ang, fwd: Math.cos((ang * Math.PI) / 180) > 0, mem: V1 === E };
  }

  /* reglajele automate: pragul din curentul de sarcină, apoi TMS pe lanțuri, cu inelul deschis la sursă */
  function ringSettings(d) {
    const S = {};
    const st = d.ct * 0.01;
    const Is = Math.ceil((d.kSig * d.kP * d.Iload) / d.kRev / st - 1e-9) * st;
    relaysOf(d).forEach((r) => (S[r] = { curve: d.curve, Is, tms: d.tmsMin, Ih: 0, th: 0 }));
    const rep = { Is, chains: {} };
    Object.entries(CHAINS).forEach(([dir, chain]) => {
      const openAt = dir === "cw" ? "DA@A" : "AB@A";
      rep.chains[dir] = [];
      for (let i = 1; i < chain.length; i++) {
        const dn = chain[i - 1], up = chain[i];
        const [line, bus] = dn.split("@");
        const L = d.lines.find((l) => l.id === line);
        const m = bus === L.a ? 0.001 : 0.999;
        const r = ringSolve(d, "max", { line, m }, new Set([openAt]));
        const Imax = abs(r.cur[dn].I);
        let need = 0, at = null;
        const lo = M03.GT * Math.max(S[dn].Is, S[up].Is) * 1.0001;
        for (let k = 0; k <= 160 && Imax > lo; k++) {
          const Ii = lo * Math.pow(Imax / lo, k / 160);
          const tdn = M03.tripTime(S[dn], Ii, d.tOwn).t;
          if (!isFinite(tdn)) continue;
          const tms = (tdn + d.cti) / M03.curveTime(S[up].curve, Ii / S[up].Is);
          if (tms > need) { need = tms; at = { I: Ii, tdn }; }
        }
        S[up].tms = Math.max(d.tmsMin, Math.ceil(need * 100 - 1e-9) / 100);
        rep.chains[dir].push({ dn, up, Imax, need, at, tms: S[up].tms });
      }
    });
    return { S, rep };
  }

  /* simularea secvenței de declanșare în bucla închisă: releele integrează 1/t(I) cât timp sunt pornite */
  function ringSequence(d, S, kase, fault, maxEvents = 8) {
    const open = new Set(), prog = {}, events = [];
    const relays = relaysOf(d);
    relays.forEach((r) => (prog[r] = 0));
    let t = 0, last = null;
    for (let it = 0; it < maxEvents; it++) {
      const sol = ringSolve(d, kase, fault, open);
      if (abs(sol.Ifault) < 1) break;                 // defectul nu mai e alimentat
      const top = {};
      relays.forEach((r) => {
        if (open.has(r) || !sol.cur[r]) { top[r] = Infinity; return; }
        const { I, V } = sol.cur[r];
        const dr = ringDir(I, V, sol.E, d.rca);
        top[r] = dr.fwd ? M03.tripTime(S[r], abs(I), d.tOwn).t : Infinity;
      });
      const cand = relays.filter((r) => isFinite(top[r]));
      if (!cand.length) { last = { sol, top, stuck: true }; break; }
      const dt = Math.min(...cand.map((r) => (1 - prog[r]) * top[r]));
      t += dt;
      relays.forEach((r) => { prog[r] = isFinite(top[r]) ? prog[r] + dt / top[r] : 0; });
      const fired = cand.filter((r) => prog[r] >= 1 - 1e-9);
      fired.forEach((r) => { open.add(r); events.push({ relay: r, t, I: abs(sol.cur[r].I) }); });
      last = { sol, top };
    }
    // după izolare: cât le mai trebuia celorlalte relee pornite (rezerva de timp)
    const sol = ringSolve(d, kase, fault, open);
    const isolated = abs(sol.Ifault) < 1;
    const fl = d.lines.find((l) => l.id === fault.line);
    const need = [`${fl.id}@${fl.a}`, `${fl.id}@${fl.b}`];
    const correct = isolated && events.every((e) => need.includes(e.relay));
    let margin = Infinity;
    if (last && last.top) relays.forEach((r) => { if (!open.has(r) && isFinite(last.top[r])) margin = Math.min(margin, (1 - prog[r]) * last.top[r] + 0); });
    return { events, isolated, correct, tClear: events.length ? events[events.length - 1].t : null, margin, open };
  }

  return { NET, DEF_A, partA, directional, rcaStudy, DEF_B, BUS, CHAINS, relaysOf, ringSolve, ringDir, ringSettings, ringSequence, solveLinear, wrap };
});
