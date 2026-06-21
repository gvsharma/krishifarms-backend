from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.master_data.models import CropType, Village
from app.modules.master_data.schemas import (
    CropTypeCreateRequest,
    CropTypeUpdateRequest,
    VillageCreateRequest,
    VillageUpdateRequest,
)
from app.shared.services.audit import write_audit_log


def _soft_delete(entity, actor_user_id: UUID) -> None:
    entity.deleted_at = datetime.now(UTC)
    entity.updated_by = actor_user_id


def list_villages(db: Session, org_id: UUID, page: int, page_size: int) -> tuple[list[Village], int]:
    query = db.query(Village).filter(Village.org_id == org_id, Village.deleted_at.is_(None)).order_by(Village.name)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def create_village(db: Session, org_id: UUID, payload: VillageCreateRequest, actor_user_id: UUID) -> Village:
    existing = (
        db.query(Village)
        .filter(Village.org_id == org_id, Village.name == payload.name, Village.deleted_at.is_(None))
        .first()
    )
    if existing:
        raise ConflictError("Village already exists")

    village = Village(org_id=org_id, created_by=actor_user_id, updated_by=actor_user_id, **payload.model_dump())
    db.add(village)
    db.flush()
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="village",
        entity_id=village.id,
        after_state=payload.model_dump(),
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

    before = {"name": village.name, "district": village.district}
    for field, value in payload.model_dump(exclude_unset=True).items():
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
        after_state=payload.model_dump(exclude_unset=True),
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
