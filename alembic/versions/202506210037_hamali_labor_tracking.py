"""Hamali labor tracking tables and RBAC permissions."""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import apply_updated_at_trigger, audit_columns, org_fk

revision: str = "202506210037"
down_revision: Union[str, None] = "202506210036"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

HAMALI_PERMISSIONS = [
    ("hamali:read", "View hamali workers and daily charges", "hamali"),
    ("hamali:create", "Create hamali workers and daily entries", "hamali"),
    ("hamali:update", "Update hamali workers and daily entries", "hamali"),
    ("hamali:pay", "Create and settle hamali weekly payments", "hamali"),
]

HAMALI_ROLE_GRANTS = {
    "OWNER": [p[0] for p in HAMALI_PERMISSIONS],
    "MANAGER": [p[0] for p in HAMALI_PERMISSIONS],
    "SUPERVISOR": ["hamali:read", "hamali:create", "hamali:update"],
    "ACCOUNTANT": ["hamali:read", "hamali:pay"],
}


def _grant_permissions(conn, org_id: str) -> None:
    for role_code, perm_codes in HAMALI_ROLE_GRANTS.items():
        role_row = conn.execute(
            sa.text("SELECT id FROM roles WHERE org_id = :org_id AND code = :code"),
            {"org_id": org_id, "code": role_code},
        ).fetchone()
        if not role_row:
            continue
        role_id = str(role_row.id)
        for code in perm_codes:
            perm_row = conn.execute(
                sa.text("SELECT id FROM permissions WHERE code = :code"),
                {"code": code},
            ).fetchone()
            if not perm_row:
                continue
            conn.execute(
                sa.text(
                    """
                    INSERT INTO role_permissions (role_id, permission_id)
                    VALUES (:role_id, :permission_id)
                    ON CONFLICT DO NOTHING
                    """
                ),
                {"role_id": role_id, "permission_id": str(perm_row.id)},
            )


def upgrade() -> None:
    op.create_table(
        "hamali_workers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("worker_code", sa.String(length=50), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("full_name_te", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("default_rate_per_bag", sa.Numeric(14, 2), server_default="20.00", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        *audit_columns(),
        org_fk(),
        sa.CheckConstraint("default_rate_per_bag >= 0", name="ck_hamali_workers_rate_non_negative"),
        sa.CheckConstraint("status IN ('active','inactive')", name="ck_hamali_workers_status"),
    )
    op.create_index(
        "uq_hamali_workers_org_code_active",
        "hamali_workers",
        ["org_id", "worker_code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index("ix_hamali_workers_org_id", "hamali_workers", ["org_id"])

    op.create_table(
        "hamali_weekly_payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_number", sa.String(length=50), nullable=False),
        sa.Column("week_start_date", sa.Date(), nullable=False),
        sa.Column("week_end_date", sa.Date(), nullable=False),
        sa.Column("total_bags", sa.Integer(), server_default="0", nullable=False),
        sa.Column("total_labor_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("total_maintenance_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("total_tip_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("total_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="draft", nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payment_reference", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["paid_by"], ["users.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("total_bags >= 0", name="ck_hamali_weekly_total_bags"),
        sa.CheckConstraint(
            "total_labor_amount >= 0 AND total_maintenance_amount >= 0 "
            "AND total_tip_amount >= 0 AND total_amount >= 0",
            name="ck_hamali_weekly_amounts_non_negative",
        ),
        sa.CheckConstraint("status IN ('draft','paid')", name="ck_hamali_weekly_status"),
        sa.CheckConstraint("week_end_date >= week_start_date", name="ck_hamali_weekly_dates"),
    )
    op.create_index(
        "uq_hamali_weekly_org_number_active",
        "hamali_weekly_payments",
        ["org_id", "payment_number"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index("ix_hamali_weekly_org_week", "hamali_weekly_payments", ["org_id", "week_start_date"])

    op.create_table(
        "hamali_daily_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hamali_worker_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("bags_lifted", sa.Integer(), server_default="0", nullable=False),
        sa.Column("rate_per_bag", sa.Numeric(14, 2), server_default="20.00", nullable=False),
        sa.Column("labor_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("maintenance_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("tip_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("total_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("payment_status", sa.String(length=20), server_default="pending", nullable=False),
        sa.Column("weekly_payment_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("procurement_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("procurement_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["hamali_worker_id"], ["hamali_workers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["weekly_payment_id"], ["hamali_weekly_payments.id"], ondelete="SET NULL"),
        sa.CheckConstraint("bags_lifted >= 0", name="ck_hamali_daily_bags_non_negative"),
        sa.CheckConstraint("rate_per_bag >= 0", name="ck_hamali_daily_rate_non_negative"),
        sa.CheckConstraint(
            "labor_amount >= 0 AND maintenance_amount >= 0 AND tip_amount >= 0 AND total_amount >= 0",
            name="ck_hamali_daily_amounts_non_negative",
        ),
        sa.CheckConstraint(
            "payment_status IN ('pending','scheduled','paid')",
            name="ck_hamali_daily_payment_status",
        ),
    )
    op.create_index(
        "uq_hamali_daily_worker_date_active",
        "hamali_daily_entries",
        ["org_id", "hamali_worker_id", "entry_date"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index("ix_hamali_daily_org_date", "hamali_daily_entries", ["org_id", "entry_date"])
    op.create_index("ix_hamali_daily_worker", "hamali_daily_entries", ["hamali_worker_id"])
    op.create_index("ix_hamali_daily_weekly_payment", "hamali_daily_entries", ["weekly_payment_id"])

    for table in ("hamali_workers", "hamali_weekly_payments", "hamali_daily_entries"):
        apply_updated_at_trigger(table)

    conn = op.get_bind()
    for code, description, module in HAMALI_PERMISSIONS:
        conn.execute(
            sa.text(
                """
                INSERT INTO permissions (id, code, description, module)
                VALUES (:id, :code, :description, :module)
                ON CONFLICT (code) DO UPDATE
                SET description = EXCLUDED.description, module = EXCLUDED.module
                """
            ),
            {"id": str(uuid4()), "code": code, "description": description, "module": module},
        )
    for org_row in conn.execute(sa.text("SELECT id FROM organizations")).fetchall():
        _grant_permissions(conn, str(org_row.id))


def downgrade() -> None:
    conn = op.get_bind()
    codes = [p[0] for p in HAMALI_PERMISSIONS]
    conn.execute(
        sa.text(
            """
            DELETE FROM role_permissions
            WHERE permission_id IN (SELECT id FROM permissions WHERE code = ANY(:codes))
            """
        ),
        {"codes": codes},
    )
    conn.execute(sa.text("DELETE FROM permissions WHERE code = ANY(:codes)"), {"codes": codes})

    for table in ("hamali_daily_entries", "hamali_weekly_payments", "hamali_workers"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table};")

    op.drop_index("ix_hamali_daily_weekly_payment", table_name="hamali_daily_entries")
    op.drop_index("ix_hamali_daily_worker", table_name="hamali_daily_entries")
    op.drop_index("ix_hamali_daily_org_date", table_name="hamali_daily_entries")
    op.drop_index("uq_hamali_daily_worker_date_active", table_name="hamali_daily_entries")
    op.drop_table("hamali_daily_entries")

    op.drop_index("ix_hamali_weekly_org_week", table_name="hamali_weekly_payments")
    op.drop_index("uq_hamali_weekly_org_number_active", table_name="hamali_weekly_payments")
    op.drop_table("hamali_weekly_payments")

    op.drop_index("ix_hamali_workers_org_id", table_name="hamali_workers")
    op.drop_index("uq_hamali_workers_org_code_active", table_name="hamali_workers")
    op.drop_table("hamali_workers")
