from datetime import UTC, datetime
import re
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.master_data.models import CropType, District, Mandal, Village
from app.modules.master_data.schemas import (
    CropTypeCreateRequest,
    CropTypeUpdateRequest,
    DistrictCreateRequest,
    DistrictUpdateRequest,
    MandalCreateRequest,
    MandalUpdateRequest,
    VillageCreateRequest,
    VillageUpdateRequest,
)
from app.modules.platform.models import FieldAgent
from app.shared.services.audit import write_audit_log

_VILLAGE_CODE_PREFIX = "VIL-"


def _soft_delete(entity, actor_user_id: UUID) -> None:
    entity.deleted_at = datetime.now(UTC)
    entity.updated_by = actor_user_id


def _get_district(db: Session, org_id: UUID, district_id: UUID) -> District:
    district = (
        db.query(District)
        .filter(District.id == district_id, District.org_id == org_id, District.deleted_at.is_(None))
        .first()
    )
    if district is None:
        raise NotFoundError("District not found")
    return district


def _get_mandal(db: Session, org_id: UUID, mandal_id: UUID) -> Mandal:
    mandal = (
        db.query(Mandal)
        .filter(Mandal.id == mandal_id, Mandal.org_id == org_id, Mandal.deleted_at.is_(None))
        .first()
    )
    if mandal is None:
        raise NotFoundError("Mandal not found")
    return mandal


def _resolve_location_fks(
    db: Session,
    org_id: UUID,
    *,
    district_id: UUID | None,
    mandal_id: UUID | None,
    district: str | None,
    mandal: str | None,
) -> tuple[UUID | None, UUID | None, str | None, str | None]:
    """Prefer explicit FKs; sync denormalized name strings for dropdown clients."""
    resolved_district_id = district_id
    resolved_mandal_id = mandal_id
    resolved_district = district
    resolved_mandal = mandal

    if resolved_mandal_id is not None:
        m = _get_mandal(db, org_id, resolved_mandal_id)
        resolved_mandal = m.name
        resolved_district_id = m.district_id
        d = _get_district(db, org_id, m.district_id)
        resolved_district = d.name
    elif resolved_district_id is not None:
        d = _get_district(db, org_id, resolved_district_id)
        resolved_district = d.name

    return resolved_district_id, resolved_mandal_id, resolved_district, resolved_mandal


def list_districts(
    db: Session,
    org_id: UUID,
    page: int,
    page_size: int,
    *,
    q: str | None = None,
) -> tuple[list[District], int]:
    query = db.query(District).filter(District.org_id == org_id, District.deleted_at.is_(None))
    if q:
        query = query.filter(District.name.ilike(f"%{q.strip()}%"))
    query = query.order_by(District.name)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def create_district(
    db: Session, org_id: UUID, payload: DistrictCreateRequest, actor_user_id: UUID
) -> District:
    existing = (
        db.query(District)
        .filter(District.org_id == org_id, District.name == payload.name, District.deleted_at.is_(None))
        .first()
    )
    if existing:
        raise ConflictError("District already exists")

    district = District(
        org_id=org_id, created_by=actor_user_id, updated_by=actor_user_id, **payload.model_dump()
    )
    db.add(district)
    db.flush()
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="district",
        entity_id=district.id,
        after_state=payload.model_dump(),
    )
    db.commit()
    db.refresh(district)
    return district


def update_district(
    db: Session, org_id: UUID, district_id: UUID, payload: DistrictUpdateRequest, actor_user_id: UUID
) -> District:
    district = _get_district(db, org_id, district_id)
    before = {"name": district.name, "state": district.state}
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(district, field, value)
    district.updated_by = actor_user_id
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_type="district",
        entity_id=district.id,
        before_state=before,
        after_state=payload.model_dump(exclude_unset=True),
    )
    db.commit()
    db.refresh(district)
    return district


def delete_district(db: Session, org_id: UUID, district_id: UUID, actor_user_id: UUID) -> None:
    district = _get_district(db, org_id, district_id)
    _soft_delete(district, actor_user_id)
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_type="district",
        entity_id=district.id,
    )
    db.commit()


def list_mandals(
    db: Session,
    org_id: UUID,
    page: int,
    page_size: int,
    *,
    district_id: UUID | None = None,
    district: str | None = None,
    q: str | None = None,
) -> tuple[list[Mandal], int]:
    query = db.query(Mandal).filter(Mandal.org_id == org_id, Mandal.deleted_at.is_(None))
    if district_id is not None:
        query = query.filter(Mandal.district_id == district_id)
    if district:
        query = query.join(District, District.id == Mandal.district_id).filter(
            District.org_id == org_id,
            District.deleted_at.is_(None),
            District.name.ilike(district.strip()),
        )
    if q:
        query = query.filter(Mandal.name.ilike(f"%{q.strip()}%"))
    query = query.order_by(Mandal.name)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def create_mandal(db: Session, org_id: UUID, payload: MandalCreateRequest, actor_user_id: UUID) -> Mandal:
    _get_district(db, org_id, payload.district_id)
    existing = (
        db.query(Mandal)
        .filter(
            Mandal.org_id == org_id,
            Mandal.district_id == payload.district_id,
            Mandal.name == payload.name,
            Mandal.deleted_at.is_(None),
        )
        .first()
    )
    if existing:
        raise ConflictError("Mandal already exists in this district")

    mandal = Mandal(
        org_id=org_id, created_by=actor_user_id, updated_by=actor_user_id, **payload.model_dump()
    )
    db.add(mandal)
    db.flush()
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="mandal",
        entity_id=mandal.id,
        after_state=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(mandal)
    return mandal


def update_mandal(
    db: Session, org_id: UUID, mandal_id: UUID, payload: MandalUpdateRequest, actor_user_id: UUID
) -> Mandal:
    mandal = _get_mandal(db, org_id, mandal_id)
    data = payload.model_dump(exclude_unset=True)
    if "district_id" in data and data["district_id"] is not None:
        _get_district(db, org_id, data["district_id"])
    before = {"name": mandal.name, "district_id": str(mandal.district_id)}
    for field, value in data.items():
        setattr(mandal, field, value)
    mandal.updated_by = actor_user_id
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_type="mandal",
        entity_id=mandal.id,
        before_state=before,
        after_state={k: (str(v) if isinstance(v, UUID) else v) for k, v in data.items()},
    )
    db.commit()
    db.refresh(mandal)
    return mandal


def delete_mandal(db: Session, org_id: UUID, mandal_id: UUID, actor_user_id: UUID) -> None:
    mandal = _get_mandal(db, org_id, mandal_id)
    _soft_delete(mandal, actor_user_id)
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_type="mandal",
        entity_id=mandal.id,
    )
    db.commit()


def list_villages(
    db: Session,
    org_id: UUID,
    page: int,
    page_size: int,
    *,
    district_id: UUID | None = None,
    mandal_id: UUID | None = None,
    district: str | None = None,
    mandal: str | None = None,
    status: str | None = None,
    q: str | None = None,
) -> tuple[list[Village], int]:
    query = db.query(Village).filter(Village.org_id == org_id, Village.deleted_at.is_(None))
    if district_id is not None:
        query = query.filter(Village.district_id == district_id)
    if mandal_id is not None:
        query = query.filter(Village.mandal_id == mandal_id)
    if district:
        query = query.filter(Village.district.ilike(district.strip()))
    if mandal:
        query = query.filter(Village.mandal.ilike(mandal.strip()))
    if status:
        query = query.filter(Village.status == status)
    if q:
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Village.name.ilike(term),
                Village.name_te.ilike(term),
                Village.village_code.ilike(term),
                Village.mandal.ilike(term),
                Village.district.ilike(term),
                Village.pincode.ilike(term),
            )
        )
    query = query.order_by(Village.name)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_village(db: Session, org_id: UUID, village_id: UUID) -> Village:
    village = (
        db.query(Village)
        .filter(Village.id == village_id, Village.org_id == org_id, Village.deleted_at.is_(None))
        .first()
    )
    if village is None:
        raise NotFoundError("Village not found")
    return village


def _next_village_code(db: Session, org_id: UUID) -> str:
    rows = (
        db.query(Village.village_code)
        .filter(Village.org_id == org_id, Village.village_code.like(f"{_VILLAGE_CODE_PREFIX}%"))
        .all()
    )
    max_seq = 0
    for (code,) in rows:
        match = re.match(rf"^{re.escape(_VILLAGE_CODE_PREFIX)}(\d+)$", code or "")
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return f"{_VILLAGE_CODE_PREFIX}{max_seq + 1:04d}"


def agent_name_map(db: Session, villages: list[Village]) -> dict[UUID, str]:
    ids = {v.agent_id for v in villages if v.agent_id}
    if not ids:
        return {}
    rows = db.query(FieldAgent.id, FieldAgent.name).filter(FieldAgent.id.in_(ids)).all()
    return {row.id: row.name for row in rows}


def create_village(db: Session, org_id: UUID, payload: VillageCreateRequest, actor_user_id: UUID) -> Village:
    district_id, mandal_id, district, mandal = _resolve_location_fks(
        db,
        org_id,
        district_id=payload.district_id,
        mandal_id=payload.mandal_id,
        district=payload.district,
        mandal=payload.mandal,
    )
    existing = (
        db.query(Village)
        .filter(
            Village.org_id == org_id,
            Village.name == payload.name,
            Village.mandal == mandal,
            Village.deleted_at.is_(None),
        )
        .first()
    )
    if existing:
        raise ConflictError("Village already exists")

    if payload.agent_id is not None:
        agent = (
            db.query(FieldAgent)
            .filter(
                FieldAgent.id == payload.agent_id,
                FieldAgent.org_id == org_id,
                FieldAgent.deleted_at.is_(None),
            )
            .first()
        )
        if agent is None:
            raise NotFoundError("Field agent not found")

    village = Village(
        org_id=org_id,
        created_by=actor_user_id,
        updated_by=actor_user_id,
        village_code=_next_village_code(db, org_id),
        name=payload.name,
        mandal=mandal,
        district=district,
        state=payload.state,
        pincode=payload.pincode,
        district_id=district_id,
        mandal_id=mandal_id,
        geo_lat=payload.geo_lat,
        geo_lng=payload.geo_lng,
        agent_id=payload.agent_id,
        status=payload.status or "active",
        population=payload.population,
        estimated_cultivable_area=payload.estimated_cultivable_area,
        notes=payload.notes,
    )
    db.add(village)
    db.flush()
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="village",
        entity_id=village.id,
        after_state=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(village)
    return village


def update_village(
    db: Session, org_id: UUID, village_id: UUID, payload: VillageUpdateRequest, actor_user_id: UUID
) -> Village:
    village = (
        db.query(Village)
        .filter(Village.id == village_id, Village.org_id == org_id, Village.deleted_at.is_(None))
        .first()
    )
    if village is None:
        raise NotFoundError("Village not found")

    data = payload.model_dump(exclude_unset=True)
    district_id = data.get("district_id", village.district_id)
    mandal_id = data.get("mandal_id", village.mandal_id)
    district = data.get("district", village.district)
    mandal = data.get("mandal", village.mandal)
    if any(k in data for k in ("district_id", "mandal_id", "district", "mandal")):
        district_id, mandal_id, district, mandal = _resolve_location_fks(
            db,
            org_id,
            district_id=district_id,
            mandal_id=mandal_id,
            district=district,
            mandal=mandal,
        )
        data["district_id"] = district_id
        data["mandal_id"] = mandal_id
        data["district"] = district
        data["mandal"] = mandal

    if "agent_id" in data and data["agent_id"] is not None:
        agent = (
            db.query(FieldAgent)
            .filter(
                FieldAgent.id == data["agent_id"],
                FieldAgent.org_id == org_id,
                FieldAgent.deleted_at.is_(None),
            )
            .first()
        )
        if agent is None:
            raise NotFoundError("Field agent not found")

    before = {"name": village.name, "district": village.district, "mandal": village.mandal}
    for field, value in data.items():
        setattr(village, field, value)
    village.updated_by = actor_user_id
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_type="village",
        entity_id=village.id,
        before_state=before,
        after_state={k: (str(v) if isinstance(v, UUID) else v) for k, v in data.items()},
    )
    db.commit()
    db.refresh(village)
    return village


def delete_village(db: Session, org_id: UUID, village_id: UUID, actor_user_id: UUID) -> None:
    village = (
        db.query(Village)
        .filter(Village.id == village_id, Village.org_id == org_id, Village.deleted_at.is_(None))
        .first()
    )
    if village is None:
        raise NotFoundError("Village not found")
    _soft_delete(village, actor_user_id)
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_type="village",
        entity_id=village.id,
    )
    db.commit()


def list_crop_types(db: Session, org_id: UUID, page: int, page_size: int) -> tuple[list[CropType], int]:
    query = (
        db.query(CropType)
        .filter(CropType.org_id == org_id, CropType.deleted_at.is_(None))
        .order_by(CropType.name)
    )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def create_crop_type(
    db: Session, org_id: UUID, payload: CropTypeCreateRequest, actor_user_id: UUID
) -> CropType:
    existing = (
        db.query(CropType)
        .filter(CropType.org_id == org_id, CropType.code == payload.code, CropType.deleted_at.is_(None))
        .first()
    )
    if existing:
        raise ConflictError("Crop type code already exists")

    crop_type = CropType(
        org_id=org_id, created_by=actor_user_id, updated_by=actor_user_id, **payload.model_dump()
    )
    db.add(crop_type)
    db.flush()
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="crop_type",
        entity_id=crop_type.id,
        after_state=payload.model_dump(),
    )
    db.commit()
    db.refresh(crop_type)
    return crop_type


def update_crop_type(
    db: Session, org_id: UUID, crop_type_id: UUID, payload: CropTypeUpdateRequest, actor_user_id: UUID
) -> CropType:
    crop_type = (
        db.query(CropType)
        .filter(CropType.id == crop_type_id, CropType.org_id == org_id, CropType.deleted_at.is_(None))
        .first()
    )
    if crop_type is None:
        raise NotFoundError("Crop type not found")

    before = {"name": crop_type.name, "code": crop_type.code, "is_active": crop_type.is_active}
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(crop_type, field, value)
    crop_type.updated_by = actor_user_id
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_type="crop_type",
        entity_id=crop_type.id,
        before_state=before,
        after_state=payload.model_dump(exclude_unset=True),
    )
    db.commit()
    db.refresh(crop_type)
    return crop_type


def delete_crop_type(db: Session, org_id: UUID, crop_type_id: UUID, actor_user_id: UUID) -> None:
    crop_type = (
        db.query(CropType)
        .filter(CropType.id == crop_type_id, CropType.org_id == org_id, CropType.deleted_at.is_(None))
        .first()
    )
    if crop_type is None:
        raise NotFoundError("Crop type not found")
    _soft_delete(crop_type, actor_user_id)
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_type="crop_type",
        entity_id=crop_type.id,
    )
    db.commit()
