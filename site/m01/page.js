/* Modulul 01 — interfața paginii (laborator, reglaje, test). Calculele sunt în engine.js. */
(function () {
  "use strict";
  const M = window.M01, X = window.CX, PR = window.PR;
  const { abs, argDeg } = X;
  const bi = PR.bi, t = PR.t;

  const lineVals = (k) => { const l = M.LINES[k]; return { R1: l.R1, X1: l.X1, R0: l.R0, X0: l.X0 }; };
  const P = { ...M.DEFAULTS };
  const UI = { type: "1F", kase: "max" };

  const FT = {
    "3F": { ro: "trifazat", en: "three-phase" },
    "2F": { ro: "bifazat L2–L3", en: "phase-to-phase L2–L3" },
    "1F": { ro: "monofazat L1–pământ", en: "single-phase L1–earth" },
    "2FE": { ro: "bifazat cu pământ L2–L3–E", en: "two-phase-to-earth L2–L3–E" },
  };
  const NEU = {
    R: { ro: "rezistor", en: "resistor" },
    L: { ro: "bobină de stingere", en: "arc suppression coil" },
    I: { ro: "izolat", en: "isolated" },
    S: { ro: "legat direct prin BPN", en: "solidly earthed via earthing transformer" },
  };

  /* ---------- formatări ---------- */
  const fI = (I) => (I >= 10000 ? `${PR.fmt(I / 1000, 2)} kA` : I >= 100 ? `${PR.fmt(I, 0)} A` : `${PR.fmt(I, 1)} A`);
  const fz = (z, d = 3) => `${PR.fmt(z.re, d)} ${z.im < 0 ? "−" : "+"} j${PR.fmt(Math.abs(z.im), d)} Ω`;
  const fph = (z, u = "A", s = 4) => (abs(z) < 1e-6 ? `0 ${u}` : `${PR.sig(abs(z), s)} ${u} ∠ ${PR.fmt(argDeg(z), 1)}°`);

  /* ---------- scenarii ---------- */
  const PRESETS = [
    [{ ro: "Rețeaua-exemplu (rezistor 300 A)", en: "Example network (300 A resistor)" }, () => { UI.type = "1F"; UI.kase = "max"; return { ...M.DEFAULTS }; }],
    [{ ro: "Bobină de stingere, I_C = 60 A", en: "Arc suppression coil, I_C = 60 A" }, (p) => { UI.type = "1F"; return { ...p, neutral: "L", Rf: 0 }; }],
    [{ ro: "Neutru izolat", en: "Isolated neutral" }, (p) => { UI.type = "1F"; return { ...p, neutral: "I", Rf: 0 }; }],
    [{ ro: "Plecare în cablu, 8 km", en: "Cable feeder, 8 km" }, (p) => ({ ...p, line: "cab185", ...lineVals("cab185"), L: 8, x: 8 })],
    [{ ro: "Bifazat la capăt, regim minim", en: "Phase-to-phase at the end, minimum case" }, (p) => { UI.type = "2F"; UI.kase = "min"; return { ...p, x: p.L }; }],
    [{ ro: "Monofazat prin R_f = 25 Ω", en: "Single-phase through R_f = 25 Ω" }, (p) => { UI.type = "1F"; return { ...p, Rf: 25 }; }],
  ];

  /* ---------- controale ---------- */
  const LINESEL = Object.entries(M.LINES).map(([k, v]) => [k, { ro: v.ro, en: v.en }]);
  const SCHEMA = [
    { g: { ro: "Rețeaua de 110 kV", en: "110 kV grid" }, col: "--c1", items: [
      { k: "SkQmax", l: { ro: "S″kQ maxim", en: "S″kQ maximum" }, u: "MVA", step: 100, range: [500, 8000] },
      { k: "SkQmin", l: { ro: "S″kQ minim", en: "S″kQ minimum" }, u: "MVA", step: 100, range: [300, 6000] },
      { k: "rxQ", l: { ro: "R_Q/X_Q", en: "R_Q/X_Q" }, u: "–", step: 0.05 },
    ] },
    { g: { ro: "Transformatorul T1 (YNd11)", en: "Transformer T1 (YNd11)" }, col: "--c6", items: [
      { k: "Sr", l: { ro: "Puterea nominală S_rT", en: "Rated power S_rT" }, u: "MVA", step: 1 },
      { k: "uk", l: { ro: "Tensiunea de scurtcircuit u_k", en: "Short-circuit voltage u_k" }, u: "%", step: 0.5, range: [6, 20] },
      { k: "Pk", l: { ro: "Pierderile în cupru P_k", en: "Load losses P_k" }, u: "kW", step: 1 },
      { k: "UrHV", l: { ro: "U_r pe ÎT", en: "U_r HV side" }, u: "kV", step: 1 },
      { k: "UrLV", l: { ro: "U_r pe MT", en: "U_r MV side" }, u: "kV", step: 0.5 },
    ] },
    { g: { ro: "Neutrul rețelei de 20 kV", en: "20 kV neutral earthing" }, col: "--seq0", open: true, openNarrow: false, items: [
      { k: "neutral", l: { ro: "Tratarea neutrului", en: "Neutral earthing" }, sel: Object.entries(NEU), wide: true },
      { k: "Ilim", l: { ro: "Curentul limitat de rezistor", en: "Resistor current limit" }, u: "A", step: 50, range: [100, 1000] },
      { k: "Ic", l: { ro: "Curentul capacitiv al rețelei I_C", en: "Network capacitive current I_C" }, u: "A", step: 5, range: [0, 300] },
      { k: "v", l: { ro: "Gradul de dezacord v", en: "Detuning v" }, u: "–", step: 0.01, range: [-0.2, 0.3] },
      { k: "d", l: { ro: "Componenta activă d", en: "Damping d" }, u: "–", step: 0.01 },
      { k: "Z0bpn", l: { ro: "Reactanța homopolară BPN", en: "Earthing transformer X0" }, u: "Ω", step: 1 },
    ] },
    { g: { ro: "Linia (plecarea F1)", en: "Line (feeder F1)" }, col: "--c3", open: true, openNarrow: false, items: [
      { k: "line", l: { ro: "Tipul liniei", en: "Line type" }, sel: LINESEL, wide: true },
      { k: "L", l: { ro: "Lungimea", en: "Length" }, u: "km", step: 1, range: [1, 50] },
      { k: "R1", l: "R₁", u: "Ω/km", step: 0.001 },
      { k: "X1", l: "X₁", u: "Ω/km", step: 0.001 },
      { k: "R0", l: "R₀", u: "Ω/km", step: 0.001 },
      { k: "X0", l: "X₀", u: "Ω/km", step: 0.001 },
      { k: "thetaE", l: { ro: "θ_e (regim minim)", en: "θ_e (minimum case)" }, u: "°C", step: 5 },
    ] },
  ];
  const FSCHEMA = [{ g: { ro: "Locul și rezistența defectului", en: "Fault location and resistance" }, open: true, items: [
    { k: "x", l: { ro: "Distanța de la bare", en: "Distance from busbar" }, u: "km", step: 0.1, range: [0, 20] },
    { k: "Rf", l: { ro: "Rezistența de defect R_f", en: "Fault resistance R_f" }, u: "Ω", step: 1, range: [0, 100] },
  ] }];

  let ctl, fctl;
  function onChange(k) {
    if (k === "line") Object.assign(P, lineVals(P.line));
    if (k === "L" || k === "line") { if (P.x > P.L) P.x = P.L; }
    const r = document.getElementById("in-x-r"); if (r) r.max = P.L;
    ctl.sync(); fctl.sync(); visKnobs(); render();
  }
  function visKnobs() {
    const show = (k, on) => { const el = document.getElementById("in-" + k); if (el) el.closest(".knob").hidden = !on; };
    show("Ilim", P.neutral === "R"); show("v", P.neutral === "L"); show("d", P.neutral === "L"); show("Z0bpn", P.neutral !== "I");
  }
  function buildButtons() {
    const ft = document.getElementById("ftype");
    ft.innerHTML = M.FAULTS.map((f) => `<button class="btn" data-f="${f}" aria-pressed="${UI.type === f}">${f === "2FE" ? "2F-E" : f}</button>`).join("");
    ft.onclick = (e) => { const b = e.target.closest("[data-f]"); if (!b) return; UI.type = b.dataset.f; syncButtons(); render(); };
    const fc = document.getElementById("fcase");
    fc.innerHTML = `<button class="btn" data-c="max">${bi("Regim maxim", "Maximum case")}</button><button class="btn" data-c="min">${bi("Regim minim", "Minimum case")}</button>`;
    fc.onclick = (e) => { const b = e.target.closest("[data-c]"); if (!b) return; UI.kase = b.dataset.c; syncButtons(); render(); };
    const pr = document.getElementById("presets");
    pr.innerHTML = PRESETS.map((x, i) => `<button class="btn" data-i="${i}">${bi(x[0])}</button>`).join("");
    pr.onclick = (e) => { const b = e.target.closest("[data-i]"); if (!b) return; Object.assign(P, PRESETS[+b.dataset.i][1](P)); onChange("preset"); syncButtons(); };
  }
  function syncButtons() {
    document.querySelectorAll("#ftype [data-f]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.f === UI.type));
    document.querySelectorAll("#fcase [data-c]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.c === UI.kase));
  }

  /* ---------- randare laborator ---------- */
  const HEALTHY = { "3F": [], "2F": [0], "1F": [1, 2], "2FE": [0] };
  function render() {
    const r = M.compute(P, UI.kase, UI.type, P.x, P.Rf);
    const ro = M.compute(P, UI.kase === "max" ? "min" : "max", UI.type, P.x, P.Rf);
    const earth = UI.type === "1F";
    const outOfScope = earth && (P.neutral === "I" || P.neutral === "L");
    // stare
    let msgRo = `Defect ${FT[UI.type].ro} la ${PR.fmt(P.x, 1)} km, regim ${UI.kase === "max" ? "maxim" : "minim"}: <b class="mono">${fI(r.Ik)}</b>.`;
    let msgEn = `${FT[UI.type].en[0].toUpperCase() + FT[UI.type].en.slice(1)} fault at ${PR.fmt(P.x, 1)} km, ${UI.kase === "max" ? "maximum" : "minimum"} case: <b class="mono">${fI(r.Ik)}</b>.`;
    if (earth && P.neutral === "R") { msgRo += ` Curentul e limitat de rezistorul de neutru (${PR.fmt(P.Ilim, 0)} A la defect franc pe bare).`; msgEn += ` The current is limited by the neutral resistor (${PR.fmt(P.Ilim, 0)} A for a bolted busbar fault).`; }
    if (outOfScope) { msgRo += " Punere la pământ într-o rețea cu neutru " + (P.neutral === "I" ? "izolat" : "compensat") + ": curentul vine din capacitățile rețelei și nu intră sub IEC 60909-0."; msgEn += " Earth fault in a network with " + (P.neutral === "I" ? "isolated" : "resonance-earthed") + " neutral: the current comes from the network capacitances and is outside IEC 60909-0."; }
    document.getElementById("status").innerHTML = `<div class="status ${outOfScope ? "warn" : "info"}"><span class="led"></span><span class="pill">${UI.type === "2FE" ? "2F-E" : UI.type}</span><span class="msg">${bi(msgRo, msgEn)}</span></div>`;
    // KPI
    const hp = HEALTHY[UI.type];
    const vmax = hp.length ? Math.max(...hp.map((i) => r.vpu[i])) : null;
    const kp = [
      [bi(`I″k regim ${UI.kase === "max" ? "maxim" : "minim"}`, `I″k ${UI.kase === "max" ? "maximum" : "minimum"} case`), fI(r.Ik)],
      [bi(`I″k regim ${UI.kase === "max" ? "minim" : "maxim"}`, `I″k ${UI.kase === "max" ? "minimum" : "maximum"} case`), fI(ro.Ik)],
      [bi("Curentul rezidual 3I₀", "Residual current 3I₀"), fI(r.I3I0)],
      [bi("Tensiunea fazei sănătoase", "Healthy-phase voltage"), vmax == null ? "—" : `${PR.fmt(vmax, 2)} <small>${t("u.r.", "p.u.")}</small>`],
    ];
    document.getElementById("kpis").innerHTML = kp.map(([l, v]) => `<div><div class="label">${l}</div><div class="v">${v}</div></div>`).join("");
    drawSLD(r); drawSeq(r); drawPhasors(r); drawProfile(); drawSteps(r);
  }

  /* schema monofilară */
  function drawSLD(r) {
    const x0 = 250, x1 = 730, xf = x0 + ((x1 - x0) * P.x) / P.L, y = 70;
    let s = `<circle cx="40" cy="${y}" r="18" fill="var(--surface)" stroke="var(--ink)" stroke-width="1.5"/><path d="M30 ${y} q5 -8 10 0 t10 0" fill="none" stroke="var(--ink)" stroke-width="1.5"/>
      <text x="40" y="${y - 28}" class="lbl" text-anchor="middle">110 kV</text>
      <text x="40" y="${y + 36}" class="tick" text-anchor="middle">${PR.fmt(UI.kase === "max" ? P.SkQmax : P.SkQmin, 0)} MVA</text>
      <line x1="58" y1="${y}" x2="96" y2="${y}" stroke="var(--ink)" stroke-width="1.5"/>
      <circle cx="110" cy="${y}" r="15" fill="none" stroke="var(--ink)" stroke-width="1.5"/><circle cx="130" cy="${y}" r="15" fill="none" stroke="var(--ink)" stroke-width="1.5"/>
      <text x="120" y="${y - 24}" class="lbl" text-anchor="middle">T1</text><text x="120" y="${y + 32}" class="tick" text-anchor="middle">${PR.fmt(P.Sr, 0)} MVA · YNd11</text>
      <text x="77" y="${y - 8}" class="tick" text-anchor="middle" fill="var(--c2)">${fI(Math.max(...r.IhvMag))}</text>
      <line x1="145" y1="${y}" x2="180" y2="${y}" stroke="var(--ink)" stroke-width="1.5"/>
      <line x1="180" y1="30" x2="180" y2="112" stroke="var(--ink)" stroke-width="5"/>
      <text x="188" y="32" class="lbl">20 kV</text>
      <line x1="180" y1="${y}" x2="${x1}" y2="${y}" stroke="var(--c3)" stroke-width="2.5"/>
      <rect x="198" y="${y - 7}" width="14" height="14" fill="var(--surface)" stroke="var(--ink)" stroke-width="1.5"/>
      <circle cx="226" cy="${y}" r="6" fill="none" stroke="var(--ink)" stroke-width="1.5"/>
      <text x="226" y="${y - 14}" class="tick" text-anchor="middle">TC</text>`;
    // BPN + element de neutru
    const nx = 180, ny = 112;
    if (P.neutral !== "I") {
      s += `<line x1="${nx}" y1="${ny}" x2="${nx}" y2="${ny + 8}" stroke="var(--ink)" stroke-width="1.5"/>
        <rect x="${nx - 13}" y="${ny + 8}" width="26" height="20" fill="var(--surface)" stroke="var(--ink)" stroke-width="1.5"/><path d="M${nx - 8} ${ny + 13} l8 5 -8 5 M${nx} ${ny + 13} l8 5 -8 5" stroke="var(--ink)" fill="none"/>
        <text x="${nx + 18}" y="${ny + 22}" class="tick">BPN</text>
        <line x1="${nx}" y1="${ny + 28}" x2="${nx}" y2="${ny + 36}" stroke="var(--ink)" stroke-width="1.5"/>`;
      if (P.neutral === "R") s += `<rect x="${nx - 6}" y="${ny + 36}" width="12" height="24" fill="var(--surface)" stroke="var(--seq0)" stroke-width="2"/><text x="${nx + 12}" y="${ny + 52}" class="tick">R_N = ${PR.fmt(r.zb.RN, 1)} Ω</text>`;
      else if (P.neutral === "L") s += `<path d="M${nx} ${ny + 36} c8 0 8 6 0 6 c8 0 8 6 0 6 c8 0 8 6 0 6 c8 0 8 6 0 6" fill="none" stroke="var(--seq0)" stroke-width="2"/><text x="${nx + 12}" y="${ny + 52}" class="tick">I_L = ${PR.fmt(r.zb.IL, 0)} A</text>`;
      else s += `<line x1="${nx}" y1="${ny + 36}" x2="${nx}" y2="${ny + 60}" stroke="var(--ink)" stroke-width="1.5"/>`;
      s += `<line x1="${nx}" y1="${ny + 60}" x2="${nx}" y2="${ny + 66}" stroke="var(--ink)" stroke-width="1.5"/><path d="M${nx - 10} ${ny + 66} h20 M${nx - 6} ${ny + 70} h12 M${nx - 2} ${ny + 74} h4" stroke="var(--ink)"/>`;
    } else {
      s += `<text x="${nx + 10}" y="${ny + 22}" class="tick">${t("neutru izolat", "isolated neutral")}</text>`;
    }
    if (P.Ic > 0) s += `<text x="${nx + 10}" y="${ny + 88}" class="tick">I_C = ${PR.fmt(P.Ic, 0)} A</text>`;
    // scară km
    const ticks = PR.niceTicks(0, P.L, 6);
    ticks.forEach((k) => { const xx = x0 + ((x1 - x0) * k) / P.L; s += `<line x1="${xx}" y1="${y + 4}" x2="${xx}" y2="${y + 9}" stroke="var(--muted)"/><text x="${xx}" y="${y + 22}" class="tick" text-anchor="middle">${PR.fmt(k, k % 1 ? 1 : 0)}</text>`; });
    s += `<text x="${x1}" y="${y + 36}" class="tick" text-anchor="end">km</text>`;
    s += `<line x1="180" y1="${y}" x2="${x0}" y2="${y}" stroke="var(--c3)" stroke-width="2.5"/>`;
    // defect
    s += `<path d="M${xf - 6} ${y - 34} l10 12 -7 3 9 15" stroke="var(--trip)" stroke-width="2.5" fill="none"/><text x="${xf}" y="${y - 40}" class="lbl" text-anchor="middle" fill="var(--trip)">F</text>`;
    const ax0 = 240, ax1 = Math.max(ax0 + 14, xf - 14);
    if (ax1 - ax0 > 20) s += PR.arrow(ax0, y - 14, ax1, y - 14, "var(--c2)", 1.5);
    const lx = Math.min(Math.max((ax0 + ax1) / 2, 300), 640);
    s += `<text x="${lx}" y="${y - 20}" class="lbl" text-anchor="middle" fill="var(--c2)">${fI(r.Ik)}</text>`;
    s += `<text x="${x1}" y="${y + 60}" class="tick" text-anchor="end">${t(M.LINES[P.line]?.ro || "", M.LINES[P.line]?.en || "")} · ${PR.fmt(P.L, 1)} km</text>`;
    document.getElementById("sld").innerHTML = s;
  }

  /* rețelele de secvență */
  function drawSeq(r) {
    const w = 150, h = 58;
    const box = (x, y, key, name, z, I, src) => {
      const col = { 1: "var(--seq1)", 2: "var(--seq2)", 0: "var(--seq0)" }[key];
      return `<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="4" fill="var(--surface)" stroke="${col}" stroke-width="2"/>
        <text x="${x + 8}" y="${y + 16}" class="lbl" fill="${col}" font-weight="600">${name}</text>
        <text x="${x + 8}" y="${y + 33}" class="tick">Z${["₀", "₁", "₂"][key]} = ${PR.sig(abs(z), 3)} Ω</text>
        <text x="${x + 8}" y="${y + 49}" class="tick">I${["₀", "₁", "₂"][key]} = ${fI(abs(I))}</text>
        ${src ? `<circle cx="${x + w - 20}" cy="${y + h / 2}" r="11" fill="none" stroke="${col}" stroke-width="1.5"/><text x="${x + w - 20}" y="${y + h / 2 + 4}" class="tick" text-anchor="middle">E</text>` : ""}
        <circle cx="${x}" cy="${y + h / 2}" r="3" fill="var(--ink)"/><circle cx="${x + w}" cy="${y + h / 2}" r="3" fill="var(--ink)"/>
        <text x="${x - 4}" y="${y + h / 2 - 7}" class="tick" text-anchor="end">F</text><text x="${x + w + 4}" y="${y + h / 2 - 7}" class="tick">N</text>`;
    };
    const wire = (pts) => `<polyline points="${pts.map((p) => p.join(",")).join(" ")}" fill="none" stroke="var(--ink)" stroke-width="1.5"/>`;
    const res = (cx, cy, lab, vert) => vert
      ? `<rect x="${cx - 7}" y="${cy - 18}" width="14" height="36" fill="var(--surface)" stroke="var(--ink)" stroke-width="1.5"/><text x="${cx + 12}" y="${cy + 4}" class="tick">${lab}</text>`
      : `<rect x="${cx - 18}" y="${cy - 7}" width="36" height="14" fill="var(--surface)" stroke="var(--ink)" stroke-width="1.5"/><text x="${cx}" y="${cy - 12}" class="tick" text-anchor="middle">${lab}</text>`;
    const nm = { 1: t("Rețeaua directă", "Positive network"), 2: t("Rețeaua inversă", "Negative network"), 0: t("Rețeaua homopolară", "Zero network") };
    const rf = `R_f = ${PR.fmt(P.Rf, 0)} Ω`, rf3 = `3R_f = ${PR.fmt(3 * P.Rf, 0)} Ω`;
    let s = "";
    if (UI.type === "3F") {
      s += box(300, 60, 1, nm[1], r.z1, r.I1, true);
      s += wire([[300, 89], [250, 89], [250, 180], [357, 180]]) + res(375, 180, rf) + wire([[393, 180], [500, 180], [500, 89], [450, 89]]);
    } else if (UI.type === "2F") {
      s += box(300, 30, 1, nm[1], r.z1, r.I1, true) + box(300, 140, 2, nm[2], r.z2, r.I2, false);
      s += wire([[300, 59], [250, 59], [250, 96]]) + res(250, 114, rf, true) + wire([[250, 132], [250, 169], [300, 169]]);
      s += wire([[450, 59], [500, 59], [500, 169], [450, 169]]);
    } else if (UI.type === "1F") {
      s += box(40, 60, 1, nm[1], r.z1, r.I1, true) + box(305, 60, 2, nm[2], r.z2, r.I2, false) + box(570, 60, 0, nm[0], r.z0, r.I0, false);
      s += wire([[190, 89], [305, 89]]) + wire([[455, 89], [570, 89]]);
      s += wire([[720, 89], [740, 89], [740, 195], [405, 195]]) + res(387, 195, rf3) + wire([[369, 195], [18, 195], [18, 89], [40, 89]]);
    } else {
      s += box(40, 85, 1, nm[1], r.z1, r.I1, true) + box(330, 25, 2, nm[2], r.z2, r.I2, false) + box(330, 145, 0, nm[0], r.z0, r.I0, false);
      s += wire([[190, 114], [265, 114]]) + wire([[265, 54], [265, 174]]) + wire([[265, 54], [330, 54]]) + wire([[265, 174], [330, 174]]);
      s += wire([[480, 54], [600, 54], [600, 114]]) + wire([[480, 174], [512, 174]]) + res(530, 174, rf3) + wire([[548, 174], [600, 174], [600, 114]]);
      s += wire([[600, 114], [640, 114], [640, 215], [18, 215], [18, 114], [40, 114]]);
      s += `<circle cx="265" cy="114" r="3" fill="var(--ink)"/><circle cx="600" cy="114" r="3" fill="var(--ink)"/>`;
    }
    document.getElementById("seqnet").innerHTML = s;
  }

  /* fazori */
  function drawPhasors(r) {
    const cols = ["var(--L1)", "var(--L2)", "var(--L3)"], names = ["L1", "L2", "L3"];
    const panel = (cx, title, vecs, unitR, unitLbl, fmtv) => {
      const R = 105, cy = 160;
      let s = `<text x="${cx}" y="22" class="lbl" text-anchor="middle" font-weight="600">${title}</text>
        <line x1="${cx - R - 10}" y1="${cy}" x2="${cx + R + 10}" y2="${cy}" class="grid"/><line x1="${cx}" y1="${cy - R - 10}" x2="${cx}" y2="${cy + R + 10}" class="grid"/>`;
      const mx = Math.max(...vecs.map(abs), unitR ? 1 : 0, 1e-9);
      const k = R / mx;
      if (unitR) s += `<circle cx="${cx}" cy="${cy}" r="${k}" fill="none" stroke="var(--muted)" stroke-dasharray="3 4"/><text x="${cx + k * 0.72 + 4}" y="${cy - k * 0.72 - 4}" class="tick">${unitLbl}</text>`;
      vecs.forEach((v, i) => {
        if (abs(v) * k < 2) return;
        const x1 = cx + v.re * k, y1 = cy - v.im * k;
        s += PR.arrow(cx, cy, x1, y1, cols[i], 2.2);
        const ang = Math.atan2(-v.im, v.re), lx = x1 + Math.cos(ang) * 14, ly = y1 + Math.sin(ang) * 14;
        s += `<text x="${lx}" y="${ly + 4}" class="tick" text-anchor="${Math.cos(ang) > 0.3 ? "start" : Math.cos(ang) < -0.3 ? "end" : "middle"}" fill="${cols[i]}" font-weight="600">${names[i]}</text>`;
      });
      // valori
      s += `<text x="${cx}" y="${cy + R + 30}" class="tick" text-anchor="middle">${vecs.map((v, i) => `${names[i]} ${fmtv(v)}`).join("   ")}</text>`;
      return s;
    };
    const E = abs(r.E);
    const vpu = r.Vabc.map((v) => X.scale(v, 1 / E));
    let s = panel(190, t("Curenții de defect", "Fault currents"), r.Iabc, false, "", (v) => fI(abs(v)));
    s += panel(570, t("Tensiunile la locul defectului", "Voltages at the fault"), vpu, true, "1", (v) => PR.fmt(abs(v), 2));
    document.getElementById("phasors").innerHTML = s;
  }

  /* profil de-a lungul liniei */
  function drawProfile() {
    const pr = M.profile(P, 80);
    const L = 80, R = 740, T = 18, B = 240;
    const series = [
      ["Ik3max", "var(--c1)", { ro: "3F, regim maxim", en: "3F, maximum case" }, ""],
      ["Ik2min", "var(--c3)", { ro: "2F, regim minim", en: "2F, minimum case" }, ""],
      ["Ik1max", "var(--c4)", { ro: "1F, regim maxim", en: "1F, maximum case" }, ""],
      ["Ik1min", "var(--c5)", { ro: `1F, regim minim, R_f = ${PR.fmt(P.Rf, 0)} Ω`, en: `1F, minimum case, R_f = ${PR.fmt(P.Rf, 0)} Ω` }, "5 4"],
    ];
    const vals = pr.flatMap((p) => series.map((sr) => p[sr[0]])).filter((v) => v > 0);
    const lo = Math.pow(10, Math.floor(Math.log10(Math.min(...vals)))), hi = Math.pow(10, Math.ceil(Math.log10(Math.max(...vals))));
    const xs = (x) => L + ((R - L) * x) / P.L, ys = (v) => B - ((B - T) * (Math.log10(v) - Math.log10(lo))) / (Math.log10(hi) - Math.log10(lo));
    let s = "";
    for (let e = Math.log10(lo); e <= Math.log10(hi); e++) {
      [1, 2, 5].forEach((m) => {
        const v = m * Math.pow(10, e); if (v < lo || v > hi) return;
        s += `<line x1="${L}" x2="${R}" y1="${ys(v)}" y2="${ys(v)}" class="${m === 1 ? "grid" : "minor"}"/><text x="${L - 6}" y="${ys(v) + 4}" class="tick" text-anchor="end">${v >= 1000 ? PR.fmt(v / 1000, 0) + " k" : PR.fmt(v, 0)}</text>`;
      });
    }
    PR.niceTicks(0, P.L, 8).forEach((k) => { s += `<line x1="${xs(k)}" x2="${xs(k)}" y1="${T}" y2="${B}" class="minor"/><text x="${xs(k)}" y="${B + 16}" class="tick" text-anchor="middle">${PR.fmt(k, k % 1 ? 1 : 0)}</text>`; });
    s += `<line x1="${L}" x2="${R}" y1="${B}" y2="${B}" class="ax"/><line x1="${L}" x2="${L}" y1="${T}" y2="${B}" class="ax"/>`;
    s += `<text x="${R}" y="${B + 30}" class="tick" text-anchor="end">${t("distanța de la bare, km", "distance from busbar, km")}</text><text x="${L - 40}" y="${(T + B) / 2}" class="tick" text-anchor="middle" transform="rotate(-90 ${L - 40} ${(T + B) / 2})">${t("curent, A", "current, A")}</text>`;
    series.forEach(([k, col, , dash]) => { s += `<polyline points="${pr.map((p) => `${xs(p.x).toFixed(1)},${ys(Math.max(p[k], lo)).toFixed(1)}`).join(" ")}" fill="none" stroke="${col}" stroke-width="2" ${dash ? `stroke-dasharray="${dash}"` : ""}/>`; });
    s += `<line x1="${xs(P.x)}" x2="${xs(P.x)}" y1="${T}" y2="${B}" stroke="var(--trip)" stroke-dasharray="4 3"/><text x="${xs(P.x)}" y="${T + 10}" class="tick" fill="var(--trip)" text-anchor="${P.x > P.L * 0.85 ? "end" : "start"}" dx="${P.x > P.L * 0.85 ? -4 : 4}">F</text>`;
    let lx = L;
    series.forEach(([, col, lab, dash]) => { const txt = t(lab); s += `<line x1="${lx}" x2="${lx + 18}" y1="${B + 46}" y2="${B + 46}" stroke="${col}" stroke-width="2.5" ${dash ? `stroke-dasharray="${dash}"` : ""}/><text x="${lx + 22}" y="${B + 50}" class="tick">${txt}</text>`; lx += 30 + txt.length * 6.4; });
    document.getElementById("profile").innerHTML = s;
  }

  /* calcul pas cu pas */
  function drawSteps(r) {
    const s = r.src, zb = r.zb;
    const H = (ro, en) => `<tr class="head"><td colspan="3">${bi(ro, en)}</td></tr>`;
    const R = (lab, eq, val) => `<tr><td>${typeof lab === "string" ? lab : bi(lab)}</td><td class="eq">${eq}</td><td class="n">${val}</td></tr>`;
    let h = `<tr><th>${bi("Mărime", "Quantity")}</th><th>${bi("Relația", "Relation")}</th><th class="n">${bi("Valoare", "Value")}</th></tr>`;
    h += H("Rețeaua de 110 kV", "110 kV grid");
    h += R({ ro: "Impedanța rețelei", en: "Grid impedance" }, `(6) c·U²_nQ/S″_kQ, c = ${PR.fmt(s.c, 2)}`, `${PR.fmt(s.ZQ, 3)} Ω`);
    h += R({ ro: "Raportată la 20 kV", en: "Referred to 20 kV" }, `(6) Z_Q/t_r², t_r = ${PR.fmt(s.tr, 3)}`, fz(s.zQt, 4));
    h += H("Transformatorul T1", "Transformer T1");
    h += R({ ro: "Impedanța, rezistența, reactanța", en: "Impedance, resistance, reactance" }, "(7)", `${PR.fmt(s.ZT, 3)} / ${PR.fmt(s.RT, 4)} / ${PR.fmt(s.XT, 3)} Ω`);
    h += R({ ro: "Factorul de corecție", en: "Correction factor" }, UI.kase === "max" ? `(8) x_T = ${PR.fmt(s.xT, 4)}` : t("(8) regim minim: nu se aplică", "(8) minimum case: not applied"), `K_T = ${PR.fmt(s.KT, 5)}`);
    h += R({ ro: "Impedanța directă la bare", en: "Positive-sequence at busbar" }, "Z_Qt + K_T·Z_T", fz(s.z1bus, 4));
    h += H("Neutrul de 20 kV", "20 kV neutral");
    if (P.neutral === "R") h += R({ ro: "Rezistorul de neutru", en: "Neutral resistor" }, "R_N = U_f/I_lim", `${PR.fmt(zb.RN, 2)} Ω`);
    if (P.neutral === "L") h += R({ ro: "Bobina de stingere", en: "Suppression coil" }, "I_L = I_C(1+v), X_N = U_f/I_L", `${PR.fmt(zb.IL, 1)} A, ${PR.fmt(zb.XN, 1)} Ω`);
    if (P.Ic > 0) h += R({ ro: "Capacitatea homopolară", en: "Zero-sequence capacitance" }, "(13) C₀ = I_C/(3ωU_f)", `${PR.fmt(zb.C0uF, 3)} µF`);
    h += R({ ro: "Impedanța homopolară la bare", en: "Zero-sequence at busbar" }, "(13) Z_0N ∥ 1/(jωC₀)", fz(zb.z0bus, 2));
    h += H(`Linia până la defect (${PR.fmt(P.x, 1)} km)`, `Line up to the fault (${PR.fmt(P.x, 1)} km)`);
    h += R({ ro: "Corecția de temperatură", en: "Temperature correction" }, UI.kase === "min" ? `(9) θ_e = ${PR.fmt(P.thetaE, 0)} °C` : t("regim maxim: 20 °C", "maximum case: 20 °C"), PR.fmt(r.kth, 3));
    h += R({ ro: "Secvența directă", en: "Positive sequence" }, "(R₁·k_θ + jX₁)·x", fz(r.z1L, 3));
    h += R({ ro: "Secvența zero", en: "Zero sequence" }, "(R₀·k_θ + jX₀)·x", fz(r.z0L, 3));
    h += H("La locul defectului", "At the fault");
    h += R("Z₁ = Z₂", "", fz(r.z1, 3));
    h += R("Z₀", "", fz(r.z0, 2));
    h += R({ ro: "Sursa echivalentă", en: "Equivalent source" }, "E = c·U_n/√3", `${PR.fmt(abs(r.E), 1)} V`);
    const eqn = { "3F": "(2)", "2F": "(3)", "1F": "(4)", "2FE": "(5)" }[UI.type];
    h += R({ ro: "Componentele simetrice", en: "Symmetrical components" }, `${eqn} I₁ / I₂ / I₀`, `${fph(r.I1)}<br>${fph(r.I2)}<br>${fph(r.I0)}`);
    h += R({ ro: "Curenții pe faze", en: "Phase currents" }, "(1) L1 / L2 / L3", r.Iabc.map((z) => fph(z)).join("<br>"));
    h += `<tr class="res"><td>${bi("Curentul de defect", "Fault current")}</td><td class="eq">${UI.type === "2FE" ? "3|I₀|" : UI.type === "1F" ? "3|I₀| = |I_L1|" : UI.type === "2F" ? "|I_L2|" : "|I_L1|"}</td><td class="n">${fI(r.Ik)}</td></tr>`;
    h += R({ ro: "Tensiunile pe faze", en: "Phase voltages" }, "U/E, L1 / L2 / L3", r.vpu.map((v) => PR.fmt(v, 3)).join(" / ") + ` ${t("u.r.", "p.u.")}`);
    if (UI.type === "3F") { const k = M.kappa(r.z1); h += R({ ro: "Curentul de șoc", en: "Peak current" }, `(10) κ = ${PR.fmt(k, 3)}`, `i_p = ${fI(k * Math.SQRT2 * r.Ik)}`); }
    h += H("Pe partea de 110 kV a lui T1", "On the 110 kV side of T1");
    h += R({ ro: "Curenții pe faze", en: "Phase currents" }, "(14) L1 / L2 / L3", r.IhvMag.map((v) => fI(v)).join(" / "));
    document.getElementById("steps").innerHTML = h;
  }

  /* ---------- reglaje ---------- */
  function renderSheet() {
    const tb = M.settingsTable(P), hvx = M.hvBus(P, "max"), hvn = M.hvBus(P, "min");
    document.getElementById("sheet-meta").innerHTML = bi(
      `T1 ${PR.fmt(P.Sr, 0)} MVA ${PR.fmt(P.UrHV, 0)}/${PR.fmt(P.UrLV, 0)} kV, u_k ${PR.fmt(P.uk, 1)} % · S″kQ ${PR.fmt(P.SkQmax, 0)}/${PR.fmt(P.SkQmin, 0)} MVA · neutru: ${t(NEU[P.neutral].ro)}${P.neutral === "R" ? ` ${PR.fmt(P.Ilim, 0)} A` : ""} · ${M.LINES[P.line]?.ro || ""}, ${PR.fmt(P.L, 1)} km`,
      `T1 ${PR.fmt(P.Sr, 0)} MVA ${PR.fmt(P.UrHV, 0)}/${PR.fmt(P.UrLV, 0)} kV, u_k ${PR.fmt(P.uk, 1)} % · S″kQ ${PR.fmt(P.SkQmax, 0)}/${PR.fmt(P.SkQmin, 0)} MVA · neutral: ${NEU[P.neutral].en}${P.neutral === "R" ? ` ${PR.fmt(P.Ilim, 0)} A` : ""} · ${M.LINES[P.line]?.en || ""}, ${PR.fmt(P.L, 1)} km`);
    const smax = M.source(P, "max"), smin = M.source(P, "min");
    document.getElementById("calc-max").innerHTML = `c = ${PR.fmt(P.cmax, 2)}   S″kQ = ${PR.fmt(P.SkQmax, 0)} MVA   K_T = ${PR.fmt(smax.KT, 4)}   θ = 20 °C\nZ₁ ${t("la bare", "at busbar")} = ${fz(smax.z1bus, 4)}   →   I″k3 = ${fI(tb[0].Ik3max)}`;
    document.getElementById("calc-min").innerHTML = `c = ${PR.fmt(P.cmin, 2)}   S″kQ = ${PR.fmt(P.SkQmin, 0)} MVA   K_T = 1   θ_e = ${PR.fmt(P.thetaE, 0)} °C   R_f = ${PR.fmt(P.Rf, 0)} Ω\nZ₁ ${t("la bare", "at busbar")} = ${fz(smin.z1bus, 4)}   →   I″k2 ${t("la capătul liniei", "at line end")} = ${fI(tb[tb.length - 1].Ik2min)}`;
    const head = [t("Punct", "Point"), "x (km)", "I″k3 max", "I″k2 min", "I″k1 max", `I″k1 min (R_f ${PR.fmt(P.Rf, 0)} Ω)`, "I″kE2E max", t("ÎT: 3F max", "HV: 3F max"), t("ÎT: 2F min", "HV: 2F min")];
    const name = (x, i) => (i === 0 ? t("Bare 20 kV", "20 kV busbar") : i === tb.length - 1 ? t("Capăt linie", "Line end") : `${t("Linie", "Line")} ${Math.round((100 * x) / P.L)} %`);
    let h = `<tr>${head.map((c, i) => `<th class="${i > 0 ? "n" : ""}">${c}</th>`).join("")}</tr>`;
    h += `<tr><td>${t("Bare 110 kV", "110 kV busbar")}</td><td class="n">—</td><td class="n">${fI(hvx.Ik3 * 1000)}</td><td class="n">${fI((hvn.Ik3 * 1000 * Math.sqrt(3)) / 2)}</td><td class="n">—</td><td class="n">—</td><td class="n">—</td><td class="n">—</td><td class="n">—</td></tr>`;
    tb.forEach((r, i) => { h += `<tr><td>${name(r.x, i)}</td><td class="n">${PR.fmt(r.x, 1)}</td><td class="n">${fI(r.Ik3max)}</td><td class="n">${fI(r.Ik2min)}</td><td class="n">${fI(r.Ik1max)}</td><td class="n">${fI(r.Ik1min)}</td><td class="n">${fI(r.IkE2Emax)}</td><td class="n">${fI(r.Ihv3max)}</td><td class="n">${fI(r.Ihv2min)}</td></tr>`; });
    document.getElementById("sc-table").innerHTML = h;
    document.getElementById("tbl-cap").textContent = t("Curenți în amperi, valori inițiale simetrice I″k", "Currents in amperes, initial symmetrical I″k");
    // tabel de utilizare
    const U = [
      [{ ro: "I″k3 max la capătul liniei / barele din aval", en: "I″k3 max at line end / downstream bus" }, { ro: "treapta instantanee I>> a protecției plecării (nu trebuie să depășească zona)", en: "instantaneous stage I>> of the feeder protection (must not overreach)" }, "M03"],
      [{ ro: "I″k3 max la locul releului", en: "I″k3 max at the relay" }, { ro: "saturația TC, timpii de coordonare la curentul maxim", en: "CT saturation, coordination margins at maximum current" }, "M02, M03"],
      [{ ro: "I″k2 min la capătul zonei", en: "I″k2 min at the end of the zone" }, { ro: "sensibilitatea treptei temporizate I> (k_sens)", en: "sensitivity of the time-delayed stage I> (k_sens)" }, "M03"],
      [{ ro: "I″k1 min prin R_f", en: "I″k1 min through R_f" }, { ro: "sensibilitatea protecției homopolare I₀>", en: "sensitivity of the earth-fault stage I₀>" }, "M04, M05"],
      [{ ro: "Coloanele ÎT", en: "HV columns" }, { ro: "coordonarea protecției de pe 110 kV a transformatorului cu cea de pe 20 kV", en: "coordination of the transformer 110 kV protection with the 20 kV one" }, "M03, M10"],
      [{ ro: "I″k3 max și i_p la barele de 20 kV", en: "I″k3 max and i_p at the 20 kV busbar" }, { ro: "capacitatea de rupere a întrerupătoarelor, stabilitatea termică și dinamică", en: "breaker interrupting rating, thermal and dynamic withstand" }, "—"],
    ];
    document.getElementById("use-table").innerHTML = `<tr><th>${bi("Valoarea", "Value")}</th><th>${bi("Folosită pentru", "Used for")}</th><th>${bi("Modul", "Module")}</th></tr>` + U.map(([a, b, c]) => `<tr><td>${bi(a)}</td><td>${bi(b)}</td><td class="mono">${c}</td></tr>`).join("");
  }
  document.getElementById("copy-tbl").addEventListener("click", (e) => {
    const tb = M.settingsTable(P), hv = M.hvBus(P, "max");
    const rows = [["x_km", "Ik3_max_A", "Ik2_min_A", "Ik1_max_A", "Ik1_min_A", "IkE2E_max_A", "HV_3F_max_A", "HV_2F_min_A"]];
    rows.push(["110kV", PR.xnum(hv.Ik3 * 1000, 1), "", "", "", "", "", ""]);
    tb.forEach((r) => rows.push([PR.xnum(r.x, 2), PR.xnum(r.Ik3max, 1), PR.xnum(r.Ik2min, 1), PR.xnum(r.Ik1max, 1), PR.xnum(r.Ik1min, 1), PR.xnum(r.IkE2Emax, 1), PR.xnum(r.Ihv3max, 1), PR.xnum(r.Ihv2min, 1)]));
    PR.copyTSV(rows, e.currentTarget);
  });

  /* ---------- test ---------- */
  const MCQ = [
    { q: { ro: "Ce factor de tensiune c se folosește la 20 kV pentru curentul minim de scurtcircuit?", en: "Which voltage factor c is used at 20 kV for the minimum short-circuit current?" }, o: [{ ro: "0,95", en: "0.95" }, { ro: "1,00", en: "1.00" }, { ro: "1,05", en: "1.05" }, { ro: "1,10", en: "1.10" }], a: 1, e: { ro: "IEC 60909-0: c_min = 1,00 pentru U_n > 1 kV; c_max = 1,10.", en: "IEC 60909-0: c_min = 1.00 for U_n > 1 kV; c_max = 1.10." } },
    { q: { ro: "La ce verificare servește curentul minim de defect?", en: "What is the minimum fault current used for?" }, o: [{ ro: "Capacitatea de rupere a întrerupătorului", en: "Breaker interrupting rating" }, { ro: "Sensibilitatea protecției", en: "Protection sensitivity" }, { ro: "Reglajul treptei instantanee", en: "Instantaneous stage setting" }, { ro: "Saturația TC", en: "CT saturation" }], a: 1, e: { ro: "Protecția trebuie să acționeze sigur la cel mai mic defect din zonă: k_sens = I″k min/I_pp.", en: "The protection must operate reliably for the smallest fault in its zone: k_sens = I″k min/I_pickup." } },
    { q: { ro: "Cât este I″k2/I″k3 pentru un defect departe de generatoare (Z₂ = Z₁, R_f = 0)?", en: "What is I″k2/I″k3 for a far-from-generator fault (Z₂ = Z₁, R_f = 0)?" }, o: [{ ro: "0,5", en: "0.5" }, { ro: "√3/2 ≈ 0,866", en: "√3/2 ≈ 0.866" }, { ro: "1", en: "1" }, { ro: "2/√3 ≈ 1,155", en: "2/√3 ≈ 1.155" }], a: 1, e: { ro: "Din (2) și (3): I″k2 = cU_n/|2Z₁| = (√3/2)·cU_n/(√3|Z₁|).", en: "From (2) and (3): I″k2 = cU_n/|2Z₁| = (√3/2)·cU_n/(√3|Z₁|)." } },
    { q: { ro: "Cum se conectează rețelele de secvență la un defect monofazat?", en: "How are the sequence networks connected for a single-phase fault?" }, o: [{ ro: "Toate trei în serie", en: "All three in series" }, { ro: "Directă și inversă în paralel", en: "Positive and negative in parallel" }, { ro: "Numai rețeaua directă", en: "Positive network only" }, { ro: "Directă în serie cu (inversă ∥ zero)", en: "Positive in series with (negative ∥ zero)" }], a: 0, e: { ro: "I₀ = I₁ = I₂, deci cele trei rețele sunt parcurse de același curent, în serie cu 3R_f.", en: "I₀ = I₁ = I₂, so the three networks carry the same current, in series with 3R_f." } },
    { q: { ro: "De ce, în rețeaua tratată prin rezistor, curentul de punere la pământ variază puțin cu locul defectului?", en: "Why, in a resistor-earthed network, does the earth-fault current change little with fault location?" }, o: [{ ro: "Pentru că 3R_N domină impedanța homopolară", en: "Because 3R_N dominates the zero-sequence impedance" }, { ro: "Pentru că linia nu are impedanță homopolară", en: "Because the line has no zero-sequence impedance" }, { ro: "Pentru că rezistorul e pe 110 kV", en: "Because the resistor is on 110 kV" }, { ro: "Pentru că I_C e zero", en: "Because I_C is zero" }], a: 0, e: { ro: "Cu I_lim = 300 A la 20 kV, 3R_N ≈ 115 Ω, mult peste impedanța unei linii de câțiva kilometri.", en: "With I_lim = 300 A at 20 kV, 3R_N ≈ 115 Ω, far above the impedance of a few kilometres of line." } },
    { q: { ro: "Ce curenți vede protecția de pe 110 kV (YNd11) la un defect bifazat pe 20 kV?", en: "What does the 110 kV protection (YNd11) see for a phase-to-phase fault on 20 kV?" }, o: [{ ro: "1 : 1 : 2, faza maximă egală cu curentul trifazat raportat", en: "1 : 1 : 2, largest phase equal to the referred three-phase current" }, { ro: "1 : 1 : 0", en: "1 : 1 : 0" }, { ro: "Numai curent homopolar", en: "Zero-sequence current only" }, { ro: "Nimic", en: "Nothing" }], a: 0, e: { ro: "Relația (14): secvențele directă și inversă se rotesc în sens opus cu 30°·h și se recompun ca 1 : 1 : 2.", en: "Relation (14): positive and negative sequences rotate by ±30°·h and recombine as 1 : 1 : 2." } },
    { q: { ro: "Ce apare pe 110 kV la un defect monofazat pe 20 kV?", en: "What appears on 110 kV for a single-phase fault on 20 kV?" }, o: [{ ro: "Curenți 1 : 1 : 0, fără 3I₀", en: "Currents 1 : 1 : 0, no 3I₀" }, { ro: "Curenți 1 : 1 : 2", en: "Currents 1 : 1 : 2" }, { ro: "Același 3I₀, raportat", en: "The same 3I₀, referred" }, { ro: "Nimic", en: "Nothing" }], a: 0, e: { ro: "Triunghiul blochează secvența zero; I₁ și I₂ trec rotite și dau 1 : 1 : 0.", en: "The delta blocks zero sequence; I₁ and I₂ pass rotated and give 1 : 1 : 0." } },
    { q: { ro: "Când se aplică factorul K_T al transformatorului?", en: "When is the transformer factor K_T applied?" }, o: [{ ro: "Numai pentru curenții maximi", en: "Only for maximum currents" }, { ro: "Numai pentru curenții minimi", en: "Only for minimum currents" }, { ro: "În ambele regimuri", en: "In both cases" }, { ro: "Niciodată la transformatoarele de rețea", en: "Never for network transformers" }], a: 0, e: { ro: "IEC 60909-0:2016 §6.3.3; pandapower îl aplică la fel.", en: "IEC 60909-0:2016 §6.3.3; pandapower applies it the same way." } },
    { q: { ro: "În rețeaua cu neutru izolat, la o punere la pământ franchă, tensiunea fazelor sănătoase devine aproximativ:", en: "In an isolated-neutral network, for a bolted earth fault, the healthy-phase voltage becomes about:" }, o: [{ ro: "1 u.r.", en: "1 p.u." }, { ro: "1,25 u.r.", en: "1.25 p.u." }, { ro: "√3 ≈ 1,73 u.r.", en: "√3 ≈ 1.73 p.u." }, { ro: "2 u.r.", en: "2 p.u." }], a: 2, e: { ro: "Punctul neutru se deplasează la tensiunea fazei defecte; fazele sănătoase ajung la tensiunea de linie.", en: "The neutral point shifts to the faulted phase voltage; the healthy phases reach line voltage." } },
    { q: { ro: "Ce reprezintă I_C?", en: "What does I_C represent?" }, o: [{ ro: "Curentul capacitiv la punerea la pământ franchă într-o rețea izolată", en: "The capacitive current of a bolted earth fault in an isolated network" }, { ro: "Curentul nominal al bobinei", en: "The rated current of the coil" }, { ro: "Curentul de sarcină al plecării", en: "The feeder load current" }, { ro: "Curentul trifazat la bare", en: "The three-phase busbar current" }], a: 0, e: { ro: "I_C = 3ωC₀U_f, pentru toată rețeaua galvanic legată.", en: "I_C = 3ωC₀U_f, for the whole galvanically connected network." } },
    { q: { ro: "De ce X₀ al unei LEA de 20 kV fără conductor de protecție e de circa 4 ori X₁?", en: "Why is X₀ of a 20 kV overhead line without shield wire about 4 times X₁?" }, o: [{ ro: "Returul prin pământ se face la adâncimea echivalentă D_e, de sute de metri", en: "The earth return flows at the equivalent depth D_e, hundreds of metres down" }, { ro: "Din cauza capacității liniei", en: "Because of the line capacitance" }, { ro: "Pentru că R₀ > R₁", en: "Because R₀ > R₁" }, { ro: "Din cauza transformatorului", en: "Because of the transformer" }], a: 0, e: { ro: "Relația (12): bucla fază–pământ are aria dată de D_e ≈ 931 m (ρ = 100 Ω·m).", en: "Relation (12): the phase–earth loop area is set by D_e ≈ 931 m (ρ = 100 Ω·m)." } },
    { q: { ro: "În regimul minim, rezistența liniilor se ia:", en: "In the minimum case, line resistance is taken:" }, o: [{ ro: "La 20 °C", en: "At 20 °C" }, { ro: "La temperatura de la sfârșitul defectului θ_e, deci mai mare", en: "At the end-of-fault temperature θ_e, hence larger" }, { ro: "Egală cu zero", en: "As zero" }, { ro: "La −20 °C", en: "At −20 °C" }], a: 1, e: { ro: "Relația (9): R_L crește cu 0,4 %/°C, curentul scade, iar verificarea de sensibilitate rămâne acoperitoare.", en: "Relation (9): R_L rises by 0.4 %/°C, the current falls, and the sensitivity check stays on the safe side." } },
    { q: { ro: "IEC 60909-0 calculează punerea la pământ simplă într-o rețea cu bobină de stingere?", en: "Does IEC 60909-0 cover the single earth fault in a resonance-earthed network?" }, o: [{ ro: "Nu, e în afara domeniului standardului", en: "No, it is outside the scope of the standard" }, { ro: "Da, cu c = 1,1", en: "Yes, with c = 1.1" }, { ro: "Da, numai pentru cabluri", en: "Yes, for cables only" }, { ro: "Da, prin K_T", en: "Yes, through K_T" }], a: 0, e: { ro: "Standardul exclude punerea la pământ simplă în rețelele izolate sau compensate; dubla punere la pământ e în IEC 60909-3.", en: "The standard excludes the single earth fault in isolated or compensated networks; double earth faults are in IEC 60909-3." } },
  ];
  function NUM() {
    const Sk = PR.rnd(1000, 6000, 250), Z1r = PR.rnd(0.3, 3, 0.05), Z1x = PR.rnd(1, 8, 0.1), Il = PR.pick([300, 400, 600, 1000]), C0 = PR.rnd(0.5, 6, 0.1), I3 = PR.rnd(2, 12, 0.1);
    const Z = Math.hypot(Z1r, Z1x);
    return [
      { q: { ro: `Calculează impedanța rețelei de 110 kV pentru S″kQ = ${PR.fmt(Sk, 0)} MVA (c = 1,1).`, en: `Compute the 110 kV grid impedance for S″kQ = ${PR.fmt(Sk, 0)} MVA (c = 1.1).` }, u: "Ω", v: (1.1 * 110 * 110) / Sk, e: { ro: "Z_Q = c·U²_nQ/S″kQ, relația (6).", en: "Z_Q = c·U²_nQ/S″kQ, relation (6)." } },
      { q: { ro: `La 20 kV, Z₁ = ${PR.fmt(Z1r, 2)} + j${PR.fmt(Z1x, 1)} Ω. Cât este I″k3 maxim (c = 1,1)?`, en: `At 20 kV, Z₁ = ${PR.fmt(Z1r, 2)} + j${PR.fmt(Z1x, 1)} Ω. What is the maximum I″k3 (c = 1.1)?` }, u: "kA", v: (1.1 * 20) / (Math.sqrt(3) * Z), e: { ro: "I″k3 = c·U_n/(√3·|Z₁|), relația (2).", en: "I″k3 = c·U_n/(√3·|Z₁|), relation (2)." } },
      { q: { ro: `Curentul trifazat într-un punct e ${PR.fmt(I3, 1)} kA. Cât e curentul bifazat (Z₂ = Z₁, R_f = 0)?`, en: `The three-phase current at a point is ${PR.fmt(I3, 1)} kA. What is the phase-to-phase current (Z₂ = Z₁, R_f = 0)?` }, u: "kA", v: (I3 * Math.sqrt(3)) / 2, e: { ro: "I″k2 = (√3/2)·I″k3.", en: "I″k2 = (√3/2)·I″k3." } },
      { q: { ro: `Ce rezistență de neutru limitează punerea la pământ franchă pe barele de 20 kV la ${Il} A?`, en: `Which neutral resistance limits a bolted 20 kV busbar earth fault to ${Il} A?` }, u: "Ω", v: 20000 / Math.sqrt(3) / Il, e: { ro: "R_N = U_f/I_lim = (20 000/√3)/I_lim.", en: "R_N = U_f/I_lim = (20 000/√3)/I_lim." } },
      { q: { ro: `Rețeaua de 20 kV are C₀ = ${PR.fmt(C0, 1)} µF pe fază. Cât este curentul capacitiv de punere la pământ?`, en: `The 20 kV network has C₀ = ${PR.fmt(C0, 1)} µF per phase. What is the capacitive earth-fault current?` }, u: "A", v: 3 * 2 * Math.PI * 50 * C0 * 1e-6 * (20000 / Math.sqrt(3)), e: { ro: "I_C = 3ωC₀U_f, relația (13).", en: "I_C = 3ωC₀U_f, relation (13)." } },
    ];
  }

  /* ---------- pornire ---------- */
  ctl = PR.controls(document.getElementById("controls"), SCHEMA, P, onChange);
  fctl = PR.controls(document.getElementById("fknobs"), FSCHEMA, P, onChange);
  buildButtons(); syncButtons(); visKnobs();
  document.getElementById("in-x-r").max = P.L;
  render(); renderSheet();
  PR.onLang(() => { render(); renderSheet(); });
  document.addEventListener("tabchange", (e) => { if (e.detail === "reglaje") renderSheet(); });
  // fișa de reglaje urmează orice schimbare din laborator
  window.addEventListener("input", () => renderSheet());
  document.getElementById("presets").addEventListener("click", () => renderSheet());
  PR.math();
  PR.tabs(["lab", "reglaje", "teorie", "test"], "lab");
  PR.quiz(document.getElementById("qlist"), document.getElementById("score"), document.getElementById("q-reset"), { mcq: MCQ, num: NUM, pick: 8 });
})();
