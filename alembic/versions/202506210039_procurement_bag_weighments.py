"""Procurement bag weighment entries and tare on weighment."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from migration_utils import audit_columns, org_fk

revision: str = "202506210039"
down_revision: Union[str, None] = "202506210038"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "procurements",
        sa.Column("tare_weight_kg", sa.Numeric(12, 3), server_default="0", nullable=False),
    )
    op.create_check_constraint(
        "ck_procurements_tare_weight_kg_non_negative",
        "procurements",
        "tare_weight_kg >= 0",
    )

    op.create_table(
        "procurement_bag_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("procurement_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("procurement_date", sa.Date(), nullable=False),
        sa.Column("bag_number", sa.Integer(), nullable=False),
        sa.Column("weight_kg", sa.Numeric(12, 3), nullable=False),
        *audit_columns(),
        org_fk(),
        sa.ForeignKeyConstraint(
            ["procurement_id", "procurement_date"],
            ["procurements.id", "procurements.procurement_date"],
            ondelete="CASCADE",
        ),
        sa.CheckConstraint("bag_number > 0", name="ck_procurement_bag_entries_bag_number_positive"),
        sa.CheckConstraint("weight_kg > 0", name="ck_procurement_bag_entries_weight_positive"),
        sa.UniqueConstraint(
            "procurement_id",
            "procurement_date",
            "bag_number",
            name="uq_procurement_bag_entries_bag",
        ),
    )
    op.create_index(
        "ix_procurement_bag_entries_procurement",
        "procurement_bag_entries",
        ["procurement_id", "procurement_date"],
    )


def downgrade() -> None:
    op.drop_index("ix_procurement_bag_entries_procurement", table_name="procurement_bag_entries")
    op.drop_table("procurement_bag_entries")
    op.drop_constraint("ck_procurements_tare_weight_kg_non_negative", "procurements", type_="check")
    op.drop_column("procurements", "tare_weight_kg")
