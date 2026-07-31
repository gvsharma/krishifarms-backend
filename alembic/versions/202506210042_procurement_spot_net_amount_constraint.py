"""Fix procurements net_amount check for spot payment deduction."""

from typing import Sequence, Union

from alembic import op

revision: str = "202506210042b"
down_revision: Union[str, None] = "202506210042"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_procurements_net_amount", "procurements", type_="check")
    op.create_check_constraint(
        "ck_procurements_net_amount",
        "procurements",
        "net_amount = gross_amount - deduction_amount - spot_deduction_amount",
    )


def downgrade() -> None:
    op.drop_constraint("ck_procurements_net_amount", "procurements", type_="check")
    op.create_check_constraint(
        "ck_procurements_net_amount",
        "procurements",
        "net_amount = gross_amount - deduction_amount",
    )
