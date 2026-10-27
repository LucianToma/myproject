/* Modulul 01 — motorul de calcul: curenți de defect pe o plecare MT radială (IEC 60909-0, componente simetrice).
   Toate impedanțele sunt raportate la tensiunea MT (Ω). Rulează în browser (global M01) și în Node (teste). */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory(require("../assets/cx.js"));
  else root.M01 = factory(root.CX);
})(typeof self !== "undefined" ? self : this, function (X) {
  const { C, add, sub, mul, div, scale, abs, argDeg, polar, par, seq2abc } = X;
  const S3 = Math.sqrt(3);
  const W = 2 * Math.PI * 50;

  /* Rețeaua-exemplu a cursului (date de exemplu, modificabile în pagină) */
  const DEFAULTS = {
    UnQ: 110, SkQmax: 3000, SkQmin: 1500, rxQ: 0.1,          // rețeaua 110 kV
    Sr: 25, UrHV: 110, UrLV: 20, uk: 12, Pk: 102.5, clock: 11, // T1: tipul standard pandapower „25 MVA 110/20 kV” (u_kr 0,41 % → P_k = 102,5 kW)
    Un: 20, cmax: 1.1, cmin: 1.0,                            // IEC 60909-0, tabelul 1 (U_n > 1 kV)
    neutral: "R", Ilim: 300, Z0bpn: 6, Ic: 60, v: 0.05, d: 0.05, // tratarea neutrului 20 kV
    line: "ol70", R1: 0.4132, X1: 0.36, R0: 0.5612, X0: 1.578, L: 20, x: 20, thetaE: 80,
    fault: "1F", Rf: 0,
  };

  /* Tipuri de linie: secvența pozitivă din biblioteca de tipuri standard pandapower (EN 50182 / DIN);
     secvența zero calculată cu formulele lui Carson (ρ = 100 Ω·m, fără conductor de protecție) — vezi verify/m01_line_params.py */
  const LINES = {
    ol70: { R1: 0.4132, X1: 0.36, R0: 0.5612, X0: 1.578, ro: "LEA Ol-Al 70/12 mm² (70-AL1/11-ST1A)", en: "OHL ACSR 70/12 mm² (70-AL1/11-ST1A)" },
    ol120: { R1: 0.2376, X1: 0.344, R0: 0.3856, X0: 1.557, ro: "LEA Ol-Al 120/21 mm² (122-AL1/20-ST1A)", en: "OHL ACSR 120/21 mm² (122-AL1/20-ST1A)" },
    cab185: { R1: 0.161, X1: 0.117, R0: 0.861, X0: 0.117, ro: "LES Al 185 mm² XLPE (NA2XS2Y 1×185), ecran Cu 25 mm²", en: "Cable Al 185 mm² XLPE (NA2XS2Y 1×185), Cu screen 25 mm²" },
  };

  const FAULTS = ["3F", "2F", "1F", "2FE"];

  /* Impedanțele rețelei pentru un caz (max/min), raportate la MT */
  function source(p, kase) {
    const c = kase === "max" ? p.cmax : p.cmin;
    const SkQ = kase === "max" ? p.SkQmax : p.SkQmin;
    const tr = p.UrHV / p.UrLV;
    const ZQ = (c * p.UnQ * p.UnQ) / SkQ;                 // (IEC 60909-0) Z_Q = c·U_nQ²/S″_kQ
    const zQ = X.zRX(ZQ, p.rxQ);
    const zQt = scale(zQ, 1 / (tr * tr));
    const base = (p.UrLV * p.UrLV) / p.Sr;
    const ZT = (p.uk / 100) * base;
    const RT = (p.Pk / 1000) * (p.UrLV * p.UrLV) / (p.Sr * p.Sr); // R_T = P_krT·U_rT²/S_rT²
    const XT = Math.sqrt(Math.max(ZT * ZT - RT * RT, 0));
    const xT = XT / base;
    const KT = kase === "max" ? (0.95 * p.cmax) / (1 + 0.6 * xT) : 1; // K_T numai pentru curenți maximi (IEC 60909-0:2016 §6.3.3)
    const zT = scale(C(RT, XT), KT);
    return { c, SkQ, tr, ZQ, zQ, zQt, ZT, RT, XT, xT, KT, zT, z1bus: add(zQt, zT) };
  }

  /* Impedanța homopolară văzută la barele MT, după tratarea neutrului */
  function zeroBus(p) {
    const Uph = (p.Un * 1000) / S3;
    const out = { Uph };
    // capacitatea homopolară a rețelei galvanic legate, din curentul capacitiv de punere la pământ: I_C = 3·ω·C0·U_f
    out.bC = p.Ic > 0 ? p.Ic / (3 * Uph) : 0;                    // ω·C0 (S)
    out.C0uF = (out.bC / W) * 1e6;
    const yC = C(0, out.bC);
    let yN = C(0);
    if (p.neutral === "R") {
      out.RN = Uph / p.Ilim;                                       // R_N = U_f/I_lim
      out.zN = add(C(0, p.Z0bpn), C(3 * out.RN, 0));               // Z0N = Z0,BPN + 3R_N
      yN = X.inv(out.zN);
    } else if (p.neutral === "L") {
      const IL = p.Ic * (1 + p.v);                                 // grad de dezacord v = (I_L − I_C)/I_C
      out.XN = Uph / IL;
      out.IL = IL;
      out.Iw = p.d * p.Ic;                                         // componenta activă (pierderi bobină + izolație), d·I_C
      out.zN = add(C(0, p.Z0bpn), C(0, 3 * out.XN));
      yN = add(X.inv(out.zN), C(out.Iw / (3 * Uph), 0));
    } else if (p.neutral === "S") {
      out.zN = C(0, p.Z0bpn);
      yN = X.inv(out.zN);
    } // "I" izolat: numai capacitățile
    const y = add(yN, yC);
    out.z0bus = abs(y) > 0 ? X.inv(y) : C(1e12, 0);
    return out;
  }

  /* Defectul propriu-zis: componente simetrice la locul defectului.
     E = c·U_n/√3 (sursa echivalentă IEC 60909-0); defectul între faze L2–L3 (2F, 2FE) sau L1–pământ (1F). */
  function solveFault(type, E, z1, z2, z0, Rf) {
    let I1 = C(0), I2 = C(0), I0 = C(0);
    const rf = C(Rf, 0), rf3 = C(3 * Rf, 0);
    if (type === "3F") { I1 = div(E, add(z1, rf)); }
    else if (type === "2F") { I1 = div(E, add(z1, z2, rf)); I2 = scale(I1, -1); }
    else if (type === "1F") { I1 = div(E, add(z1, z2, z0, rf3)); I2 = I1; I0 = I1; }
    else if (type === "2FE") {
      const z0f = add(z0, rf3);
      I1 = div(E, add(z1, par(z2, z0f)));
      I2 = scale(mul(I1, div(z0f, add(z2, z0f))), -1);
      I0 = scale(mul(I1, div(z2, add(z2, z0f))), -1);
    }
    const V1 = sub(E, mul(z1, I1)), V2 = scale(mul(z2, I2), -1), V0 = scale(mul(z0, I0), -1);
    const Iabc = seq2abc(I0, I1, I2), Vabc = seq2abc(V0, V1, V2);
    return { I0, I1, I2, V0, V1, V2, Iabc, Vabc };
  }

  /* Calcul complet pentru un punct x (km) și un caz */
  function compute(p, kase, type, xkm, Rf) {
    const s = source(p, kase);
    const zb = zeroBus(p);
    const kth = kase === "min" ? 1 + 0.004 * (p.thetaE - 20) : 1;  // R_L(θe) = [1 + 0,004/°C·(θe − 20 °C)]·R_L20
    const z1L = C(p.R1 * kth * xkm, p.X1 * xkm);
    const z0L = C(p.R0 * kth * xkm, p.X0 * xkm);
    const z1 = add(s.z1bus, z1L), z2 = z1;
    const z0 = add(zb.z0bus, z0L);
    const E = C((s.c * p.Un * 1000) / S3, 0);
    const f = solveFault(type, E, z1, z2, z0, Rf);
    const mags = f.Iabc.map(abs);
    // curentul de defect „caracteristic” pentru fiecare tip
    let Ik;
    if (type === "3F") Ik = mags[0];
    else if (type === "2F") Ik = mags[1];
    else if (type === "1F") Ik = mags[0];
    else Ik = abs(scale(f.I0, 3));                                   // 2FE: curentul prin pământ I″_kE2E
    // tensiunile fazelor în u.r. față de E (factorul de punere la pământ, IEC 60071)
    const vpu = f.Vabc.map((v) => abs(v) / abs(E));
    // curenții pe partea ÎT a lui T1 (grupa de conexiuni h): secvența + rotită cu +30°·h, secvența − cu −30°·h, homopolar blocat (Δ)
    const k = p.UrLV / p.UrHV;
    const I1h = scale(mul(f.I1, polar(1, 30 * p.clock)), k);
    const I2h = scale(mul(f.I2, polar(1, -30 * p.clock)), k);
    const Ihv = seq2abc(C(0), I1h, I2h);
    return { kase, type, x: xkm, Rf, src: s, zb, kth, z1L, z0L, z1, z2, z0, E, ...f, mags, Ik, vpu, Ihv, IhvMag: Ihv.map(abs), I3I0: abs(scale(f.I0, 3)) };
  }

  /* Curentul de scurtcircuit trifazat la barele de 110 kV (pentru reglajele protecției de pe partea ÎT) */
  function hvBus(p, kase) {
    const c = kase === "max" ? p.cmax : p.cmin, SkQ = kase === "max" ? p.SkQmax : p.SkQmin;
    const ZQ = (c * p.UnQ * p.UnQ) / SkQ;
    return { Ik3: (c * p.UnQ) / (S3 * ZQ), ZQ };                  // = S″kQ/(√3·U_nQ)
  }

  /* Tabelul pentru studiul de reglaje: puncte de calcul de-a lungul plecării */
  function settingsTable(p) {
    const pts = [0, 0.25, 0.5, 0.75, 1].map((f) => f * p.L);
    return pts.map((x) => {
      const r3max = compute(p, "max", "3F", x, 0);
      const r2min = compute(p, "min", "2F", x, 0);
      const r1max = compute(p, "max", "1F", x, 0);
      const r1min = compute(p, "min", "1F", x, p.Rf);
      const r2emax = compute(p, "max", "2FE", x, 0);
      return { x, Ik3max: r3max.Ik, Ik2min: r2min.Ik, Ik1max: r1max.Ik, Ik1min: r1min.Ik, IkE2Emax: r2emax.Ik, Ihv3max: Math.max(...r3max.IhvMag), Ihv2min: Math.max(...r2min.IhvMag), ipKappa: kappa(r3max.z1) };
    });
  }

  /* factorul κ pentru curentul de șoc (metoda B, rețea radială): κ = 1,02 + 0,98·e^(−3R/X) */
  function kappa(z) { return 1.02 + 0.98 * Math.exp((-3 * z.re) / z.im); }

  /* Profil de-a lungul liniei pentru grafic */
  function profile(p, n = 60) {
    const out = [];
    for (let i = 0; i <= n; i++) {
      const x = (p.L * i) / n;
      out.push({ x, Ik3max: compute(p, "max", "3F", x, 0).Ik, Ik2min: compute(p, "min", "2F", x, 0).Ik, Ik1max: compute(p, "max", "1F", x, 0).Ik, Ik1min: compute(p, "min", "1F", x, p.Rf).Ik });
    }
    return out;
  }

  return { DEFAULTS, LINES, FAULTS, source, zeroBus, solveFault, compute, hvBus, settingsTable, profile, kappa };
});
