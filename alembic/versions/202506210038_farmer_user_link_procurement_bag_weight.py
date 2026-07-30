"""Link users to farmers; store per-bag gross weight on procurements."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202506210038"
down_revision: Union[str, None] = "202506210037"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("farmer_id", sa.UUID(), sa.ForeignKey("farmers.id"), nullable=True),
    )
    op.create_index("ix_users_farmer_id", "users", ["farmer_id"], unique=False)

    op.add_column(
        "procurements",
        sa.Column("weight_per_bag_kg", sa.Numeric(precision=8, scale=3), nullable=True),
    )
    op.create_check_constraint(
        "ck_procurements_weight_per_bag_kg_positive",
        "procurements",
        "weight_per_bag_kg IS NULL OR weight_per_bag_kg > 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_procurements_weight_per_bag_kg_positive", "procurements", type_="check")
    op.drop_column("procurements", "weight_per_bag_kg")
    op.drop_index("ix_users_farmer_id", table_name="users")
    op.drop_column("users", "farmer_id")
