#!/usr/bin/env sh
set -eu
PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$PROJECT_ROOT"
python3 -m venv .venv
.venv/bin/python -m pip install -e "backend[dev]"
cd backend
../.venv/bin/python -m alembic upgrade head
cd ../frontend
npm install
printf '%s\n' "FraudLens configurado. Execute o pipeline antes de iniciar as aplicações."

