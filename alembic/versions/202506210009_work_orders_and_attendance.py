"""Work orders, attendance, and work order photos."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import audit_columns, create_monthly_partitions, drop_monthly_partitions, org_fk

revision: str = "202506210009"
down_revision: Union[str, None] = "202506210008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PARTITION_YEAR = 2026


def upgrade() -> None:
    op.create_table(
        "work_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("work_order_number", sa.String(length=50), nullable=False),
        sa.Column("worker_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("activity_type_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("rate_type", sa.String(length=20), nullable=False),
        sa.Column("rate", sa.Numeric(14, 2), nullable=False),
        sa.Column("cost", sa.Numeric(14, 2), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="open", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("notes_te", sa.Text(), nullable=True),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["worker_id"], ["workers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["activity_type_id"], ["activity_types.id"], ondelete="RESTRICT"),
        sa.CheckConstraint("rate >= 0", name="ck_work_orders_rate"),
        sa.CheckConstraint("duration_minutes IS NULL OR duration_minutes >= 0", name="ck_work_orders_duration"),
        sa.CheckConstraint("end_time IS NULL OR end_time >= start_time", name="ck_work_orders_times"),
        sa.CheckConstraint("rate_type IN ('hourly','daily','fixed')", name="ck_work_orders_rate_type"),
        sa.CheckConstraint("status IN ('open','in_progress','completed','cancelled')", name="ck_work_orders_status"),
    )
    op.create_index(
        "uq_work_orders_org_number_active",
        "work_orders",
        ["org_id", "work_order_number"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index("ix_work_orders_farm_start", "work_orders", ["farm_id", "start_time"])
    op.create_index("ix_work_orders_worker_status", "work_orders", ["worker_id", "status"])

    op.create_table(
        "work_order_photos",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        org_fk(),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_work_order_photos_work_order_id", "work_order_photos", ["work_order_id"])

    op.create_table(
        "attendance_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("worker_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attendance_date", sa.Date(), nullable=False),
        sa.Column("check_in", sa.DateTime(timezone=True), nullable=True),
        sa.Column("check_out", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("recorded_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        org_fk(),
        sa.ForeignKeyConstraint(["worker_id"], ["workers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["farm_id"], ["farms.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["recorded_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id", "attendance_date"),
        sa.UniqueConstraint("worker_id", "attendance_date", name="uq_attendance_worker_date"),
        sa.CheckConstraint("status IN ('present','absent','half_day','leave')", name="ck_attendance_status"),
        postgresql_partition_by="RANGE (attendance_date)",
    )
    create_monthly_partitions("attendance_records", "attendance_date", PARTITION_YEAR)

    op.execute(
        """
        CREATE TRIGGER trg_work_orders_updated_at
        BEFORE UPDATE ON work_orders
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_attendance_records_updated_at
        BEFORE UPDATE ON attendance_records
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_attendance_records_updated_at ON attendance_records;")
    op.execute("DROP TRIGGER IF EXISTS trg_work_orders_updated_at ON work_orders;")
    drop_monthly_partitions("attendance_records", PARTITION_YEAR)
    op.drop_table("attendance_records")
    op.drop_index("ix_work_order_photos_work_order_id", table_name="work_order_photos")
    op.drop_table("work_order_photos")
    op.drop_index("ix_work_orders_worker_status", table_name="work_orders")
    op.drop_index("ix_work_orders_farm_start", table_name="work_orders")
    op.drop_index("uq_work_orders_org_number_active", table_name="work_orders")
    op.drop_table("work_orders")
