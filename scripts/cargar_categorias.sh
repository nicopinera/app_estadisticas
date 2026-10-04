#!/usr/bin/env bash
set -euo pipefail

# Arrancar siempre desde src/, sin importar desde donde se llame el script
cd "$(dirname "${BASH_SOURCE[0]}")/../src"

# Atajo: "stats club add ..." en vez de "uv run python main.py club add ..."
stats() { uv run python main.py "$@"; }

for categoria in  "LIGA PROXIMO" "MAYORES MASCULINOS"; do
    stats categoria add --nombre "$categoria"
done
