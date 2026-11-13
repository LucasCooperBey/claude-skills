#!/usr/bin/env bash
# build-index.sh, rebuild $WIKI_DIR/INDEX.md (default ./wiki).
# Runs scripts/wiki_index.py. No scheduler and no log file.

set -euo pipefail

WIKI="${WIKI_DIR:-./wiki}"
export WIKI_DIR="$WIKI"
HERE=$(dirname "$0")

if [[ -n "${PYTHON:-}" ]]; then
  PY="$PYTHON"
else
  PY="python3"
fi

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "ERROR: could not build index: python3 not found" >&2
  exit 1
fi

exec "$PY" "$HERE/wiki_index.py"
