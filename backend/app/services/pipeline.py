from __future__ import annotations

import hashlib
import json
import logging
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app import __version__
from app.core.config import Settings, get_settings
from app.db.models import (
    Account,
    Alert,
    AlertFeedback,
    AuthenticationEvent,
    Counterparty,
    DatasetManifest,
    Device,
    ModelRun,
    Transaction,
)
from app.detection.data_quality import validate_generated_data
from app.detection.explanations import DeterministicExplanationGenerator
from app.detection.features import MODEL_FEATURES, build_features
from app.detection.generator import generate_synthetic_data
from app.detection.metrics import evaluate_scores, population_stability_index
from app.detection.model import IsolationForestDetector
from app.detection.rules import RuleEngine
from app.detection.scoring import combine_scores

logger = logging.getLogger(__name__)


def _dataframe(session: Session, model: type[Any]) -> pd.DataFrame:
    rows = session.execute(select(model)).scalars().all()
    data = [
        {column.name: getattr(row, column.name) for column in model.__table__.columns}
        for row in rows
    ]
    return pd.DataFrame(data)


def reset_database(session: Session) -> None:
    for model in (
        AlertFeedback,
        Alert,
        ModelRun,
        DatasetManifest,
        AuthenticationEvent,
        Transaction,
        Device,
        Counterparty,
        Account,
    ):
        session.execute(delete(model))
    session.commit()


def persist_generated_data(
    session: Session,
    account_count: int,
    transaction_count: int,
    seed: int,
    reset: bool = True,
) -> dict[str, Any]:
    started = time.perf_counter()
    if reset:
        reset_database(session)
    generated = generate_synthetic_data(account_count, transaction_count, seed)
    quality = validate_generated_data(generated)
    session.bulk_insert_mappings(Account, generated.accounts)
    session.bulk_insert_mappings(Counterparty, generated.counterparties)
    session.bulk_insert_mappings(Device, generated.devices)
    session.bulk_insert_mappings(AuthenticationEvent, generated.authentication_events)
    session.bulk_insert_mappings(Transaction, generated.transactions)
    session.commit()
    scenarios = sorted(
        {row["synthetic_scenario"] for row in generated.transactions if row["synthetic_scenario"]}
    )

    def canonical(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        raise TypeError(f"Unsupported dataset value: {type(value)!r}")

    digest = hashlib.sha256(
        json.dumps(
            {
                "accounts": generated.accounts,
                "counterparties": generated.counterparties,
                "devices": generated.devices,
                "authentication_events": generated.authentication_events,
                "transactions": generated.transactions,
            },
            default=canonical,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    ).hexdigest()
    timestamps = [row["timestamp"] for row in generated.transactions]
    scenario_rows = sum(bool(row["synthetic_ground_truth"]) for row in generated.transactions)
    generated_at = datetime.now(UTC)
    manifest = DatasetManifest(
        id=f"DST-{generated_at.strftime('%Y%m%d%H%M%S%f')[:18]}",
        schema_version="1.0",
        generated_at=generated_at,
        seed=seed,
        account_count=len(generated.accounts),
        transaction_count=len(generated.transactions),
        scenario_count=len(scenarios),
        scenario_rows=scenario_rows,
        period_start=min(timestamps),
        period_end=max(timestamps),
        dataset_hash=digest,
        quality_report=quality,
    )
    session.add(manifest)
    session.commit()
    result = {
        "accounts": len(generated.accounts),
        "transactions": len(generated.transactions),
        "scenarios": scenarios,
        "seed": seed,
        "dataset_hash": digest,
        "manifest_id": manifest.id,
        "period_start": manifest.period_start,
        "period_end": manifest.period_end,
        "scenario_rows": scenario_rows,
        "quality": quality,
        "duration_seconds": round(time.perf_counter() - started, 3),
    }
    logger.info("Synthetic dataset generated", extra={"event": "data_generated"})
    return result


def build_feature_frame(session: Session) -> pd.DataFrame:
    return build_features(
        _dataframe(session, Transaction),
        _dataframe(session, Account),
        _dataframe(session, Counterparty),
        _dataframe(session, Device),
        _dataframe(session, AuthenticationEvent),
    )


def train_model(session: Session, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    clock_started = time.perf_counter()
    started = datetime.now(UTC)
    features = build_feature_frame(session)
    if features.empty:
        raise ValueError("No transactions available. Generate data before training.")
    manifest = session.scalar(
        select(DatasetManifest).order_by(DatasetManifest.generated_at.desc()).limit(1)
    )
    if manifest is None:
        raise ValueError("Dataset manifest not found. Generate data before training.")
    detector = IsolationForestDetector(seed=manifest.seed)
    detector.fit(features)
    artifact_path = settings.model_artifact_path.resolve()
    detector.save(artifact_path)
    artifact_hash = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
    feature_signature = hashlib.sha256("|".join(MODEL_FEATURES).encode()).hexdigest()
    run_id = f"RUN-{started.strftime('%Y%m%d%H%M%S%f')[:18]}"
    run = ModelRun(
        id=run_id,
        model_name="IsolationForest",
        model_version="1.0.0",
        seed=manifest.seed,
        dataset_hash=manifest.dataset_hash,
        feature_signature=feature_signature,
        code_version=__version__,
        started_at=started,
        completed_at=datetime.now(UTC),
        training_rows=len(features),
        scored_rows=0,
        feature_list=MODEL_FEATURES,
        parameters={"n_estimators": 180, "contamination": 0.08, "seed": manifest.seed},
        metrics={},
        artifact_path=str(artifact_path),
        artifact_hash=artifact_hash,
        status="trained",
    )
    session.add(run)
    session.commit()
    return {
        "model_run_id": run_id,
        "training_rows": len(features),
        "artifact_path": str(artifact_path),
        "artifact_hash": artifact_hash,
        "dataset_hash": manifest.dataset_hash,
        "feature_signature": feature_signature,
        "seed": manifest.seed,
        "duration_seconds": round(time.perf_counter() - clock_started, 3),
    }


def score_transactions(session: Session, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    started = time.perf_counter()
    latest_run = session.scalar(select(ModelRun).order_by(ModelRun.started_at.desc()).limit(1))
    if latest_run is None:
        raise ValueError("No trained model run found. Train the model before scoring.")
    artifact_path = Path(latest_run.artifact_path)
    if not artifact_path.exists():
        raise ValueError(f"Model artifact not found: {artifact_path}")
    features = build_feature_frame(session)
    detector = IsolationForestDetector.load(artifact_path)
    model_scores = detector.score(features)
    rule_engine = RuleEngine(settings.detection_config_path.resolve())
    scoring_config = rule_engine.config["scoring"]
    session.execute(delete(AlertFeedback))
    session.execute(delete(Alert))
    alerts: list[Alert] = []
    final_scores = np.zeros(len(features))
    alert_predictions = np.zeros(len(features), dtype=bool)
    severity_counts: dict[str, int] = {"baixa": 0, "média": 0, "alta": 0, "crítica": 0}
    explainer = DeterministicExplanationGenerator()
    for position, (_, row) in enumerate(features.iterrows()):
        rule_results = rule_engine.evaluate(row)
        rules_score = rule_engine.score(rule_results)
        risk = combine_scores(
            float(model_scores[position]),
            rules_score,
            rule_results,
            float(scoring_config["model_weight"]),
            float(scoring_config["rules_weight"]),
            float(scoring_config["severity_thresholds"]["medium"]),
            float(scoring_config["severity_thresholds"]["high"]),
            float(scoring_config["severity_thresholds"]["critical"]),
        )
        final_scores[position] = risk.final
        severity_counts[risk.severity] += 1
        eligible = risk.final >= float(scoring_config["alert_threshold"]) and (
            rules_score >= float(scoring_config["minimum_rules_for_alert"])
            or float(model_scores[position]) >= float(scoring_config["model_only_alert_threshold"])
        )
        alert_predictions[position] = eligible
        if not eligible:
            continue
        triggered = [result for result in rule_results if result.triggered]
        alerts.append(
            Alert(
                id=f"ALT-{len(alerts) + 1:08d}",
                transaction_id=str(row["id"]),
                account_id=str(row["account_id"]),
                created_at=datetime.now(UTC),
                risk_score=risk.final,
                severity=risk.severity,
                model_score=risk.model,
                rules_score=risk.rules,
                context_booster=risk.booster,
                reason_codes=[result.rule_id for result in triggered],
                explanation=explainer.generate(risk, rule_results),
                evidence=[result.to_dict() for result in triggered],
                status="novo",
                synthetic_ground_truth=bool(row["synthetic_ground_truth"]),
            )
        )
    session.add_all(alerts)
    metrics = evaluate_scores(
        features["synthetic_ground_truth"],
        final_scores,
        features["synthetic_scenario"],
        float(scoring_config["alert_threshold"]),
        alert_predictions,
    )
    metrics["severity_distribution"] = severity_counts
    metrics["score_distribution"] = [
        {
            "bucket": f"{start}-{start + 9}",
            "count": int(((final_scores >= start) & (final_scores < start + 10)).sum()),
        }
        for start in range(0, 100, 10)
    ]
    split = max(1, len(features) * 3 // 4)
    reference_amounts = features["amount"].to_numpy(dtype=float)[:split]
    recent_amounts = features["amount"].to_numpy(dtype=float)[split:]
    psi = population_stability_index(reference_amounts, recent_amounts)
    drift = "relevante" if psi >= 0.25 else "atenção" if psi >= 0.1 else "estável"
    metrics["monitoring"] = {
        "status": "available",
        "drift": drift,
        "indicators": [
            {"name": "PSI de valores", "value": round(psi, 4), "status": drift},
            {
                "name": "Diferença de média",
                "value": round(float(recent_amounts.mean() - reference_amounts.mean()), 2),
                "status": drift,
            },
            {
                "name": "Diferença de desvio-padrão",
                "value": round(float(recent_amounts.std() - reference_amounts.std()), 2),
                "status": drift,
            },
            {
                "name": "Taxa recente de alertas",
                "value": round(float(alert_predictions[split:].mean()), 4),
                "status": "informativo",
            },
        ],
        "disclaimer": (
            "Sinal estatístico exploratório sobre dados sintéticos; não representa "
            "conclusão definitiva de drift."
        ),
    }
    latest_run.scored_rows = len(features)
    latest_run.metrics = metrics
    latest_run.completed_at = datetime.now(UTC)
    latest_run.status = "completed"
    session.commit()
    return {
        "model_run_id": latest_run.id,
        "transactions_scored": len(features),
        "alerts": len(alerts),
        "metrics": metrics,
        "duration_seconds": round(time.perf_counter() - started, 3),
    }


def run_all(
    session: Session,
    account_count: int,
    transaction_count: int,
    seed: int,
    settings: Settings | None = None,
) -> dict[str, Any]:
    settings = settings or get_settings()
    generation = persist_generated_data(session, account_count, transaction_count, seed)
    training = train_model(session, settings)
    scoring = score_transactions(session, settings)
    return {"generation": generation, "training": training, "scoring": scoring}


def ensure_demo(session: Session, settings: Settings | None = None) -> dict[str, Any]:
    settings = settings or get_settings()
    transaction_total = session.scalar(select(func.count()).select_from(Transaction)) or 0
    if transaction_total > 0:
        return {"status": "already_initialized", "transactions": transaction_total}
    return run_all(
        session,
        settings.default_account_count,
        settings.default_transaction_count,
        settings.random_seed,
        settings,
    )


def write_performance_report(result: dict[str, Any], path: Path) -> None:
    content = {
        "measured_at": datetime.now(UTC).isoformat(),
        "environment": "local development runtime",
        **result,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
