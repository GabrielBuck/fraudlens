from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class ApiResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("*", when_used="json", check_fields=False)
    def serialize_utc_datetimes(self, value: Any) -> Any:
        if not isinstance(value, datetime):
            return value
        aware = value.replace(tzinfo=UTC) if value.tzinfo is None else value.astimezone(UTC)
        return aware.isoformat().replace("+00:00", "Z")


class Severity(StrEnum):
    LOW = "baixa"
    MEDIUM = "média"
    HIGH = "alta"
    CRITICAL = "crítica"


class AlertStatus(StrEnum):
    NEW = "novo"
    REVIEWING = "em análise"
    CONFIRMED = "fraude confirmada"
    FALSE_POSITIVE = "falso positivo"
    CLOSED = "encerrado"


class AlertUpdate(BaseModel):
    status: AlertStatus
    reviewer_note: str | None = Field(default=None, max_length=1000)


class FeedbackCreate(BaseModel):
    classification: Literal["fraude confirmada", "falso positivo", "inconclusivo"]
    comment: str = Field(min_length=2, max_length=1000)


class AdminRequest(BaseModel):
    accounts: int = Field(default=120, ge=8, le=10_000)
    transactions: int = Field(default=5000, ge=80, le=500_000)
    seed: int = Field(default=42, ge=0, le=2_147_483_647)


class ErrorDetails(BaseModel):
    code: str
    message: str
    details: object | None
    correlation_id: str


class ErrorResponse(BaseModel):
    error: ErrorDetails


class TransactionResponse(ApiResponse):
    """Operational transaction contract; evaluation labels are intentionally absent."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    account_id: str
    counterparty_id: str
    device_id: str
    timestamp: datetime
    amount: float
    currency: str
    payment_method: str
    direction: str
    status: str
    merchant_category: str
    ip_country: str
    ip_city: str
    latitude: float
    longitude: float
    description: str


class EvidenceResponse(BaseModel):
    triggered: bool
    rule_id: str
    rule_name: str
    weight: float
    severity: str
    observed_value: float
    expected_value: str
    description: str


class FeedbackResponse(ApiResponse):
    model_config = ConfigDict(from_attributes=True)

    id: str
    alert_id: str
    classification: str
    comment: str
    created_at: datetime


class AlertResponse(ApiResponse):
    model_config = ConfigDict(from_attributes=True)

    id: str
    transaction_id: str
    account_id: str
    created_at: datetime
    risk_score: float
    severity: Severity
    model_score: float
    rules_score: float
    context_booster: float
    reason_codes: list[str]
    explanation: str
    evidence: list[EvidenceResponse]
    status: AlertStatus
    reviewed_at: datetime | None
    reviewer_note: str | None
    transaction: TransactionResponse | None = None


class AlertDetailResponse(AlertResponse):
    transaction: TransactionResponse
    nearby_transactions: list[TransactionResponse]
    feedback: list[FeedbackResponse]


class Pagination(BaseModel):
    page: int
    page_size: int
    total: int
    pages: int


class AlertListResponse(Pagination):
    items: list[AlertResponse]


class TransactionListResponse(Pagination):
    items: list[TransactionResponse]


class AccountResponse(ApiResponse):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    customer_segment: str
    home_city: str
    home_state: str
    account_age_days: int
    usual_transaction_hour_start: int
    usual_transaction_hour_end: int
    average_monthly_volume: float
    risk_profile: str
    is_active: bool
    transaction_count: int = 0
    transaction_volume: float = 0
    alert_count: int = 0
    highest_priority: float = 0
    last_activity: datetime | None = None


class AccountListResponse(Pagination):
    items: list[AccountResponse]


class TimelineItem(TransactionResponse):
    alert: AlertResponse | None


class PaymentMethodCount(BaseModel):
    method: str
    count: int


class HourCount(BaseModel):
    hour: int
    count: int


class AccountBehaviorResponse(BaseModel):
    average_amount: float
    median_amount: float
    p95_amount: float
    payment_methods: list[PaymentMethodCount]
    common_hours: list[HourCount]
    usual_window: tuple[int, int]


class NetworkNode(BaseModel):
    id: str
    label: str
    type: Literal["account", "counterparty", "device"]
    risk: float


class NetworkEdge(BaseModel):
    id: str
    source: str
    target: str
    amount: float


class NetworkResponse(BaseModel):
    nodes: list[NetworkNode]
    edges: list[NetworkEdge]
    limited_to: int


class DatasetManifestResponse(ApiResponse):
    model_config = ConfigDict(from_attributes=True)

    id: str
    schema_version: str
    generated_at: datetime
    seed: int
    account_count: int
    transaction_count: int
    scenario_count: int
    scenario_rows: int
    period_start: datetime
    period_end: datetime
    dataset_hash: str
    quality_report: dict[str, Any]


class ModelRunResponse(ApiResponse):
    model_config = ConfigDict(from_attributes=True)

    id: str
    model_name: str
    model_version: str
    seed: int
    dataset_hash: str
    feature_signature: str
    code_version: str
    started_at: datetime
    completed_at: datetime | None
    training_rows: int
    scored_rows: int
    feature_list: list[str]
    parameters: dict[str, Any]
    metrics: dict[str, Any]
    artifact_hash: str
    status: str


class MetaResponse(ApiResponse):
    name: str
    subtitle: str
    version: str
    language: str
    data_classification: str
    disclaimer: str
    dataset: DatasetManifestResponse | None
    model: ModelRunResponse | None
    last_scoring_at: datetime | None


class OverviewKpis(BaseModel):
    monitored_volume: float
    transactions: int
    alerts: int
    critical_alerts: int
    high_critical_alerts: int
    alert_rate: float
    accounts: int
    volume_change: float | None
    comparison_available: bool


class OverviewResponse(ApiResponse):
    kpis: OverviewKpis
    recent_alerts: list[AlertResponse]
    period_start: datetime | None
    period_end: datetime | None
    updated_at: datetime | None


class TimeseriesPoint(BaseModel):
    date: str
    volume: float
    transactions: int
    alerts: int


class PaymentMethodSummary(BaseModel):
    method: str
    transactions: int
    alerts: int
    volume: float


class SeveritySummary(BaseModel):
    severity: Severity
    count: int


class ReasonSummary(BaseModel):
    reason_code: str
    count: int


class MonitoringIndicator(BaseModel):
    name: str
    value: float
    status: str


class MonitoringResponse(BaseModel):
    status: str
    drift: str
    indicators: list[MonitoringIndicator]
    disclaimer: str
