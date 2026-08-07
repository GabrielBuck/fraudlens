#!/usr/bin/env sh
set -eu
alembic upgrade head
if [ "${AUTO_SEED:-false}" = "true" ]; then
  python -m app.cli pipeline ensure-demo
fi
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
