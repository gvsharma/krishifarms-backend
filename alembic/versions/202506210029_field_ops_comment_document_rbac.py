"""Grant field-ops RBAC: farmer comments + agent/driver document uploads."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202506210029"
down_revision: Union[str, None] = "202506210028"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Existing permissions — grant only (no new permission rows).
FARMER_PERMS = ["comments:create"]
AGENT_DRIVER_PERMS = ["documents:read", "documents:create"]


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


def _revoke_role_permissions(conn, org_id: str, role_code: str, perm_codes: list[str]) -> None:
    role_row = conn.execute(
        sa.text("SELECT id FROM roles WHERE org_id = :org_id AND code = :code"),
        {"org_id": org_id, "code": role_code},
    ).fetchone()
    if not role_row:
        return
    role_id = str(role_row.id)
    for code in perm_codes:
        conn.execute(
            sa.text(
                """
                DELETE FROM role_permissions
                WHERE role_id = :role_id
                  AND permission_id IN (SELECT id FROM permissions WHERE code = :code)
                """
            ),
            {"role_id": role_id, "code": code},
        )


def upgrade() -> None:
    conn = op.get_bind()
    for org_row in conn.execute(sa.text("SELECT id FROM organizations")).fetchall():
        org_id = str(org_row.id)
        _grant_role_permissions(conn, org_id, "FARMER", FARMER_PERMS)
        _grant_role_permissions(conn, org_id, "AGENT", AGENT_DRIVER_PERMS)
        _grant_role_permissions(conn, org_id, "DRIVER", AGENT_DRIVER_PERMS)


def downgrade() -> None:
    conn = op.get_bind()
    for org_row in conn.execute(sa.text("SELECT id FROM organizations")).fetchall():
        org_id = str(org_row.id)
        _revoke_role_permissions(conn, org_id, "FARMER", FARMER_PERMS)
        _revoke_role_permissions(conn, org_id, "AGENT", AGENT_DRIVER_PERMS)
        _revoke_role_permissions(conn, org_id, "DRIVER", AGENT_DRIVER_PERMS)
