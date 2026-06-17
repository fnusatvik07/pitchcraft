#!/usr/bin/env bash
# DeckForge setup — run once on a fresh machine. Idempotent.
#   bash setup.sh
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$HERE/.venv"

echo "DeckForge setup"
echo "  root: $HERE"

# 1) pick a stable Python (3.14 is flaky for python-pptx/lxml)
PYBIN=""
for c in python3.13 python3.12 python3.11 python3; do command -v "$c" >/dev/null 2>&1 && { PYBIN="$c"; break; }; done
[ -z "$PYBIN" ] && { echo "  ERROR: python3 not found. Install Python 3.11–3.13."; exit 1; }
echo "  python: $($PYBIN --version)"

# 2) venv + python deps
[ -x "$VENV/bin/python" ] || { echo "  creating venv…"; "$PYBIN" -m venv "$VENV"; }
"$VENV/bin/pip" -q install --upgrade pip >/dev/null 2>&1 || true
echo "  installing python deps…"
"$VENV/bin/pip" -q install -r "$HERE/requirements.txt"
"$VENV/bin/python" -m playwright install chromium 2>&1 | tail -1 || echo "  WARN: chromium install failed"

# 3) node deps (Mermaid diagrams + pdf.js QA render)
if command -v npm >/dev/null 2>&1; then
  echo "  installing node deps…"
  ( cd "$HERE/engine/node" && npm install --silent >/dev/null 2>&1 ) && echo "  ok: node deps" || echo "  WARN: npm install failed (diagrams/QA-render need these)"
else
  echo "  WARN: node/npm not found — install Node 18+ for diagrams & browser QA render."
fi

# 4) external binaries
ok=1
need(){ command -v "$1" >/dev/null 2>&1 && echo "  ok: $1" || { echo "  MISSING: $1 — $2"; ok=0; }; }
echo "checking system binaries…"
need soffice  "LibreOffice — needed to convert .pptx→PDF (brew install --cask libreoffice / apt install libreoffice)"
need pdftoppm "poppler — QA/handout rasterize (brew install poppler / apt install poppler-utils)"
command -v rsvg-convert >/dev/null 2>&1 && echo "  ok: rsvg-convert (optional)" || echo "  optional: rsvg-convert (librsvg) — only for fetched icons"

echo
[ "$ok" -eq 1 ] && echo "Setup complete." || echo "Setup finished — install the MISSING binaries above, then re-run."
echo "Smoke test:  \"$VENV/bin/python\" engine/html_to_pptx.py examples/four-day-week out/Example.pptx"
