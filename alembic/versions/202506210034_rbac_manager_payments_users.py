"""Repair MANAGER role_permissions for farmer payments and user create."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202506210034"
down_revision: Union[str, None] = "202506210033"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

MANAGER_REPAIR = [
    "users:create",
    "farmer_payments:read",
    "farmer_payments:create",
]


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
    for org_row in conn.execute(sa.text("SELECT id FROM organizations")).fetchall():
        org_id = str(org_row.id)
        _grant_role_permissions(conn, org_id, "MANAGER", MANAGER_REPAIR)
        _grant_role_permissions(conn, org_id, "OWNER", MANAGER_REPAIR)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            DELETE FROM role_permissions
            WHERE permission_id IN (
                SELECT id FROM permissions WHERE code = ANY(:codes)
            )
            AND role_id IN (
                SELECT id FROM roles WHERE code = 'MANAGER'
            )
            """
        ),
        {"codes": MANAGER_REPAIR},
    )
