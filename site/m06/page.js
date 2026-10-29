/* Modulul 06 — interfața paginii. Calculele sunt în engine.js (M06), ../m03/engine.js și ../m01/engine.js. */
(function () {
  "use strict";
  const M = window.M06, PR = window.PR;
  const bi = PR.bi, t = PR.t;
  const clone = (o) => JSON.parse(JSON.stringify(o));
  const S3 = Math.sqrt(3);

  const P = clone(M.DEFAULTS);
  const RG = { kSensB: 1.2, cti: 0.3, Uset: 0.85, tUset: 3.2, Uov: 1.15, tUov: 0.5 };
  const DG = { none: { ro: "fără centrală", en: "no plant" }, sync: { ro: "generator sincron", en: "synchronous generator" }, inv: { ro: "centrală cu invertor", en: "inverter-based plant" } };
  const ADJN = (id) => ({ ro: `${id} · ${M.ADJ[id].type === "ol70" ? "LEA 70/12" : "LES 185"} ${M.ADJ[id].km} km`, en: `${id} · ${M.ADJ[id].type === "ol70" ? "OHL 70/12" : "cable 185"} ${M.ADJ[id].km} km` });
  const SET = () => M.settingsFor(P);
  const fA = (I) => `${PR.fmt(Math.abs(I) < 0.5 ? 0 : I, 0)} A`;
  const fs = (x) => (isFinite(x) ? `${PR.fmt(x, 2)} s` : "—");
  const DIR = { fwd: { ro: "înainte", en: "forward" }, rev: { ro: "înapoi", en: "reverse" }, mixed: { ro: "mixt", en: "mixed" }, none: { ro: "—", en: "—" } };
  const who = (k) => ({ R2: "R2", R3: "R3", R4: "R4", A: t(`releul ${P.adj}`, `the ${P.adj} relay`) }[k] || "—");

  /* ---------- controale ---------- */
  const SCHEMA = [
    { g: { ro: "Centrala de pe F1", en: "Plant on F1" }, col: "--c4", open: true, openNarrow: false, items: [
      { k: "dg", l: { ro: "Tipul", en: "Type" }, sel: Object.entries(DG), wide: true },
      { k: "Sg", l: { ro: "Puterea aparentă S_rG", en: "Apparent power S_rG" }, u: "MVA", step: 0.5, min: 0.5, max: 10, range: [0.5, 10] },
      { k: "xg", l: { ro: "Poziția pe F1", en: "Position on F1" }, u: "km", step: 0.5, min: 0.5, max: 20, range: [0.5, 20] },
      { k: "xd", l: { ro: "Reactanța x″d", en: "Reactance x″d" }, u: "u.r.", step: 0.01, min: 0.05 },
      { k: "ukT", l: { ro: "u_k al transformatorului bloc", en: "Unit transformer u_k" }, u: "%", step: 0.5, min: 1 },
      { k: "k", l: { ro: "Curentul invertorului k = I/I_r", en: "Inverter current k = I/I_r" }, u: "–", step: 0.1, min: 1, max: 2, range: [1, 2] },
      { k: "phiInv", l: { ro: "Unghiul φ în urma lui U₁", en: "Angle φ lagging U₁" }, u: "°", step: 5, min: 0, max: 90, range: [0, 90] },
    ] },
    { g: { ro: "Defectul", en: "The fault" }, col: "--trip", open: true, openNarrow: false, items: [
      { k: "fault", l: { ro: "Locul", en: "Location" }, sel: [["F1", { ro: "pe F1 (linia cu centrala)", en: "on F1 (the plant's line)" }], ["adj", { ro: "pe plecarea vecină", en: "on the adjacent feeder" }], ["bus", { ro: "pe barele de 20 kV", en: "on the 20 kV busbar" }]], wide: true },
      { k: "xf", l: { ro: "Distanța pe F1", en: "Distance on F1" }, u: "km", step: 0.5, min: 0, max: 20, range: [0, 20] },
      { k: "adj", l: { ro: "Plecarea vecină", en: "Adjacent feeder" }, sel: Object.keys(M.ADJ).map((id) => [id, ADJN(id)]), wide: true },
      { k: "xa", l: { ro: "Distanța pe plecarea vecină", en: "Distance on the adjacent feeder" }, u: "km", step: 0.5, min: 0, max: 30, range: [0, 30] },
      { k: "type", l: { ro: "Tipul defectului", en: "Fault type" }, sel: [["3F", { ro: "trifazat (3F)", en: "three-phase (3F)" }], ["2F", { ro: "bifazat (2F)", en: "phase-to-phase (2F)" }]] },
      { k: "Rf", l: { ro: "Rezistența de defect", en: "Fault resistance" }, u: "Ω", step: 1, min: 0, range: [0, 50] },
      { k: "kase", l: { ro: "Regimul", en: "Case" }, sel: [["max", { ro: "maxim", en: "maximum" }], ["min", { ro: "minim", en: "minimum" }]] },
    ] },
    { g: { ro: "Reglajele releelor", en: "Relay settings" }, col: "--c3", items: [
      { k: "rel", l: { ro: "Reglajele R2–R4", en: "R2–R4 settings" }, sel: [["m03", { ro: "M03 (calculate fără centrală)", en: "M03 (computed without the plant)" }], ["rev", { ro: "revizuite pentru exportul centralei", en: "revised for the plant export" }]], wide: true },
      { k: "tmsA", l: { ro: "Plecarea vecină: TMS (IEC VI, I> ca R3)", en: "Adjacent feeder: TMS (IEC VI, I> as R3)" }, u: "–", step: 0.01, min: 0.05, max: 1.2, range: [0.05, 1.2] },
      { k: "IhA", l: { ro: "Plecarea vecină: treapta I>> activă", en: "Adjacent feeder: I>> stage enabled" }, chk: true },
    ] },
    { g: { ro: "Insularizarea", en: "Islanding" }, col: "--c5", items: [
      { k: "PG", l: { ro: "Puterea centralei P_G", en: "Plant output P_G" }, u: "MW", step: 0.1, min: 0 },
      { k: "PL", l: { ro: "Sarcina insulei P_L", en: "Island load P_L" }, u: "MW", step: 0.1, min: 0 },
      { k: "H", l: { ro: "Constanta de inerție H", en: "Inertia constant H" }, u: "s", step: 0.1, min: 0.3, max: 10, range: [0.3, 6] },
      { k: "rocof", l: { ro: "Pragul RoCoF>", en: "RoCoF> pickup" }, u: "Hz/s", step: 0.05, min: 0.05 },
      { k: "tRocof", l: { ro: "Temporizarea RoCoF", en: "RoCoF delay" }, u: "s", step: 0.05, min: 0 },
      { k: "tRAR", l: { ro: "Pauza RAR pe F1", en: "F1 auto-reclose dead time" }, u: "s", step: 0.1, min: 0.1 },
    ] },
  ];
  const PRESETS = [
    [{ ro: "Generator sincron 5 MVA (exemplu)", en: "5 MVA synchronous generator (example)" }, () => { Object.assign(P, clone(M.DEFAULTS)); }],
    [{ ro: "Centrală cu invertor 5 MVA", en: "5 MVA inverter-based plant" }, () => { Object.assign(P, clone(M.DEFAULTS), { dg: "inv" }); }],
    [{ ro: "Fără centrală (reglajele M03)", en: "No plant (M03 settings)" }, () => { P.dg = "none"; }],
    [{ ro: "Defect lângă bare pe F4", en: "Fault near the busbar on F4" }, () => { Object.assign(P, clone(M.DEFAULTS), { fault: "adj", adj: "F4", xa: 0, type: "3F", kase: "max", Rf: 0 }); }],
    [{ ro: "Centrală după R4, reglaje M03", en: "Plant beyond R4, M03 settings" }, () => { Object.assign(P, clone(M.DEFAULTS), { xg: 15, fault: "adj", adj: "F4", xa: 0, type: "3F", kase: "max", rel: "m03" }); }],
    [{ ro: "Declanșare simpatică: 10 MVA, F4 lentă", en: "Sympathetic trip: 10 MVA, slow F4" }, () => { Object.assign(P, clone(M.DEFAULTS), { dg: "sync", Sg: 10, xg: 2, fault: "adj", adj: "F4", xa: 0, type: "3F", kase: "max", Rf: 0, tmsA: 1.0, IhA: false, rel: "rev" }); }],
    [{ ro: "Defect pe barele de 20 kV", en: "Fault on the 20 kV busbar" }, () => { Object.assign(P, clone(M.DEFAULTS), { fault: "bus", type: "3F", kase: "max", Rf: 0 }); }],
    [{ ro: "Insulă echilibrată (P_G ≈ P_L)", en: "Balanced island (P_G ≈ P_L)" }, () => { Object.assign(P, clone(M.DEFAULTS), { PG: 3.9, PL: 4.0 }); }],
  ];
  let ctl, rgCtlA, rgCtlB, rgCtlC;
  function onChange() {
    P.xa = Math.min(P.xa, M.ADJ[P.adj].km);
    syncAll(); visKnobs(); render();
  }
  const syncAll = () => { [ctl, rgCtlA, rgCtlB, rgCtlC].forEach((c) => c && c.sync()); };
  function visKnobs() {
    const show = (k, on) => { const el = document.getElementById("in-" + k); if (el) el.closest(".knob").hidden = !on; };
    const has = P.dg !== "none";
    ["Sg", "xg"].forEach((k) => show(k, has));
    ["xd", "ukT"].forEach((k) => show(k, P.dg === "sync"));
    ["k", "phiInv"].forEach((k) => show(k, P.dg === "inv"));
    show("xf", P.fault === "F1"); show("adj", P.fault === "adj"); show("xa", P.fault === "adj");
    const xa = document.getElementById("in-xa-r"); if (xa) xa.max = M.ADJ[P.adj].km;
  }
  function buildButtons() {
    const pr = document.getElementById("presets");
    pr.innerHTML = PRESETS.map((x, i) => `<button class="btn" data-i="${i}">${bi(x[0])}</button>`).join("");
    pr.onclick = (e) => { const b = e.target.closest("[data-i]"); if (!b) return; PRESETS[+b.dataset.i][1](); onChange(); };
  }

  /* ---------- laborator ---------- */
  const M03GT = 1.1;
  function verdict(r, c) {
    const tm = c.times, p = r.p;
    if (p.fault === "F1") {
      const own = p.xf >= M.X4 ? "R4" : "R3";
      if (!c.who) return { cls: "bad", pill: t("NEELIMINAT", "NOT CLEARED"), msg: bi(`Defectul ${p.type} pe F1 la ${PR.fmt(p.xf, 1)} km nu e văzut de nicio protecție.`, `The ${p.type} fault on F1 at ${PR.fmt(p.xf, 1)} km is not seen by any protection.`) };
      const ok = c.who === own;
      let msg = bi(`Defect ${p.type} pe F1 la ${PR.fmt(p.xf, 1)} km: eliminat de ${c.who} în ${fs(c.t)} (releu + întrerupător).`, `${p.type} fault on F1 at ${PR.fmt(p.xf, 1)} km: cleared by ${c.who} in ${fs(c.t)} (relay + breaker).`);
      if (p.xf < M.X4 && tm.R4 < Infinity) msg += " " + bi(`R4 vede curentul centralei spre defect (${fA(r.IR4)}) și declanșează în ${fs(tm.R4)}: secțiunea de după R4 rămâne fără tensiune.`, `R4 sees the plant current towards the fault (${fA(r.IR4)}) and trips in ${fs(tm.R4)}: the section beyond R4 loses supply.`);
      return { cls: ok ? "ok" : "warn", pill: ok ? t("SELECTIV", "SELECTIVE") : t("REZERVĂ", "BACKUP"), msg };
    }
    if (p.fault === "adj") {
      const tA = tm.A;
      const base = bi(`Defect ${p.type} pe ${p.adj} la ${PR.fmt(p.xa, 1)} km: releul ${p.adj} declanșează în ${fs(tA)}. `, `${p.type} fault on ${p.adj} at ${PR.fmt(p.xa, 1)} km: the ${p.adj} relay trips in ${fs(tA)}. `);
      if (p.dg === "none") return { cls: "ok", pill: t("SELECTIV", "SELECTIVE"), msg: base + bi("Fără centrală, R3 și R4 nu văd nimic.", "Without the plant, R3 and R4 see nothing.") };
      // cel mai rapid releu de pe F1 care pornește pe curentul invers al centralei
      const cand = [["R3", tm.R3, r.IR3], ["R4", tm.R4, r.IR4]].filter((x) => x[1] < Infinity).sort((x, y) => x[1] - y[1]);
      if (!cand.length) return { cls: "ok", pill: t("SELECTIV", "SELECTIVE"), msg: base + bi(`R3 vede ${fA(r.IR3)} înapoi, sub pragul de pornire (${fA(M03GT * SET().R3.Is)}).`, `R3 sees ${fA(r.IR3)} reverse, below the pickup threshold (${fA(M03GT * SET().R3.Is)}).`) };
      const [k, tk, Ik] = cand[0], m = tk - tA;
      if (tk < tA + P.tcb) return { cls: "bad", pill: t("DECLANȘARE SIMPATICĂ", "SYMPATHETIC TRIP"), msg: base + bi(`${k} vede ${fA(Ik)} înapoi și temporizarea lui (${fs(tk)}) expiră înainte ca întrerupătorul plecării ${p.adj} să întrerupă (${fs(tA + P.tcb)}): F1 se deconectează fără defect.`, `${k} sees ${fA(Ik)} reverse and its delay (${fs(tk)}) expires before the ${p.adj} breaker interrupts (${fs(tA + P.tcb)}): F1 is disconnected without a fault.`) };
      if (m < RG.cti) return { cls: "warn", pill: t("MARJĂ INSUFICIENTĂ", "MARGIN TOO SMALL"), msg: base + bi(`${k} vede ${fA(Ik)} înapoi și declanșează în ${fs(tk)}: marja ${PR.fmt(m, 2)} s e sub Δt = ${PR.fmt(RG.cti, 2)} s.`, `${k} sees ${fA(Ik)} reverse and trips in ${fs(tk)}: the ${PR.fmt(m, 2)} s margin is below Δt = ${PR.fmt(RG.cti, 2)} s.`) };
      return { cls: "ok", pill: t("SELECTIV", "SELECTIVE"), msg: base + bi(`${k} vede ${fA(Ik)} înapoi și pornește, dar declanșează abia în ${fs(tk)} (marja ${PR.fmt(m, 2)} s ≥ Δt).`, `${k} sees ${fA(Ik)} reverse and picks up, but would trip only in ${fs(tk)} (margin ${PR.fmt(m, 2)} s ≥ Δt).`) };
    }
    // bare
    const base = bi(`Defect ${p.type} pe barele de 20 kV: R2 declanșează în ${fs(tm.R2)}. `, `${p.type} fault on the 20 kV busbar: R2 trips in ${fs(tm.R2)}. `);
    if (p.dg === "none") return { cls: "ok", pill: t("ELIMINAT", "CLEARED"), msg: base + bi("Fără centrală, după R2 defectul nu mai e alimentat.", "Without the plant, the fault is no longer fed after R2 opens.") };
    const tF1 = Math.min(tm.R3, tm.R4);
    if (tF1 < Infinity) return { cls: "ok", pill: t("ELIMINAT", "CLEARED"), msg: base + bi(`Centrala alimentează în continuare defectul prin F1 (${fA(r.IR3)}); ${tm.R3 <= tm.R4 ? "R3" : "R4"} nedirecțional o separă în ${fs(tF1)}. Cu R3 direcțional „înainte” ar fi nevoie de declanșare transmisă de la protecția barelor.`, `The plant keeps feeding the fault through F1 (${fA(r.IR3)}); a non-directional ${tm.R3 <= tm.R4 ? "R3" : "R4"} separates it in ${fs(tF1)}. With R3 directional forward, a transfer trip from the busbar protection would be needed.`) };
    return { cls: "warn", pill: t("ALIMENTAT DE CENTRALĂ", "FED BY THE PLANT"), msg: base + bi(`Centrala alimentează defectul prin F1 cu ${fA(r.IR3)}, sub pragul lui R3: îl oprește doar protecția de interfață (U< ${PR.fmt(RG.Uset, 2)}·U_n în ${PR.fmt(RG.tUset, 1)} s) sau o declanșare transmisă.`, `The plant feeds the fault through F1 with ${fA(r.IR3)}, below the R3 pickup: only the interface protection (U< ${PR.fmt(RG.Uset, 2)}·U_n in ${PR.fmt(RG.tUset, 1)} s) or a transfer trip stops it.`) };
  }

  function render() {
    const r = M.compute(P), c = M.clearing(r);
    const r0 = P.dg === "none" ? r : M.compute({ ...P, dg: "none" });
    const v = verdict(r, c);
    let st = `<div class="status ${v.cls}"><span class="led"></span><span class="pill">${v.pill}</span><span class="msg">${v.msg}</span></div>`;
    if (P.dg !== "none") {
      const nc = M.normalCheck(P, SET()), badN = ["R3", "R4"].filter((k) => !nc[k].ok);
      if (badN.length) st += `<div class="status bad" style="margin-top:8px"><span class="led"></span><span class="pill">${t("REGIM NORMAL", "NORMAL OPERATION")}</span><span class="msg">${badN.map((k) => bi(`${k}: exportul centralei, până la ${fA(nc[k].exp)}, cere I> ≥ ${fA(nc[k].need)}, dar pragul e ${fA(nc[k].Is)}: releul poate declanșa fără defect.`, `${k}: the plant export, up to ${fA(nc[k].exp)}, requires I> ≥ ${fA(nc[k].need)}, but the pickup is ${fA(nc[k].Is)}: the relay may trip without a fault.`)).join(" ")} ${bi("Alege reglajele revizuite (sau vezi fila Reglaje).", "Choose the revised settings (or see the Settings tab).")}</span></div>`;
    }
    document.getElementById("status").innerHTML = st;
    const ch = r0.IR3 > 0 && P.fault === "F1" && P.dg !== "none" ? ` <small>(${PR.fmt((100 * (r.IR3 - r0.IR3)) / r0.IR3, 1)} %)</small>` : "";
    const kp = [
      [bi("Curentul văzut de R3", "Current seen by R3"), `${fA(r.IR3)}${ch}`],
      [bi("Contribuția centralei", "Plant contribution"), P.dg === "none" ? "—" : fA(r.IDG)],
      [bi("U în punctul de racordare", "U at the connection point"), P.dg === "none" ? "—" : `${PR.fmt(r.VLLg, 2)} <small>${t("u.r.", "p.u.")}</small>`],
      [bi("Eliminarea defectului", "Fault clearing"), c.who ? `${PR.fmt(c.t, 2)} <small>s · ${who(c.who)}</small>` : "—"],
    ];
    document.getElementById("kpis").innerHTML = kp.map(([l, x]) => `<div><div class="label">${l}</div><div class="v">${x}</div></div>`).join("");
    drawSLD(r, c);
    drawTable(r, r0, c);
    drawBlind(r);
    drawFRT(r, c);
    drawIsland();
    renderSheet();
  }

  function drawSLD(r, c) {
    const xb = 150, x0 = 175, x1 = 715, yF = 92, yA = 214, L = 20;
    // km 0 al liniilor începe după TC-ul releului din cap (caseta de la x0)
    const k0 = x0 + 24, X = (km) => k0 + ((x1 - k0) * km) / L;
    const LA = M.ADJ[P.adj].km, XA = (km) => k0 + ((x1 - k0) * km) / 30;
    const tm = c.times;
    const box = (x, y, lab, trip, col = "var(--ink)") => `<rect x="${x - 9}" y="${y - 9}" width="18" height="18" rx="2" fill="${trip ? "var(--trip)" : "var(--surface)"}" stroke="${trip ? "var(--trip)" : col}" stroke-width="2"/><text x="${x}" y="${y - 14}" class="tick" text-anchor="middle" font-weight="600">${lab}</text>`;
    // ce declanșează: releul care elimină defectul și releele de pe F1 care expiră înaintea lui
    const tEnd = c.who ? c.relay + P.tcb : Infinity;
    const trips = (k) => (c.who === k) || (k !== "R2" && tm[k] < tEnd);
    let s = "";
    s += `<circle cx="40" cy="150" r="13" fill="none" stroke="var(--ink)" stroke-width="1.5"/><text x="40" y="155" class="tick" text-anchor="middle">110</text>`;
    s += `<line x1="53" y1="150" x2="70" y2="150" stroke="var(--ink)"/><circle cx="80" cy="150" r="10" fill="none" stroke="var(--ink)" stroke-width="1.5"/><circle cx="94" cy="150" r="10" fill="none" stroke="var(--ink)" stroke-width="1.5"/><text x="87" y="132" class="tick" text-anchor="middle">T1</text>`;
    s += `<line x1="104" y1="150" x2="${xb}" y2="150" stroke="var(--ink)"/>` + box(125, 150, "R2", c.who === "R2");
    s += `<text x="125" y="182" class="tick" text-anchor="middle">${fA(r.IR2)}</text>`;
    s += `<line x1="${xb}" y1="60" x2="${xb}" y2="240" stroke="var(--ink)" stroke-width="5"/><text x="${xb - 6}" y="252" class="lbl" text-anchor="end">20 kV</text>`;
    s += `<line x1="${xb}" y1="${yF}" x2="${x1}" y2="${yF}" stroke="var(--c1)" stroke-width="2" stroke-dasharray="8 4"/><text x="${x1}" y="${yF + 20}" class="tick" text-anchor="end">F1 · ${t("LEA 70/12", "OHL 70/12")} · 20 km</text>`;
    s += box(x0, yF, "R3", trips("R3")) + box(X(M.X4), yF, "R4", trips("R4"));
    const arrow = (d) => (d === "rev" ? "←" : d === "fwd" ? "→" : d === "mixed" ? "↔" : "");
    s += `<text x="${x0 + 14}" y="${yF + 22}" class="tick" font-weight="600" fill="${r.IR3 > 0 ? "var(--ink)" : "var(--muted)"}">${fA(r.IR3)} ${arrow(r.dirR3)}</text>`;
    if (r.IR4 > 0) s += `<text x="${X(M.X4) + 14}" y="${yF + 22}" class="tick" font-weight="600">${fA(r.IR4)} ${P.fault === "F1" && P.xf >= M.X4 ? "→" : "←"}</text>`;
    [0, 5, 10, 15, 20].forEach((k) => (s += `<line x1="${X(k)}" x2="${X(k)}" y1="${yF + 28}" y2="${yF + 33}" stroke="var(--muted)"/><text x="${X(k)}" y="${yF + 45}" class="tick" text-anchor="middle">${k}</text>`));
    if (P.dg !== "none") {
      const xg = X(Math.max(P.xg, M.XGMIN)), yg = 36;
      s += `<line x1="${xg}" y1="${yF}" x2="${xg}" y2="${yg + 13}" stroke="var(--c4)" stroke-width="2"/>`;
      if (P.dg === "sync") s += `<circle cx="${xg}" cy="${yg}" r="13" fill="var(--surface)" stroke="var(--c4)" stroke-width="2"/><text x="${xg}" y="${yg + 5}" class="tick" text-anchor="middle" font-weight="600" fill="var(--c4)">G</text>`;
      else s += `<rect x="${xg - 14}" y="${yg - 12}" width="28" height="24" fill="var(--surface)" stroke="var(--c4)" stroke-width="2"/><path d="M${xg - 14} ${yg + 12} L${xg + 14} ${yg - 12}" stroke="var(--c4)"/><text x="${xg - 7}" y="${yg - 1}" class="tick" fill="var(--c4)">=</text><text x="${xg + 3}" y="${yg + 9}" class="tick" fill="var(--c4)">~</text>`;
      const right = xg < 560;
      s += `<text x="${right ? xg + 20 : xg - 20}" y="${yg - 2}" class="tick" fill="var(--c4)" font-weight="600" text-anchor="${right ? "start" : "end"}">${PR.fmt(P.Sg, 1)} MVA · ${fA(r.IDG)}</text><text x="${right ? xg + 20 : xg - 20}" y="${yg + 12}" class="tick" text-anchor="${right ? "start" : "end"}">U ${PR.fmt(r.VLLg, 2)} ${t("u.r.", "p.u.")}</text>`;
    }
    s += `<line x1="${xb}" y1="${yA}" x2="${XA(LA)}" y2="${yA}" stroke="var(--c3)" stroke-width="${M.ADJ[P.adj].type === "ol70" ? 2 : 4}" ${M.ADJ[P.adj].type === "ol70" ? 'stroke-dasharray="8 4"' : ""}/><text x="${XA(LA)}" y="${yA + 20}" class="tick" text-anchor="end">${t(ADJN(P.adj))}</text>`;
    s += box(x0, yA, P.adj, c.who === "A", "var(--c3)");
    if (P.fault === "adj") s += `<text x="${x0 + 14}" y="${yA + 22}" class="tick" font-weight="600">${fA(r.IA)} →</text>`;
    const fx = P.fault === "F1" ? X(P.xf) : P.fault === "adj" ? XA(P.xa) : xb, fy = P.fault === "F1" ? yF : P.fault === "adj" ? yA : 150;
    const fr = fx < 600;
    s += `<path d="M${fx + 4} ${fy - 24} l10 12 -7 3 9 15" stroke="var(--trip)" stroke-width="2.5" fill="none"/><text x="${fr ? fx + 22 : fx - 6}" y="${fy - 12}" class="tick" fill="var(--trip)" font-weight="600" text-anchor="${fr ? "start" : "end"}">${P.type} · ${fA(r.IF)}</text>`;
    s += `<g transform="translate(160,278)"><rect x="0" y="-10" width="14" height="14" fill="var(--trip)"/><text x="20" y="1" class="tick">${t("declanșează", "trips")}</text><text x="130" y="1" class="tick">→ ${t("înainte (spre linie)", "forward (into the line)")} · ← ${t("înapoi (spre bare)", "reverse (towards busbar)")}</text></g>`;
    document.getElementById("sld").innerHTML = s;
  }

  function drawTable(r, r0, c) {
    const tm = c.times, S = SET();
    const rows = [
      ["R2", t("sosirea T1", "T1 incomer"), r.IR2, r0.IR2, S.R2, tm.R2, ""],
      ["R3", t("capul lui F1", "F1 head"), r.IR3, r0.IR3, S.R3, tm.R3, r.IR3 > 0 ? `${t(DIR[r.dirR3])}${r.dirPicked ? "" : t(" (nepornit)", " (not picked up)")}` : ""],
      ["R4", t("F1, km 10", "F1, km 10"), r.IR4, r0.IR4, S.R4, tm.R4, r.IR4 > 0 && !(P.fault === "F1" && P.xf >= M.X4) ? t("curentul centralei, înapoi", "plant current, reverse") : ""],
      [P.adj, t("plecarea vecină", "adjacent feeder"), r.IA, r0.IA, M.relayA(P), tm.A, ""],
    ];
    let h = `<tr><th>${bi("Releul", "Relay")}</th><th>${bi("Locul", "Location")}</th><th class="n">${bi("Curentul", "Current")}</th><th class="n">${bi("Fără centrală", "Without plant")}</th><th class="n">I&gt;</th><th class="n">TMS</th><th class="n">I&gt;&gt;</th><th class="n">${bi("Timpul", "Time")}</th><th>${bi("Observație", "Note")}</th></tr>`;
    rows.forEach(([id, loc, I, I0, St, tt, note]) => {
      h += `<tr${c.who && (c.who === id || (c.who === "A" && id === P.adj)) ? ' class="res"' : ""}><td>${id}</td><td>${loc}</td><td class="n">${fA(I)}</td><td class="n">${fA(I0)}</td><td class="n">${fA(St.Is)}</td><td class="n">${PR.fmt(St.tms, 2)}</td><td class="n">${St.Ih > 0 ? `${fA(St.Ih)} / ${PR.fmt(St.th, 2)} s` : "—"}</td><td class="n">${fs(tt)}</td><td>${note}</td></tr>`;
    });
    if (P.dg !== "none") h += `<tr><td>${t("Centrala", "Plant")}</td><td>F1, km ${PR.fmt(P.xg, 1)}</td><td class="n">${fA(r.IDG)}</td><td class="n">—</td><td colspan="5" class="note">${P.dg === "inv" ? bi(`k·I_r = ${PR.fmt(P.k, 2)}·${PR.fmt(r.Ir, 1)} A${r.frozen ? "; unghiul de dinainte de defect (tensiune sub 0,1 u.r. sau fără punct fix)" : ""}`, `k·I_r = ${PR.fmt(P.k, 2)}·${PR.fmt(r.Ir, 1)} A${r.frozen ? "; pre-fault angle (voltage below 0.1 p.u. or no fixed point)" : ""}`) : bi(`Z_G = ${PR.fmt(r.zg.re, 2)} + j${PR.fmt(r.zg.im, 2)} Ω (la 20 kV)`, `Z_G = ${PR.fmt(r.zg.re, 2)} + j${PR.fmt(r.zg.im, 2)} Ω (at 20 kV)`)}</td></tr>`;
    h += `<tr><td colspan="9" class="note">${P.rel === "rev" && P.dg !== "none" ? bi("Reglajele R2–R4 sunt revizuite pentru exportul centralei (procedura M03, curba IEC VI).", "R2–R4 settings are revised for the plant export (M03 procedure, IEC VI curve).") : bi("Reglajele R2–R4 sunt cele din fișa M03 (curba IEC VI), calculate fără centrală.", "R2–R4 settings are those of the M03 sheet (IEC VI curve), computed without the plant.")} ${bi("Releul plecării vecine are I> al lui R3 din M03, cu TMS și I>> din laborator. Timpul nu include întrerupătorul.", "The adjacent feeder relay has the M03 R3 I>, with TMS and I>> from the lab. The time excludes the breaker.")}</td></tr>`;
    document.getElementById("rtab").innerHTML = h;
  }

  function drawBlind(r) {
    const b = M.blinding(P);
    const L = 64, Rr = 740, T = 22, B = 236;
    // scară logaritmică: se văd și curenții mari de lângă bare, și diferențele de la capătul liniei
    const lo = 100, hi = Math.pow(10, Math.ceil(Math.log10(Math.max(...b.pts.map((p) => Math.max(p.with, p.without))) * 1.05)));
    const sx = (km) => L + ((Rr - L) * km) / 20, sy = (I) => B - ((B - T) * (Math.log10(Math.max(I, lo)) - Math.log10(lo))) / (Math.log10(hi) - Math.log10(lo));
    let s = "";
    for (let e = Math.log10(lo); e <= Math.log10(hi) + 1e-9; e++) [1, 2, 5].forEach((m) => {
      const v = m * Math.pow(10, e); if (v > hi * 1.0001) return;
      s += `<line x1="${L}" x2="${Rr}" y1="${sy(v)}" y2="${sy(v)}" class="grid" ${m === 1 ? "" : 'stroke-dasharray="2 4"'}/><text x="${L - 6}" y="${sy(v) + 4}" class="tick" text-anchor="end">${PR.fmt(v, 0)}</text>`;
    });
    [0, 5, 10, 15, 20].forEach((k) => (s += `<line x1="${sx(k)}" x2="${sx(k)}" y1="${T}" y2="${B}" class="grid"/><text x="${sx(k)}" y="${B + 15}" class="tick" text-anchor="middle">${k}</text>`));
    const line = (key, col, dash, w = 2.2) => `<polyline points="${b.pts.map((p) => `${sx(p.xf).toFixed(1)},${sy(p[key]).toFixed(1)}`).join(" ")}" fill="none" stroke="${col}" stroke-width="${w}" ${dash ? `stroke-dasharray="${dash}"` : ""}/>`;
    s += line("without", "var(--muted)", "6 4");
    if (P.dg !== "none") s += line("with", "var(--c4)", "", 2.6);
    const hl = (v, lab, right) => `<line x1="${L}" x2="${Rr}" y1="${sy(v)}" y2="${sy(v)}" stroke="var(--trip)" stroke-dasharray="5 3"/><text x="${right ? Rr - 4 : L + 6}" y="${right ? sy(v) - 4 : sy(v) + 13}" class="tick" text-anchor="${right ? "end" : "start"}" fill="var(--trip)">${lab}</text>`;
    s += hl(b.Is, `I> R3 = ${fA(b.Is)}`, false) + hl(RG.kSensB * b.Is, `${PR.fmt(RG.kSensB, 1)}·I> = ${fA(RG.kSensB * b.Is)} (${t("rezervă", "backup")})`, true);
    s += `<line x1="${sx(M.X4)}" x2="${sx(M.X4)}" y1="${T}" y2="${B}" stroke="var(--ink)" stroke-dasharray="2 3"/><text x="${sx(M.X4) + 4}" y="${T + 12}" class="tick">R4</text>`;
    if (P.dg !== "none") s += `<line x1="${sx(P.xg)}" x2="${sx(P.xg)}" y1="${T}" y2="${B}" stroke="var(--c4)" stroke-dasharray="2 3"/><text x="${sx(P.xg) + 4}" y="${T + 26}" class="tick" fill="var(--c4)">${P.dg === "sync" ? "G" : "≈"}</text>`;
    if (P.fault === "F1") s += `<circle cx="${sx(Math.max(P.xf, M.XFMIN))}" cy="${sy(r.p.type === "2F" && r.p.kase === "min" && r.p.Rf === 0 ? r.IR3 : b.pts.reduce((a, q) => (Math.abs(q.xf - P.xf) < Math.abs(a.xf - P.xf) ? q : a)).with)}" r="4.5" fill="var(--trip)" stroke="var(--surface)" stroke-width="1.5"/>`;
    s += `<text x="${Rr}" y="${B + 30}" class="tick" text-anchor="end">${t("locul defectului pe F1, km", "fault location on F1, km")}</text><text x="16" y="${(T + B) / 2}" class="tick" text-anchor="middle" transform="rotate(-90 16 ${(T + B) / 2})">A</text>`;
    const lg = [["var(--muted)", "6 4", t("fără centrală", "without plant")]].concat(P.dg !== "none" ? [["var(--c4)", "", t(`cu ${DG[P.dg].ro} ${PR.fmt(P.Sg, 1)} MVA`, `with ${DG[P.dg].en} ${PR.fmt(P.Sg, 1)} MVA`)]] : []);
    lg.forEach(([cc, d, txt], i) => { const x = L + 10 + i * 190; s += `<line x1="${x}" x2="${x + 22}" y1="${B + 44}" y2="${B + 44}" stroke="${cc}" stroke-width="2.4" ${d ? `stroke-dasharray="${d}"` : ""}/><text x="${x + 27}" y="${B + 48}" class="tick">${txt}</text>`; });
    if (P.dg !== "none") s += `<text x="${Rr}" y="${B + 48}" class="tick" text-anchor="end" font-weight="600">${t("la 20 km", "at 20 km")}: ${PR.fmt(b.red * -100, 1)} % · k_sens ${PR.fmt(b.kEnd, 2)}</text>`;
    document.getElementById("blind").setAttribute("viewBox", `0 0 760 ${B + 58}`);
    document.getElementById("blind").innerHTML = s;
  }

  function drawFRT(r, c) {
    const svg = document.getElementById("frt");
    if (P.dg === "none") { svg.innerHTML = `<text x="380" y="140" class="lbl" text-anchor="middle">${t("Alege o centrală pentru a vedea golul de tensiune.", "Choose a plant to see the voltage dip.")}</text>`; document.getElementById("frt-note").innerHTML = ""; return; }
    const f = P.frt[P.dg], L = 60, Rr = 740, T = 20, B = 230;
    const tclr = c.t, tmax = Math.max(4, Math.min(isFinite(tclr) ? tclr + 0.6 : 4, 6), RG.tUset + 0.5);
    const sx = (x) => L + ((Rr - L) * x) / tmax, sy = (u) => B - ((B - T) * u) / 1.2;
    let s = "";
    [0, 0.2, 0.4, 0.6, 0.8, 1, 1.2].forEach((u) => (s += `<line x1="${L}" x2="${Rr}" y1="${sy(u)}" y2="${sy(u)}" class="grid"/><text x="${L - 6}" y="${sy(u) + 4}" class="tick" text-anchor="end">${PR.fmt(u, 1)}</text>`));
    PR.niceTicks(0, tmax, 8).forEach((x) => (s += `<line x1="${sx(x)}" x2="${sx(x)}" y1="${T}" y2="${B}" class="grid"/><text x="${sx(x)}" y="${B + 15}" class="tick" text-anchor="middle">${PR.fmt(x, 1)}</text>`));
    // profilul: zona în care centrala are voie să se deconecteze (sub curbă)
    const pts = [[0, f.Uret], [f.tclr, f.Uret], [f.tclr, f.Uclr], [f.trec2, f.Uclr], [f.trec3, f.Urec2], [tmax, f.Urec2]];
    s += `<polygon points="${pts.map(([x, u]) => `${sx(x).toFixed(1)},${sy(u).toFixed(1)}`).join(" ")} ${sx(tmax)},${sy(0)} ${sx(0)},${sy(0)}" fill="var(--start-bg)"/>`;
    s += `<polyline points="${pts.map(([x, u]) => `${sx(x).toFixed(1)},${sy(u).toFixed(1)}`).join(" ")}" fill="none" stroke="var(--start)" stroke-width="2.4"/>`;
    s += `<text x="${sx(0.75)}" y="${sy(0.1)}" class="tick" fill="var(--start)">${t("sub profil: centrala are voie să iasă", "below the profile: the plant may trip")}</text>`;
    // treapta U<
    s += `<polyline points="${sx(0)},${sy(RG.Uset)} ${sx(RG.tUset)},${sy(RG.Uset)} ${sx(RG.tUset)},${sy(0)}" fill="none" stroke="var(--trip)" stroke-dasharray="5 3" stroke-width="1.6"/><text x="${sx(RG.tUset) - 4}" y="${sy(RG.Uset) + 14}" class="tick" text-anchor="end" fill="var(--trip)">U< ${PR.fmt(RG.Uset, 2)} / ${PR.fmt(RG.tUset, 1)} s</text>`;
    // golul de tensiune
    const u = r.VLLg, te = isFinite(tclr) ? Math.min(tclr, tmax) : tmax;
    s += `<polyline points="${sx(0)},${sy(1)} ${sx(0)},${sy(u)} ${sx(te)},${sy(u)} ${isFinite(tclr) && tclr < tmax ? `${sx(te)},${sy(1)} ${sx(tmax)},${sy(1)}` : ""}" fill="none" stroke="var(--c4)" stroke-width="2.8"/>`;
    s += `<text x="${sx(te) + 5}" y="${sy(u) - 6}" class="tick" fill="var(--c4)" font-weight="600">${PR.fmt(u, 2)} ${t("u.r.", "p.u.")} · ${isFinite(tclr) ? `t_clr ${PR.fmt(tclr, 2)} s` : t("neeliminat", "not cleared")}</text>`;
    s += `<text x="${Rr}" y="${B + 30}" class="tick" text-anchor="end">t, s</text><text x="16" y="${(T + B) / 2}" class="tick" text-anchor="middle" transform="rotate(-90 16 ${(T + B) / 2})">U/U_n</text>`;
    const chk = M.frtCheck(f, u, isFinite(tclr) ? tclr : 10);
    const uvTrip = u < RG.Uset && (!isFinite(tclr) || tclr >= RG.tUset);
    const msg = chk.mustStay ? (uvTrip ? t("CONFLICT: profilul cere să rămână conectată, dar U< declanșează.", "CONFLICT: the profile requires staying connected, but U< trips.") : t("Golul e deasupra profilului: centrala trebuie să rămână conectată (U< nu declanșează).", "The dip is above the profile: the plant must stay connected (U< does not trip).")) : t(`Golul coboară sub profil la t = ${PR.fmt(chk.at, 2)} s: centrala are voie să se deconecteze. ${uvTrip ? "U< declanșează." : "U< nu declanșează: centrala rămâne conectată și alimentează defectul."}`, `The dip falls below the profile at t = ${PR.fmt(chk.at, 2)} s: the plant may disconnect. ${uvTrip ? "U< trips." : "U< does not trip: the plant stays connected and feeds the fault."}`);
    document.getElementById("frt-note").innerHTML = `<b style="color:${chk.mustStay && uvTrip ? "var(--trip)" : "var(--ink)"}">${msg}</b>`;
    svg.setAttribute("viewBox", `0 0 760 ${B + 36}`);
    svg.innerHTML = s;
  }

  function drawIsland() {
    const svg = document.getElementById("isl");
    if (P.dg === "none") { svg.innerHTML = `<text x="380" y="140" class="lbl" text-anchor="middle">${t("Fără centrală nu există insulă.", "Without a plant there is no island.")}</text>`; return; }
    const is = M.island(P), nd = M.ndz(P);
    // panoul stâng: f(t)
    const L = 56, Rr = 390, T = 22, B = 236, tmax = Math.max(3, P.tRAR + 0.5);
    const fmin = 46.5, fmax = 53.5;
    const sx = (x) => L + ((Rr - L) * x) / tmax, sy = (f) => B - ((B - T) * (f - fmin)) / (fmax - fmin);
    let s = `<text x="${(L + Rr) / 2}" y="12" class="lbl" text-anchor="middle" font-weight="600">${t("Frecvența insulei", "Island frequency")}</text>`;
    [47, 48, 49, 50, 51, 52, 53].forEach((f) => (s += `<line x1="${L}" x2="${Rr}" y1="${sy(f)}" y2="${sy(f)}" class="grid"/><text x="${L - 6}" y="${sy(f) + 4}" class="tick" text-anchor="end">${f}</text>`));
    PR.niceTicks(0, tmax, 6).forEach((x) => (s += `<text x="${sx(x)}" y="${B + 15}" class="tick" text-anchor="middle">${PR.fmt(x, 1)}</text>`));
    [P.fmin, P.fmax].forEach((f) => (s += `<line x1="${L}" x2="${Rr}" y1="${sy(f)}" y2="${sy(f)}" stroke="var(--trip)" stroke-dasharray="5 3"/><text x="${Rr - 3}" y="${sy(f) + (f < 50 ? 14 : -5)}" class="tick" text-anchor="end" fill="var(--trip)">${f < 50 ? "f<" : "f>"} ${PR.fmt(f, 1)} Hz</text>`));
    const fEnd = 50 + is.rocof * tmax, tCut = is.rocof === 0 ? tmax : Math.min(tmax, ((is.rocof < 0 ? fmin : fmax) - 50) / is.rocof);
    s += `<line x1="${sx(0)}" y1="${sy(50)}" x2="${sx(tCut)}" y2="${sy(50 + is.rocof * tCut)}" stroke="var(--c5)" stroke-width="2.6"/>`;
    s += `<line x1="${sx(P.tRAR)}" x2="${sx(P.tRAR)}" y1="${T}" y2="${B}" stroke="var(--ink)" stroke-width="1.6"/><text x="${sx(P.tRAR) + 4}" y="${T + 10}" class="tick">${t("RAR", "reclose")} ${PR.fmt(P.tRAR, 1)} s</text>`;
    if (isFinite(is.tOff) && is.tOff <= tmax) s += `<line x1="${sx(is.tOff)}" x2="${sx(is.tOff)}" y1="${T}" y2="${B}" stroke="${is.beforeRAR ? "var(--ok)" : "var(--trip)"}" stroke-dasharray="4 3" stroke-width="1.6"/><text x="${sx(is.tOff) + 4}" y="${T + 26}" class="tick" fill="${is.beforeRAR ? "var(--ok)" : "var(--trip)"}">${t("deconectare", "disconnection")} ${PR.fmt(is.tOff, 2)} s</text>`;
    s += `<text x="${L}" y="${B + 32}" class="tick">RoCoF = ${PR.fmt(is.rocof, 2)} Hz/s · ${is.beforeRAR ? t("iese înainte de RAR", "trips before reclosing") : t("NU iese înainte de RAR", "does NOT trip before reclosing")}</text>`;
    void fEnd;
    // panoul drept: t_off(ΔP)
    const L2 = 452, R2 = 744, tl = (x) => Math.log10(Math.min(Math.max(x, 0.1), 100));
    const px = (d) => L2 + ((R2 - L2) * (d + 0.5)) / 1, py = (x) => B - ((B - T) * (tl(x) + 1)) / 3;
    s += `<text x="${(L2 + R2) / 2}" y="12" class="lbl" text-anchor="middle" font-weight="600">${t("Timpul de deconectare față de ΔP/S_rG", "Disconnection time versus ΔP/S_rG")}</text>`;
    [0.1, 1, 10, 100].forEach((x) => (s += `<line x1="${L2}" x2="${R2}" y1="${py(x)}" y2="${py(x)}" class="grid"/><text x="${L2 - 6}" y="${py(x) + 4}" class="tick" text-anchor="end">${PR.sig(x, 1)}</text>`));
    [-0.5, -0.25, 0, 0.25, 0.5].forEach((d) => (s += `<text x="${px(d)}" y="${B + 15}" class="tick" text-anchor="middle">${PR.fmt(d * 100, 0)} %</text>`));
    if (nd.lo < nd.hi) s += `<rect x="${px(Math.max(nd.lo, -0.5))}" y="${T}" width="${px(Math.min(nd.hi, 0.5)) - px(Math.max(nd.lo, -0.5))}" height="${B - T}" fill="var(--trip-bg)"/><text x="${px(0)}" y="${T + 12}" class="tick" text-anchor="middle" fill="var(--trip)">${t("zona nedetectată", "non-detection zone")}</text>`;
    s += `<polyline points="${nd.pts.map((q) => `${px(q.d).toFixed(1)},${py(isFinite(q.t) ? q.t : 100).toFixed(1)}`).join(" ")}" fill="none" stroke="var(--c5)" stroke-width="2.2"/>`;
    s += `<line x1="${L2}" x2="${R2}" y1="${py(P.tRAR)}" y2="${py(P.tRAR)}" stroke="var(--ink)" stroke-width="1.6"/><text x="${R2 - 3}" y="${py(P.tRAR) - 5}" class="tick" text-anchor="end">${t("pauza RAR", "dead time")}</text>`;
    const d0 = (P.PG - P.PL) / P.Sg;
    if (Math.abs(d0) <= 0.5) s += `<circle cx="${px(d0)}" cy="${py(isFinite(is.tOff) ? is.tOff : 100)}" r="5" fill="${is.beforeRAR ? "var(--ok)" : "var(--trip)"}" stroke="var(--surface)" stroke-width="1.5"/>`;
    s += `<text x="${R2}" y="${B + 32}" class="tick" text-anchor="end">ΔP/S_rG · ${t("zona", "zone")} ±${PR.fmt(nd.hi * 100, 1)} % = ±${PR.fmt(nd.hi * P.Sg, 2)} MW</text>`;
    s += `<text x="${L2 - 40}" y="${(T + B) / 2}" class="tick" text-anchor="middle" transform="rotate(-90 ${L2 - 40} ${(T + B) / 2})">t, s</text>`;
    svg.innerHTML = s;
  }

  /* ---------- reglaje ---------- */
  let lastSheet = null;
  function renderSheet() {
    const has = P.dg !== "none";
    const PRV = { ...P, rel: "rev" }, S0 = M.RELAYS, SR = M.settingsFor(PRV);
    const Ir = M.IrG(P);
    document.getElementById("sheet-meta").innerHTML = has ? bi(`${DG[P.dg].ro} ${PR.fmt(P.Sg, 1)} MVA la ${PR.fmt(P.xg, 1)} km pe F1`, `${DG[P.dg].en} ${PR.fmt(P.Sg, 1)} MVA at ${PR.fmt(P.xg, 1)} km on F1`) : bi("fără centrală", "no plant");
    // 1) date
    let d = "";
    if (P.dg === "sync") {
      const zb = (20 * 20) / P.Sg, zr = 0.07 * P.xd * zb, zx = (P.xd + P.ukT / 100) * zb, Ik = (1.1 * 20000) / S3 / Math.hypot(zr, zx);
      d = `I_rG = S_rG/(√3·U_n) = ${PR.fmt(P.Sg, 1)}/(√3·20) = ${PR.fmt(Ir, 1)} A\nZ_G = (0,07·${PR.fmt(P.xd, 2)} + j(${PR.fmt(P.xd, 2)} + ${PR.fmt(P.ukT / 100, 3)}))·20²/${PR.fmt(P.Sg, 1)} = ${PR.fmt(zr, 2)} + j${PR.fmt(zx, 2)} Ω\n${t("Contribuția la un defect 3F franc în punctul de racordare (c = 1,1)", "Contribution to a bolted 3F fault at the connection point (c = 1.1)")}: ${PR.fmt(Ik, 0)} A = ${PR.fmt(Ik / Ir, 2)}·I_rG`;
    } else if (P.dg === "inv") d = `I_rG = ${PR.fmt(P.Sg, 1)}/(√3·20) = ${PR.fmt(Ir, 1)} A\n${t("Contribuția (limitată de invertor)", "Contribution (limited by the inverter)")}: k·I_rG = ${PR.fmt(P.k, 2)}·${PR.fmt(Ir, 1)} = ${PR.fmt(P.k * Ir, 0)} A, ${t("numai secvență pozitivă", "positive sequence only")}`;
    else d = t("Fără centrală: reglajele M03 rămân valabile.", "No plant: the M03 settings remain valid.");
    d += `\nM03: R3 I> ${PR.fmt(S0.R3.Is, 0)} A, TMS ${PR.fmt(S0.R3.tms, 2)}, I>> ${PR.fmt(S0.R3.Ih, 0)} A · R4 I> ${PR.fmt(S0.R4.Is, 0)} A, TMS ${PR.fmt(S0.R4.tms, 2)} · R2 I> ${PR.fmt(S0.R2.Is, 0)} A, TMS ${PR.fmt(S0.R2.tms, 2)}, I>> ${PR.fmt(S0.R2.Ih, 0)} A / ${PR.fmt(S0.R2.th, 2)} s (IEC VI)`;
    document.getElementById("rg-data").textContent = d;

    // 2) regimul normal
    const n0 = M.normalCheck(P, S0), nR = M.normalCheck(P, SR);
    let h = `<tr><th>${bi("Releul", "Relay")}</th><th class="n">${bi("Sarcina (M03)", "Load (M03)")}</th><th class="n">${bi("Exportul centralei", "Plant export")}</th><th class="n">I_max</th><th class="n">${bi("Prag necesar", "Required pickup")}</th><th class="n">I&gt; M03</th><th class="n">I&gt; ${bi("revizuit", "revised")}</th><th class="n">TMS M03 → ${bi("revizuit", "revised")}</th><th class="n">I&gt;&gt; ${bi("revizuit", "revised")}</th></tr>`;
    ["R3", "R4"].forEach((k) => {
      const a0 = n0[k], aR = nR[k];
      h += `<tr><td>${k}</td><td class="n">${fA(a0.Iload)}</td><td class="n">${a0.exp > 0 ? fA(a0.exp) : "—"}</td><td class="n">${fA(a0.Imax)}</td><td class="n">${fA(a0.need)}</td><td class="n"><span class="${a0.ok ? "ok" : "bad"}">${fA(S0[k].Is)}</span></td><td class="n"><span class="${aR.ok ? "ok" : "bad"}">${fA(SR[k].Is)}</span></td><td class="n">${PR.fmt(S0[k].tms, 2)} → ${PR.fmt(SR[k].tms, 2)}</td><td class="n">${SR[k].Ih > 0 ? fA(SR[k].Ih) : "—"}</td></tr>`;
    });
    h += `<tr><td colspan="9" class="note">${bi("k_sig = 1,2, k_p = 1, k_rev = 0,95, pas de reglaj 0,01·I_n,TC (M03). Exportul trece prin R4 numai dacă centrala e după km 10.", "k_sig = 1.2, k_p = 1, k_rev = 0.95, setting step 0.01·I_n,CT (M03). The export flows through R4 only if the plant is beyond km 10.")}</td></tr>`;
    document.getElementById("rg-norm").innerHTML = has ? h : `<tr><td>${bi("Fără centrală: nu există export.", "No plant: no export.")}</td></tr>`;

    // 3) orbire: toate pozițiile centralei, reglaje revizuite
    const pos = [1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20];
    const r0 = M.compute({ ...P, dg: "none", fault: "F1", xf: 20, type: "2F", kase: "min", Rf: 0 });
    const t0 = M.times(r0);
    let worst = null;
    h = `<tr><th>${bi("Poziția centralei", "Plant position")}</th><th class="n">I_R3 (2F min, 20 km)</th><th class="n">${bi("față de fără centrală", "vs. no plant")}</th><th class="n">I&gt; R3</th><th class="n">k<sub>sens</sub></th><th class="n">t_R3</th><th class="n">t_R4</th><th class="n">t_R3 − t_R4</th></tr>`;
    if (has) pos.forEach((xg) => {
      const pp = { ...PRV, xg }, S = M.settingsFor(pp);
      const r = M.compute({ ...pp, fault: "F1", xf: 20, type: "2F", kase: "min", Rf: 0 }), tt = M.times(r);
      const k = r.IR3 / S.R3.Is;
      if (!worst || k < worst.k) worst = { xg, k, r, tt };
      const ok = k >= RG.kSensB, okm = tt.R3 - tt.R4 >= RG.cti - 1e-9;
      h += `<tr${xg === P.xg ? ' class="res"' : ""}><td>${PR.fmt(xg, 0)} km</td><td class="n">${fA(r.IR3)}</td><td class="n">${PR.fmt((100 * (r.IR3 - r0.IR3)) / r0.IR3, 1)} %</td><td class="n">${fA(S.R3.Is)}</td><td class="n"><span class="${ok ? "ok" : "bad"}">${PR.fmt(k, 2)}</span></td><td class="n">${fs(tt.R3)}</td><td class="n">${fs(tt.R4)}</td><td class="n"><span class="${okm ? "ok" : "bad"}">${PR.fmt(tt.R3 - tt.R4, 2)} s</span></td></tr>`;
    });
    h += `<tr class="res"><td>${bi("fără centrală", "no plant")}</td><td class="n">${fA(r0.IR3)}</td><td class="n">—</td><td class="n">${fA(S0.R3.Is)}</td><td class="n">${PR.fmt(r0.IR3 / S0.R3.Is, 2)}</td><td class="n">${fs(t0.R3)}</td><td class="n">${fs(t0.R4)}</td><td class="n">${PR.fmt(t0.R3 - t0.R4, 2)} s</td></tr>`;
    document.getElementById("rg-blind").innerHTML = h;
    document.getElementById("rg-blind-note").innerHTML = `<b class="k">${bi("Interpretare", "Interpretation")}</b>` + (!has ? bi("Fără centrală nu există orbire.", "Without a plant there is no blinding.") : worst.k >= RG.kSensB ? bi(`Cel mai defavorabil: centrala la ${PR.fmt(worst.xg, 0)} km, k<sub>sens</sub> = ${PR.fmt(worst.k, 2)} ≥ ${PR.fmt(RG.kSensB, 1)}: R3 rămâne rezervă sensibilă pentru R4. Timpul de rezervă devine ${fs(worst.tt.R3)} (fără centrală ${fs(t0.R3)}).`, `Worst case: plant at ${PR.fmt(worst.xg, 0)} km, k<sub>sens</sub> = ${PR.fmt(worst.k, 2)} ≥ ${PR.fmt(RG.kSensB, 1)}: R3 remains a sensitive backup for R4. The backup time becomes ${fs(worst.tt.R3)} (without the plant ${fs(t0.R3)}).`) : bi(`Centrala la ${PR.fmt(worst.xg, 0)} km reduce k<sub>sens</sub> la ${PR.fmt(worst.k, 2)} &lt; ${PR.fmt(RG.kSensB, 1)}: R3 nu mai e rezervă sigură. Soluții: o treaptă de rezervă la R4 sau teleprotecție; pragul lui R3 nu poate coborî sub exportul centralei.`, `A plant at ${PR.fmt(worst.xg, 0)} km reduces k<sub>sens</sub> to ${PR.fmt(worst.k, 2)} &lt; ${PR.fmt(RG.kSensB, 1)}: R3 is no longer a reliable backup. Remedies: a backup stage at R4 or teleprotection; the R3 pickup cannot go below the plant export.`)) + (P.dg === "inv" ? " " + bi("La invertor, curentul văzut de R3 la defectele 2F poate chiar să crească: invertorul nu dă secvență negativă.", "With an inverter, the current seen by R3 for 2F faults may even increase: the inverter supplies no negative sequence.") : "");

    // 4) declanșarea simpatică, pe fiecare plecare vecină, cu reglajele revizuite
    h = `<tr><th>${bi("Plecarea vecină", "Adjacent feeder")}</th><th class="n">${bi("I invers max R3 / R4", "Max reverse I R3 / R4")}</th><th>${bi("Cazul cel mai strâns", "Tightest case")}</th><th class="n">${bi("t releu F1", "F1 relay t")}</th><th class="n">t_A</th><th class="n">${bi("Marja", "Margin")}</th><th>67 R3</th></tr>`;
    const sres = {};
    let anyBad = false, wrong67 = 0;
    Object.keys(M.ADJ).forEach((id) => {
      const s2 = has ? M.sympathetic({ ...PRV, adj: id }, RG.cti) : null;
      sres[id] = s2;
      if (!s2) return;
      const w = s2.worst;
      if (!s2.ok) anyBad = true;
      const w67 = s2.rows.filter((x) => x.trip67).length;
      wrong67 += w67;
      h += `<tr${id === P.adj ? ' class="res"' : ""}><td>${t(ADJN(id))} · TMS ${PR.fmt(P.tmsA, 2)}${P.IhA ? "" : ", " + t("fără I>>", "no I>>")}</td><td class="n">${fA(s2.maxRev)} / ${s2.maxRev4 > 0.5 ? fA(s2.maxRev4) : "—"}</td><td>${w ? `${w.relay}: ${w.type} ${w.kase}, ${PR.fmt(w.x, 1)} km` : t("niciun releu nu pornește", "no relay picks up")}</td><td class="n">${w ? fs(w.tRel) : "—"}</td><td class="n">${w ? fs(w.tA) : "—"}</td><td class="n">${w ? `<span class="${s2.ok ? "ok" : "bad"}">${PR.fmt(w.margin, 2)} s</span>` : `<span class="ok">—</span>`}</td><td>${w67 ? `<span class="warn">${t(`nesigur (${w67})`, `unreliable (${w67})`)}</span>` : t("blochează", "blocks")}</td></tr>`;
    });
    if (has) {
      const b3 = sres[P.adj].bus.reduce((a, b) => (b.IR3 > a.IR3 ? b : a));
      const tb = Math.min(b3.tR3, b3.tR4);
      h += `<tr><td>${bi("Barele de 20 kV", "20 kV busbar")}</td><td class="n">${fA(b3.IR3)} / ${b3.IR4 > 0.5 ? fA(b3.IR4) : "—"}</td><td>${b3.type} ${b3.kase}</td><td class="n">${fs(tb)}</td><td class="n">R2 ${fs(b3.tR2)}</td><td colspan="2">${t("declanșarea e utilă aici", "a trip is useful here")}</td></tr>`;
    }
    document.getElementById("rg-symp").innerHTML = has ? h : `<tr><td>${bi("Fără centrală, R3 și R4 nu văd curent invers.", "Without a plant, R3 and R4 see no reverse current.")}</td></tr>`;
    const allRev = has ? Math.max(...Object.values(sres).map((x) => x.maxRev)) : 0;
    document.getElementById("rg-symp-note").innerHTML = `<b class="k">${bi("Recomandare", "Recommendation")}</b>` + (!has ? bi("Nimic de verificat.", "Nothing to check.") : !anyBad && !Object.values(sres).some((x) => x.pickup) ? bi(`Curentul invers maxim (${fA(allRev)}) rămâne sub pragurile de pornire: releele pot rămâne nedirecționale.`, `The maximum reverse current (${fA(allRev)}) stays below the pickup thresholds: the relays may stay non-directional.`) : anyBad ? bi(`Un releu nedirecțional de pe F1 nu e selectiv față de cel puțin o plecare vecină. Se trece releul respectiv pe 67 (direcțional „înainte”, θ<sub>c</sub> = 30°, M04)${wrong67 ? `; la invertor, decizia direcțională a lui R3 e însă nesigură în ${wrong67} cazuri, deci se preferă o temporizare sau un prag mai mare, cu reverificarea sensibilității` : ""}. Pentru defectele pe bare: declanșare transmisă de la protecția barelor.`, `A non-directional F1 relay is not selective against at least one adjacent feeder. That relay is changed to 67 (directional forward, θ<sub>c</sub> = 30°, M04)${wrong67 ? `; with an inverter, however, the R3 directional decision is unreliable in ${wrong67} cases, so a longer delay or higher pickup is preferred, rechecking sensitivity` : ""}. For busbar faults: a transfer trip from the busbar protection.`) : bi(`Releele de pe F1 pornesc la defecte pe plecările vecine, dar sunt mai lente cu cel puțin Δt = ${PR.fmt(RG.cti, 2)} s: selectivitatea depinde de reglajele plecărilor vecine. La orice modificare a lor (TMS mai mare, I&gt;&gt; scos), verificarea se reface.`, `The F1 relays pick up for faults on the adjacent feeders, but are slower by at least Δt = ${PR.fmt(RG.cti, 2)} s: selectivity depends on the adjacent feeder settings. Any change to them (higher TMS, I&gt;&gt; removed) requires a new check.`));

    // 5) protecția de interfață
    const f = has ? P.frt[P.dg] : P.frt.sync;
    const uv = M.underVoltageCompat(f, RG.Uset, RG.tUset);
    const isl = M.island(P), nd = M.ndz(P);
    const SRC_A = t("Ord. ANRE 132/2020 (prosumatori), exemplu", "ANRE Order 132/2020 (prosumers), example");
    const rowsI = [
      ["27 U<", `${PR.fmt(RG.Uset, 2)}·U_n`, `${PR.fmt(RG.tUset, 2)} s`, SRC_A, uv.ok ? `<span class="ok">${t(`compatibil FRT: D = ${PR.fmt(uv.D, 2)} s < t`, `FRT-compatible: D = ${PR.fmt(uv.D, 2)} s < t`)}</span>` : `<span class="bad">${isFinite(uv.D) ? t(`incompatibil FRT: D = ${PR.fmt(uv.D, 2)} s ≥ t`, `FRT conflict: D = ${PR.fmt(uv.D, 2)} s ≥ t`) : t("incompatibil FRT: U_set > U_rec2", "FRT conflict: U_set > U_rec2")}</span>`],
      ["59 U>", `${PR.fmt(RG.Uov, 2)}·U_n`, `${PR.fmt(RG.tUov, 2)} s`, SRC_A, "—"],
      ["59 U> (10 min)", "1,10·U_n", t("media pe 10 min", "10-min average"), SRC_A, "—"],
      ["81U f<", `${PR.fmt(P.fmin, 1)} Hz`, `${PR.fmt(P.tF, 2)} s`, SRC_A, `${t("insulă", "island")}: ${isFinite(isl.tFreq) ? fs(isl.tFreq) : "—"}`],
      ["81O f>", `${PR.fmt(P.fmax, 1)} Hz`, `${PR.fmt(P.tF, 2)} s`, SRC_A, "—"],
      ["81R RoCoF", `${PR.fmt(P.rocof, 2)} Hz/s`, `${PR.fmt(P.tRocof, 2)} s`, t("G59 revizuit / G99 (Marea Britanie), exemplu", "revised G59 / G99 (Great Britain), example"), `${t("zona nedetectată", "non-detection zone")} ±${PR.fmt(nd.dRoc * 100, 1)} % S_rG`],
    ];
    h = `<tr><th>${bi("Funcția", "Function")}</th><th class="n">${bi("Prag", "Pickup")}</th><th class="n">${bi("Temporizare", "Delay")}</th><th>${bi("Sursa valorii", "Value source")}</th><th>${bi("Verificare", "Check")}</th></tr>` + rowsI.map((x) => `<tr><td class="mono">${x[0]}</td><td class="n">${x[1]}</td><td class="n">${x[2]}</td><td>${x[3]}</td><td>${x[4]}</td></tr>`).join("");
    document.getElementById("rg-ifp").innerHTML = h;
    const r = M.compute(PRV), c = M.clearing(r);
    let fr = `${t("Profilul", "Profile")} ${P.dg === "inv" ? "PPM" : t("sincron", "synchronous")}: U_ret ${PR.fmt(f.Uret, 2)} → t_clear ${PR.fmt(f.tclr, 2)} s; U_clear ${PR.fmt(f.Uclr, 2)} → t_rec2 ${PR.fmt(f.trec2, 2)} s; U_rec2 ${PR.fmt(f.Urec2, 2)} ${t("la", "at")} t_rec3 ${PR.fmt(f.trec3, 2)} s\n`;
    if (isFinite(uv.D)) fr += `D(U_set = ${PR.fmt(RG.Uset, 2)}) = ${PR.fmt(uv.D, 2)} s ${uv.ok ? "<" : "≥"} t_set = ${PR.fmt(RG.tUset, 2)} s → ${uv.ok ? t("treapta U< nu deconectează centrala pe marginea profilului", "the U< stage does not trip the plant along the profile edge") : t("treapta U< deconectează centrala la un gol pe care trebuie să-l suporte", "the U< stage trips the plant for a dip it must withstand")}\n`;
    if (has) { const ck = M.frtCheck(f, r.VLLg, isFinite(c.t) ? c.t : 10); fr += `${t("Defectul din laborator, reglaje revizuite", "Lab fault, revised settings")}: U = ${PR.fmt(r.VLLg, 2)} u.r. ${t("până la", "until")} t_clr = ${fs(c.t)} → ${ck.mustStay ? t("trebuie să rămână conectată", "must stay connected") : t(`sub profil la ${PR.fmt(ck.at, 2)} s (poate ieși)`, `below the profile at ${PR.fmt(ck.at, 2)} s (may trip)`)}`; }
    document.getElementById("rg-frt").textContent = fr;

    // 6) insularizarea
    const tw = P.tRAR - P.tcb - P.tF;
    let il = `RoCoF = (P_G − P_L)/S_rG · f0/(2H) = (${PR.fmt(P.PG, 2)} − ${PR.fmt(P.PL, 2)})/${PR.fmt(P.Sg, 1)} · 50/(2·${PR.fmt(P.H, 1)}) = ${PR.fmt(isl.rocof, 3)} Hz/s\n`;
    il += `81R: ${Math.abs(isl.rocof) >= P.rocof ? `|RoCoF| ≥ ${PR.fmt(P.rocof, 2)} → t = ${PR.fmt(P.tRocof, 2)} s` : `|RoCoF| < ${PR.fmt(P.rocof, 2)} → ${t("nu pornește", "no pickup")}`}\n`;
    il += `81U/81O: ${isFinite(isl.tFreq) ? `t = Δf/|RoCoF| + t_f = ${PR.fmt(isl.tFreq, 2)} s` : t("frecvența nu se modifică", "frequency does not change")}\n`;
    il += `${t("Deconectare", "Disconnection")}: t_det + t_CB = ${isFinite(isl.tOff) ? PR.fmt(isl.tOff, 2) : "∞"} s ${isl.beforeRAR ? "<" : "≥"} t_RAR = ${PR.fmt(P.tRAR, 2)} s\n`;
    il += `${t("Zona nedetectată", "Non-detection zone")}: |ΔP|/S_rG < min(2H·RoCoF>/f0 = ${PR.fmt(nd.dRoc, 3)}${tw > 0 ? `; 2H·Δf/(f0·(t_RAR − t_CB − t_f)) = ${PR.fmt((2 * P.H * (50 - P.fmin)) / (50 * tw), 3)}` : ""}) → ±${PR.fmt(nd.hi * P.Sg, 2)} MW`;
    document.getElementById("rg-isl").textContent = has ? il : t("Fără centrală.", "No plant.");
    document.getElementById("rg-isl-note").innerHTML = `<b class="k">${bi("Interpretare", "Interpretation")}</b>` + (!has ? "—" : (isl.beforeRAR ? bi("Pentru dezechilibrul din laborator, centrala iese înainte de reanclanșare.", "For the lab imbalance, the plant trips before reclosing.") : bi("Pentru dezechilibrul din laborator, centrala e încă conectată la reanclanșare: risc de reanclanșare în opoziție de fază.", "For the lab imbalance, the plant is still connected at reclosure: risk of out-of-phase reclosing.")) + " " + bi(`Oricum, pentru |ΔP| sub ${PR.fmt(nd.hi * P.Sg, 2)} MW protecțiile pasive nu văd insula în pauza RAR. Soluții: declanșare transmisă de la întrerupătorul liniei la centrală, pauză RAR mai lungă decât timpul de detecție, sau RAR condiționat de absența tensiunii pe linie.`, `In any case, for |ΔP| below ${PR.fmt(nd.hi * P.Sg, 2)} MW the passive protections do not see the island within the dead time. Remedies: a transfer trip from the line breaker to the plant, a dead time longer than the detection time, or reclosing conditioned on a dead line.`));

    // 7) fișa
    const symA = has ? sres[P.adj] : null;
    const needDir = has && anyBad ? (Object.values(sres).some((x) => !x.ok && x.worst.relay === "R4") ? ["R3", "R4"].filter((k) => Object.values(sres).some((x) => !x.ok && x.worst.relay === k)) : ["R3"]) : [];
    const rel = (k) => `I> ${PR.fmt(SR[k].Is, 0)} A, IEC VI, TMS ${PR.fmt(SR[k].tms, 2)}${SR[k].Ih > 0 ? `; I>> ${PR.fmt(SR[k].Ih, 0)} A${SR[k].th > 0 ? ` / ${PR.fmt(SR[k].th, 2)} s` : ""}` : ""}${needDir.includes(k) ? `; ${t("direcțional înainte", "directional forward")}, θc = 30°` : ""}`;
    const chg = (k) => (SR[k].Is !== S0[k].Is || SR[k].tms !== S0[k].tms ? t(`modificat (M03: I> ${PR.fmt(S0[k].Is, 0)} A, TMS ${PR.fmt(S0[k].tms, 2)})`, `changed (M03: I> ${PR.fmt(S0[k].Is, 0)} A, TMS ${PR.fmt(S0[k].tms, 2)})`) : t("ca în M03", "as in M03"));
    const rowsS = [
      ["R2 · " + t("sosirea T1", "T1 incomer"), "51 + 50", rel("R2"), chg("R2")],
      ["R3 · " + t("cap F1", "F1 head"), needDir.includes("R3") ? "67 + 50" : "51 + 50", rel("R3"), `${chg("R3")}${has && worst ? `; k_sens ${PR.fmt(worst.k, 2)}` : ""}`],
      ["R4 · F1 km 10", needDir.includes("R4") ? "67" : "51", rel("R4"), chg("R4")],
      [`${P.adj} · ${t("plecarea vecină", "adjacent feeder")}`, P.IhA ? "51 + 50" : "51", `I> ${PR.fmt(S0.R3.Is, 0)} A, IEC VI, TMS ${PR.fmt(P.tmsA, 2)}${P.IhA ? `; I>> ${PR.fmt(S0.R3.Ih, 0)} A` : ""}`, has ? (symA.ok ? t("selectiv față de F1", "selective against F1") : t("F1 neselectiv", "F1 not selective")) : "—"],
      [t("Centrala · interfață", "Plant · interface"), "27/59/81U/81O/81R", `U< ${PR.fmt(RG.Uset, 2)}·U_n/${PR.fmt(RG.tUset, 1)} s; U> ${PR.fmt(RG.Uov, 2)}·U_n/${PR.fmt(RG.tUov, 1)} s; f< ${PR.fmt(P.fmin, 1)} Hz, f> ${PR.fmt(P.fmax, 1)} Hz/${PR.fmt(P.tF, 1)} s; RoCoF ${PR.fmt(P.rocof, 2)} Hz/s/${PR.fmt(P.tRocof, 2)} s`, uv.ok ? t("compatibil FRT", "FRT-compatible") : t("conflict FRT", "FRT conflict")],
      [t("F1 · reanclanșare", "F1 · reclosing"), "79", `${t("pauza", "dead time")} ${PR.fmt(P.tRAR, 2)} s`, has ? (isl.beforeRAR ? `> t_det + t_CB = ${PR.fmt(isl.tOff, 2)} s` : t("centrala nu iese la timp", "the plant does not trip in time")) : "—"],
    ];
    lastSheet = rowsS;
    h = `<tr><th>${bi("Echipamentul", "Equipment")}</th><th>${bi("Funcția", "Function")}</th><th>${bi("Reglaje", "Settings")}</th><th>${bi("Verificare", "Check")}</th></tr>` + rowsS.map((x) => `<tr><td>${x[0]}</td><td class="mono">${x[1]}</td><td class="mono">${x[2]}</td><td>${x[3]}</td></tr>`).join("");
    document.getElementById("rg-sheet").innerHTML = h;
    document.getElementById("rg-cap").textContent = needDir.length ? t(`${needDir.join(", ")} devine direcțional (67)`, `${needDir.join(", ")} becomes directional (67)`) : t("Releele de pe F1 pot rămâne nedirecționale", "The F1 relays may stay non-directional");
  }
  document.getElementById("copy-sheet").addEventListener("click", (e) => {
    if (!lastSheet) return;
    PR.copyTSV([[t("echipament", "equipment"), t("functie", "function"), t("reglaje", "settings"), t("verificare", "check")]].concat(lastSheet), e.currentTarget);
  });

  /* ---------- test ---------- */
  const MCQ = [
    { q: { ro: "Ce înseamnă orbirea releului din capul liniei?", en: "What is blinding of the feeder-head relay?" }, o: [{ ro: "Centrala preia o parte din curentul de defect, iar releul vede mai puțin", en: "The plant supplies part of the fault current, so the relay sees less" }, { ro: "Releul nu are tensiune de polarizare", en: "The relay has no polarising voltage" }, { ro: "TC-ul se saturează", en: "The CT saturates" }, { ro: "Releul vede curent invers", en: "The relay sees reverse current" }], a: 0, e: { ro: "Relația (3): I_R3 = I_f − I_DG.", en: "Relation (3): I_R3 = I_f − I_DG." } },
    { q: { ro: "De ce poate declanșa R3 la un defect pe altă plecare?", en: "Why can R3 trip for a fault on another feeder?" }, o: [{ ro: "Centrala trimite curent prin R3 spre bare, iar un releu nedirecțional nu vede sensul", en: "The plant sends current through R3 towards the busbar, and a non-directional relay cannot see the direction" }, { ro: "Din cauza curentului de sarcină", en: "Because of load current" }, { ro: "Din cauza saturației TC", en: "Because of CT saturation" }, { ro: "Nu poate", en: "It cannot" }], a: 0, e: { ro: "Declanșarea simpatică, relația (4).", en: "Sympathetic tripping, relation (4)." } },
    { q: { ro: "Cu aceleași reglaje pe R3 și pe releul plecării vecine, cine e mai rapid la un defect pe plecarea vecină?", en: "With the same settings on R3 and on the adjacent feeder relay, which is faster for a fault on the adjacent feeder?" }, o: [{ ro: "Releul plecării vecine, pentru că vede tot curentul de defect", en: "The adjacent feeder relay, because it sees the whole fault current" }, { ro: "R3", en: "R3" }, { ro: "Sunt la fel", en: "They are equal" }, { ro: "Depinde numai de TC", en: "It depends only on the CT" }], a: 0, e: { ro: "R3 vede doar contribuția centralei; problema apare când plecarea vecină e reglată mai lent.", en: "R3 sees only the plant contribution; the problem appears when the adjacent feeder is set slower." } },
    { q: { ro: "Ce curent dă la defect o centrală cu invertor (Boutsika și Papathanassiou)?", en: "What current does an inverter-based plant give during a fault (Boutsika and Papathanassiou)?" }, o: [{ ro: "Aproximativ 1,5–2 ori curentul nominal", en: "About 1.5–2 times rated current" }, { ro: "4–5 ori curentul nominal", en: "4–5 times rated current" }, { ro: "Zero", en: "Zero" }, { ro: "Cât rețeaua", en: "As much as the grid" }], a: 0, e: { ro: "I″k = k·I_rG, k = 1,5–2.", en: "I″k = k·I_rG, k = 1.5–2." } },
    { q: { ro: "De ce poate crește curentul văzut de R3 la un defect 2F cu o centrală cu invertor după R3?", en: "Why can the current seen by R3 increase for a 2F fault with an inverter plant beyond R3?" }, o: [{ ro: "Invertorul nu dă secvență negativă, deci R3 duce tot curentul de secvență negativă, iar tensiunea la defect crește", en: "The inverter gives no negative sequence, so R3 carries all the negative-sequence current, while the fault voltage rises" }, { ro: "Invertorul dă curent invers", en: "The inverter gives reverse current" }, { ro: "Din cauza TC", en: "Because of the CT" }, { ro: "Nu poate crește", en: "It cannot increase" }], a: 0, e: { ro: "În rețeaua-exemplu, +7,9 % la capătul liniei.", en: "In the example network, +7.9 % at the line end." } },
    { q: { ro: "Ce cere profilul FRT din NC RfG?", en: "What does the NC RfG FRT profile require?" }, o: [{ ro: "Ca centrala să rămână conectată cât timp tensiunea e deasupra profilului", en: "That the plant stays connected while the voltage is above the profile" }, { ro: "Ca centrala să iasă la orice gol", en: "That the plant trips for any dip" }, { ro: "Ca releul liniei să fie direcțional", en: "That the line relay be directional" }, { ro: "Un anumit TMS", en: "A specific TMS" }], a: 0, e: { ro: "Art. 14(3)(a), tabelele 3.1 și 3.2.", en: "Art. 14(3)(a), Tables 3.1 and 3.2." } },
    { q: { ro: "Când e treapta U< compatibilă cu profilul FRT?", en: "When is the U< stage compatible with the FRT profile?" }, o: [{ ro: "Când t_set depășește timpul cât tensiunea poate sta sub U_set pe marginea profilului", en: "When t_set exceeds the time the voltage may stay below U_set along the profile edge" }, { ro: "Când U_set = 1", en: "When U_set = 1" }, { ro: "Întotdeauna", en: "Always" }, { ro: "Când t_set = 0", en: "When t_set = 0" }], a: 0, e: { ro: "Relația (5).", en: "Relation (5)." } },
    { q: { ro: "Cum depinde RoCoF-ul insulei de dezechilibrul de putere?", en: "How does island RoCoF depend on the power imbalance?" }, o: [{ ro: "Proporțional cu ΔP/S_rG și invers proporțional cu H", en: "Proportional to ΔP/S_rG and inversely proportional to H" }, { ro: "Nu depinde", en: "It does not" }, { ro: "Proporțional cu H", en: "Proportional to H" }, { ro: "Proporțional cu tensiunea", en: "Proportional to voltage" }], a: 0, e: { ro: "Relația (6).", en: "Relation (6)." } },
    { q: { ro: "Ce e zona nedetectată a unui releu RoCoF?", en: "What is the non-detection zone of a RoCoF relay?" }, o: [{ ro: "Dezechilibrele mici, pentru care |RoCoF| rămâne sub prag", en: "Small imbalances, for which |RoCoF| stays below the pickup" }, { ro: "Defectele departe de centrală", en: "Faults far from the plant" }, { ro: "Golurile scurte de tensiune", en: "Short voltage dips" }, { ro: "Zona din spatele releului", en: "The zone behind the relay" }], a: 0, e: { ro: "|ΔP|/S_rG < 2H·RoCoF>/f0.", en: "|ΔP|/S_rG < 2H·RoCoF>/f0." } },
    { q: { ro: "De ce trebuie centrala să iasă înainte de reanclanșarea liniei?", en: "Why must the plant trip before the line recloses?" }, o: [{ ro: "Ca reanclanșarea să nu se facă în opoziție de fază", en: "So the reclosure is not out of phase" }, { ro: "Ca să crească curentul de defect", en: "To increase the fault current" }, { ro: "Pentru măsurarea frecvenței", en: "For frequency measurement" }, { ro: "Nu trebuie", en: "It need not" }], a: 0, e: { ro: "Relația (7) și lucrarea SEL despre reanclanșarea în opoziție de fază.", en: "Relation (7) and the SEL paper on out-of-phase reclosing." } },
    { q: { ro: "La un defect pe barele de 20 kV, cu centrală pe F1, ce e de dorit pentru R3?", en: "For a 20 kV busbar fault, with a plant on F1, what is desirable for R3?" }, o: [{ ro: "Să declanșeze, ca centrala să nu mai alimenteze defectul", en: "To trip, so the plant stops feeding the fault" }, { ro: "Să rămână închis", en: "To stay closed" }, { ro: "Să se blocheze", en: "To be blocked" }, { ro: "Nu contează", en: "It does not matter" }], a: 0, e: { ro: "Cu R3 direcțional „înainte” e nevoie de declanșare transmisă de la protecția barelor.", en: "With R3 directional forward, a transfer trip from the busbar protection is needed." } },
    { q: { ro: "Ce rezistență fictivă atribuie IEC 60909-0 unui generator de 6,3 kV și 5 MVA?", en: "What fictitious resistance does IEC 60909-0 assign to a 6.3 kV, 5 MVA generator?" }, o: [{ ro: "0,07·X″d", en: "0.07·X″d" }, { ro: "0,05·X″d", en: "0.05·X″d" }, { ro: "0,15·X″d", en: "0.15·X″d" }, { ro: "Zero", en: "Zero" }], a: 0, e: { ro: "U_rG > 1 kV și S_rG < 100 MVA.", en: "U_rG > 1 kV and S_rG < 100 MVA." } },
    { q: { ro: "Ce reglaj RoCoF s-a adoptat în Marea Britanie după revizuirea G59 (și în G99)?", en: "What RoCoF setting was adopted in Great Britain after the G59 revision (and in G99)?" }, o: [{ ro: "1 Hz/s cu 0,5 s", en: "1 Hz/s with 0.5 s" }, { ro: "0,125 Hz/s instantaneu", en: "0.125 Hz/s instantaneous" }, { ro: "5 Hz/s", en: "5 Hz/s" }, { ro: "Salt de vector", en: "Vector shift" }], a: 0, e: { ro: "Pragurile de 0,125 Hz/s erau prea sensibile, iar saltul de vector a fost scos.", en: "0.125 Hz/s settings were too sensitive, and vector shift was removed." } },
  ];
  function NUM() {
    const dP = PR.rnd(0.2, 1.5, 0.1), S = PR.pick([2, 4, 5, 8]), H = PR.pick([1, 1.5, 2, 3]), k = PR.pick([1.2, 1.5, 2]), xd = PR.pick([0.15, 0.18, 0.2]), uk = PR.pick([6, 7, 8]), R = PR.pick([0.5, 1, 1.5]);
    const zb = 400 / S;
    return [
      { q: { ro: `Insulă cu S_rG = ${S} MVA, H = ${PR.fmt(H, 1)} s și un deficit de putere de ${PR.fmt(dP, 1)} MW. Ce |RoCoF| apare (Hz/s)?`, en: `Island with S_rG = ${S} MVA, H = ${PR.fmt(H, 1)} s and a ${PR.fmt(dP, 1)} MW power deficit. What |RoCoF| results (Hz/s)?` }, u: "Hz/s", v: (dP / S) * (50 / (2 * H)), e: { ro: "Relația (6).", en: "Relation (6)." } },
      { q: { ro: `Releu RoCoF reglat la ${PR.fmt(R, 1)} Hz/s, centrală cu H = ${PR.fmt(H, 1)} s. Până la ce dezechilibru |ΔP|/S_rG (în %) nu vede insula?`, en: `RoCoF relay set to ${PR.fmt(R, 1)} Hz/s, plant with H = ${PR.fmt(H, 1)} s. Up to what imbalance |ΔP|/S_rG (in %) does it miss the island?` }, u: "%", v: (100 * 2 * H * R) / 50, e: { ro: "2H·RoCoF>/f0.", en: "2H·RoCoF>/f0." } },
      { q: { ro: `Ce curent dă la defect o centrală cu invertor de ${S} MVA pe 20 kV, cu k = ${PR.fmt(k, 1)}?`, en: `What fault current does a ${S} MVA inverter plant at 20 kV give, with k = ${PR.fmt(k, 1)}?` }, u: "A", v: (k * S * 1e6) / (S3 * 20000), e: { ro: "k·S_rG/(√3·U_n).", en: "k·S_rG/(√3·U_n)." } },
      { q: { ro: `Generator de ${S} MVA cu x″d = ${PR.fmt(xd, 2)} și transformator bloc cu u_k = ${uk} %. Ce curent dă la un defect 3F franc în punctul de racordare de 20 kV (c = 1,1, R_Gf = 0,07·X″d)?`, en: `A ${S} MVA generator with x″d = ${PR.fmt(xd, 2)} and a unit transformer with u_k = ${uk} %. What current does it give for a bolted 3F fault at the 20 kV connection point (c = 1.1, R_Gf = 0.07·X″d)?` }, u: "A", v: (1.1 * 20000) / S3 / Math.hypot(0.07 * xd * zb, (xd + uk / 100) * zb), e: { ro: "Relația (1).", en: "Relation (1)." } },
    ];
  }

  /* ---------- pornire ---------- */
  ctl = PR.controls(document.getElementById("controls"), SCHEMA, P, onChange);
  const RGS = [{ g: { ro: "Verificări", en: "Checks" }, open: true, items: [
    { k: "kSensB", l: { ro: "k_sens de rezervă pentru R3", en: "R3 backup k_sens" }, u: "–", step: 0.05 },
    { k: "cti", l: { ro: "Marja de coordonare Δt", en: "Coordination margin Δt" }, u: "s", step: 0.05 },
  ] }, { g: { ro: "Protecția de interfață (tensiune)", en: "Interface protection (voltage)" }, open: true, items: [
    { k: "Uset", l: { ro: "U< (din U_n)", en: "U< (of U_n)" }, u: "–", step: 0.01 },
    { k: "tUset", l: { ro: "Temporizarea U<", en: "U< delay" }, u: "s", step: 0.1 },
    { k: "Uov", l: { ro: "U> (din U_n)", en: "U> (of U_n)" }, u: "–", step: 0.01 },
    { k: "tUov", l: { ro: "Temporizarea U>", en: "U> delay" }, u: "s", step: 0.1 },
  ] }];
  document.getElementById("rg-inputs").innerHTML = `<div class="panel" id="rg-a"></div><div class="panel" id="rg-b"></div><div class="panel" id="rg-c"></div>`;
  rgCtlA = PR.controls(document.getElementById("rg-a"), [RGS[0]], RG, () => render());
  rgCtlB = PR.controls(document.getElementById("rg-b"), [RGS[1]], RG, () => render());
  rgCtlC = PR.controls(document.getElementById("rg-c"), [{ g: { ro: "Frecvență și RAR", en: "Frequency and reclosing" }, open: true, items: [
    { k: "fmin", l: { ro: "f<", en: "f<" }, u: "Hz", step: 0.1 },
    { k: "fmax", l: { ro: "f>", en: "f>" }, u: "Hz", step: 0.1 },
    { k: "tF", l: { ro: "Temporizarea f< / f>", en: "f< / f> delay" }, u: "s", step: 0.05 },
    { k: "tcb", l: { ro: "Timpul întrerupătorului t_CB", en: "Breaker time t_CB" }, u: "s", step: 0.01 },
  ] }], P, () => { syncAll(); render(); });
  buildButtons(); visKnobs();
  render();
  PR.onLang(render);
  PR.math();
  PR.tabs(["lab", "reglaje", "teorie", "test"], "lab");
  PR.quiz(document.getElementById("qlist"), document.getElementById("score"), document.getElementById("q-reset"), { mcq: MCQ, num: NUM, pick: 8 });
})();
