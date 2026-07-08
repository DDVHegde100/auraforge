#!/usr/bin/env bash
# start local api + web ui
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -e "packages/engine[dev]" -q

if [[ ! -d packages/web/node_modules ]]; then
  (cd packages/web && npm install)
fi

cleanup() {
  # shellcheck disable=SC2046
  kill $(jobs -p) 2>/dev/null || true
}
trap cleanup EXIT

echo "api  → http://127.0.0.1:8787/health"
echo "web  → http://127.0.0.1:5173"
uvicorn auraforge_engine.api:app --app-dir packages/engine --host 127.0.0.1 --port 8787 &
(cd packages/web && npm run dev -- --host 127.0.0.1 --port 5173)
