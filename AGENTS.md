# FraudLens — Development Guide

## Repository objective

FraudLens is an educational, full-stack payment anomaly investigation platform. It generates only synthetic data, builds historical features, combines deterministic rules with an unsupervised anomaly model, and presents explainable alerts for analyst review.

## Architecture and stack

- `backend/`: Python 3.11+, FastAPI, Pydantic, SQLAlchemy, Alembic, pandas, scikit-learn, Typer, SQLite by default and optional PostgreSQL.
- `frontend/`: Next.js, React, strict TypeScript, Tailwind CSS, Recharts and accessible reusable components.
- `scripts/`: thin entry points for reproducible setup and pipeline operations.
- `docs/`: architecture, security, data, model and portfolio material.
- `.github/`: CI, security automation and contribution templates.

The primary flow is: synthetic generation → feature engineering → model training → rules/model scoring → persisted alerts → versioned API → dashboard.

## Main commands

- `make setup`: install and initialize the local project.
- `make pipeline`: generate demo data, train and score.
- `make backend` / `make frontend`: run each application.
- `make lint`, `make typecheck`, `make test`, `make security`, `make build`: required quality gates.
- Windows equivalents are documented in `README.md` and `scripts/setup.ps1`.

## Conventions

- Code, identifiers, commits and technical comments are in English.
- Product UI, API explanations and the main documentation are in Brazilian Portuguese.
- Use typed boundaries, small cohesive modules and explicit domain errors.
- API routes live under `/api/v1`; health remains at `/health`.
- List endpoints use bounded pagination and stable ordering.
- Use Conventional Commits and the `feature/fraudlens-mvp` branch for MVP work.

## Security and data rules

- Never commit secrets, tokens, credentials, real personal data or generated production-sized databases.
- The system must operate without paid services or external AI APIs.
- All identifiers and records are fictitious. Do not generate CPF, CNPJ or realistic personal identifiers.
- `synthetic_ground_truth` and `synthetic_scenario` are evaluation-only fields and must never enter model features.
- Validate all external input, restrict CORS, parameterize database access and avoid sensitive payload logging.
- Administrative endpoints are disabled by default and require an environment token when enabled.

## Detection and testing rules

- Historical features must be causal: a row can only use records strictly available at its timestamp.
- Every change to a detection rule, feature calculation, threshold or score formula requires a focused test.
- Unit-test detection components; integration-test persistence, API and CLI; smoke-test the principal dashboard journey.
- Critical detection modules target 90% coverage and the backend targets at least 80% meaningful coverage.
- Scores represent investigation priority, never a probability or proof of fraud.
- Explanations are deterministic, neutral and non-accusatory.

## Documentation rules

- Record material architecture, scoring, security and product decisions in `docs/`.
- Report only metrics actually measured on synthetic data and label their context.
- Keep Mermaid diagrams and command examples aligned with the implementation.
- Document limitations honestly; no production-readiness claims.

## Definition of done

A change is done when it is integrated, typed, error-handled, tested, linted, locally reproducible, documented where relevant, and contains neither secrets nor real data. UI work also includes loading, empty and error states plus keyboard-accessible interaction.

## Files requiring deliberate changes

Do not edit generated migrations, dependency lockfiles, CI workflows, score configuration, security policies or sample data casually. Model artifacts, local databases, caches, logs, coverage output and full generated datasets must stay untracked.
