# FraudLens

**Explainable payment anomaly investigation with synthetic data.**

[![Backend CI](https://github.com/GabrielBuck/fraudlens/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/GabrielBuck/fraudlens/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/GabrielBuck/fraudlens/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/GabrielBuck/fraudlens/actions/workflows/frontend-ci.yml)
[![Docker CI](https://github.com/GabrielBuck/fraudlens/actions/workflows/docker-ci.yml/badge.svg)](https://github.com/GabrielBuck/fraudlens/actions/workflows/docker-ci.yml)
[![Security](https://github.com/GabrielBuck/fraudlens/actions/workflows/security.yml/badge.svg)](https://github.com/GabrielBuck/fraudlens/actions/workflows/security.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-2f3336.svg)](LICENSE)

![FraudLens risk operations overview](docs/images/overview.png)

FraudLens is a full-stack reference implementation for investigating unusual payment behavior. A
deterministic pipeline generates fictitious accounts and transactions, builds causal features,
combines an unsupervised Isolation Forest with an explainable rule engine, and delivers a human
review workflow through a versioned API and an operations console.

> Scores rank investigation priority. They are not probabilities, proof of fraud, or grounds for an
> automated financial decision. All records, scenarios, labels, and measured results are synthetic.

[Architecture](docs/ARCHITECTURE.md) · [Model card](docs/MODEL_CARD.md) ·
[Performance](docs/PERFORMANCE.md) · [Security](docs/SECURITY.md) ·
[API after startup](http://localhost:8000/docs)

## System

```mermaid
flowchart LR
  G[Synthetic generator] --> Q[Quality checks + manifest]
  Q --> DB[(SQLite / PostgreSQL)]
  DB --> F[Causal features]
  F --> M[Isolation Forest]
  F --> R[Rule engine]
  M --> S[Investigation score]
  R --> S
  S --> A[Explainable alerts]
  A --> API[FastAPI /api/v1]
  API --> UI[Next.js operations console]
  UI --> H[Human review history]
  H --> DB
```

The architecture is a modular monolith: easy to run locally, explicit at domain boundaries, and
simple to evolve without premature distributed infrastructure. The evaluation domain owns synthetic
labels; operational API contracts and investigation screens never expose them.

## Key capabilities

- Deterministic generation of accounts, counterparties, devices, authentication events, and payments.
- Dataset manifest with seed, schema version, temporal range, row counts, quality checks, and SHA-256.
- Forty historical, temporal, behavioral, relationship, device, and geographic features.
- Causal windows (`shift(1)` and left-closed rolling windows) tested against future leakage.
- Reproducible Isolation Forest plus thirteen configurable and individually explainable rules.
- Transparent formula: `model × 0.55 + rules × 0.45 + contextual booster`, bounded to 0–100.
- Case files with evidence, nearby activity, account profile, relationship graph, and review history.
- URL-backed filters for dates, score, severity, status, signal, payment method, and ordering.
- Explicit Pydantic response models, structured errors, OpenAPI tags, and bounded pagination.
- Model/data monitoring with dataset hash, feature signature, artifact hash, metrics, and drift indicators.
- SQLite locally; PostgreSQL, non-root images, health checks, and persistence via Docker Compose.
- Ruff, mypy, pytest/coverage, ESLint, Prettier, TypeScript, Vitest, Playwright, audits, and CodeQL.

## Detection approach

`IsolationForest` maps low-density multivariate patterns to an anomaly contribution from 0 to 100.
The rule engine covers legible signals such as new devices, authentication failures, unusual values,
velocity, and incompatible travel. A contextual booster adds eight points only for configured signal
combinations. The final value is a queue-ranking mechanism, not a calibrated probability.

Default severity boundaries are `0–29 baixa`, `30–59 média`, `60–79 alta`, and `80–100 crítica`.
An alert is persisted only when the final score reaches 30 and either rules contribute at least 18 or
the model contribution reaches 95. Configuration lives in
[`backend/config/detection.yaml`](backend/config/detection.yaml).

## Data and synthetic evaluation

The standard reproducible run uses `1,000` accounts, `50,000` transactions, and seed `42`. Eight
controlled validation scenarios produce labels used only after scoring for aggregate evaluation.
The latest published measurements are documented in [docs/PERFORMANCE.md](docs/PERFORMANCE.md).
They validate pipeline behavior on constructed scenarios; they do not estimate performance in a
banking operation.

## Screenshots

| Investigation queue | Case file |
|---|---|
| ![Alert queue](docs/images/alerts.png) | ![Alert case file](docs/images/alert-detail.png) |

| Account profile | Model and data monitoring |
|---|---|
| ![Account behavioral profile](docs/images/account.png) | ![Model monitoring](docs/images/model.png) |

## Quick start

### Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

- Console: `http://localhost:3000`
- API: `http://localhost:8000`
- OpenAPI: `http://localhost:8000/docs`

The default profile uses SQLite and initializes a small dataset only when its persistent volume is
empty. PostgreSQL is optional:

```bash
docker compose --profile postgres up --build
```

Set `DATABASE_URL=postgresql+psycopg://fraudlens:fraudlens_local@postgres:5432/fraudlens` in your
local `.env` when using that profile.

### Local Windows

```powershell
.\scripts\setup.ps1
Set-Location backend
..\.venv\Scripts\python.exe -m alembic upgrade head
..\.venv\Scripts\python.exe -m app.cli pipeline run-all --accounts 120 --transactions 5000 --seed 42
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

In another terminal, run `npm run dev` from `frontend/`. On macOS/Linux, use
`./scripts/setup.sh` and `.venv/bin/python`.

### Standard dataset

```bash
cd backend
../.venv/bin/python -m app.cli pipeline run-all --accounts 1000 --transactions 50000 --seed 42
```

## Quality gates

```bash
# backend
cd backend
../.venv/bin/python -m ruff check .
../.venv/bin/python -m ruff format --check .
../.venv/bin/python -m mypy app
../.venv/bin/python -m pytest --cov=app --cov-fail-under=80
../.venv/bin/python -m pip_audit

# frontend
cd ../frontend
npm ci
npm run lint
npm run format:check
npm run typecheck
npm test -- --run
npm run build
npm run test:e2e
npm audit --audit-level=high
```

GitHub Actions also validates migrations, both container images, Compose configuration, service
startup, HTTP health, the principal Playwright journey, dependency audits, and CodeQL analysis.

## Repository structure

```text
backend/        detection, pipeline, persistence, API, migrations, and tests
frontend/       operations console, components, unit tests, and Playwright journeys
data/samples/   small inspectable synthetic sample
docs/           architecture, data, model, performance, security, and case study
scripts/        setup and reproducible command entry points
.github/        CI, dependency updates, templates, and security automation
```

## Security and responsible use

FraudLens contains no real customer data, identifiers, banking integrations, or external AI APIs.
CORS is restricted, inputs are validated, response headers are hardened, logs use correlation IDs,
and administrative endpoints are disabled by default. The local rate limiter is intentionally
single-process and does not replace an edge gateway. See [SECURITY.md](SECURITY.md) and the
[threat model](docs/THREAT_MODEL.md).

## Limitations and roadmap

- Synthetic scenarios are cleaner and less diverse than real-world abuse.
- Thresholds are heuristic and have not been calibrated for a live financial process.
- No authentication, corporate RBAC, immutable audit log, streaming, or automated blocking exists.
- PSI and aggregate monitoring are exploratory; production would materialize feature-level drift.
- Joblib is loaded only from the locally generated path; production requires signed artifacts and a registry.
- A production evolution would add temporal validation, governed feedback, SSO/RBAC, append-only audit,
  asynchronous idempotent scoring, distributed rate limits, and OpenTelemetry.

Contributions follow [CONTRIBUTING.md](CONTRIBUTING.md). Released under the [MIT License](LICENSE).
