/* Modulul 06 — motorul de calcul: protecția rețelelor cu generare distribuită.
   Plecarea F1 din rețeaua-exemplu (M01) are o centrală la x_g km: generator sincron (sursă de tensiune în spatele
   lui X″d și al transformatorului bloc) sau centrală cu invertor (sursă de curent k·I_r în secvența pozitivă, cu
   unghiul legat de tensiunea de secvență pozitivă din punctul de racordare). Defecte 3F și 2F pe F1, pe o plecare
   vecină (din rețeaua M05) sau pe bare; curenții văzuți de R3 (capul lui F1), R4 (km 10), releul plecării vecine,
   R2 (sosirea transformatorului) și centrală; tensiunea în punctul de racordare; profilul de trecere prin gol de
   tensiune (NC RfG) și detecția insularizării (ecuația de mișcare a rotorului). */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory(require("../assets/cx.js"), require("../m01/engine.js"), require("../m03/engine.js"));
  else root.M06 = factory(root.CX, root.M01, root.M03);
})(typeof self !== "undefined" ? self : this, function (X, M01, M03) {
  const { C, add, sub, mul, div, scale, abs, argDeg, polar, inv, seq2abc, solve } = X;
  const S3 = Math.sqrt(3);
  const wrap = (d) => ((d + 180) % 360 + 360) % 360 - 180;

  /* plecările vecine: aceleași ca în rețeaua M05 (tipuri de linie din M01) */
  const ADJ = { F2: { type: "cab185", km: 6 }, F4: { type: "ol70", km: 30 }, F6: { type: "ol70", km: 15 } };
  const DEFAULTS = {
    // centrala: generator sincron 6,3 kV cu transformator bloc 6,3/20 kV, sau centrală cu invertor
    dg: "sync", Sg: 5, xd: 0.18, rxg: 0.07, ukT: 7,
    k: 1.5, phiInv: 90, uPLL: 0.1,     // invertor: |I| = k·I_r, în urma lui U1 cu φ (90° = curent reactiv)
    xg: 8,
    // defectul
    fault: "F1", xf: 20, adj: "F4", xa: 30, type: "2F", Rf: 0, kase: "min",
    tmsA: 0.16, IhA: true,               // releul plecării vecine: reglajele lui R3, cu TMS propriu și I>> activ sau nu
    rel: "m03",                          // reglajele releelor de pe F1: "m03" (calculate fără centrală) sau "rev" (revizuite)
    // FRT (NC RfG, art. 14(3)(a)): parametri aleși în intervalele din tabelele 3.1 (sincron) și 3.2 (PPM)
    frt: { sync: { Uret: 0.3, tclr: 0.15, Uclr: 0.7, trec2: 0.7, Urec2: 0.9, trec3: 1.5 }, inv: { Uret: 0.05, tclr: 0.15, Uclr: 0.15, trec2: 0.15, Urec2: 0.85, trec3: 3.0 } },
    tcb: 0.06,                           // timpul de întrerupere al întrerupătorului (3 perioade)
    // insularizarea
    H: 2, PG: 3.5, PL: 4.0, rocof: 1.0, tRocof: 0.5, fmin: 47.5, fmax: 52, tF: 0.5, tRAR: 0.8,
  };

  /* reglajele releelor din M03 (fișa de reglaje); releul plecării vecine are reglajele lui R3, cu TMS propriu */
  const RELAYS = M03.autoSettings({ ...M01.DEFAULTS }, M03.DEFAULTS).S;
  const X4 = M03.DEFAULTS.x4;
  const relayA = (p) => ({ ...RELAYS.R3, tms: p.tmsA, Ih: p.IhA ? RELAYS.R3.Ih : 0 });
  const IrG = (p) => (p.Sg * 1e6) / (S3 * M01.DEFAULTS.Un * 1000);
  const xgOf = (p) => Math.min(Math.max(p.xg, 0.1), M01.DEFAULTS.L);

  /* regimul normal: prin R3 trece exportul centralei (până la I_rG, la sarcină zero), iar prin R4 numai dacă
     centrala e după el. Pragul trebuie să rămână peste curentul maxim: I> ≥ k_sig·k_p·I_max/k_rev (M03). */
  function normalCheck(p0, S) {
    const p = { ...DEFAULTS, ...p0 }, d = M03.DEFAULTS, Ir = p.dg === "none" ? 0 : IrG(p);
    const out = {};
    for (const k of ["R3", "R4"]) {
      const exp = k === "R3" || xgOf(p) > X4 ? Ir : 0;
      const Imax = Math.max(d[k].Iload, exp);
      const need = (d.kSig * d.kP * Imax) / d.kRev;
      out[k] = { Iload: d[k].Iload, exp, Imax, need, Is: S[k].Is, ok: S[k].Is >= need - 1e-9 };
    }
    return out;
  }
  /* reglajele revizuite: procedura M03 (prag, eșalonarea pragurilor, sensibilitate, I>>, TMS) refăcută cu
     curentul maxim de regim normal care include exportul centralei */
  const REVCACHE = new Map();
  function settingsFor(p0) {
    const p = { ...DEFAULTS, ...p0 };
    if (p.rel !== "rev" || p.dg === "none") return RELAYS;
    const Ir = IrG(p), after = xgOf(p) > X4, key = Ir.toFixed(9) + "|" + after;
    if (!REVCACHE.has(key)) {
      const d0 = M03.DEFAULTS;
      const d = { ...d0, R3: { ...d0.R3, Iload: Math.max(d0.R3.Iload, Ir) }, R4: { ...d0.R4, Iload: after ? Math.max(d0.R4.Iload, Ir) : d0.R4.Iload } };
      REVCACHE.set(key, M03.autoSettings({ ...M01.DEFAULTS }, d).S);
    }
    return REVCACHE.get(key);
  }
  /* centrala e pe F1, după TC-ul lui R3: x_g ≥ 0,1 km (la x_g = 0 ar fi pe bare, înaintea lui R3) */
  const XGMIN = 0.1;
  /* un defect pe F1 „la 0 km” e imediat după TC-ul lui R3 (nu pe bare): x_f ≥ 0,01 km */
  const XFMIN = 0.01;

  function compute(p0) {
    const p = { ...DEFAULTS, ...p0 };
    const net = { ...M01.DEFAULTS };
    const src = M01.source(net, p.kase);
    const c = p.kase === "max" ? net.cmax : net.cmin;
    const E = C((c * net.Un * 1000) / S3, 0);
    const kth = p.kase === "min" ? 1 + 0.004 * (net.thetaE - 20) : 1;   // R_L(θe), ca în M01
    const zkm = C(net.R1 * kth, net.X1);
    const A = ADJ[p.adj], LA = M01.LINES[A.type], zkmA = C(LA.R1 * kth, LA.X1);
    const has = p.dg !== "none";
    // nodurile plecării F1 (poziții, km); nodul 0 = barele
    const rnd = (v) => Math.round(v * 1e6) / 1e6;
    const pos = [0, X4, net.L];
    const xg = xgOf(p);
    if (has) pos.push(xg);
    const xf = Math.min(Math.max(p.xf, XFMIN), net.L);
    if (p.fault === "F1") pos.push(xf);
    const P = [...new Set(pos.map((v) => rnd(Math.min(Math.max(v, 0), net.L))))].sort((a, b) => a - b);
    const idx = new Map(P.map((v, i) => [v, i]));
    let n = P.length;
    const segs = [];
    for (let i = 0; i + 1 < P.length; i++) segs.push({ a: i, b: i + 1, z: scale(zkm, P[i + 1] - P[i]), line: "F1", from: P[i] });
    let nA = -1;
    if (p.fault === "adj") { nA = n++; segs.push({ a: 0, b: nA, z: scale(zkmA, Math.min(Math.max(p.xa, 1e-6), A.km)), line: "A", from: 0 }); }
    const fNode = p.fault === "bus" ? 0 : p.fault === "adj" ? nA : idx.get(rnd(xf));
    const gNode = has ? idx.get(rnd(xg)) : -1;
    // generatorul sincron și transformatorul bloc, raportate la 20 kV: R_Gf = r·X″d (IEC 60909-0), R_T neglijat
    const Ir = (p.Sg * 1e6) / (S3 * net.Un * 1000);
    const zb = (net.Un * net.Un) / p.Sg;
    const zg = has && p.dg === "sync" ? C(p.rxg * p.xd * zb, (p.xd + p.ukT / 100) * zb) : null;
    const Y = Array.from({ length: n }, () => Array.from({ length: n }, () => C(0)));
    const ad = (i, j, y) => { Y[i][i] = add(Y[i][i], y); if (j >= 0) { Y[j][j] = add(Y[j][j], y); Y[i][j] = sub(Y[i][j], y); Y[j][i] = sub(Y[j][i], y); } };
    ad(0, -1, inv(src.z1bus));
    if (zg) ad(gNode, -1, inv(zg));
    segs.forEach((s) => ad(s.a, s.b, inv(s.z)));
    // secvența negativă are aceeași matrice (Z2 = Z1 pentru rețea, linii și generator — X2 ≈ X″d, simplificare)
    const e = (k) => Array.from({ length: n }, (_, i) => C(i === k ? 1 : 0));
    const Zc = solve(Y, e(fNode));                       // coloana fNode a matricei Z_bus
    const inj = (Iinv) => {
      const I = Array.from({ length: n }, () => C(0));
      I[0] = div(E, src.z1bus);
      if (zg) I[gNode] = add(I[gNode], div(E, zg));
      if (has && p.dg === "inv") I[gNode] = add(I[gNode], Iinv);
      return I;
    };
    const zf = p.type === "3F" ? add(Zc[fNode], C(p.Rf, 0)) : add(scale(Zc[fNode], 2), C(p.Rf, 0));
    const run = (th) => {
      const Iinv = has && p.dg === "inv" ? polar(p.k * Ir, th - p.phiInv) : C(0);
      const Voc = solve(Y, inj(Iinv));
      const I1f = div(Voc[fNode], zf);
      const V1 = Voc.map((v, i) => sub(v, mul(Zc[i], I1f)));
      const V2 = p.type === "3F" ? V1.map(() => C(0)) : Zc.map((z) => mul(z, I1f));
      return { Iinv, I1f, V1, V2 };
    };
    // invertorul: punct fix pe unghiul tensiunii de secvență pozitivă din punctul de racordare (θ = arg U1g), cu
    // relaxare 0,5. Sub uPLL·E unghiul tensiunii nu mai e o referință sigură, iar la un defect franc 3F între
    // rețea și centrală U1g e produsă numai de curentul invertorului și punctul fix nu există: atunci modelul
    // păstrează unghiul de dinainte de defect (0°). Ipoteză de model — comportarea reală depinde de algoritmul PLL.
    const isInv = has && p.dg === "inv";
    let th = 0, iter = 0, conv = !isInv, frozen = false, sol = run(0);
    if (isInv) {
      for (; iter < 300; iter++) {
        if (abs(sol.V1[gNode]) < p.uPLL * abs(E)) break;
        const d = wrap(argDeg(sol.V1[gNode]) - th);
        if (Math.abs(d) < 1e-7) { conv = true; break; }
        th = wrap(th + 0.5 * d);
        sol = run(th);
      }
      if (!conv || abs(sol.V1[gNode]) < p.uPLL * abs(E)) { frozen = true; th = 0; sol = run(0); }
    }
    const { Iinv, I1f, V1, V2 } = sol;
    const br = (s) => { const i1 = div(sub(V1[s.a], V1[s.b]), s.z), i2 = div(sub(V2[s.a], V2[s.b]), s.z); return { i1, i2, abc: seq2abc(C(0), i1, i2) }; };
    const seg3 = segs.find((s) => s.line === "F1" && s.a === 0);
    const seg4 = segs.find((s) => s.line === "F1" && Math.abs(s.from - X4) < 1e-9);
    const segA = segs.find((s) => s.line === "A");
    const R3 = br(seg3), R4 = br(seg4), RA = segA ? br(segA) : null;
    // sosirea transformatorului (R2): curentul rețelei din amonte
    const i1s = div(sub(E, V1[0]), src.z1bus), i2s = scale(div(V2[0], src.z1bus), -1);
    const R2 = { i1: i1s, i2: i2s, abc: seq2abc(C(0), i1s, i2s) };
    let dgI = null;
    if (has) {
      const i1 = p.dg === "sync" ? div(sub(E, V1[gNode]), zg) : Iinv;
      const i2 = p.dg === "sync" ? scale(div(V2[gNode], zg), -1) : C(0);
      dgI = { i1, i2, abc: seq2abc(C(0), i1, i2) };
    }
    const If = seq2abc(C(0), I1f, p.type === "3F" ? C(0) : scale(I1f, -1));
    const mag = (o) => (o ? Math.max(...o.abc.map(abs)) : 0);
    const Vabc = (k) => seq2abc(C(0), V1[k], V2[k]);
    const vll = (k) => { const v = Vabc(k); return Math.min(abs(sub(v[0], v[1])), abs(sub(v[1], v[2])), abs(sub(v[2], v[0]))) / (abs(E) * S3); };
    // direcția lui R3: fiecare element de fază cu conexiunea la 90° și θc = 30° (ca în M04), cu tensiunea de memorie
    // (dinainte de defect) când tensiunea de polarizare scade sub 5 %. Contează elementele pornite (|I| ≥ I> al lui R3);
    // dacă niciunul nu a pornit, se afișează decizia elementelor cu curent semnificativ (≥ 10 % din maxim).
    const vb = Vabc(0), pol = [[1, 2], [2, 0], [0, 1]], Epre = seq2abc(C(0), E, C(0)), Unom = abs(E) * S3, SET = settingsFor(p);
    const Imax3 = Math.max(...R3.abc.map(abs));
    const ph = [0, 1, 2].map((i) => {
      const [u, v] = pol[i];
      let Vp = sub(vb[u], vb[v]), mem = false;
      if (abs(Vp) < 0.05 * Unom) { Vp = sub(Epre[u], Epre[v]); mem = true; }
      const ang = wrap(argDeg(R3.abc[i]) - argDeg(Vp) - 30);
      return { I: abs(R3.abc[i]), ang, mem, fwd: Math.cos((ang * Math.PI) / 180) > 0, active: abs(R3.abc[i]) >= SET.R3.Is };
    });
    let act = ph.filter((x) => x.active);
    const picked = act.length > 0;
    if (!picked) act = ph.filter((x) => Imax3 > 1e-6 && x.I >= 0.1 * Imax3);
    const dirR3 = act.length ? (act.every((x) => x.fwd) ? "fwd" : act.every((x) => !x.fwd) ? "rev" : "mixed") : "none";
    const angR3 = (act.length ? act.reduce((m, x) => (x.I > m.I ? x : m)) : ph[0]).ang;
    return {
      p, E, Ir, zg, iter, conv, frozen, thInv: th, fNode, gNode, nodes: P,
      IR3: mag(R3), IR4: mag(R4), IA: mag(RA), IR2: mag(R2), IDG: mag(dgI), IF: Math.max(...If.map(abs)),
      dirR3, dirPicked: picked, dirPh: ph, angR3, R3fwd: dirR3 === "fwd" ? true : dirR3 === "rev" ? false : null,
      trip67: act.some((x) => x.fwd),   // un 67 pe R3 declanșează dacă cel puțin un element pornit vede „înainte”
      V1g: has ? abs(V1[gNode]) / abs(E) : null, VLLg: has ? vll(gNode) : null, VLLbus: vll(0),
      R3, R4, RA, R2, dgI, If,
    };
  }

  /* timpii releelor (reglajele din M03): R3 și R4 pe F1, A pe plecarea vecină, R2 pe sosire */
  function times(r) {
    const tR = (S, I) => (I > 0 ? M03.tripTime(S, I, M03.DEFAULTS.tOwn).t : Infinity);
    const S = settingsFor(r.p);
    return {
      R3: tR(S.R3, r.IR3),
      R4: tR(S.R4, r.IR4),   // nedirecțional: vede și curentul invers al unei centrale aflate după el
      A: tR(relayA(r.p), r.IA),
      R2: tR(S.R2, r.IR2),
    };
  }

  /* cine elimină defectul și când (timpul releului + întrerupătorul); null dacă nu îl vede nimeni */
  function clearing(r) {
    const t = times(r), p = r.p;
    let who = null, tr = Infinity;
    if (p.fault === "F1") { if (p.xf >= X4 && t.R4 < Infinity) { who = "R4"; tr = t.R4; } if (t.R3 < tr) { who = "R3"; tr = t.R3; } }
    else if (p.fault === "adj") { who = "A"; tr = t.A; }
    else { who = "R2"; tr = t.R2; }
    if (!(tr < Infinity) && t.R2 < Infinity) { who = "R2"; tr = t.R2; }
    return { who: tr < Infinity ? who : null, t: tr < Infinity ? tr + p.tcb : Infinity, relay: tr, times: t };
  }

  /* declanșarea simpatică a releelor nedirecționale de pe F1 la defecte pe plecarea vecină: R3 (și R4, dacă centrala
     e după el) vede curentul centralei „înapoi”; e acceptabil numai dacă nu pornește sau e mai lent decât releul
     plecării vecine cu cel puțin Δt. Defectul pe bare e raportat separat: acolo declanșarea e utilă (oprește
     alimentarea defectului de către centrală). */
  function sympathetic(p0, cti = M03.DEFAULTS.cti) {
    const p = { ...DEFAULTS, ...p0 };
    const L = ADJ[p.adj].km, rows = [], bus = [];
    for (const kase of ["max", "min"]) for (const type of ["3F", "2F"]) {
      for (let i = 0; i <= 20; i++) {
        const r = compute({ ...p, fault: "adj", xa: (L * i) / 20, type, kase, Rf: 0 });
        const t = times(r);
        rows.push({ x: (L * i) / 20, type, kase, IR3: r.IR3, IR4: r.IR4, IA: r.IA, tR3: t.R3, tR4: t.R4, tA: t.A, mR3: t.R3 - t.A, mR4: t.R4 - t.A, dir: r.dirR3, trip67: r.trip67 && r.dirPicked });
      }
      const r = compute({ ...p, fault: "bus", type, kase, Rf: 0 });
      const t = times(r);
      bus.push({ type, kase, IR3: r.IR3, IR4: r.IR4, tR3: t.R3, tR4: t.R4, tR2: t.R2, dir: r.dirR3, trip67: r.trip67 && r.dirPicked });
    }
    let worst = null;
    rows.forEach((x) => ["R3", "R4"].forEach((k) => {
      const tt = x["t" + k], m = x["m" + k];
      if (tt < Infinity && (!worst || m < worst.margin)) worst = { ...x, relay: k, tRel: tt, margin: m, I: x["I" + k] };
    }));
    const maxRev = Math.max(...rows.map((x) => x.IR3)), maxRev4 = Math.max(...rows.map((x) => x.IR4));
    return { rows, bus, worst, maxRev, maxRev4, pickup: !!worst, ok: !worst || worst.margin >= cti - 1e-9, cti };
  }

  /* orbirea lui R3: curentul văzut în lungul lui F1, cu și fără centrală (2F, regim minim);
     sensibilitatea ca rezervă la capătul liniei */
  function blinding(p0) {
    const p = { ...DEFAULTS, ...p0 }, L = M01.DEFAULTS.L, pts = [];
    for (let i = 0; i <= 40; i++) {
      const xf = (L * i) / 40;
      const w = compute({ ...p, fault: "F1", xf, type: "2F", kase: "min", Rf: 0 });
      const o = compute({ ...p, dg: "none", fault: "F1", xf, type: "2F", kase: "min", Rf: 0 });
      pts.push({ xf, with: w.IR3, without: o.IR3, dgI: w.IDG });
    }
    const end = pts[pts.length - 1], Is = settingsFor(p).R3.Is;
    return { pts, kEnd: end.with / Is, kEnd0: end.without / Is, red: 1 - end.with / end.without, Is };
  }

  /* profilul tensiune–timp NC RfG (limita inferioară): tensiunea minimă la care centrala trebuie să rămână conectată */
  function frtLimit(f, t) {
    if (t < 0) return 1;
    if (t <= f.tclr) return f.Uret;
    if (t <= f.trec2) return f.Uclr;
    if (t <= f.trec3) return f.Uclr + ((f.Urec2 - f.Uclr) * (t - f.trec2)) / Math.max(f.trec3 - f.trec2, 1e-9);
    return f.Urec2;
  }
  /* defect eliminat la t_clr, cu tensiunea u constantă până atunci (apoi revine; simplificare):
     dacă u ≥ limita pe tot intervalul, centrala trebuie să rămână conectată */
  function frtCheck(f, u, tclr) {
    const T = Math.min(tclr, 10);
    let worst = Infinity, at = 0;
    for (let i = 0; i <= 2000; i++) { const t = (T * i) / 2000; const m = u - frtLimit(f, t); if (m < worst) { worst = m; at = t; } }
    return { mustStay: worst >= 0, margin: worst, at };
  }
  /* compatibilitatea treptei U< cu profilul: cât timp poate sta tensiunea sub U_set fără ca centrala să aibă voie
     să se deconecteze (D). Treapta e compatibilă dacă t_set > D și U_set ≤ U_rec2. */
  function underVoltageCompat(f, Uset, tset) {
    if (Uset > f.Urec2 + 1e-12) return { D: Infinity, ok: false };
    let D;
    if (Uset <= f.Uret) D = 0;
    else if (Uset <= f.Uclr) D = f.tclr;
    else if (f.Urec2 > f.Uclr) D = f.trec2 + ((Uset - f.Uclr) / (f.Urec2 - f.Uclr)) * (f.trec3 - f.trec2);
    else D = f.trec2;
    return { D, ok: tset > D };
  }

  /* insularizarea: viteza de variație a frecvenței (ecuația de mișcare, fără regulatoare) și timpii de detecție */
  function island(p0) {
    const p = { ...DEFAULTS, ...p0 };
    const rocof = ((p.PG - p.PL) / p.Sg) * (50 / (2 * p.H));        // Hz/s
    const tf = rocof < 0 ? (50 - p.fmin) / -rocof : rocof > 0 ? (p.fmax - 50) / rocof : Infinity;
    const tFreq = tf + p.tF;
    const tRoc = Math.abs(rocof) >= p.rocof ? p.tRocof : Infinity;
    const tDet = Math.min(tFreq, tRoc);
    return { rocof, tFreq, tRoc, tDet, tOff: tDet + p.tcb, beforeRAR: tDet + p.tcb < p.tRAR };
  }
  /* zona nedetectată (înainte de RAR): dezechilibrele ΔP/S_g pentru care centrala e încă conectată la reanclanșare.
     Detectat la timp: |RoCoF| ≥ RoCoF> (dacă t_RoCoF + t_CB < t_RAR) sau frecvența atinge pragul înainte de
     t_RAR − t_CB − t_f. Cum |RoCoF| = |ΔP|/S_g·f0/(2H), fiecare criteriu dă o limită pe |ΔP|/S_g. */
  function ndz(p0) {
    const p = { ...DEFAULTS, ...p0 };
    const k = 50 / (2 * p.H);                                   // Hz/s pentru ΔP/S_g = 1
    const dRoc = p.tRocof + p.tcb < p.tRAR ? p.rocof / k : Infinity;
    const tw = p.tRAR - p.tcb - p.tF;                           // timpul disponibil frecvenței să atingă pragul
    const dLo = tw > 0 ? (50 - p.fmin) / tw / k : Infinity, dHi = tw > 0 ? (p.fmax - 50) / tw / k : Infinity;
    const pts = [];
    for (let i = -100; i <= 100; i++) { const d = i / 200; const r = island({ ...p, PG: p.PL + d * p.Sg }); pts.push({ d, t: r.tOff, ok: r.beforeRAR }); }
    return { pts, lo: -Math.min(dRoc, dLo), hi: Math.min(dRoc, dHi), dRoc, k };
  }

  return { DEFAULTS, ADJ, X4, XGMIN, XFMIN, RELAYS, relayA, IrG, normalCheck, settingsFor, compute, times, clearing, sympathetic, blinding, frtLimit, frtCheck, underVoltageCompat, island, ndz, wrap };
});
