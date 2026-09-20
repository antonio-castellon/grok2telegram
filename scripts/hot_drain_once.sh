#!/bin/sh
# One-shot: print pending inbox as JSON (for Mesa hot linger).
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [ -f .venv/bin/activate ]; then . .venv/bin/activate; fi
python -m bridge.drain
