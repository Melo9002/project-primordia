#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"
PRIMORDIA_PYTHON=".venv/bin/python"

if [ ! -x "$PRIMORDIA_PYTHON" ]; then
    echo "[PRIMORDIA] Creating a local Python environment..."
    if ! command -v python3 >/dev/null 2>&1; then
        echo "[PRIMORDIA] Python 3.12 or newer is required." >&2
        exit 1
    fi
    python3 -m venv .venv
    echo "[PRIMORDIA] Installing dependencies..."
    "$PRIMORDIA_PYTHON" -m pip install -e ".[dev]"
fi

exec "$PRIMORDIA_PYTHON" -m primordia "$@"
