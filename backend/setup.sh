#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

if [ ! -f ../.env ]; then
  cp ../.env.example ../.env
fi

echo "Create databases (requires createdb on PATH):"
echo "  createdb hireus"
echo "  createdb hireus_test"
echo "Then update ../.env with your DB password."

alembic upgrade head

echo "Setup complete. Run: uvicorn app.main:app --reload"
