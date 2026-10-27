// Verificare în browser: fiecare pagină se încarcă fără erori JavaScript, în RO și EN,
// la lățime de desktop (tema deschisă) și de telefon (tema întunecată), iar corpul paginii
// nu are derulare orizontală. Face capturi de ecran în tests/shots/.
//
// Rulare: node tests/browser_check.cjs [pagini...]   (implicit: toate paginile din site/)
const http = require("http");
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const ROOT = path.resolve(__dirname, "..", "site");
const SHOTS = path.resolve(__dirname, "shots");
fs.mkdirSync(SHOTS, { recursive: true });
const ALL = ["index.html", "m01/index.html", "m02/index.html", "m03/index.html", "m04/index.html"];
const PAGES = (process.argv.slice(2).length ? process.argv.slice(2) : ALL).filter((p) => fs.existsSync(path.join(ROOT, p)));
// copie locală KaTeX 0.16.9 (npm), opțională: KATEX_JS=/cale/katex.min.js
const KATEX = process.env.KATEX_JS && fs.existsSync(process.env.KATEX_JS) ? process.env.KATEX_JS : null;
const TYPES = { ".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8", ".json": "application/json", ".svg": "image/svg+xml" };

const server = http.createServer((req, res) => {
  const u = decodeURIComponent(req.url.split("?")[0].split("#")[0]);
  const f = path.join(ROOT, u === "/" ? "index.html" : u);
  if (!f.startsWith(ROOT) || !fs.existsSync(f)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { "Content-Type": TYPES[path.extname(f)] || "application/octet-stream" });
  fs.createReadStream(f).pipe(res);
});

(async () => {
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const port = server.address().port, base = `http://127.0.0.1:${port}/`;
  const problems = [];
  const browser = await chromium.launch();
  for (const p of PAGES) {
    const tabs = p === "index.html" ? [""] : ["lab", "reglaje", "teorie", "test"];
    for (const lang of ["ro", "en"]) {
      for (const [width, tag] of [[1280, "desk"], [390, "phone"]]) {
        const ctx = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: width > 500 ? "light" : "dark" });
        await ctx.addInitScript((l) => { try { localStorage.setItem("pr-lang", l); } catch (e) {} }, lang);
        // resursele externe (fonturi, KaTeX) nu sunt accesibile în containerul de test: le refuzăm explicit
        await ctx.route("**/*", (route) => {
          const u = route.request().url();
          if (u.startsWith(base)) return route.continue();
          // KaTeX de pe cdnjs: îl servim din copia locală (aceeași versiune), dacă există
          if (KATEX && /cdnjs\.cloudflare\.com\/ajax\/libs\/KaTeX\/0\.16\.9\/katex\.min\.js$/.test(u)) return route.fulfill({ path: KATEX, contentType: "text/javascript" });
          return route.abort();
        });
        const pg = await ctx.newPage();
        const errs = [];
        pg.on("pageerror", (e) => errs.push(`pageerror: ${e.message}`));
        pg.on("console", (m) => { if (m.type() === "error" && !/net::|Failed to load resource/.test(m.text())) errs.push(`console.error: ${m.text()}`); });
        for (const tab of tabs) {
          await pg.goto(base + p + (tab ? "#" + tab : ""));
          await pg.waitForTimeout(250);
          const [sw, cw] = await pg.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]);
          if (sw > cw + 1) problems.push(`${p}#${tab} ${lang} ${tag}: derulare orizontală ${sw} > ${cw}`);
          const name = p.replace(/\//g, "_").replace(".html", "") + (tab ? "_" + tab : "") + `_${lang}_${tag}.png`;
          await pg.screenshot({ path: path.join(SHOTS, name), fullPage: true });
        }
        if (p !== "index.html") {
          await pg.goto(base + p + "#lab");
          for (const sel of ["#presets [data-i]", "#ftype [data-f]", "#fcase [data-c]", "[data-act]"]) {
            for (const el of await pg.$$(sel)) { try { await el.click({ timeout: 300 }); await pg.waitForTimeout(25); } catch (e) {} }
          }
          // fiecare select și fiecare câmp numeric din panoul de control
          for (const el of await pg.$$("#controls select")) {
            const opts = await el.$$eval("option", (o) => o.map((x) => x.value));
            for (const v of opts) { try { await el.selectOption(v, { timeout: 300 }); await pg.waitForTimeout(20); } catch (e) {} }
          }
          await pg.goto(base + p + "#test");
          for (const el of (await pg.$$(".opt")).slice(0, 40)) { try { await el.click({ timeout: 200 }); } catch (e) {} }
          for (const el of await pg.$$(".q.num")) {
            try { await (await el.$("input")).fill("1,5"); await (await el.$(".btn")).click({ timeout: 200 }); } catch (e) {}
          }
        }
        errs.forEach((e) => problems.push(`${p} ${lang} ${tag}: ${e}`));
        await ctx.close();
      }
    }
  }
  await browser.close();
  server.close();
  console.log("Pagini verificate: " + PAGES.join(", "));
  if (problems.length) { console.log("PROBLEME:"); problems.forEach((x) => console.log("  - " + x)); process.exit(1); }
  console.log("Fără erori JavaScript și fără derulare orizontală.");
})();
