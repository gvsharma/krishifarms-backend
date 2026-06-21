"""Worker management tables and user linkage."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import audit_columns, org_fk

revision: str = "202506210005"
down_revision: Union[str, None] = "202506210004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "workers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("worker_code", sa.String(length=50), nullable=False),
        sa.Column("full_name", sa.String(length=200), nullable=False),
        sa.Column("full_name_te", sa.Text(), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("village_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("hourly_rate", sa.Numeric(14, 2), nullable=True),
        sa.Column("daily_rate", sa.Numeric(14, 2), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["village_id"], ["villages.id"], ondelete="RESTRICT"),
        sa.CheckConstraint(
            "(hourly_rate IS NULL OR hourly_rate >= 0) AND (daily_rate IS NULL OR daily_rate >= 0)",
            name="ck_workers_rates",
        ),
    )
    op.create_index(
        "uq_workers_org_code_active",
        "workers",
        ["org_id", "worker_code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index("ix_workers_org_id", "workers", ["org_id"])

    op.create_table(
        "worker_skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("worker_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("skill_name", sa.String(length=100), nullable=False),
        sa.Column("skill_name_te", sa.Text(), nullable=True),
        sa.Column("proficiency", sa.String(length=20), nullable=True),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["worker_id"], ["workers.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_worker_skills_worker_id", "worker_skills", ["worker_id"])

    op.create_foreign_key(
        "fk_users_worker_id_workers",
        "users",
        "workers",
        ["worker_id"],
        ["id"],
        ondelete="SET NULL",
    )

    for table in ("workers", "worker_skills"):
        op.execute(
            f"""
            CREATE TRIGGER trg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            """
        )


def downgrade() -> None:
    for table in ("worker_skills", "workers"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table};")
    op.drop_constraint("fk_users_worker_id_workers", "users", type_="foreignkey")
    op.drop_index("ix_worker_skills_worker_id", table_name="worker_skills")
    op.drop_table("worker_skills")
    op.drop_index("ix_workers_org_id", table_name="workers")
    op.drop_index("uq_workers_org_code_active", table_name="workers")
    op.drop_table("workers")
