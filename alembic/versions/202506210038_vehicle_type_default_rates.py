"""Default per-unit rates on vehicle types (tractor implements)."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202506210038"
down_revision: Union[str, None] = "202506210037"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Cultivator ₹1200/hr, Rotavator ₹1440/hr, Trolley ₹250/trip, Baler ₹40/bale,
# Weeder ₹1000/hr, Fertilizer pump ₹500/hr
_VEHICLE_RATES: dict[str, tuple[str, str]] = {
    "CULTIVATOR": ("1200.00", "hour"),
    "ROTAVATOR": ("1440.00", "hour"),
    "TROLLEY": ("250.00", "trip"),
    "BALER": ("40.00", "bale"),
    "WEEDER": ("1000.00", "hour"),
    "FERTILIZER_PUMP": ("500.00", "hour"),
    "PUMP": ("500.00", "hour"),
}


def upgrade() -> None:
    op.add_column(
        "vehicle_types",
        sa.Column("default_rate", sa.Numeric(14, 2), nullable=True),
    )
    op.add_column(
        "vehicle_types",
        sa.Column("default_rate_unit", sa.String(length=20), nullable=True),
    )
    op.create_check_constraint(
        "ck_vehicle_types_default_rate_non_negative",
        "vehicle_types",
        "default_rate IS NULL OR default_rate >= 0",
    )
    op.create_check_constraint(
        "ck_vehicle_types_default_rate_unit",
        "vehicle_types",
        "default_rate_unit IS NULL OR default_rate_unit IN ('hour','trip','bale')",
    )

    conn = op.get_bind()
    for code, (rate, unit) in _VEHICLE_RATES.items():
        conn.execute(
            sa.text(
                """
                UPDATE vehicle_types
                SET default_rate = :rate, default_rate_unit = :unit
                WHERE code = :code AND deleted_at IS NULL
                """
            ),
            {"code": code, "rate": rate, "unit": unit},
        )


def downgrade() -> None:
    op.drop_constraint("ck_vehicle_types_default_rate_unit", "vehicle_types", type_="check")
    op.drop_constraint("ck_vehicle_types_default_rate_non_negative", "vehicle_types", type_="check")
    op.drop_column("vehicle_types", "default_rate_unit")
    op.drop_column("vehicle_types", "default_rate")
