#!/usr/bin/env bash
# Rulează toate verificările independente ale motoarelor de calcul.
# Cere: node, python3 cu numpy, scipy, pandapower.
set -euo pipefail
cd "$(dirname "$0")/.."
for f in m01_line_params m01_verify m02_verify m03_verify m04_verify m05_verify m06_verify; do
  echo "=== $f ==="
  python3 "verify/$f.py" | tail -n 3
done
