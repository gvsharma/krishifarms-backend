"""Seed analytics:admin permission — OWNER-only financial analytics."""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "202506210043"
down_revision: Union[str, None] = "202506210042b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PERM_CODE = "analytics:admin"
PERM_DESC = "View admin analytics (profit, revenue, expenses)"


def _grant_owner(conn, org_id: str) -> None:
    role_row = conn.execute(
        sa.text("SELECT id FROM roles WHERE org_id = :org_id AND code = 'OWNER'"),
        {"org_id": org_id},
    ).fetchone()
    perm_row = conn.execute(
        sa.text("SELECT id FROM permissions WHERE code = :code"),
        {"code": PERM_CODE},
    ).fetchone()
    if not role_row or not perm_row:
        return
    conn.execute(
        sa.text(
            """
            INSERT INTO role_permissions (role_id, permission_id)
            VALUES (:role_id, :permission_id)
            ON CONFLICT DO NOTHING
            """
        ),
        {"role_id": str(role_row.id), "permission_id": str(perm_row.id)},
    )


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            INSERT INTO permissions (id, code, description, module)
            VALUES (:id, :code, :description, 'analytics')
            ON CONFLICT (code) DO UPDATE
            SET description = EXCLUDED.description, module = EXCLUDED.module
            """
        ),
        {"id": str(uuid4()), "code": PERM_CODE, "description": PERM_DESC},
    )
    for org_row in conn.execute(sa.text("SELECT id FROM organizations")).fetchall():
        _grant_owner(conn, str(org_row.id))


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            DELETE FROM role_permissions
            WHERE permission_id IN (SELECT id FROM permissions WHERE code = :code)
            """
        ),
        {"code": PERM_CODE},
    )
    conn.execute(sa.text("DELETE FROM permissions WHERE code = :code"), {"code": PERM_CODE})
