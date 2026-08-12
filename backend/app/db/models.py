from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    customer_segment: Mapped[str] = mapped_column(String(32), index=True)
    home_city: Mapped[str] = mapped_column(String(64))
    home_state: Mapped[str] = mapped_column(String(2))
    home_latitude: Mapped[float] = mapped_column(Float)
    home_longitude: Mapped[float] = mapped_column(Float)
    account_age_days: Mapped[int] = mapped_column(Integer)
    usual_transaction_hour_start: Mapped[int] = mapped_column(Integer)
    usual_transaction_hour_end: Mapped[int] = mapped_column(Integer)
    average_monthly_volume: Mapped[float] = mapped_column(Float)
    risk_profile: Mapped[str] = mapped_column(String(16))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account")


class Counterparty(Base):
    __tablename__ = "counterparties"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    category: Mapped[str] = mapped_column(String(40))
    city: Mapped[str] = mapped_column(String(64))
    state: Mapped[str] = mapped_column(String(2))
    historical_risk_level: Mapped[str] = mapped_column(String(16), index=True)
    is_known: Mapped[bool] = mapped_column(Boolean)


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(16), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    device_type: Mapped[str] = mapped_column(String(20))
    operating_system: Mapped[str] = mapped_column(String(24))
    browser: Mapped[str] = mapped_column(String(24))
    trusted: Mapped[bool] = mapped_column(Boolean)


class AuthenticationEvent(Base):
    __tablename__ = "authentication_events"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    success: Mapped[bool] = mapped_column(Boolean)
    ip_country: Mapped[str] = mapped_column(String(2))
    ip_region: Mapped[str] = mapped_column(String(32))
    ip_city: Mapped[str] = mapped_column(String(64))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    failure_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        Index("ix_transactions_account_timestamp", "account_id", "timestamp"),
        Index("ix_transactions_method_timestamp", "payment_method", "timestamp"),
    )

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    counterparty_id: Mapped[str] = mapped_column(ForeignKey("counterparties.id"), index=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(3), default="BRL")
    payment_method: Mapped[str] = mapped_column(String(24), index=True)
    direction: Mapped[str] = mapped_column(String(12))
    status: Mapped[str] = mapped_column(String(12), index=True)
    merchant_category: Mapped[str] = mapped_column(String(40))
    ip_country: Mapped[str] = mapped_column(String(2))
    ip_city: Mapped[str] = mapped_column(String(64))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(String(120))
    synthetic_scenario: Mapped[str | None] = mapped_column(String(48), nullable=True, index=True)
    synthetic_ground_truth: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    account: Mapped[Account] = relationship(back_populates="transactions")


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        Index("ix_alerts_severity_score", "severity", "risk_score"),
        Index("ix_alerts_status_created", "status", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"), unique=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    risk_score: Mapped[float] = mapped_column(Float, index=True)
    severity: Mapped[str] = mapped_column(String(12), index=True)
    model_score: Mapped[float] = mapped_column(Float)
    rules_score: Mapped[float] = mapped_column(Float)
    context_booster: Mapped[float] = mapped_column(Float, default=0.0)
    reason_codes: Mapped[list[str]] = mapped_column(JSON, default=list)
    explanation: Mapped[str] = mapped_column(Text)
    evidence: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(24), default="novo", index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    synthetic_ground_truth: Mapped[bool] = mapped_column(Boolean, default=False)


class ModelRun(Base):
    __tablename__ = "model_runs"

    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    model_name: Mapped[str] = mapped_column(String(48))
    model_version: Mapped[str] = mapped_column(String(24))
    seed: Mapped[int] = mapped_column(Integer)
    dataset_hash: Mapped[str] = mapped_column(String(64), index=True)
    feature_signature: Mapped[str] = mapped_column(String(64))
    code_version: Mapped[str] = mapped_column(String(40))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    training_rows: Mapped[int] = mapped_column(Integer)
    scored_rows: Mapped[int] = mapped_column(Integer, default=0)
    feature_list: Mapped[list[str]] = mapped_column(JSON)
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    artifact_path: Mapped[str] = mapped_column(String(255))
    artifact_hash: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), index=True)


class DatasetManifest(Base):
    __tablename__ = "dataset_manifests"

    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    schema_version: Mapped[str] = mapped_column(String(16))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    seed: Mapped[int] = mapped_column(Integer)
    account_count: Mapped[int] = mapped_column(Integer)
    transaction_count: Mapped[int] = mapped_column(Integer)
    scenario_count: Mapped[int] = mapped_column(Integer)
    scenario_rows: Mapped[int] = mapped_column(Integer)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    dataset_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    quality_report: Mapped[dict[str, Any]] = mapped_column(JSON)


class AlertFeedback(Base):
    __tablename__ = "alert_feedback"

    id: Mapped[str] = mapped_column(String(24), primary_key=True)
    alert_id: Mapped[str] = mapped_column(ForeignKey("alerts.id"), index=True)
    classification: Mapped[str] = mapped_column(String(24))
    comment: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
