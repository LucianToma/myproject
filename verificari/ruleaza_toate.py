"""Rulează toate verificările numerice ale cursului și afișează un rezumat.

Utilizare (din rădăcina depozitului):
    python3 verificari/ruleaza_toate.py

Codul de ieșire este 0 doar dacă toate verificările trec.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import comun  # noqa: E402
import v02_fundamente  # noqa: E402
import v04_redresoare  # noqa: E402
import v05_dc_dc  # noqa: E402
import v06_invertoare  # noqa: E402
import v07_pierderi  # noqa: E402
import v08_exercitii  # noqa: E402

MODULE = [
    ("Modulul 2 - Fundamente", v02_fundamente),
    ("Modulul 4 - Redresoare", v04_redresoare),
    ("Modulul 5 - Convertoare DC-DC", v05_dc_dc),
    ("Modulul 6 - Invertoare", v06_invertoare),
    ("Modulele 1, 3, 7 - Randament, pierderi, termic", v07_pierderi),
    ("Modulul 8 - Exerciții", v08_exercitii),
]


def main():
    rezumat = []
    for nume, modul in MODULE:
        print("\n" + "#" * 78 + f"\n# {nume}\n" + "#" * 78)
        start = len(comun.REZULTATE)
        t0 = time.time()
        modul.main()
        rez = comun.REZULTATE[start:]
        rezumat.append((nume, sum(ok for _, ok in rez), len(rez), time.time() - t0))

    print("\n" + "=" * 78 + "\nREZUMAT\n" + "=" * 78)
    for nume, trecute, total, durata in rezumat:
        print(f"  {nume:<50s} {trecute:3d}/{total:<3d} ({durata:5.1f} s)")
    esecuri = [d for d, ok in comun.REZULTATE if not ok]
    total = len(comun.REZULTATE)
    print(f"\n  TOTAL: {total - len(esecuri)}/{total} verificări trecute")
    for d in esecuri:
        print(f"  EȘEC: {d}")
    return 0 if not esecuri else 1


if __name__ == "__main__":
    sys.exit(main())
