"""Village 360° profile fields: code, GPS, agent, status, cultivable area."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202506210031"
down_revision: Union[str, None] = "202506210030"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("villages", sa.Column("village_code", sa.String(length=50), nullable=True))
    op.add_column("villages", sa.Column("geo_lat", sa.Numeric(10, 7), nullable=True))
    op.add_column("villages", sa.Column("geo_lng", sa.Numeric(10, 7), nullable=True))
    op.add_column(
        "villages",
        sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "villages",
        sa.Column("status", sa.String(length=20), server_default="active", nullable=False),
    )
    op.add_column("villages", sa.Column("population", sa.Integer(), nullable=True))
    op.add_column(
        "villages",
        sa.Column("estimated_cultivable_area", sa.Numeric(12, 3), nullable=True),
    )
    op.add_column("villages", sa.Column("notes", sa.Text(), nullable=True))

    op.create_foreign_key(
        "fk_villages_agent_id",
        "villages",
        "field_agents",
        ["agent_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_check_constraint(
        "ck_villages_status",
        "villages",
        "status IN ('active','inactive')",
    )
    op.create_index(
        "uq_villages_org_code_active",
        "villages",
        ["org_id", "village_code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL AND village_code IS NOT NULL"),
    )
    op.create_index("ix_villages_agent_id", "villages", ["agent_id"])

    # Backfill village_code for existing rows (org-scoped sequence)
    op.execute(
        """
        WITH ranked AS (
            SELECT id,
                   org_id,
                   ROW_NUMBER() OVER (PARTITION BY org_id ORDER BY created_at, name) AS rn
            FROM villages
            WHERE deleted_at IS NULL AND village_code IS NULL
        )
        UPDATE villages v
        SET village_code = 'VIL-' || LPAD(ranked.rn::text, 4, '0')
        FROM ranked
        WHERE v.id = ranked.id
        """
    )


def downgrade() -> None:
    op.drop_index("ix_villages_agent_id", table_name="villages")
    op.drop_index("uq_villages_org_code_active", table_name="villages")
    op.drop_constraint("ck_villages_status", "villages", type_="check")
    op.drop_constraint("fk_villages_agent_id", "villages", type_="foreignkey")
    for col in (
        "notes",
        "estimated_cultivable_area",
        "population",
        "status",
        "agent_id",
        "geo_lng",
        "geo_lat",
        "village_code",
    ):
        op.drop_column("villages", col)
