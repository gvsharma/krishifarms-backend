"""Shared helpers for Alembic migrations."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

UUID = postgresql.UUID(as_uuid=True)
JSONB = postgresql.JSONB(astext_type=sa.Text())


def audit_columns(*, include_soft_delete: bool = True) -> list[sa.Column]:
    columns = [
        sa.Column("created_by", UUID, nullable=True),
        sa.Column("updated_by", UUID, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    ]
    if include_soft_delete:
        columns.insert(2, sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    return columns


def org_fk() -> sa.ForeignKeyConstraint:
    return sa.ForeignKeyConstraint(["org_id"], ["organizations.id"], ondelete="RESTRICT")


def users_fk(column: str, *, nullable: bool = True) -> sa.ForeignKeyConstraint:
    return sa.ForeignKeyConstraint([column], ["users.id"], ondelete="RESTRICT")


def apply_updated_at_trigger(table_name: str) -> None:
    op.execute(
        f"""
        CREATE TRIGGER trg_{table_name}_updated_at
        BEFORE UPDATE ON {table_name}
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def create_updated_at_function() -> None:
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )


def drop_updated_at_function() -> None:
    op.execute("DROP FUNCTION IF EXISTS set_updated_at() CASCADE;")


def create_extensions() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm";')


def drop_extensions() -> None:
    op.execute('DROP EXTENSION IF EXISTS "pg_trgm";')
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto";')


def create_monthly_partitions(parent_table: str, column: str, year: int) -> None:
    for month in range(1, 13):
        next_month = month + 1
        next_year = year
        if month == 12:
            next_month = 1
            next_year = year + 1
        partition_name = f"{parent_table}_{year}_{month:02d}"
        op.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {partition_name}
            PARTITION OF {parent_table}
            FOR VALUES FROM ('{year}-{month:02d}-01')
            TO ('{next_year}-{next_month:02d}-01');
            """
        )


def drop_monthly_partitions(parent_table: str, year: int) -> None:
    for month in range(1, 13):
        partition_name = f"{parent_table}_{year}_{month:02d}"
        op.execute(f"DROP TABLE IF EXISTS {partition_name};")
