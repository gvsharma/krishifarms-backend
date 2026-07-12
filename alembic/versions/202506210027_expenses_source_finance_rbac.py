"""Expenses source linkage + finance RBAC (expenses/collections)."""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202506210027"
down_revision: Union[str, None] = "202506210026"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_PERMISSIONS = [
    ("expenses:read", "View expenses", "expenses"),
    ("expenses:create", "Create expenses", "expenses"),
    ("expenses:update", "Update expenses", "expenses"),
    ("expenses:delete", "Delete expenses", "expenses"),
    ("collections:read", "View collections", "collections"),
    ("collections:create", "Create collections", "collections"),
]

MANAGER_EXTRA = [
    "expenses:read",
    "expenses:create",
    "expenses:update",
    "collections:read",
    "collections:create",
]
OWNER_EXTRA = [code for code, _, _ in NEW_PERMISSIONS]


def _grant_role_permissions(conn, org_id: str, role_code: str, perm_codes: list[str]) -> None:
    role_row = conn.execute(
        sa.text("SELECT id FROM roles WHERE org_id = :org_id AND code = :code"),
        {"org_id": org_id, "code": role_code},
    ).fetchone()
    if not role_row:
        return
    role_id = str(role_row.id)
    for code in perm_codes:
        perm_row = conn.execute(
            sa.text("SELECT id FROM permissions WHERE code = :code"),
            {"code": code},
        ).fetchone()
        if not perm_row:
            continue
        conn.execute(
            sa.text(
                """
                INSERT INTO role_permissions (role_id, permission_id)
                VALUES (:role_id, :permission_id)
                ON CONFLICT DO NOTHING
                """
            ),
            {"role_id": role_id, "permission_id": str(perm_row.id)},
        )


def upgrade() -> None:
    op.add_column("expenses", sa.Column("source_type", sa.String(length=50), nullable=True))
    op.add_column("expenses", sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index(
        "uq_expenses_org_source_active",
        "expenses",
        ["org_id", "source_type", "source_id"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL AND source_type IS NOT NULL"),
    )
    op.create_index("ix_expenses_org_source", "expenses", ["org_id", "source_type", "source_id"])

    conn = op.get_bind()
    for code, description, module in NEW_PERMISSIONS:
        conn.execute(
            sa.text(
                """
                INSERT INTO permissions (id, code, description, module)
                VALUES (:id, :code, :description, :module)
                ON CONFLICT (code) DO UPDATE
                SET description = EXCLUDED.description, module = EXCLUDED.module
                """
            ),
            {"id": str(uuid4()), "code": code, "description": description, "module": module},
        )

    for org_row in conn.execute(sa.text("SELECT id FROM organizations")).fetchall():
        org_id = str(org_row.id)
        _grant_role_permissions(conn, org_id, "OWNER", OWNER_EXTRA)
        _grant_role_permissions(conn, org_id, "MANAGER", MANAGER_EXTRA)


def downgrade() -> None:
    conn = op.get_bind()
    codes = [code for code, _, _ in NEW_PERMISSIONS]
    conn.execute(
        sa.text(
            """
            DELETE FROM role_permissions
            WHERE permission_id IN (SELECT id FROM permissions WHERE code = ANY(:codes))
            """
        ),
        {"codes": codes},
    )
    conn.execute(sa.text("DELETE FROM permissions WHERE code = ANY(:codes)"), {"codes": codes})

    op.drop_index("ix_expenses_org_source", table_name="expenses")
    op.drop_index("uq_expenses_org_source_active", table_name="expenses")
    op.drop_column("expenses", "source_id")
    op.drop_column("expenses", "source_type")
