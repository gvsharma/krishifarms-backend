"""Shared money + date filter helpers for analytics services."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from app.modules.analytics.schemas import AnalyticsFilter

_ZERO = Decimal("0.00")
_MONEY_Q = Decimal("0.01")
_KG_Q = Decimal("0.001")

# Procurement statuses that contribute to revenue / confirmed volume.
CONFIRMED_PROCUREMENT_STATUSES = frozenset({"confirmed", "paid_partial", "paid_full"})
# Non-terminal statuses for "in progress" ops pulse.
OPEN_PROCUREMENT_STATUSES = frozenset(
    {"draft", "submitted", "weighment", "weighed", "priced", "confirmed", "paid_partial"}
)


def money(value: Decimal | int | float | None) -> Decimal:
    if value is None:
        return _ZERO
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(_MONEY_Q, rounding=ROUND_HALF_UP)


def kg(value: Decimal | int | float | None) -> Decimal:
    if value is None:
        return Decimal("0.000")
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(_KG_Q, rounding=ROUND_HALF_UP)


def resolve_date_range(filters: AnalyticsFilter, *, today: date | None = None) -> tuple[date, date]:
    """Resolve presets to inclusive [date_from, date_to]. Default: last 30 days."""
    today = today or date.today()
    preset = (filters.preset or "").lower().strip() if filters.preset else ""

    if filters.date_from and filters.date_to:
        return filters.date_from, filters.date_to

    if preset == "today":
        return today, today
    if preset == "7d":
        return today - timedelta(days=6), today
    if preset == "season":
        # Rough Kharif/Rabi heuristic for Telangana: if month >= 6 use Jun 1, else Dec 1 prior year.
        if today.month >= 6:
            return date(today.year, 6, 1), today
        return date(today.year - 1, 12, 1), today
    if preset == "30d" or not preset:
        if filters.date_from and not filters.date_to:
            return filters.date_from, today
        if filters.date_to and not filters.date_from:
            return filters.date_to - timedelta(days=29), filters.date_to
        return today - timedelta(days=29), today

    # custom without both dates → 30d
    return today - timedelta(days=29), today


def drill_query(
    path: str,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    village_id: UUID | None = None,
    crop_type_id: UUID | None = None,
    farmer_id: UUID | None = None,
    buyer_id: UUID | None = None,
) -> str:
    params: list[str] = []
    if date_from:
        params.append(f"date_from={date_from.isoformat()}")
    if date_to:
        params.append(f"date_to={date_to.isoformat()}")
    if village_id:
        params.append(f"village_id={village_id}")
    if crop_type_id:
        params.append(f"crop_type_id={crop_type_id}")
    if farmer_id:
        params.append(f"farmer_id={farmer_id}")
    if buyer_id:
        params.append(f"buyer_id={buyer_id}")
    if not params:
        return path
    return f"{path}?{'&'.join(params)}"
