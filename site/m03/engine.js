/* Modulul 03 — motorul de calcul: protecția maximală de curent (50/51), reglaje și coordonare
   pe rețeaua-exemplu a cursului. Curenții de defect vin din motorul modulului 01.
   Curenții sunt în amperi primari, la tensiunea releului (R1 pe 110 kV, celelalte pe 20 kV). */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory(require("../m01/engine.js"));
  else root.M03 = factory(root.M01);
})(typeof self !== "undefined" ? self : this, function (M01) {
  const S3 = Math.sqrt(3);

  /* Caracteristici dependente: IEC 60255-151 (t = TMS·k/(M^α − 1)) și IEEE C37.112 (t = TD·(A/(M^p − 1) + B)) */
  const CURVES = {
    "IEC-SI": { fam: "IEC", k: 0.14, a: 0.02, b: 0, ro: "IEC normal invers (SI)", en: "IEC standard inverse (SI)" },
    "IEC-VI": { fam: "IEC", k: 13.5, a: 1, b: 0, ro: "IEC foarte invers (VI)", en: "IEC very inverse (VI)" },
    "IEC-EI": { fam: "IEC", k: 80, a: 2, b: 0, ro: "IEC extrem de invers (EI)", en: "IEC extremely inverse (EI)" },
    "IEC-LTI": { fam: "IEC", k: 120, a: 1, b: 0, ro: "IEC invers de lungă durată (LTI)", en: "IEC long-time inverse (LTI)" },
    "IEEE-MI": { fam: "IEEE", k: 0.0515, a: 0.02, b: 0.114, ro: "IEEE moderat invers (MI)", en: "IEEE moderately inverse (MI)" },
    "IEEE-VI": { fam: "IEEE", k: 19.61, a: 2, b: 0.491, ro: "IEEE foarte invers (VI)", en: "IEEE very inverse (VI)" },
    "IEEE-EI": { fam: "IEEE", k: 28.2, a: 2, b: 0.1217, ro: "IEEE extrem de invers (EI)", en: "IEEE extremely inverse (EI)" },
    "DT": { fam: "DT", ro: "independentă (timp definit)", en: "definite time (DT)" },
  };
  const GT = 1.1;  // pragul de la care caracteristica dependentă e garantată (G_T = 1,1·G_S)
  const GD = 20;   // peste 20·G_S timpul rămâne constant (G_D = 20·G_S)

  /* timpul caracteristicii pentru TMS = 1 */
  function curveTime(type, M) {
    const c = CURVES[type];
    if (!c || c.fam === "DT") return 1;
    const m = Math.min(M, GD);
    return c.k / (Math.pow(m, c.a) - 1) + c.b;
  }

  /* timpul de acționare al unui releu cu treptele I> (51) și I>> (50) */
  function tripTime(s, I, tOwn) {
    let t51 = Infinity, t50 = Infinity;
    if (s.Is > 0) {
      const M = I / s.Is;
      if (s.curve === "DT") { if (M >= 1) t51 = Math.max(s.tms, tOwn); }
      else if (M >= GT) t51 = Math.max(s.tms * curveTime(s.curve, M), tOwn);
    }
    if (s.Ih > 0 && I >= s.Ih) t50 = Math.max(s.th, tOwn);
    return { t: Math.min(t51, t50), t51, t50, stage: t50 <= t51 ? "I>>" : t51 < Infinity ? "I>" : "—" };
  }

  /* Datele implicite: rețeaua din M01 + releele R1…R4 */
  const NET = { ...M01.DEFAULTS };
  const DEFAULTS = {
    x4: 10,                // poziția R4 pe linie, km
    kSig: 1.2, kRev: 0.95, kP: 1.0, kD: 1.3, kSensMain: 1.5, kSensBack: 1.2,
    cti: 0.3, tmsMin: 0.05, tOwn: 0.03,
    R4: { Iload: 80, ct: 100, curve: "IEC-VI" },
    R3: { Iload: 200, ct: 300, curve: "IEC-VI" },
    R2: { Iload: null, ct: 1000, curve: "IEC-VI" },  // null → curentul nominal al lui T1
    R1: { Iload: null, ct: 200, curve: "IEC-VI" },
  };
  const ORDER = ["R4", "R3", "R2", "R1"];

  function ratedT1(net) { return { lv: (net.Sr * 1e6) / (S3 * net.UrLV * 1e3), hv: (net.Sr * 1e6) / (S3 * net.UrHV * 1e3) }; }

  /* Curenții de defect văzuți de fiecare releu.
     loc: "B20" (bare 20 kV) sau un număr x (km pe plecarea F1, x ≥ 0, după R3).
     Întoarce curentul maxim pe faze (ce compară releul cu pragul). */
  function seen(net, d, loc, type, kase) {
    const x = loc === "B20" ? 0 : loc;
    const r = M01.compute(net, kase, type, x, 0);
    const I = Math.max(...r.mags);
    const Ihv = Math.max(...r.IhvMag);
    return {
      R4: loc !== "B20" && x >= d.x4 ? I : 0,
      R3: loc !== "B20" ? I : 0,
      R2: I,
      R1: Ihv,
    };
  }

  /* treaptă de reglaj: rotunjire în sus la pasul releului (0,01·I_n secundar) */
  const roundUp = (v, step) => Math.ceil(v / step - 1e-9) * step;

  /* Reglajele automate, de la aval spre amonte, cu raportul de calcul pas cu pas */
  function autoSettings(net, d) {
    const rt = ratedT1(net);
    const load = { R4: d.R4.Iload, R3: d.R3.Iload, R2: d.R2.Iload ?? rt.lv, R1: d.R1.Iload ?? rt.hv };
    const S = {}, rep = {};
    const L = net.L, x4 = d.x4;
    // curenții de calcul (M01)
    const I3 = (x) => M01.compute(net, "max", "3F", x, 0).Ik;
    const I2min = (x) => M01.compute(net, "min", "2F", x, 0).Ik;
    const hv = (x, type, kase) => Math.max(...M01.compute(net, kase, type, x, 0).IhvMag);

    // 1) curentul de pornire I> = k_sig·k_p·I_sarcină/k_rev, rotunjit la 0,01·I_n
    ORDER.forEach((k) => {
      const raw = (d.kSig * d.kP * load[k]) / d.kRev;
      const Is = roundUp(raw, d[k].ct * 0.01);
      S[k] = { curve: d[k].curve, Is, tms: d.tmsMin, Ih: 0, th: 0, ct: d[k].ct };
      rep[k] = { load: load[k], IsRaw: raw, Is };
    });
    // 1b) pragurile se eșalonează: pragul din amonte, raportat la curentul pe care îl vede releul din aval,
    //     nu trebuie să fie sub pragul acestuia (altfel un defect slab din aval e eliminat de releul din amonte).
    //     Raportul maxim Iup/Idn: 1 pe aceeași tensiune; (U_rLV/U_rHV)·2/√3 pentru R1–R2 (defect bifazat, YNd11).
    [["R4", "R3"], ["R3", "R2"], ["R2", "R1"]].forEach(([dn, up]) => {
      const ratio = Math.max(...coordCases(net, d, dn, up).map((c) => c.Iup / c.Idn));
      const need = S[dn].Is * ratio;
      rep[up].grade = { ratio, need, applied: need > S[up].Is + 1e-9 };
      if (need > S[up].Is + 1e-9) { S[up].Is = roundUp(need, d[up].ct * 0.01); rep[up].Is = S[up].Is; }
    });
    // 2) sensibilitate
    const sens = (k, Imin, Is) => Imin / Is;
    rep.R4.sensMain = { where: L, I: I2min(L), k: sens("R4", I2min(L), S.R4.Is), need: d.kSensMain };
    rep.R3.sensMain = { where: x4, I: I2min(x4), k: I2min(x4) / S.R3.Is, need: d.kSensMain };
    rep.R3.sensBack = { where: L, I: I2min(L), k: I2min(L) / S.R3.Is, need: d.kSensBack };
    rep.R2.sensMain = { where: 0, I: I2min(0), k: I2min(0) / S.R2.Is, need: d.kSensMain };
    rep.R2.sensBack = { where: L, I: I2min(L), k: I2min(L) / S.R2.Is, need: d.kSensBack };
    rep.R1.sensMain = { where: 0, I: hv(0, "2F", "min"), k: hv(0, "2F", "min") / S.R1.Is, need: d.kSensBack };

    // 3) treptele I>>
    // R4: ultimul releu de pe linie — fără treaptă rapidă (aval sunt posturi de transformare cu siguranțe, M06)
    // R3: I>> ≥ k_d·I″k3 max la locul lui R4, instantaneu
    rep.R3.IhBase = I3(x4);
    S.R3.Ih = roundUp(d.kD * rep.R3.IhBase, d.R3.ct * 0.01); S.R3.th = 0;
    rep.R3.reach = reachKm(net, S.R3.Ih, "max", "3F");
    rep.R3.reachMin = reachKm(net, S.R3.Ih, "min", "2F");
    // R2: I>> sensibil la defectele pe bare (I″k2 min la bare / k_sens), temporizat după R3
    // (nu sub pragul I>> al lui R3: altfel treapta temporizată I>> din R2 ar concura cu curba lui R3)
    rep.R2.IhBase = I2min(0);
    rep.R2.IhSens = I2min(0) / d.kSensMain;
    S.R2.Ih = roundUp(Math.max(rep.R2.IhSens, S.R3.Ih), d.R2.ct * 0.01);
    S.R2.th = round2(Math.max(S.R3.th, d.tOwn) + d.cti);
    // R1: I>> ≥ k_d·curentul maxim pe 110 kV la defect pe barele de 20 kV, instantaneu
    rep.R1.IhBase = hv(0, "3F", "max");
    S.R1.Ih = roundUp(d.kD * rep.R1.IhBase, d.R1.ct * 0.01); S.R1.th = 0;
    rep.R1.IhOverIr = S.R1.Ih / rt.hv;
    rep.R1.IhHVfault = M01.hvBus(net, "min").Ik3 * 1000;

    // 4) TMS: cel mai mic TMS care păstrează marja CTI pe tot domeniul de curenți comuni
    rep.R4.tms = { tms: S.R4.tms, note: "min" };
    const pairs = [["R4", "R3"], ["R3", "R2"], ["R2", "R1"]];
    pairs.forEach(([dn, up]) => {
      const need = requiredTMS(net, d, S, dn, up);
      S[up].tms = Math.max(d.tmsMin, Math.ceil(need.tms * 100 - 1e-9) / 100);
      rep[up].tms = { ...need, tms: S[up].tms };
    });
    return { S, rep, load, rt };
  }
  const round2 = (v) => Math.round(v * 100) / 100;

  /* până unde (km) ajunge o treaptă I>> de prag Ih pe plecare */
  function reachKm(net, Ih, kase, type) {
    if (M01.compute(net, kase, type, 0, 0).Ik < Ih) return 0;
    if (M01.compute(net, kase, type, net.L, 0).Ik >= Ih) return net.L;
    let a = 0, b = net.L;
    for (let i = 0; i < 50; i++) { const m = (a + b) / 2; if (M01.compute(net, kase, type, m, 0).Ik >= Ih) a = m; else b = m; }
    return (a + b) / 2;
  }

  /* Scenariile de coordonare pentru o pereche aval–amonte: defecte pe care le văd ambele relee */
  function coordCases(net, d, dn, up) {
    const out = [];
    const push = (loc, type) => out.push({ loc, type, ...seenPair(net, d, loc, type, "max", dn, up) });
    if (dn === "R4") { push(d.x4, "3F"); push(d.x4, "2F"); }
    if (dn === "R3") { push(0, "3F"); push(0, "2F"); }
    if (dn === "R2") { push("B20", "3F"); push("B20", "2F"); }
    return out;
  }
  function seenPair(net, d, loc, type, kase, dn, up) { const s = seen(net, d, loc, type, kase); return { Idn: s[dn], Iup: s[up] }; }

  /* Pentru fiecare scenariu (defect cu curentul maxim Idn, Iup), aceeași rețea dă curenți proporționali
     pentru defecte mai îndepărtate sau mai rezistive: baleiem curentul de la pragul releului din amonte
     până la valoarea maximă, păstrând raportul Iup/Idn al scenariului. */
  function sweep(c, Sdn, Sup, n = 120) {
    const ratio = c.Iup / c.Idn;
    const Imax = c.Idn, Imin = Math.max(GT * Sup.Is / ratio, GT * Sdn.Is) * 1.0001;
    const pts = [];
    if (!(Imax > Imin)) return pts;
    for (let i = 0; i <= n; i++) {
      const Idn = Imin * Math.pow(Imax / Imin, i / n);
      pts.push({ Idn, Iup: Idn * ratio });
    }
    return pts;
  }

  function requiredTMS(net, d, S, dn, up) {
    let need = 0, at = null;
    coordCases(net, d, dn, up).forEach((c) => {
      sweep(c, S[dn], S[up]).forEach((p) => {
        const tdn = tripTime(S[dn], p.Idn, d.tOwn).t;
        if (!isFinite(tdn)) return;
        // curba I> din amonte trebuie să păstreze marja la orice curent comun, chiar dacă și treapta I>> acționează:
        // releul declanșează la min(t51, t50), deci o curbă I> prea rapidă strică selectivitatea
        const fUp = S[up].curve === "DT" ? 1 : curveTime(S[up].curve, p.Iup / S[up].Is);
        const tms = (tdn + d.cti) / fUp;
        if (tms > need) { need = tms; at = { ...p, type: c.type, tdn }; }
      });
    });
    return { tms: need, at };
  }

  /* Verificarea selectivității: marja minimă pe fiecare pereche, pe tot domeniul de curenți comuni */
  function coordination(net, d, S) {
    const res = {};
    [["R4", "R3"], ["R3", "R2"], ["R2", "R1"]].forEach(([dn, up]) => {
      let worst = { margin: Infinity };
      coordCases(net, d, dn, up).forEach((c) => {
        sweep(c, S[dn], S[up]).forEach((p) => {
          const tdn = tripTime(S[dn], p.Idn, d.tOwn), tup = tripTime(S[up], p.Iup, d.tOwn);
          if (!isFinite(tdn.t)) return;
          const m = tup.t - tdn.t;
          if (m < worst.margin) worst = { margin: m, Idn: p.Idn, Iup: p.Iup, tdn: tdn.t, tup: tup.t, type: c.type, stageUp: tup.stage, stageDn: tdn.stage };
        });
      });
      const ratio = Math.max(...coordCases(net, d, dn, up).map((c) => c.Iup / c.Idn));
      const pickupOk = S[up].Is / ratio >= S[dn].Is * (1 - 1e-9);
      res[dn + "-" + up] = { ...worst, ratio, pickupOk, marginOk: worst.margin >= d.cti - 1e-6, ok: worst.margin >= d.cti - 1e-6 && pickupOk };
    });
    return res;
  }

  /* Cine declanșează, pentru un defect dat */
  function whoTrips(net, d, S, loc, type, kase) {
    const s = seen(net, d, loc, type, kase);
    const out = {};
    ORDER.forEach((k) => { out[k] = { I: s[k], ...tripTime(S[k], s[k], d.tOwn) }; });
    const first = ORDER.filter((k) => isFinite(out[k].t)).sort((a, b) => out[a].t - out[b].t)[0] || null;
    return { s, out, first };
  }

  /* marja de coordonare calculată din componente (formula din NPAG / literatura de aplicații) */
  function ctiFromParts(t, Er, Ect, tcb, to, ts) { return ((2 * Er + Ect) * t) / 100 + tcb + to + ts; }

  return { CURVES, GT, GD, curveTime, tripTime, DEFAULTS, NET, ORDER, ratedT1, seen, autoSettings, reachKm, coordCases, sweep, requiredTMS, coordination, whoTrips, ctiFromParts };
});
