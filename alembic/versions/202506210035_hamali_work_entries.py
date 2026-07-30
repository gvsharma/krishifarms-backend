"""Hamali work entries table + HAMALI role RBAC."""

from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import audit_columns, org_fk

revision: str = "202506210035"
down_revision: Union[str, None] = "202506210034"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

NEW_PERMISSIONS: list[tuple[str, str]] = [
    ("hamali_work:read", "View hamali bag and tip records"),
    ("hamali_work:create", "Log hamali bag and tip records"),
    ("hamali_work:update", "Update hamali bag and tip records"),
    ("hamali_work:delete", "Delete hamali bag and tip records"),
    ("workers:read", "View worker profiles"),
    ("workers:create", "Create worker profiles"),
]

HAMALI_ROLE_PERMS = ["hamali_work:read", "dashboard:read"]

MANAGER_HAMALI = [
    "hamali_work:read",
    "hamali_work:create",
    "hamali_work:update",
    "hamali_work:delete",
    "workers:read",
    "workers:create",
]

SUPERVISOR_HAMALI = [
    "hamali_work:read",
    "hamali_work:create",
    "hamali_work:update",
    "workers:read",
    "workers:create",
]

OWNER_EXTRA = MANAGER_HAMALI


def _insert_permissions(conn) -> dict[str, str]:
    ids: dict[str, str] = {}
    for code, description in NEW_PERMISSIONS:
        row = conn.execute(
            sa.text("SELECT id FROM permissions WHERE code = :code"),
            {"code": code},
        ).fetchone()
        if row:
            ids[code] = str(row.id)
            continue
        perm_id = str(uuid4())
        conn.execute(
            sa.text(
                """
                INSERT INTO permissions (id, code, description)
                VALUES (:id, :code, :description)
                """
            ),
            {"id": perm_id, "code": code, "description": description},
        )
        ids[code] = perm_id
    return ids


def _grant(conn, org_id: str, role_code: str, perm_codes: list[str], perm_ids: dict[str, str]) -> None:
    role_row = conn.execute(
        sa.text("SELECT id FROM roles WHERE org_id = :org_id AND code = :code"),
        {"org_id": org_id, "code": role_code},
    ).fetchone()
    if not role_row:
        return
    role_id = str(role_row.id)
    for code in perm_codes:
        perm_id = perm_ids.get(code)
        if not perm_id:
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


def upgrade() -> None:
    op.create_table(
        "hamali_work_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("worker_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farmer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("work_date", sa.Date(), nullable=False),
        sa.Column("bag_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tip_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("procurement_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(["worker_id"], ["workers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["procurement_id"], ["procurements.id"], ondelete="SET NULL"),
        sa.CheckConstraint("bag_count >= 0", name="ck_hamali_work_entries_bag_count"),
        sa.CheckConstraint("tip_amount >= 0", name="ck_hamali_work_entries_tip_amount"),
    )
    op.create_index("ix_hamali_work_entries_org_worker_date", "hamali_work_entries", ["org_id", "worker_id", "work_date"])
    op.create_index("ix_hamali_work_entries_org_farmer", "hamali_work_entries", ["org_id", "farmer_id"])
    op.execute(
        """
        CREATE TRIGGER trg_hamali_work_entries_updated_at
        BEFORE UPDATE ON hamali_work_entries
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )

    conn = op.get_bind()
    perm_ids = _insert_permissions(conn)

    for org_row in conn.execute(sa.text("SELECT id FROM organizations")).fetchall():
        org_id = str(org_row.id)

        hamali_role = conn.execute(
            sa.text("SELECT id FROM roles WHERE org_id = :org_id AND code = 'HAMALI'"),
            {"org_id": org_id},
        ).fetchone()
        if not hamali_role:
            role_id = str(uuid4())
            conn.execute(
                sa.text(
                    """
                    INSERT INTO roles (id, org_id, code, name, is_system, created_at, updated_at)
                    VALUES (:id, :org_id, 'HAMALI', 'Hamali / Porter', TRUE, NOW(), NOW())
                    """
                ),
                {"id": role_id, "org_id": org_id},
            )
        _grant(conn, org_id, "HAMALI", HAMALI_ROLE_PERMS, perm_ids)
        _grant(conn, org_id, "MANAGER", MANAGER_HAMALI, perm_ids)
        _grant(conn, org_id, "SUPERVISOR", SUPERVISOR_HAMALI, perm_ids)
        _grant(conn, org_id, "OWNER", OWNER_EXTRA, perm_ids)


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM role_permissions WHERE role_id IN (SELECT id FROM roles WHERE code = 'HAMALI')"))
    conn.execute(sa.text("DELETE FROM roles WHERE code = 'HAMALI'"))
    for code, _ in NEW_PERMISSIONS:
        conn.execute(
            sa.text("DELETE FROM role_permissions WHERE permission_id IN (SELECT id FROM permissions WHERE code = :code)"),
            {"code": code},
        )
        conn.execute(sa.text("DELETE FROM permissions WHERE code = :code"), {"code": code})
    op.drop_table("hamali_work_entries")
