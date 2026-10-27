/* Modulul 04 — interfața paginii. Calculele sunt în engine.js (M04), cu M01 (rețeaua) și M03 (curbele). */
(function () {
  "use strict";
  const M = window.M04, M3 = window.M03, X = window.CX, PR = window.PR;
  const { abs, argDeg } = X;
  const bi = PR.bi, t = PR.t;

  const PA = { ...M.DEF_A };
  const D = JSON.parse(JSON.stringify(M.DEF_B));
  let RS = M.ringSettings(D);
  const RB = { line: "CD", m: 0.5, kase: "max" };

  const fA = (I) => (I >= 10000 ? `${PR.fmt(I / 1000, 2)} kA` : `${PR.fmt(I, I >= 100 ? 0 : 1)} A`);
  const fs = (x) => (isFinite(x) ? `${PR.fmt(x, 3)} s` : "—");
  const fdeg = (x) => `${PR.fmt(x, 1)}°`;
  const VERD = { fwd: { ro: "ÎNAINTE", en: "FORWARD" }, rev: { ro: "ÎNAPOI", en: "REVERSE" }, none: { ro: "NU PORNEȘTE", en: "NO PICKUP" }, mixed: { ro: "MIXT", en: "MIXED" } };
  const pill = (v) => `<span class="verd ${v}">${t(VERD[v])}</span>`;

  /* ---------- controale A ---------- */
  const SCHEMA = [
    { g: { ro: "Defectul", en: "The fault" }, col: "--trip", open: true, openNarrow: false, items: [
      { k: "type", l: { ro: "Tipul", en: "Type" }, sel: [["3F", { ro: "trifazat", en: "three-phase" }], ["2F", { ro: "bifazat L2–L3", en: "phase-to-phase L2–L3" }], ["1F", { ro: "monofazat L1–pământ", en: "single-phase L1–earth" }], ["2FE", { ro: "bifazat cu pământ", en: "two-phase-to-earth" }]], wide: true },
      { k: "dir", l: { ro: "Locul față de releu", en: "Location relative to the relay" }, sel: [["fwd", { ro: "înainte, pe linia A–B", en: "forward, on line A–B" }], ["rev", { ro: "înapoi, pe barele A", en: "reverse, on busbar A" }]], wide: true },
      { k: "m", l: { ro: "Poziția pe linie (de la A)", en: "Position on the line (from A)" }, u: "–", step: 0.01, range: [0.01, 0.99] },
      { k: "Rf", l: { ro: "Rezistența de defect", en: "Fault resistance" }, u: "Ω", step: 1 },
      { k: "kase", l: { ro: "Regimul", en: "Case" }, sel: [["max", { ro: "maxim", en: "maximum" }], ["min", { ro: "minim", en: "minimum" }]] },
    ] },
    { g: { ro: "Releul de la capătul A", en: "The relay at end A" }, col: "--c1", open: true, openNarrow: false, items: [
      { k: "rca", l: { ro: "Unghiul caracteristic θc (fază)", en: "Characteristic angle θc (phase)" }, u: "°", step: 5, range: [-90, 90] },
      { k: "rcaN", l: { ro: "Unghiul caracteristic θcN (67N)", en: "Characteristic angle θcN (67N)" }, u: "°", step: 5, range: [-90, 90] },
      { k: "Is", l: { ro: "Pragul I> (fază)", en: "I> pickup (phase)" }, u: "A", step: 5 },
      { k: "IsN", l: { ro: "Pragul I0> (3I0)", en: "I0> pickup (3I0)" }, u: "A", step: 5 },
    ] },
    { g: { ro: "Rețeaua", en: "The network" }, col: "--c3", items: [
      { k: "lenL", l: { ro: "Lungimea liniei A–B (cablu)", en: "Line A–B length (cable)" }, u: "km", step: 0.5 },
      { k: "SkB", l: { ro: "S″k a sursei de la capătul B", en: "S″k of the source at end B" }, u: "MVA", step: 10, range: [10, 500] },
      { k: "gB", l: { ro: "Sursa B are neutrul legat la pământ", en: "Source B has an earthed neutral" }, chk: true },
    ] },
  ];
  const PRESETS = [
    [{ ro: "Bifazat înainte, la mijloc", en: "Phase-to-phase forward, mid-line" }, { type: "2F", dir: "fwd", m: 0.5, rca: 45, gB: false, Rf: 0 }],
    [{ ro: "Trifazat înapoi, pe barele A", en: "Three-phase reverse, on busbar A" }, { type: "3F", dir: "rev", rca: 45, Rf: 0 }],
    [{ ro: "Trifazat foarte aproape (memorie)", en: "Close-in three-phase (memory)" }, { type: "3F", dir: "fwd", m: 0.01, rca: 45, Rf: 0 }],
    [{ ro: "Monofazat înainte (67N)", en: "Single-phase forward (67N)" }, { type: "1F", dir: "fwd", m: 0.5, gB: false, Rf: 0 }],
    [{ ro: "Monofazat înapoi, sursa B legată la pământ", en: "Single-phase reverse, source B earthed" }, { type: "1F", dir: "rev", gB: true, Rf: 0 }],
    [{ ro: "Unghi caracteristic greșit: −60°", en: "Wrong characteristic angle: −60°" }, { type: "3F", dir: "fwd", m: 0.5, rca: -60, Rf: 0 }],
  ];
  let ctlA, ctlB;

  function renderA() {
    const r = M.partA(PA), dd = r.dirs;
    const expect = PA.dir;
    const wrong = [dd.phase, dd.ground].some((v) => (v === "fwd" || v === "rev") && v !== expect);
    const mixed = dd.phase === "mixed";
    const cls = wrong ? "bad" : mixed ? "warn" : "ok";
    const dirTxt = expect === "fwd" ? bi("înainte", "forward") : bi("înapoi", "reverse");
    let msg = bi(`Defectul e ${t("înainte", "")}`, "");
    msg = `${bi("Defectul este", "The fault is")} ${dirTxt}. ${bi("Elemente de fază", "Phase elements")}: ${pill(dd.phase)} · 67N: ${pill(dd.ground)}. `;
    if (wrong) msg += bi("Cel puțin un element decide greșit sensul.", "At least one element decides the wrong direction.");
    else if (mixed) msg += bi("Elementele de fază se contrazic: la punerile la pământ decide elementul homopolar.", "The phase elements disagree: for earth faults the earth-fault element decides.");
    else msg += bi("Deciziile pornite sunt corecte.", "The elements that picked up decide correctly.");
    if (dd.ph.some((x) => x.mem && x.active)) msg += " " + bi("Tensiunea s-a prăbușit: elementele folosesc memoria.", "The voltage collapsed: the elements use memory.");
    document.getElementById("status").innerHTML = `<div class="status ${cls}"><span class="led"></span><span class="pill">${wrong ? t("GREȘIT", "WRONG") : mixed ? t("ATENȚIE", "CAUTION") : t("CORECT", "CORRECT")}</span><span class="msg">${msg}</span></div>`;
    const Imax = Math.max(...r.Iabc.map(abs));
    const kp = [
      [bi("Curentul maxim pe faze la releu", "Maximum phase current at relay"), fA(Imax)],
      [bi("Curentul rezidual 3I₀", "Residual current 3I₀"), fA(abs(dd.gnd.I))],
      [bi("Decizia elementelor de fază", "Phase elements decision"), pill(dd.phase)],
      [bi("Decizia 67N", "67N decision"), pill(dd.ground)],
    ];
    document.getElementById("kpis").innerHTML = kp.map(([l, v]) => `<div><div class="label">${l}</div><div class="v" style="font-size:1.15rem">${v}</div></div>`).join("");
    drawPhasor(r);
    drawElems(r);
  }

  function wedge(cx, cy, R, a0, a1) {
    let pts = [`${cx},${cy}`];
    for (let i = 0; i <= 48; i++) { const a = ((a0 + ((a1 - a0) * i) / 48) * Math.PI) / 180; pts.push(`${(cx + R * Math.cos(a)).toFixed(1)},${(cy - R * Math.sin(a)).toFixed(1)}`); }
    return `<polygon points="${pts.join(" ")}" fill="var(--ok-bg)" stroke="none"/>`;
  }
  function panel(cx, title, el, rca, labI, labV, inactiveTxt) {
    const R = 112, cy = 170;
    let s = `<text x="${cx}" y="24" class="lbl" text-anchor="middle" font-weight="600">${title}</text>`;
    if (!el) return s + `<text x="${cx}" y="${cy}" class="tick" text-anchor="middle">${inactiveTxt}</text>`;
    const aV = argDeg(el.Vp), aM = aV + rca;
    s += wedge(cx, cy, R, aM - 90, aM + 90);
    s += `<circle cx="${cx}" cy="${cy}" r="${R}" fill="none" stroke="var(--line)"/>`;
    s += `<line x1="${cx - R - 8}" y1="${cy}" x2="${cx + R + 8}" y2="${cy}" class="grid"/><line x1="${cx}" y1="${cy - R - 8}" x2="${cx}" y2="${cy + R + 8}" class="grid"/>`;
    const pt = (a, L) => [cx + L * Math.cos((a * Math.PI) / 180), cy - L * Math.sin((a * Math.PI) / 180)];
    // limita zonei
    [aM - 90, aM + 90].forEach((a) => { const [x, y] = pt(a, R); s += `<line x1="${cx}" y1="${cy}" x2="${x}" y2="${y}" stroke="var(--ok)" stroke-width="1"/>`; });
    const [mx, my] = pt(aM, R + 6); s += `<line x1="${cx}" y1="${cy}" x2="${mx}" y2="${my}" stroke="var(--ok)" stroke-dasharray="6 4" stroke-width="1.5"/>`;
    const [tx, ty] = pt(aM, R + 18); s += `<text x="${tx}" y="${ty + 4}" class="tick" text-anchor="middle" fill="var(--ok)">${t("cuplu max.", "max. torque")}</text>`;
    const [vx, vy] = pt(aV, R * 0.82); s += PR.arrow(cx, cy, vx, vy, "var(--muted)", 2.2, el.mem ? "4 3" : "");
    const [vlx, vly] = pt(aV, R * 0.82 + 14); s += `<text x="${vlx}" y="${vly + 4}" class="tick" text-anchor="middle">${labV}${el.mem ? " (" + t("memorie", "memory") + ")" : ""}</text>`;
    const aI = argDeg(el.I); const [ix, iy] = pt(aI, R * 0.95); s += PR.arrow(cx, cy, ix, iy, el.fwd ? "var(--ok)" : "var(--accent)", 3);
    const [ilx, ily] = pt(aI, R * 0.95 + 14); s += `<text x="${ilx}" y="${ily + 4}" class="tick" text-anchor="middle" font-weight="600" fill="${el.fwd ? "var(--ok)" : "var(--accent)"}">${labI}</text>`;
    s += `<text x="${cx}" y="${cy + R + 34}" class="tick" text-anchor="middle">φ = ${fdeg(M.wrap(argDeg(el.I) - argDeg(el.Vp)))} · φ − θc = ${fdeg(el.ang)} → ${t(VERD[el.fwd ? "fwd" : "rev"])}</text>`;
    return s;
  }
  function drawPhasor(r) {
    const dd = r.dirs, names = ["L1", "L2", "L3"], pols = ["U23", "U31", "U12"];
    const act = dd.ph.map((x, i) => ({ ...x, i })).filter((x) => x.active);
    const pick = act.length ? act.sort((a, b) => abs(b.I) - abs(a.I))[0] : null;
    let s = panel(190, pick ? `${t("Element de fază", "Phase element")} ${names[pick.i]}` : t("Elementele de fază", "Phase elements"), pick, PA.rca, `I ${names[pick ? pick.i : 0]}`, pick ? pols[pick.i] : "", t("niciun element nu a pornit", "no element picked up"));
    s += panel(570, t("Elementul homopolar 67N", "Earth-fault element 67N"), dd.gnd.active ? dd.gnd : null, PA.rcaN, "3I₀", "−3U₀", t("3I₀ sub prag: nu pornește", "3I₀ below pickup: no start"));
    document.getElementById("phasor").innerHTML = s;
  }
  function drawElems(r) {
    const dd = r.dirs, names = ["L1", "L2", "L3"], pols = ["U23", "U31", "U12"];
    const fph = (z, u) => `${PR.sig(abs(z), 4)} ${u} ∠ ${fdeg(argDeg(z))}`;
    let h = `<tr><th>${bi("Element", "Element")}</th><th class="n">${bi("Curent", "Current")}</th><th class="n">${bi("Polarizare", "Polarisation")}</th><th class="n">φ − θc</th><th>${bi("Pornit", "Picked up")}</th><th>${bi("Decizia", "Decision")}</th></tr>`;
    dd.ph.forEach((x, i) => { h += `<tr><td class="mono">67 ${names[i]}</td><td class="n">${fph(x.I, "A")}</td><td class="n">${pols[i]}: ${fph(x.Vp, "V")}${x.mem ? " · " + t("memorie", "memory") : ""}</td><td class="n">${fdeg(x.ang)}</td><td>${x.active ? t("da", "yes") : t("nu", "no")}</td><td>${x.active ? pill(x.fwd ? "fwd" : "rev") : "—"}</td></tr>`; });
    const g = dd.gnd;
    h += `<tr><td class="mono">67N</td><td class="n">3I₀: ${fph(g.I, "A")}</td><td class="n">−3U₀: ${fph(g.Vp, "V")}</td><td class="n">${fdeg(g.ang)}</td><td>${g.active ? t("da", "yes") : t("nu", "no")}</td><td>${g.active ? pill(g.fwd ? "fwd" : "rev") : "—"}</td></tr>`;
    document.getElementById("elems").innerHTML = h;
  }

  /* ---------- partea B ---------- */
  const RSCHEMA = [{ g: { ro: "Defectul în buclă", en: "The fault in the ring" }, col: "--trip", open: true, items: [
    { k: "line", l: { ro: "Linia defectă", en: "Faulted line" }, sel: D.lines.map((l) => [l.id, { ro: `${l.a}–${l.b} (${l.km} km)`, en: `${l.a}–${l.b} (${l.km} km)` }]), wide: true },
    { k: "m", l: { ro: "Poziția pe linie (de la primul capăt)", en: "Position on the line (from first end)" }, u: "–", step: 0.01, range: [0.01, 0.99] },
    { k: "kase", l: { ro: "Regimul", en: "Case" }, sel: [["max", { ro: "maxim", en: "maximum" }], ["min", { ro: "minim", en: "minimum" }]] },
  ] }];
  const POS = { A: [130, 80], B: [630, 80], C: [630, 290], D: [130, 290] };

  function renderB() {
    const fault = { line: RB.line, m: RB.m };
    const seq = M.ringSequence(D, RS.S, RB.kase, fault);
    const sol0 = M.ringSolve(D, RB.kase, fault, new Set());
    const fl = D.lines.find((l) => l.id === RB.line);
    const ok = seq.correct;
    const ev = seq.events.map((e, i) => `${e.relay} (${fs(e.t)})`).join(", ");
    document.getElementById("ringstatus").innerHTML = `<div class="status ${ok ? "ok" : "bad"}"><span class="led"></span><span class="pill">${ok ? t("IZOLAT CORECT", "CORRECTLY ISOLATED") : t("IZOLARE GREȘITĂ", "WRONG ISOLATION")}</span><span class="msg">${bi(`Linia ${fl.a}–${fl.b} e izolată în ${fs(seq.tClear)}: ${ev}. Rezerva celorlalte relee: ${fs(seq.margin)}.`, `Line ${fl.a}–${fl.b} is isolated in ${fs(seq.tClear)}: ${ev}. Margin of the other relays: ${fs(seq.margin)}.`)}</span></div>`;
    // desen
    let s = `<circle cx="40" cy="80" r="18" fill="var(--surface)" stroke="var(--ink)" stroke-width="1.5"/><path d="M30 80 q5 -8 10 0 t10 0" fill="none" stroke="var(--ink)" stroke-width="1.5"/><line x1="58" y1="80" x2="${POS.A[0] - 8}" y2="80" stroke="var(--ink)" stroke-width="1.5"/><text x="40" y="120" class="tick" text-anchor="middle">T1</text>`;
    const order = {}; seq.events.forEach((e, i) => (order[e.relay] = i + 1));
    D.lines.forEach((l) => {
      const [x1, y1] = POS[l.a], [x2, y2] = POS[l.b];
      s += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="var(--c6)" stroke-width="3"/>`;
      // lungimea, la o treime din linie (mijlocul rămâne liber pentru defect și curent)
      const mx = x1 + (x2 - x1) * 0.3, my = y1 + (y2 - y1) * 0.3, horiz = y1 === y2;
      s += `<text x="${mx + (horiz ? 0 : 14)}" y="${my + (horiz ? (y1 < 200 ? -12 : 22) : 4)}" class="tick" text-anchor="${horiz ? "middle" : "start"}">${l.km} km</text>`;
      // relee la capete
      [[l.a, x1, y1, x2, y2], [l.b, x2, y2, x1, y1]].forEach(([bus, bx, by, ox, oy]) => {
        const id = `${l.id}@${bus}`, L = Math.hypot(ox - bx, oy - by), ux = (ox - bx) / L, uy = (oy - by) / L;
        const rx = bx + ux * 42, ry = by + uy * 42;
        const tripped = order[id] != null;
        const c0 = sol0.cur[id];
        const started = c0 && M.ringDir(c0.I, c0.V, sol0.E, D.rca).fwd && abs(c0.I) >= M3.GT * RS.S[id].Is;
        const fill = tripped ? "var(--trip)" : started ? "var(--start-bg)" : "var(--surface)", stroke = tripped ? "var(--trip)" : started ? "var(--start)" : "var(--muted)";
        s += `<rect x="${rx - 9}" y="${ry - 9}" width="18" height="18" rx="2" fill="${fill}" stroke="${stroke}" stroke-width="2"/>`;
        if (tripped) s += `<text x="${rx}" y="${ry + 4}" class="tick" text-anchor="middle" fill="var(--surface)" font-weight="600">${order[id]}</text>`;
        // săgeata direcției de acționare
        s += PR.arrow(rx + ux * 12, ry + uy * 12, rx + ux * 26, ry + uy * 26, stroke, 1.5);
        const lx = rx + (horiz2(bx, by, ox, oy) ? 0 : uy === 0 ? 0 : -uy * 0) + (Math.abs(uy) > 0.5 ? -40 : 0), ly = ry + (Math.abs(uy) > 0.5 ? 4 : by < 200 ? 26 : -16);
        s += `<text x="${lx}" y="${ly}" class="tick" text-anchor="middle">${id}</text>`;
      });
      // curentul inițial pe linie
      const ca = sol0.cur[`${l.id}@${l.a}`], cb = sol0.cur[`${l.id}@${l.b}`];
      if (l.id !== RB.line && ca) {
        const P = ca.V.re * ca.I.re + ca.V.im * ca.I.im;      // sensul puterii active, de la a spre b dacă P > 0
        const [fx, fy, tx, ty] = P > 0 ? [x1, y1, x2, y2] : [x2, y2, x1, y1];
        const L = Math.hypot(tx - fx, ty - fy), ux = (tx - fx) / L, uy = (ty - fy) / L, cxm = (fx + tx) / 2, cym = (fy + ty) / 2;
        s += PR.arrow(cxm - ux * 18, cym - uy * 18, cxm + ux * 18, cym + uy * 18, "var(--c2)", 2.2);
        s += `<text x="${cxm + (y1 === y2 ? 0 : 30)}" y="${cym + (y1 === y2 ? 20 : -14)}" class="tick" text-anchor="${y1 === y2 ? "middle" : "start"}" fill="var(--c2)">${fA(abs(ca.I))}</text>`;
      }
    });
    // defectul
    const [x1, y1] = POS[fl.a], [x2, y2] = POS[fl.b];
    const fx = x1 + (x2 - x1) * RB.m, fy = y1 + (y2 - y1) * RB.m;
    s += `<path d="M${fx - 6} ${fy - 30} l10 12 -7 3 9 15" stroke="var(--trip)" stroke-width="2.5" fill="none"/>`;
    const ca = sol0.cur[`${fl.id}@${fl.a}`], cb = sol0.cur[`${fl.id}@${fl.b}`];
    s += `<text x="${fx}" y="${fy + (y1 === y2 ? -38 : 4)}" dx="${y1 === y2 ? 0 : 16}" class="tick" text-anchor="${y1 === y2 ? "middle" : "start"}" fill="var(--trip)">${fA(abs(sol0.Ifault))} = ${ca ? fA(abs(ca.I)) : "0"} + ${cb ? fA(abs(cb.I)) : "0"}</text>`;
    Object.entries(POS).forEach(([b, [x, y]]) => { s += `<circle cx="${x}" cy="${y}" r="7" fill="var(--ink)"/><text x="${x + (x < 300 ? -16 : 16)}" y="${y + (y < 200 ? -10 : 22)}" class="lbl" text-anchor="middle" font-weight="600">${b}</text>`; });
    s += `<g transform="translate(250,362)"><rect x="0" y="-10" width="14" height="14" fill="var(--trip)"/><text x="20" y="1" class="tick">${t("a declanșat (ordinea)", "tripped (order)")}</text><rect x="190" y="-10" width="14" height="14" fill="var(--start-bg)" stroke="var(--start)" stroke-width="2"/><text x="210" y="1" class="tick">${t("pornit, n-a declanșat", "started, did not trip")}</text></g>`;
    document.getElementById("ring").innerHTML = s;
    let h = `<tr><th class="n">#</th><th>${bi("Releul", "Relay")}</th><th class="n">${bi("Momentul", "Time")}</th><th class="n">${bi("Curentul la declanșare", "Current at trip")}</th></tr>`;
    seq.events.forEach((e, i) => { h += `<tr><td class="n">${i + 1}</td><td class="mono">${e.relay}</td><td class="n">${fs(e.t)}</td><td class="n">${fA(e.I)}</td></tr>`; });
    document.getElementById("seq").innerHTML = h;
  }
  const horiz2 = (x1, y1, x2, y2) => y1 === y2;

  /* ---------- reglaje ---------- */
  function renderSheet() {
    document.getElementById("sheet-meta").innerHTML = bi(`Linia A–B: ${PR.fmt(PA.lenL, 1)} km cablu · bucla: ${D.lines.map((l) => `${l.id} ${l.km} km`).join(", ")}`, `Line A–B: ${PR.fmt(PA.lenL, 1)} km cable · ring: ${D.lines.map((l) => `${l.id} ${l.km} km`).join(", ")}`);
    const st = M.rcaStudy(PA);
    let h = `<tr><th>${bi("Defect", "Fault")}</th><th>${bi("Element", "Element")}</th><th class="n">${bi("Poziția", "Position")}</th><th class="n">${bi("I conduce U_pol cu", "I leads U_pol by")}</th><th class="n">θc = 30°</th><th class="n">θc = 45°</th></tr>`;
    const rows = []; const seen = new Set();
    st.phase.forEach((x) => { const k = x.type + x.m + x.lead.toFixed(2); if (seen.has(k)) return; seen.add(k); rows.push(x); });
    const marg = (lead, rca) => 90 - Math.abs(M.wrap(lead - rca));
    rows.forEach((x) => { h += `<tr><td>${x.type}</td><td class="mono">67 L${x.ph + 1}</td><td class="n">${PR.fmt(x.m * 100, 0)} %</td><td class="n">${fdeg(x.lead)}</td><td class="n">${fdeg(marg(x.lead, 30))}</td><td class="n">${fdeg(marg(x.lead, 45))}</td></tr>`; });
    document.getElementById("rg-rca").innerHTML = h;
    const cand = [30, 45].map((c) => ({ c, worst: Math.min(...rows.map((x) => marg(x.lead, c))) }));
    const best = cand.sort((a, b) => b.worst - a.worst)[0];
    document.getElementById("rg-rca-pick").textContent = `${t("Marja minimă până la limita zonei", "Minimum margin to the zone boundary")}: θc = 30° → ${fdeg(cand.find((x) => x.c === 30).worst)}; θc = 45° → ${fdeg(cand.find((x) => x.c === 45).worst)}\n${t("Se alege", "Chosen")} θc = ${best.c}° (${t("conduce", "leading")}); ${t("aceeași valoare se folosește pentru releele buclei (același cablu)", "the same value is used for the ring relays (same cable)")}.`;
    if (D.rca !== best.c) { D.rca = best.c; renderB(); }
    document.getElementById("rg-rcan").textContent = `Z₀S = ${PR.fmt(M.partA(PA).zSA[0].re, 2)} ${M.partA(PA).zSA[0].im < 0 ? "−" : "+"} j${PR.fmt(Math.abs(M.partA(PA).zSA[0].im), 2)} Ω, arg Z₀S = ${fdeg(st.z0angle)}\n${t("Curentul 3I₀ conduce −3U₀ cu", "3I₀ leads −3U₀ by")} ${fdeg(st.groundLead)} ${t("la un defect înainte", "for a forward fault")} → θcN ≈ ${fdeg(-st.z0angle)}\n${t("Cu θcN = 0° (valoarea uzuală la neutrul tratat prin rezistor), marja până la limita zonei este", "With θcN = 0° (the usual value for a resistor-earthed neutral), the margin to the zone boundary is")} ${fdeg(90 - Math.abs(st.groundLead))}.`;
    // bucla
    const rep = RS.rep;
    document.getElementById("rg-pick").textContent = `I> = ${PR.fmt(D.kSig, 2)}·${PR.fmt(D.kP, 2)}·${PR.fmt(D.Iload, 0)} / ${PR.fmt(D.kRev, 2)} = ${PR.fmt((D.kSig * D.kP * D.Iload) / D.kRev, 1)} A → ${PR.fmt(rep.Is, 0)} A (TC ${D.ct}/1 A, ${t("pas", "step")} ${PR.fmt(D.ct * 0.01, 0)} A) · ${t("curba", "curve")} ${t(M3.CURVES[D.curve])} · Δt = ${PR.fmt(D.cti, 2)} s`;
    h = `<tr><th>${bi("Lanțul", "Chain")}</th><th>${bi("Inel deschis la", "Ring opened at")}</th><th>${bi("Aval", "Downstream")}</th><th>${bi("Amonte", "Upstream")}</th><th class="n">I max</th><th class="n">${bi("t aval", "t downstream")}</th><th class="n">${bi("TMS necesar", "TMS required")}</th><th class="n">TMS</th></tr>`;
    Object.entries(rep.chains).forEach(([dir, list]) => {
      h += `<tr><td>${dir === "cw" ? t("orar", "clockwise") : t("antiorar", "anticlockwise")}</td><td class="mono">${dir === "cw" ? "DA@A" : "AB@A"}</td><td class="mono">${M.CHAINS[dir][0]}</td><td></td><td></td><td></td><td></td><td class="n">${PR.fmt(RS.S[M.CHAINS[dir][0]].tms, 2)}</td></tr>`;
      list.forEach((x) => { h += `<tr><td></td><td></td><td class="mono">${x.dn}</td><td class="mono">${x.up}</td><td class="n">${fA(x.Imax)}</td><td class="n">${fs(x.at ? x.at.tdn : NaN)}</td><td class="n">${PR.fmt(x.need, 3)}</td><td class="n">${PR.fmt(x.tms, 2)}</td></tr>`; });
    });
    document.getElementById("rg-chains").innerHTML = h;
    // verificarea în bucla închisă
    let n = 0, good = 0, minM = Infinity, maxT = 0, maxAt = null;
    h = `<tr><th>${bi("Linia", "Line")}</th><th>${bi("Regimul", "Case")}</th><th class="n">10 %</th><th class="n">50 %</th><th class="n">90 %</th><th>${bi("Toate pozițiile (5 %…95 %)", "All positions (5 %…95 %)")}</th></tr>`;
    D.lines.forEach((l) => ["max", "min"].forEach((kase) => {
      const cells = [0.1, 0.5, 0.9].map((m) => M.ringSequence(D, RS.S, kase, { line: l.id, m }));
      let okAll = true;
      for (let i = 1; i < 20; i++) {
        const r = M.ringSequence(D, RS.S, kase, { line: l.id, m: i / 20 });
        n++; if (r.correct) good++; else okAll = false;
        if (isFinite(r.margin)) minM = Math.min(minM, r.margin);
        if (r.tClear > maxT) { maxT = r.tClear; maxAt = `${l.id}, ${i * 5} %, ${kase}`; }
      }
      h += `<tr><td class="mono">${l.a}–${l.b}</td><td>${kase === "max" ? t("maxim", "maximum") : t("minim", "minimum")}</td>${cells.map((r) => `<td class="n">${r.correct ? fs(r.tClear) : `<span class="bad">${t("greșit", "wrong")}</span>`}</td>`).join("")}<td><span class="${okAll ? "ok" : "bad"}">${okAll ? t("izolare corectă", "correct isolation") : t("erori", "errors")}</span></td></tr>`;
    }));
    document.getElementById("rg-check").innerHTML = h;
    document.getElementById("rg-check-note").innerHTML = `<b class="k">${bi("Rezultat", "Result")}</b>` + bi(`${good} din ${n} defecte sunt izolate corect, numai de releele liniei defecte. Cea mai mică rezervă a unui releu care n-a declanșat este ${fs(minM)}. Cel mai lung timp de eliminare, ${fs(maxT)}, apare la ${maxAt}: defectele de lângă sursă sunt eliminate de releele cu TMS-ul cel mai mare. Aici o protecție diferențială de linie sau o schemă cu comunicație (M08) ar elimina defectul instantaneu.`, `${good} of ${n} faults are isolated correctly, by the faulted line's relays only. The smallest margin of a relay that did not trip is ${fs(minM)}. The longest clearing time, ${fs(maxT)}, occurs at ${maxAt}: faults near the source are cleared by the relays with the largest TMS. Here a line differential or a communication-aided scheme (M08) would clear the fault instantaneously.`);
    // fișa
    h = `<tr><th>${bi("Releul", "Relay")}</th><th>${bi("Bara", "Bus")}</th><th>${bi("Privește spre", "Looks into")}</th><th>${bi("Direcțional", "Directional")}</th><th class="n">θc</th><th>${bi("Curba", "Curve")}</th><th class="n">I&gt; ${bi("prim.", "prim.")}</th><th class="n">I&gt; ${bi("sec.", "sec.")}</th><th class="n">TMS</th></tr>`;
    M.relaysOf(D).sort().forEach((r) => {
      const [line, bus] = r.split("@"), st2 = RS.S[r];
      const atSrc = bus === "A";
      h += `<tr><td class="mono">${r}</td><td>${bus}</td><td>${line}</td><td>${atSrc ? t("da (poate fi nedirecțional: curentul iese mereu din A)", "yes (may be non-directional: current always leaves A)") : t("da", "yes")}</td><td class="n">${D.rca}°</td><td>${t(M3.CURVES[st2.curve])}</td><td class="n">${fA(st2.Is)}</td><td class="n">${PR.fmt(st2.Is / D.ct, 2)} A</td><td class="n">${PR.fmt(st2.tms, 2)}</td></tr>`;
    });
    document.getElementById("rg-sheet").innerHTML = h;
  }
  document.getElementById("copy-sheet").addEventListener("click", (e) => {
    const rows = [["releu", "bara", "linia", "theta_c_grade", "curba", "I>_prim_A", "I>_sec_A", "TMS"]];
    M.relaysOf(D).sort().forEach((r) => { const [line, bus] = r.split("@"), s = RS.S[r]; rows.push([r, bus, line, D.rca, s.curve, PR.xnum(s.Is, 0), PR.xnum(s.Is / D.ct, 2), PR.xnum(s.tms, 2)]); });
    PR.copyTSV(rows, e.currentTarget);
  });

  /* ---------- test ---------- */
  const MCQ = [
    { q: { ro: "Când e nevoie de protecție direcțională?", en: "When is directional protection needed?" }, o: [{ ro: "Când defectul poate fi alimentat din ambele părți ale releului", en: "When the fault can be fed from both sides of the relay" }, { ro: "În orice rețea radială", en: "In any radial network" }, { ro: "Numai la generatoare", en: "Only on generators" }, { ro: "Când TC-ul se saturează", en: "When the CT saturates" }], a: 0, e: { ro: "Bucle închise, linii paralele, generare distribuită.", en: "Closed rings, parallel lines, distributed generation." } },
    { q: { ro: "În conexiunea la 90°, curentul I_L1 se polarizează cu:", en: "In the 90° connection, I_L1 is polarised with:" }, o: [{ ro: "U23", en: "U23" }, { ro: "U1", en: "U1" }, { ro: "U12", en: "U12" }, { ro: "3U0", en: "3U0" }], a: 0, e: { ro: "Relația (2): tensiunea dintre celelalte două faze.", en: "Relation (2): the voltage between the other two phases." } },
    { q: { ro: "Pentru un defect cu unghiul buclei θ, cu cât conduce I_L1 tensiunea U23?", en: "For a fault with loop angle θ, by how much does I_L1 lead U23?" }, o: [{ ro: "90° − θ", en: "90° − θ" }, { ro: "θ", en: "θ" }, { ro: "θ − 30°", en: "θ − 30°" }, { ro: "180° − θ", en: "180° − θ" }], a: 0, e: { ro: "Relația (3).", en: "Relation (3)." } },
    { q: { ro: "Ce valori are de obicei unghiul caracteristic al elementelor de fază?", en: "What are the usual phase-element characteristic angles?" }, o: [{ ro: "30° sau 45°, curentul conducând", en: "30° or 45°, current leading" }, { ro: "90°", en: "90°" }, { ro: "−90°", en: "−90°" }, { ro: "0° întotdeauna", en: "Always 0°" }], a: 0, e: { ro: "Corespund unghiurilor de buclă de 60° și 45°.", en: "They correspond to loop angles of 60° and 45°." } },
    { q: { ro: "Ce face elementul direcțional la un defect trifazat chiar la bornele releului?", en: "What does the directional element do for a three-phase fault right at the relay?" }, o: [{ ro: "Folosește tensiunea memorată dinainte de defect", en: "It uses the voltage memorised before the fault" }, { ro: "Folosește curentul homopolar", en: "It uses zero-sequence current" }, { ro: "Decide mereu înapoi", en: "It always decides reverse" }, { ro: "Nimic, tensiunea nu contează", en: "Nothing, voltage does not matter" }], a: 0, e: { ro: "Toate tensiunile se prăbușesc; memoria păstrează referința de fază.", en: "All voltages collapse; memory keeps the phase reference." } },
    { q: { ro: "Cu ce se polarizează elementul 67N?", en: "What polarises the 67N element?" }, o: [{ ro: "−3U0", en: "−3U0" }, { ro: "U23", en: "U23" }, { ro: "I2", en: "I2" }, { ro: "U1", en: "U1" }], a: 0, e: { ro: "Relația (4).", en: "Relation (4)." } },
    { q: { ro: "Ce unghi caracteristic se potrivește elementului 67N într-o rețea tratată prin rezistor?", en: "Which characteristic angle suits the 67N element in a resistor-earthed network?" }, o: [{ ro: "În jur de 0°", en: "About 0°" }, { ro: "+90°", en: "+90°" }, { ro: "−90°", en: "−90°" }, { ro: "180°", en: "180°" }], a: 0, e: { ro: "θcN = −arg Z0S, iar Z0S e aproape rezistivă (3R_N).", en: "θcN = −arg Z0S, and Z0S is nearly resistive (3R_N)." } },
    { q: { ro: "De ce punerile la pământ se tratează cu 67N și nu cu elementele de fază?", en: "Why are earth faults handled by 67N and not by the phase elements?" }, o: [{ ro: "Elementele de fază pot da decizii contradictorii", en: "The phase elements can give contradictory decisions" }, { ro: "67N e mai rapid", en: "67N is faster" }, { ro: "Elementele de fază nu văd curent", en: "Phase elements see no current" }, { ro: "Din cauza TC", en: "Because of the CT" }], a: 0, e: { ro: "Curenții fazelor sănătoase pot avea orice sens; laboratorul le arată „mixt”.", en: "Healthy-phase currents can point either way; the lab shows “mixed”." } },
    { q: { ro: "Cum se coordonează releele unei bucle cu o singură sursă?", en: "How are the relays of a single-source ring coordinated?" }, o: [{ ro: "Se deschide inelul la sursă și se reglează separat lanțul orar și cel antiorar", en: "Open the ring at the source and grade the clockwise and anticlockwise chains separately" }, { ro: "Toate cu același TMS", en: "All with the same TMS" }, { ro: "Numai cu trepte instantanee", en: "Only with instantaneous stages" }, { ro: "Nu se pot coordona", en: "They cannot be coordinated" }], a: 0, e: { ro: "Fiecare lanț se reglează ca o rețea radială (M03).", en: "Each chain is graded as a radial network (M03)." } },
    { q: { ro: "Care relee ale buclei pot fi nedirecționale?", en: "Which ring relays can be non-directional?" }, o: [{ ro: "Cele de pe barele sursei", en: "Those on the source bus" }, { ro: "Cele de la mijlocul buclei", en: "Those at mid-ring" }, { ro: "Toate", en: "All of them" }, { ro: "Niciunul", en: "None" }], a: 0, e: { ro: "Acolo curentul iese mereu din bare.", en: "There the current always leaves the bus." } },
    { q: { ro: "Care e dezavantajul coordonării buclei cu caracteristici dependente?", en: "What is the drawback of grading a ring with inverse curves?" }, o: [{ ro: "Defectele de lângă sursă se elimină lent", en: "Faults near the source are cleared slowly" }, { ro: "Releele nu sunt selective", en: "The relays are not selective" }, { ro: "Nu se poate calcula", en: "It cannot be calculated" }, { ro: "Cere TC de clasă PX", en: "It needs class PX CTs" }], a: 0, e: { ro: "Releele de lângă sursă au TMS-ul cel mai mare.", en: "The relays near the source have the largest TMS." } },
    { q: { ro: "Pe două linii paralele, cum se aleg releele de la capătul receptor?", en: "On two parallel lines, how are the receiving-end relays chosen?" }, o: [{ ro: "Direcționale, spre linie, cu temporizări mici", en: "Directional, into the line, with short delays" }, { ro: "Nedirecționale, cu TMS mare", en: "Non-directional, with large TMS" }, { ro: "Fără relee", en: "No relays" }, { ro: "Numai 67N", en: "Only 67N" }], a: 0, e: { ro: "Un defect pe o linie e alimentat și prin cealaltă, prin barele receptoare.", en: "A fault on one line is also fed through the other, via the receiving bus." } },
  ];
  function NUM() {
    const th = PR.rnd(30, 85, 1), rca = PR.pick([30, 45]), phi = PR.rnd(-60, 120, 1), R = PR.rnd(20, 120, 1), Xx = PR.rnd(2, 20, 1);
    return [
      { q: { ro: `Unghiul buclei de defect e ${th}°. Cu câte grade conduce I_L1 tensiunea U23?`, en: `The fault loop angle is ${th}°. By how many degrees does I_L1 lead U23?` }, u: "°", v: 90 - th, tol: 0.01, e: { ro: "Relația (3).", en: "Relation (3)." } },
      { q: { ro: `θc = ${rca}°, iar curentul conduce tensiunea de polarizare cu ${phi}°. Cât e marja până la limita zonei „înainte” (90° − |φ − θc|)?`, en: `θc = ${rca}° and the current leads the polarising voltage by ${phi}°. What is the margin to the forward-zone boundary (90° − |φ − θc|)?` }, u: "°", v: 90 - Math.abs(phi - rca), tol: 0.01, e: { ro: "Valoare negativă înseamnă „înapoi”.", en: "A negative value means “reverse”." } },
      { q: { ro: `Impedanța homopolară din spatele releului e ${R} + j${Xx} Ω. Ce unghi caracteristic θcN îi corespunde, în grade?`, en: `The zero-sequence impedance behind the relay is ${R} + j${Xx} Ω. Which characteristic angle θcN corresponds, in degrees?` }, u: "°", v: -(Math.atan2(Xx, R) * 180) / Math.PI, tol: 0.02, e: { ro: "θcN = −arg Z0S, relația (4).", en: "θcN = −arg Z0S, relation (4)." } },
    ];
  }

  /* ---------- pornire ---------- */
  ctlA = PR.controls(document.getElementById("controls"), SCHEMA, PA, () => { ctlA.sync(); renderA(); renderSheet(); });
  ctlB = PR.controls(document.getElementById("ringctl"), RSCHEMA, RB, () => { ctlB.sync(); renderB(); });
  document.getElementById("presets").innerHTML = PRESETS.map((x, i) => `<button class="btn" data-i="${i}">${bi(x[0])}</button>`).join("");
  document.getElementById("presets").onclick = (e) => { const b = e.target.closest("[data-i]"); if (!b) return; Object.assign(PA, PRESETS[+b.dataset.i][1]); ctlA.sync(); renderA(); };
  renderA(); renderB(); renderSheet();
  PR.onLang(() => { renderA(); renderB(); renderSheet(); });
  PR.math();
  PR.tabs(["lab", "reglaje", "teorie", "test"], "lab");
  PR.quiz(document.getElementById("qlist"), document.getElementById("score"), document.getElementById("q-reset"), { mcq: MCQ, num: NUM, pick: 8 });
})();
