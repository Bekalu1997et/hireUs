#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

if [ ! -f "$BACKEND_DIR/.env" ] && [ -f "$ROOT_DIR/.env" ]; then
  cp "$ROOT_DIR/.env" "$BACKEND_DIR/.env"
fi

if [ -f "$BACKEND_DIR/.venv/bin/activate" ]; then
  source "$BACKEND_DIR/.venv/bin/activate"
fi

echo "Starting backend..."
pushd "$BACKEND_DIR" >/dev/null
  alembic upgrade head
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
popd >/dev/null

echo "Starting frontend..."
pushd "$FRONTEND_DIR" >/dev/null
  if [ ! -d node_modules ]; then
    npm install
  fi
  npm run dev -- --hostname 0.0.0.0 --port 3000 &
FRONTEND_PID=$!
popd >/dev/null

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"

wait
