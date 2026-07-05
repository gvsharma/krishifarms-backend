"""Extend procurement status CHECK for full workflow states."""

from typing import Sequence, Union

from alembic import op

revision: str = "202506210019"
down_revision: Union[str, None] = "202506210018"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_NEW_STATUSES = (
    "'draft','pending_weighment','weighed','priced','confirmed',"
    "'paid_partial','paid_full','cancelled','reversed'"
)


def upgrade() -> None:
    op.drop_constraint("ck_procurements_status", "procurements", type_="check")
    op.create_check_constraint(
        "ck_procurements_status",
        "procurements",
        f"status IN ({_NEW_STATUSES})",
    )


def downgrade() -> None:
    op.drop_constraint("ck_procurements_status", "procurements", type_="check")
    op.create_check_constraint(
        "ck_procurements_status",
        "procurements",
        "status IN ('draft','confirmed','cancelled')",
    )
