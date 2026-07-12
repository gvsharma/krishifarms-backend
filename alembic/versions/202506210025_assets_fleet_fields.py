"""Extend assets for fleet instances + Vehicle Supervisor asset/diesel grants."""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202506210025"
down_revision: Union[str, None] = "202506210024"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DRIVER_EXTRA = [
    "assets:read",
    "assets:create",
    "assets:update",
    "field_services:create",
    "field_services:update",
]

MANAGER_EXTRA = [
    "assets:read",
    "assets:create",
    "assets:update",
]

SUPERVISOR_EXTRA = [
    "assets:read",
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
    op.add_column(
        "assets",
        sa.Column("vehicle_type_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column("assets", sa.Column("fuel_type", sa.String(length=30), nullable=True))
    op.add_column("assets", sa.Column("driver_name", sa.String(length=200), nullable=True))
    op.create_foreign_key(
        "fk_assets_vehicle_type_id",
        "assets",
        "vehicle_types",
        ["vehicle_type_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_assets_org_vehicle_type", "assets", ["org_id", "vehicle_type_id"])

    op.drop_constraint("ck_assets_category", "assets", type_="check")
    op.create_check_constraint(
        "ck_assets_category",
        "assets",
        "asset_category IN ('tractor','dcm','baler','air_machine','bolero','implement','other')",
    )

    conn = op.get_bind()
    # Ensure assets:* exist (seeded in 015); re-assert descriptions for clarity.
    for code, description in [
        ("assets:read", "View assets"),
        ("assets:create", "Create assets"),
        ("assets:update", "Update assets"),
    ]:
        conn.execute(
            sa.text(
                """
                INSERT INTO permissions (id, code, description, module)
                VALUES (:id, :code, :description, 'assets')
                ON CONFLICT (code) DO UPDATE
                SET description = EXCLUDED.description, module = EXCLUDED.module
                """
            ),
            {"id": str(uuid4()), "code": code, "description": description},
        )

    for org_row in conn.execute(sa.text("SELECT id FROM organizations")).fetchall():
        org_id = str(org_row.id)
        _grant_role_permissions(conn, org_id, "OWNER", MANAGER_EXTRA)
        _grant_role_permissions(conn, org_id, "MANAGER", MANAGER_EXTRA)
        _grant_role_permissions(conn, org_id, "SUPERVISOR", SUPERVISOR_EXTRA)
        _grant_role_permissions(conn, org_id, "DRIVER", DRIVER_EXTRA)


def downgrade() -> None:
    conn = op.get_bind()
    for role_code, codes in (
        ("DRIVER", DRIVER_EXTRA),
        ("SUPERVISOR", SUPERVISOR_EXTRA),
    ):
        conn.execute(
            sa.text(
                """
                DELETE FROM role_permissions
                WHERE role_id IN (SELECT id FROM roles WHERE code = :role_code)
                  AND permission_id IN (
                      SELECT id FROM permissions WHERE code = ANY(:codes)
                  )
                """
            ),
            {"role_code": role_code, "codes": codes},
        )

    op.drop_constraint("ck_assets_category", "assets", type_="check")
    op.create_check_constraint(
        "ck_assets_category",
        "assets",
        "asset_category IN ('tractor','dcm','baler','air_machine','other')",
    )
    op.drop_index("ix_assets_org_vehicle_type", table_name="assets")
    op.drop_constraint("fk_assets_vehicle_type_id", "assets", type_="foreignkey")
    op.drop_column("assets", "driver_name")
    op.drop_column("assets", "fuel_type")
    op.drop_column("assets", "vehicle_type_id")
