from __future__ import annotations

import secrets
from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any, Literal

import numpy as np
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import ColumnElement

from app import __version__
from app.core.config import Settings, get_settings
from app.core.errors import DomainError, NotFoundError
from app.db.models import Account, Alert, AlertFeedback, DatasetManifest, ModelRun, Transaction
from app.db.session import get_db
from app.schemas.api import (
    AccountBehaviorResponse,
    AccountListResponse,
    AccountResponse,
    AdminRequest,
    AlertDetailResponse,
    AlertListResponse,
    AlertResponse,
    AlertUpdate,
    DatasetManifestResponse,
    FeedbackCreate,
    FeedbackResponse,
    MetaResponse,
    ModelRunResponse,
    MonitoringResponse,
    NetworkResponse,
    OverviewResponse,
    PaymentMethodSummary,
    ReasonSummary,
    SeveritySummary,
    TimelineItem,
    TimeseriesPoint,
    TransactionListResponse,
    TransactionResponse,
)
from app.services.pipeline import persist_generated_data, score_transactions, train_model

router = APIRouter(prefix="/api/v1")
Db = Annotated[Session, Depends(get_db)]


def _transaction_payload(row: Transaction) -> dict[str, Any]:
    return TransactionResponse.model_validate(row).model_dump()


def _alert_payload(alert: Alert, transaction: Transaction | None = None) -> dict[str, Any]:
    payload = AlertResponse.model_validate(alert).model_dump()
    if transaction is not None:
        payload["transaction"] = _transaction_payload(transaction)
    return payload


def _model_payload(row: ModelRun) -> dict[str, Any]:
    return ModelRunResponse.model_validate(row).model_dump()


def _pagination(total: int, page: int, page_size: int) -> dict[str, int]:
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": (total + page_size - 1) // page_size,
    }


def _resolve_period(
    db: Session, start_at: datetime | None, end_at: datetime | None
) -> tuple[datetime | None, datetime | None]:
    latest = db.scalar(select(func.max(Transaction.timestamp)))
    if latest is None:
        return None, None
    period_end = end_at or latest
    period_start = start_at or period_end - timedelta(days=90)
    if period_start > period_end:
        raise DomainError("INVALID_DATE_RANGE", "A data inicial deve preceder a data final.", 422)
    return period_start, period_end


def _period_filters(
    start_at: datetime | None, end_at: datetime | None
) -> list[ColumnElement[bool]]:
    filters: list[ColumnElement[bool]] = []
    if start_at is not None:
        filters.append(Transaction.timestamp >= start_at)
    if end_at is not None:
        filters.append(Transaction.timestamp <= end_at)
    return filters


@router.get("/meta", response_model=MetaResponse, tags=["System"], summary="Product metadata")
def meta(db: Db) -> dict[str, Any]:
    manifest = db.scalar(
        select(DatasetManifest).order_by(DatasetManifest.generated_at.desc()).limit(1)
    )
    model_run = db.scalar(select(ModelRun).order_by(ModelRun.started_at.desc()).limit(1))
    return {
        "name": "FraudLens",
        "subtitle": "Payment anomaly investigation",
        "version": __version__,
        "language": "pt-BR",
        "data_classification": "100% sintético",
        "disclaimer": (
            "Scores indicam prioridade de investigação, não probabilidade ou prova de fraude."
        ),
        "dataset": DatasetManifestResponse.model_validate(manifest).model_dump()
        if manifest
        else None,
        "model": _model_payload(model_run) if model_run else None,
        "last_scoring_at": model_run.completed_at
        if model_run and model_run.status == "completed"
        else None,
    }


@router.get(
    "/overview", response_model=OverviewResponse, tags=["Overview"], summary="Risk overview"
)
def overview(
    db: Db,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
) -> dict[str, Any]:
    period_start, period_end = _resolve_period(db, start_at, end_at)
    filters = _period_filters(period_start, period_end)
    total_transactions, volume, accounts = db.execute(
        select(
            func.count(Transaction.id),
            func.coalesce(func.sum(Transaction.amount), 0.0),
            func.count(func.distinct(Transaction.account_id)),
        ).where(*filters)
    ).one()
    total_alerts, critical, high = db.execute(
        select(
            func.count(Alert.id),
            func.coalesce(func.sum(case((Alert.severity == "crítica", 1), else_=0)), 0),
            func.coalesce(func.sum(case((Alert.severity == "alta", 1), else_=0)), 0),
        )
        .select_from(Alert)
        .join(Transaction, Alert.transaction_id == Transaction.id)
        .where(*filters)
    ).one()
    variation: float | None = None
    comparison_available = False
    if period_start is not None and period_end is not None:
        window = period_end - period_start
        previous_start = period_start - window
        recent_volume = float(volume)
        previous_count, previous_volume = db.execute(
            select(
                func.count(Transaction.id),
                func.coalesce(func.sum(Transaction.amount), 0.0),
            ).where(Transaction.timestamp >= previous_start, Transaction.timestamp < period_start)
        ).one()
        comparison_available = bool(
            previous_volume and previous_count >= int(total_transactions * 0.8)
        )
        if comparison_available:
            variation = (recent_volume - float(previous_volume)) / float(previous_volume) * 100
    recent_rows = db.execute(
        select(Alert, Transaction)
        .join(Transaction, Alert.transaction_id == Transaction.id)
        .where(*filters)
        .order_by(Transaction.timestamp.desc(), Alert.risk_score.desc())
        .limit(8)
    ).all()
    latest_run = db.scalar(select(ModelRun).order_by(ModelRun.started_at.desc()).limit(1))
    return {
        "kpis": {
            "monitored_volume": round(float(volume), 2),
            "transactions": int(total_transactions),
            "alerts": int(total_alerts),
            "critical_alerts": int(critical),
            "high_critical_alerts": int(high + critical),
            "alert_rate": round(total_alerts / max(total_transactions, 1) * 100, 2),
            "accounts": int(accounts),
            "volume_change": round(variation, 2) if variation is not None else None,
            "comparison_available": comparison_available,
        },
        "recent_alerts": [_alert_payload(alert, transaction) for alert, transaction in recent_rows],
        "period_start": period_start,
        "period_end": period_end,
        "updated_at": latest_run.completed_at if latest_run else period_end,
    }


@router.get(
    "/overview/timeseries",
    response_model=list[TimeseriesPoint],
    tags=["Overview"],
    summary="Daily activity",
)
def overview_timeseries(
    db: Db, start_at: datetime | None = None, end_at: datetime | None = None
) -> list[dict[str, Any]]:
    start_at, end_at = _resolve_period(db, start_at, end_at)
    rows = db.execute(
        select(
            func.date(Transaction.timestamp).label("date"),
            func.sum(Transaction.amount).label("volume"),
            func.count(Transaction.id).label("transactions"),
            func.count(Alert.id).label("alerts"),
        )
        .outerjoin(Alert, Alert.transaction_id == Transaction.id)
        .where(*_period_filters(start_at, end_at))
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


@router.get(
    "/overview/payment-methods",
    response_model=list[PaymentMethodSummary],
    tags=["Overview"],
    summary="Activity by payment method",
)
def payment_methods(
    db: Db, start_at: datetime | None = None, end_at: datetime | None = None
) -> list[dict[str, Any]]:
    start_at, end_at = _resolve_period(db, start_at, end_at)
    rows = db.execute(
        select(
            Transaction.payment_method,
            func.count(Transaction.id),
            func.count(Alert.id),
            func.sum(Transaction.amount),
        )
        .outerjoin(Alert, Alert.transaction_id == Transaction.id)
        .where(*_period_filters(start_at, end_at))
        .group_by(Transaction.payment_method)
        .order_by(func.count(Alert.id).desc())
    ).all()
    return [
        {"method": row[0], "transactions": row[1], "alerts": row[2], "volume": round(row[3], 2)}
        for row in rows
    ]


@router.get(
    "/overview/severity",
    response_model=list[SeveritySummary],
    tags=["Overview"],
    summary="Alert severity distribution",
)
def severity_distribution(
    db: Db, start_at: datetime | None = None, end_at: datetime | None = None
) -> list[dict[str, Any]]:
    start_at, end_at = _resolve_period(db, start_at, end_at)
    rows = db.execute(
        select(Alert.severity, func.count())
        .join(Transaction, Alert.transaction_id == Transaction.id)
        .where(*_period_filters(start_at, end_at))
        .group_by(Alert.severity)
        .order_by(func.count().desc())
    ).all()
    return [{"severity": severity, "count": count} for severity, count in rows]


@router.get(
    "/overview/reason-codes",
    response_model=list[ReasonSummary],
    tags=["Overview"],
    summary="Most frequent alert signals",
)
def reason_codes(
    db: Db, start_at: datetime | None = None, end_at: datetime | None = None
) -> list[dict[str, Any]]:
    start_at, end_at = _resolve_period(db, start_at, end_at)
    counter: Counter[str] = Counter()
    for codes in db.scalars(
        select(Alert.reason_codes)
        .join(Transaction, Alert.transaction_id == Transaction.id)
        .where(*_period_filters(start_at, end_at))
    ):
        counter.update(codes or [])
    return [{"reason_code": code, "count": count} for code, count in counter.most_common(10)]


@router.get(
    "/alerts", response_model=AlertListResponse, tags=["Alerts"], summary="Investigation queue"
)
def list_alerts(
    db: Db,
    severity: str | None = None,
    status: str | None = None,
    account_id: str | None = None,
    payment_method: str | None = None,
    min_score: float | None = Query(default=None, ge=0, le=100),
    reason_code: str | None = None,
    search: str | None = Query(default=None, max_length=80),
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    sort: Literal["risk_desc", "risk_asc", "newest", "oldest"] = "risk_desc",
) -> dict[str, Any]:
    if start_at and end_at and start_at > end_at:
        raise DomainError("INVALID_DATE_RANGE", "A data inicial deve preceder a data final.", 422)
    filters: list[ColumnElement[bool]] = _period_filters(start_at, end_at)
    if severity:
        filters.append(Alert.severity == severity)
    if status:
        filters.append(Alert.status == status)
    if account_id:
        filters.append(Alert.account_id == account_id)
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
    rows = db.execute(
        base.order_by(ordering, Alert.id).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return {
        "items": [_alert_payload(alert, transaction) for alert, transaction in rows],
        **_pagination(total, page, page_size),
    }


@router.get(
    "/alerts/{alert_id}",
    response_model=AlertDetailResponse,
    tags=["Alerts"],
    summary="Investigation case file",
)
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
        FeedbackResponse.model_validate(item).model_dump()
        for item in db.scalars(
            select(AlertFeedback)
            .where(AlertFeedback.alert_id == alert_id)
            .order_by(AlertFeedback.created_at, AlertFeedback.id)
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
            .order_by(Transaction.timestamp, Transaction.id)
            .limit(30)
        )
    ]
    return payload


@router.patch(
    "/alerts/{alert_id}", response_model=AlertResponse, tags=["Alerts"], summary="Update a case"
)
def update_alert(alert_id: str, update: AlertUpdate, db: Db) -> dict[str, Any]:
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise NotFoundError("ALERT_NOT_FOUND", "Alerta não encontrado.")
    alert.status = update.status.value
    alert.reviewer_note = update.reviewer_note
    alert.reviewed_at = datetime.now(UTC)
    db.commit()
    return _alert_payload(alert)


@router.post(
    "/alerts/{alert_id}/feedback",
    response_model=FeedbackResponse,
    status_code=201,
    tags=["Alerts"],
    summary="Record a human review",
)
def add_feedback(alert_id: str, feedback: FeedbackCreate, db: Db) -> AlertFeedback:
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
    return item


@router.get(
    "/transactions",
    response_model=TransactionListResponse,
    tags=["Transactions"],
    summary="List operational transactions",
)
def list_transactions(
    db: Db,
    account_id: str | None = None,
    payment_method: str | None = None,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    if start_at and end_at and start_at > end_at:
        raise DomainError("INVALID_DATE_RANGE", "A data inicial deve preceder a data final.", 422)
    filters = _period_filters(start_at, end_at)
    if account_id:
        filters.append(Transaction.account_id == account_id)
    if payment_method:
        filters.append(Transaction.payment_method == payment_method)
    query = select(Transaction).where(*filters)
    total = db.scalar(select(func.count()).select_from(Transaction).where(*filters)) or 0
    items = db.scalars(
        query.order_by(Transaction.timestamp.desc(), Transaction.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return {
        "items": [_transaction_payload(item) for item in items],
        **_pagination(total, page, page_size),
    }


@router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    tags=["Transactions"],
    summary="Get an operational transaction",
)
def get_transaction(transaction_id: str, db: Db) -> dict[str, Any]:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise NotFoundError("TRANSACTION_NOT_FOUND", "Transação não encontrada.")
    return _transaction_payload(transaction)


@router.get(
    "/accounts", response_model=AccountListResponse, tags=["Accounts"], summary="List accounts"
)
def list_accounts(
    db: Db,
    search: str | None = Query(default=None, max_length=80),
    segment: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> dict[str, Any]:
    filters: list[ColumnElement[bool]] = []
    if search:
        term = f"%{search.strip()}%"
        filters.append(or_(Account.id.ilike(term), Account.home_city.ilike(term)))
    if segment:
        filters.append(Account.customer_segment == segment)
    tx_count = (
        select(func.count())
        .where(Transaction.account_id == Account.id)
        .correlate(Account)
        .scalar_subquery()
    )
    tx_volume = (
        select(func.coalesce(func.sum(Transaction.amount), 0.0))
        .where(Transaction.account_id == Account.id)
        .correlate(Account)
        .scalar_subquery()
    )
    alert_count = (
        select(func.count())
        .where(Alert.account_id == Account.id)
        .correlate(Account)
        .scalar_subquery()
    )
    highest = (
        select(func.coalesce(func.max(Alert.risk_score), 0.0))
        .where(Alert.account_id == Account.id)
        .correlate(Account)
        .scalar_subquery()
    )
    last_activity = (
        select(func.max(Transaction.timestamp))
        .where(Transaction.account_id == Account.id)
        .correlate(Account)
        .scalar_subquery()
    )
    total = db.scalar(select(func.count()).select_from(Account).where(*filters)) or 0
    rows = db.execute(
        select(Account, tx_count, tx_volume, alert_count, highest, last_activity)
        .where(*filters)
        .order_by(highest.desc(), Account.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    items = []
    for account, transactions, volume, alerts, priority, activity in rows:
        payload = AccountResponse.model_validate(account).model_dump()
        payload.update(
            transaction_count=transactions,
            transaction_volume=round(float(volume), 2),
            alert_count=alerts,
            highest_priority=round(float(priority), 2),
            last_activity=activity,
        )
        items.append(payload)
    return {"items": items, **_pagination(total, page, page_size)}


@router.get(
    "/accounts/{account_id}",
    response_model=AccountResponse,
    tags=["Accounts"],
    summary="Account behavioral profile",
)
def get_account(account_id: str, db: Db) -> dict[str, Any]:
    account = db.get(Account, account_id)
    if account is None:
        raise NotFoundError("ACCOUNT_NOT_FOUND", "Conta não encontrada.")
    payload = AccountResponse.model_validate(account).model_dump()
    payload.update(
        transaction_count=db.scalar(
            select(func.count())
            .select_from(Transaction)
            .where(Transaction.account_id == account_id)
        )
        or 0,
        transaction_volume=round(
            float(
                db.scalar(
                    select(func.coalesce(func.sum(Transaction.amount), 0.0)).where(
                        Transaction.account_id == account_id
                    )
                )
                or 0
            ),
            2,
        ),
        alert_count=db.scalar(
            select(func.count()).select_from(Alert).where(Alert.account_id == account_id)
        )
        or 0,
        highest_priority=round(
            float(
                db.scalar(
                    select(func.coalesce(func.max(Alert.risk_score), 0.0)).where(
                        Alert.account_id == account_id
                    )
                )
                or 0
            ),
            2,
        ),
        last_activity=db.scalar(
            select(func.max(Transaction.timestamp)).where(Transaction.account_id == account_id)
        ),
    )
    return payload


@router.get(
    "/accounts/{account_id}/timeline",
    response_model=list[TimelineItem],
    tags=["Accounts"],
    summary="Account activity timeline",
)
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
        .order_by(Transaction.timestamp.desc(), Transaction.id)
        .limit(limit)
    )
    return [
        {
            **_transaction_payload(row),
            "alert": _alert_payload(alerts[row.id]) if row.id in alerts else None,
        }
        for row in rows
    ]


@router.get(
    "/accounts/{account_id}/behavior",
    response_model=AccountBehaviorResponse,
    tags=["Accounts"],
    summary="Account historical baseline",
)
def account_behavior(account_id: str, db: Db) -> dict[str, Any]:
    account = db.get(Account, account_id)
    if account is None:
        raise NotFoundError("ACCOUNT_NOT_FOUND", "Conta não encontrada.")
    transactions = list(
        db.scalars(
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .order_by(Transaction.timestamp)
        )
    )
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
        "usual_window": (account.usual_transaction_hour_start, account.usual_transaction_hour_end),
    }


@router.get(
    "/accounts/{account_id}/network",
    response_model=NetworkResponse,
    tags=["Accounts"],
    summary="Account relationship network",
)
def account_network(
    account_id: str, db: Db, limit: int = Query(default=40, ge=5, le=100)
) -> dict[str, Any]:
    if db.get(Account, account_id) is None:
        raise NotFoundError("ACCOUNT_NOT_FOUND", "Conta não encontrada.")
    transactions = list(
        db.scalars(
            select(Transaction)
            .where(Transaction.account_id == account_id)
            .order_by(Transaction.timestamp.desc())
            .limit(limit)
        )
    )
    nodes: dict[str, dict[str, Any]] = {
        account_id: {"id": account_id, "label": account_id, "type": "account", "risk": 0}
    }
    edges: list[dict[str, Any]] = []
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
        edges.extend(
            [
                {
                    "id": f"{row.id}-cp",
                    "source": account_id,
                    "target": row.counterparty_id,
                    "amount": row.amount,
                },
                {
                    "id": f"{row.id}-dev",
                    "source": row.device_id,
                    "target": account_id,
                    "amount": row.amount,
                },
            ]
        )
    return {"nodes": list(nodes.values()), "edges": edges, "limited_to": limit}


@router.get(
    "/model-runs", response_model=list[ModelRunResponse], tags=["Models"], summary="Model runs"
)
def list_model_runs(db: Db) -> list[dict[str, Any]]:
    return [
        _model_payload(row)
        for row in db.scalars(select(ModelRun).order_by(ModelRun.started_at.desc()).limit(20))
    ]


@router.get(
    "/model-runs/latest",
    response_model=ModelRunResponse,
    tags=["Models"],
    summary="Latest model run",
)
def latest_model_run(db: Db) -> dict[str, Any]:
    row = db.scalar(select(ModelRun).order_by(ModelRun.started_at.desc()).limit(1))
    if row is None:
        raise NotFoundError("MODEL_RUN_NOT_FOUND", "Execução de modelo não encontrada.")
    return _model_payload(row)


@router.get(
    "/model-runs/{model_run_id}",
    response_model=ModelRunResponse,
    tags=["Models"],
    summary="Model run provenance",
)
def get_model_run(model_run_id: str, db: Db) -> dict[str, Any]:
    row = db.get(ModelRun, model_run_id)
    if row is None:
        raise NotFoundError("MODEL_RUN_NOT_FOUND", "Execução de modelo não encontrada.")
    return _model_payload(row)


@router.get(
    "/dataset-manifests/latest",
    response_model=DatasetManifestResponse,
    tags=["Evaluation"],
    summary="Latest synthetic dataset manifest",
)
def latest_dataset_manifest(db: Db) -> DatasetManifest:
    row = db.scalar(select(DatasetManifest).order_by(DatasetManifest.generated_at.desc()).limit(1))
    if row is None:
        raise NotFoundError("DATASET_NOT_FOUND", "Manifesto do conjunto não encontrado.")
    return row


@router.get(
    "/model-monitoring",
    response_model=MonitoringResponse,
    tags=["Evaluation"],
    summary="Synthetic monitoring indicators",
)
def model_monitoring(db: Db) -> dict[str, Any]:
    run = db.scalar(select(ModelRun).order_by(ModelRun.started_at.desc()).limit(1))
    if run is None or not run.metrics.get("monitoring"):
        return {
            "status": "insufficient_data",
            "drift": "indisponível",
            "indicators": [],
            "disclaimer": "Execute o pipeline para calcular indicadores sobre dados sintéticos.",
        }
    return dict(run.metrics["monitoring"])


def _authorize_admin(settings: Settings, token: str | None) -> None:
    if not settings.enable_admin_api:
        raise DomainError("ADMIN_API_DISABLED", "API administrativa desabilitada.", 404)
    if (
        not settings.admin_api_token
        or not token
        or not secrets.compare_digest(token, settings.admin_api_token)
    ):
        raise DomainError("ADMIN_UNAUTHORIZED", "Token administrativo inválido.", 401)


@router.post("/admin/generate", tags=["Admin"], summary="Generate a synthetic dataset")
def admin_generate(
    payload: AdminRequest, db: Db, x_admin_token: Annotated[str | None, Header()] = None
) -> dict[str, Any]:
    settings = get_settings()
    _authorize_admin(settings, x_admin_token)
    return persist_generated_data(db, payload.accounts, payload.transactions, payload.seed)


@router.post("/admin/train", tags=["Admin"], summary="Train the anomaly detector")
def admin_train(db: Db, x_admin_token: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    settings = get_settings()
    _authorize_admin(settings, x_admin_token)
    return train_model(db, settings)


@router.post("/admin/score", tags=["Admin"], summary="Score synthetic transactions")
def admin_score(db: Db, x_admin_token: Annotated[str | None, Header()] = None) -> dict[str, Any]:
    settings = get_settings()
    _authorize_admin(settings, x_admin_token)
    return score_transactions(db, settings)
