/* Protecții în rețelele electrice — funcții comune pentru pagini:
   limba (RO/EN), tab-uri, formule KaTeX, controale, teste, copiere tabele, ajutoare SVG. */
(function () {
  "use strict";
  const PR = (window.PR = window.PR || {});
  const LS = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) {} },
  };
  PR.LS = LS;

  /* ---------------- limba ---------------- */
  const navRo = (navigator.language || "").toLowerCase().startsWith("ro");
  PR.lang = LS.get("pr-lang") || (navRo ? "ro" : "en");
  if (PR.lang !== "ro" && PR.lang !== "en") PR.lang = "ro";
  const root = document.documentElement;
  root.dataset.lang = PR.lang;
  root.lang = PR.lang;
  PR.t = (o, en) => (typeof o === "string" ? (PR.lang === "en" && en != null ? en : o) : o ? o[PR.lang] ?? o.ro : "");
  /* ambele variante în HTML, ascunse prin CSS după limbă */
  PR.bi = (o, en) => (typeof o === "string" ? `<span lang="ro">${o}</span><span lang="en">${en ?? o}</span>` : `<span lang="ro">${o.ro}</span><span lang="en">${o.en ?? o.ro}</span>`);
  PR.setLang = (l) => {
    if (l === PR.lang) return;
    PR.lang = l; root.dataset.lang = l; root.lang = l; LS.set("pr-lang", l);
    document.querySelectorAll("[data-langbtn]").forEach((b) => b.setAttribute("aria-pressed", b.dataset.langbtn === l));
    document.dispatchEvent(new CustomEvent("langchange", { detail: l }));
  };
  PR.onLang = (fn) => document.addEventListener("langchange", fn);

  /* ---------------- numere ---------------- */
  PR.loc = () => (PR.lang === "ro" ? "ro-RO" : "en-GB");
  /* separatorul de mii este spațiul îngust (stil SI, ISO 80000-1), ca să nu fie confundat cu virgula zecimală */
  const NF = {};
  PR.fmt = (x, d = 2) => {
    if (x == null || !isFinite(x)) return "—";
    const key = PR.loc() + d;
    const nf = NF[key] || (NF[key] = new Intl.NumberFormat(PR.loc(), { minimumFractionDigits: d, maximumFractionDigits: d }));
    return nf.formatToParts(Number(x)).map((q) => (q.type === "group" ? "\u202f" : q.type === "minusSign" ? "−" : q.value)).join("");
  };
  /* cifre semnificative, pentru valori de ordine diferite */
  PR.sig = (x, s = 3) => {
    if (x == null || !isFinite(x)) return "—";
    if (x === 0) return "0";
    const d = Math.max(0, s - 1 - Math.floor(Math.log10(Math.abs(x))));
    return PR.fmt(x, Math.min(d, 6));
  };
  PR.num = (s) => parseFloat(String(s).trim().replace(/\s/g, "").replace(",", "."));

  /* ---------------- antet: buton limbă ---------------- */
  PR.header = () => {
    document.querySelectorAll("[data-langbtn]").forEach((b) => {
      b.setAttribute("aria-pressed", b.dataset.langbtn === PR.lang);
      b.addEventListener("click", () => PR.setLang(b.dataset.langbtn));
    });
  };

  /* ---------------- tab-uri ---------------- */
  PR.tabs = (ids, def) => {
    const nav = document.querySelector("nav.tabs");
    const show = (t, push) => {
      if (!ids.includes(t)) t = def;
      nav.querySelectorAll("button").forEach((b) => b.setAttribute("aria-selected", b.dataset.tab === t));
      ids.forEach((id) => { const s = document.getElementById(id); if (s) s.hidden = id !== t; });
      if (push && location.hash.slice(1) !== t) { try { history.replaceState(null, "", "#" + t); } catch (e) { location.hash = t; } }
      document.dispatchEvent(new CustomEvent("tabchange", { detail: t }));
    };
    nav.addEventListener("click", (e) => { const b = e.target.closest("button[data-tab]"); if (b) show(b.dataset.tab, true); });
    window.addEventListener("hashchange", () => show(location.hash.slice(1), false));
    show(location.hash.slice(1) || def, false);
  };

  /* ---------------- formule ---------------- */
  PR.math = (scope) => {
    (scope || document).querySelectorAll("[data-tex]").forEach((el) => {
      if (el.dataset.done) return;
      try {
        window.katex.render(el.dataset.tex, el, { output: "mathml", throwOnError: false, displayMode: el.classList.contains("d") });
      } catch (e) { el.textContent = el.dataset.tex; el.classList.add("mono"); }
      el.dataset.done = 1;
    });
  };

  /* ---------------- controale (rail) ----------------
     schema: [{g:{ro,en}, col, open, items:[{k, l:{ro,en}, u, step, min, max, range:[a,b], chk, sel:[[v,{ro,en}]]}]}] */
  PR.controls = (host, schema, state, onChange) => {
    const narrow = window.innerWidth < 920; // pe telefon grupurile pornesc închise, ca rezultatele să fie aproape
    host.innerHTML = schema.map((g) => `<details class="grp" ${g.open && (!narrow || g.openNarrow !== false) ? "open" : ""}><summary>${g.col ? `<span class="swatch" style="background:var(${g.col})"></span>` : ""}${PR.bi(g.g)}</summary>${g.items.map((it) => {
      const id = "in-" + it.k;
      if (it.chk) return `<div class="knob check"><label for="${id}">${PR.bi(it.l)}</label><input type="checkbox" id="${id}" data-k="${it.k}"></div>`;
      if (it.sel) return `<div class="knob ${it.wide ? "wide" : ""}"><label for="${id}">${PR.bi(it.l)}</label><select id="${id}" data-k="${it.k}">${it.sel.map(([v, t]) => `<option value="${v}" data-ro="${t.ro}" data-en="${t.en}">${PR.t(t)}</option>`).join("")}</select></div>`;
      return `<div class="knob"><label for="${id}">${PR.bi(it.l)}${it.u ? `<small>${it.u}</small>` : ""}</label><input type="number" inputmode="decimal" id="${id}" data-k="${it.k}" step="${it.step ?? "any"}" ${it.min != null ? `min="${it.min}"` : ""} ${it.max != null ? `max="${it.max}"` : ""}>${it.range ? `<input type="range" id="${id}-r" data-k="${it.k}" min="${it.range[0]}" max="${it.range[1]}" step="${it.step ?? "any"}" aria-label="${PR.t(it.l)}">` : ""}</div>`;
    }).join("")}</details>`).join("");
    const sync = (skipEl) => {
      host.querySelectorAll("[data-k]").forEach((el) => {
        if (el === skipEl) return;
        const v = state[el.dataset.k];
        if (el.type === "checkbox") el.checked = !!v;
        else if (el.tagName === "SELECT") el.value = v;
        else el.value = typeof v === "number" ? +v.toPrecision(6) : v;
      });
    };
    host.addEventListener("input", (e) => {
      const k = e.target.dataset.k; if (!k) return;
      let v = e.target.type === "checkbox" ? e.target.checked : e.target.tagName === "SELECT" ? e.target.value : PR.num(e.target.value);
      if (typeof v === "number" && !isFinite(v)) return;
      state[k] = v; sync(e.target); onChange(k);
    });
    PR.onLang(() => host.querySelectorAll("option[data-ro]").forEach((o) => (o.textContent = o.dataset[PR.lang])));
    sync();
    return { sync: () => sync() };
  };

  /* ---------------- copiere tabel (TSV, se lipește direct în Excel) ---------------- */
  PR.copyTSV = (rows, btn) => {
    const txt = rows.map((r) => r.map((c) => String(c ?? "")).join("\t")).join("\n");
    const done = () => {
      let s = btn.parentElement.querySelector(".copied");
      if (!s) { s = document.createElement("span"); s.className = "copied"; btn.after(s); }
      s.textContent = PR.t("copiat", "copied");
      setTimeout(() => (s.textContent = ""), 2200);
    };
    const fallback = () => {
      const ta = document.createElement("textarea");
      ta.value = txt; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); done(); } catch (e) {}
      ta.remove();
    };
    try { navigator.clipboard.writeText(txt).then(done, fallback); } catch (e) { fallback(); }
  };
  /* valoare numerică pentru export: zecimale cu virgulă în RO, ca să o recunoască Excel-ul românesc */
  PR.xnum = (x, d = 3) => (x == null || !isFinite(x) ? "" : PR.lang === "ro" ? x.toFixed(d).replace(".", ",") : x.toFixed(d));

  /* ---------------- teste ----------------
     mcq: [{q:{ro,en}, o:[{ro,en}...], a:index, e:{ro,en}}]
     num(): [{q:{ro,en}, u:"kA", v:valoare, e:{ro,en}, tol:0.02}] */
  PR.quiz = (host, scoreEl, resetBtn, { mcq, num, pick = 8 }) => {
    let qs = [], right = 0;
    const build = () => {
      right = 0;
      const m = [...mcq].sort(() => Math.random() - 0.5).slice(0, pick).map((q) => {
        const order = q.o.map((_, i) => i).sort(() => Math.random() - 0.5);
        return { ...q, kind: "mcq", order };
      });
      qs = m.concat(num().map((q) => ({ ...q, kind: "num" })));
      render();
    };
    const render = () => {
      host.innerHTML = qs.map((q, i) => {
        if (q.kind === "mcq") {
          return `<div class="q" data-i="${i}"><div class="qt">${i + 1}. ${PR.bi(q.q)}</div><div class="opts">${q.order.map((j) => {
            const cls = q.done ? (j === q.a ? "right" : j === q.chosen ? "wrong" : "") : "";
            return `<button class="opt ${cls}" data-j="${j}" ${q.done ? "disabled" : ""}>${PR.bi(q.o[j])}</button>`;
          }).join("")}</div><div class="expl" ${q.done ? "" : "hidden"}>${PR.bi(q.e)}</div></div>`;
        }
        const tol = q.tol ?? 0.02;
        return `<div class="q num" data-i="${i}"><div class="qt">${i + 1}. ${PR.bi(q.q)}</div><div class="num-row"><input type="text" inputmode="decimal" id="nq${i}" aria-label="${PR.t("Răspuns", "Answer")}" value="${q.given ?? ""}" ${q.done ? "disabled" : ""} style="${q.done ? `border-color:var(${q.ok ? "--ok" : "--trip"})` : ""}"><span class="mono">${q.u}</span><button class="btn primary" ${q.done ? "disabled" : ""}>${PR.bi("Verifică", "Check")}</button></div><div class="expl" ${q.done ? "" : "hidden"}>${PR.bi(q.e)} ${PR.bi("Rezultat", "Result")}: <b class="mono">${PR.sig(q.v, 4)} ${q.u}</b> (${PR.bi("toleranță", "tolerance")} ${Math.round(tol * 100)} %).</div></div>`;
      }).join("");
      scoreEl.textContent = `${right} / ${qs.length}`;
    };
    host.addEventListener("click", (e) => {
      const qe = e.target.closest(".q"); if (!qe) return;
      const q = qs[+qe.dataset.i]; if (!q || q.done) return;
      const opt = e.target.closest(".opt");
      if (opt && q.kind === "mcq") {
        q.chosen = +opt.dataset.j; q.done = true; if (q.chosen === q.a) right++;
      } else if (e.target.closest(".btn") && q.kind === "num") {
        const inp = qe.querySelector("input"), v = PR.num(inp.value);
        if (!isFinite(v)) { inp.focus(); return; }
        q.given = inp.value; q.ok = Math.abs(v - q.v) <= (q.tol ?? 0.02) * Math.abs(q.v); q.done = true; if (q.ok) right++;
      } else return;
      render();
    });
    resetBtn.addEventListener("click", build);
    build();
  };
  /* numere aleatoare „rotunde” pentru problemele numerice */
  PR.rnd = (a, b, step) => Math.round((a + Math.random() * (b - a)) / step) * step;
  PR.pick = (arr) => arr[Math.floor(Math.random() * arr.length)];

  /* ---------------- SVG ---------------- */
  PR.esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;");
  /* gradații „frumoase” pe axă liniară */
  PR.niceTicks = (min, max, n = 5) => {
    const span = max - min || 1, raw = span / n, mag = Math.pow(10, Math.floor(Math.log10(raw)));
    const step = [1, 2, 2.5, 5, 10].map((m) => m * mag).find((s) => span / s <= n) || 10 * mag;
    const out = []; for (let v = Math.ceil(min / step) * step; v <= max + step * 1e-9; v += step) out.push(+v.toPrecision(12));
    return out;
  };
  /* decade pentru axe logaritmice */
  PR.logDecades = (min, max) => { const out = []; for (let e = Math.floor(Math.log10(min)); e <= Math.ceil(Math.log10(max)); e++) out.push(e); return out; };

  /* săgeată de fazor: din (x0,y0) până la (x1,y1) */
  PR.arrow = (x0, y0, x1, y1, color, w = 2, dash = "") => {
    const dx = x1 - x0, dy = y1 - y0, L = Math.hypot(dx, dy);
    if (L < 1) return "";
    const ux = dx / L, uy = dy / L, h = Math.min(9, L * 0.4), hw = h * 0.5;
    const bx = x1 - ux * h, by = y1 - uy * h;
    return `<line x1="${x0.toFixed(1)}" y1="${y0.toFixed(1)}" x2="${bx.toFixed(1)}" y2="${by.toFixed(1)}" stroke="${color}" stroke-width="${w}" ${dash ? `stroke-dasharray="${dash}"` : ""}/><path d="M${x1.toFixed(1)} ${y1.toFixed(1)} L${(bx - uy * hw).toFixed(1)} ${(by + ux * hw).toFixed(1)} L${(bx + uy * hw).toFixed(1)} ${(by - ux * hw).toFixed(1)} Z" fill="${color}"/>`;
  };

  document.addEventListener("DOMContentLoaded", PR.header);
})();
