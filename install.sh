#!/usr/bin/env bash
# Set up a virtual environment and install paper-to-code dependencies.
set -euo pipefail

cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" >/dev/null 2>&1; then
    PYTHON=python
fi

echo "Creating virtual environment in .venv ..."
"$PYTHON" -m venv .venv

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Done. Next steps:"
echo "  source .venv/bin/activate"
echo "  python scripts/fetch_paper.py 1706.03762 --out runs/transformer"
