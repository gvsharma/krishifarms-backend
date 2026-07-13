"""Farmer 360° profile fields: prefs, trust, GPS, land/crop extensions."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "202506210030"
down_revision: Union[str, None] = "202506210029"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- farmers summary / relationship prefs (all optional) ---
    op.add_column("farmers", sa.Column("preferred_language", sa.String(length=10), nullable=True))
    op.add_column("farmers", sa.Column("preferred_payment_cycle", sa.String(length=50), nullable=True))
    op.add_column("farmers", sa.Column("preferred_payment_method", sa.String(length=50), nullable=True))
    op.add_column("farmers", sa.Column("trust_rating", sa.SmallInteger(), nullable=True))
    op.add_column("farmers", sa.Column("is_vip", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("farmers", sa.Column("geo_lat", sa.Numeric(10, 7), nullable=True))
    op.add_column("farmers", sa.Column("geo_lng", sa.Numeric(10, 7), nullable=True))
    op.create_check_constraint(
        "ck_farmers_trust_rating",
        "farmers",
        "trust_rating IS NULL OR (trust_rating >= 1 AND trust_rating <= 5)",
    )

    # --- land parcel agriculture details (all optional) ---
    op.add_column("farmer_land_parcels", sa.Column("ownership", sa.String(length=20), nullable=True))
    op.add_column("farmer_land_parcels", sa.Column("irrigation_type", sa.String(length=50), nullable=True))
    op.add_column("farmer_land_parcels", sa.Column("water_source", sa.String(length=50), nullable=True))
    op.add_column("farmer_land_parcels", sa.Column("soil_type", sa.String(length=50), nullable=True))
    op.add_column("farmer_land_parcels", sa.Column("village_name", sa.String(length=200), nullable=True))
    op.create_check_constraint(
        "ck_farmer_land_parcels_ownership",
        "farmer_land_parcels",
        "ownership IS NULL OR ownership IN ('owned','lease','shared')",
    )

    # --- crop history farming detail (all optional) ---
    op.add_column("farmer_crop_history", sa.Column("survey_number", sa.String(length=100), nullable=True))
    op.add_column("farmer_crop_history", sa.Column("village_name", sa.String(length=200), nullable=True))
    op.add_column("farmer_crop_history", sa.Column("seed_variety", sa.String(length=100), nullable=True))
    op.add_column("farmer_crop_history", sa.Column("seed_supplier", sa.String(length=200), nullable=True))
    op.add_column("farmer_crop_history", sa.Column("fertilizer_supplier", sa.String(length=200), nullable=True))
    op.add_column("farmer_crop_history", sa.Column("pesticides_used", sa.Text(), nullable=True))
    op.add_column("farmer_crop_history", sa.Column("cultivation_stage", sa.String(length=50), nullable=True))
    op.add_column("farmer_crop_history", sa.Column("expected_yield", sa.Numeric(12, 3), nullable=True))
    op.add_column("farmer_crop_history", sa.Column("actual_yield", sa.Numeric(12, 3), nullable=True))
    op.add_column("farmer_crop_history", sa.Column("selling_market", sa.String(length=200), nullable=True))
    op.add_column("farmer_crop_history", sa.Column("selling_price", sa.Numeric(14, 2), nullable=True))
    op.add_column("farmer_crop_history", sa.Column("harvest_date", sa.Date(), nullable=True))
    op.add_column("farmer_crop_history", sa.Column("geo_lat", sa.Numeric(10, 7), nullable=True))
    op.add_column("farmer_crop_history", sa.Column("geo_lng", sa.Numeric(10, 7), nullable=True))


def downgrade() -> None:
    for col in (
        "geo_lng",
        "geo_lat",
        "harvest_date",
        "selling_price",
        "selling_market",
        "actual_yield",
        "expected_yield",
        "cultivation_stage",
        "pesticides_used",
        "fertilizer_supplier",
        "seed_supplier",
        "seed_variety",
        "village_name",
        "survey_number",
    ):
        op.drop_column("farmer_crop_history", col)

    op.drop_constraint("ck_farmer_land_parcels_ownership", "farmer_land_parcels", type_="check")
    for col in ("village_name", "soil_type", "water_source", "irrigation_type", "ownership"):
        op.drop_column("farmer_land_parcels", col)

    op.drop_constraint("ck_farmers_trust_rating", "farmers", type_="check")
    for col in (
        "geo_lng",
        "geo_lat",
        "is_vip",
        "trust_rating",
        "preferred_payment_method",
        "preferred_payment_cycle",
        "preferred_language",
    ):
        op.drop_column("farmers", col)
