from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.models import ModelRun
from app.db.session import Base, get_db
from app.main import app
from app.services import pipeline
from app.services.pipeline import run_all

EVALUATION_LABELS = {"synthetic_ground_truth", "synthetic_scenario"}


def _assert_operational_payload_has_no_labels(value: object) -> None:
    if isinstance(value, dict):
        assert EVALUATION_LABELS.isdisjoint(value)
        for nested in value.values():
            _assert_operational_payload_has_no_labels(nested)
    elif isinstance(value, list):
        for nested in value:
            _assert_operational_payload_has_no_labels(nested)


def test_end_to_end_pipeline_and_api(tmp_path: Path, monkeypatch) -> None:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    settings = Settings(
        database_url=str(engine.url),
        model_artifact_path=tmp_path / "model.joblib",
        detection_config_path=Path(__file__).parents[2] / "config" / "detection.yaml",
        default_account_count=8,
        default_transaction_count=120,
    )
    monkeypatch.setattr(
        pipeline,
        "__file__",
        "/opt/venv/lib/python3.12/site-packages/app/services/pipeline.py",
    )
    with Session(engine) as session:
        result = run_all(session, 8, 120, 42, settings)
        assert result["generation"]["transactions"] == 120
        assert result["generation"]["quality"]["status"] == "passed"
        assert len(result["generation"]["dataset_hash"]) == 64
        assert result["scoring"]["alerts"] > 0
        assert 0 <= result["scoring"]["metrics"]["recall"] <= 1

    def override_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)
    health = client.get("/health")
    assert health.status_code == 200
    overview = client.get("/api/v1/overview")
    assert overview.status_code == 200
    assert overview.json()["kpis"]["transactions"] == 120
    assert overview.json()["kpis"]["comparison_available"] is False
    assert overview.json()["kpis"]["volume_change"] is None
    meta = client.get("/api/v1/meta").json()
    assert meta["data_classification"] == "100% sintético"
    assert meta["dataset"]["seed"] == 42
    assert meta["dataset"]["quality_report"]["status"] == "passed"
    assert meta["model"]["feature_signature"]
    assert meta["model"]["dataset_hash"] == meta["dataset"]["dataset_hash"]
    for endpoint in (
        "/api/v1/overview/timeseries",
        "/api/v1/overview/payment-methods",
        "/api/v1/overview/severity",
        "/api/v1/overview/reason-codes",
    ):
        response = client.get(endpoint)
        assert response.status_code == 200
        assert response.json()
    alerts = client.get("/api/v1/alerts?page_size=5&severity=crítica")
    assert alerts.status_code == 200
    assert alerts.json()["pages"] >= 1
    _assert_operational_payload_has_no_labels(alerts.json())
    any_alert = client.get("/api/v1/alerts?page_size=1").json()["items"][0]
    detail = client.get(f"/api/v1/alerts/{any_alert['id']}")
    assert detail.status_code == 200
    assert "context_booster" in detail.json()
    _assert_operational_payload_has_no_labels(detail.json())
    transaction_id = any_alert["transaction"]["id"]
    account_id = any_alert["account_id"]
    transactions = client.get("/api/v1/transactions?page_size=5")
    assert transactions.status_code == 200
    _assert_operational_payload_has_no_labels(transactions.json())
    transaction = client.get(f"/api/v1/transactions/{transaction_id}")
    assert transaction.json()["id"] == transaction_id
    _assert_operational_payload_has_no_labels(transaction.json())
    account_list = client.get("/api/v1/accounts?page_size=5")
    assert account_list.status_code == 200
    assert "highest_priority" in account_list.json()["items"][0]
    assert client.get(f"/api/v1/accounts/{account_id}").json()["id"] == account_id
    assert client.get(f"/api/v1/accounts/{account_id}/timeline?limit=5").status_code == 200
    assert client.get(f"/api/v1/accounts/{account_id}/behavior").status_code == 200
    network = client.get(f"/api/v1/accounts/{account_id}/network?limit=5")
    assert network.status_code == 200
    assert network.json()["nodes"]
    runs = client.get("/api/v1/model-runs").json()
    assert runs
    latest = client.get("/api/v1/model-runs/latest").json()
    assert latest["seed"] == 42
    assert len(latest["id"]) <= ModelRun.__table__.c.id.type.length
    assert latest["artifact_hash"]
    assert "artifact_path" not in latest
    assert latest["started_at"].endswith("Z")
    assert latest["code_version"] == "1.0.0"
    assert client.get(f"/api/v1/model-runs/{latest['id']}").status_code == 200
    assert client.get("/api/v1/model-monitoring").status_code == 200
    manifest = client.get("/api/v1/dataset-manifests/latest")
    assert manifest.status_code == 200
    assert manifest.json()["transaction_count"] == 120
    assert client.post("/api/v1/admin/train").status_code == 404
    update = client.patch(
        f"/api/v1/alerts/{any_alert['id']}",
        json={"status": "em análise", "reviewer_note": "Revisão em teste"},
    )
    assert update.json()["status"] == "em análise"
    feedback = client.post(
        f"/api/v1/alerts/{any_alert['id']}/feedback",
        json={"classification": "falso positivo", "comment": "Contexto validado no teste."},
    )
    assert feedback.status_code == 201
    history = client.get(f"/api/v1/alerts/{any_alert['id']}").json()["feedback"]
    assert history[-1]["comment"] == "Contexto validado no teste."
    missing = client.get("/api/v1/alerts/ALT-DOES-NOT-EXIST")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "ALERT_NOT_FOUND"
    assert client.get("/api/v1/transactions/TX-MISSING").status_code == 404
    assert client.get("/api/v1/accounts/ACC-MISSING").status_code == 404
    assert client.get("/api/v1/model-runs/RUN-MISSING").status_code == 404
    invalid_range = client.get(
        "/api/v1/overview?start_at=2026-07-01T00:00:00Z&end_at=2026-06-01T00:00:00Z"
    )
    assert invalid_range.status_code == 422
    assert invalid_range.json()["error"]["code"] == "INVALID_DATE_RANGE"
    for header in (
        "x-correlation-id",
        "x-content-type-options",
        "x-frame-options",
        "referrer-policy",
        "permissions-policy",
        "content-security-policy",
    ):
        assert header in overview.headers
    openapi = client.get("/openapi.json").json()
    assert openapi["paths"]["/api/v1/alerts"]["get"]["responses"]["200"]["content"]
    app.dependency_overrides.clear()


def test_dynamic_overview_periods_shift_with_dataset(tmp_path: Path) -> None:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'period.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    settings = Settings(
        database_url=str(engine.url),
        model_artifact_path=tmp_path / "period-model.joblib",
        detection_config_path=Path(__file__).parents[2] / "config" / "detection.yaml",
    )
    with Session(engine) as session:
        run_all(session, 8, 120, 7, settings)

    def override_db():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)
    default = client.get("/api/v1/overview").json()
    assert default["period_end"].startswith("2026-06")
    narrow = client.get(
        "/api/v1/overview?start_at=2026-06-28T00:00:00Z&end_at=2026-07-01T00:00:00Z"
    ).json()
    assert narrow["kpis"]["transactions"] < default["kpis"]["transactions"]
    app.dependency_overrides.clear()
