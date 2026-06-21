"""Rental customers and rental agreements."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import audit_columns, org_fk

revision: str = "202506210011"
down_revision: Union[str, None] = "202506210010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rental_customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("name_te", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("village_id", postgresql.UUID(as_uuid=True), nullable=True),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["village_id"], ["villages.id"], ondelete="RESTRICT"),
    )
    op.create_index(
        "uq_rental_customers_org_code_active",
        "rental_customers",
        ["org_id", "customer_code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.create_table(
        "rental_agreements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agreement_number", sa.String(length=50), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("start_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_datetime", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rate_type", sa.String(length=20), nullable=False),
        sa.Column("hourly_rate", sa.Numeric(14, 2), nullable=False),
        sa.Column("total_hours", sa.Numeric(10, 2), nullable=True),
        sa.Column("revenue", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("collected_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column(
            "pending_collection",
            sa.Numeric(14, 2),
            sa.Computed("revenue - collected_amount", persisted=True),
            nullable=True,
        ),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["customer_id"], ["rental_customers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("rate_type IN ('hourly','daily')", name="ck_rental_agreements_rate_type"),
        sa.CheckConstraint("status IN ('active','completed','cancelled')", name="ck_rental_agreements_status"),
    )
    op.create_index(
        "uq_rental_agreements_org_number_active",
        "rental_agreements",
        ["org_id", "agreement_number"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_rental_agreements_pending",
        "rental_agreements",
        ["org_id", "status"],
        postgresql_where=sa.text("pending_collection > 0"),
    )

    for table in ("rental_customers", "rental_agreements"):
        op.execute(
            f"""
            CREATE TRIGGER trg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            """
        )


def downgrade() -> None:
    for table in ("rental_agreements", "rental_customers"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table};")
    op.drop_index("ix_rental_agreements_pending", table_name="rental_agreements")
    op.drop_index("uq_rental_agreements_org_number_active", table_name="rental_agreements")
    op.drop_table("rental_agreements")
    op.drop_index("uq_rental_customers_org_code_active", table_name="rental_customers")
    op.drop_table("rental_customers")
