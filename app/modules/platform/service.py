from __future__ import annotations

from datetime import UTC, datetime
from typing import TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.client_context import ClientContext
from app.core.exceptions import ConflictError, NotFoundError
from app.modules.platform.models import (
    ActivityType,
    Buyer,
    CropPriceRule,
    EntityComment,
    EntityTag,
    FieldAgent,
    VehicleType,
)
from app.modules.platform.schemas import (
    ActivityTypeCreateRequest,
    ActivityTypeUpdateRequest,
    BuyerCreateRequest,
    BuyerUpdateRequest,
    CommentCreateRequest,
    CropPriceCreateRequest,
    CropPriceUpdateRequest,
    FieldAgentCreateRequest,
    FieldAgentUpdateRequest,
    TagCreateRequest,
    VehicleTypeCreateRequest,
    VehicleTypeUpdateRequest,
)
from app.modules.users.models import User
from app.shared.services.audit import write_activity_feed, write_audit_log

T = TypeVar("T")


def _soft_delete(entity, actor_user_id: UUID) -> None:
    entity.deleted_at = datetime.now(UTC)
    entity.updated_by = actor_user_id


def _user_names(db: Session, user_ids: set[UUID]) -> dict[UUID, str]:
    if not user_ids:
        return {}
    rows = db.query(User.id, User.full_name).filter(User.id.in_(user_ids)).all()
    return {row.id: row.full_name for row in rows}


def _audit(
    db: Session,
    *,
    org_id: UUID,
    actor_user_id: UUID,
    action: str,
    entity_type: str,
    entity_id: UUID,
    before: dict | None = None,
    after: dict | None = None,
    client: ClientContext | None = None,
    summary: str | None = None,
) -> None:
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_state=before,
        after_state=after,
        device_id=client.device_id if client else None,
        client_type=client.client_type if client else None,
        request_id=client.request_id if client else None,
    )
    if summary:
        write_activity_feed(
            db,
            org_id=org_id,
            actor_user_id=actor_user_id,
            summary=summary,
            entity_type=entity_type,
            entity_id=entity_id,
            device_id=client.device_id if client else None,
            client_type=client.client_type if client else None,
        )


def _paginate(query, page: int, page_size: int) -> tuple[list, int]:
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


# --- Activity types (services) ---


def list_activity_types(db: Session, org_id: UUID, page: int, page_size: int) -> tuple[list[ActivityType], int]:
    q = (
        db.query(ActivityType)
        .filter(ActivityType.org_id == org_id, ActivityType.deleted_at.is_(None))
        .order_by(ActivityType.name)
    )
    return _paginate(q, page, page_size)


def create_activity_type(
    db: Session, org_id: UUID, payload: ActivityTypeCreateRequest, actor_user_id: UUID, client: ClientContext | None
) -> ActivityType:
    if (
        db.query(ActivityType)
        .filter(ActivityType.org_id == org_id, ActivityType.code == payload.code, ActivityType.deleted_at.is_(None))
        .first()
    ):
        raise ConflictError("Activity type code already exists")
    row = ActivityType(org_id=org_id, created_by=actor_user_id, updated_by=actor_user_id, **payload.model_dump())
    db.add(row)
    db.flush()
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="activity_type",
        entity_id=row.id,
        after=payload.model_dump(mode="json"),
        client=client,
        summary=f"Service type created: {row.name}",
    )
    db.commit()
    db.refresh(row)
    return row


def update_activity_type(
    db: Session,
    org_id: UUID,
    row_id: UUID,
    payload: ActivityTypeUpdateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> ActivityType:
    row = (
        db.query(ActivityType)
        .filter(ActivityType.id == row_id, ActivityType.org_id == org_id, ActivityType.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Activity type not found")
    before = {"name": row.name, "is_active": row.is_active}
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_type="activity_type",
        entity_id=row.id,
        before=before,
        after=payload.model_dump(exclude_unset=True, mode="json"),
        client=client,
        summary=f"Service type updated: {row.name}",
    )
    db.commit()
    db.refresh(row)
    return row


def delete_activity_type(
    db: Session, org_id: UUID, row_id: UUID, actor_user_id: UUID, client: ClientContext | None
) -> None:
    row = (
        db.query(ActivityType)
        .filter(ActivityType.id == row_id, ActivityType.org_id == org_id, ActivityType.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Activity type not found")
    _soft_delete(row, actor_user_id)
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_type="activity_type",
        entity_id=row.id,
        client=client,
        summary=f"Service type deleted: {row.name}",
    )
    db.commit()


# --- Buyers ---


def list_buyers(db: Session, org_id: UUID, page: int, page_size: int) -> tuple[list[Buyer], int]:
    q = db.query(Buyer).filter(Buyer.org_id == org_id, Buyer.deleted_at.is_(None)).order_by(Buyer.name)
    return _paginate(q, page, page_size)


def create_buyer(
    db: Session, org_id: UUID, payload: BuyerCreateRequest, actor_user_id: UUID, client: ClientContext | None
) -> Buyer:
    row = Buyer(org_id=org_id, created_by=actor_user_id, updated_by=actor_user_id, **payload.model_dump())
    db.add(row)
    db.flush()
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="buyer",
        entity_id=row.id,
        after=payload.model_dump(mode="json"),
        client=client,
        summary=f"Buyer created: {row.name}",
    )
    db.commit()
    db.refresh(row)
    return row


def update_buyer(
    db: Session, org_id: UUID, row_id: UUID, payload: BuyerUpdateRequest, actor_user_id: UUID, client: ClientContext | None
) -> Buyer:
    row = db.query(Buyer).filter(Buyer.id == row_id, Buyer.org_id == org_id, Buyer.deleted_at.is_(None)).first()
    if row is None:
        raise NotFoundError("Buyer not found")
    before = {"name": row.name}
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_type="buyer",
        entity_id=row.id,
        before=before,
        after=payload.model_dump(exclude_unset=True, mode="json"),
        client=client,
        summary=f"Buyer updated: {row.name}",
    )
    db.commit()
    db.refresh(row)
    return row


def delete_buyer(db: Session, org_id: UUID, row_id: UUID, actor_user_id: UUID, client: ClientContext | None) -> None:
    row = db.query(Buyer).filter(Buyer.id == row_id, Buyer.org_id == org_id, Buyer.deleted_at.is_(None)).first()
    if row is None:
        raise NotFoundError("Buyer not found")
    _soft_delete(row, actor_user_id)
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_type="buyer",
        entity_id=row.id,
        client=client,
        summary=f"Buyer deleted: {row.name}",
    )
    db.commit()


# --- Field agents ---


def list_agents(db: Session, org_id: UUID, page: int, page_size: int) -> tuple[list[FieldAgent], int]:
    q = db.query(FieldAgent).filter(FieldAgent.org_id == org_id, FieldAgent.deleted_at.is_(None)).order_by(FieldAgent.name)
    return _paginate(q, page, page_size)


def create_agent(
    db: Session, org_id: UUID, payload: FieldAgentCreateRequest, actor_user_id: UUID, client: ClientContext | None
) -> FieldAgent:
    row = FieldAgent(org_id=org_id, created_by=actor_user_id, updated_by=actor_user_id, **payload.model_dump())
    db.add(row)
    db.flush()
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="field_agent",
        entity_id=row.id,
        after=payload.model_dump(mode="json"),
        client=client,
        summary=f"Agent created: {row.name}",
    )
    db.commit()
    db.refresh(row)
    return row


def update_agent(
    db: Session,
    org_id: UUID,
    row_id: UUID,
    payload: FieldAgentUpdateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> FieldAgent:
    row = (
        db.query(FieldAgent)
        .filter(FieldAgent.id == row_id, FieldAgent.org_id == org_id, FieldAgent.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Agent not found")
    before = {"name": row.name}
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_type="field_agent",
        entity_id=row.id,
        before=before,
        after=payload.model_dump(exclude_unset=True, mode="json"),
        client=client,
        summary=f"Agent updated: {row.name}",
    )
    db.commit()
    db.refresh(row)
    return row


def delete_agent(db: Session, org_id: UUID, row_id: UUID, actor_user_id: UUID, client: ClientContext | None) -> None:
    row = (
        db.query(FieldAgent)
        .filter(FieldAgent.id == row_id, FieldAgent.org_id == org_id, FieldAgent.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Agent not found")
    _soft_delete(row, actor_user_id)
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_type="field_agent",
        entity_id=row.id,
        client=client,
        summary=f"Agent deleted: {row.name}",
    )
    db.commit()


# --- Vehicle types ---


def list_vehicle_types(db: Session, org_id: UUID, page: int, page_size: int) -> tuple[list[VehicleType], int]:
    q = (
        db.query(VehicleType)
        .filter(VehicleType.org_id == org_id, VehicleType.deleted_at.is_(None))
        .order_by(VehicleType.name)
    )
    return _paginate(q, page, page_size)


def create_vehicle_type(
    db: Session, org_id: UUID, payload: VehicleTypeCreateRequest, actor_user_id: UUID, client: ClientContext | None
) -> VehicleType:
    if (
        db.query(VehicleType)
        .filter(VehicleType.org_id == org_id, VehicleType.code == payload.code, VehicleType.deleted_at.is_(None))
        .first()
    ):
        raise ConflictError("Vehicle type code already exists")
    row = VehicleType(org_id=org_id, created_by=actor_user_id, updated_by=actor_user_id, **payload.model_dump())
    db.add(row)
    db.flush()
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="vehicle_type",
        entity_id=row.id,
        after=payload.model_dump(mode="json"),
        client=client,
        summary=f"Vehicle type created: {row.name}",
    )
    db.commit()
    db.refresh(row)
    return row


def update_vehicle_type(
    db: Session,
    org_id: UUID,
    row_id: UUID,
    payload: VehicleTypeUpdateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> VehicleType:
    row = (
        db.query(VehicleType)
        .filter(VehicleType.id == row_id, VehicleType.org_id == org_id, VehicleType.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Vehicle type not found")
    before = {"name": row.name}
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_type="vehicle_type",
        entity_id=row.id,
        before=before,
        after=payload.model_dump(exclude_unset=True, mode="json"),
        client=client,
        summary=f"Vehicle type updated: {row.name}",
    )
    db.commit()
    db.refresh(row)
    return row


def delete_vehicle_type(
    db: Session, org_id: UUID, row_id: UUID, actor_user_id: UUID, client: ClientContext | None
) -> None:
    row = (
        db.query(VehicleType)
        .filter(VehicleType.id == row_id, VehicleType.org_id == org_id, VehicleType.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Vehicle type not found")
    _soft_delete(row, actor_user_id)
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_type="vehicle_type",
        entity_id=row.id,
        client=client,
        summary=f"Vehicle type deleted: {row.name}",
    )
    db.commit()


# --- Crop prices ---


def list_crop_prices(db: Session, org_id: UUID, page: int, page_size: int) -> tuple[list[CropPriceRule], int]:
    q = (
        db.query(CropPriceRule)
        .filter(CropPriceRule.org_id == org_id, CropPriceRule.deleted_at.is_(None))
        .order_by(CropPriceRule.effective_from.desc())
    )
    return _paginate(q, page, page_size)


def create_crop_price(
    db: Session, org_id: UUID, payload: CropPriceCreateRequest, actor_user_id: UUID, client: ClientContext | None
) -> CropPriceRule:
    row = CropPriceRule(org_id=org_id, created_by=actor_user_id, updated_by=actor_user_id, **payload.model_dump())
    db.add(row)
    db.flush()
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="crop_price_rule",
        entity_id=row.id,
        after=payload.model_dump(mode="json"),
        client=client,
        summary="Crop price rule created",
    )
    db.commit()
    db.refresh(row)
    return row


def update_crop_price(
    db: Session,
    org_id: UUID,
    row_id: UUID,
    payload: CropPriceUpdateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> CropPriceRule:
    row = (
        db.query(CropPriceRule)
        .filter(CropPriceRule.id == row_id, CropPriceRule.org_id == org_id, CropPriceRule.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Crop price rule not found")
    before = {"rate_per_quintal": str(row.rate_per_quintal)}
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, field, value)
    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_type="crop_price_rule",
        entity_id=row.id,
        before=before,
        after=payload.model_dump(exclude_unset=True, mode="json"),
        client=client,
        summary="Crop price rule updated",
    )
    db.commit()
    db.refresh(row)
    return row


def delete_crop_price(
    db: Session, org_id: UUID, row_id: UUID, actor_user_id: UUID, client: ClientContext | None
) -> None:
    row = (
        db.query(CropPriceRule)
        .filter(CropPriceRule.id == row_id, CropPriceRule.org_id == org_id, CropPriceRule.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Crop price rule not found")
    _soft_delete(row, actor_user_id)
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_type="crop_price_rule",
        entity_id=row.id,
        client=client,
        summary="Crop price rule deleted",
    )
    db.commit()


# --- Comments ---


def list_comments(
    db: Session,
    org_id: UUID,
    entity_type: str | None,
    entity_id: UUID | None,
    page: int,
    page_size: int,
) -> tuple[list[EntityComment], int, dict[UUID, str]]:
    q = db.query(EntityComment).filter(EntityComment.org_id == org_id, EntityComment.deleted_at.is_(None))
    if entity_type:
        q = q.filter(EntityComment.entity_type == entity_type)
    if entity_id:
        q = q.filter(EntityComment.entity_id == entity_id)
    q = q.order_by(EntityComment.created_at.desc())
    items, total = _paginate(q, page, page_size)
    names = _user_names(db, {c.author_user_id for c in items})
    return items, total, names


def create_comment(
    db: Session, org_id: UUID, payload: CommentCreateRequest, author_user_id: UUID, client: ClientContext
) -> EntityComment:
    row = EntityComment(
        org_id=org_id,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        body=payload.body,
        body_te=payload.body_te,
        author_user_id=author_user_id,
        device_id=client.device_id,
        client_type=client.client_type,
        created_at=datetime.now(UTC),
    )
    db.add(row)
    db.flush()
    _audit(
        db,
        org_id=org_id,
        actor_user_id=author_user_id,
        action="COMMENT",
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        after={"comment_id": str(row.id), "body": payload.body[:200]},
        client=client,
        summary=f"Comment on {payload.entity_type}",
    )
    db.commit()
    db.refresh(row)
    if payload.entity_type == "farmer":
        try:
            from app.modules.devices.service import notify_farmer_comment

            notify_farmer_comment(
                db,
                org_id=org_id,
                farmer_id=payload.entity_id,
                actor_user_id=author_user_id,
                preview=payload.body,
            )
        except Exception:
            pass
    return row


# --- Tags ---


def list_tags(
    db: Session, org_id: UUID, entity_type: str | None, entity_id: UUID | None
) -> tuple[list[EntityTag], dict[UUID, str]]:
    q = db.query(EntityTag).filter(EntityTag.org_id == org_id)
    if entity_type:
        q = q.filter(EntityTag.entity_type == entity_type)
    if entity_id:
        q = q.filter(EntityTag.entity_id == entity_id)
    items = q.order_by(EntityTag.tag).all()
    names = _user_names(db, {t.created_by for t in items if t.created_by})
    return items, names


def create_tag(
    db: Session, org_id: UUID, payload: TagCreateRequest, actor_user_id: UUID, client: ClientContext
) -> EntityTag:
    existing = (
        db.query(EntityTag)
        .filter(
            EntityTag.org_id == org_id,
            EntityTag.entity_type == payload.entity_type,
            EntityTag.entity_id == payload.entity_id,
            EntityTag.tag == payload.tag,
        )
        .first()
    )
    if existing:
        raise ConflictError("Tag already exists on this entity")
    row = EntityTag(
        org_id=org_id,
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        tag=payload.tag.strip().lower(),
        created_by=actor_user_id,
        device_id=client.device_id,
        created_at=datetime.now(UTC),
    )
    db.add(row)
    db.flush()
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="TAG",
        entity_type=payload.entity_type,
        entity_id=payload.entity_id,
        after={"tag": row.tag},
        client=client,
        summary=f"Tag added: {row.tag}",
    )
    db.commit()
    db.refresh(row)
    return row


def delete_tag(db: Session, org_id: UUID, tag_id: UUID, actor_user_id: UUID, client: ClientContext | None) -> None:
    row = db.query(EntityTag).filter(EntityTag.id == tag_id, EntityTag.org_id == org_id).first()
    if row is None:
        raise NotFoundError("Tag not found")
    tag_value = row.tag
    entity_type = row.entity_type
    entity_id = row.entity_id
    db.delete(row)
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UNTAG",
        entity_type=entity_type,
        entity_id=entity_id,
        before={"tag": tag_value},
        client=client,
        summary=f"Tag removed: {tag_value}",
    )
    db.commit()
