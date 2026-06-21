"""Audit enhancements, activity feed Telugu support, and mobile sync tables."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202506210013"
down_revision: Union[str, None] = "202506210012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("activity_feed", sa.Column("summary_te", sa.Text(), nullable=True))

    op.create_index("ix_audit_logs_org_occurred", "audit_logs", ["org_id", "occurred_at"])
    op.create_index("ix_audit_logs_entity", "audit_logs", ["entity_type", "entity_id", "occurred_at"])

    op.create_table(
        "sync_batches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_id", sa.String(length=100), nullable=False),
        sa.Column("pushed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="completed", nullable=False),
        sa.Column("conflict_count", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_sync_batches_user_device", "sync_batches", ["user_id", "device_id", "pushed_at"])

    op.create_table(
        "sync_conflicts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("sync_batch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("client_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("server_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("resolution", sa.String(length=20), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["sync_batch_id"], ["sync_batches.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_sync_conflicts_batch_id", "sync_conflicts", ["sync_batch_id"])

    op.create_table(
        "schema_migrations_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("schema_migrations_log")
    op.drop_index("ix_sync_conflicts_batch_id", table_name="sync_conflicts")
    op.drop_table("sync_conflicts")
    op.drop_index("ix_sync_batches_user_device", table_name="sync_batches")
    op.drop_table("sync_batches")
    op.drop_index("ix_audit_logs_entity", table_name="audit_logs")
    op.drop_index("ix_audit_logs_org_occurred", table_name="audit_logs")
    op.drop_column("activity_feed", "summary_te")
