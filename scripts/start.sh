#!/bin/sh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p data
if [ -f .venv/bin/activate ]; then
  . .venv/bin/activate
fi
nohup python -m bridge >>data/bridge.log 2>&1 &
echo $! >data/pid
echo "started pid=$(cat data/pid)"
