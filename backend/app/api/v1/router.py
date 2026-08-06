from __future__ import annotations

import secrets
from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any, Literal

import numpy as np
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app import __version__
from app.core.config import Settings, get_settings
from app.core.errors import DomainError, NotFoundError
from app.db.models import Account, Alert, AlertFeedback, ModelRun, Transaction
from app.db.session import get_db
from app.detection.metrics import population_stability_index
from app.schemas.api import AdminRequest, AlertUpdate, FeedbackCreate
from app.services.pipeline import persist_generated_data, score_transactions, train_model

router = APIRouter(prefix="/api/v1")
Db = Annotated[Session, Depends(get_db)]


def _transaction_payload(row: Transaction) -> dict[str, Any]:
    return {column.name: getattr(row, column.name) for column in Transaction.__table__.columns}


def _alert_payload(alert: Alert, transaction: Transaction | None = None) -> dict[str, Any]:
    payload = {column.name: getattr(alert, column.name) for column in Alert.__table__.columns}
    if transaction is not None:
        payload["transaction"] = _transaction_payload(transaction)
    return payload


@router.get("/meta")
def meta() -> dict[str, Any]:
    return {
        "name": "FraudLens",
        "subtitle": "Intelligent Payment Anomaly Radar",
        "version": __version__,
        "language": "pt-BR",
        "data_classification": "100% sintético",
        "disclaimer": (
            "Scores indicam prioridade de investigação, não probabilidade ou prova de fraude."
        ),
    }


@router.get("/overview")
def overview(db: Db) -> dict[str, Any]:
    total_transactions = db.scalar(select(func.count()).select_from(Transaction)) or 0
    volume = db.scalar(select(func.coalesce(func.sum(Transaction.amount), 0.0))) or 0.0
    total_alerts = db.scalar(select(func.count()).select_from(Alert)) or 0
    critical = (
        db.scalar(select(func.count()).select_from(Alert).where(Alert.severity == "crítica")) or 0
    )
    high = db.scalar(select(func.count()).select_from(Alert).where(Alert.severity == "alta")) or 0
    accounts = db.scalar(select(func.count()).select_from(Account)) or 0
    previous_cutoff = datetime(2026, 5, 31, tzinfo=UTC)
    recent_volume = (
        db.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
                Transaction.timestamp >= previous_cutoff
            )
        )
        or 0.0
    )
    previous_volume = (
        db.scalar(
            select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
                Transaction.timestamp < previous_cutoff
            )
        )
        or 0.0
    )
    variation = (
        ((recent_volume - previous_volume) / previous_volume * 100) if previous_volume else 0.0
    )
    recent_rows = db.execute(
        select(Alert, Transaction)
        .join(Transaction, Alert.transaction_id == Transaction.id)
        .order_by(Alert.created_at.desc(), Alert.risk_score.desc())
        .limit(6)
    ).all()
    return {
        "kpis": {
            "monitored_volume": round(float(volume), 2),
            "transactions": int(total_transactions),
            "alerts": int(total_alerts),
            "critical_alerts": int(critical),
            "high_critical_alerts": int(high + critical),
            "alert_rate": round(total_alerts / max(total_transactions, 1) * 100, 2),
            "accounts": int(accounts),
            "volume_change": round(variation, 2),
        },
        "recent_alerts": [_alert_payload(alert, transaction) for alert, transaction in recent_rows],
        "updated_at": datetime.now(UTC),
    }


@router.get("/overview/timeseries")
def overview_timeseries(db: Db) -> list[dict[str, Any]]:
    rows = db.execute(
        select(
            func.date(Transaction.timestamp).label("date"),
            func.sum(Transaction.amount).label("volume"),
            func.count(Transaction.id).label("transactions"),
            func.count(Alert.id).label("alerts"),
        )
        .outerjoin(Alert, Alert.transaction_id == Transaction.id)
        .group_by(func.date(Transaction.timestamp))
        .order_by(func.date(Transaction.timestamp))
    ).all()
    return [
        {
            "date": str(row.date),
            "volume": round(float(row.volume or 0), 2),
            "transactions": int(row.transactions),
            "alerts": int(row.alerts),
        }
        for row in rows
    ]


@router.get("/overview/payment-methods")
def payment_methods(db: Db) -> list[dict[str, Any]]:
    rows = db.execute(
        select(
            Transaction.payment_method,
            func.count(Transaction.id),
            func.count(Alert.id),
            func.sum(Transaction.amount),
        )
        .outerjoin(Alert, Alert.transaction_id == Transaction.id)
        .group_by(Transaction.payment_method)
        .order_by(func.count(Alert.id).desc())
    ).all()
    return [
        {"method": row[0], "transactions": row[1], "alerts": row[2], "volume": round(row[3], 2)}
        for row in rows
    ]


@router.get("/overview/severity")
def severity_distribution(db: Db) -> list[dict[str, Any]]:
    rows = db.execute(
        select(Alert.severity, func.count()).group_by(Alert.severity).order_by(func.count().desc())
    ).all()
    return [{"severity": severity, "count": count} for severity, count in rows]


@router.get("/overview/reason-codes")
def reason_codes(db: Db) -> list[dict[str, Any]]:
    counter: Counter[str] = Counter()
    for codes in db.scalars(select(Alert.reason_codes)):
        counter.update(codes or [])
    return [{"reason_code": code, "count": count} for code, count in counter.most_common(10)]


@router.get("/alerts")
def list_alerts(
    db: Db,
    severity: str | None = None,
    status: str | None = None,
    account_id: str | None = None,
    scenario: str | None = None,
    payment_method: str | None = None,
    min_score: float | None = Query(default=None, ge=0, le=100),
    reason_code: str | None = None,
    search: str | None = Query(default=None, max_length=80),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort: Literal["risk_desc", "risk_asc", "newest", "oldest"] = "risk_desc",
) -> dict[str, Any]:
    filters = []
    if severity:
        filters.append(Alert.severity == severity)
    if status:
        filters.append(Alert.status == status)
    if account_id:
        filters.append(Alert.account_id == account_id)
    if scenario:
        filters.append(Transaction.synthetic_scenario == scenario)
    if payment_method:
        filters.append(Transaction.payment_method == payment_method)
    if min_score is not None:
        filters.append(Alert.risk_score >= min_score)
    if reason_code:
        filters.append(Alert.reason_codes.contains(reason_code))
    if search:
        term = f"%{search.strip()}%"
        filters.append(
            or_(
                Alert.id.ilike(term), Alert.account_id.ilike(term), Alert.transaction_id.ilike(term)
            )
        )
    base = select(Alert, Transaction).join(Transaction, Alert.transaction_id == Transaction.id)
    count_query = (
        select(func.count())
        .select_from(Alert)
        .join(Transaction, Alert.transaction_id == Transaction.id)
    )
    if filters:
        base = base.where(and_(*filters))
        count_query = count_query.where(and_(*filters))
    ordering: ColumnElement[Any]
    if sort == "risk_desc":
        ordering = Alert.risk_score.desc()
    elif sort == "risk_asc":
        ordering = Alert.risk_score.asc()
    elif sort == "newest":
        ordering = Transaction.timestamp.desc()
    else:
        ordering = Transaction.timestamp.asc()
    total = db.scalar(count_query) or 0
    rows = db.execute(base.order_by(ordering).offset((page - 1) * page_size).limit(page_size)).all()
    return {
        "items": [_alert_payload(alert, transaction) for alert, transaction in rows],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": (total + page_size - 1) // page_size,
    }


@router.get("/alerts/{alert_id}")
def get_alert(alert_id: str, db: Db) -> dict[str, Any]:
    row = db.execute(
        select(Alert, Transaction)
        .join(Transaction, Alert.transaction_id == Transaction.id)
        .where(Alert.id == alert_id)
    ).first()
    if row is None:
        raise NotFoundError("ALERT_NOT_FOUND", "Alerta não encontrado.")
    alert, transaction = row
    payload = _alert_payload(alert, transaction)
    payload["feedback"] = [
        {column.name: getattr(item, column.name) for column in AlertFeedback.__table__.columns}
        for item in db.scalars(
            select(AlertFeedback)
            .where(AlertFeedback.alert_id == alert_id)
            .order_by(AlertFeedback.created_at)
        )
    ]
    payload["nearby_transactions"] = [
        _transaction_payload(item)
        for item in db.scalars(
            select(Transaction)
            .where(
                Transaction.account_id == alert.account_id,
                Transaction.timestamp.between(
                    transaction.timestamp - timedelta(hours=2),
                    transaction.timestamp + timedelta(hours=2),
                ),
            )
            .order_by(Transaction.timestamp)
            .limit(30)
        )
    ]
    return payload


@router.patch("/alerts/{alert_id}")
def update_alert(alert_id: str, update: AlertUpdate, db: Db) -> dict[str, Any]:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise NotFoundError("ALERT_NOT_FOUND", "Alerta não encontrado.")
    alert.status = update.status
    alert.reviewer_note = update.reviewer_note
    alert.reviewed_at = datetime.now(UTC)
    db.commit()
    return _alert_payload(alert)


@router.post("/alerts/{alert_id}/feedback", status_code=201)
def add_feedback(alert_id: str, feedback: FeedbackCreate, db: Db) -> dict[str, Any]:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise NotFoundError("ALERT_NOT_FOUND", "Alerta não encontrado.")
    item = AlertFeedback(
        id=f"FDB-{secrets.token_hex(6).upper()}",
        alert_id=alert_id,
        classification=feedback.classification,
        comment=feedback.comment,
        created_at=datetime.now(UTC),
    )
    alert.status = (
        feedback.classification if feedback.classification != "inconclusivo" else "em análise"
    )
    alert.reviewed_at = item.created_at
    db.add(item)
    db.commit()
    return {column.name: getattr(item, column.name) for column in AlertFeedback.__table__.columns}


@router.get("/transactions")
def list_transactions(
    db: Db,
    account_id: str | None = None,
    payment_method: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    filters = []
    if account_id:
        filters.append(Transaction.account_id == account_id)
    if payment_method:
        filters.append(Transaction.payment_method == payment_method)
    query = select(Transaction)
    count_query = select(func.count()).select_from(Transaction)
    if filters:
        query = query.where(*filters)
        count_query = count_query.where(*filters)
    total = db.scalar(count_query) or 0
    items = db.scalars(
        query.order_by(Transaction.timestamp.desc()).offset((page - 1) * page_size).limit(page_size)
    )
    return {"items": [_transaction_payload(item) for item in items], "total": total, "page": page}


@router.get("/transactions/{transaction_id}")
def get_transaction(transaction_id: str, db: Db) -> dict[str, Any]:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise NotFoundError("TRANSACTION_NOT_FOUND", "Transação não encontrada.")
    return _transaction_payload(transaction)


@router.get("/accounts")
def list_accounts(
    db: Db,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    total = db.scalar(select(func.count()).select_from(Account)) or 0
    rows = db.scalars(
        select(Account).order_by(Account.id).offset((page - 1) * page_size).limit(page_size)
    )
    return {
        "items": [
            {column.name: getattr(row, column.name) for column in Account.__table__.columns}
            for row in rows
        ],
        "total": total,
        "page": page,
    }


@router.get("/accounts/{account_id}")
def get_account(account_id: str, db: Db) -> dict[str, Any]:
    account = db.get(Account, account_id)
    if account is None:
        raise NotFoundError("ACCOUNT_NOT_FOUND", "Conta não encontrada.")
    payload = {column.name: getattr(account, column.name) for column in Account.__table__.columns}
    payload["transaction_count"] = (
        db.scalar(
            select(func.count())
            .select_from(Transaction)
            .where(Transaction.account_id == account_id)
        )
        or 0
    )
    payload["alert_count"] = (
        db.scalar(select(func.count()).select_from(Alert).where(Alert.account_id == account_id))
        or 0
    )
    return payload


@router.get("/accounts/{account_id}/timeline")
def account_timeline(
    account_id: str, db: Db, limit: int = Query(default=100, ge=1, le=300)
) -> list[dict[str, Any]]:
    if db.get(Account, account_id) is None:
        raise NotFoundError("ACCOUNT_NOT_FOUND", "Conta não encontrada.")
    alerts = {
        item.transaction_id: item
        for item in db.scalars(select(Alert).where(Alert.account_id == account_id))
    }
    rows = db.scalars(
        select(Transaction)
        .where(Transaction.account_id == account_id)
        .order_by(Transaction.timestamp.desc())
        .limit(limit)
    )
    return [
        {
            **_transaction_payload(row),
            "alert": _alert_payload(alerts[row.id]) if row.id in alerts else None,
        }
        for row in rows
    ]


@router.get("/accounts/{account_id}/behavior")
def account_behavior(account_id: str, db: Db) -> dict[str, Any]:
    account = db.get(Account, account_id)
    if account is None:
        raise NotFoundError("ACCOUNT_NOT_FOUND", "Conta não encontrada.")
    rows = db.scalars(
        select(Transaction)
        .where(Transaction.account_id == account_id)
        .order_by(Transaction.timestamp)
    )
    transactions = list(rows)
    amounts = np.array([row.amount for row in transactions], dtype=float)
    methods = Counter(row.payment_method for row in transactions)
    hours = Counter(row.timestamp.hour for row in transactions)
    return {
        "average_amount": round(float(amounts.mean()), 2) if len(amounts) else 0,
        "median_amount": round(float(np.median(amounts)), 2) if len(amounts) else 0,
        "p95_amount": round(float(np.quantile(amounts, 0.95)), 2) if len(amounts) else 0,
        "payment_methods": [
            {"method": key, "count": value} for key, value in methods.most_common()
        ],
        "common_hours": [{"hour": key, "count": value} for key, value in sorted(hours.items())],
        "usual_window": [account.usual_transaction_hour_start, account.usual_transaction_hour_end],
    }


@router.get("/accounts/{account_id}/network")
def account_network(
    account_id: str, db: Db, limit: int = Query(default=40, ge=5, le=100)
) -> dict[str, Any]:
    if db.get(Account, account_id) is None:
        raise NotFoundError("ACCOUNT_NOT_FOUND", "Conta não encontrada.")
    rows = db.scalars(
        select(Transaction)
        .where(Transaction.account_id == account_id)
        .order_by(Transaction.timestamp.desc())
        .limit(limit)
    )
    transactions = list(rows)
    nodes: dict[str, dict[str, Any]] = {
        account_id: {"id": account_id, "label": account_id, "type": "account", "risk": 0}
    }
    edges = []
    alert_by_tx = {
        a.transaction_id: a for a in db.scalars(select(Alert).where(Alert.account_id == account_id))
    }
    for row in transactions:
        risk = alert_by_tx[row.id].risk_score if row.id in alert_by_tx else 0
        nodes[row.counterparty_id] = {
            "id": row.counterparty_id,
            "label": row.counterparty_id,
            "type": "counterparty",
            "risk": risk,
        }
        nodes[row.device_id] = {
            "id": row.device_id,
            "label": row.device_id,
            "type": "device",
            "risk": risk,
        }
        edges.append(
            {
                "id": f"{row.id}-cp",
                "source": account_id,
                "target": row.counterparty_id,
                "amount": row.amount,
            }
        )
        edges.append(
            {
                "id": f"{row.id}-dev",
                "source": row.device_id,
                "target": account_id,
                "amount": row.amount,
            }
        )
    return {"nodes": list(nodes.values()), "edges": edges, "limited_to": limit}


@router.get("/model-runs")
def list_model_runs(db: Db) -> list[dict[str, Any]]:
    rows = db.scalars(select(ModelRun).order_by(ModelRun.started_at.desc()).limit(20))
    return [
        {column.name: getattr(row, column.name) for column in ModelRun.__table__.columns}
        for row in rows
    ]


@router.get("/model-runs/latest")
def latest_model_run(db: Db) -> dict[str, Any]:
    row = db.scalar(select(ModelRun).order_by(ModelRun.started_at.desc()).limit(1))
    if row is None:
        raise NotFoundError("MODEL_RUN_NOT_FOUND", "Execução de modelo não encontrada.")
    return {column.name: getattr(row, column.name) for column in ModelRun.__table__.columns}


@router.get("/model-runs/{model_run_id}")
def get_model_run(model_run_id: str, db: Db) -> dict[str, Any]:
    row = db.get(ModelRun, model_run_id)
    if row is None:
        raise NotFoundError("MODEL_RUN_NOT_FOUND", "Execução de modelo não encontrada.")
    return {column.name: getattr(row, column.name) for column in ModelRun.__table__.columns}


@router.get("/model-monitoring")
def model_monitoring(db: Db) -> dict[str, Any]:
    transactions = list(db.scalars(select(Transaction).order_by(Transaction.timestamp)))
    alerts = list(db.scalars(select(Alert)))
    if len(transactions) < 2:
        return {"status": "insufficient_data", "drift": "estável", "indicators": []}
    split = max(1, len(transactions) * 3 // 4)
    reference = np.array([row.amount for row in transactions[:split]])
    recent = np.array([row.amount for row in transactions[split:]])
    psi = population_stability_index(reference, recent)
    drift = "relevante" if psi >= 0.25 else "atenção" if psi >= 0.1 else "estável"
    recent_cutoff = transactions[split].timestamp
    timestamp_by_id = {transaction.id: transaction.timestamp for transaction in transactions}
    recent_alert_rate = sum(
        timestamp_by_id[alert.transaction_id] >= recent_cutoff
        for alert in alerts
        if alert.transaction_id in timestamp_by_id
    ) / max(len(recent), 1)
    return {
        "status": "available",
        "drift": drift,
        "indicators": [
            {"name": "PSI de valores", "value": round(psi, 4), "status": drift},
            {
                "name": "Diferença de média",
                "value": round(float(recent.mean() - reference.mean()), 2),
                "status": drift,
            },
            {
                "name": "Diferença de desvio-padrão",
                "value": round(float(recent.std() - reference.std()), 2),
                "status": drift,
            },
            {
                "name": "Taxa recente de alertas",
                "value": round(recent_alert_rate, 4),
                "status": "informativo",
            },
        ],
        "disclaimer": (
            "Sinal estatístico exploratório; não representa conclusão definitiva de drift."
        ),
    }


def _authorize_admin(settings: Settings, token: str | None) -> None:
    if not settings.enable_admin_api:
        raise DomainError("ADMIN_API_DISABLED", "API administrativa desabilitada.", 404)
    if (
        not settings.admin_api_token
        or not token
        or not secrets.compare_digest(token, settings.admin_api_token)
    ):
        raise DomainError("ADMIN_UNAUTHORIZED", "Token administrativo inválido.", 401)


@router.post("/admin/generate")
def admin_generate(
    payload: AdminRequest,
    db: Db,
    x_admin_token: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    settings = get_settings()
    _authorize_admin(settings, x_admin_token)
    return persist_generated_data(db, payload.accounts, payload.transactions, payload.seed)


@router.post("/admin/train")
def admin_train(db: Db, x_admin_token: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    settings = get_settings()
    _authorize_admin(settings, x_admin_token)
    return train_model(db, settings)


@router.post("/admin/score")
def admin_score(db: Db, x_admin_token: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    settings = get_settings()
    _authorize_admin(settings, x_admin_token)
    return score_transactions(db, settings)
