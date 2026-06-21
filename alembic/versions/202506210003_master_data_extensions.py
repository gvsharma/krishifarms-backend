"""Master data extensions: activity types, payment modes, number sequences."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import audit_columns, org_fk

revision: str = "202506210003"
down_revision: Union[str, None] = "202506210002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "activity_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("name_te", sa.Text(), nullable=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("default_rate_type", sa.String(length=20), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *audit_columns(),
        org_fk(),
        sa.CheckConstraint(
            "default_rate_type IS NULL OR default_rate_type IN ('hourly','daily','fixed')",
            name="ck_activity_types_default_rate_type",
        ),
    )
    op.create_index(
        "uq_activity_types_org_code_active",
        "activity_types",
        ["org_id", "code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index("ix_activity_types_org_id", "activity_types", ["org_id"])

    op.create_table(
        "payment_modes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("name_te", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *audit_columns(),
        org_fk(),
    )
    op.create_index(
        "uq_payment_modes_org_code_active",
        "payment_modes",
        ["org_id", "code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index("ix_payment_modes_org_id", "payment_modes", ["org_id"])

    op.create_table(
        "number_sequences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sequence_type", sa.String(length=50), nullable=False),
        sa.Column("prefix", sa.String(length=20), server_default="", nullable=False),
        sa.Column("current_value", sa.BigInteger(), server_default="0", nullable=False),
        sa.Column("fiscal_year", sa.SmallInteger(), nullable=True),
        org_fk(),
        sa.UniqueConstraint("org_id", "sequence_type", "fiscal_year", name="uq_number_sequences_org_type_year"),
    )
    op.create_index("ix_number_sequences_org_id", "number_sequences", ["org_id"])

    for table in ("activity_types", "payment_modes"):
        op.execute(
            f"""
            CREATE TRIGGER trg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            """
        )


def downgrade() -> None:
    for table in ("payment_modes", "activity_types"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table};")
    op.drop_index("ix_number_sequences_org_id", table_name="number_sequences")
    op.drop_table("number_sequences")
    op.drop_index("ix_payment_modes_org_id", table_name="payment_modes")
    op.drop_index("uq_payment_modes_org_code_active", table_name="payment_modes")
    op.drop_table("payment_modes")
    op.drop_index("ix_activity_types_org_id", table_name="activity_types")
    op.drop_index("uq_activity_types_org_code_active", table_name="activity_types")
    op.drop_table("activity_types")
