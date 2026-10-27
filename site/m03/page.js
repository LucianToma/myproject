/* Modulul 03 — interfața paginii. Calculele sunt în engine.js (M03) și ../m01/engine.js (curenții de defect). */
(function () {
  "use strict";
  const M = window.M03, F1 = window.M01, PR = window.PR;
  const bi = PR.bi, t = PR.t;
  const clone = (o) => JSON.parse(JSON.stringify(o));

  const NET = { ...F1.DEFAULTS };
  const D = clone(M.DEFAULTS);
  let AUTO = M.autoSettings(NET, D);
  let S = clone(AUTO.S);
  const UI = { x: 15, bus: false, type: "3F", kase: "max" };
  const RL = M.ORDER;                                   // R4, R3, R2, R1
  const COL = { R4: "var(--c4)", R3: "var(--c1)", R2: "var(--c3)", R1: "var(--c5)" };
  const NAME = {
    R4: { ro: "R4 · punct de secționare km 10", en: "R4 · sectionaliser at km 10" },
    R3: { ro: "R3 · plecarea F1", en: "R3 · feeder F1" },
    R2: { ro: "R2 · sosire 20 kV", en: "R2 · 20 kV incomer" },
    R1: { ro: "R1 · T1 pe 110 kV", en: "R1 · T1 on 110 kV" },
  };
  const kHV = () => NET.UrLV / NET.UrHV;
  const fA = (I) => (I >= 10000 ? `${PR.fmt(I / 1000, 2)} kA` : `${PR.fmt(I, I >= 100 ? 0 : 1)} A`);
  const fs = (x) => (isFinite(x) ? `${PR.fmt(x, x < 1 ? 3 : 2)} s` : "—");
  const CURSEL = Object.entries(M.CURVES).map(([k, v]) => [k, { ro: v.ro, en: v.en }]);

  /* ---------- controale laborator (stare plată sincronizată cu S) ---------- */
  const FS = {};
  const toFlat = () => RL.forEach((r) => ["curve", "Is", "tms", "Ih", "th"].forEach((k) => (FS[r + "_" + k] = S[r][k])));
  const fromFlat = () => RL.forEach((r) => ["curve", "Is", "tms", "Ih", "th"].forEach((k) => (S[r][k] = FS[r + "_" + k])));
  toFlat();
  const SCHEMA = RL.map((r, i) => ({ g: NAME[r], col: { R4: "--c4", R3: "--c1", R2: "--c3", R1: "--c5" }[r], open: i === 1, openNarrow: false, items: [
    { k: r + "_curve", l: { ro: "Caracteristica I>", en: "I> characteristic" }, sel: CURSEL, wide: true },
    { k: r + "_Is", l: { ro: "Pragul I> (primar)", en: "I> pickup (primary)" }, u: r === "R1" ? "A, 110 kV" : "A", step: 1 },
    { k: r + "_tms", l: { ro: "TMS (DT: timpul, s)", en: "TMS (DT: time, s)" }, u: "–", step: 0.01, range: [0.05, 1] },
    { k: r + "_Ih", l: { ro: "Pragul I>> (0 = oprit)", en: "I>> pickup (0 = off)" }, u: r === "R1" ? "A, 110 kV" : "A", step: 5 },
    { k: r + "_th", l: { ro: "Temporizarea t>>", en: "Delay t>>" }, u: "s", step: 0.01 },
  ] }));
  const PSCHEMA = [{ g: { ro: "Locul defectului de probă", en: "Probe fault location" }, open: true, items: [
    { k: "x", l: { ro: "Distanța pe plecarea F1", en: "Distance along feeder F1" }, u: "km", step: 0.1, range: [0, NET.L] },
    { k: "bus", l: { ro: "Defect pe barele de 20 kV", en: "Fault on the 20 kV busbar" }, chk: true },
  ] }];

  const PRESETS = [
    [{ ro: "Reglajele calculate (fișa de reglaje)", en: "Computed settings (settings sheet)" }, () => { AUTO = M.autoSettings(NET, D); S = clone(AUTO.S); }],
    [{ ro: "Toate curbele IEC SI", en: "All curves IEC SI" }, () => { const d = clone(D); RL.forEach((r) => (d[r].curve = "IEC-SI")); S = clone(M.autoSettings(NET, d).S); }],
    [{ ro: "Toate curbele IEC EI", en: "All curves IEC EI" }, () => { const d = clone(D); RL.forEach((r) => (d[r].curve = "IEC-EI")); S = clone(M.autoSettings(NET, d).S); }],
    [{ ro: "R3 cu TMS = 0,05 (greșit)", en: "R3 with TMS = 0.05 (wrong)" }, () => { S.R3.tms = 0.05; }],
    [{ ro: "R1 fără eșalonarea pragului", en: "R1 without pickup grading" }, () => { S.R1.Is = Math.ceil((D.kSig * AUTO.rt.hv) / D.kRev / 2) * 2; }],
    [{ ro: "R3 fără treapta I>>", en: "R3 without I>> stage" }, () => { S.R3.Ih = 0; }],
  ];

  let ctl, pctl;
  function onLab(k) { fromFlat(); UI.x = FS.x; UI.bus = FS.bus; renderLab(); }
  FS.x = UI.x; FS.bus = UI.bus;

  function buildButtons() {
    const pr = document.getElementById("presets");
    pr.innerHTML = PRESETS.map((x, i) => `<button class="btn" data-i="${i}">${bi(x[0])}</button>`).join("");
    pr.onclick = (e) => { const b = e.target.closest("[data-i]"); if (!b) return; PRESETS[+b.dataset.i][1](); toFlat(); ctl.sync(); renderLab(); };
    document.getElementById("ftype").innerHTML = ["3F", "2F"].map((f) => `<button class="btn" data-f="${f}">${f}</button>`).join("");
    document.getElementById("ftype").onclick = (e) => { const b = e.target.closest("[data-f]"); if (!b) return; UI.type = b.dataset.f; syncBtn(); renderLab(); };
    document.getElementById("fcase").innerHTML = `<button class="btn" data-c="max">${bi("Regim maxim", "Maximum case")}</button><button class="btn" data-c="min">${bi("Regim minim", "Minimum case")}</button>`;
    document.getElementById("fcase").onclick = (e) => { const b = e.target.closest("[data-c]"); if (!b) return; UI.kase = b.dataset.c; syncBtn(); renderLab(); };
  }
  function syncBtn() {
    document.querySelectorAll("#ftype [data-f]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.f === UI.type));
    document.querySelectorAll("#fcase [data-c]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.c === UI.kase));
  }

  /* ---------- laborator ---------- */
  function renderLab() {
    const co = M.coordination(NET, D, S);
    const probeLoc = UI.bus ? "B20" : UI.x;
    const who = M.whoTrips(NET, D, S, probeLoc, UI.type, UI.kase);
    const pairs = [["R4", "R3"], ["R3", "R2"], ["R2", "R1"]];
    const issues = [];
    pairs.forEach(([dn, up]) => {
      const c = co[dn + "-" + up];
      if (!c.marginOk) issues.push(bi(`marja ${dn}–${up} este ${PR.fmt(c.margin, 3)} s la ${fA(c.Idn)} (${c.type}), sub ${PR.fmt(D.cti, 2)} s`, `margin ${dn}–${up} is ${PR.fmt(c.margin, 3)} s at ${fA(c.Idn)} (${c.type}), below ${PR.fmt(D.cti, 2)} s`));
      if (!c.pickupOk) issues.push(bi(`pragul lui ${up}, raportat, e sub pragul lui ${dn}`, `${up}'s referred pickup is below ${dn}'s`));
    });
    const ok = !issues.length;
    document.getElementById("status").innerHTML = `<div class="status ${ok ? "ok" : "bad"}"><span class="led"></span><span class="pill">${ok ? t("SELECTIV", "SELECTIVE") : t("NESELECTIV", "NOT SELECTIVE")}</span><span class="msg">${ok ? bi(`Toate marjele sunt de cel puțin ${PR.fmt(D.cti, 2)} s și pragurile sunt eșalonate.`, `All margins are at least ${PR.fmt(D.cti, 2)} s and pickups are graded.`) : issues.join("; ") + "."}</span></div>`;
    const kp = pairs.map(([dn, up]) => { const c = co[dn + "-" + up]; return [bi(`Marja minimă ${dn}–${up}`, `Minimum margin ${dn}–${up}`), `<span style="color:var(${c.ok ? "--ok" : "--trip"})">${fs(c.margin)}</span>`]; });
    kp.push([bi("Defectul de probă", "Probe fault"), who.first ? `${who.first} <small>${fs(who.out[who.first].t)}</small>` : "—"]);
    document.getElementById("kpis").innerHTML = kp.map(([l, v]) => `<div><div class="label">${l}</div><div class="v">${v}</div></div>`).join("");
    drawTCC(who);
    drawWho(who);
    drawSetTable();
  }

  function drawTCC(who) {
    const W = 760, L = 66, R = 744, T = 16, B = 420;
    const I0 = 30, I1 = 30000, T0 = 0.01, T1 = 100;
    const xs = (I) => L + ((R - L) * Math.log10(I / I0)) / Math.log10(I1 / I0);
    const ys = (tt) => B - ((B - T) * Math.log10(tt / T0)) / Math.log10(T1 / T0);
    let s = "";
    for (let e = Math.log10(I0) | 0; e <= 5; e++) [1, 2, 5].forEach((m) => {
      const v = m * Math.pow(10, e); if (v < I0 || v > I1) return;
      s += `<line x1="${xs(v)}" x2="${xs(v)}" y1="${T}" y2="${B}" class="${m === 1 ? "grid" : "minor"}"/><text x="${xs(v)}" y="${B + 16}" class="tick" text-anchor="middle">${v >= 1000 ? PR.fmt(v / 1000, 0) + "k" : PR.fmt(v, 0)}</text>`;
    });
    for (let e = -2; e <= 2; e++) [1, 2, 5].forEach((m) => {
      const v = m * Math.pow(10, e); if (v < T0 || v > T1) return;
      s += `<line x1="${L}" x2="${R}" y1="${ys(v)}" y2="${ys(v)}" class="${m === 1 ? "grid" : "minor"}"/><text x="${L - 6}" y="${ys(v) + 4}" class="tick" text-anchor="end">${PR.fmt(v, v < 0.1 ? 2 : v < 1 ? 1 : 0)}</text>`;
    });
    s += `<rect x="${L}" y="${T}" width="${R - L}" height="${B - T}" fill="none" stroke="var(--ink)"/>`;
    s += `<text x="${R}" y="${B + 32}" class="tick" text-anchor="end">${t("curentul raportat la 20 kV, A", "current referred to 20 kV, A")}</text><text x="${L - 50}" y="${(T + B) / 2}" class="tick" text-anchor="middle" transform="rotate(-90 ${L - 50} ${(T + B) / 2})">${t("timp, s", "time, s")}</text>`;
    // repere de curent de defect
    const marks = [
      [F1.compute(NET, "max", "3F", 0, 0).Ik, t("3F max bare", "3F max bus")],
      [F1.compute(NET, "max", "3F", D.x4, 0).Ik, t("3F max la R4", "3F max at R4")],
      [F1.compute(NET, "max", "3F", NET.L, 0).Ik, t("3F max capăt", "3F max end")],
      [F1.compute(NET, "min", "2F", D.x4, 0).Ik, t("2F min la R4", "2F min at R4")],
      [F1.compute(NET, "min", "2F", NET.L, 0).Ik, t("2F min capăt", "2F min end")],
    ];
    // etichetele alternează sus/jos, ca să nu se suprapună când reperele sunt apropiate
    marks.sort((a, b) => a[0] - b[0]).forEach(([I, lab], i) => {
      const top = i % 2 === 0, yy = top ? T + 6 : B - 6;
      s += `<line x1="${xs(I)}" x2="${xs(I)}" y1="${T}" y2="${B}" stroke="var(--muted)" stroke-dasharray="2 4"/><text x="${xs(I) - 4}" y="${yy}" class="tick" text-anchor="${top ? "end" : "start"}" transform="rotate(-90 ${xs(I) - 4} ${yy})">${lab} ${fA(I)}</text>`;
    });
    // caracteristicile
    const maxI = { R4: F1.compute(NET, "max", "3F", D.x4, 0).Ik, R3: marks[0][0], R2: marks[0][0], R1: marks[0][0] };
    const curve = (r, factor, dash) => {
      const st = S[r]; if (!(st.Is > 0)) return "";
      const toLV = (Irel) => Irel / factor;           // curentul releului → curent raportat la 20 kV
      const lo = st.curve === "DT" ? st.Is : M.GT * st.Is;
      let pts = [];
      const Imin = toLV(lo), Imx = Math.min(maxI[r], I1);
      if (Imx <= Imin) return "";
      const n = 140;
      let xsI = [];
      for (let i = 0; i <= n; i++) xsI.push(Imin * Math.pow(Imx / Imin, i / n));
      if (st.Ih > 0) { const h = toLV(st.Ih); if (h > Imin && h < Imx) xsI.push(h * 0.99999, h); }
      xsI = xsI.sort((a, b) => a - b);
      xsI.forEach((I) => { const tt = M.tripTime(st, I * factor, D.tOwn).t; if (isFinite(tt)) pts.push([xs(I), ys(Math.min(Math.max(tt, T0), T1))]); });
      return `<polyline points="${pts.map((p) => p.map((v) => v.toFixed(1)).join(",")).join(" ")}" fill="none" stroke="${COL[r]}" stroke-width="2.4" ${dash ? 'stroke-dasharray="6 4"' : ""}/>`;
    };
    ["R4", "R3", "R2"].forEach((r) => (s += curve(r, 1)));
    s += curve("R1", kHV()) + curve("R1", (kHV() * 2) / Math.sqrt(3), true);
    // defectul de probă
    const s0 = who.s, Ilv = s0.R2;
    if (Ilv > I0) {
      s += `<line x1="${xs(Ilv)}" x2="${xs(Ilv)}" y1="${T}" y2="${B}" stroke="var(--trip)" stroke-width="1.5"/><text x="${xs(Ilv) + 4}" y="${B - 6}" class="tick" fill="var(--trip)">F ${fA(Ilv)}</text>`;
      RL.forEach((r) => { const o = who.out[r]; if (!isFinite(o.t) || o.t > T1) return; s += `<circle cx="${xs(Ilv)}" cy="${ys(Math.max(o.t, T0))}" r="${r === who.first ? 6 : 4.5}" fill="${COL[r]}" stroke="var(--surface)" stroke-width="1.5"/>`; });
    }
    // legendă
    // legendă pe două coloane
    const leg = RL.map((r) => [COL[r], t(NAME[r]), ""]).concat([[COL.R1, t("R1 la defect bifazat pe 20 kV", "R1 for a phase-to-phase fault on 20 kV"), "6 4"]]);
    leg.forEach(([c, txt, dash], i) => {
      const lx = L + (i % 2) * 330, ly = B + 50 + Math.floor(i / 2) * 18;
      s += `<line x1="${lx}" x2="${lx + 20}" y1="${ly}" y2="${ly}" stroke="${c}" stroke-width="3" ${dash ? `stroke-dasharray="${dash}"` : ""}/><text x="${lx + 26}" y="${ly + 4}" class="tick">${txt}</text>`;
    });
    document.getElementById("tcc").innerHTML = s;
  }

  function drawWho(who) {
    const order = RL.filter((r) => isFinite(who.out[r].t)).sort((a, b) => who.out[a].t - who.out[b].t);
    let h = `<tr><th>${bi("Releu", "Relay")}</th><th class="n">${bi("Curent văzut", "Current seen")}</th><th class="n">I/I&gt;</th><th>${bi("Treapta", "Stage")}</th><th class="n">${bi("Timp", "Time")}</th><th class="n">${bi("Ordine", "Order")}</th></tr>`;
    RL.forEach((r) => {
      const o = who.out[r], seenI = who.s[r];
      const idx = order.indexOf(r);
      h += `<tr class="${r === who.first ? "first" : ""}"><td><span class="relay-chip"><i style="background:${COL[r]}"></i>${t(NAME[r])}</span></td><td class="n">${seenI > 0 ? fA(seenI) + (r === "R1" ? " (110 kV)" : "") : "—"}</td><td class="n">${seenI > 0 ? PR.fmt(seenI / S[r].Is, 2) : "—"}</td><td>${seenI > 0 ? o.stage : bi("nu vede defectul", "does not see the fault")}</td><td class="n">${fs(o.t)}</td><td class="n">${idx >= 0 ? idx + 1 : "—"}</td></tr>`;
    });
    if (order.length > 1) h += `<tr class="res"><td colspan="4">${bi(`Marja dintre ${order[0]} și ${order[1]}`, `Margin between ${order[0]} and ${order[1]}`)}</td><td class="n">${fs(who.out[order[1]].t - who.out[order[0]].t)}</td><td></td></tr>`;
    document.getElementById("who").innerHTML = h;
  }

  function drawSetTable() {
    let h = `<tr><th>${bi("Releu", "Relay")}</th><th>${bi("Curba", "Curve")}</th><th class="n">I&gt; ${bi("primar", "primary")}</th><th class="n">I&gt;/I<sub>n TC</sub></th><th class="n">TMS</th><th class="n">I&gt;&gt; ${bi("primar", "primary")}</th><th class="n">t&gt;&gt;</th></tr>`;
    RL.forEach((r) => { const st = S[r]; h += `<tr><td><span class="relay-chip"><i style="background:${COL[r]}"></i>${r}</span></td><td>${t(M.CURVES[st.curve])}</td><td class="n">${fA(st.Is)}</td><td class="n">${PR.fmt(st.Is / D[r].ct, 2)}</td><td class="n">${PR.fmt(st.tms, 2)}</td><td class="n">${st.Ih > 0 ? fA(st.Ih) : "—"}</td><td class="n">${st.Ih > 0 ? (st.th > 0 ? fs(st.th) : t("0 s (instant.)", "0 s (instant.)")) : "—"}</td></tr>`; });
    document.getElementById("settab").innerHTML = h;
  }

  /* ---------- reglaje ---------- */
  const RG = {};
  const syncRGfromD = () => {
    ["kSig", "kRev", "kP", "kD", "kSensMain", "kSensBack", "tmsMin", "tOwn", "cti"].forEach((k) => (RG[k] = D[k]));
    const rt = M.ratedT1(NET);
    RL.forEach((r) => { RG[r + "_Iload"] = D[r].Iload ?? +((r === "R2" ? rt.lv : rt.hv).toFixed(1)); RG[r + "_ct"] = D[r].ct; RG[r + "_curve"] = D[r].curve; });
  };
  syncRGfromD();
  const RGS = {
    gen: [{ g: { ro: "Coeficienți și timpi", en: "Factors and times" }, open: true, items: [
      { k: "kSig", l: { ro: "k_sig, siguranță", en: "k_sig, safety" }, u: "–", step: 0.05 },
      { k: "kRev", l: { ro: "k_rev, revenire", en: "k_rev, reset ratio" }, u: "–", step: 0.01 },
      { k: "kP", l: { ro: "k_p, autopornire / sarcină rece", en: "k_p, self-start / cold load" }, u: "–", step: 0.1 },
      { k: "kD", l: { ro: "k_d, treapta rapidă", en: "k_d, high-set" }, u: "–", step: 0.05 },
      { k: "kSensMain", l: { ro: "k_sens zona de bază", en: "k_sens main zone" }, u: "–", step: 0.1 },
      { k: "kSensBack", l: { ro: "k_sens zona de rezervă", en: "k_sens backup zone" }, u: "–", step: 0.1 },
      { k: "cti", l: { ro: "Marja de coordonare Δt", en: "Coordination margin Δt" }, u: "s", step: 0.01 },
      { k: "tmsMin", l: { ro: "TMS minim al releului", en: "Relay minimum TMS" }, u: "–", step: 0.01 },
      { k: "tOwn", l: { ro: "Timpul propriu al releului", en: "Relay own time" }, u: "s", step: 0.01 },
    ] }],
  };
  RL.forEach((r) => (RGS[r] = [{ g: NAME[r], col: { R4: "--c4", R3: "--c1", R2: "--c3", R1: "--c5" }[r], open: true, items: [
    { k: r + "_Iload", l: { ro: "Curentul maxim de sarcină", en: "Maximum load current" }, u: r === "R1" ? "A, 110 kV" : "A", step: 1 },
    { k: r + "_ct", l: { ro: "Raportul TC (primar, /1 A)", en: "CT ratio (primary, /1 A)" }, u: "A", step: 5 },
    { k: r + "_curve", l: { ro: "Curba", en: "Curve" }, sel: CURSEL, wide: true },
  ] }]));
  function onRG() {
    ["kSig", "kRev", "kP", "kD", "kSensMain", "kSensBack", "tmsMin", "tOwn", "cti"].forEach((k) => (D[k] = RG[k]));
    RL.forEach((r) => { D[r].Iload = RG[r + "_Iload"]; D[r].ct = RG[r + "_ct"]; D[r].curve = RG[r + "_curve"]; });
    AUTO = M.autoSettings(NET, D);
    renderSheet();
  }

  function renderSheet() {
    const A = AUTO, S2 = A.S, rep = A.rep, rt = A.rt;
    document.getElementById("sheet-meta").innerHTML = bi(`Rețeaua M01 · T1 ${PR.fmt(NET.Sr, 0)} MVA, I_rT = ${PR.fmt(rt.hv, 1)} A / ${PR.fmt(rt.lv, 1)} A · Δt = ${PR.fmt(D.cti, 2)} s`, `M01 network · T1 ${PR.fmt(NET.Sr, 0)} MVA, I_rT = ${PR.fmt(rt.hv, 1)} A / ${PR.fmt(rt.lv, 1)} A · Δt = ${PR.fmt(D.cti, 2)} s`);
    // curenți de defect
    const c3 = (x) => F1.compute(NET, "max", "3F", x, 0), c2 = (x) => F1.compute(NET, "min", "2F", x, 0);
    const rowsF = [[t("Bare 20 kV / capul plecării", "20 kV bus / feeder head"), 0], [t("Locul lui R4", "R4 location"), D.x4], [t("Capătul liniei", "Line end"), NET.L]];
    let h = `<tr><th>${bi("Punct", "Point")}</th><th class="n">x (km)</th><th class="n">I″k3 max</th><th class="n">I″k2 min</th><th class="n">${bi("110 kV: 3F max", "110 kV: 3F max")}</th><th class="n">${bi("110 kV: 2F min", "110 kV: 2F min")}</th></tr>`;
    rowsF.forEach(([n, x]) => { h += `<tr><td>${n}</td><td class="n">${PR.fmt(x, 1)}</td><td class="n">${fA(c3(x).Ik)}</td><td class="n">${fA(c2(x).Ik)}</td><td class="n">${fA(Math.max(...c3(x).IhvMag))}</td><td class="n">${fA(Math.max(...c2(x).IhvMag))}</td></tr>`; });
    document.getElementById("rg-faults").innerHTML = h;
    // pornire
    const pk = RL.map((r) => {
      const R = rep[r];
      let line = `${r}: ${PR.fmt(D.kSig, 2)}·${PR.fmt(D.kP, 2)}·${PR.fmt(R.load, 1)} / ${PR.fmt(D.kRev, 2)} = ${PR.fmt(R.IsRaw, 1)} A`;
      if (R.grade && R.grade.applied) line += ` → ${t("eșalonare", "grading")}: ${PR.fmt(R.grade.need / R.grade.ratio, 0)} A · ${PR.fmt(R.grade.ratio, 4)} = ${PR.fmt(R.grade.need, 1)} A`;
      return line + ` → I> = ${PR.fmt(S2[r].Is, 0)} A (${t("pas", "step")} ${PR.fmt(D[r].ct * 0.01, 0)} A = 0,01·I_n)`;
    });
    document.getElementById("rg-pickup").textContent = pk.join("\n");
    // sensibilitate
    const sensRows = [
      ["R4", t("bază: capătul liniei", "main: line end"), rep.R4.sensMain],
      ["R3", t("bază: locul lui R4", "main: R4 location"), rep.R3.sensMain],
      ["R3", t("rezervă: capătul liniei", "backup: line end"), rep.R3.sensBack],
      ["R2", t("bază: barele 20 kV", "main: 20 kV bus"), rep.R2.sensMain],
      ["R2", t("rezervă: capătul liniei", "backup: line end"), rep.R2.sensBack],
      ["R1", t("rezervă: barele 20 kV (2F pe 110 kV)", "backup: 20 kV bus (2F on 110 kV)"), rep.R1.sensMain],
    ];
    h = `<tr><th>${bi("Releu", "Relay")}</th><th>${bi("Zona", "Zone")}</th><th class="n">I″k2 min</th><th class="n">I&gt;</th><th class="n">k<sub>sens</sub></th><th class="n">${bi("cerut", "required")}</th><th>${bi("Rezultat", "Result")}</th></tr>`;
    let backupFail = false;
    sensRows.forEach(([r, z, v]) => { const ok = v.k >= v.need - 1e-9; if (!ok && r === "R2") backupFail = true; h += `<tr><td class="mono">${r}</td><td>${z}</td><td class="n">${fA(v.I)}</td><td class="n">${fA(S2[r].Is)}</td><td class="n">${PR.fmt(v.k, 2)}</td><td class="n">≥ ${PR.fmt(v.need, 1)}</td><td><span class="${ok ? "ok" : "bad"}">${ok ? t("îndeplinit", "met") : t("neîndeplinit", "not met")}</span></td></tr>`; });
    document.getElementById("rg-sens").innerHTML = h;
    document.getElementById("rg-sens-note").innerHTML = `<b class="k">${bi("Interpretare", "Interpretation")}</b>` + (backupFail
      ? bi(`R2 nu poate fi rezervă pentru capătul plecării: pragul lui e legat de curentul nominal al transformatorului (${fA(rt.lv)}), iar defectul bifazat minim de la ${PR.fmt(NET.L, 0)} km dă doar ${fA(rep.R2.sensBack.I)}. Rezerva se asigură local: R3 vede capătul liniei cu k<sub>sens</sub> = ${PR.fmt(rep.R3.sensBack.k, 2)}, iar refuzul întrerupătorului e acoperit de DRRI (M09). Aceasta e situația obișnuită pe plecările lungi.`, `R2 cannot back up the far end of the feeder: its pickup is tied to the transformer rated current (${fA(rt.lv)}), and the minimum phase-to-phase fault at ${PR.fmt(NET.L, 0)} km gives only ${fA(rep.R2.sensBack.I)}. Backup is provided locally: R3 sees the line end with k<sub>sens</sub> = ${PR.fmt(rep.R3.sensBack.k, 2)}, and breaker failure is covered by the breaker-failure protection (M09). This is the usual situation on long feeders.`)
      : bi("Toate condițiile de sensibilitate sunt îndeplinite.", "All sensitivity conditions are met."));
    // trepte rapide
    const hi = [
      bi("R4: fără treaptă rapidă. Aval sunt posturi de transformare protejate cu siguranțe; coordonarea cu ele e în M06.", "R4: no high-set stage. Downstream are distribution substations protected by fuses; coordination with them is in M06."),
      `R3: I>> ≥ ${PR.fmt(D.kD, 2)} · ${fA(rep.R3.IhBase)} = ${fA(D.kD * rep.R3.IhBase)} → <b>${fA(S2.R3.Ih)}</b>, ${t("instantaneu", "instantaneous")}. ${t("Acoperă", "Covers")} ${PR.fmt(rep.R3.reach, 1)} km ${t("în regim maxim (3F) și", "in the maximum case (3F) and")} ${PR.fmt(rep.R3.reachMin, 1)} km ${t("în regim minim (2F), din cei", "in the minimum case (2F), out of the")} ${PR.fmt(D.x4, 0)} km ${t("până la R4", "up to R4")}.`,
      `R2: I>> = max(${fA(rep.R2.IhBase)} / ${PR.fmt(D.kSensMain, 1)}; ${t("pragul I>> al lui R3", "R3's I>> pickup")}) = <b>${fA(S2.R2.Ih)}</b>, t>> = ${PR.fmt(Math.max(S2.R3.th, D.tOwn), 2)} + ${PR.fmt(D.cti, 2)} = <b>${fs(S2.R2.th)}</b>. ${t("Protejează rapid barele de 20 kV, temporizat după treapta rapidă a plecărilor.", "Protects the 20 kV busbar quickly, delayed after the feeders' high-set stage.")}`,
      `R1: I>> ≥ ${PR.fmt(D.kD, 2)} · ${fA(rep.R1.IhBase)} = ${fA(D.kD * rep.R1.IhBase)} → <b>${fA(S2.R1.Ih)}</b> (110 kV), ${t("instantaneu", "instantaneous")}. ${t("Defectul trifazat minim la bornele de 110 kV", "The minimum three-phase fault at the 110 kV terminals")} = ${fA(rep.R1.IhHVfault)}: ${rep.R1.IhHVfault > S2.R1.Ih ? t("acoperit", "covered") : t("NEACOPERIT", "NOT covered")}.`,
    ];
    document.getElementById("rg-high").innerHTML = hi.join("\n");
    document.getElementById("rg-inrush").innerHTML = `<b class="k">${bi("Curentul de magnetizare", "Magnetising inrush")}</b>` + bi(`Pragul I>> al lui R1 este ${PR.fmt(rep.R1.IhOverIr, 1)}·I_rT. Curentul de magnetizare la conectarea transformatorului atinge 6–10·I_rT și mai mult, după momentul conectării. Cu un prag de acest ordin, treapta rapidă se blochează la armonica a 2-a sau primește o temporizare scurtă; verifică în manualul releului ce variantă are.`, `R1's I>> pickup is ${PR.fmt(rep.R1.IhOverIr, 1)}·I_rT. Transformer inrush reaches 6–10·I_rT and more, depending on the switching instant. With a pickup of this order, the high-set stage is blocked by second harmonic or given a short delay; check which option the relay manual offers.`);
    // TMS
    const tm = ["R3", "R2", "R1"].map((r) => {
      const v = rep[r].tms, dn = { R3: "R4", R2: "R3", R1: "R2" }[r];
      if (!v.at) return `${r}: TMS = ${PR.fmt(S2[r].tms, 2)}`;
      return `${r}: TMS = ${PR.fmt(S2[r].tms, 2)} (${t("necesar", "required")} ${PR.fmt(v.tms === S2[r].tms ? v.tms : v.tms, 3)}) — ${t("punctul critic", "critical point")}: ${v.at.type}, I_${dn} = ${fA(v.at.Idn)}, t_${dn} = ${fs(v.at.tdn)} → t_${r} ≥ ${fs(v.at.tdn + D.cti)}`;
    });
    tm.unshift(`R4: TMS = ${PR.fmt(S2.R4.tms, 2)} (${t("minimul releului; R4 e ultimul releu de pe linie", "relay minimum; R4 is the last relay on the line")})`);
    document.getElementById("rg-tms").textContent = tm.join("\n");
    // fișa
    const co = M.coordination(NET, D, S2);
    h = `<tr><th>${bi("Releu", "Relay")}</th><th class="n">TC</th><th>${bi("Curba", "Curve")}</th><th class="n">I&gt; ${bi("prim.", "prim.")}</th><th class="n">I&gt; ${bi("sec.", "sec.")}</th><th class="n">TMS</th><th class="n">I&gt;&gt; ${bi("prim.", "prim.")}</th><th class="n">I&gt;&gt; ${bi("sec.", "sec.")}</th><th class="n">t&gt;&gt;</th></tr>`;
    RL.forEach((r) => { const st = S2[r]; h += `<tr><td><span class="relay-chip"><i style="background:${COL[r]}"></i>${t(NAME[r])}</span></td><td class="n">${D[r].ct}/1 A</td><td>${t(M.CURVES[st.curve])}</td><td class="n">${fA(st.Is)}</td><td class="n">${PR.fmt(st.Is / D[r].ct, 2)} A</td><td class="n">${PR.fmt(st.tms, 2)}</td><td class="n">${st.Ih > 0 ? fA(st.Ih) : "—"}</td><td class="n">${st.Ih > 0 ? PR.fmt(st.Ih / D[r].ct, 2) + " A" : "—"}</td><td class="n">${st.Ih > 0 ? (st.th > 0 ? fs(st.th) : t("0 s (instant.)", "0 s (instant.)")) : "—"}</td></tr>`; });
    document.getElementById("rg-sheet").innerHTML = h;
    const allOk = Object.values(co).every((c) => c.ok);
    document.getElementById("rg-verdict").innerHTML = `<div class="status ${allOk ? "ok" : "bad"}"><span class="led"></span><span class="pill">${allOk ? t("SELECTIV", "SELECTIVE") : t("NESELECTIV", "NOT SELECTIVE")}</span><span class="msg">${Object.entries(co).map(([k, c]) => `${k.replace("-", "–")}: ${fs(c.margin)}`).join(" · ")}</span></div>`;
    drawCTI();
  }
  const CT = { Er: 5, Ect: 10, tcb: 0.06, to: 0.02, ts: 0.05, t: 0.5 };
  function drawCTI() {
    const v = M.ctiFromParts(CT.t, CT.Er, CT.Ect, CT.tcb, CT.to, CT.ts);
    document.getElementById("cti-out").innerHTML = `Δt = (2·${PR.fmt(CT.Er, 1)} + ${PR.fmt(CT.Ect, 1)})·${PR.fmt(CT.t, 2)}/100 + ${PR.fmt(CT.tcb, 2)} + ${PR.fmt(CT.to, 2)} + ${PR.fmt(CT.ts, 2)} = <b>${fs(v)}</b>`;
    document.getElementById("cti-use").dataset.v = v;
  }
  function buildCTI() {
    const host = document.getElementById("cti-calc");
    host.innerHTML = `<div class="label" style="margin-bottom:6px">${bi("Calculatorul marjei, relația (7)", "Margin calculator, relation (7)")}</div><div id="cti-knobs"></div><div class="tools" style="margin-top:8px"><span class="mono" id="cti-out"></span><button class="btn" id="cti-use">${bi("Folosește în calcul", "Use in the calculation")}</button></div>`;
    PR.controls(document.getElementById("cti-knobs"), [{ g: { ro: "Componentele marjei", en: "Margin components" }, open: false, items: [
      { k: "Er", l: { ro: "Eroarea de timp a releului E_R", en: "Relay timing error E_R" }, u: "%", step: 0.5 },
      { k: "Ect", l: { ro: "Eroarea TC E_CT", en: "CT error E_CT" }, u: "%", step: 1 },
      { k: "t", l: { ro: "Timpul releului din aval t", en: "Downstream relay time t" }, u: "s", step: 0.05 },
      { k: "tcb", l: { ro: "Timpul de rupere t_CB", en: "Breaker time t_CB" }, u: "s", step: 0.01 },
      { k: "to", l: { ro: "Depășirea t_o", en: "Overshoot t_o" }, u: "s", step: 0.01 },
      { k: "ts", l: { ro: "Rezerva t_s", en: "Safety margin t_s" }, u: "s", step: 0.01 },
    ] }], CT, drawCTI);
    document.getElementById("cti-use").addEventListener("click", (e) => { RG.cti = Math.ceil(+e.currentTarget.dataset.v * 100 - 1e-9) / 100; rgCtl.gen.sync(); onRG(); });
  }

  const rgCtl = {};
  function buildRG() {
    const host = document.getElementById("rg-inputs");
    host.innerHTML = ["gen", ...RL].map((k) => `<div class="panel" id="rg-${k}"></div>`).join("");
    ["gen", ...RL].forEach((k) => (rgCtl[k] = PR.controls(document.getElementById("rg-" + k), RGS[k], RG, onRG)));
  }
  document.getElementById("copy-sheet").addEventListener("click", (e) => {
    const S2 = AUTO.S;
    const rows = [["releu", "TC", "curba", "I>_prim_A", "I>_sec_A", "TMS", "I>>_prim_A", "I>>_sec_A", "t>>_s"]];
    RL.forEach((r) => { const st = S2[r]; rows.push([r, `${D[r].ct}/1`, st.curve, PR.xnum(st.Is, 0), PR.xnum(st.Is / D[r].ct, 2), PR.xnum(st.tms, 2), st.Ih > 0 ? PR.xnum(st.Ih, 0) : "", st.Ih > 0 ? PR.xnum(st.Ih / D[r].ct, 2) : "", st.Ih > 0 ? PR.xnum(st.th, 2) : ""]); });
    PR.copyTSV(rows, e.currentTarget);
  });
  document.getElementById("apply-lab").addEventListener("click", () => { S = clone(AUTO.S); toFlat(); ctl.sync(); renderLab(); location.hash = "lab"; });

  /* ---------- test ---------- */
  const MCQ = [
    { q: { ro: "Care sunt constantele curbei IEC normal inverse (SI)?", en: "What are the constants of the IEC standard inverse (SI) curve?" }, o: [{ ro: "k = 0,14; α = 0,02", en: "k = 0.14; α = 0.02" }, { ro: "k = 13,5; α = 1", en: "k = 13.5; α = 1" }, { ro: "k = 80; α = 2", en: "k = 80; α = 2" }, { ro: "k = 120; α = 1", en: "k = 120; α = 1" }], a: 0, e: { ro: "IEC 60255-151: SI 0,14/0,02; VI 13,5/1; EI 80/2; LTI 120/1.", en: "IEC 60255-151: SI 0.14/0.02; VI 13.5/1; EI 80/2; LTI 120/1." } },
    { q: { ro: "Cât durează acționarea unei curbe IEC VI la 10·I>, cu TMS = 1?", en: "What is the operating time of an IEC VI curve at 10·I>, TMS = 1?" }, o: [{ ro: "0,81 s", en: "0.81 s" }, { ro: "1,50 s", en: "1.50 s" }, { ro: "2,97 s", en: "2.97 s" }, { ro: "13,3 s", en: "13.3 s" }], a: 1, e: { ro: "t = 13,5/(10 − 1) = 1,5 s.", en: "t = 13.5/(10 − 1) = 1.5 s." } },
    { q: { ro: "De ce apare coeficientul de revenire k_rev în formula pragului?", en: "Why does the reset ratio k_rev appear in the pickup formula?" }, o: [{ ro: "Ca releul să revină după eliminarea unui defect din aval, cu sarcina maximă prin el", en: "So the relay resets after a downstream fault is cleared, with maximum load through it" }, { ro: "Ca să crească sensibilitatea", en: "To increase sensitivity" }, { ro: "Pentru curentul de magnetizare", en: "For inrush current" }, { ro: "Pentru eroarea TC", en: "For the CT error" }], a: 0, e: { ro: "După eliminarea defectului, prin releu trece din nou sarcina; dacă ea e peste pragul de revenire, releul ar rămâne pornit.", en: "After the fault is cleared, load flows again; if it exceeds the reset level, the relay would stay picked up." } },
    { q: { ro: "Ce marjă de coordonare se folosește uzual între relee numerice cu întrerupătoare în vid?", en: "What coordination margin is commonly used between numerical relays with vacuum breakers?" }, o: [{ ro: "0,05 s", en: "0.05 s" }, { ro: "0,25–0,3 s", en: "0.25–0.3 s" }, { ro: "0,8 s", en: "0.8 s" }, { ro: "1,5 s", en: "1.5 s" }], a: 1, e: { ro: "Relația (7) dă în jur de 0,25 s; 0,3 s e valoarea folosită frecvent.", en: "Relation (7) gives about 0.25 s; 0.3 s is the commonly used value." } },
    { q: { ro: "Cum se reglează treapta instantanee a releului de la capul plecării?", en: "How is the feeder-head instantaneous stage set?" }, o: [{ ro: "Peste 1,2–1,3·I″k3 max la releul următor", en: "Above 1.2–1.3·I″k3 max at the next relay" }, { ro: "Sub I″k2 min la capătul liniei", en: "Below I″k2 min at the line end" }, { ro: "La 2·I_sarcină", en: "At 2·I_load" }, { ro: "Egal cu pragul I>", en: "Equal to the I> pickup" }], a: 0, e: { ro: "Relația (6): treapta instantanee trebuie să nu vadă defectele din zona următoare.", en: "Relation (6): the instantaneous stage must not see faults in the next zone." } },
    { q: { ro: "Cu ce curent se verifică sensibilitatea treptei I>?", en: "Which current is used to check the sensitivity of I>?" }, o: [{ ro: "I″k2 min la capătul zonei", en: "I″k2 min at the end of the zone" }, { ro: "I″k3 max la locul releului", en: "I″k3 max at the relay" }, { ro: "Curentul de sarcină", en: "The load current" }, { ro: "Curentul de șoc", en: "The peak current" }], a: 0, e: { ro: "Relația (4): cel mai mic defect din zonă, în regim minim.", en: "Relation (4): the smallest fault in the zone, minimum case." } },
    { q: { ro: "De ce pragul releului din amonte, raportat, nu poate fi sub cel din aval?", en: "Why can't the referred upstream pickup be below the downstream one?" }, o: [{ ro: "Un defect slab din aval ar fi eliminat de releul din amonte", en: "A weak downstream fault would be cleared by the upstream relay" }, { ro: "Ar crește curentul de defect", en: "The fault current would increase" }, { ro: "TC s-ar satura", en: "The CT would saturate" }, { ro: "Nu contează", en: "It does not matter" }], a: 0, e: { ro: "Între cele două praguri, doar releul din amonte ar porni.", en: "Between the two pickups, only the upstream relay would start." } },
    { q: { ro: "La un defect bifazat pe 20 kV, față de R2, R1 (110 kV, YNd11) primește relativ:", en: "For a phase-to-phase fault on 20 kV, relative to R2, R1 (110 kV, YNd11) receives:" }, o: [{ ro: "2/√3 ≈ 1,155 ori mai mult", en: "2/√3 ≈ 1.155 times more" }, { ro: "√3/2 ≈ 0,866 din curent", en: "√3/2 ≈ 0.866 of the current" }, { ro: "La fel", en: "The same" }, { ro: "Nimic", en: "Nothing" }], a: 0, e: { ro: "R2 vede √3/2 din curentul trifazat, R1 vede pe o fază curentul trifazat întreg (raportat).", en: "R2 sees √3/2 of the three-phase current, R1 sees the full (referred) three-phase current on one phase." } },
    { q: { ro: "Care reglaj rezultă din coordonare, nu din curentul de sarcină?", en: "Which setting results from coordination, not from the load current?" }, o: [{ ro: "TMS", en: "TMS" }, { ro: "Pragul I>", en: "The I> pickup" }, { ro: "Raportul TC", en: "The CT ratio" }, { ro: "k_rev", en: "k_rev" }], a: 0, e: { ro: "Relația (8): TMS-ul cel mai mic care păstrează marja față de releul din aval.", en: "Relation (8): the smallest TMS that keeps the margin over the downstream relay." } },
    { q: { ro: "Celula de sosire nu vede capătul unei plecări lungi. Ce se face?", en: "The incomer cannot see the end of a long feeder. What is done?" }, o: [{ ro: "Rezervă locală: a doua treaptă la plecare și DRRI", en: "Local backup: a second stage on the feeder and breaker-failure protection" }, { ro: "Se scade pragul sosirii sub curentul nominal", en: "Lower the incomer pickup below rated current" }, { ro: "Se scoate protecția plecării", en: "Remove the feeder protection" }, { ro: "Se crește TMS-ul sosirii", en: "Increase the incomer TMS" }], a: 0, e: { ro: "Pragul sosirii nu poate coborî sub sarcina transformatorului; rezerva se mută local.", en: "The incomer pickup cannot go below the transformer load; backup moves to local means." } },
    { q: { ro: "De ce se blochează la armonica a 2-a treapta rapidă de pe 110 kV a transformatorului?", en: "Why is the transformer's 110 kV high-set stage blocked by second harmonic?" }, o: [{ ro: "Pragul ei e de ordinul curentului de magnetizare la conectare", en: "Its pickup is of the order of the magnetising inrush current" }, { ro: "Pentru defecte pe 20 kV", en: "For 20 kV faults" }, { ro: "Pentru sarcina rece", en: "For cold load" }, { ro: "Pentru supratensiuni", en: "For overvoltages" }], a: 0, e: { ro: "Inrush-ul are mult conținut de armonica a 2-a; defectul nu.", en: "Inrush is rich in second harmonic; a fault is not." } },
    { q: { ro: "Ce dezavantaj au curbele extrem de inverse?", en: "What is the drawback of extremely inverse curves?" }, o: [{ ro: "Rezerva pentru defectele de la capătul liniei poate fi foarte lentă", en: "Backup for line-end faults can be very slow" }, { ro: "Nu se coordonează cu siguranțe", en: "They do not coordinate with fuses" }, { ro: "Nu au formulă standard", en: "They have no standard formula" }, { ro: "Sunt lente la defecte apropiate", en: "They are slow for close faults" }], a: 0, e: { ro: "Panta mare face timpii mari la curenți mici.", en: "The steep slope gives long times at low currents." } },
    { q: { ro: "Ce se întâmplă cu o curbă IEC peste 20·I>?", en: "What happens with an IEC curve above 20·I>?" }, o: [{ ro: "Timpul rămâne cel de la 20·I>", en: "The time stays at its 20·I> value" }, { ro: "Releul se blochează", en: "The relay blocks" }, { ro: "Timpul crește", en: "The time increases" }, { ro: "Releul trece pe curba IEEE", en: "The relay switches to the IEEE curve" }], a: 0, e: { ro: "G_D = 20·G_S: peste acest punct caracteristica devine independentă.", en: "G_D = 20·G_S: above this point the characteristic becomes definite-time." } },
  ];
  function NUM() {
    const cv = PR.pick(["IEC-SI", "IEC-VI", "IEC-EI"]), Mm = PR.rnd(2, 15, 0.5), tms = PR.rnd(0.05, 0.6, 0.01);
    const Il = PR.rnd(80, 600, 10), td = PR.rnd(0.1, 0.8, 0.01), Mu = PR.rnd(3, 12, 0.5), I2 = PR.rnd(500, 5000, 10), Is = PR.rnd(100, 800, 5);
    const c = M.CURVES[cv], cu = M.CURVES["IEC-SI"];
    return [
      { q: { ro: `Releu cu curba ${c.ro}, TMS = ${PR.fmt(tms, 2)}. Cât durează acționarea la ${PR.fmt(Mm, 1)}·I>?`, en: `Relay with curve ${c.en}, TMS = ${PR.fmt(tms, 2)}. What is the operating time at ${PR.fmt(Mm, 1)}·I>?` }, u: "s", v: tms * M.curveTime(cv, Mm), e: { ro: "Relația (1).", en: "Relation (1)." } },
      { q: { ro: `Curentul maxim de sarcină e ${PR.fmt(Il, 0)} A; k_sig = 1,2, k_p = 1, k_rev = 0,95. Care e pragul minim I>?`, en: `The maximum load current is ${PR.fmt(Il, 0)} A; k_sig = 1.2, k_p = 1, k_rev = 0.95. What is the minimum I> pickup?` }, u: "A", v: (1.2 * Il) / 0.95, e: { ro: "Relația (3).", en: "Relation (3)." } },
      { q: { ro: `Releul din aval acționează în ${PR.fmt(td, 2)} s. Releul din amonte, IEC SI, vede ${PR.fmt(Mu, 1)}·I>. Ce TMS îi trebuie pentru Δt = 0,3 s?`, en: `The downstream relay operates in ${PR.fmt(td, 2)} s. The upstream relay, IEC SI, sees ${PR.fmt(Mu, 1)}·I>. What TMS does it need for Δt = 0.3 s?` }, u: "–", v: (td + 0.3) / M.curveTime("IEC-SI", Mu), e: { ro: "Relația (8), într-un singur punct.", en: "Relation (8), at a single point." } },
      { q: { ro: `I″k2 min la capătul zonei e ${PR.fmt(I2, 0)} A, iar pragul I> e ${PR.fmt(Is, 0)} A. Cât e k_sens?`, en: `I″k2 min at the end of the zone is ${PR.fmt(I2, 0)} A and the I> pickup is ${PR.fmt(Is, 0)} A. What is k_sens?` }, u: "–", v: I2 / Is, e: { ro: "Relația (4).", en: "Relation (4)." } },
    ];
  }

  /* ---------- pornire ---------- */
  ctl = PR.controls(document.getElementById("controls"), SCHEMA, FS, onLab);
  pctl = PR.controls(document.getElementById("fknobs"), PSCHEMA, FS, onLab);
  buildButtons(); syncBtn(); buildRG(); buildCTI();
  renderLab(); renderSheet();
  PR.onLang(() => { renderLab(); renderSheet(); });
  PR.math();
  PR.tabs(["lab", "reglaje", "teorie", "test"], "lab");
  PR.quiz(document.getElementById("qlist"), document.getElementById("score"), document.getElementById("q-reset"), { mcq: MCQ, num: NUM, pick: 8 });
})();
