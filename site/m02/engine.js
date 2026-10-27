/* Modulul 02 — motorul de calcul: transformatorul de curent pentru protecție.
   (a) dimensionare: sarcina reală, factorul limită de precizie real F_a, verificările pentru releul maximal;
   (b) regim tranzitoriu: integrarea numerică a ecuației TC cu caracteristică de magnetizare neliniară,
       curentul măsurat de releu (filtru Fourier pe o perioadă) și timpul până la saturație.
   Datele de defect și reglajele vin din M01 și M03. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory(require("../m01/engine.js"), require("../m03/engine.js"));
  else root.M02 = factory(root.M01, root.M03);
})(typeof self !== "undefined" ? self : this, function (M01, M03) {
  const W = 2 * Math.PI * 50;
  const RHO_CU = 0.0175;  // Ω·mm²/m, cupru la 20 °C

  const DEFAULTS = {
    relay: "R3",
    Ipn: 300, Isn: 1, cls: "5P", alf: 20, Sn: 10, Rct: 2.0,  // TC 300/1 A, 5P20, 10 VA, R_ct = 2 Ω (exemplu)
    lead: 50, leadA: 2.5, Srelay: 0.1,                          // conductoare 50 m (dus), 2,5 mm² Cu; releu 0,1 VA
    nExp: 13, rem: 0, offset: 1,                                // exponentul curbei de magnetizare; remanența; asimetria (1 = maximă)
    tEnd: 0.2, dt: 5e-5,
  };

  /* Datele de defect și reglajele pentru releul ales (R3 sau R2) */
  function context(p) {
    const net = { ...M01.DEFAULTS };
    const set = M03.autoSettings(net, M03.DEFAULTS).S[p.relay];
    const r = M01.compute(net, "max", "3F", 0, 0);                // defect trifazat maxim la capul plecării / la bare
    const xr = r.z1.im / r.z1.re;
    const r1 = M01.compute(net, "max", "1F", 0, 0);
    return { If: r.Ik, xr, If1: r1.Ik, Is: set.Is, Ih: set.Ih, th: set.th, curve: set.curve, tms: set.tms };
  }

  /* Dimensionarea */
  function sizing(p, c) {
    const Rbn = p.Sn / (p.Isn * p.Isn);                          // sarcina nominală, Ω
    const Rl = (RHO_CU * p.lead) / p.leadA;                       // un conductor, dus
    const Rr = p.Srelay / (p.Isn * p.Isn);                        // intrarea releului
    const Rb1 = Rl + Rr, Rb2 = 2 * Rl + Rr;                       // factorul de buclă 1 (3F) și 2 (nesimetric, acoperitor)
    const Eal = p.alf * p.Isn * (p.Rct + Rbn);                    // t.e.m. limită de precizie
    const Fa1 = (p.alf * (p.Rct + Rbn)) / (p.Rct + Rb1);          // factorul limită real
    const Fa2 = (p.alf * (p.Rct + Rbn)) / (p.Rct + Rb2);
    const needIDMT = (20 * c.Is) / p.Ipn;                         // ABB: F_a > 20·I_pornire/I_1n (treaptă dependentă)
    const needHigh = c.Ih > 0 ? c.Ih / p.Ipn : 0;                 // treapta I>> trebuie să fie sub F_a
    const kF = c.If / p.Ipn;                                       // curentul maxim de defect, în multipli de I_pn
    // factorul de saturație (raportul t.e.m. disponibile la cea cerută de curentul simetric) și timpul până la saturație
    const Ks = Fa1 / kF;
    const ts = timeToSat(Ks * (1 - p.rem), c.xr);
    return { Rbn, Rl, Rr, Rb1, Rb2, Eal, Fa1, Fa2, needIDMT, needHigh, kF, Ks, ts, okIDMT: Math.min(Fa1, Fa2) >= needIDMT, okHigh: needHigh === 0 || Fa1 > needHigh, okSym: Fa1 >= kF };
  }

  /* Timpul până la saturație, curent complet asimetric, fără sarcină inductivă (IEEE C37.110):
     anvelopa fluxului = 1 + (X/R)(1 − e^(−t/T1)); saturația când atinge K_s. */
  function timeToSat(Ks, xr) {
    if (Ks <= 1) return 0;
    if (Ks >= 1 + xr) return Infinity;
    const T1 = xr / W;
    return -T1 * Math.log(1 - (Ks - 1) / xr);
  }

  /* Caracteristica de magnetizare: i_m(λ) = a·λ + b·|λ|^n·sgn(λ), λ în V·s raportat la secundar.
     Calibrare: la t.e.m. limită E_al, valoarea efectivă a curentului de magnetizare = ε·ALF·I_sn (ε = 5 % la 5P, 10 % la 10P);
     la t.e.m. nominală, ε/10 (porțiunea liniară). */
  function magnet(p) {
    const eps = p.cls === "10P" ? 0.1 : 0.05;
    const Eal = p.alf * p.Isn * (p.Rct + p.Sn / (p.Isn * p.Isn));
    const lamAl = (Math.SQRT2 * Eal) / W;
    const n = p.nExp;
    // valoarea efectivă a lui sin^n: √(mean(sin^(2n))) = √((2n−1)!!/(2n)!!)
    let m = 1; for (let k = 1; k <= n; k++) m *= (2 * k - 1) / (2 * k);
    const rmsSinN = Math.sqrt(m);
    const b = (eps * p.alf * p.Isn) / (Math.pow(lamAl, n) * rmsSinN);
    const lamN = lamAl / p.alf;                                   // fluxul la curentul nominal pe sarcina nominală
    const a = ((eps / 10) * p.Isn * Math.SQRT2) / lamN;           // i_m de vârf la nominal = (ε/10)·√2·I_sn (liniar)
    const im = (l) => a * l + b * Math.sign(l) * Math.pow(Math.abs(l), n);
    const dim = (l) => a + b * n * Math.pow(Math.abs(l), n - 1);
    // punctul de cot IEC: +10 % tensiune → +50 % curent; pe curba (E_rms, I_rms) cu flux sinusoidal
    const Irms = (E) => { const lp = (Math.SQRT2 * E) / W; let s = 0; const N = 400; for (let i = 0; i < N; i++) { const v = im(lp * Math.sin((2 * Math.PI * (i + 0.5)) / N)); s += v * v; } return Math.sqrt(s / N); };
    let lo = Eal * 0.05, hi = Eal * 1.5;
    for (let i = 0; i < 60; i++) { const E = Math.sqrt(lo * hi); if (Irms(1.1 * E) / Irms(E) > 1.5) hi = E; else lo = E; }
    const Ek = Math.sqrt(lo * hi);
    return { a, b, n, eps, Eal, lamAl, im, dim, Ek, Ik: Irms(Ek), Irms };
  }

  /* Simularea în timp: curent primar cu componentă aperiodică, TC cu sarcină rezistivă R_ct + R_b,
     integrare implicită (Euler înapoi, cu Newton) — stabilă și în saturație profundă. */
  function simulate(p, c, opts = {}) {
    const mg = magnet(p);
    const n = p.Ipn / p.Isn;
    const Rb = opts.Rb ?? sizing(p, c).Rb1;
    const R = p.Rct + Rb;
    const If = opts.If ?? c.If, xr = opts.xr ?? c.xr, T1 = xr / W;
    const off = opts.offset ?? p.offset;          // 1: asimetrie maximă; 0: simetric
    const dt = opts.dt ?? p.dt, N = Math.round((opts.tEnd ?? p.tEnd) / dt);
    const ipk = Math.SQRT2 * If;
    // i1(t) = √2·I·[ −cos(ωt) + off·e^(−t/T1) ] + (1 − off)·…: pentru off = 1 trece prin zero la t = 0 cu asimetrie maximă
    const i1 = (tt) => ipk * (-Math.cos(W * tt) * off + Math.sin(W * tt) * (1 - off) + off * Math.exp(-tt / T1));
    let lam = p.rem * mg.lamAl;
    const out = { t: [], i1: [], i2: [], im: [], lam: [] };
    let tSat = null;
    for (let k = 0; k <= N; k++) {
      const tt = k * dt;
      if (k > 0) {
        const is = i1(tt) / n;
        // g(λ) = λ − λ_prev − dt·R·(is − i_m(λ)) = 0
        let x = lam;
        for (let it = 0; it < 50; it++) {
          const g = x - lam - dt * R * (is - mg.im(x));
          const gp = 1 + dt * R * mg.dim(x);
          const dx = g / gp; x -= dx;
          if (Math.abs(dx) < 1e-12 * Math.max(1e-6, Math.abs(x))) break;
        }
        lam = x;
      }
      const ii = i1(tt) / n, imv = mg.im(lam);
      out.t.push(tt); out.i1.push(ii); out.i2.push(ii - imv); out.im.push(imv); out.lam.push(lam);
      if (tSat === null && Math.abs(lam) >= mg.lamAl) tSat = tt;
    }
    out.tSat = tSat;
    out.mg = mg; out.R = R; out.n = n;
    return out;
  }

  /* Filtrul Fourier pe o perioadă (cel folosit de releele numerice), eșantionat la fs */
  function dft(sim, fs = 1000) {
    const step = Math.round(1 / fs / (sim.t[1] - sim.t[0]));
    const s = [], tt = [];
    for (let k = 0; k < sim.t.length; k += step) { s.push(sim.i2[k]); tt.push(sim.t[k]); }
    const id = [];
    for (let k = 0; k < sim.t.length; k += step) id.push(sim.i1[k]);
    const Nc = Math.round(fs / 50);
    // înainte de defect curentul e considerat zero (plecare fără sarcină): fereastra se umple treptat
    const at = (arr, j) => (j < 0 ? 0 : arr[j]);
    const mag = (arr, k) => { let re = 0, im = 0; for (let j = 0; j < Nc; j++) { const ang = (2 * Math.PI * j) / Nc; const v = at(arr, k - Nc + 1 + j); re += v * Math.cos(ang); im -= v * Math.sin(ang); } return (Math.SQRT2 / Nc) * Math.hypot(re, im); };
    const out = { t: [], I: [], Iid: [] };
    for (let k = 0; k < s.length; k++) { out.t.push(tt[k]); out.I.push(mag(s, k)); out.Iid.push(mag(id, k)); }
    return out;
  }

  /* Momentul în care măsura releului depășește un prag (secundar) */
  function pickupTime(d, thr) { for (let k = 0; k < d.t.length; k++) if (d.I[k] >= thr) return d.t[k]; return null; }

  /* Eroarea compusă în regim permanent (IEC 61869-2): valoarea efectivă a lui (i2 − i1/n), raportată la I1/n */
  function compositeError(p, Imult, Rb) {
    const c = { If: Imult * p.Ipn, xr: 10 };
    const sim = simulate(p, c, { Rb, offset: 0, tEnd: 0.4, If: Imult * p.Ipn });
    const n0 = Math.round(0.3 / (sim.t[1] - sim.t[0]));       // ultimele 5 perioade
    let se = 0, si = 0, cnt = 0;
    for (let k = n0; k < sim.t.length; k++) { se += sim.im[k] ** 2; si += sim.i1[k] ** 2; cnt++; }
    return Math.sqrt(se / cnt) / Math.sqrt(si / cnt);
  }

  return { DEFAULTS, RHO_CU, context, sizing, timeToSat, magnet, simulate, dft, pickupTime, compositeError };
});
