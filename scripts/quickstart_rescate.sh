#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if command -v python3.11 >/dev/null 2>&1; then
  PYTHON_BIN="python3.11"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "❌ No encuentro python3.11 ni python3. Instala Python 3.11 y vuelve a intentar." >&2
  exit 1
fi

echo "➡️ Usando: $PYTHON_BIN"

$PYTHON_BIN -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e '.[dev]'
python -m tennis_analytics.cli ingest --years 2023,2024,2025 --source jeff
python -m tennis_analytics.cli report-player --player "Carlos Alcaraz"
python -m tennis_analytics.cli report-top100
python -m tennis_analytics.cli report-coverage

echo
echo "✅ Terminado. Comprueba archivos:"
ls -lah db/tennis.duckdb reports/top100_summary.csv reports/coverage_report.md reports/players/carlos_alcaraz.md
