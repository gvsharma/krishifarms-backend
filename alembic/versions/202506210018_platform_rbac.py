"""Platform RBAC: new permissions, AGENT/DRIVER roles, manager delete restrictions."""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "202506210018"
down_revision: Union[str, None] = "202506210017"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_PERMISSIONS: list[tuple[str, str, str]] = [
    ("crop_prices:read", "View crop prices", "master_data"),
    ("crop_prices:create", "Create crop prices", "master_data"),
    ("crop_prices:update", "Update crop prices", "master_data"),
    ("crop_prices:delete", "Delete crop prices", "master_data"),
    ("buyers:read", "View buyers", "master_data"),
    ("buyers:create", "Create buyers", "master_data"),
    ("buyers:update", "Update buyers", "master_data"),
    ("buyers:delete", "Delete buyers", "master_data"),
    ("agents:read", "View field agents", "master_data"),
    ("agents:create", "Create field agents", "master_data"),
    ("agents:update", "Update field agents", "master_data"),
    ("agents:delete", "Delete field agents", "master_data"),
    ("activity_types:read", "View service types", "master_data"),
    ("activity_types:create", "Create service types", "master_data"),
    ("activity_types:update", "Update service types", "master_data"),
    ("activity_types:delete", "Delete service types", "master_data"),
    ("vehicle_types:read", "View vehicle types", "master_data"),
    ("vehicle_types:create", "Create vehicle types", "master_data"),
    ("vehicle_types:update", "Update vehicle types", "master_data"),
    ("vehicle_types:delete", "Delete vehicle types", "master_data"),
    ("comments:read", "View comments", "platform"),
    ("comments:create", "Add comments", "platform"),
    ("tags:read", "View tags", "platform"),
    ("tags:create", "Add tags", "platform"),
    ("tags:delete", "Remove tags", "platform"),
]

MANAGER_PLATFORM_READ_CREATE_UPDATE = [
    code for code, _, _ in NEW_PERMISSIONS if not code.endswith(":delete")
]

AGENT_DRIVER_PERMS = [
    "comments:read",
    "comments:create",
    "tags:read",
    "dashboard:read",
]

DRIVER_EXTRA = ["vehicle_types:read"]

NEW_ROLES = [
    ("AGENT", "Field Agent", "ఫీల్డ్ ఏజెంట్"),
    ("DRIVER", "Driver", "డ్రైవర్"),
]


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

    perm_rows = conn.execute(sa.text("SELECT id, code FROM permissions")).fetchall()
    permission_ids = {row.code: str(row.id) for row in perm_rows}

    org_rows = conn.execute(sa.text("SELECT id FROM organizations")).fetchall()
    for org_row in org_rows:
        org_id = str(org_row.id)

        for code, name, name_te in NEW_ROLES:
            existing = conn.execute(
                sa.text("SELECT id FROM roles WHERE org_id = :org_id AND code = :code"),
                {"org_id": org_id, "code": code},
            ).fetchone()
            if not existing:
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO roles (id, org_id, code, name, name_te, is_system, created_at, updated_at)
                        VALUES (:id, :org_id, :code, :name, :name_te, TRUE, now(), now())
                        """
                    ),
                    {"id": str(uuid4()), "org_id": org_id, "code": code, "name": name, "name_te": name_te},
                )

        owner = conn.execute(
            sa.text("SELECT id FROM roles WHERE org_id = :org_id AND code = 'OWNER'"),
            {"org_id": org_id},
        ).fetchone()
        manager = conn.execute(
            sa.text("SELECT id FROM roles WHERE org_id = :org_id AND code = 'MANAGER'"),
            {"org_id": org_id},
        ).fetchone()
        agent = conn.execute(
            sa.text("SELECT id FROM roles WHERE org_id = :org_id AND code = 'AGENT'"),
            {"org_id": org_id},
        ).fetchone()
        driver = conn.execute(
            sa.text("SELECT id FROM roles WHERE org_id = :org_id AND code = 'DRIVER'"),
            {"org_id": org_id},
        ).fetchone()

        if owner:
            for code, _, _ in NEW_PERMISSIONS:
                pid = permission_ids.get(code)
                if pid:
                    conn.execute(
                        sa.text(
                            """
                            INSERT INTO role_permissions (role_id, permission_id)
                            VALUES (:role_id, :permission_id)
                            ON CONFLICT DO NOTHING
                            """
                        ),
                        {"role_id": str(owner.id), "permission_id": pid},
                    )

        if manager:
            conn.execute(
                sa.text(
                    """
                    DELETE FROM role_permissions rp
                    USING permissions p, roles r
                    WHERE rp.role_id = r.id AND rp.permission_id = p.id
                      AND r.id = :role_id
                      AND (p.code LIKE '%:delete' OR p.code = 'users:create')
                    """
                ),
                {"role_id": str(manager.id)},
            )
            for code in MANAGER_PLATFORM_READ_CREATE_UPDATE:
                pid = permission_ids.get(code)
                if pid:
                    conn.execute(
                        sa.text(
                            """
                            INSERT INTO role_permissions (role_id, permission_id)
                            VALUES (:role_id, :permission_id)
                            ON CONFLICT DO NOTHING
                            """
                        ),
                        {"role_id": str(manager.id), "permission_id": pid},
                    )

        for role_row, extra in ((agent, []), (driver, DRIVER_EXTRA)):
            if not role_row:
                continue
            conn.execute(
                sa.text("DELETE FROM role_permissions WHERE role_id = :role_id"),
                {"role_id": str(role_row.id)},
            )
            for code in AGENT_DRIVER_PERMS + extra:
                pid = permission_ids.get(code)
                if pid:
                    conn.execute(
                        sa.text(
                            """
                            INSERT INTO role_permissions (role_id, permission_id)
                            VALUES (:role_id, :permission_id)
                            ON CONFLICT DO NOTHING
                            """
                        ),
                        {"role_id": str(role_row.id), "permission_id": pid},
                    )


def downgrade() -> None:
    conn = op.get_bind()
    codes = [code for code, _, _ in NEW_PERMISSIONS]
    conn.execute(
        sa.text(
            """
            DELETE FROM role_permissions rp
            USING permissions p
            WHERE rp.permission_id = p.id AND p.code = ANY(:codes)
            """
        ),
        {"codes": codes},
    )
    conn.execute(
        sa.text("DELETE FROM roles WHERE code IN ('AGENT', 'DRIVER')"),
    )
    conn.execute(
        sa.text("DELETE FROM permissions WHERE code = ANY(:codes)"),
        {"codes": codes},
    )
