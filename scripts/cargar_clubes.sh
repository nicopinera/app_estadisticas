#!/usr/bin/env bash
set -euo pipefail

# Arrancar siempre desde src/, sin importar desde donde se llame el script
cd "$(dirname "${BASH_SOURCE[0]}")/../src"

# Atajo: "stats club add ..." en vez de "uv run python main.py club add ..."
stats() { uv run python main.py "$@"; }

for club in "Racing" "Banco Cordoba" "Dante Alghieri" "Independiente Cosquin" "Deportivo Norte" "Universitario" "Municipalidad" "Atenas B" "P. Velez Sarsfield" "Matienzo B" "Pilar Sport" "Gral. Paz Juniors"; do
    stats club add --nombre "$club"
done
