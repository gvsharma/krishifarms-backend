"""Seed payment_modes:* permissions omitted from platform RBAC 018."""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "202506210028"
down_revision: Union[str, None] = "202506210027"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_PERMISSIONS: list[tuple[str, str, str]] = [
    ("payment_modes:read", "View payment modes", "master_data"),
    ("payment_modes:create", "Create payment modes", "master_data"),
    ("payment_modes:update", "Update payment modes", "master_data"),
    ("payment_modes:delete", "Delete payment modes", "master_data"),
]

MANAGER_PERMS = [code for code, _, _ in NEW_PERMISSIONS if not code.endswith(":delete")]
SUPERVISOR_PERMS = ["payment_modes:read"]


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
        _grant_role_permissions(conn, org_id, "OWNER", [code for code, _, _ in NEW_PERMISSIONS])
        _grant_role_permissions(conn, org_id, "MANAGER", MANAGER_PERMS)
        _grant_role_permissions(conn, org_id, "SUPERVISOR", SUPERVISOR_PERMS)


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
