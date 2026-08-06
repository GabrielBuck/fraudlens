PYTHON ?= python
NPM ?= npm

.PHONY: install setup db-init seed train score pipeline backend frontend dev test test-backend test-frontend lint format typecheck security build screenshots clean demo

install:
	$(PYTHON) -m pip install -e "backend[dev]"
	cd frontend && $(NPM) install

setup: install db-init

db-init:
	cd backend && $(PYTHON) -m alembic upgrade head

seed:
	$(PYTHON) scripts/generate_data.py --accounts 1000 --transactions 50000 --seed 42

train:
	$(PYTHON) scripts/train_model.py

score:
	$(PYTHON) scripts/score_transactions.py

pipeline:
	cd backend && $(PYTHON) -m app.cli pipeline run-all

backend:
	cd backend && $(PYTHON) -m uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && $(NPM) run dev

dev:
	docker compose up --build

test: test-backend test-frontend

test-backend:
	cd backend && $(PYTHON) -m pytest --cov=app --cov-report=term-missing

test-frontend:
	cd frontend && $(NPM) test -- --run

lint:
	cd backend && $(PYTHON) -m ruff check .
	cd frontend && $(NPM) run lint

format:
	cd backend && $(PYTHON) -m ruff format .
	cd frontend && $(NPM) run format

typecheck:
	cd backend && $(PYTHON) -m mypy app
	cd frontend && $(NPM) run typecheck

security:
	cd backend && $(PYTHON) -m pip_audit
	cd frontend && $(NPM) audit --audit-level=high

build:
	cd frontend && $(NPM) run build

screenshots:
	cd frontend && $(NPM) run screenshots

clean:
	$(PYTHON) scripts/clean.py

demo:
	cd backend && $(PYTHON) -m app.cli demo reset

