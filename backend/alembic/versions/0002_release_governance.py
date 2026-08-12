"""Add release governance metadata.

Revision ID: 0002_release_governance
Revises: 0001_initial
"""

import sqlalchemy as sa

from alembic import op

revision = "0002_release_governance"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "alerts", sa.Column("context_booster", sa.Float(), nullable=False, server_default="0")
    )
    op.add_column(
        "model_runs", sa.Column("seed", sa.Integer(), nullable=False, server_default="42")
    )
    op.add_column(
        "model_runs",
        sa.Column("dataset_hash", sa.String(64), nullable=False, server_default="legacy"),
    )
    op.add_column(
        "model_runs",
        sa.Column("feature_signature", sa.String(64), nullable=False, server_default="legacy"),
    )
    op.add_column(
        "model_runs",
        sa.Column("code_version", sa.String(40), nullable=False, server_default="0.1.0"),
    )
    op.add_column(
        "model_runs",
        sa.Column("artifact_hash", sa.String(64), nullable=False, server_default="legacy"),
    )
    op.create_index("ix_model_runs_dataset_hash", "model_runs", ["dataset_hash"])
    op.create_table(
        "dataset_manifests",
        sa.Column("id", sa.String(24), primary_key=True),
        sa.Column("schema_version", sa.String(16), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=False),
        sa.Column("account_count", sa.Integer(), nullable=False),
        sa.Column("transaction_count", sa.Integer(), nullable=False),
        sa.Column("scenario_count", sa.Integer(), nullable=False),
        sa.Column("scenario_rows", sa.Integer(), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dataset_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("quality_report", sa.JSON(), nullable=False),
    )
    op.create_index("ix_dataset_manifests_generated_at", "dataset_manifests", ["generated_at"])
    op.create_index("ix_dataset_manifests_dataset_hash", "dataset_manifests", ["dataset_hash"])


def downgrade() -> None:
    op.drop_table("dataset_manifests")
    op.drop_index("ix_model_runs_dataset_hash", table_name="model_runs")
    for column in (
        "artifact_hash",
        "code_version",
        "feature_signature",
        "dataset_hash",
        "seed",
    ):
        op.drop_column("model_runs", column)
    op.drop_column("alerts", "context_booster")
