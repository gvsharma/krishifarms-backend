"""Add per-bag weight deduction (kata) to procurements.

Standard grain-procurement practice deducts a fixed weight per bag (default
2 kg/bag) before computing the payable net weight:
    net_weight_kg = gross_weight_kg - tare_weight_kg - (bag_count * per_bag_deduction_kg)
"""

from decimal import Decimal
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202506210035"
down_revision: Union[str, None] = "202506210034"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_DEFAULT_PER_BAG_KG = "2.000"


def upgrade() -> None:
    op.add_column(
        "procurements",
        sa.Column(
            "per_bag_deduction_kg",
            sa.Numeric(precision=6, scale=3),
            nullable=False,
            server_default=_DEFAULT_PER_BAG_KG,
        ),
    )
    op.create_check_constraint(
        "ck_procurements_per_bag_deduction_kg_non_negative",
        "procurements",
        "per_bag_deduction_kg >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_procurements_per_bag_deduction_kg_non_negative",
        "procurements",
        type_="check",
    )
    op.drop_column("procurements", "per_bag_deduction_kg")


# Keep the default value referenced for documentation / tooling.
DEFAULT_PER_BAG_DEDUCTION_KG = Decimal(_DEFAULT_PER_BAG_KG)
