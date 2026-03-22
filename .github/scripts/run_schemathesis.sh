#!/usr/bin/env bash
set -euo pipefail

if command -v uv >/dev/null 2>&1; then
  exec uv run --extra dev python .github/scripts/run_schemathesis.py "$@"
fi

if command -v python >/dev/null 2>&1; then
  exec python .github/scripts/run_schemathesis.py "$@"
fi

if command -v python3 >/dev/null 2>&1; then
  exec python3 .github/scripts/run_schemathesis.py "$@"
fi

echo "Neither uv nor Python interpreter found."
exit 127
