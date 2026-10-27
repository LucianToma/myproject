"""Rulează toate verificările problemelor și regenerează toate figurile.

Utilizare:  python ruleaza_tot.py
Orice verificare eșuată oprește execuția cu mesaj de eroare.
"""

import contextlib
import io
import runpy
import sys
from pathlib import Path

AICI = Path(__file__).resolve().parent
sys.path.insert(0, str(AICI))

scripturi = sorted(AICI.glob("probleme_cap*.py")) + sorted(AICI.glob("figuri_*.py"))
total_ok = 0
for s in scripturi:
    print(f"\n=== {s.name} ===")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        runpy.run_path(str(s), run_name="__main__")
    text = buf.getvalue()
    print(text, end="")
    total_ok += text.count("[verificare OK]")
print(f"\nToate cele {len(scripturi)} scripturi au rulat fără erori; {total_ok} verificări trecute.")
