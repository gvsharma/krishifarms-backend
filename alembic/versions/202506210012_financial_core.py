"""Financial core: transactions, expenses, collections, and payments."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import audit_columns, create_monthly_partitions, drop_monthly_partitions, org_fk

revision: str = "202506210012"
down_revision: Union[str, None] = "202506210011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PARTITION_YEAR = 2026


def upgrade() -> None:
    op.create_table(
        "financial_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_number", sa.String(length=50), nullable=False),
        sa.Column("transaction_type", sa.String(length=30), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="posted", nullable=False),
        sa.Column("party_type", sa.String(length=50), nullable=True),
        sa.Column("party_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("reversal_of_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source_type", sa.String(length=50), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("posted_by", postgresql.UUID(as_uuid=True), nullable=False),
        org_fk(),
        sa.ForeignKeyConstraint(["posted_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", "transaction_date"),
        sa.CheckConstraint("amount > 0", name="ck_financial_transactions_amount"),
        sa.CheckConstraint(
            "transaction_type IN ('expense','collection','payment','journal')",
            name="ck_financial_transactions_type",
        ),
        sa.CheckConstraint("status IN ('draft','posted','reversed')", name="ck_financial_transactions_status"),
        postgresql_partition_by="RANGE (transaction_date)",
    )
    create_monthly_partitions("financial_transactions", "transaction_date", PARTITION_YEAR)

    op.create_table(
        "financial_transaction_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        org_fk(),
        sa.ForeignKeyConstraint(
            ["transaction_id", "transaction_date"],
            ["financial_transactions.id", "financial_transactions.transaction_date"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["category_id"], ["expense_categories.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("amount > 0", name="ck_financial_transaction_lines_amount"),
    )

    op.create_table(
        "expenses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("expense_number", sa.String(length=50), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("expense_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("vendor_name", sa.String(length=200), nullable=True),
        sa.Column("payment_mode_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("financial_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("financial_transaction_date", sa.Date(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("description_te", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="posted", nullable=False),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["category_id"], ["expense_categories.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["payment_mode_id"], ["payment_modes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("amount > 0", name="ck_expenses_amount"),
    )
    op.create_index(
        "uq_expenses_org_number_active",
        "expenses",
        ["org_id", "expense_number"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index("ix_expenses_org_date", "expenses", ["org_id", "expense_date"])
    op.create_index("ix_expenses_category_date", "expenses", ["category_id", "expense_date"])

    op.create_table(
        "collections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("collection_number", sa.String(length=50), nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("collection_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("payment_mode_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("financial_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("financial_transaction_date", sa.Date(), nullable=True),
        sa.Column("reference_no", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="posted", nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        org_fk(),
        sa.ForeignKeyConstraint(["customer_id"], ["rental_customers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["payment_mode_id"], ["payment_modes.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("org_id", "collection_number", name="uq_collections_org_number"),
        sa.CheckConstraint("amount > 0", name="ck_collections_amount"),
    )
    op.create_index("ix_collections_org_date", "collections", ["org_id", "collection_date"])

    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_number", sa.String(length=50), nullable=False),
        sa.Column("payee_type", sa.String(length=50), nullable=False),
        sa.Column("payee_name", sa.String(length=200), nullable=False),
        sa.Column("payee_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("payment_mode_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("financial_transaction_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("financial_transaction_date", sa.Date(), nullable=True),
        sa.Column("reference_no", sa.String(length=100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="posted", nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        org_fk(),
        sa.ForeignKeyConstraint(["payment_mode_id"], ["payment_modes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["category_id"], ["expense_categories.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("org_id", "payment_number", name="uq_payments_org_number"),
        sa.CheckConstraint("amount > 0", name="ck_payments_amount"),
    )
    op.create_index("ix_payments_org_date", "payments", ["org_id", "payment_date"])
    op.create_index("ix_financial_transactions_org_date", "financial_transactions", ["org_id", "transaction_date"])

    for table in ("expenses", "collections", "payments"):
        op.execute(
            f"""
            CREATE TRIGGER trg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            """
        )


def downgrade() -> None:
    for table in ("payments", "collections", "expenses"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table};")
    op.drop_index("ix_financial_transactions_org_date", table_name="financial_transactions")
    op.drop_index("ix_payments_org_date", table_name="payments")
    op.drop_table("payments")
    op.drop_index("ix_collections_org_date", table_name="collections")
    op.drop_table("collections")
    op.drop_index("ix_expenses_category_date", table_name="expenses")
    op.drop_index("ix_expenses_org_date", table_name="expenses")
    op.drop_index("uq_expenses_org_number_active", table_name="expenses")
    op.drop_table("expenses")
    op.drop_table("financial_transaction_lines")
    drop_monthly_partitions("financial_transactions", PARTITION_YEAR)
    op.drop_table("financial_transactions")
