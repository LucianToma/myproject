"""Pregătește o copie a site-ului pentru previzualizarea ca Artifact pe claude.ai.

Pagina principală a unui Artifact e învelită automat într-un schelet HTML, deci din index.html se scot
doctype, <html>, <head>, <body> și metadatele pe care le adaugă scheletul. Celelalte pagini (modulele)
rămân documente complete. Rulare: python3 tools/build_artifact.py <folder-destinație>
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "site"
out = Path(sys.argv[1]).resolve()
if out.exists():
    shutil.rmtree(out)
shutil.copytree(ROOT, out)
html = (ROOT / "index.html").read_text(encoding="utf-8")
for pat in [r"<!doctype html>\s*", r"<html[^>]*>\s*", r"</html>\s*", r"<head>\s*", r"</head>\s*", r"<body>\s*", r"</body>\s*",
            r'<meta charset="utf-8">\s*', r'<meta name="viewport"[^>]*>\s*']:
    html = re.sub(pat, "", html, flags=re.I)
(out / "index.html").write_text(html, encoding="utf-8")
files = sorted(str(p.relative_to(out)) for p in out.rglob("*") if p.is_file() and p.relative_to(out) != Path("index.html"))
print("\n".join(files))
