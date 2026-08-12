"""Initial FraudLens schema."""

import sqlalchemy as sa

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("customer_segment", sa.String(32), nullable=False),
        sa.Column("home_city", sa.String(64), nullable=False),
        sa.Column("home_state", sa.String(2), nullable=False),
        sa.Column("home_latitude", sa.Float(), nullable=False),
        sa.Column("home_longitude", sa.Float(), nullable=False),
        sa.Column("account_age_days", sa.Integer(), nullable=False),
        sa.Column("usual_transaction_hour_start", sa.Integer(), nullable=False),
        sa.Column("usual_transaction_hour_end", sa.Integer(), nullable=False),
        sa.Column("average_monthly_volume", sa.Float(), nullable=False),
        sa.Column("risk_profile", sa.String(16), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_accounts_created_at", "accounts", ["created_at"])
    op.create_index("ix_accounts_customer_segment", "accounts", ["customer_segment"])
    op.create_table(
        "counterparties",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("category", sa.String(40), nullable=False),
        sa.Column("city", sa.String(64), nullable=False),
        sa.Column("state", sa.String(2), nullable=False),
        sa.Column("historical_risk_level", sa.String(16), nullable=False),
        sa.Column("is_known", sa.Boolean(), nullable=False),
    )
    op.create_index(
        "ix_counterparties_historical_risk_level",
        "counterparties",
        ["historical_risk_level"],
    )
    op.create_table(
        "devices",
        sa.Column("id", sa.String(16), primary_key=True),
        sa.Column("account_id", sa.String(16), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("device_type", sa.String(20), nullable=False),
        sa.Column("operating_system", sa.String(24), nullable=False),
        sa.Column("browser", sa.String(24), nullable=False),
        sa.Column("trusted", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_devices_account_id", "devices", ["account_id"])
    op.create_table(
        "authentication_events",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("account_id", sa.String(16), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("device_id", sa.String(16), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("success", sa.Boolean(), nullable=False),
        sa.Column("ip_country", sa.String(2), nullable=False),
        sa.Column("ip_region", sa.String(32), nullable=False),
        sa.Column("ip_city", sa.String(64), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("failure_reason", sa.String(64)),
    )
    for column in ("account_id", "device_id", "timestamp"):
        op.create_index(f"ix_authentication_events_{column}", "authentication_events", [column])
    op.create_table(
        "transactions",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("account_id", sa.String(16), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column(
            "counterparty_id", sa.String(16), sa.ForeignKey("counterparties.id"), nullable=False
        ),
        sa.Column("device_id", sa.String(16), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("payment_method", sa.String(24), nullable=False),
        sa.Column("direction", sa.String(12), nullable=False),
        sa.Column("status", sa.String(12), nullable=False),
        sa.Column("merchant_category", sa.String(40), nullable=False),
        sa.Column("ip_country", sa.String(2), nullable=False),
        sa.Column("ip_city", sa.String(64), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.Column("description", sa.String(120), nullable=False),
        sa.Column("synthetic_scenario", sa.String(48)),
        sa.Column("synthetic_ground_truth", sa.Boolean(), nullable=False),
    )
    for column in (
        "account_id",
        "counterparty_id",
        "device_id",
        "timestamp",
        "payment_method",
        "status",
        "synthetic_scenario",
        "synthetic_ground_truth",
    ):
        op.create_index(f"ix_transactions_{column}", "transactions", [column])
    op.create_index(
        "ix_transactions_account_timestamp", "transactions", ["account_id", "timestamp"]
    )
    op.create_index(
        "ix_transactions_method_timestamp", "transactions", ["payment_method", "timestamp"]
    )
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("transaction_id", sa.String(20), sa.ForeignKey("transactions.id"), unique=True),
        sa.Column("account_id", sa.String(16), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("severity", sa.String(12), nullable=False),
        sa.Column("model_score", sa.Float(), nullable=False),
        sa.Column("rules_score", sa.Float(), nullable=False),
        sa.Column("reason_codes", sa.JSON(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(24), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("reviewer_note", sa.Text()),
        sa.Column("synthetic_ground_truth", sa.Boolean(), nullable=False),
    )
    for column in ("account_id", "created_at", "risk_score", "severity", "status"):
        op.create_index(f"ix_alerts_{column}", "alerts", [column])
    op.create_index("ix_alerts_severity_score", "alerts", ["severity", "risk_score"])
    op.create_index("ix_alerts_status_created", "alerts", ["status", "created_at"])
    op.create_table(
        "model_runs",
        sa.Column("id", sa.String(24), primary_key=True),
        sa.Column("model_name", sa.String(48), nullable=False),
        sa.Column("model_version", sa.String(24), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("training_rows", sa.Integer(), nullable=False),
        sa.Column("scored_rows", sa.Integer(), nullable=False),
        sa.Column("feature_list", sa.JSON(), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("metrics", sa.JSON(), nullable=False),
        sa.Column("artifact_path", sa.String(255), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
    )
    op.create_index("ix_model_runs_started_at", "model_runs", ["started_at"])
    op.create_index("ix_model_runs_status", "model_runs", ["status"])
    op.create_table(
        "alert_feedback",
        sa.Column("id", sa.String(24), primary_key=True),
        sa.Column("alert_id", sa.String(20), sa.ForeignKey("alerts.id"), nullable=False),
        sa.Column("classification", sa.String(24), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_alert_feedback_alert_id", "alert_feedback", ["alert_id"])
    op.create_index("ix_alert_feedback_created_at", "alert_feedback", ["created_at"])


def downgrade() -> None:
    for table in (
        "alert_feedback",
        "model_runs",
        "alerts",
        "transactions",
        "authentication_events",
        "devices",
        "counterparties",
        "accounts",
    ):
        op.drop_table(table)
