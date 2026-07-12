"""RBAC role alignment: location masters, soft-wired domain perms, Farmer role."""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op

revision: str = "202506210024"
down_revision: Union[str, None] = "202506210023"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_PERMISSIONS: list[tuple[str, str, str]] = [
    ("districts:read", "View districts", "master_data"),
    ("districts:create", "Create districts", "master_data"),
    ("districts:update", "Update districts", "master_data"),
    ("districts:delete", "Delete districts", "master_data"),
    ("mandals:read", "View mandals", "master_data"),
    ("mandals:create", "Create mandals", "master_data"),
    ("mandals:update", "Update mandals", "master_data"),
    ("mandals:delete", "Delete mandals", "master_data"),
    ("master_data:read", "View master data catalogs", "master_data"),
    ("vehicles:read", "View vehicles / fleet", "fleet"),
    ("transport:read", "View transport trips", "fleet"),
    ("transport:create", "Create transport trips", "fleet"),
    ("transport:update", "Update transport trips", "fleet"),
    ("diesel:read", "View diesel logs", "fleet"),
    ("diesel:create", "Create diesel logs", "fleet"),
    ("diesel:update", "Update diesel logs", "fleet"),
    ("farming:read", "View farming / field ops", "operations"),
    ("farming:create", "Create farming / field ops", "operations"),
    ("farming:update", "Update farming / field ops", "operations"),
    ("finance:read", "View finance modules", "finance"),
    ("approve", "Approve workflow actions", "platform"),
    ("delete", "Hard-privileged delete actions", "platform"),
]

ROLE_DISPLAY_UPDATES = [
    ("OWNER", "Admin / Owner"),
    ("MANAGER", "Manager"),
    ("SUPERVISOR", "Farming Supervisor"),
    ("AGENT", "Agent"),
    ("DRIVER", "Vehicle Supervisor"),
]

MANAGER_NEW = [
    "districts:read",
    "districts:create",
    "districts:update",
    "mandals:read",
    "mandals:create",
    "mandals:update",
    "master_data:read",
    "vehicles:read",
    "transport:read",
    "transport:create",
    "transport:update",
    "diesel:read",
    "diesel:create",
    "diesel:update",
    "farming:read",
    "farming:create",
    "farming:update",
    "finance:read",
    "approve",
]

SUPERVISOR_NEW = [
    "districts:read",
    "mandals:read",
    "master_data:read",
    "farming:read",
    "farming:create",
    "farming:update",
    "vehicles:read",
]

DRIVER_NEW = [
    "districts:read",
    "mandals:read",
    "villages:read",
    "vehicles:read",
    "transport:read",
    "transport:create",
    "transport:update",
    "diesel:read",
    "diesel:create",
    "diesel:update",
    "field_services:read",
]

AGENT_NEW = [
    "districts:read",
    "mandals:read",
    "villages:read",
    "farmers:read",
    "farming:read",
    "master_data:read",
]

FARMER_PERMS = [
    "districts:read",
    "mandals:read",
    "villages:read",
    "crop_types:read",
    "crop_prices:read",
    "farmers:read",
    "procurements:read",
    "field_services:read",
    "farming:read",
    "documents:read",
    "comments:read",
    "dashboard:read",
    "master_data:read",
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

    org_rows = conn.execute(sa.text("SELECT id FROM organizations")).fetchall()
    for org_row in org_rows:
        org_id = str(org_row.id)

        for role_code, display_name in ROLE_DISPLAY_UPDATES:
            conn.execute(
                sa.text(
                    """
                    UPDATE roles
                    SET name = :name, updated_at = now()
                    WHERE org_id = :org_id AND code = :code
                    """
                ),
                {"org_id": org_id, "code": role_code, "name": display_name},
            )

        existing_farmer = conn.execute(
            sa.text("SELECT id FROM roles WHERE org_id = :org_id AND code = 'FARMER'"),
            {"org_id": org_id},
        ).fetchone()
        if not existing_farmer:
            conn.execute(
                sa.text(
                    """
                    INSERT INTO roles (id, org_id, code, name, name_te, is_system, created_at, updated_at)
                    VALUES (:id, :org_id, 'FARMER', 'Farmer', 'రైతు', TRUE, now(), now())
                    """
                ),
                {"id": str(uuid4()), "org_id": org_id},
            )

        _grant_role_permissions(conn, org_id, "OWNER", [code for code, _, _ in NEW_PERMISSIONS])
        _grant_role_permissions(conn, org_id, "MANAGER", MANAGER_NEW)
        _grant_role_permissions(conn, org_id, "SUPERVISOR", SUPERVISOR_NEW)
        _grant_role_permissions(conn, org_id, "DRIVER", DRIVER_NEW)
        _grant_role_permissions(conn, org_id, "AGENT", AGENT_NEW)
        _grant_role_permissions(conn, org_id, "FARMER", FARMER_PERMS)

        # Align manager: no users:create (provisioning is OWNER-only).
        conn.execute(
            sa.text(
                """
                DELETE FROM role_permissions
                WHERE role_id = (
                    SELECT id FROM roles WHERE org_id = :org_id AND code = 'MANAGER'
                )
                AND permission_id = (
                    SELECT id FROM permissions WHERE code = 'users:create'
                )
                """
            ),
            {"org_id": org_id},
        )


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
    conn.execute(sa.text("DELETE FROM role_permissions WHERE role_id IN (SELECT id FROM roles WHERE code = 'FARMER')"))
    conn.execute(sa.text("DELETE FROM roles WHERE code = 'FARMER'"))
    for role_code, old_name in [
        ("OWNER", "Owner"),
        ("SUPERVISOR", "Farm Supervisor"),
        ("AGENT", "Field Agent"),
        ("DRIVER", "Driver"),
    ]:
        conn.execute(
            sa.text("UPDATE roles SET name = :name WHERE code = :code"),
            {"name": old_name, "code": role_code},
        )
