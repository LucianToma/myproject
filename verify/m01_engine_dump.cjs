// Rulează motorul din pagina modulului 01 pe o matrice de cazuri și scrie rezultatele în JSON,
// ca să fie comparate cu calculul independent din verify/m01_verify.py.
const M = require("../site/m01/engine.js");
const X = require("../site/assets/cx.js");
const out = [];
const neutrals = ["R", "L", "I", "S"];
const lines = ["ol70", "ol120", "cab185"];
for (const neutral of neutrals) for (const line of lines) for (const kase of ["max", "min"]) for (const type of M.FAULTS) for (const x of [0, 7.5, 20]) for (const Rf of [0, 25]) {
  const p = { ...M.DEFAULTS, neutral, line, ...M.LINES[line] };
  delete p.ro; delete p.en;
  const r = M.compute(p, kase, type, x, Rf);
  out.push({
    p: { ...p }, kase, type, x, Rf,
    Iabc: r.Iabc.map((z) => [z.re, z.im]),
    Vabc: r.Vabc.map((z) => [z.re, z.im]),
    Ihv: r.Ihv.map((z) => [z.re, z.im]),
    Ik: r.Ik,
  });
}
const p0 = { ...M.DEFAULTS };
out.push({ table: M.settingsTable(p0), hv: { max: M.hvBus(p0, "max"), min: M.hvBus(p0, "min") }, p: p0 });
process.stdout.write(JSON.stringify(out));
