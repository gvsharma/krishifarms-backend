"""Seed global permissions and default role-permission mappings."""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202506210015"
down_revision: Union[str, None] = "202506210014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PERMISSIONS: list[tuple[str, str, str]] = [
    ("users:read", "View users", "users"),
    ("users:create", "Create users", "users"),
    ("users:update", "Update users", "users"),
    ("users:delete", "Delete users", "users"),
    ("roles:read", "View roles", "roles"),
    ("villages:read", "View villages", "master_data"),
    ("villages:create", "Create villages", "master_data"),
    ("villages:update", "Update villages", "master_data"),
    ("villages:delete", "Delete villages", "master_data"),
    ("crop_types:read", "View crop types", "master_data"),
    ("crop_types:create", "Create crop types", "master_data"),
    ("crop_types:update", "Update crop types", "master_data"),
    ("crop_types:delete", "Delete crop types", "master_data"),
    ("expense_categories:read", "View expense categories", "financial"),
    ("expense_categories:create", "Create expense categories", "financial"),
    ("expense_categories:update", "Update expense categories", "financial"),
    ("expense_categories:delete", "Delete expense categories", "financial"),
    ("farmers:read", "View farmers", "farmers"),
    ("farmers:create", "Create farmers", "farmers"),
    ("farmers:update", "Update farmers", "farmers"),
    ("farmers:delete", "Delete farmers", "farmers"),
    ("farms:read", "View farms", "farms"),
    ("farms:create", "Create farms", "farms"),
    ("farms:update", "Update farms", "farms"),
    ("farms:delete", "Delete farms", "farms"),
    ("procurements:read", "View procurements", "procurement"),
    ("procurements:create", "Create procurements", "procurement"),
    ("procurements:update", "Update procurements", "procurement"),
    ("procurements:confirm", "Confirm procurements", "procurement"),
    ("procurements:cancel", "Cancel procurements", "procurement"),
    ("farmer_payments:read", "View farmer payments", "procurement"),
    ("farmer_payments:create", "Create farmer payments", "procurement"),
    ("farmer_payments:reverse", "Reverse farmer payments", "procurement"),
    ("workers:read", "View workers", "workforce"),
    ("workers:create", "Create workers", "workforce"),
    ("workers:update", "Update workers", "workforce"),
    ("workers:delete", "Delete workers", "workforce"),
    ("work_orders:read", "View work orders", "workforce"),
    ("work_orders:create", "Create work orders", "workforce"),
    ("work_orders:update", "Update work orders", "workforce"),
    ("attendance:read", "View attendance", "workforce"),
    ("attendance:create", "Create attendance", "workforce"),
    ("attendance:update", "Update attendance", "workforce"),
    ("assets:read", "View assets", "assets"),
    ("assets:create", "Create assets", "assets"),
    ("assets:update", "Update assets", "assets"),
    ("vehicle_trips:read", "View vehicle trips", "assets"),
    ("vehicle_trips:create", "Create vehicle trips", "assets"),
    ("rentals:read", "View rentals", "rentals"),
    ("rentals:create", "Create rentals", "rentals"),
    ("rentals:update", "Update rentals", "rentals"),
    ("expenses:read", "View expenses", "financial"),
    ("expenses:create", "Create expenses", "financial"),
    ("expenses:update", "Update expenses", "financial"),
    ("collections:read", "View collections", "financial"),
    ("collections:create", "Create collections", "financial"),
    ("payments:read", "View payments", "financial"),
    ("payments:create", "Create payments", "financial"),
    ("documents:read", "View documents", "documents"),
    ("documents:create", "Upload documents", "documents"),
    ("documents:delete", "Delete documents", "documents"),
    ("audit:read", "View audit logs", "audit"),
    ("dashboard:read", "View dashboard", "dashboard"),
    ("ai:read", "View AI suggestions", "ai"),
    ("ai:review", "Review AI suggestions", "ai"),
]

ROLE_PERMISSIONS: dict[str, list[str]] = {
    "OWNER": [code for code, _, _ in PERMISSIONS],
    "MANAGER": [
        "users:read",
        "roles:read",
        "villages:read",
        "villages:create",
        "villages:update",
        "crop_types:read",
        "crop_types:create",
        "crop_types:update",
        "expense_categories:read",
        "expense_categories:create",
        "expense_categories:update",
        "farmers:read",
        "farmers:create",
        "farmers:update",
        "farms:read",
        "farms:create",
        "farms:update",
        "procurements:read",
        "procurements:create",
        "procurements:update",
        "procurements:confirm",
        "procurements:cancel",
        "farmer_payments:read",
        "farmer_payments:create",
        "workers:read",
        "workers:create",
        "workers:update",
        "work_orders:read",
        "work_orders:create",
        "work_orders:update",
        "attendance:read",
        "attendance:create",
        "attendance:update",
        "assets:read",
        "assets:create",
        "assets:update",
        "vehicle_trips:read",
        "vehicle_trips:create",
        "rentals:read",
        "rentals:create",
        "rentals:update",
        "expenses:read",
        "expenses:create",
        "expenses:update",
        "collections:read",
        "collections:create",
        "payments:read",
        "payments:create",
        "documents:read",
        "documents:create",
        "audit:read",
        "dashboard:read",
        "ai:read",
        "ai:review",
    ],
    "SUPERVISOR": [
        "villages:read",
        "crop_types:read",
        "farmers:read",
        "farms:read",
        "farms:update",
        "procurements:read",
        "procurements:create",
        "procurements:update",
        "workers:read",
        "work_orders:read",
        "work_orders:create",
        "work_orders:update",
        "attendance:read",
        "attendance:create",
        "attendance:update",
        "assets:read",
        "vehicle_trips:read",
        "vehicle_trips:create",
        "documents:read",
        "documents:create",
        "dashboard:read",
        "ai:read",
    ],
    "WORKER": [
        "work_orders:read",
        "work_orders:update",
        "attendance:read",
        "attendance:create",
        "documents:read",
        "documents:create",
    ],
}

ROLE_DEFINITIONS: list[tuple[str, str, str | None]] = [
    ("OWNER", "Owner", "యజమాని"),
    ("MANAGER", "Manager", "నిర్వాహకుడు"),
    ("SUPERVISOR", "Farm Supervisor", "వ్యవసాయ పర్యవేక్షకుడు"),
    ("WORKER", "Worker", "కార్మికుడు"),
]


def upgrade() -> None:
    conn = op.get_bind()

    for code, description, module in PERMISSIONS:
        conn.execute(
            sa.text(
                """
                INSERT INTO permissions (id, code, description, module)
                VALUES (:id, :code, :description, :module)
                ON CONFLICT (code) DO UPDATE
                SET description = EXCLUDED.description,
                    module = EXCLUDED.module
                """
            ),
            {"id": str(uuid4()), "code": code, "description": description, "module": module},
        )

    result = conn.execute(sa.text("SELECT id, code FROM permissions"))
    permission_ids = {row.code: str(row.id) for row in result}

    org_rows = conn.execute(sa.text("SELECT id FROM organizations")).fetchall()
    for org_row in org_rows:
        org_id = str(org_row.id)
        role_ids: dict[str, str] = {}

        for code, name, name_te in ROLE_DEFINITIONS:
            existing = conn.execute(
                sa.text("SELECT id FROM roles WHERE org_id = :org_id AND code = :code"),
                {"org_id": org_id, "code": code},
            ).fetchone()
            if existing:
                role_ids[code] = str(existing.id)
                conn.execute(
                    sa.text("UPDATE roles SET name = :name, name_te = :name_te, is_system = TRUE WHERE id = :id"),
                    {"id": role_ids[code], "name": name, "name_te": name_te},
                )
            else:
                role_id = str(uuid4())
                role_ids[code] = role_id
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO roles (id, org_id, code, name, name_te, is_system, created_at, updated_at)
                        VALUES (:id, :org_id, :code, :name, :name_te, TRUE, now(), now())
                        """
                    ),
                    {
                        "id": role_id,
                        "org_id": org_id,
                        "code": code,
                        "name": name,
                        "name_te": name_te,
                    },
                )

        for role_code, perm_codes in ROLE_PERMISSIONS.items():
            role_id = role_ids[role_code]
            conn.execute(
                sa.text("DELETE FROM role_permissions WHERE role_id = :role_id"),
                {"role_id": role_id},
            )
            for perm_code in perm_codes:
                perm_id = permission_ids.get(perm_code)
                if perm_id is None:
                    continue
                conn.execute(
                    sa.text(
                        """
                        INSERT INTO role_permissions (role_id, permission_id)
                        VALUES (:role_id, :permission_id)
                        ON CONFLICT DO NOTHING
                        """
                    ),
                    {"role_id": role_id, "permission_id": perm_id},
                )

    conn.execute(
        sa.text(
            """
            INSERT INTO schema_migrations_log (version, description)
            VALUES (:version, :description)
            """
        ),
        {
            "version": revision,
            "description": "Seed permissions and system roles for all organizations",
        },
    )


def downgrade() -> None:
    conn = op.get_bind()
    codes = [code for code, _, _ in PERMISSIONS]
    conn.execute(
        sa.text("DELETE FROM schema_migrations_log WHERE version = :version"),
        {"version": revision},
    )
    conn.execute(
        sa.text(
            """
            DELETE FROM role_permissions rp
            USING permissions p
            WHERE rp.permission_id = p.id
              AND p.code = ANY(:codes)
            """
        ),
        {"codes": codes},
    )
    conn.execute(
        sa.text("DELETE FROM permissions WHERE code = ANY(:codes)"),
        {"codes": codes},
    )
