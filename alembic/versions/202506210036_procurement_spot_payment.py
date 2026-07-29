"""Spot (100%) payment flag and per-quintal cash discount on procurements."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202506210036"
down_revision: Union[str, None] = "202506210035"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "procurements",
        sa.Column(
            "is_spot_payment",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.add_column(
        "procurements",
        sa.Column(
            "spot_deduction_per_quintal",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
            server_default="100.00",
        ),
    )
    op.add_column(
        "procurements",
        sa.Column(
            "spot_deduction_amount",
            sa.Numeric(precision=14, scale=2),
            nullable=False,
            server_default="0",
        ),
    )
    op.create_check_constraint(
        "ck_procurements_spot_deduction_per_quintal_non_negative",
        "procurements",
        "spot_deduction_per_quintal >= 0",
    )
    op.create_check_constraint(
        "ck_procurements_spot_deduction_amount_non_negative",
        "procurements",
        "spot_deduction_amount >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_procurements_spot_deduction_amount_non_negative",
        "procurements",
        type_="check",
    )
    op.drop_constraint(
        "ck_procurements_spot_deduction_per_quintal_non_negative",
        "procurements",
        type_="check",
    )
    op.drop_column("procurements", "spot_deduction_amount")
    op.drop_column("procurements", "spot_deduction_per_quintal")
    op.drop_column("procurements", "is_spot_payment")
