// Randează cu KaTeX toate formulele (atributele data-tex) din paginile date și raportează erorile.
// Rulare: KATEX_DIR=/cale/node_modules/katex node tests/katex_check.cjs site/m01/index.html ...
const fs = require("fs");
const katex = require(process.env.KATEX_DIR || "katex");
let bad = 0, n = 0;
for (const f of process.argv.slice(2)) {
  const html = fs.readFileSync(f, "utf8");
  const re = /data-tex="([^"]*)"/g;
  let m;
  while ((m = re.exec(html))) {
    n++;
    const tex = m[1].replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"');
    try { katex.renderToString(tex, { throwOnError: true, output: "mathml" }); }
    catch (e) { bad++; console.log(`${f}: ${e.message}\n   ${tex}`); }
  }
}
console.log(`${n} formule verificate, ${bad} erori`);
process.exit(bad ? 1 : 0);
