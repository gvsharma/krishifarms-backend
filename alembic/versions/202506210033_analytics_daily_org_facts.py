"""Analytics daily org facts summary table for Admin Analytics Hub Phase 1.

down_revision is 031 (Village 360). Revision id 033 leaves 032 free for the
farmer-relationship hub migration on the farmer-360 WIP branch.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202506210033"
down_revision: Union[str, None] = "202506210031"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UUID = postgresql.UUID(as_uuid=True)


def upgrade() -> None:
    op.create_table(
        "analytics_daily_org_facts",
        sa.Column("id", UUID, primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", UUID, sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("fact_date", sa.Date(), nullable=False),
        sa.Column("revenue", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("expenses", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("collections", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("procurement_kg", sa.Numeric(14, 3), nullable=False, server_default="0"),
        sa.Column("procurement_net_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("field_service_amount", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("outstanding", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("farmers_active", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("procurements_confirmed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("trips_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("field_services_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("org_id", "fact_date", name="uq_analytics_daily_org_facts_org_date"),
    )
    op.create_index(
        "ix_analytics_daily_org_facts_org_date",
        "analytics_daily_org_facts",
        ["org_id", "fact_date"],
    )
    op.create_index(
        "ix_analytics_daily_org_facts_fact_date",
        "analytics_daily_org_facts",
        ["fact_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_analytics_daily_org_facts_fact_date", table_name="analytics_daily_org_facts")
    op.drop_index("ix_analytics_daily_org_facts_org_date", table_name="analytics_daily_org_facts")
    op.drop_table("analytics_daily_org_facts")
