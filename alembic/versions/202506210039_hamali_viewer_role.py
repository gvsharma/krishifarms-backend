"""HAMALI viewer role + link users to hamali_workers roster."""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "202506210039"
down_revision: Union[str, None] = "202506210038"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

HAMALI_ROLE_PERMS = ["hamali:read", "dashboard:read"]


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("hamali_worker_id", sa.UUID(), sa.ForeignKey("hamali_workers.id"), nullable=True),
    )
    op.create_index("ix_users_hamali_worker_id", "users", ["hamali_worker_id"], unique=False)

    conn = op.get_bind()
    for org_row in conn.execute(sa.text("SELECT id FROM organizations")).fetchall():
        org_id = str(org_row.id)
        role_row = conn.execute(
            sa.text("SELECT id FROM roles WHERE org_id = :org_id AND code = 'HAMALI'"),
            {"org_id": org_id},
        ).fetchone()
        if not role_row:
            role_id = str(uuid4())
            conn.execute(
                sa.text(
                    """
                    INSERT INTO roles (id, org_id, code, name, name_te, is_system, created_at, updated_at)
                    VALUES (:id, :org_id, 'HAMALI', 'Hamali / Porter', 'హమాలి', TRUE, NOW(), NOW())
                    """
                ),
                {"id": role_id, "org_id": org_id},
            )
        else:
            role_id = str(role_row.id)

        for code in HAMALI_ROLE_PERMS:
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


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            DELETE FROM role_permissions
            WHERE role_id IN (SELECT id FROM roles WHERE code = 'HAMALI')
            """
        )
    )
    conn.execute(sa.text("DELETE FROM roles WHERE code = 'HAMALI'"))
    op.drop_index("ix_users_hamali_worker_id", table_name="users")
    op.drop_column("users", "hamali_worker_id")
