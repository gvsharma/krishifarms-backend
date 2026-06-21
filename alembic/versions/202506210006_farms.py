"""Farm management tables."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import audit_columns, org_fk

revision: str = "202506210006"
down_revision: Union[str, None] = "202506210005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "farms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farm_code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("name_te", sa.Text(), nullable=True),
        sa.Column("acres", sa.Numeric(10, 3), nullable=False),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("village_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("owner_farmer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("lease_start_date", sa.Date(), nullable=True),
        sa.Column("lease_end_date", sa.Date(), nullable=True),
        sa.Column("lease_amount", sa.Numeric(14, 2), nullable=True),
        sa.Column("lease_notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("geo_lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("geo_lng", sa.Numeric(10, 7), nullable=True),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["village_id"], ["villages.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["owner_farmer_id"], ["farmers.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("acres > 0", name="ck_farms_acres"),
        sa.CheckConstraint(
            "lease_end_date IS NULL OR lease_start_date IS NULL OR lease_end_date >= lease_start_date",
            name="ck_farms_lease_dates",
        ),
    )
    op.create_index(
        "uq_farms_org_code_active",
        "farms",
        ["org_id", "farm_code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index("ix_farms_org_id", "farms", ["org_id"])

    op.create_table(
        "farm_activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("activity_type_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("activity_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("description_te", sa.Text(), nullable=True),
        sa.Column("performed_by_worker_id", postgresql.UUID(as_uuid=True), nullable=True),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["activity_type_id"], ["activity_types.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["performed_by_worker_id"], ["workers.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_farm_activities_farm_id", "farm_activities", ["farm_id", "activity_date"])

    for table in ("farms", "farm_activities"):
        op.execute(
            f"""
            CREATE TRIGGER trg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            """
        )


def downgrade() -> None:
    for table in ("farm_activities", "farms"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table};")
    op.drop_index("ix_farm_activities_farm_id", table_name="farm_activities")
    op.drop_table("farm_activities")
    op.drop_index("ix_farms_org_id", table_name="farms")
    op.drop_index("uq_farms_org_code_active", table_name="farms")
    op.drop_table("farms")
