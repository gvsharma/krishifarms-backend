"""Add buyer_id and payment terms columns to procurements."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "202506210026"
down_revision: Union[str, None] = "202506210025"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_PAYMENT_TERMS = "'one_week','10_days','2_weeks','20_days','custom'"


def upgrade() -> None:
    op.add_column(
        "procurements",
        sa.Column("buyer_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "procurements",
        sa.Column("payment_terms", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "procurements",
        sa.Column("payment_terms_custom", sa.Text(), nullable=True),
    )
    op.add_column(
        "procurements",
        sa.Column("expected_payment_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "procurements",
        sa.Column("actual_payment_date", sa.Date(), nullable=True),
    )
    op.create_foreign_key(
        "fk_procurements_buyer_id",
        "procurements",
        "buyers",
        ["buyer_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index("ix_procurements_org_buyer", "procurements", ["org_id", "buyer_id"])
    op.create_check_constraint(
        "ck_procurements_payment_terms",
        "procurements",
        f"payment_terms IS NULL OR payment_terms IN ({_PAYMENT_TERMS})",
    )


def downgrade() -> None:
    op.drop_constraint("ck_procurements_payment_terms", "procurements", type_="check")
    op.drop_index("ix_procurements_org_buyer", table_name="procurements")
    op.drop_constraint("fk_procurements_buyer_id", "procurements", type_="foreignkey")
    op.drop_column("procurements", "actual_payment_date")
    op.drop_column("procurements", "expected_payment_date")
    op.drop_column("procurements", "payment_terms_custom")
    op.drop_column("procurements", "payment_terms")
    op.drop_column("procurements", "buyer_id")
