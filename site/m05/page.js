/* Modulul 05 — interfața paginii. Calculele sunt în engine.js (M05) și ../m01/engine.js. */
(function () {
  "use strict";
  const M = window.M05, X = window.CX, PR = window.PR;
  const { abs, argDeg } = X;
  const bi = PR.bi, t = PR.t;
  const clone = (o) => JSON.parse(JSON.stringify(o));

  const P = clone(M.DEFAULTS);
  const RG = { kSig: 1.2, kSens: 1.5, RfT: 500, uUnb: 0.03, kU: 1.5, Imin: 5, tF: 0.5, cti: 0.3 };
  const REC = { R: "67N", I: "sin", L: "cos" };
  const UI = { method: REC[P.neutral] };
  const MNAME = {
    "51N": { ro: "51N · curent rezidual", en: "51N · residual current" },
    "67N": { ro: "67N · direcțional", en: "67N · directional" },
    sin: { ro: "I₀·sin φ · reactiv", en: "I₀·sin φ · reactive" },
    cos: { ro: "I₀·cos φ · wattmetric", en: "I₀·cos φ · wattmetric" },
    Y0: { ro: "Y₀ · admitanță", en: "Y₀ · admittance" },
  };
  const NEU = { I: { ro: "izolat", en: "isolated" }, L: { ro: "compensat (bobină de stingere)", en: "compensated (arc suppression coil)" }, R: { ro: "rezistor", en: "resistor" } };
  const FCOL = { F1: "var(--c1)", F2: "var(--c3)", F3: "var(--c4)", F4: "var(--c5)", F5: "var(--c6)", F6: "var(--L3)" };
  const fA = (I) => `${PR.fmt(I, I >= 100 ? 0 : I >= 10 ? 1 : 2)} A`;
  const fmS = (y) => `${PR.fmt(y * 1000, 3)} mS`;

  let S = null;
  const settingsNow = () => { S = M.autoSettings(P, RG); return { U0start: S.U0start, rcaN: S.rcaN, feeders: S.feeders }; };

  /* ---------- controale ---------- */
  const flat = {};
  const toFlat = () => { Object.assign(flat, { neutral: P.neutral, Ilim: P.Ilim, v: P.v, dL: P.dL, dN: P.dN, PR: P.PR, IPR: P.IPR, fault: P.fault, x: P.x, Rf: P.Rf, kase: P.kase }); P.feeders.forEach((f) => (flat["km_" + f.id] = f.km)); };
  const fromFlat = () => { ["neutral", "Ilim", "v", "dL", "dN", "PR", "IPR", "fault", "x", "Rf", "kase"].forEach((k) => (P[k] = flat[k])); P.feeders.forEach((f) => (f.km = flat["km_" + f.id])); const ff = P.feeders.find((f) => f.id === P.fault); if (P.x > ff.km) { P.x = ff.km; flat.x = ff.km; } };
  toFlat();
  const SCHEMA = [
    { g: { ro: "Neutrul rețelei", en: "Network neutral" }, col: "--seq0", open: true, openNarrow: false, items: [
      { k: "neutral", l: { ro: "Tratarea neutrului", en: "Neutral earthing" }, sel: Object.entries(NEU), wide: true },
      { k: "Ilim", l: { ro: "Curentul limitat de rezistor", en: "Resistor current limit" }, u: "A", step: 50, range: [100, 1000] },
      { k: "v", l: { ro: "Dezacordul bobinei v", en: "Coil detuning v" }, u: "–", step: 0.01, range: [-0.2, 0.2] },
      { k: "dL", l: { ro: "Pierderile bobinei (din I_L)", en: "Coil losses (of I_L)" }, u: "–", step: 0.005 },
      { k: "PR", l: { ro: "Rezistorul paralel conectat", en: "Parallel resistor connected" }, chk: true },
      { k: "IPR", l: { ro: "Curentul rezistorului paralel", en: "Parallel resistor current" }, u: "A", step: 1 },
      { k: "dN", l: { ro: "Scurgerile rețelei (din I_C)", en: "Network leakage (of I_C)" }, u: "–", step: 0.005 },
    ] },
    { g: { ro: "Defectul", en: "The fault" }, col: "--trip", open: true, openNarrow: false, items: [
      { k: "fault", l: { ro: "Plecarea defectă", en: "Faulted feeder" }, sel: P.feeders.map((f) => [f.id, { ro: `${f.id} · ${M.TYPES[f.type].ro}`, en: `${f.id} · ${M.TYPES[f.type].en}` }]), wide: true },
      { k: "x", l: { ro: "Distanța de la bare", en: "Distance from busbar" }, u: "km", step: 0.5, range: [0, 30] },
      { k: "Rf", l: { ro: "Rezistența de defect R_f", en: "Fault resistance R_f" }, u: "Ω", step: 10, range: [0, 5000] },
      { k: "kase", l: { ro: "Regimul", en: "Case" }, sel: [["max", { ro: "maxim", en: "maximum" }], ["min", { ro: "minim", en: "minimum" }]] },
    ] },
    { g: { ro: "Lungimile plecărilor", en: "Feeder lengths" }, col: "--c3", items: P.feeders.map((f) => ({ k: "km_" + f.id, l: { ro: `${f.id} · ${M.TYPES[f.type].ro}`, en: `${f.id} · ${M.TYPES[f.type].en}` }, u: "km", step: 1 })) },
  ];
  const PRESETS = [
    [{ ro: "Rețea compensată (exemplu)", en: "Compensated network (example)" }, () => { Object.assign(P, clone(M.DEFAULTS)); }],
    [{ ro: "Neutru izolat", en: "Isolated neutral" }, () => { P.neutral = "I"; }],
    [{ ro: "Rezistor 300 A", en: "300 A resistor" }, () => { P.neutral = "R"; P.Ilim = 300; }],
    [{ ro: "Defect rezistiv: 2 kΩ", en: "Resistive fault: 2 kΩ" }, () => { P.Rf = 2000; }],
    [{ ro: "Rezistorul paralel deconectat", en: "Parallel resistor disconnected" }, () => { P.neutral = "L"; P.PR = false; }],
    [{ ro: "Defect pe plecarea în cablu F5", en: "Fault on cable feeder F5" }, () => { P.fault = "F5"; P.x = 4; }],
  ];
  let ctl;
  function onChange(k) { fromFlat(); if (k === "neutral" || k === "preset") UI.method = REC[P.neutral]; toFlat(); ctl.sync(); syncMethods(); visKnobs(); render(); }
  function visKnobs() {
    const show = (k, on) => { const el = document.getElementById("in-" + k); if (el) el.closest(".knob").hidden = !on; };
    show("Ilim", P.neutral === "R"); ["v", "dL", "PR", "IPR"].forEach((k) => show(k, P.neutral === "L"));
  }

  function buildButtons() {
    const pr = document.getElementById("presets");
    pr.innerHTML = PRESETS.map((x, i) => `<button class="btn" data-i="${i}">${bi(x[0])}</button>`).join("");
    pr.onclick = (e) => { const b = e.target.closest("[data-i]"); if (!b) return; PRESETS[+b.dataset.i][1](); toFlat(); onChange("preset"); };
    const mt = document.getElementById("methods");
    mt.innerHTML = M.METHODS.map((m) => `<button class="btn" data-m="${m}">${bi(MNAME[m])}</button>`).join("");
    mt.onclick = (e) => { const b = e.target.closest("[data-m]"); if (!b) return; UI.method = b.dataset.m; syncMethods(); render(); };
  }
  const syncMethods = () => document.querySelectorAll("#methods [data-m]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.m === UI.method));

  /* ---------- laborator ---------- */
  function render() {
    const st = settingsNow();
    const r = M.compute(P), dec = M.decide(r, st);
    const m = UI.method, trips = dec.filter((x) => x.d[m]).map((x) => x.id);
    const correct = trips.length === 1 && trips[0] === P.fault, none = trips.length === 0;
    const cls = correct ? "ok" : none ? "warn" : "bad";
    const rec = REC[P.neutral] === m;
    let msg = bi(`Neutru ${NEU[P.neutral].ro}, defect pe ${P.fault} la ${PR.fmt(P.x, 1)} km prin ${PR.fmt(P.Rf, 0)} Ω. ${MNAME[m].ro}: `, `${NEU[P.neutral].en[0].toUpperCase() + NEU[P.neutral].en.slice(1)} neutral, fault on ${P.fault} at ${PR.fmt(P.x, 1)} km through ${PR.fmt(P.Rf, 0)} Ω. ${MNAME[m].en}: `);
    if (correct) msg += bi(`declanșează numai ${P.fault}.`, `only ${P.fault} trips.`);
    else if (none) msg += bi(r.u0 < st.U0start && m !== "51N" ? `nu pornește: U₀ = ${PR.fmt(r.u0 * 100, 1)} % e sub pragul de ${PR.fmt(st.U0start * 100, 0)} %.` : "nicio plecare nu declanșează: defectul nu e detectat.", r.u0 < st.U0start && m !== "51N" ? `no start: U₀ = ${PR.fmt(r.u0 * 100, 1)} % is below the ${PR.fmt(st.U0start * 100, 0)} % pickup.` : "no feeder trips: the fault is not detected.");
    else msg += bi(`declanșează ${trips.join(", ")}${trips.includes(P.fault) ? "" : " — nu plecarea defectă"}.`, `${trips.join(", ")} trip${trips.length > 1 ? "" : "s"}${trips.includes(P.fault) ? "" : " — not the faulted feeder"}.`);
    if (!rec) msg += " " + bi(`Pentru neutrul ${NEU[P.neutral].ro}, principiul recomandat este ${MNAME[REC[P.neutral]].ro}.`, `For the ${NEU[P.neutral].en} neutral, the recommended principle is ${MNAME[REC[P.neutral]].en}.`);
    document.getElementById("status").innerHTML = `<div class="status ${cls}"><span class="led"></span><span class="pill">${correct ? t("SELECTIV", "SELECTIVE") : none ? t("NEDETECTAT", "NOT DETECTED") : t("GREȘIT", "WRONG")}</span><span class="msg">${msg}</span></div>`;
    const ff = r.feeders.find((f) => f.id === P.fault);
    const kp = [
      [bi("Curentul de defect", "Fault current"), fA(r.IF)],
      [bi("Deplasarea neutrului U₀/U_f", "Neutral displacement U₀/U_f"), `${PR.fmt(r.u0 * 100, 1)} <small>%</small>`],
      [bi(`3I₀ pe ${P.fault}`, `3I₀ on ${P.fault}`), fA(ff.I)],
      [bi("Tensiunea fazelor sănătoase", "Healthy-phase voltage"), `${PR.fmt(Math.max(r.upu[1], r.upu[2]), 2)} <small>${t("u.r.", "p.u.")}</small>`],
    ];
    document.getElementById("kpis").innerHTML = kp.map(([l, v]) => `<div><div class="label">${l}</div><div class="v">${v}</div></div>`).join("");
    drawSLD(r, dec);
    drawPhasor(r, st);
    drawSens(st);
    drawTable(r, dec);
    renderSheet();
  }

  function drawSLD(r, dec) {
    const y0 = 60, xs = (i) => 220 + i * 95;
    let s = `<line x1="150" y1="${y0}" x2="${xs(5) + 40}" y2="${y0}" stroke="var(--ink)" stroke-width="5"/><text x="${xs(5) + 40}" y="${y0 - 10}" class="lbl" text-anchor="end">20 kV</text>`;
    // transformatorul și neutrul
    s += `<circle cx="105" cy="22" r="12" fill="none" stroke="var(--ink)" stroke-width="1.5"/><circle cx="105" cy="38" r="12" fill="none" stroke="var(--ink)" stroke-width="1.5"/><text x="125" y="20" class="tick">T1</text><line x1="105" y1="50" x2="105" y2="${y0}" stroke="var(--ink)"/><line x1="105" y1="${y0}" x2="150" y2="${y0}" stroke="var(--ink)" stroke-width="5"/>`;
    const nx = 105;
    if (P.neutral === "I") s += `<text x="${nx}" y="${y0 + 30}" class="tick" text-anchor="middle">${t("neutru izolat", "isolated neutral")}</text>`;
    else {
      s += `<line x1="${nx}" y1="${y0}" x2="${nx}" y2="${y0 + 14}" stroke="var(--ink)"/><rect x="${nx - 12}" y="${y0 + 14}" width="24" height="18" fill="var(--surface)" stroke="var(--ink)"/><text x="${nx + 18}" y="${y0 + 27}" class="tick">BPN</text><line x1="${nx}" y1="${y0 + 32}" x2="${nx}" y2="${y0 + 42}" stroke="var(--ink)"/>`;
      if (P.neutral === "R") s += `<rect x="${nx - 6}" y="${y0 + 42}" width="12" height="28" fill="var(--surface)" stroke="var(--seq0)" stroke-width="2"/><text x="${nx + 12}" y="${y0 + 60}" class="tick">${PR.fmt(P.Ilim, 0)} A</text>`;
      else {
        s += `<path d="M${nx} ${y0 + 42} c9 0 9 7 0 7 c9 0 9 7 0 7 c9 0 9 7 0 7 c9 0 9 7 0 7" fill="none" stroke="var(--seq0)" stroke-width="2"/><text x="${nx + 12}" y="${y0 + 58}" class="tick">I_L ${PR.fmt(r.ad.info.IL, 0)} A</text>`;
        if (P.PR) s += `<line x1="${nx}" y1="${y0 + 38}" x2="${nx - 26}" y2="${y0 + 38}" stroke="var(--ink)"/><rect x="${nx - 32}" y="${y0 + 44}" width="12" height="22" fill="var(--surface)" stroke="var(--c3)" stroke-width="2"/><line x1="${nx - 26}" y1="${y0 + 38}" x2="${nx - 26}" y2="${y0 + 44}" stroke="var(--ink)"/><line x1="${nx - 26}" y1="${y0 + 66}" x2="${nx - 26}" y2="${y0 + 74}" stroke="var(--ink)"/><line x1="${nx - 26}" y1="${y0 + 74}" x2="${nx}" y2="${y0 + 74}" stroke="var(--ink)"/><text x="${nx - 26}" y="${y0 + 90}" class="tick" text-anchor="middle">R_p</text>`;
      }
      s += `<line x1="${nx}" y1="${y0 + 70}" x2="${nx}" y2="${y0 + 76}" stroke="var(--ink)"/><path d="M${nx - 9} ${y0 + 76} h18 M${nx - 5} ${y0 + 80} h10 M${nx - 2} ${y0 + 84} h4" stroke="var(--ink)"/>`;
      s += `<text x="${nx}" y="${y0 + 106}" class="tick" text-anchor="middle">I_N ${fA(abs(r.IN))}</text>`;
    }
    r.feeders.forEach((f, i) => {
      const x = xs(i), trip = dec[i].d[UI.method], isF = f.id === P.fault;
      const col = FCOL[f.id];
      s += `<line x1="${x}" y1="${y0}" x2="${x}" y2="${y0 + 190}" stroke="${col}" stroke-width="${M.TYPES[f.type].C0 > 1e-7 ? 4 : 2}" ${M.TYPES[f.type].C0 > 1e-7 ? "" : 'stroke-dasharray="7 4"'}/>`;
      s += `<rect x="${x - 10}" y="${y0 + 16}" width="20" height="20" rx="2" fill="${trip ? "var(--trip)" : "var(--surface)"}" stroke="${trip ? "var(--trip)" : "var(--muted)"}" stroke-width="2"/>`;
      s += `<text x="${x + 7}" y="${y0 + 54}" class="tick" font-weight="600" fill="${isF ? "var(--trip)" : "var(--ink)"}">${fA(f.I)}</text>`;
      const short = M.TYPES[f.type].C0 > 1e-7 ? t("LES", "cable") : t("LEA", "OHL");
      s += `<text x="${x}" y="${y0 + 210}" class="lbl" text-anchor="middle" font-weight="600">${f.id}</text><text x="${x}" y="${y0 + 226}" class="tick" text-anchor="middle">${short} ${PR.fmt(f.km, 0)} km</text><text x="${x}" y="${y0 + 240}" class="tick" text-anchor="middle">I_C ${fA(f.Ic)}</text>`;
      if (isF) { const yf = y0 + 70 + (110 * P.x) / f.km; s += `<path d="M${x + 4} ${yf - 18} l10 12 -7 3 9 15" stroke="var(--trip)" stroke-width="2.5" fill="none"/><text x="${x + 24}" y="${yf + 2}" class="tick" fill="var(--trip)">${fA(r.IF)}</text>`; }
    });
    s += `<g transform="translate(150,${y0 + 262})"><rect x="0" y="-10" width="14" height="14" fill="var(--trip)"/><text x="20" y="1" class="tick">${t("declanșează", "trips")} (${t(MNAME[UI.method])})</text><line x1="320" x2="350" y1="-3" y2="-3" stroke="var(--muted)" stroke-width="4"/><text x="356" y="1" class="tick">${t("cablu", "cable")}</text><line x1="420" x2="450" y1="-3" y2="-3" stroke="var(--muted)" stroke-width="2" stroke-dasharray="7 4"/><text x="456" y="1" class="tick">LEA</text></g>`;
    document.getElementById("sld").innerHTML = s;
  }

  function drawPhasor(r, st) {
    // fazori, raportați la −3U0 (orizontal, spre dreapta)
    const cx = 190, cy = 170, R = 120;
    let s = `<text x="${cx}" y="22" class="lbl" text-anchor="middle" font-weight="600">${t("Fazorii 3I₀ (referința −3U₀)", "3I₀ phasors (reference −3U₀)")}</text>`;
    const pt = (a, L) => [cx + L * Math.cos((a * Math.PI) / 180), cy - L * Math.sin((a * Math.PI) / 180)];
    const sector = (a0, a1) => { let pts = [`${cx},${cy}`]; for (let i = 0; i <= 40; i++) { const [x, y] = pt(a0 + ((a1 - a0) * i) / 40, R); pts.push(`${x.toFixed(1)},${y.toFixed(1)}`); } return `<polygon points="${pts.join(" ")}" fill="var(--ok-bg)"/>`; };
    const m = UI.method;
    if (m === "67N") s += sector(st.rcaN - 90, st.rcaN + 90);
    if (m === "sin") s += sector(0, 180);
    if (m === "cos") s += sector(-90, 90);
    s += `<circle cx="${cx}" cy="${cy}" r="${R}" fill="none" stroke="var(--line)"/><line x1="${cx - R - 6}" y1="${cy}" x2="${cx + R + 6}" y2="${cy}" class="grid"/><line x1="${cx}" y1="${cy - R - 6}" x2="${cx}" y2="${cy + R + 6}" class="grid"/>`;
    s += PR.arrow(cx, cy, cx + R + 4, cy, "var(--muted)", 2) + `<text x="${cx + R + 8}" y="${cy - 6}" class="tick">−3U₀</text>`;
    const mx = Math.max(...r.feeders.map((f) => f.I), 1e-9);
    r.feeders.forEach((f, i) => {
      const isF = f.id === P.fault, L = Math.max(8, (R * 0.95 * f.I) / mx);
      const [x, y] = pt(f.phi, L);
      s += PR.arrow(cx, cy, x, y, isF ? "var(--trip)" : FCOL[f.id], isF ? 3 : 2);
      const [lx, ly] = pt(f.phi, L + 12 + (isF ? 0 : (i % 3) * 11));
      s += `<text x="${lx + (isF ? 0 : 14)}" y="${ly + 4}" class="tick" text-anchor="middle" fill="${isF ? "var(--trip)" : FCOL[f.id]}" font-weight="600">${f.id}</text>`;
    });
    s += `<text x="${cx}" y="${cy + R + 34}" class="tick" text-anchor="middle">${m === "51N" ? t("51N nu folosește direcția", "51N uses no direction") : m === "Y0" ? t("Y₀: vezi planul admitanțelor", "Y₀: see the admittance plane") : t("zona verde: sensul „spre linie”", "green zone: “into the line”")}</text>`;
    // planul admitanțelor
    const ax = 570, ay = 170, AR = 120;
    s += `<text x="${ax}" y="22" class="lbl" text-anchor="middle" font-weight="600">${t("Planul admitanțelor Y₀ = 3I₀/(−3U₀)", "Admittance plane Y₀ = 3I₀/(−3U₀)")}</text>`;
    const ys = r.feeders.map((f) => f.Y0);
    const lim = Math.max(...ys.map((y) => Math.max(Math.abs(y.re), Math.abs(y.im))), 1e-6) * 1.15;
    const sx = (g) => ax + (AR * g) / lim, sy = (b) => ay - (AR * b) / lim;
    const set = st.feeders[P.fault];
    if (isFinite(set.G) && set.G < lim) s += `<rect x="${sx(set.G)}" y="${ay - AR}" width="${ax + AR - sx(set.G)}" height="${2 * AR}" fill="var(--ok-bg)"/>`;
    if (isFinite(set.B) && set.B < lim) s += `<rect x="${ax - AR}" y="${ay - AR}" width="${2 * AR}" height="${sy(set.B) - (ay - AR)}" fill="var(--ok-bg)"/>`;
    s += `<rect x="${ax - AR}" y="${ay - AR}" width="${2 * AR}" height="${2 * AR}" fill="none" stroke="var(--line)"/><line x1="${ax - AR}" y1="${ay}" x2="${ax + AR}" y2="${ay}" class="ax"/><line x1="${ax}" y1="${ay - AR}" x2="${ax}" y2="${ay + AR}" class="ax"/>`;
    s += `<text x="${ax + AR - 2}" y="${ay - 6}" class="tick" text-anchor="end">G</text><text x="${ax + 6}" y="${ay - AR + 12}" class="tick">B</text>`;
    s += `<text x="${ax + AR}" y="${ay + AR + 16}" class="tick" text-anchor="end">±${PR.sig(lim * 1000, 2)} mS</text>`;
    r.feeders.forEach((f) => { const isF = f.id === P.fault; s += `<circle cx="${sx(f.Y0.re)}" cy="${sy(f.Y0.im)}" r="${isF ? 6 : 4.5}" fill="${isF ? "var(--trip)" : FCOL[f.id]}" stroke="var(--surface)" stroke-width="1.5"/><text x="${sx(f.Y0.re) + 8}" y="${sy(f.Y0.im) + (isF ? -6 : 4)}" class="tick" fill="${isF ? "var(--trip)" : FCOL[f.id]}">${f.id}</text>`; });
    s += `<text x="${ax}" y="${ay + AR + 34}" class="tick" text-anchor="middle">${t(`zona verde: G ≥ G> sau B ≥ B> (reglajele lui ${P.fault})`, `green zone: G ≥ G> or B ≥ B> (${P.fault} settings)`)}</text>`;
    document.getElementById("phasor").innerHTML = s;
  }

  function drawSens(st) {
    const Rs = []; for (let i = 0; i <= 48; i++) Rs.push(Math.pow(10, (4 * i) / 48));  // 1 Ω … 10 kΩ
    const pts = Rs.map((Rf) => { const r = M.compute({ ...P, Rf }); const f = r.feeders.find((g) => g.id === P.fault); return { Rf, I: f.I, c: f.Icos, s: f.Isin, u: r.u0 }; });
    const set = st.feeders[P.fault];
    // panoul stâng: curenți (log–log)
    const L = 60, Rr = 380, T = 26, B = 240;
    const ymax = Math.pow(10, Math.ceil(Math.log10(Math.max(...pts.map((p) => p.I), set.I0, 1)))), ymin = 0.1;
    const lx = (R) => L + ((Rr - L) * Math.log10(R)) / 4, ly = (v) => B - ((B - T) * (Math.log10(Math.max(v, ymin)) - Math.log10(ymin))) / (Math.log10(ymax) - Math.log10(ymin));
    let s = `<text x="${(L + Rr) / 2}" y="14" class="lbl" text-anchor="middle" font-weight="600">${t(`Curenții măsurați pe ${P.fault}`, `Currents measured on ${P.fault}`)}</text>`;
    for (let e = 0; e <= 4; e++) s += `<line x1="${lx(Math.pow(10, e))}" x2="${lx(Math.pow(10, e))}" y1="${T}" y2="${B}" class="grid"/><text x="${lx(Math.pow(10, e))}" y="${B + 14}" class="tick" text-anchor="middle">${["1", "10", "100", "1k", "10k"][e]}</text>`;
    for (let e = Math.log10(ymin); e <= Math.log10(ymax); e++) { const v = Math.pow(10, e); s += `<line x1="${L}" x2="${Rr}" y1="${ly(v)}" y2="${ly(v)}" class="grid"/><text x="${L - 4}" y="${ly(v) + 4}" class="tick" text-anchor="end">${PR.sig(v, 1)}</text>`; }
    const line = (k, col, dash) => `<polyline points="${pts.filter((p) => p[k] > 0).map((p) => `${lx(p.Rf).toFixed(1)},${ly(p[k]).toFixed(1)}`).join(" ")}" fill="none" stroke="${col}" stroke-width="2" ${dash ? `stroke-dasharray="${dash}"` : ""}/>`;
    s += line("I", "var(--ink)") + line("c", "var(--c4)", "6 3") + line("s", "var(--c5)", "2 3");
    const hl = (v, col, lab) => (v > ymin && v < ymax ? `<line x1="${L}" x2="${Rr}" y1="${ly(v)}" y2="${ly(v)}" stroke="${col}" stroke-dasharray="5 3"/><text x="${Rr - 2}" y="${ly(v) - 3}" class="tick" text-anchor="end" fill="${col}">${lab}</text>` : "");
    const mth = UI.method;
    if (mth === "51N") s += hl(set.I0, "var(--trip)", `I₀> ${fA(set.I0)}`);
    if (mth === "67N") s += hl(set.I0dir, "var(--trip)", `I₀> ${fA(set.I0dir)}`);
    if (mth === "cos") s += hl(set.Icos, "var(--trip)", `I₀cos> ${fA(set.Icos)}`);
    if (mth === "sin") s += hl(set.Isin, "var(--trip)", `I₀sin> ${fA(set.Isin)}`);
    s += `<line x1="${lx(Math.max(P.Rf, 1))}" x2="${lx(Math.max(P.Rf, 1))}" y1="${T}" y2="${B}" stroke="var(--trip)"/>`;
    s += `<text x="${Rr}" y="${B + 28}" class="tick" text-anchor="end">R_f, Ω</text><text x="${L - 40}" y="${(T + B) / 2}" class="tick" text-anchor="middle" transform="rotate(-90 ${L - 40} ${(T + B) / 2})">A</text>`;
    [["var(--ink)", "", "|3I₀|"], ["var(--c4)", "6 3", "I₀·cos φ"], ["var(--c5)", "2 3", "I₀·sin φ"]].forEach(([c, d, txt], i) => { const x = L + i * 105; s += `<line x1="${x}" x2="${x + 20}" y1="${B + 46}" y2="${B + 46}" stroke="${c}" stroke-width="2.4" ${d ? `stroke-dasharray="${d}"` : ""}/><text x="${x + 24}" y="${B + 50}" class="tick">${txt}</text>`; });
    // panoul drept: U0
    const L2 = 450, R2 = 744;
    const ux = (R) => L2 + ((R2 - L2) * Math.log10(R)) / 4, uy = (u) => B - (B - T) * Math.min(u, 1.15) / 1.15;
    s += `<text x="${(L2 + R2) / 2}" y="14" class="lbl" text-anchor="middle" font-weight="600">${t("Deplasarea neutrului U₀/U_f", "Neutral displacement U₀/U_f")}</text>`;
    for (let e = 0; e <= 4; e++) s += `<line x1="${ux(Math.pow(10, e))}" x2="${ux(Math.pow(10, e))}" y1="${T}" y2="${B}" class="grid"/><text x="${ux(Math.pow(10, e))}" y="${B + 14}" class="tick" text-anchor="middle">${["1", "10", "100", "1k", "10k"][e]}</text>`;
    [0, 0.25, 0.5, 0.75, 1].forEach((u) => (s += `<line x1="${L2}" x2="${R2}" y1="${uy(u)}" y2="${uy(u)}" class="grid"/><text x="${L2 - 4}" y="${uy(u) + 4}" class="tick" text-anchor="end">${PR.fmt(u * 100, 0)} %</text>`));
    s += `<polyline points="${pts.map((p) => `${ux(p.Rf).toFixed(1)},${uy(p.u).toFixed(1)}`).join(" ")}" fill="none" stroke="var(--seq0)" stroke-width="2.4"/>`;
    s += `<line x1="${L2}" x2="${R2}" y1="${uy(st.U0start)}" y2="${uy(st.U0start)}" stroke="var(--trip)" stroke-dasharray="5 3"/><text x="${R2 - 2}" y="${uy(st.U0start) - 3}" class="tick" text-anchor="end" fill="var(--trip)">U₀> ${PR.fmt(st.U0start * 100, 0)} %</text>`;
    s += `<line x1="${ux(Math.max(P.Rf, 1))}" x2="${ux(Math.max(P.Rf, 1))}" y1="${T}" y2="${B}" stroke="var(--trip)"/><text x="${R2}" y="${B + 28}" class="tick" text-anchor="end">R_f, Ω</text>`;
    document.getElementById("sens").innerHTML = s;
  }

  function drawTable(r, dec) {
    let h = `<tr><th>${bi("Plecarea", "Feeder")}</th><th class="n">I_C</th><th class="n">|3I₀|</th><th class="n">φ</th><th class="n">I₀·cos φ</th><th class="n">I₀·sin φ</th><th class="n">G</th><th class="n">B</th>${M.METHODS.map((m) => `<th class="n">${m === "sin" ? "sin φ" : m === "cos" ? "cos φ" : m}</th>`).join("")}</tr>`;
    r.feeders.forEach((f, i) => {
      const isF = f.id === P.fault;
      h += `<tr${isF ? ' class="res"' : ""}><td><span class="swatch" style="background:${FCOL[f.id]};margin-right:6px"></span>${f.id} · ${t(M.TYPES[f.type])} ${PR.fmt(f.km, 0)} km</td><td class="n">${fA(f.Ic)}</td><td class="n">${fA(f.I)}</td><td class="n">${PR.fmt(f.phi, 1)}°</td><td class="n">${PR.fmt(f.Icos, 2)} A</td><td class="n">${PR.fmt(f.Isin, 2)} A</td><td class="n">${PR.fmt(f.Y0.re * 1000, 3)}</td><td class="n">${PR.fmt(f.Y0.im * 1000, 3)}</td>${M.METHODS.map((m) => `<td class="n">${dec[i].d[m] ? `<span class="yes">${t("DA", "TRIP")}</span>` : "—"}</td>`).join("")}</tr>`;
    });
    h += `<tr><td colspan="13" class="note">${bi("G și B în mS. „DA”: plecarea declanșează după principiul respectiv, cu reglajele din fișa de reglaje.", "G and B in mS. “TRIP”: the feeder trips under that principle, with the settings from the settings sheet.")}</td></tr>`;
    document.getElementById("ftab").innerHTML = h;
  }

  /* ---------- reglaje ---------- */
  let rgCtl;
  function renderSheet() {
    const st = settingsNow();
    const ad = M.admittances(P, { ...window.M01.DEFAULTS });
    document.getElementById("sheet-meta").innerHTML = bi(`Neutru ${NEU[P.neutral].ro} · I_C total ${fA(ad.IcTot)} · R_f țintă ${PR.fmt(RG.RfT, 0)} Ω`, `${NEU[P.neutral].en} neutral · total I_C ${fA(ad.IcTot)} · target R_f ${PR.fmt(RG.RfT, 0)} Ω`);
    let h = `<tr><th>${bi("Plecarea", "Feeder")}</th><th>${bi("Tipul", "Type")}</th><th class="n">${bi("Lungimea", "Length")}</th><th class="n">C₀·ℓ</th><th class="n">I_C</th></tr>`;
    ad.fd.forEach((f) => { h += `<tr><td>${f.id}</td><td>${t(M.TYPES[f.type])}</td><td class="n">${PR.fmt(f.km, 0)} km</td><td class="n">${PR.fmt(M.TYPES[f.type].C0 * f.km * 1e6, 3)} µF</td><td class="n">${fA(f.Ic)}</td></tr>`; });
    h += `<tr class="res"><td colspan="4">${bi("Total rețea galvanic legată", "Total galvanically connected network")}</td><td class="n">${fA(ad.IcTot)}</td></tr>`;
    document.getElementById("rg-net").innerHTML = h;
    const U = ad.U;
    let nt;
    if (P.neutral === "R") nt = `R_N = U_f/I_lim = ${PR.fmt(U, 0)}/${PR.fmt(P.Ilim, 0)} = ${PR.fmt(ad.info.RN, 2)} Ω\n${t("Curentul activ al rezistorului domină: zeci–sute de amperi la defecte rezistive.", "The resistor's active current dominates: tens to hundreds of amperes for resistive faults.")}`;
    else if (P.neutral === "L") nt = `I_L = I_C·(1 + v) = ${PR.fmt(ad.IcTot, 1)}·(1 + ${PR.fmt(P.v, 2)}) = ${PR.fmt(ad.info.IL, 1)} A\nI_w = d_L·I_L + I_Rp + d_N·I_C = ${PR.fmt(ad.info.IwL, 2)} + ${PR.fmt(ad.info.IPR, 1)} + ${PR.fmt(P.dN * ad.IcTot, 2)} = ${PR.fmt(ad.info.IwL + ad.info.IPR + P.dN * ad.IcTot, 2)} A\nI_rest ≈ √((I_C − I_L)² + I_w²) = ${PR.fmt(Math.hypot(ad.IcTot - ad.info.IL, ad.info.IwL + ad.info.IPR + P.dN * ad.IcTot), 2)} A`;
    else nt = `I_F ≈ I_C = ${PR.fmt(ad.IcTot, 1)} A ${t("(defect franc)", "(bolted fault)")}`;
    document.getElementById("rg-neutral").textContent = nt;
    document.getElementById("rg-u0").textContent = `U₀> = k_U·u_nesim = ${PR.fmt(RG.kU, 2)}·${PR.fmt(RG.uUnb * 100, 1)} % → ${PR.fmt(S.U0start * 100, 0)} % U_f\n${t("Defect pe", "Fault on")} ${P.fault} ${t("la", "at")} ${PR.fmt(P.x, 1)} km: U₀ ≥ U₀> ${t("până la", "up to")} R_f = ${PR.fmt(S.RfMaxU, 0)} Ω`;
    // pragurile pe plecări
    const rec = REC[P.neutral];
    h = `<tr><th>${bi("Plecarea", "Feeder")}</th><th class="n">I_C</th><th class="n">51N I₀&gt;</th><th class="n">k<sub>sens</sub> 51N</th><th class="n">67N I₀&gt;</th><th class="n">I₀sin&gt;</th><th class="n">I₀cos&gt;</th><th class="n">G&gt;</th><th class="n">B&gt;</th><th class="n">R<sub>f</sub> max 51N</th><th class="n">R<sub>f</sub> max ${rec === "sin" ? "sin φ" : rec === "cos" ? "cos φ" : rec}</th></tr>`;
    const weak = [];
    const stt = st;
    P.feeders.forEach((f) => {
      const s2 = S.feeders[f.id];
      const r0 = M.compute({ ...P, fault: f.id, x: f.km, Rf: 0, kase: "min" }).feeders.find((g) => g.id === f.id);
      const ks = r0.I / s2.I0;
      if (ks < RG.kSens) weak.push(f.id);
      const pf = { ...P, fault: f.id, x: f.km };
      const rf51 = M.RfLimit(pf, stt, "51N"), rfRec = M.RfLimit(pf, stt, rec);
      const fRf = (v) => (isFinite(v) ? (v === 0 ? t("nu vede", "none") : `${PR.fmt(v, 0)} Ω`) : "> 1 MΩ");
      h += `<tr><td>${f.id}</td><td class="n">${fA(S.rep[f.id].Ic)}</td><td class="n">${fA(s2.I0)}</td><td class="n"><span class="${ks >= RG.kSens ? "ok" : "bad"}">${PR.fmt(ks, 2)}</span></td><td class="n">${fA(s2.I0dir)}</td><td class="n">${fA(s2.Isin)}</td><td class="n">${fA(s2.Icos)}</td><td class="n">${PR.fmt(s2.G * 1000, 3)} mS</td><td class="n">${isFinite(s2.B) ? PR.fmt(s2.B * 1000, 3) + " mS" : "—"}</td><td class="n">${fRf(rf51)}</td><td class="n">${fRf(rfRec)}</td></tr>`;
    });
    document.getElementById("rg-set").innerHTML = h;
    const why = { R: bi("Rezistorul dă un curent activ mare: 67N cu unghiul 0° e sigur și sensibil; 51N merge și el, dacă pragul trece de curentul capacitiv propriu.", "The resistor gives a large active current: 67N with a 0° angle is secure and sensitive; 51N also works if its pickup exceeds the own capacitive current."), I: bi("Plecarea defectă duce curentul capacitiv al celorlalte plecări, la +90° față de −3U₀: criteriul I₀·sin φ e potrivit. Componenta activă e prea mică pentru cos φ.", "The faulted feeder carries the other feeders' capacitive current, at +90° relative to −3U₀: the I₀·sin φ criterion fits. The active component is too small for cos φ."), L: bi("Bobina anulează componenta reactivă; rămâne componenta activă, mărită de rezistorul paralel: criteriul I₀·cos φ (wattmetric). Protecția de admitanță e o alternativă cu sensibilitate limitată doar de pragul U₀>.", "The coil cancels the reactive component; the active component remains, increased by the parallel resistor: the I₀·cos φ (wattmetric) criterion. Admittance protection is an alternative whose sensitivity is limited only by the U₀> pickup.") }[P.neutral];
    document.getElementById("rg-note").innerHTML = `<b class="k">${bi("Interpretare", "Interpretation")}</b>${why}` + (weak.length ? " " + bi(`Pentru ${weak.join(", ")}, 51N nu are sensibilitatea cerută nici la defect franc: curentul capacitiv propriu împinge pragul prea sus. Aici e nevoie de un principiu direcțional.`, `For ${weak.join(", ")}, 51N lacks the required sensitivity even for a bolted fault: the own capacitive current pushes the pickup too high. A directional principle is needed here.`) : "");
    document.getElementById("rg-cap").textContent = t(`Principiul recomandat pentru neutrul ${NEU[P.neutral].ro}: ${MNAME[rec].ro}`, `Recommended principle for the ${NEU[P.neutral].en} neutral: ${MNAME[rec].en}`);
    const val = (s2) => ({ "67N": `I₀> ${fA(s2.I0dir)}, θcN ${S.rcaN}°`, sin: `I₀·sin φ> ${fA(s2.Isin)}`, cos: `I₀·cos φ> ${fA(s2.Icos)}` }[rec]);
    h = `<tr><th>${bi("Plecarea", "Feeder")}</th><th>${bi("Funcția", "Function")}</th><th>${bi("Reglaj", "Setting")}</th><th class="n">U₀&gt;</th><th class="n">${bi("Temporizare", "Delay")}</th><th>${bi("Alternativă (admitanță)", "Alternative (admittance)")}</th></tr>`;
    P.feeders.forEach((f) => { const s2 = S.feeders[f.id]; h += `<tr><td>${f.id}</td><td>${t(MNAME[rec])}</td><td class="mono">${val(s2)}</td><td class="n">${PR.fmt(S.U0start * 100, 0)} %</td><td class="n">${PR.fmt(RG.tF, 2)} s</td><td class="mono">G> ${PR.fmt(s2.G * 1000, 3)} mS${isFinite(s2.B) ? `, B> ${PR.fmt(s2.B * 1000, 3)} mS` : ""}</td></tr>`; });
    h += `<tr><td>${t("Neutrul / sosirea", "Neutral / incomer")}</td><td>${P.neutral === "R" ? "51N" : "59N"}</td><td class="mono">${P.neutral === "R" ? t("pe TC-ul rezistorului", "on the resistor CT") : `U₀> ${PR.fmt(S.U0start * 100, 0)} %`}</td><td class="n">${PR.fmt(S.U0start * 100, 0)} %</td><td class="n">${PR.fmt(RG.tF + RG.cti, 2)} s</td><td>${t("rezervă pentru toate plecările", "backup for all feeders")}</td></tr>`;
    document.getElementById("rg-sheet").innerHTML = h;
    document.getElementById("rg-time").textContent = t(`Plecările: ${PR.fmt(RG.tF, 2)} s. Rezerva (neutrul sau 59N pe bare): ${PR.fmt(RG.tF, 2)} + ${PR.fmt(RG.cti, 2)} = ${PR.fmt(RG.tF + RG.cti, 2)} s. În rețelele compensate, procedura operatorului poate cere doar semnalizarea defectului pentru un timp; atunci treapta de declanșare primește temporizarea stabilită de operator.`, `Feeders: ${PR.fmt(RG.tF, 2)} s. Backup (neutral or busbar 59N): ${PR.fmt(RG.tF, 2)} + ${PR.fmt(RG.cti, 2)} = ${PR.fmt(RG.tF + RG.cti, 2)} s. In compensated networks the operator's procedure may require only an alarm for a while; the tripping stage then gets the delay set by the operator.`);
  }
  document.getElementById("copy-sheet").addEventListener("click", (e) => {
    const rec = REC[P.neutral];
    const rows = [["plecare", "functie", "I0_51N_A", "I0_67N_A", "I0sin_A", "I0cos_A", "G_mS", "B_mS", "U0_start_pct", "t_s"]];
    P.feeders.forEach((f) => { const s2 = S.feeders[f.id]; rows.push([f.id, rec, PR.xnum(s2.I0, 1), PR.xnum(s2.I0dir, 1), PR.xnum(s2.Isin, 1), PR.xnum(s2.Icos, 1), PR.xnum(s2.G * 1000, 3), isFinite(s2.B) ? PR.xnum(s2.B * 1000, 3) : "", PR.xnum(S.U0start * 100, 0), PR.xnum(RG.tF, 2)]); });
    PR.copyTSV(rows, e.currentTarget);
  });

  /* ---------- test ---------- */
  const MCQ = [
    { q: { ro: "Într-o rețea cu neutru izolat, ce curent rezidual vede plecarea defectă?", en: "In an isolated-neutral network, what residual current does the faulted feeder see?" }, o: [{ ro: "Curentul capacitiv al tuturor celorlalte plecări", en: "The capacitive current of all the other feeders" }, { ro: "Numai curentul ei capacitiv", en: "Only its own capacitive current" }, { ro: "Curentul de sarcină", en: "The load current" }, { ro: "Zero", en: "Zero" }], a: 0, e: { ro: "Relația (2): 3I₀,k = −3(Y₀ − Y₀k)U₀.", en: "Relation (2): 3I₀,k = −3(Y₀ − Y₀k)U₀." } },
    { q: { ro: "Ce curent vede o plecare sănătoasă?", en: "What current does a healthy feeder see?" }, o: [{ ro: "Curentul ei capacitiv, la −90° față de −3U₀", en: "Its own capacitive current, at −90° relative to −3U₀" }, { ro: "Curentul de defect", en: "The fault current" }, { ro: "Curentul bobinei", en: "The coil current" }, { ro: "Nimic", en: "Nothing" }], a: 0, e: { ro: "Relația (2), cu Y₀i aproape pur capacitivă.", en: "Relation (2), with Y₀i almost purely capacitive." } },
    { q: { ro: "Ce criteriu se folosește în rețeaua cu neutru izolat?", en: "Which criterion is used in an isolated-neutral network?" }, o: [{ ro: "I₀·sin φ (componenta reactivă)", en: "I₀·sin φ (reactive component)" }, { ro: "I₀·cos φ", en: "I₀·cos φ" }, { ro: "Numai 59N", en: "Only 59N" }, { ro: "Protecția diferențială", en: "Differential protection" }], a: 0, e: { ro: "Curentul plecării defecte e la +90° față de −3U₀.", en: "The faulted-feeder current is at +90° relative to −3U₀." } },
    { q: { ro: "Ce criteriu se folosește în rețeaua compensată?", en: "Which criterion is used in a compensated network?" }, o: [{ ro: "I₀·cos φ (wattmetric), unghi 0°", en: "I₀·cos φ (wattmetric), 0° angle" }, { ro: "I₀·sin φ", en: "I₀·sin φ" }, { ro: "51N cu prag mic", en: "51N with a low pickup" }, { ro: "67 de fază", en: "Phase 67" }], a: 0, e: { ro: "Bobina anulează componenta reactivă; rămâne cea activă.", en: "The coil cancels the reactive component; the active one remains." } },
    { q: { ro: "De ce se conectează un rezistor în paralel cu bobina de stingere?", en: "Why is a resistor connected in parallel with the arc suppression coil?" }, o: [{ ro: "Ca să mărească componenta activă a curentului de defect", en: "To increase the active component of the fault current" }, { ro: "Ca să reducă tensiunea", en: "To reduce the voltage" }, { ro: "Ca să compenseze capacitățile", en: "To compensate the capacitances" }, { ro: "Pentru măsurarea frecvenței", en: "For frequency measurement" }], a: 0, e: { ro: "Componenta activă din pierderi e adesea prea mică pentru o decizie sigură.", en: "The active component from losses is often too small for a secure decision." } },
    { q: { ro: "De ce trebuie ca pragul 51N al unei plecări să depășească curentul ei capacitiv?", en: "Why must a feeder's 51N pickup exceed its own capacitive current?" }, o: [{ ro: "Ca să nu declanșeze la un defect pe altă plecare", en: "So it does not trip for a fault on another feeder" }, { ro: "Ca să fie mai rapidă", en: "To be faster" }, { ro: "Din cauza curentului de sarcină", en: "Because of load current" }, { ro: "Pentru TC", en: "For the CT" }], a: 0, e: { ro: "Relația (5): declanșarea simpatică a plecărilor lungi în cablu.", en: "Relation (5): sympathetic tripping of long cable feeders." } },
    { q: { ro: "Ce proprietate are admitanța măsurată Y₀ = 3I₀/(−3U₀)?", en: "What property does the measured admittance Y₀ = 3I₀/(−3U₀) have?" }, o: [{ ro: "Nu depinde de rezistența de defect", en: "It does not depend on the fault resistance" }, { ro: "Crește cu R_f", en: "It increases with R_f" }, { ro: "E mereu zero pe plecarea defectă", en: "It is always zero on the faulted feeder" }, { ro: "Depinde de sarcină", en: "It depends on load" }], a: 0, e: { ro: "R_f schimbă amplitudinile lui U₀ și 3I₀, nu raportul lor.", en: "R_f changes the magnitudes of U₀ and 3I₀, not their ratio." } },
    { q: { ro: "Ce limitează sensibilitatea protecției de admitanță?", en: "What limits the sensitivity of admittance protection?" }, o: [{ ro: "Pragul de pornire pe tensiune homopolară", en: "The residual-voltage start pickup" }, { ro: "Curentul de sarcină", en: "The load current" }, { ro: "Raportul TC", en: "The CT ratio" }, { ro: "Lungimea plecării", en: "The feeder length" }], a: 0, e: { ro: "Când U₀ scade sub U₀>, funcția nu pornește.", en: "When U₀ drops below U₀>, the function does not start." } },
    { q: { ro: "În rețeaua tratată prin rezistor, cum variază U₀ cu R_f?", en: "In a resistor-earthed network, how does U₀ vary with R_f?" }, o: [{ ro: "Scade repede, pentru că Y₀ e mare", en: "It falls quickly, because Y₀ is large" }, { ro: "Rămâne aproape U_f până la kΩ", en: "It stays near U_f up to kΩ" }, { ro: "Crește", en: "It increases" }, { ro: "Nu depinde", en: "It does not depend" }], a: 0, e: { ro: "Relația (7) cu Y₀ ≈ 1/(3R_N).", en: "Relation (7) with Y₀ ≈ 1/(3R_N)." } },
    { q: { ro: "Cu cât e mai mare curentul capacitiv al unui km de cablu de 185 mm² față de un km de LEA 70/12, în rețeaua-exemplu?", en: "How much larger is the capacitive current of 1 km of 185 mm² cable than of 1 km of 70/12 overhead line, in the example network?" }, o: [{ ro: "De circa 66 de ori", en: "About 66 times" }, { ro: "De 2 ori", en: "2 times" }, { ro: "La fel", en: "The same" }, { ro: "De 1000 de ori", en: "1000 times" }], a: 0, e: { ro: "2,97 A/km față de 0,045 A/km.", en: "2.97 A/km against 0.045 A/km." } },
    { q: { ro: "Cât e curentul rezidual la locul defectului într-o rețea compensată (aproximativ)?", en: "What is the residual current at the fault in a compensated network (approximately)?" }, o: [{ ro: "I_C·√(v² + d²)", en: "I_C·√(v² + d²)" }, { ro: "I_C", en: "I_C" }, { ro: "I_C·(1 + v)", en: "I_C·(1 + v)" }, { ro: "Zero", en: "Zero" }], a: 0, e: { ro: "Relația (4): rămân dezacordul și componenta activă.", en: "Relation (4): the detuning and the active component remain." } },
    { q: { ro: "Până la cât poate ajunge deplasarea neutrului în regim normal într-o rețea compensată cu multe LEA netranspuse, după manualul ABB?", en: "How high can the healthy-state neutral displacement reach in a compensated network with many untransposed overhead lines, per the ABB manual?" }, o: [{ ro: "Până la 30 % din U_f", en: "Up to 30 % of U_f" }, { ro: "0,1 %", en: "0.1 %" }, { ro: "100 %", en: "100 %" }, { ro: "Niciodată peste 1 %", en: "Never above 1 %" }], a: 0, e: { ro: "De aceea pragul U₀> se stabilește din măsurători în rețea.", en: "This is why the U₀> pickup is set from network measurements." } },
  ];
  function NUM() {
    const km = PR.rnd(2, 15, 0.5), Ict = PR.rnd(20, 150, 1), Ick = PR.rnd(2, 15, 0.5), Rf = PR.rnd(100, 3000, 50), Ic = PR.rnd(20, 120, 1), v = PR.rnd(-0.1, 0.1, 0.01), d = PR.rnd(0.02, 0.08, 0.005);
    const Uf = 20000 / Math.sqrt(3);
    return [
      { q: { ro: `Ce curent capacitiv are o plecare în cablu de ${PR.fmt(km, 1)} km, cu C₀ = 273 nF/km, la 20 kV?`, en: `What capacitive current does a ${PR.fmt(km, 1)} km cable feeder have, with C₀ = 273 nF/km, at 20 kV?` }, u: "A", v: 3 * 2 * Math.PI * 50 * 273e-9 * km * Uf, e: { ro: "Relația (1).", en: "Relation (1)." } },
      { q: { ro: `Rețea izolată cu I_C total = ${Ict} A. Defect franc pe o plecare cu I_C = ${PR.fmt(Ick, 1)} A. Ce curent rezidual vede ea?`, en: `Isolated network with total I_C = ${Ict} A. Bolted fault on a feeder with I_C = ${PR.fmt(Ick, 1)} A. What residual current does it see?` }, u: "A", v: Ict - Ick, e: { ro: "Relația (3) cu U₀ = U_f.", en: "Relation (3) with U₀ = U_f." } },
      { q: { ro: `Rețea izolată de 20 kV cu I_C = ${Ic} A. Cât e U₀/U_f, în %, la un defect prin R_f = ${Rf} Ω (relația 7)?`, en: `Isolated 20 kV network with I_C = ${Ic} A. What is U₀/U_f, in %, for a fault through R_f = ${Rf} Ω (relation 7)?` }, u: "%", v: 100 / Math.sqrt(1 + Math.pow((Rf * Ic) / Uf, 2)), e: { ro: "Y₀ = jI_C/(3U_f), deci U₀/U_f = 1/√(1 + (R_f·I_C/U_f)²).", en: "Y₀ = jI_C/(3U_f), so U₀/U_f = 1/√(1 + (R_f·I_C/U_f)²)." } },
      { q: { ro: `Rețea compensată: I_C = ${Ic} A, v = ${PR.fmt(v, 2)}, d = ${PR.fmt(d, 3)}. Cât e curentul rezidual la defect franc?`, en: `Compensated network: I_C = ${Ic} A, v = ${PR.fmt(v, 2)}, d = ${PR.fmt(d, 3)}. What is the residual current for a bolted fault?` }, u: "A", v: Ic * Math.sqrt(v * v + d * d), e: { ro: "Relația (4).", en: "Relation (4)." } },
    ];
  }

  /* ---------- pornire ---------- */
  ctl = PR.controls(document.getElementById("controls"), SCHEMA, flat, onChange);
  const RGS = [{ g: { ro: "Coeficienți", en: "Factors" }, open: true, items: [
    { k: "kSig", l: { ro: "k_sig față de I_C propriu (51N)", en: "k_sig over own I_C (51N)" }, u: "–", step: 0.05 },
    { k: "kSens", l: { ro: "k_sens", en: "k_sens" }, u: "–", step: 0.1 },
    { k: "RfT", l: { ro: "R_f țintă", en: "Target R_f" }, u: "Ω", step: 50 },
    { k: "Imin", l: { ro: "Cel mai mic curent rezidual măsurat sigur", en: "Smallest reliably measured residual current" }, u: "A", step: 0.5 },
  ] }, { g: { ro: "Tensiune și timp", en: "Voltage and time" }, open: true, items: [
    { k: "uUnb", l: { ro: "Deplasarea neutrului în regim normal", en: "Healthy-state neutral displacement" }, u: "–", step: 0.005 },
    { k: "kU", l: { ro: "Marja pragului U₀>", en: "U₀> margin" }, u: "–", step: 0.1 },
    { k: "tF", l: { ro: "Temporizarea plecărilor", en: "Feeder delay" }, u: "s", step: 0.05 },
    { k: "cti", l: { ro: "Marja de coordonare Δt", en: "Coordination margin Δt" }, u: "s", step: 0.05 },
  ] }];
  document.getElementById("rg-inputs").innerHTML = `<div class="panel" id="rg-a"></div><div class="panel" id="rg-b"></div>`;
  PR.controls(document.getElementById("rg-a"), [RGS[0]], RG, () => render());
  PR.controls(document.getElementById("rg-b"), [RGS[1]], RG, () => render());
  buildButtons(); syncMethods(); visKnobs();
  render();
  PR.onLang(render);
  PR.math();
  PR.tabs(["lab", "reglaje", "teorie", "test"], "lab");
  PR.quiz(document.getElementById("qlist"), document.getElementById("score"), document.getElementById("q-reset"), { mcq: MCQ, num: NUM, pick: 8 });
})();
