"""Field services: catalog extensions and unified service records."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import apply_updated_at_trigger, audit_columns, org_fk

revision: str = "202506210021"
down_revision: Union[str, None] = "202506210020"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SERVICE_CATEGORIES = (
    "field_service",
    "tractor_work",
    "transport",
    "fertiliser",
    "seeds",
    "agri_finance",
    "vehicle_ops",
    "godown",
)


def upgrade() -> None:
    op.add_column(
        "activity_types",
        sa.Column("service_category", sa.String(length=30), nullable=True),
    )
    op.create_check_constraint(
        "ck_activity_types_service_category",
        "activity_types",
        "service_category IS NULL OR service_category IN ("
        + ",".join(f"'{c}'" for c in SERVICE_CATEGORIES)
        + ")",
    )
    op.create_index(
        "ix_activity_types_org_category",
        "activity_types",
        ["org_id", "service_category"],
    )

    op.create_table(
        "field_service_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("record_number", sa.String(length=50), nullable=False),
        sa.Column("service_category", sa.String(length=30), nullable=False),
        sa.Column("activity_type_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("vehicle_type_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("service_date", sa.Date(), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("location_te", sa.Text(), nullable=True),
        sa.Column("hours", sa.Numeric(8, 2), nullable=True),
        sa.Column("bag_count", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Numeric(12, 3), nullable=True),
        sa.Column("quantity_unit", sa.String(length=20), nullable=True),
        sa.Column("rate_per_unit", sa.Numeric(14, 2), nullable=True),
        sa.Column("diesel_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("amount_given", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("advance_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("total_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("pending_amount", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("cleaning_status", sa.String(length=20), nullable=True),
        sa.Column("facility_status", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="open", nullable=False),
        sa.Column("comments", sa.Text(), nullable=True),
        sa.Column("comments_te", sa.Text(), nullable=True),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["activity_type_id"], ["activity_types.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["vehicle_type_id"], ["vehicle_types.id"], ondelete="RESTRICT"),
        sa.CheckConstraint(
            "service_category IN ("
            + ",".join(f"'{c}'" for c in SERVICE_CATEGORIES)
            + ")",
            name="ck_field_service_records_category",
        ),
        sa.CheckConstraint(
            "cleaning_status IS NULL OR cleaning_status IN ('pending','done','not_required')",
            name="ck_field_service_records_cleaning",
        ),
        sa.CheckConstraint(
            "facility_status IS NULL OR facility_status IN ('active','repair','maintenance','cleaning')",
            name="ck_field_service_records_facility",
        ),
        sa.CheckConstraint(
            "status IN ('open','completed','cancelled')",
            name="ck_field_service_records_status",
        ),
        sa.CheckConstraint("hours IS NULL OR hours >= 0", name="ck_field_service_records_hours"),
        sa.CheckConstraint("bag_count IS NULL OR bag_count >= 0", name="ck_field_service_records_bags"),
        sa.CheckConstraint("quantity IS NULL OR quantity >= 0", name="ck_field_service_records_quantity"),
        sa.CheckConstraint("diesel_amount >= 0", name="ck_field_service_records_diesel"),
        sa.CheckConstraint("amount_given >= 0", name="ck_field_service_records_given"),
        sa.CheckConstraint("advance_amount >= 0", name="ck_field_service_records_advance"),
        sa.CheckConstraint("total_amount >= 0", name="ck_field_service_records_total"),
        sa.CheckConstraint("pending_amount >= 0", name="ck_field_service_records_pending"),
    )
    op.create_index(
        "uq_field_service_records_org_number_active",
        "field_service_records",
        ["org_id", "record_number"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_field_service_records_org_date",
        "field_service_records",
        ["org_id", "service_date"],
    )
    op.create_index(
        "ix_field_service_records_org_category",
        "field_service_records",
        ["org_id", "service_category", "status"],
    )
    op.create_index(
        "ix_field_service_records_farmer_date",
        "field_service_records",
        ["farmer_id", "service_date"],
    )
    apply_updated_at_trigger("field_service_records")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_field_service_records_updated_at ON field_service_records;")
    op.drop_index("ix_field_service_records_farmer_date", table_name="field_service_records")
    op.drop_index("ix_field_service_records_org_category", table_name="field_service_records")
    op.drop_index("ix_field_service_records_org_date", table_name="field_service_records")
    op.drop_index("uq_field_service_records_org_number_active", table_name="field_service_records")
    op.drop_table("field_service_records")
    op.drop_index("ix_activity_types_org_category", table_name="activity_types")
    op.drop_constraint("ck_activity_types_service_category", "activity_types", type_="check")
    op.drop_column("activity_types", "service_category")
