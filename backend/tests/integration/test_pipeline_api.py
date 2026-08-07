from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.db.session import Base, get_db
from app.main import app
from app.services.pipeline import run_all


def test_end_to_end_pipeline_and_api(tmp_path: Path) -> None:
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    settings = Settings(
        database_url=str(engine.url),
        model_artifact_path=tmp_path / "model.joblib",
        default_account_count=8,
        default_transaction_count=120,
    )
    with Session(engine) as session:
        result = run_all(session, 8, 120, 42, settings)
        assert result["generation"]["transactions"] == 120
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
    assert client.get("/api/v1/meta").json()["data_classification"] == "100% sintético"
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
    any_alert = client.get("/api/v1/alerts?page_size=1").json()["items"][0]
    detail = client.get(f"/api/v1/alerts/{any_alert['id']}")
    assert detail.status_code == 200
    transaction_id = any_alert["transaction"]["id"]
    account_id = any_alert["account_id"]
    assert client.get("/api/v1/transactions?page_size=5").status_code == 200
    assert client.get(f"/api/v1/transactions/{transaction_id}").json()["id"] == transaction_id
    assert client.get("/api/v1/accounts?page_size=5").status_code == 200
    assert client.get(f"/api/v1/accounts/{account_id}").json()["id"] == account_id
    assert client.get(f"/api/v1/accounts/{account_id}/timeline?limit=5").status_code == 200
    assert client.get(f"/api/v1/accounts/{account_id}/behavior").status_code == 200
    network = client.get(f"/api/v1/accounts/{account_id}/network?limit=5")
    assert network.status_code == 200
    assert network.json()["nodes"]
    runs = client.get("/api/v1/model-runs").json()
    assert runs
    latest = client.get("/api/v1/model-runs/latest").json()
    assert client.get(f"/api/v1/model-runs/{latest['id']}").status_code == 200
    assert client.get("/api/v1/model-monitoring").status_code == 200
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
    missing = client.get("/api/v1/alerts/ALT-DOES-NOT-EXIST")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "ALERT_NOT_FOUND"
    assert client.get("/api/v1/transactions/TX-MISSING").status_code == 404
    assert client.get("/api/v1/accounts/ACC-MISSING").status_code == 404
    assert client.get("/api/v1/model-runs/RUN-MISSING").status_code == 404
    app.dependency_overrides.clear()
