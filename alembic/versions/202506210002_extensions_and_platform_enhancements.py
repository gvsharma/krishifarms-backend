"""Extensions, platform enhancements, and shared database functions."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import (
    audit_columns,
    create_extensions,
    create_updated_at_function,
    drop_extensions,
    drop_updated_at_function,
    org_fk,
)

revision: str = "202506210002"
down_revision: Union[str, None] = "202506210001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    create_extensions()
    create_updated_at_function()

    op.add_column("organizations", sa.Column("name_te", sa.Text(), nullable=True))
    op.add_column(
        "organizations",
        sa.Column("fiscal_year_start_month", sa.SmallInteger(), server_default="4", nullable=False),
    )
    op.create_check_constraint(
        "ck_organizations_fiscal_year_start_month",
        "organizations",
        "fiscal_year_start_month BETWEEN 1 AND 12",
    )

    op.add_column("permissions", sa.Column("module", sa.String(length=50), server_default="platform", nullable=False))
    op.add_column("roles", sa.Column("name_te", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("full_name_te", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("worker_id", postgresql.UUID(as_uuid=True), nullable=True))

    op.add_column("villages", sa.Column("name_te", sa.Text(), nullable=True))
    op.add_column("crop_types", sa.Column("name_te", sa.Text(), nullable=True))
    op.add_column("expense_categories", sa.Column("name_te", sa.Text(), nullable=True))
    op.add_column(
        "expense_categories",
        sa.Column("sort_order", sa.SmallInteger(), server_default="0", nullable=False),
    )

    op.create_table(
        "user_scopes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope_type", sa.String(length=30), nullable=False),
        sa.Column("scope_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        org_fk(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "scope_type", "scope_id", name="uq_user_scopes_user_scope"),
    )
    op.create_index("ix_user_scopes_org_id", "user_scopes", ["org_id"])

    op.drop_constraint("uq_users_org_email", "users", type_="unique")
    op.create_index(
        "uq_users_org_email_active",
        "users",
        ["org_id", "email"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL AND email IS NOT NULL"),
    )
    op.create_index(
        "uq_users_org_phone_active",
        "users",
        ["org_id", "phone"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL AND phone IS NOT NULL"),
    )

    op.add_column("refresh_tokens", sa.Column("device_id", sa.String(length=100), nullable=True))

    for table in (
        "organizations",
        "roles",
        "users",
        "villages",
        "crop_types",
        "expense_categories",
        "documents",
    ):
        op.execute(
            f"""
            CREATE TRIGGER trg_{table}_updated_at
            BEFORE UPDATE ON {table}
            FOR EACH ROW EXECUTE FUNCTION set_updated_at();
            """
        )


def downgrade() -> None:
    for table in (
        "documents",
        "expense_categories",
        "crop_types",
        "villages",
        "users",
        "roles",
        "organizations",
    ):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{table}_updated_at ON {table};")

    op.drop_index("uq_users_org_phone_active", table_name="users")
    op.drop_index("uq_users_org_email_active", table_name="users")
    op.create_unique_constraint("uq_users_org_email", "users", ["org_id", "email"])
    op.drop_index("ix_user_scopes_org_id", table_name="user_scopes")
    op.drop_table("user_scopes")

    op.drop_column("refresh_tokens", "device_id")
    op.drop_column("expense_categories", "sort_order")
    op.drop_column("expense_categories", "name_te")
    op.drop_column("crop_types", "name_te")
    op.drop_column("villages", "name_te")
    op.drop_column("users", "worker_id")
    op.drop_column("users", "full_name_te")
    op.drop_column("roles", "name_te")
    op.drop_column("permissions", "module")
    op.drop_constraint("ck_organizations_fiscal_year_start_month", "organizations", type_="check")
    op.drop_column("organizations", "fiscal_year_start_month")
    op.drop_column("organizations", "name_te")

    drop_updated_at_function()
    drop_extensions()
