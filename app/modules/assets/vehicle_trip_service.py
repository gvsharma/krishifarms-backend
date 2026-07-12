from __future__ import annotations

import re
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.assets.models import Asset
from app.modules.assets.vehicle_trip_models import VehicleTrip
from app.modules.assets.vehicle_trip_schemas import VehicleTripCreateRequest, VehicleTripUpdateRequest
from app.modules.financial.expense_service import find_expense_by_source, sync_vehicle_trip_diesel_expense
from app.modules.financial.schemas import VEHICLE_TRIP_SOURCE

_TRIP_PREFIX = "VT-"
_TWOPLACES = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(_TWOPLACES, rounding=ROUND_HALF_UP)


def _total_cost(
    fuel_cost: Decimal,
    loading: Decimal,
    unloading: Decimal,
    waiting: Decimal,
    other: Decimal,
) -> Decimal:
    return _money(fuel_cost + loading + unloading + waiting + other)


def _next_trip_number(db: Session, org_id: UUID) -> str:
    rows = (
        db.query(VehicleTrip.trip_number)
        .filter(VehicleTrip.org_id == org_id, VehicleTrip.trip_number.like(f"{_TRIP_PREFIX}%"))
        .all()
    )
    max_seq = 0
    for (code,) in rows:
        match = re.match(rf"^{re.escape(_TRIP_PREFIX)}(\d+)$", code or "")
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return f"{_TRIP_PREFIX}{max_seq + 1:04d}"


def _get_asset(db: Session, org_id: UUID, asset_id: UUID) -> Asset:
    row = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.org_id == org_id, Asset.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Asset not found")
    return row


def diesel_expense_id_for_trip(db: Session, org_id: UUID, trip_id: UUID) -> UUID | None:
    expense = find_expense_by_source(db, org_id, VEHICLE_TRIP_SOURCE, trip_id)
    return expense.id if expense else None


def list_trips(
    db: Session,
    org_id: UUID,
    *,
    page: int,
    page_size: int,
    asset_id: UUID | None = None,
    driver_worker_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[list[VehicleTrip], int]:
    q = db.query(VehicleTrip).filter(VehicleTrip.org_id == org_id)
    if asset_id:
        q = q.filter(VehicleTrip.asset_id == asset_id)
    if driver_worker_id:
        q = q.filter(VehicleTrip.driver_worker_id == driver_worker_id)
    if date_from:
        q = q.filter(VehicleTrip.trip_date >= date_from)
    if date_to:
        q = q.filter(VehicleTrip.trip_date <= date_to)
    total = q.count()
    items = (
        q.order_by(VehicleTrip.trip_date.desc(), VehicleTrip.trip_number.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_trip(db: Session, org_id: UUID, trip_id: UUID, trip_date: date) -> VehicleTrip:
    row = (
        db.query(VehicleTrip)
        .filter(
            VehicleTrip.id == trip_id,
            VehicleTrip.trip_date == trip_date,
            VehicleTrip.org_id == org_id,
        )
        .first()
    )
    if row is None:
        raise NotFoundError("Vehicle trip not found")
    return row


def create_trip(
    db: Session,
    org_id: UUID,
    payload: VehicleTripCreateRequest,
    actor_user_id: UUID,
) -> VehicleTrip:
    _get_asset(db, org_id, payload.asset_id)
    now = datetime.now(UTC)
    fuel_cost = _money(payload.fuel_cost)
    loading = _money(payload.loading_charges)
    unloading = _money(payload.unloading_charges)
    waiting = _money(payload.waiting_charges)
    other = _money(payload.other_charges)
    row = VehicleTrip(
        org_id=org_id,
        trip_number=_next_trip_number(db, org_id),
        asset_id=payload.asset_id,
        driver_worker_id=payload.driver_worker_id,
        source=payload.source,
        source_te=payload.source_te,
        destination=payload.destination,
        destination_te=payload.destination_te,
        trip_date=payload.trip_date,
        distance_km=payload.distance_km,
        fuel_liters=payload.fuel_liters,
        fuel_cost=fuel_cost,
        loading_charges=loading,
        unloading_charges=unloading,
        waiting_charges=waiting,
        other_charges=other,
        total_cost=_total_cost(fuel_cost, loading, unloading, waiting, other),
        status="completed",
        notes=payload.notes,
        created_by=actor_user_id,
        updated_by=actor_user_id,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.flush()
    sync_vehicle_trip_diesel_expense(
        db,
        org_id,
        trip_id=row.id,
        trip_number=row.trip_number,
        trip_date=row.trip_date,
        asset_id=row.asset_id,
        fuel_cost=row.fuel_cost,
        fuel_liters=row.fuel_liters,
        trip_status=row.status,
        actor_user_id=actor_user_id,
    )
    db.commit()
    db.refresh(row)
    return row


def update_trip(
    db: Session,
    org_id: UUID,
    trip_id: UUID,
    trip_date: date,
    payload: VehicleTripUpdateRequest,
    actor_user_id: UUID,
) -> VehicleTrip:
    row = get_trip(db, org_id, trip_id, trip_date)
    if row.status == "cancelled":
        raise ConflictError("Cancelled trips cannot be updated")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(row, field, value)

    row.fuel_cost = _money(row.fuel_cost)
    row.loading_charges = _money(row.loading_charges)
    row.unloading_charges = _money(row.unloading_charges)
    row.waiting_charges = _money(row.waiting_charges)
    row.other_charges = _money(row.other_charges)
    row.total_cost = _total_cost(
        row.fuel_cost,
        row.loading_charges,
        row.unloading_charges,
        row.waiting_charges,
        row.other_charges,
    )
    row.updated_by = actor_user_id
    row.updated_at = datetime.now(UTC)
    db.flush()
    sync_vehicle_trip_diesel_expense(
        db,
        org_id,
        trip_id=row.id,
        trip_number=row.trip_number,
        trip_date=row.trip_date,
        asset_id=row.asset_id,
        fuel_cost=row.fuel_cost,
        fuel_liters=row.fuel_liters,
        trip_status=row.status,
        actor_user_id=actor_user_id,
    )
    db.commit()
    db.refresh(row)
    return row
