from __future__ import annotations

from datetime import UTC, date, datetime
from re import sub
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.farmers.models import Farmer
from app.modules.farms.models import Farm, FarmActivity
from app.modules.farms.schemas import (
    FarmActivityCreateRequest,
    FarmActivityUpdateRequest,
    FarmCreateRequest,
    FarmUpdateRequest,
)
from app.modules.master_data.models import Village
from app.modules.platform.models import ActivityType


def _slug_code(name: str) -> str:
    cleaned = sub(r"[^A-Za-z0-9]+", "-", name.strip().upper()).strip("-")
    return (cleaned or "FARM")[:40]


def _unique_farm_code(db: Session, org_id: UUID, base: str) -> str:
    code = base
    n = 1
    while (
        db.query(Farm.id)
        .filter(Farm.org_id == org_id, Farm.farm_code == code, Farm.deleted_at.is_(None))
        .first()
    ):
        n += 1
        code = f"{base}-{n}"[:50]
    return code


def _validate_village(db: Session, org_id: UUID, village_id: UUID | None) -> None:
    if village_id is None:
        return
    row = (
        db.query(Village)
        .filter(Village.id == village_id, Village.org_id == org_id, Village.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Village not found")


def _validate_farmer(db: Session, org_id: UUID, farmer_id: UUID | None) -> None:
    if farmer_id is None:
        return
    row = (
        db.query(Farmer)
        .filter(Farmer.id == farmer_id, Farmer.org_id == org_id, Farmer.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Farmer not found")


def _validate_activity_type(db: Session, org_id: UUID, activity_type_id: UUID | None) -> None:
    if activity_type_id is None:
        return
    row = (
        db.query(ActivityType)
        .filter(
            ActivityType.id == activity_type_id,
            ActivityType.org_id == org_id,
            ActivityType.deleted_at.is_(None),
        )
        .first()
    )
    if row is None:
        raise NotFoundError("Activity type not found")


def _get_farm(db: Session, org_id: UUID, farm_id: UUID) -> Farm:
    row = (
        db.query(Farm)
        .filter(Farm.id == farm_id, Farm.org_id == org_id, Farm.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Farm not found")
    return row


def list_farms(
    db: Session,
    org_id: UUID,
    *,
    page: int,
    page_size: int,
    village_id: UUID | None = None,
    status: str | None = None,
    q: str | None = None,
) -> tuple[list[Farm], int]:
    query = db.query(Farm).filter(Farm.org_id == org_id, Farm.deleted_at.is_(None))
    if village_id:
        query = query.filter(Farm.village_id == village_id)
    if status:
        query = query.filter(Farm.status == status)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter((Farm.name.ilike(like)) | (Farm.farm_code.ilike(like)))
    total = query.count()
    items = query.order_by(Farm.name).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_farm(db: Session, org_id: UUID, farm_id: UUID) -> Farm:
    return _get_farm(db, org_id, farm_id)


def create_farm(
    db: Session,
    org_id: UUID,
    payload: FarmCreateRequest,
    actor_user_id: UUID,
) -> Farm:
    _validate_village(db, org_id, payload.village_id)
    _validate_farmer(db, org_id, payload.owner_farmer_id)
    if (
        payload.lease_end_date
        and payload.lease_start_date
        and payload.lease_end_date < payload.lease_start_date
    ):
        raise ConflictError("lease_end_date must be on or after lease_start_date")

    code = payload.farm_code or _unique_farm_code(db, org_id, _slug_code(payload.name))
    if (
        db.query(Farm.id)
        .filter(Farm.org_id == org_id, Farm.farm_code == code, Farm.deleted_at.is_(None))
        .first()
    ):
        raise ConflictError("Farm code already exists")

    row = Farm(
        org_id=org_id,
        farm_code=code,
        name=payload.name,
        name_te=payload.name_te,
        acres=payload.acres,
        location=payload.location,
        village_id=payload.village_id,
        owner_farmer_id=payload.owner_farmer_id,
        lease_start_date=payload.lease_start_date,
        lease_end_date=payload.lease_end_date,
        lease_amount=payload.lease_amount,
        lease_notes=payload.lease_notes,
        status="active",
        geo_lat=payload.geo_lat,
        geo_lng=payload.geo_lng,
        created_by=actor_user_id,
        updated_by=actor_user_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_farm(
    db: Session,
    org_id: UUID,
    farm_id: UUID,
    payload: FarmUpdateRequest,
    actor_user_id: UUID,
) -> Farm:
    row = _get_farm(db, org_id, farm_id)
    data = payload.model_dump(exclude_unset=True)
    if "village_id" in data:
        _validate_village(db, org_id, data["village_id"])
    if "owner_farmer_id" in data:
        _validate_farmer(db, org_id, data["owner_farmer_id"])

    for field, value in data.items():
        setattr(row, field, value)

    start = row.lease_start_date
    end = row.lease_end_date
    if start and end and end < start:
        raise ConflictError("lease_end_date must be on or after lease_start_date")

    row.updated_by = actor_user_id
    db.commit()
    db.refresh(row)
    return row


def delete_farm(db: Session, org_id: UUID, farm_id: UUID, actor_user_id: UUID) -> None:
    row = _get_farm(db, org_id, farm_id)
    row.deleted_at = datetime.now(UTC)
    row.updated_by = actor_user_id
    db.commit()


def list_activities(
    db: Session,
    org_id: UUID,
    farm_id: UUID,
    *,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[list[FarmActivity], int]:
    _get_farm(db, org_id, farm_id)
    q = db.query(FarmActivity).filter(
        FarmActivity.org_id == org_id,
        FarmActivity.farm_id == farm_id,
        FarmActivity.deleted_at.is_(None),
    )
    if date_from:
        q = q.filter(FarmActivity.activity_date >= date_from)
    if date_to:
        q = q.filter(FarmActivity.activity_date <= date_to)
    total = q.count()
    items = q.order_by(FarmActivity.activity_date.desc()).all()
    return items, total


def create_activity(
    db: Session,
    org_id: UUID,
    farm_id: UUID,
    payload: FarmActivityCreateRequest,
    actor_user_id: UUID,
) -> FarmActivity:
    _get_farm(db, org_id, farm_id)
    _validate_activity_type(db, org_id, payload.activity_type_id)
    row = FarmActivity(
        org_id=org_id,
        farm_id=farm_id,
        activity_type_id=payload.activity_type_id,
        activity_date=payload.activity_date,
        description=payload.description,
        description_te=payload.description_te,
        performed_by_worker_id=payload.performed_by_worker_id,
        created_by=actor_user_id,
        updated_by=actor_user_id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def update_activity(
    db: Session,
    org_id: UUID,
    farm_id: UUID,
    activity_id: UUID,
    payload: FarmActivityUpdateRequest,
    actor_user_id: UUID,
) -> FarmActivity:
    _get_farm(db, org_id, farm_id)
    row = (
        db.query(FarmActivity)
        .filter(
            FarmActivity.id == activity_id,
            FarmActivity.farm_id == farm_id,
            FarmActivity.org_id == org_id,
            FarmActivity.deleted_at.is_(None),
        )
        .first()
    )
    if row is None:
        raise NotFoundError("Farm activity not found")
    data = payload.model_dump(exclude_unset=True)
    if "activity_type_id" in data:
        _validate_activity_type(db, org_id, data["activity_type_id"])
    for field, value in data.items():
        setattr(row, field, value)
    row.updated_by = actor_user_id
    db.commit()
    db.refresh(row)
    return row


def delete_activity(
    db: Session,
    org_id: UUID,
    farm_id: UUID,
    activity_id: UUID,
    actor_user_id: UUID,
) -> None:
    _get_farm(db, org_id, farm_id)
    row = (
        db.query(FarmActivity)
        .filter(
            FarmActivity.id == activity_id,
            FarmActivity.farm_id == farm_id,
            FarmActivity.org_id == org_id,
            FarmActivity.deleted_at.is_(None),
        )
        .first()
    )
    if row is None:
        raise NotFoundError("Farm activity not found")
    row.deleted_at = datetime.now(UTC)
    row.updated_by = actor_user_id
    db.commit()
