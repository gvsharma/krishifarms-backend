"""Crop procurement, farmer ledger, and farmer payments (partitioned)."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import audit_columns, create_monthly_partitions, drop_monthly_partitions, org_fk

revision: str = "202506210008"
down_revision: Union[str, None] = "202506210007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PARTITION_YEAR = 2026


def upgrade() -> None:
    op.create_table(
        "procurements",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("procurement_number", sa.String(length=50), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("crop_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("village_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("procurement_date", sa.Date(), nullable=False),
        sa.Column("bag_count", sa.Integer(), nullable=False),
        sa.Column("gross_weight_kg", sa.Numeric(12, 3), nullable=False),
        sa.Column("moisture_pct", sa.Numeric(5, 2), nullable=True),
        sa.Column("net_weight_kg", sa.Numeric(12, 3), nullable=False),
        sa.Column("rate_per_quintal", sa.Numeric(14, 2), nullable=False),
        sa.Column("gross_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("deduction_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("net_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="draft", nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("confirmed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(length=100), nullable=True),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["crop_type_id"], ["crop_types.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["village_id"], ["villages.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["confirmed_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", "procurement_date"),
        sa.CheckConstraint("bag_count >= 0", name="ck_procurements_bag_count"),
        sa.CheckConstraint("gross_weight_kg >= 0 AND net_weight_kg >= 0", name="ck_procurements_weight"),
        sa.CheckConstraint("moisture_pct IS NULL OR (moisture_pct >= 0 AND moisture_pct <= 100)", name="ck_procurements_moisture"),
        sa.CheckConstraint("gross_amount >= 0 AND net_amount >= 0", name="ck_procurements_amounts"),
        sa.CheckConstraint("net_amount = gross_amount - deduction_amount", name="ck_procurements_net_amount"),
        sa.CheckConstraint("status IN ('draft','confirmed','cancelled')", name="ck_procurements_status"),
        postgresql_partition_by="RANGE (procurement_date)",
    )
    create_monthly_partitions("procurements", "procurement_date", PARTITION_YEAR)

    op.create_table(
        "procurement_deductions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("procurement_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("procurement_date", sa.Date(), nullable=False),
        sa.Column("deduction_type", sa.String(length=100), nullable=False),
        sa.Column("deduction_type_te", sa.Text(), nullable=True),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        org_fk(),
        sa.ForeignKeyConstraint(
            ["procurement_id", "procurement_date"],
            ["procurements.id", "procurements.procurement_date"],
            ondelete="CASCADE",
        ),
        sa.CheckConstraint("amount >= 0", name="ck_procurement_deductions_amount"),
    )
    op.create_index("ix_procurement_deductions_procurement", "procurement_deductions", ["procurement_id", "procurement_date"])

    op.create_table(
        "farmer_ledger_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("entry_type", sa.String(length=30), nullable=False),
        sa.Column("reference_type", sa.String(length=50), nullable=False),
        sa.Column("reference_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("debit", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("credit", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("balance_after", sa.Numeric(14, 2), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("reversal_of_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("posted_by", postgresql.UUID(as_uuid=True), nullable=False),
        org_fk(),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["posted_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", "entry_date"),
        sa.CheckConstraint("debit >= 0 AND credit >= 0", name="ck_farmer_ledger_amounts"),
        sa.CheckConstraint("NOT (debit > 0 AND credit > 0)", name="ck_farmer_ledger_debit_credit"),
        postgresql_partition_by="RANGE (entry_date)",
    )
    create_monthly_partitions("farmer_ledger_entries", "entry_date", PARTITION_YEAR)

    op.execute(
        """
        CREATE OR REPLACE FUNCTION prevent_ledger_mutation()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION 'Ledger entries are immutable. Use reversal entries.';
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_farmer_ledger_immutable
        BEFORE UPDATE OR DELETE ON farmer_ledger_entries
        FOR EACH ROW EXECUTE FUNCTION prevent_ledger_mutation();
        """
    )

    op.create_table(
        "farmer_payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_number", sa.String(length=50), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_type", sa.String(length=20), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("payment_mode_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reference_no", sa.String(length=100), nullable=True),
        sa.Column("bank_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="completed", nullable=False),
        sa.Column("reversal_of_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("idempotency_key", sa.String(length=100), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("posted_by", postgresql.UUID(as_uuid=True), nullable=False),
        org_fk(),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["payment_mode_id"], ["payment_modes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["bank_account_id"], ["farmer_bank_accounts.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["posted_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", "payment_date"),
        sa.CheckConstraint("amount > 0", name="ck_farmer_payments_amount"),
        sa.CheckConstraint("payment_type IN ('advance','final','adjustment')", name="ck_farmer_payments_type"),
        sa.CheckConstraint("status IN ('pending','completed','failed','reversed')", name="ck_farmer_payments_status"),
        postgresql_partition_by="RANGE (payment_date)",
    )
    create_monthly_partitions("farmer_payments", "payment_date", PARTITION_YEAR)

    op.create_table(
        "farmer_payment_allocations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("procurement_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("procurement_date", sa.Date(), nullable=True),
        sa.Column("allocated_amount", sa.Numeric(14, 2), nullable=False),
        org_fk(),
        sa.ForeignKeyConstraint(
            ["payment_id", "payment_date"],
            ["farmer_payments.id", "farmer_payments.payment_date"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["procurement_id", "procurement_date"],
            ["procurements.id", "procurements.procurement_date"],
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint("allocated_amount > 0", name="ck_farmer_payment_allocations_amount"),
    )

    op.create_table(
        "farmer_outstanding_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("as_of_date", sa.Date(), nullable=False),
        sa.Column("outstanding_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("refreshed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        org_fk(),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("farmer_id", "as_of_date", name="uq_farmer_outstanding_snapshots"),
    )

    op.create_index("ix_procurements_org_date", "procurements", ["org_id", "procurement_date"])
    op.create_index("ix_procurements_farmer_date", "procurements", ["farmer_id", "procurement_date"])
    op.create_index(
        "ix_procurements_confirmed",
        "procurements",
        ["org_id", "status", "procurement_date"],
        postgresql_where=sa.text("status = 'confirmed' AND deleted_at IS NULL"),
    )
    op.create_index(
        "uq_procurements_idempotency",
        "procurements",
        ["org_id", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )
    op.create_index("ix_farmer_ledger_farmer_date", "farmer_ledger_entries", ["farmer_id", "entry_date"])
    op.create_index("ix_farmer_payments_farmer_date", "farmer_payments", ["farmer_id", "payment_date"])
    op.create_index(
        "uq_farmer_payments_idempotency",
        "farmer_payments",
        ["org_id", "idempotency_key", "payment_date"],
        unique=True,
        postgresql_where=sa.text("idempotency_key IS NOT NULL"),
    )

    op.execute(
        """
        CREATE TRIGGER trg_procurements_updated_at
        BEFORE UPDATE ON procurements
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_procurements_updated_at ON procurements;")
    op.drop_index("uq_farmer_payments_idempotency", table_name="farmer_payments")
    op.drop_index("ix_farmer_payments_farmer_date", table_name="farmer_payments")
    op.drop_index("ix_farmer_ledger_farmer_date", table_name="farmer_ledger_entries")
    op.drop_index("uq_procurements_idempotency", table_name="procurements")
    op.drop_index("ix_procurements_confirmed", table_name="procurements")
    op.drop_index("ix_procurements_farmer_date", table_name="procurements")
    op.drop_index("ix_procurements_org_date", table_name="procurements")
    op.drop_table("farmer_outstanding_snapshots")
    op.drop_table("farmer_payment_allocations")
    drop_monthly_partitions("farmer_payments", PARTITION_YEAR)
    op.drop_table("farmer_payments")
    op.execute("DROP TRIGGER IF EXISTS trg_farmer_ledger_immutable ON farmer_ledger_entries;")
    op.execute("DROP FUNCTION IF EXISTS prevent_ledger_mutation();")
    drop_monthly_partitions("farmer_ledger_entries", PARTITION_YEAR)
    op.drop_table("farmer_ledger_entries")
    op.drop_index("ix_procurement_deductions_procurement", table_name="procurement_deductions")
    op.drop_table("procurement_deductions")
    drop_monthly_partitions("procurements", PARTITION_YEAR)
    op.drop_table("procurements")
