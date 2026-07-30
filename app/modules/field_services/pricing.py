"""Compute field-service charges from vehicle-type default rates."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from app.modules.platform.models import VehicleType
from app.shared.work_details import VehicleWorkDetails, bale_count_from_work_details, trips_from_work_details

_ZERO = Decimal("0")
_TWOPLACES = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(_TWOPLACES, rounding=ROUND_HALF_UP)


def compute_vehicle_charge(
    vehicle_type: VehicleType | None,
    *,
    hours: Decimal | None,
    work_details: VehicleWorkDetails | None = None,
    bag_count: int | None = None,
) -> tuple[Decimal | None, Decimal | None]:
    """Return (rate_per_unit, total_amount) when a default rate applies."""
    if vehicle_type is None or vehicle_type.default_rate is None or not vehicle_type.default_rate_unit:
        return None, None

    rate = _money(Decimal(str(vehicle_type.default_rate)))
    unit = vehicle_type.default_rate_unit

    if unit == "hour":
        if hours is None or hours <= 0:
            return rate, None
        return rate, _money(rate * hours)

    if unit == "trip":
        trips = bag_count if bag_count and bag_count > 0 else trips_from_work_details(work_details)
        if not trips or trips <= 0:
            return rate, None
        return rate, _money(rate * Decimal(trips))

    if unit == "bale":
        bales = bale_count_from_work_details(work_details)
        if not bales or bales <= 0:
            return rate, None
        return rate, _money(rate * Decimal(bales))

    return None, None
