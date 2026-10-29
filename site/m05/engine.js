/* Modulul 05 — motorul de calcul: punerea la pământ în rețelele de medie tensiune.
   Barele de 20 kV cu șase plecări; neutrul izolat, compensat (bobină de stingere) sau tratat prin rezistor.
   Pentru un defect monofazat prin R_f pe o plecare: tensiunea homopolară, curenții 3I0 măsurați de fiecare plecare
   și deciziile principiilor de protecție (51N, 67N, I0·sin φ, I0·cos φ, admitanță, 59N).
   Convenție: curenții se măsoară de la bare spre linie; polarizarea este −3U0 (ca în M04). */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory(require("../assets/cx.js"), require("../m01/engine.js"));
  else root.M05 = factory(root.CX, root.M01);
})(typeof self !== "undefined" ? self : this, function (X, M01) {
  const { C, add, sub, mul, div, scale, abs, argDeg, inv, seq2abc } = X;
  const S3 = Math.sqrt(3), W = 2 * Math.PI * 50;
  const wrap = (d) => ((d + 180) % 360 + 360) % 360 - 180;

  /* Tipurile de linie: secvența pozitivă și zero ca în M01; capacitatea homopolară:
     cablu ecranat C0 = C1 = 273 nF/km (pandapower NA2XS2Y 1×185); LEA C0 = 4,12 nF/km, calculată din geometria M01
     (vezi verify/m05_verify.py, unde aceeași geometrie dă C1 = 10,1 nF/km față de 9,7 nF/km în pandapower). */
  const TYPES = {
    ol70: { R1: 0.4132, X1: 0.36, R0: 0.5612, X0: 1.578, C0: 4.12e-9, ro: "LEA Ol-Al 70/12", en: "OHL ACSR 70/12" },
    cab185: { R1: 0.161, X1: 0.117, R0: 0.861, X0: 0.117, C0: 273e-9, ro: "LES Al 185 XLPE", en: "Cable Al 185 XLPE" },
  };

  const DEFAULTS = {
    neutral: "L",                 // "I" izolat, "L" compensat, "R" rezistor
    Ilim: 300, Z0bpn: 6,          // rezistor (ca în M01)
    v: 0.05, dL: 0.015, dN: 0.02, // bobina: dezacord (supracompensare), pierderile bobinei (fracție din I_L), scurgerile rețelei (fracție din I_C)
    IPR: 15, PR: true,            // rezistorul conectat în paralel cu bobina: curentul lui la deplasarea completă a neutrului, A
    feeders: [
      { id: "F1", type: "ol70", km: 20 }, { id: "F2", type: "cab185", km: 6 }, { id: "F3", type: "cab185", km: 4 },
      { id: "F4", type: "ol70", km: 30 }, { id: "F5", type: "cab185", km: 8 }, { id: "F6", type: "ol70", km: 15 },
    ],
    fault: "F1", x: 10, Rf: 100, kase: "max",
  };

  const Uph = (net) => (net.Un * 1000) / S3;

  /* admitanțele homopolare (pe fază) ale plecărilor și ale neutrului */
  function admittances(p, net) {
    const U = Uph(net);
    const fd = p.feeders.map((f) => {
      const t = TYPES[f.type];
      const B = W * t.C0 * f.km;              // ωC0·L, S
      const G = p.dN * B;                     // scurgeri: componenta activă, proporțională cu cea capacitivă
      return { ...f, B, G, y: C(G, B), Ic: 3 * B * U, Iw: 3 * G * U };
    });
    const IcTot = fd.reduce((s, f) => s + f.Ic, 0);
    let yN = C(0), info = {};
    if (p.neutral === "R") {
      const RN = U / p.Ilim;
      yN = inv(C(3 * RN, p.Z0bpn)); info = { RN };
    } else if (p.neutral === "L") {
      const IL = IcTot * (1 + p.v), XN = U / IL;
      yN = add(inv(C(0, p.Z0bpn + 3 * XN)), C((p.dL * IL) / (3 * U), 0));
      if (p.PR) yN = add(yN, C(p.IPR / (3 * U), 0));
      info = { IL, XN, IwL: p.dL * IL, IPR: p.PR ? p.IPR : 0 };
    }
    const Ybus = fd.reduce((s, f) => add(s, f.y), yN);
    return { fd, IcTot, yN, Ybus, info, U };
  }

  /* defectul monofazat (faza L1) prin R_f, pe plecarea p.fault, la x km */
  function compute(p) {
    const net = { ...M01.DEFAULTS };
    const ad = admittances(p, net);
    const src = M01.source(net, p.kase);
    const c = p.kase === "max" ? net.cmax : net.cmin;
    const E = C((c * net.Un * 1000) / S3, 0);
    const ff = ad.fd.find((f) => f.id === p.fault), t = TYPES[ff.type];
    const x = Math.min(Math.max(p.x, 0), ff.km);
    const z1 = add(src.z1bus, C(t.R1 * x, t.X1 * x));
    const z0 = add(inv(ad.Ybus), C(t.R0 * x, t.X0 * x));
    const fl = M01.solveFault("1F", E, z1, z1, z0, p.Rf);
    const I0f = fl.I0;
    const U0 = scale(div(I0f, ad.Ybus), -1);                     // tensiunea homopolară pe bare
    const U1 = sub(E, mul(src.z1bus, fl.I1)), U2 = scale(mul(src.z1bus, fl.I2), -1);
    const Ubus = seq2abc(U0, U1, U2);
    const Vpol = scale(U0, -3);                                   // −3U0
    const feeders = ad.fd.map((f) => {
      let I3 = scale(mul(f.y, U0), 3);                              // curentul propriu (capacitiv + scurgeri)
      if (f.id === p.fault) I3 = add(I3, scale(I0f, 3));          // plecarea defectă duce și curentul de defect
      const phi = wrap(argDeg(I3) - argDeg(Vpol));
      const Y0 = div(I3, Vpol);                                    // admitanța măsurată 3I0/(−3U0), S
      return { ...f, I3, I: abs(I3), phi, Icos: abs(I3) * Math.cos((phi * Math.PI) / 180), Isin: abs(I3) * Math.sin((phi * Math.PI) / 180), Y0 };
    });
    const IN = scale(mul(ad.yN, U0), 3);                          // curentul prin elementul de neutru
    // u0: deplasarea neutrului raportată la tensiunea de fază dinainte de defect
    return { E, U0, u0: abs(U0) / abs(E), Ubus, upu: Ubus.map((v) => abs(v) / abs(E)), Vpol, IF: abs(scale(I0f, 3)), I0f, feeders, IN, ad, z0, z1 };
  }

  /* deplasarea neutrului în funcție de R_f (rețea izolată sau compensată, Z1 și Z2 neglijate): U0/Uf = 1/|1 + 3R_f·Y0| */
  function u0Approx(p, Rf) {
    const ad = admittances(p, { ...M01.DEFAULTS });
    return 1 / abs(add(C(1), scale(ad.Ybus, 3 * Rf)));
  }

  /* principiile de protecție aplicate fiecărei plecări */
  const METHODS = ["51N", "67N", "sin", "cos", "Y0"];
  function decide(r, s) {
    const startU = r.u0 >= s.U0start;                             // pornirea pe tensiune homopolară (59N)
    return r.feeders.map((f) => {
      const set = s.feeders[f.id];
      const d = {};
      d["51N"] = f.I >= set.I0;
      d["67N"] = startU && f.I >= set.I0dir && Math.cos(((f.phi - s.rcaN) * Math.PI) / 180) > 0;
      d.sin = startU && f.Isin >= set.Isin;
      d.cos = startU && f.Icos >= set.Icos;
      d.Y0 = startU && (f.Y0.re >= set.G || f.Y0.im >= set.B);
      return { id: f.id, d };
    });
  }

  /* reglajele automate pentru o tratare a neutrului dată */
  function autoSettings(p, o = {}) {
    // kSig: siguranța față de curentul capacitiv propriu; kSens: sensibilitatea la R_f țintă;
    // uUnb: deplasarea neutrului în regim normal (nesimetria rețelei); kU: marja pragului U0 față de ea;
    // Imin: cel mai mic curent rezidual măsurat sigur (releu + TC toroidal sau conexiune Holmgreen)
    const kSig = o.kSig ?? 1.2, kSens = o.kSens ?? 1.5, RfT = o.RfT ?? 500, uUnb = o.uUnb ?? 0.03, kU = o.kU ?? 1.5, Imin = o.Imin ?? 5;
    const net = { ...M01.DEFAULTS };
    const ad = admittances(p, net);
    const U0start = Math.ceil(kU * uUnb * 100 - 1e-9) / 100;      // fracție din U_f, rotunjită la 1 %
    const feeders = {}, rep = {};
    // cel mai mic semnal la R_f țintă, pentru defect pe fiecare plecare (la capătul ei: cazul cel mai slab)
    ad.fd.forEach((f) => {
      const r = compute({ ...p, fault: f.id, x: f.km, Rf: RfT, kase: "min" });
      const me = r.feeders.find((g) => g.id === f.id);
      const others = ad.Ybus.re - f.G;                             // conductanța „vizibilă”: neutrul + celelalte plecări
      const Yf = me.Y0;
      feeders[f.id] = {
        I0: Math.max(Imin, Math.ceil(kSig * f.Ic)),                 // 51N: peste curentul capacitiv propriu (defect pe altă plecare)
        I0dir: Math.max(Imin, Math.floor(me.I / kSens)),            // 67N: sensibil la R_f țintă
        Isin: Math.max(Imin, Math.floor((me.Isin / kSens) * 10) / 10),
        Icos: Math.max(Imin, Math.floor((me.Icos / kSens) * 10) / 10),
        G: Yf.re / kSens, B: Yf.im > 0 ? Yf.im / kSens : Infinity, // admitanța nu depinde de R_f: se reglează direct din rețea
      };
      rep[f.id] = { Ic: f.Ic, IatRfT: me.I, IsinAt: me.Isin, IcosAt: me.Icos, Y0: Yf, u0: r.u0, others };
    });
    const RfMaxU = RfLimitU(p, U0start);
    return { U0start, feeders, rep, kSig, kSens, RfT, uUnb, kU, Imin, RfMaxU, rcaN: p.neutral === "I" ? 90 : 0 };
  }

  /* cea mai mare R_f pentru care U0 depășește pragul de pornire (defect pe plecarea p.fault) */
  function RfLimitU(p, u0set) {
    let lo = 0, hi = 1e6;
    if (compute({ ...p, Rf: 0, kase: "min" }).u0 < u0set) return 0;
    for (let i = 0; i < 80; i++) { const m = Math.sqrt(Math.max(lo, 1e-3) * hi); if (compute({ ...p, Rf: m, kase: "min" }).u0 >= u0set) lo = m; else hi = m; }
    return lo;
  }
  /* cea mai mare R_f detectată de o metodă pe plecarea defectă */
  function RfLimit(p, s, method) {
    const ok = (Rf) => { const r = compute({ ...p, Rf, kase: "min" }); const d = decide(r, s).find((x) => x.id === p.fault).d; return d[method]; };
    if (!ok(0)) return 0;
    let lo = 0, hi = 1e6;
    if (ok(hi)) return Infinity;
    for (let i = 0; i < 70; i++) { const m = Math.sqrt(Math.max(lo, 1e-3) * hi); if (ok(m)) lo = m; else hi = m; }
    return lo;
  }

  return { TYPES, DEFAULTS, METHODS, admittances, compute, u0Approx, decide, autoSettings, RfLimit, RfLimitU, wrap };
});
