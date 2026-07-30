"""Buyer sale assignment fields on procurements (Part B).

Adds the sale side of a procurement so multiple farmer crops can be assigned to
one buyer separately from intake:
- ``sale_rate_per_quintal`` — rate the crop is sold to the buyer at (drives margin).
- ``sale_date`` — dispatch / sale date to the buyer.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202506210042"
down_revision: Union[str, None] = "202506210041"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "procurements",
        sa.Column("sale_rate_per_quintal", sa.Numeric(precision=14, scale=2), nullable=True),
    )
    op.add_column(
        "procurements",
        sa.Column("sale_date", sa.Date(), nullable=True),
    )
    op.create_check_constraint(
        "ck_procurements_sale_rate_per_quintal_non_negative",
        "procurements",
        "sale_rate_per_quintal IS NULL OR sale_rate_per_quintal >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_procurements_sale_rate_per_quintal_non_negative",
        "procurements",
        type_="check",
    )
    op.drop_column("procurements", "sale_date")
    op.drop_column("procurements", "sale_rate_per_quintal")
