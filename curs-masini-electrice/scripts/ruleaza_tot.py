"""Rulează toate verificările problemelor și regenerează toate figurile.

Utilizare:  python ruleaza_tot.py
Orice verificare eșuată oprește execuția cu mesaj de eroare.
"""

import runpy
import sys
from pathlib import Path

AICI = Path(__file__).resolve().parent
sys.path.insert(0, str(AICI))

scripturi = (sorted(AICI.glob("probleme_cap*.py")) + [AICI / "constructie.py"]
             + sorted(AICI.glob("figuri_*.py")))
for s in scripturi:
    print(f"\n=== {s.name} ===")
    runpy.run_path(str(s), run_name="__main__")
print(f"\nToate cele {len(scripturi)} scripturi au rulat fără erori.")
