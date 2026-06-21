"""Assets, maintenance, usage logs, and vehicle trips."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import audit_columns, create_monthly_partitions, drop_monthly_partitions, org_fk

revision: str = "202506210010"
down_revision: Union[str, None] = "202506210009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PARTITION_YEAR = 2026


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asset_code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("name_te", sa.Text(), nullable=True),
        sa.Column("asset_category", sa.String(length=50), nullable=False),
        sa.Column("registration_number", sa.String(length=50), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("purchase_cost", sa.Numeric(14, 2), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        sa.Column("is_rentable", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("hourly_rate", sa.Numeric(14, 2), nullable=True),
        sa.Column("daily_rate", sa.Numeric(14, 2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *audit_columns(),
        org_fk(),
        sa.CheckConstraint(
            "asset_category IN ('tractor','dcm','baler','air_machine','other')",
            name="ck_assets_category",
        ),
        sa.CheckConstraint("status IN ('active','maintenance','retired')", name="ck_assets_status"),
    )
    op.create_index(
        "uq_assets_org_code_active",
        "assets",
        ["org_id", "asset_code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index("ix_assets_org_category_status", "assets", ["org_id", "asset_category", "status"])

    op.create_table(
        "maintenance_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("maintenance_date", sa.Date(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("vendor_name", sa.String(length=200), nullable=True),
        sa.Column("cost", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("odometer_km", sa.Numeric(10, 2), nullable=True),
        sa.Column("machine_hours", sa.Numeric(10, 2), nullable=True),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_maintenance_records_asset_date", "maintenance_records", ["asset_id", "maintenance_date"])

    op.create_table(
        "asset_usage_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("usage_date", sa.Date(), nullable=False),
        sa.Column("machine_hours", sa.Numeric(10, 2), server_default="0", nullable=False),
        sa.Column("revenue_generated", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("maintenance_cost", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("fuel_cost", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("source_type", sa.String(length=50), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("recorded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        org_fk(),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["recorded_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", "usage_date"),
        postgresql_partition_by="RANGE (usage_date)",
    )
    create_monthly_partitions("asset_usage_logs", "usage_date", PARTITION_YEAR)

    op.create_table(
        "vehicle_trips",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trip_number", sa.String(length=50), nullable=False),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("driver_worker_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("source_te", sa.Text(), nullable=True),
        sa.Column("destination", sa.String(length=255), nullable=False),
        sa.Column("destination_te", sa.Text(), nullable=True),
        sa.Column("trip_date", sa.Date(), nullable=False),
        sa.Column("distance_km", sa.Numeric(10, 2), nullable=True),
        sa.Column("fuel_liters", sa.Numeric(10, 3), nullable=True),
        sa.Column("fuel_cost", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("loading_charges", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("unloading_charges", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("waiting_charges", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("other_charges", sa.Numeric(14, 2), server_default="0", nullable=False),
        sa.Column("total_cost", sa.Numeric(14, 2), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="completed", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        org_fk(),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["driver_worker_id"], ["workers.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", "trip_date"),
        sa.UniqueConstraint("org_id", "trip_number", "trip_date", name="uq_vehicle_trips_org_number_date"),
        sa.CheckConstraint("distance_km IS NULL OR distance_km >= 0", name="ck_vehicle_trips_distance"),
        postgresql_partition_by="RANGE (trip_date)",
    )
    create_monthly_partitions("vehicle_trips", "trip_date", PARTITION_YEAR)

    op.create_index("ix_vehicle_trips_asset_date", "vehicle_trips", ["asset_id", "trip_date"])

    for table in ("assets", "maintenance_records"):
        op.execute(
            f"""
            CREATE TRIGGER trg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            """
        )
    op.execute(
        """
        CREATE TRIGGER trg_vehicle_trips_updated_at
        BEFORE UPDATE ON vehicle_trips
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_vehicle_trips_updated_at ON vehicle_trips;")
    for table in ("maintenance_records", "assets"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table};")
    op.drop_index("ix_vehicle_trips_asset_date", table_name="vehicle_trips")
    drop_monthly_partitions("vehicle_trips", PARTITION_YEAR)
    op.drop_table("vehicle_trips")
    drop_monthly_partitions("asset_usage_logs", PARTITION_YEAR)
    op.drop_table("asset_usage_logs")
    op.drop_index("ix_maintenance_records_asset_date", table_name="maintenance_records")
    op.drop_table("maintenance_records")
    op.drop_index("ix_assets_org_category_status", table_name="assets")
    op.drop_index("uq_assets_org_code_active", table_name="assets")
    op.drop_table("assets")
