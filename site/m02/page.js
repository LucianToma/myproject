/* Modulul 02 — interfața paginii. Calculele sunt în engine.js (M02); reglajele vin din M03, curenții din M01. */
(function () {
  "use strict";
  const M = window.M02, M3 = window.M03, PR = window.PR;
  const bi = PR.bi, t = PR.t;

  const ctxFor = (relay) => M.context({ ...M.DEFAULTS, relay });
  const P = { ...M.DEFAULTS };
  const base = ctxFor(P.relay);
  P.If = base.If; P.xr = base.xr;

  const fA = (I) => (I >= 10000 ? `${PR.fmt(I / 1000, 2)} kA` : `${PR.fmt(I, I >= 100 ? 0 : 1)} A`);
  const fms = (x) => (x == null ? "—" : !isFinite(x) ? t("niciodată", "never") : `${PR.fmt(x * 1000, 1)} ms`);
  const RELAYS = [["R3", { ro: "R3 · plecarea F1 (TC 300/1)", en: "R3 · feeder F1 (CT 300/1)" }], ["R2", { ro: "R2 · sosirea 20 kV (TC 1000/1)", en: "R2 · 20 kV incomer (CT 1000/1)" }]];

  const SCHEMA = [
    { g: { ro: "Releul și defectul", en: "Relay and fault" }, col: "--c2", open: true, openNarrow: false, items: [
      { k: "relay", l: { ro: "Releul (reglaje din M03)", en: "Relay (settings from M03)" }, sel: RELAYS, wide: true },
      { k: "If", l: { ro: "Curentul de defect I″k (primar)", en: "Fault current I″k (primary)" }, u: "A", step: 50 },
      { k: "xr", l: { ro: "Raportul X/R al buclei de defect", en: "Fault loop X/R ratio" }, u: "–", step: 1, range: [1, 60] },
      { k: "offset", l: { ro: "Asimetria (1 = maximă, 0 = simetric)", en: "Offset (1 = full, 0 = symmetrical)" }, u: "–", step: 0.1, range: [0, 1] },
      { k: "rem", l: { ro: "Remanența (fracție din fluxul limită)", en: "Remanence (fraction of limit flux)" }, u: "–", step: 0.05, range: [-0.8, 0.8] },
    ] },
    { g: { ro: "Transformatorul de curent", en: "Current transformer" }, col: "--c1", open: true, openNarrow: false, items: [
      { k: "Ipn", l: { ro: "Curentul primar nominal", en: "Rated primary current" }, u: "A", step: 50 },
      { k: "Isn", l: { ro: "Curentul secundar nominal", en: "Rated secondary current" }, sel: [["1", { ro: "1 A", en: "1 A" }], ["5", { ro: "5 A", en: "5 A" }]] },
      { k: "cls", l: { ro: "Clasa", en: "Class" }, sel: [["5P", { ro: "5P", en: "5P" }], ["10P", { ro: "10P", en: "10P" }]] },
      { k: "alf", l: "ALF", u: "–", step: 5 },
      { k: "Sn", l: { ro: "Puterea nominală S_n", en: "Rated burden S_n" }, u: "VA", step: 2.5 },
      { k: "Rct", l: { ro: "Rezistența înfășurării R_ct", en: "Winding resistance R_ct" }, u: "Ω", step: 0.1 },
    ] },
    { g: { ro: "Circuitul secundar", en: "Secondary circuit" }, col: "--c3", items: [
      { k: "lead", l: { ro: "Lungimea conductoarelor (dus)", en: "Lead length (one way)" }, u: "m", step: 10, range: [5, 400] },
      { k: "leadA", l: { ro: "Secțiunea conductoarelor", en: "Lead cross-section" }, u: "mm²", step: 0.5 },
      { k: "Srelay", l: { ro: "Consumul releului pe fază", en: "Relay burden per phase" }, u: "VA", step: 0.05 },
    ] },
  ];

  const PRESETS = [
    [{ ro: "Exemplu: 300/1 A, 5P20, 10 VA", en: "Example: 300/1 A, 5P20, 10 VA" }, () => { Object.assign(P, M.DEFAULTS); const c = ctxFor(P.relay); P.If = c.If; P.xr = c.xr; }],
    [{ ro: "Secundar 5 A, 150 m de conductor", en: "5 A secondary, 150 m of lead" }, () => Object.assign(P, { Isn: 5, Sn: 15, Rct: 0.3, lead: 150, leadA: 2.5, Srelay: 0.5 })],
    [{ ro: "Remanență 80 %", en: "80 % remanence" }, () => Object.assign(P, { rem: 0.8 })],
    [{ ro: "TC subdimensionat: 5P10, 2,5 VA, 200 m", en: "Undersized CT: 5P10, 2.5 VA, 200 m" }, () => Object.assign(P, { alf: 10, Sn: 2.5, Rct: 3, lead: 200, leadA: 1.5 })],
    [{ ro: "Celula de sosire R2", en: "Incomer R2" }, () => { const c = ctxFor("R2"); Object.assign(P, M.DEFAULTS, { relay: "R2", Ipn: 1000, Rct: 5, If: c.If, xr: c.xr }); }],
    [{ ro: "Defect simetric", en: "Symmetrical fault" }, () => Object.assign(P, { offset: 0 })],
  ];

  let ctl;
  function onChange(k) {
    if (typeof P.Isn === "string") P.Isn = +P.Isn;
    if (k === "relay") { const c = ctxFor(P.relay); P.If = c.If; P.xr = c.xr; P.Ipn = M3.DEFAULTS[P.relay].ct; }
    ctl.sync(); render();
  }
  function ctx() { const c = ctxFor(P.relay); return { ...c, If: P.If, xr: P.xr }; }

  /* ---------- randare ---------- */
  let LAST = null;
  function compute() {
    const c = ctx(), s = M.sizing(P, c), sim = M.simulate(P, c), d = M.dft(sim), mg = sim.mg;
    const n = P.Ipn / P.Isn;
    const thrH = c.Ih > 0 ? c.Ih / n : null, thrL = c.Is / n;
    const pk = { hi: thrH ? M.pickupTime(d, thrH) : null, hiId: thrH ? M.pickupTimeIdeal(d, thrH) : null, lo: M.pickupTime(d, thrL * M3.GT), loId: M.pickupTimeIdeal(d, thrL * M3.GT) };
    return (LAST = { c, s, sim, d, mg, n, thrH, thrL, pk });
  }
  M.pickupTimeIdeal = (d, thr) => { for (let k = 0; k < d.t.length; k++) if (d.Iid[k] >= thr) return d.t[k]; return null; };

  function render() {
    const { c, s, sim, d, mg, n, thrH, thrL, pk } = compute();
    const issues = [];
    if (!s.okIDMT) issues.push(bi(`F_a = ${PR.fmt(Math.min(s.Fa1, s.Fa2), 1)} < 20·I>/I_pn = ${PR.fmt(s.needIDMT, 1)}`, `F_a = ${PR.fmt(Math.min(s.Fa1, s.Fa2), 1)} < 20·I>/I_pn = ${PR.fmt(s.needIDMT, 1)}`));
    if (!s.okHigh) issues.push(bi(`treapta I>> (${PR.fmt(s.needHigh, 1)}·I_pn) e peste F_a`, `the I>> stage (${PR.fmt(s.needHigh, 1)}·I_pn) is above F_a`));
    const delay = pk.hi != null && pk.hiId != null ? pk.hi - pk.hiId : null;
    const msg = issues.length ? issues.join("; ") + "." : bi(
      `TC-ul îndeplinește cerințele releului maximal. ${isFinite(sim.tSat ?? Infinity) && sim.tSat != null ? `Se saturează după ${fms(sim.tSat)}` : "Nu se saturează în primele 200 ms"}${delay != null ? `; treapta I>> pornește cu ${PR.fmt(delay * 1000, 0)} ms mai târziu decât cu un TC ideal.` : "."}`,
      `The CT meets the overcurrent relay requirements. ${sim.tSat != null ? `It saturates after ${fms(sim.tSat)}` : "It does not saturate in the first 200 ms"}${delay != null ? `; the I>> stage picks up ${PR.fmt(delay * 1000, 0)} ms later than with an ideal CT.` : "."}`);
    document.getElementById("status").innerHTML = `<div class="status ${issues.length ? "bad" : sim.tSat != null ? "warn" : "ok"}"><span class="led"></span><span class="pill">${issues.length ? t("NECORESPUNZĂTOR", "NOT ADEQUATE") : t("CORESPUNZĂTOR", "ADEQUATE")}</span><span class="msg">${msg}</span></div>`;
    const kp = [
      [bi("F_a real (3F / nesimetric)", "Effective F_a (3F / unbal.)"), `${PR.fmt(s.Fa1, 0)} / ${PR.fmt(s.Fa2, 0)}`],
      [bi("I″k / I_pn", "I″k / I_pn"), PR.fmt(s.kF, 1)],
      [bi("t_sat formulă / simulare", "t_sat formula / simulation"), `${fms(s.ts)} <small>/ ${fms(sim.tSat)}</small>`],
      [bi("Întârzierea treptei I>>", "I>> stage delay"), delay != null ? `${PR.fmt(delay * 1000, 0)} <small>ms</small>` : "—"],
    ];
    document.getElementById("kpis").innerHTML = kp.map(([l, v]) => `<div><div class="label">${l}</div><div class="v">${v}</div></div>`).join("");
    drawWave(sim, s);
    drawMeas(d, thrH, thrL, pk);
    drawExcit(mg, s, c, n);
    drawSteps(c, s, sim, mg, pk, n);
    renderSheet();
  }

  /* axă temporală comună */
  function axes(L, R, T, B, tmax, ymin, ymax, ylab) {
    const xs = (tt) => L + ((R - L) * tt) / tmax, ys = (v) => B - ((B - T) * (v - ymin)) / (ymax - ymin);
    let s = "";
    PR.niceTicks(ymin, ymax, 6).forEach((v) => { s += `<line x1="${L}" x2="${R}" y1="${ys(v)}" y2="${ys(v)}" class="${v === 0 ? "ax" : "grid"}"/><text x="${L - 6}" y="${ys(v) + 4}" class="tick" text-anchor="end">${PR.fmt(v, Math.abs(v) < 10 && v % 1 ? 1 : 0)}</text>`; });
    for (let tt = 0; tt <= tmax + 1e-9; tt += 0.02) s += `<line x1="${xs(tt)}" x2="${xs(tt)}" y1="${T}" y2="${B}" class="minor"/><text x="${xs(tt)}" y="${B + 16}" class="tick" text-anchor="middle">${PR.fmt(tt * 1000, 0)}</text>`;
    s += `<text x="${R}" y="${B + 30}" class="tick" text-anchor="end">t, ms</text><text x="${L - 44}" y="${(T + B) / 2}" class="tick" text-anchor="middle" transform="rotate(-90 ${L - 44} ${(T + B) / 2})">${ylab}</text>`;
    return { xs, ys, s };
  }
  const poly = (xs, ys, tt, v, col, w, dash, every = 1) => { let pts = ""; for (let k = 0; k < tt.length; k += every) pts += `${xs(tt[k]).toFixed(1)},${ys(v[k]).toFixed(1)} `; return `<polyline points="${pts}" fill="none" stroke="${col}" stroke-width="${w}" ${dash ? `stroke-dasharray="${dash}"` : ""}/>`; };

  function drawWave(sim, s) {
    const tmax = 0.2, L = 66, R = 744, T = 14, B = 240;
    const all = sim.i1.concat(sim.i2);
    const ymax = Math.max(...all) * 1.08, ymin = Math.min(0, Math.min(...all) * 1.08);
    const A = axes(L, R, T, B, tmax, ymin, ymax, t("curent secundar, A", "secondary current, A"));
    let g = A.s;
    g += poly(A.xs, A.ys, sim.t, sim.i1, "var(--muted)", 1.6, "5 4", 2);
    g += poly(A.xs, A.ys, sim.t, sim.im, "var(--trip)", 1.2, "", 2);
    g += poly(A.xs, A.ys, sim.t, sim.i2, "var(--accent)", 2, "", 2);
    if (sim.tSat != null) g += `<line x1="${A.xs(sim.tSat)}" x2="${A.xs(sim.tSat)}" y1="${T}" y2="${B}" stroke="var(--start)" stroke-dasharray="3 3"/><text x="${A.xs(sim.tSat) + 4}" y="${T + 12}" class="tick" fill="var(--start)">${t("saturație", "saturation")} ${fms(sim.tSat)}</text>`;
    const leg = [["var(--muted)", "5 4", t("ideal, i₁/n", "ideal, i₁/n")], ["var(--accent)", "", t("secundar real, i₂", "actual secondary, i₂")], ["var(--trip)", "", t("curent de magnetizare, i_m", "excitation current, i_m")]];
    leg.forEach(([c, dsh, txt], i) => { const lx = L + i * 230; g += `<line x1="${lx}" x2="${lx + 20}" y1="${B + 48}" y2="${B + 48}" stroke="${c}" stroke-width="2.4" ${dsh ? `stroke-dasharray="${dsh}"` : ""}/><text x="${lx + 26}" y="${B + 52}" class="tick">${txt}</text>`; });
    document.getElementById("wave").innerHTML = g;
  }

  function drawMeas(d, thrH, thrL, pk) {
    const tmax = 0.2, L = 66, R = 744, T = 14, B = 220;
    const ymax = Math.max(...d.Iid, ...d.I, thrH || 0) * 1.12;
    const A = axes(L, R, T, B, tmax, 0, ymax, t("curent măsurat, A sec.", "measured current, A sec."));
    let g = A.s;
    g += poly(A.xs, A.ys, d.t, d.Iid, "var(--muted)", 1.6, "5 4");
    g += poly(A.xs, A.ys, d.t, d.I, "var(--accent)", 2.2, "");
    const hl = (v, lab) => `<line x1="${L}" x2="${R}" y1="${A.ys(v)}" y2="${A.ys(v)}" stroke="var(--c3)" stroke-dasharray="6 3"/><text x="${R - 4}" y="${A.ys(v) - 4}" class="tick" text-anchor="end" fill="var(--c3)">${lab}</text>`;
    if (thrH) g += hl(thrH, `I>> = ${PR.fmt(thrH, 2)} A`);
    if (thrL * M3.GT < ymax) g += hl(thrL * M3.GT, `1,1·I> = ${PR.fmt(thrL * M3.GT, 2)} A`);
    const dot = (tt, v, col) => (tt != null ? `<circle cx="${A.xs(tt)}" cy="${A.ys(v)}" r="4.5" fill="${col}" stroke="var(--surface)" stroke-width="1.5"/>` : "");
    if (thrH) { g += dot(pk.hiId, thrH, "var(--muted)") + dot(pk.hi, thrH, "var(--accent)"); }
    const leg = [["var(--muted)", "5 4", t("cu TC ideal", "with an ideal CT")], ["var(--accent)", "", t("cu TC-ul real", "with the actual CT")]];
    leg.forEach(([c, dsh, txt], i) => { const lx = L + i * 230; g += `<line x1="${lx}" x2="${lx + 20}" y1="${B + 48}" y2="${B + 48}" stroke="${c}" stroke-width="2.4" ${dsh ? `stroke-dasharray="${dsh}"` : ""}/><text x="${lx + 26}" y="${B + 52}" class="tick">${txt}</text>`; });
    document.getElementById("meas").innerHTML = g;
  }

  function drawExcit(mg, s, c, n) {
    const L = 76, R = 744, T = 14, B = 240;
    const E0 = mg.Eal * 0.02, E1 = mg.Eal * 1.4;
    const Es = [], Is = [];
    for (let i = 0; i <= 80; i++) { const E = E0 * Math.pow(E1 / E0, i / 80); Es.push(E); Is.push(mg.Irms(E)); }
    const I0 = Math.max(1e-4, Math.min(...Is)), I1 = Math.max(...Is);
    const lx = (I) => L + ((R - L) * Math.log10(I / I0)) / Math.log10(I1 / I0), ly = (E) => B - ((B - T) * Math.log10(E / E0)) / Math.log10(E1 / E0);
    let g = "";
    for (let e = Math.floor(Math.log10(I0)); e <= Math.ceil(Math.log10(I1)); e++) { const v = Math.pow(10, e); if (v < I0 || v > I1) continue; g += `<line x1="${lx(v)}" x2="${lx(v)}" y1="${T}" y2="${B}" class="grid"/><text x="${lx(v)}" y="${B + 16}" class="tick" text-anchor="middle">${PR.sig(v, 1)}</text>`; }
    for (let e = Math.floor(Math.log10(E0)); e <= Math.ceil(Math.log10(E1)); e++) [1, 2, 5].forEach((m) => { const v = m * Math.pow(10, e); if (v < E0 || v > E1) return; g += `<line x1="${L}" x2="${R}" y1="${ly(v)}" y2="${ly(v)}" class="${m === 1 ? "grid" : "minor"}"/><text x="${L - 6}" y="${ly(v) + 4}" class="tick" text-anchor="end">${PR.sig(v, 2)}</text>`; });
    g += `<text x="${R}" y="${B + 30}" class="tick" text-anchor="end">${t("curentul de magnetizare (efectiv), A", "excitation current (rms), A")}</text><text x="${L - 54}" y="${(T + B) / 2}" class="tick" text-anchor="middle" transform="rotate(-90 ${L - 54} ${(T + B) / 2})">${t("t.e.m. (efectivă), V", "EMF (rms), V")}</text>`;
    g += `<polyline points="${Es.map((E, i) => `${lx(Is[i]).toFixed(1)},${ly(E).toFixed(1)}`).join(" ")}" fill="none" stroke="var(--accent)" stroke-width="2.4"/>`;
    const hl = (E, lab, col) => (E > E0 && E < E1 ? `<line x1="${L}" x2="${R}" y1="${ly(E)}" y2="${ly(E)}" stroke="${col}" stroke-dasharray="6 3"/><text x="${L + 6}" y="${ly(E) - 4}" class="tick" fill="${col}">${lab}</text>` : "");
    g += hl(mg.Ek, `E_k (IEC) = ${PR.fmt(mg.Ek, 0)} V`, "var(--c4)");
    g += hl(mg.Eal, `E_al = ${PR.fmt(mg.Eal, 0)} V`, "var(--c3)");
    const Ereq = (c.If / n) * (P.Rct + s.Rb1);
    g += hl(Ereq, `${t("cerut la I″k simetric", "needed at symmetrical I″k")}: ${PR.fmt(Ereq, 0)} V`, "var(--trip)");
    document.getElementById("excit").innerHTML = g;
  }

  function drawSteps(c, s, sim, mg, pk, n) {
    const R = (lab, eq, val) => `<tr><td>${bi(lab)}</td><td class="eq">${eq}</td><td class="n">${val}</td></tr>`;
    let h = `<tr><th>${bi("Mărime", "Quantity")}</th><th>${bi("Relația", "Relation")}</th><th class="n">${bi("Valoare", "Value")}</th></tr>`;
    h += R({ ro: "Sarcina nominală", en: "Rated burden" }, "(2) R_bn = S_n/I_sn²", `${PR.fmt(s.Rbn, 3)} Ω`);
    h += R({ ro: "Un conductor de legătură", en: "One lead" }, "ρℓ/A", `${PR.fmt(s.Rl, 3)} Ω`);
    h += R({ ro: "Intrarea releului", en: "Relay input" }, "S_releu/I_sn²", `${PR.fmt(s.Rr, 3)} Ω`);
    h += R({ ro: "Sarcina reală 3F / nesimetric", en: "Actual burden 3F / unbalanced" }, "(4) k_b = 1 / 2", `${PR.fmt(s.Rb1, 3)} / ${PR.fmt(s.Rb2, 3)} Ω`);
    h += R({ ro: "T.e.m. limită de precizie", en: "Accuracy limit EMF" }, "(2)", `${PR.fmt(s.Eal, 1)} V`);
    h += R({ ro: "Factorul limită real", en: "Effective limit factor" }, "(3)", `${PR.fmt(s.Fa1, 1)} / ${PR.fmt(s.Fa2, 1)}`);
    h += R({ ro: "Curentul de defect raportat", en: "Fault current, per unit" }, "I″k/I_pn", PR.fmt(s.kF, 2));
    h += R({ ro: "Factorul de saturație", en: "Saturation factor" }, `(5) K_s = F_a/(I″k/I_pn), r = ${PR.fmt(P.rem, 2)}`, `${PR.fmt(s.Ks, 2)} → ${PR.fmt(s.Ks * (1 - P.rem), 2)}`);
    h += R({ ro: "Timpul până la saturație", en: "Time to saturation" }, `(5) X/R = ${PR.fmt(c.xr, 1)}`, `${fms(s.ts)} (${t("simulare", "simulation")}: ${fms(sim.tSat)})`);
    h += R({ ro: "Punctul de cot al modelului", en: "Model knee point" }, "+10 % U → +50 % I_m", `${PR.fmt(mg.Ek, 1)} V, ${PR.fmt(mg.Ik * 1000, 1)} mA`);
    if (pk.hi != null || pk.hiId != null) h += R({ ro: "Pornirea treptei I>>", en: "I>> stage pickup" }, t("TC ideal / real", "ideal / actual CT"), `${fms(pk.hiId)} / ${fms(pk.hi)}`);
    h += R({ ro: "Pornirea treptei I> (1,1·I>)", en: "I> stage start (1.1·I>)" }, t("TC ideal / real", "ideal / actual CT"), `${fms(pk.loId)} / ${fms(pk.lo)}`);
    document.getElementById("steps").innerHTML = h;
  }

  /* ---------- reglaje ---------- */
  function renderSheet() {
    if (!LAST) return;
    const { c, s, sim } = LAST;
    const set = M3.autoSettings({ ...window.M01.DEFAULTS }, M3.DEFAULTS);
    const load = set.load[P.relay];
    document.getElementById("sheet-meta").innerHTML = bi(`${P.relay} · TC ${PR.fmt(P.Ipn, 0)}/${P.Isn} A ${P.cls}${P.alf} ${PR.fmt(P.Sn, 1)} VA`, `${P.relay} · CT ${PR.fmt(P.Ipn, 0)}/${P.Isn} A ${P.cls}${P.alf} ${PR.fmt(P.Sn, 1)} VA`);
    const rows = [
      [{ ro: "Raportul TC", en: "CT ratio" }, `${PR.fmt(P.Ipn, 0)}/${P.Isn} A`, { ro: "plăcuța TC", en: "CT nameplate" }],
      [{ ro: "Clasa, ALF, S_n", en: "Class, ALF, S_n" }, `${P.cls}${P.alf}, ${PR.fmt(P.Sn, 1)} VA`, { ro: "plăcuța TC", en: "CT nameplate" }],
      [{ ro: "R_ct", en: "R_ct" }, `${PR.fmt(P.Rct, 2)} Ω`, { ro: "buletinul de încercări", en: "test report" }],
      [{ ro: "Conductoare", en: "Leads" }, `${PR.fmt(P.lead, 0)} m · ${PR.fmt(P.leadA, 1)} mm² Cu`, { ro: "planul de cablare", en: "wiring plan" }],
      [{ ro: "Consumul releului", en: "Relay burden" }, `${PR.fmt(P.Srelay, 2)} VA`, { ro: "fișa tehnică a releului", en: "relay data sheet" }],
      [{ ro: "I″k max la locul releului, X/R", en: "I″k max at the relay, X/R" }, `${fA(c.If)}, ${PR.fmt(c.xr, 1)}`, { ro: "M01, regim maxim", en: "M01, maximum case" }],
      [{ ro: "Curentul maxim de sarcină", en: "Maximum load current" }, fA(load), { ro: "M03, date de intrare", en: "M03, input data" }],
      [{ ro: "Reglajele I> / I>>", en: "Settings I> / I>>" }, `${fA(c.Is)} / ${c.Ih > 0 ? fA(c.Ih) : "—"}`, { ro: "fișa de reglaje M03", en: "M03 settings sheet" }],
    ];
    document.getElementById("rg-in").innerHTML = `<tr><th>${bi("Mărime", "Quantity")}</th><th class="n">${bi("Valoare", "Value")}</th><th>${bi("Sursa", "Source")}</th></tr>` + rows.map(([a, b, cc]) => `<tr><td>${bi(a)}</td><td class="n">${b}</td><td>${bi(cc)}</td></tr>`).join("");
    const rr = t("R_releu", "R_relay");
    document.getElementById("rg-burden").textContent = `R_l = ρ·ℓ/A = ${PR.fmt(0.0175, 4)}·${PR.fmt(P.lead, 0)}/${PR.fmt(P.leadA, 1)} = ${PR.fmt(s.Rl, 3)} Ω\n${rr} = ${PR.fmt(P.Srelay, 2)}/${P.Isn}² = ${PR.fmt(s.Rr, 3)} Ω\nR_b (3F) = R_l + ${rr} = ${PR.fmt(s.Rb1, 3)} Ω\nR_b (${t("nesimetric", "unbalanced")}) = 2·R_l + ${rr} = ${PR.fmt(s.Rb2, 3)} Ω`;
    document.getElementById("rg-fa").textContent = `R_bn = ${PR.fmt(P.Sn, 1)}/${P.Isn}² = ${PR.fmt(s.Rbn, 2)} Ω\nE_al = ${P.alf}·${P.Isn}·(${PR.fmt(P.Rct, 2)} + ${PR.fmt(s.Rbn, 2)}) = ${PR.fmt(s.Eal, 1)} V\nF_a (3F) = ${P.alf}·(${PR.fmt(P.Rct, 2)} + ${PR.fmt(s.Rbn, 2)})/(${PR.fmt(P.Rct, 2)} + ${PR.fmt(s.Rb1, 3)}) = ${PR.fmt(s.Fa1, 1)}\nF_a (${t("nesimetric", "unbalanced")}) = ${PR.fmt(s.Fa2, 1)}`;
    const Fmin = Math.min(s.Fa1, s.Fa2);
    const okRatio = P.Ipn >= load;
    const Ks = s.Ks * (1 - P.rem), never = Ks >= 1 + c.xr;
    const CH = [
      [{ ro: "Raportul acoperă sarcina", en: "Ratio covers the load" }, "I_pn ≥ I_s max", fA(P.Ipn), `≥ ${fA(load)}`, okRatio, "M03"],
      [{ ro: "Treapta dependentă I>", en: "Inverse-time stage I>" }, "(6) F_a > 20·I>/I_pn", PR.fmt(Fmin, 1), `> ${PR.fmt(s.needIDMT, 1)}`, s.okIDMT, "ABB RED615"],
      [{ ro: "Treapta rapidă I>>", en: "High-set stage I>>" }, "I>>/I_pn < F_a", PR.fmt(s.needHigh, 2), `< ${PR.fmt(s.Fa1, 1)}`, s.okHigh, "ABB RED615"],
      [{ ro: "Curentul maxim simetric", en: "Maximum symmetrical current" }, "I″k/I_pn ≤ F_a", PR.fmt(s.kF, 1), `≤ ${PR.fmt(s.Fa1, 1)}`, s.okSym, "IEC 61869-2"],
      [{ ro: "Fără saturație tranzitorie", en: "No transient saturation" }, "K_s(1 − r) ≥ 1 + X/R", PR.fmt(Ks, 2), `≥ ${PR.fmt(1 + c.xr, 1)}`, never, "IEEE C37.110"],
    ];
    document.getElementById("rg-checks").innerHTML = `<tr><th>${bi("Verificarea", "Check")}</th><th>${bi("Criteriul", "Criterion")}</th><th class="n">${bi("Valoare", "Value")}</th><th class="n">${bi("Cerut", "Required")}</th><th>${bi("Rezultat", "Result")}</th><th>${bi("Sursa", "Source")}</th></tr>` +
      CH.map(([a, b, v, r, ok, src], i) => `<tr><td>${bi(a)}</td><td class="eq">${b}</td><td class="n">${v}</td><td class="n">${r}</td><td><span class="${ok ? "ok" : i === 4 ? "warn" : "bad"}">${ok ? t("îndeplinit", "met") : i === 4 ? t("se saturează", "saturates") : t("neîndeplinit", "not met")}</span></td><td>${src}</td></tr>`).join("");
    const pkh = LAST.pk, dl = pkh.hi != null && pkh.hiId != null ? pkh.hi - pkh.hiId : null;
    let noteRo, noteEn;
    if (never) { noteRo = "TC-ul nu se saturează nici la curentul maxim complet asimetric."; noteEn = "The CT does not saturate even at the fully offset maximum current."; }
    else if (!(c.Ih > 0)) { noteRo = "Releul nu are treaptă rapidă; saturația tranzitorie prelungește cel mult timpul treptei dependente, cu ordinul constantei de timp aperiodice."; noteEn = "The relay has no high-set stage; transient saturation at most prolongs the inverse-time stage, by the order of the DC time constant."; }
    else if (pkh.hi == null) { noteRo = "În simulare, treapta I>> nu pornește deloc în primele 200 ms: TC-ul nu e potrivit pentru această treaptă. Se mărește F_a (sarcină mai mică, ALF sau VA mai mari) sau se coboară reglajul I>>."; noteEn = "In the simulation, the I>> stage does not pick up at all in the first 200 ms: the CT is not adequate for this stage. Increase F_a (lower burden, higher ALF or VA) or lower the I>> setting."; }
    else if (dl > 0.01) { noteRo = `În simulare, treapta I>> pornește după ${fms(pkh.hi)}, față de ${fms(pkh.hiId)} cu un TC ideal: o întârziere de ${PR.fmt(dl * 1000, 0)} ms din cauza saturației. Se verifică dacă mai e acceptabilă pentru coordonare și pentru stabilitatea termică.`; noteEn = `In the simulation, the I>> stage picks up after ${fms(pkh.hi)}, against ${fms(pkh.hiId)} with an ideal CT: a ${PR.fmt(dl * 1000, 0)} ms delay due to saturation. Check whether it is still acceptable for coordination and thermal withstand.`; }
    else { noteRo = `TC-ul se saturează, dar treapta I>> pornește înainte de saturație (${fms(pkh.hi)}, ideal ${fms(pkh.hiId)}). Pentru o protecție maximală e suficient; la protecțiile diferențiale și de distanță se dimensionează cu factorul tranzitoriu K_td (M07, M10).`; noteEn = `The CT saturates, but the I>> stage picks up before saturation (${fms(pkh.hi)}, ideal ${fms(pkh.hiId)}). For overcurrent protection this is sufficient; differential and distance protection are sized with the transient factor K_td (M07, M10).`; }
    document.getElementById("rg-note").innerHTML = `<b class="k">${bi("Interpretare", "Interpretation")}</b>` + bi(noteRo, noteEn);
    document.getElementById("rg-cap").textContent = t("Datele TC-ului și rezultatul verificărilor", "CT data and check results");
    const sum = [[t("TC", "CT"), `${PR.fmt(P.Ipn, 0)}/${P.Isn} A ${P.cls}${P.alf} ${PR.fmt(P.Sn, 1)} VA`], ["R_ct", `${PR.fmt(P.Rct, 2)} Ω`], ["R_b (3F / " + t("nesim.", "unbal.") + ")", `${PR.fmt(s.Rb1, 3)} / ${PR.fmt(s.Rb2, 3)} Ω`], ["F_a (3F / " + t("nesim.", "unbal.") + ")", `${PR.fmt(s.Fa1, 1)} / ${PR.fmt(s.Fa2, 1)}`], ["E_al", `${PR.fmt(s.Eal, 1)} V`], ["t_sat (" + t("formulă / simulare", "formula / simulation") + ")", `${fms(s.ts)} / ${fms(sim.tSat)}`], [t("Verificări îndeplinite", "Checks met"), `${CH.slice(0, 4).filter((x) => x[4]).length} / 4`]];
    document.getElementById("rg-sum").innerHTML = sum.map(([a, b]) => `<tr><td>${a}</td><td class="n">${b}</td></tr>`).join("");
  }
  document.getElementById("copy-ct").addEventListener("click", (e) => {
    const { c, s, sim } = LAST;
    PR.copyTSV([["releu", "TC", "clasa", "R_ct_ohm", "R_b_3F_ohm", "R_b_nesim_ohm", "F_a_3F", "F_a_nesim", "E_al_V", "Ik_pe_Ipn", "t_sat_formula_ms", "t_sat_sim_ms"],
      [P.relay, `${P.Ipn}/${P.Isn}`, `${P.cls}${P.alf} ${P.Sn}VA`, PR.xnum(P.Rct, 2), PR.xnum(s.Rb1, 3), PR.xnum(s.Rb2, 3), PR.xnum(s.Fa1, 1), PR.xnum(s.Fa2, 1), PR.xnum(s.Eal, 1), PR.xnum(s.kF, 2), isFinite(s.ts) ? PR.xnum(s.ts * 1000, 1) : "", sim.tSat != null ? PR.xnum(sim.tSat * 1000, 1) : ""]], e.currentTarget);
  });

  /* ---------- test ---------- */
  const MCQ = [
    { q: { ro: "Ce înseamnă 5P20?", en: "What does 5P20 mean?" }, o: [{ ro: "Eroare compusă ≤ 5 % până la 20·I_pn, pe sarcina nominală", en: "Composite error ≤ 5 % up to 20·I_pn, on rated burden" }, { ro: "Eroare de raport 5 % la 20 VA", en: "Ratio error 5 % at 20 VA" }, { ro: "5 A secundar, 20 A primar", en: "5 A secondary, 20 A primary" }, { ro: "Remanență 5 %, 20 ms", en: "5 % remanence, 20 ms" }], a: 0, e: { ro: "IEC 61869-2: clasa P, eroare compusă 5 %, ALF = 20.", en: "IEC 61869-2: class P, 5 % composite error, ALF = 20." } },
    { q: { ro: "Ce se întâmplă cu F_a dacă sarcina reală e mai mică decât cea nominală?", en: "What happens to F_a if the actual burden is below rated?" }, o: [{ ro: "Crește", en: "It increases" }, { ro: "Scade", en: "It decreases" }, { ro: "Rămâne ALF", en: "It stays ALF" }, { ro: "Devine zero", en: "It becomes zero" }], a: 0, e: { ro: "Relația (3): aceeași t.e.m. limită împinge un curent mai mare printr-o sarcină mai mică.", en: "Relation (3): the same limit EMF drives a larger current through a smaller burden." } },
    { q: { ro: "De ce se preferă secundarul de 1 A în stațiile noi?", en: "Why is a 1 A secondary preferred in new substations?" }, o: [{ ro: "Conductoarele consumă de 25 de ori mai puțini VA decât la 5 A", en: "The leads consume 25 times fewer VA than at 5 A" }, { ro: "Releele sunt mai ieftine", en: "Relays are cheaper" }, { ro: "Precizia e mai mare la 1 A", en: "Accuracy is higher at 1 A" }, { ro: "Pentru IEC 60909", en: "Because of IEC 60909" }], a: 0, e: { ro: "Puterea pe conductor e I²R: (5/1)² = 25.", en: "Lead power is I²R: (5/1)² = 25." } },
    { q: { ro: "Ce factor de buclă al conductoarelor se folosește la defectul trifazat?", en: "Which lead loop factor applies for a three-phase fault?" }, o: [{ ro: "1", en: "1" }, { ro: "2", en: "2" }, { ro: "3", en: "3" }, { ro: "√3", en: "√3" }], a: 0, e: { ro: "Curenții de întoarcere se anulează în neutru; contează doar conductorul de fază.", en: "Return currents cancel in the neutral; only the phase lead counts." } },
    { q: { ro: "De câte ori mai mult flux poate cere un curent complet asimetric față de cel simetric?", en: "How many times more flux can a fully offset current demand than a symmetrical one?" }, o: [{ ro: "1 + X/R", en: "1 + X/R" }, { ro: "√2", en: "√2" }, { ro: "2", en: "2" }, { ro: "X/R − 1", en: "X/R − 1" }], a: 0, e: { ro: "Anvelopa fluxului tinde spre 1 + X/R (relația 5).", en: "The flux envelope tends to 1 + X/R (relation 5)." } },
    { q: { ro: "Cum se compară formula timpului până la saturație cu calculul exact?", en: "How does the time-to-saturation formula compare with the exact calculation?" }, o: [{ ro: "Anticipează saturația, deci e acoperitoare", en: "It predicts saturation early, so it is conservative" }, { ro: "O întârzie", en: "It predicts it late" }, { ro: "E exactă", en: "It is exact" }, { ro: "Nu are legătură", en: "It is unrelated" }], a: 0, e: { ro: "Anvelopa presupune vârful alternativei în orice clipă; calculul exact dă saturația cu până la 8 ms mai târziu.", en: "The envelope assumes the AC peak at every instant; the exact calculation gives saturation up to 8 ms later." } },
    { q: { ro: "Ce efect are remanența?", en: "What is the effect of remanence?" }, o: [{ ro: "Reduce fluxul disponibil și grăbește saturația", en: "It reduces the available flux and hastens saturation" }, { ro: "Crește F_a", en: "It increases F_a" }, { ro: "Nu are efect", en: "No effect" }, { ro: "Elimină componenta aperiodică", en: "It removes the DC component" }], a: 0, e: { ro: "K_s se înlocuiește cu K_s(1 − r).", en: "K_s is replaced by K_s(1 − r)." } },
    { q: { ro: "Ce clasă se folosește de obicei la protecțiile diferențiale?", en: "Which class is usually used for differential protection?" }, o: [{ ro: "PX", en: "PX" }, { ro: "0,5", en: "0.5" }, { ro: "10P5", en: "10P5" }, { ro: "3P", en: "3P" }], a: 0, e: { ro: "PX e definit prin E_k, I_e și R_ct, mărimile din calculul de stabilitate al diferențialelor.", en: "PX is defined by E_k, I_e and R_ct, the quantities used in differential stability calculations." } },
    { q: { ro: "Ce clase sunt potrivite pentru protecția maximală nedirecțională?", en: "Which classes suit non-directional overcurrent protection?" }, o: [{ ro: "5P și 10P", en: "5P and 10P" }, { ro: "Numai PX", en: "PX only" }, { ro: "Numai TPZ", en: "TPZ only" }, { ro: "Clasele de măsură 0,2 și 0,5", en: "Metering classes 0.2 and 0.5" }], a: 0, e: { ro: "Ghidul ABB: 5P și 10P sunt potrivite, 5P fiind mai precisă.", en: "ABB guide: 5P and 10P are suitable, 5P being more accurate." } },
    { q: { ro: "Ce cere manualul ABB RED615 pentru treapta dependentă fără treaptă rapidă?", en: "What does the ABB RED615 manual require for an inverse-time stage without high-set?" }, o: [{ ro: "F_a > 20·I>/I_pn", en: "F_a > 20·I>/I_pn" }, { ro: "F_a > I>/I_pn", en: "F_a > I>/I_pn" }, { ro: "F_a = ALF", en: "F_a = ALF" }, { ro: "F_a < 5", en: "F_a < 5" }], a: 0, e: { ro: "Altfel timpul de acționare se prelungește.", en: "Otherwise the operating time is prolonged." } },
    { q: { ro: "Cum e definit punctul de cot (IEC)?", en: "How is the knee point defined (IEC)?" }, o: [{ ro: "+10 % tensiune produce +50 % curent de magnetizare", en: "+10 % voltage gives +50 % excitation current" }, { ro: "Curentul de magnetizare egal cu 1 A", en: "Excitation current equal to 1 A" }, { ro: "Tensiunea la ALF", en: "The voltage at ALF" }, { ro: "Unghiul de 45° pe curba log–log", en: "The 45° point on the log–log curve" }], a: 0, e: { ro: "Definiția IEC; standardul ANSI/IEEE folosește altă definiție.", en: "IEC definition; ANSI/IEEE uses a different one." } },
    { q: { ro: "De ce întârzie treapta I>> când TC-ul se saturează?", en: "Why is the I>> stage delayed when the CT saturates?" }, o: [{ ro: "Filtrul Fourier măsoară o fundamentală mai mică decât cea reală", en: "The Fourier filter measures a lower fundamental than the real one" }, { ro: "Releul se blochează", en: "The relay blocks" }, { ro: "Crește pragul", en: "The pickup increases" }, { ro: "Întrerupătorul refuză", en: "The breaker fails" }], a: 0, e: { ro: "Forma de undă trunchiată are fundamentala redusă; pragul e atins mai târziu.", en: "The clipped waveform has a reduced fundamental; the pickup is reached later." } },
  ];
  function NUM() {
    const l = PR.rnd(20, 200, 5), A = PR.pick([1.5, 2.5, 4]), Sr = PR.pick([0.05, 0.1, 0.25]), alf = PR.pick([10, 20, 30]), Rct = PR.rnd(0.5, 5, 0.1), Sn = PR.pick([5, 10, 15]), Rb = PR.rnd(0.2, 3, 0.1), Ks = PR.rnd(2, 8, 0.5), xr = PR.rnd(10, 30, 1);
    return [
      { q: { ro: `Conductoare de ${l} m (dus), ${PR.fmt(A, 1)} mm² Cu, releu de ${PR.fmt(Sr, 2)} VA, secundar 1 A. Cât e sarcina la defect trifazat?`, en: `Leads of ${l} m (one way), ${PR.fmt(A, 1)} mm² Cu, ${PR.fmt(Sr, 2)} VA relay, 1 A secondary. What is the burden for a three-phase fault?` }, u: "Ω", v: (0.0175 * l) / A + Sr, e: { ro: "Relația (4) cu k_b = 1.", en: "Relation (4) with k_b = 1." } },
      { q: { ro: `TC 5P${alf}, ${Sn} VA, 1 A, R_ct = ${PR.fmt(Rct, 1)} Ω, sarcina reală ${PR.fmt(Rb, 1)} Ω. Cât e F_a?`, en: `CT 5P${alf}, ${Sn} VA, 1 A, R_ct = ${PR.fmt(Rct, 1)} Ω, actual burden ${PR.fmt(Rb, 1)} Ω. What is F_a?` }, u: "–", v: (alf * (Rct + Sn)) / (Rct + Rb), e: { ro: "Relația (3).", en: "Relation (3)." } },
      { q: { ro: `Același TC: cât e t.e.m. limită E_al?`, en: `Same CT: what is the limit EMF E_al?` }, u: "V", v: alf * (Rct + Sn), e: { ro: "Relația (2), cu I_sn = 1 A.", en: "Relation (2), with I_sn = 1 A." } },
      { q: { ro: `K_s = ${PR.fmt(Ks, 1)}, X/R = ${xr}, la 50 Hz. După cât timp se saturează TC-ul, după formula (5)?`, en: `K_s = ${PR.fmt(Ks, 1)}, X/R = ${xr}, at 50 Hz. After how long does the CT saturate, by formula (5)?` }, u: "ms", v: M.timeToSat(Ks, xr) * 1000, e: { ro: "t_s = −T₁·ln(1 − (K_s − 1)/(X/R)), T₁ = (X/R)/ω.", en: "t_s = −T₁·ln(1 − (K_s − 1)/(X/R)), T₁ = (X/R)/ω." } },
    ];
  }

  /* ---------- pornire ---------- */
  ctl = PR.controls(document.getElementById("controls"), SCHEMA, P, onChange);
  document.getElementById("presets").innerHTML = PRESETS.map((x, i) => `<button class="btn" data-i="${i}">${bi(x[0])}</button>`).join("");
  document.getElementById("presets").onclick = (e) => { const b = e.target.closest("[data-i]"); if (!b) return; PRESETS[+b.dataset.i][1](); onChange("preset"); };
  render();
  PR.onLang(render);
  PR.math();
  PR.tabs(["lab", "reglaje", "teorie", "test"], "lab");
  PR.quiz(document.getElementById("qlist"), document.getElementById("score"), document.getElementById("q-reset"), { mcq: MCQ, num: NUM, pick: 8 });
})();
