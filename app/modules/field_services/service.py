from __future__ import annotations

import re
from datetime import UTC, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.client_context import ClientContext
from app.core.exceptions import NotFoundError
from app.modules.farmers.models import Farmer
from app.modules.field_services.models import FieldServiceRecord, SERVICE_CATEGORIES
from app.modules.field_services.schemas import (
    FieldServiceRecordCreateRequest,
    FieldServiceRecordUpdateRequest,
)
from app.modules.financial.expense_service import find_expense_by_source, sync_field_service_diesel_expense
from app.modules.financial.schemas import FIELD_SERVICE_SOURCE
from app.modules.platform.models import ActivityType, VehicleType
from app.shared.services.audit import write_activity_feed, write_audit_log

_RECORD_PREFIX = "FSR-"
_ZERO = Decimal("0")
_TWOPLACES = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(_TWOPLACES, rounding=ROUND_HALF_UP)


def _next_record_number(db: Session, org_id: UUID) -> str:
    rows = (
        db.query(FieldServiceRecord.record_number)
        .filter(
            FieldServiceRecord.org_id == org_id,
            FieldServiceRecord.record_number.like(f"{_RECORD_PREFIX}%"),
        )
        .all()
    )
    max_seq = 0
    for (code,) in rows:
        match = re.match(rf"^{re.escape(_RECORD_PREFIX)}(\d+)$", code or "")
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return f"{_RECORD_PREFIX}{max_seq + 1:04d}"


def _audit(
    db: Session,
    *,
    org_id: UUID,
    actor_user_id: UUID,
    action: str,
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
        entity_type="field_service_record",
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
            entity_type="field_service_record",
            entity_id=entity_id,
            summary=summary,
            device_id=client.device_id if client else None,
            client_type=client.client_type if client else None,
        )


def _validate_refs(
    db: Session,
    org_id: UUID,
    *,
    service_category: str,
    activity_type_id: UUID | None,
    farmer_id: UUID | None,
    vehicle_type_id: UUID | None,
) -> None:
    if service_category not in SERVICE_CATEGORIES:
        raise NotFoundError("Invalid service category")
    if activity_type_id:
        row = (
            db.query(ActivityType)
            .filter(
                ActivityType.id == activity_type_id,
                ActivityType.org_id == org_id,
                ActivityType.deleted_at.is_(None),
            )
            .first()
        )
        if not row:
            raise NotFoundError("Activity type not found")
    if farmer_id:
        row = (
            db.query(Farmer)
            .filter(Farmer.id == farmer_id, Farmer.org_id == org_id, Farmer.deleted_at.is_(None))
            .first()
        )
        if not row:
            raise NotFoundError("Farmer not found")
    if vehicle_type_id:
        row = (
            db.query(VehicleType)
            .filter(
                VehicleType.id == vehicle_type_id,
                VehicleType.org_id == org_id,
                VehicleType.deleted_at.is_(None),
            )
            .first()
        )
        if not row:
            raise NotFoundError("Vehicle type not found")


def _soft_delete(entity: FieldServiceRecord, actor_user_id: UUID) -> None:
    entity.deleted_at = datetime.now(UTC)
    entity.updated_by = actor_user_id


def _serialize(row: FieldServiceRecord) -> dict:
    return {
        "record_number": row.record_number,
        "service_category": row.service_category,
        "activity_type_id": str(row.activity_type_id) if row.activity_type_id else None,
        "farmer_id": str(row.farmer_id) if row.farmer_id else None,
        "service_date": row.service_date.isoformat(),
        "status": row.status,
        "total_amount": str(row.total_amount),
        "pending_amount": str(row.pending_amount),
    }


def list_field_service_records(
    db: Session,
    org_id: UUID,
    *,
    page: int,
    page_size: int,
    service_category: str | None = None,
    farmer_id: UUID | None = None,
    status: str | None = None,
    date_from=None,
    date_to=None,
) -> tuple[list[FieldServiceRecord], int]:
    query = db.query(FieldServiceRecord).filter(
        FieldServiceRecord.org_id == org_id,
        FieldServiceRecord.deleted_at.is_(None),
    )
    if service_category:
        query = query.filter(FieldServiceRecord.service_category == service_category)
    if farmer_id:
        query = query.filter(FieldServiceRecord.farmer_id == farmer_id)
    if status:
        query = query.filter(FieldServiceRecord.status == status)
    if date_from:
        query = query.filter(FieldServiceRecord.service_date >= date_from)
    if date_to:
        query = query.filter(FieldServiceRecord.service_date <= date_to)

    total = query.count()
    items = (
        query.order_by(FieldServiceRecord.service_date.desc(), FieldServiceRecord.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_field_service_record(db: Session, org_id: UUID, record_id: UUID) -> FieldServiceRecord:
    row = (
        db.query(FieldServiceRecord)
        .filter(
            FieldServiceRecord.id == record_id,
            FieldServiceRecord.org_id == org_id,
            FieldServiceRecord.deleted_at.is_(None),
        )
        .first()
    )
    if not row:
        raise NotFoundError("Field service record not found")
    return row


def create_field_service_record(
    db: Session,
    org_id: UUID,
    payload: FieldServiceRecordCreateRequest,
    actor_user_id: UUID,
    client: ClientContext | None = None,
) -> FieldServiceRecord:
    _validate_refs(
        db,
        org_id,
        service_category=payload.service_category,
        activity_type_id=payload.activity_type_id,
        farmer_id=payload.farmer_id,
        vehicle_type_id=payload.vehicle_type_id,
    )
    row = FieldServiceRecord(
        org_id=org_id,
        record_number=_next_record_number(db, org_id),
        service_category=payload.service_category,
        activity_type_id=payload.activity_type_id,
        farmer_id=payload.farmer_id,
        asset_id=payload.asset_id,
        vehicle_type_id=payload.vehicle_type_id,
        service_date=payload.service_date,
        location=payload.location,
        location_te=payload.location_te,
        hours=payload.hours,
        bag_count=payload.bag_count,
        quantity=payload.quantity,
        quantity_unit=payload.quantity_unit,
        rate_per_unit=_money(payload.rate_per_unit) if payload.rate_per_unit is not None else None,
        diesel_amount=_money(payload.diesel_amount),
        amount_given=_money(payload.amount_given),
        advance_amount=_money(payload.advance_amount),
        total_amount=_money(payload.total_amount),
        pending_amount=_money(payload.pending_amount),
        cleaning_status=payload.cleaning_status,
        facility_status=payload.facility_status,
        status=payload.status,
        comments=payload.comments,
        comments_te=payload.comments_te,
        created_by=actor_user_id,
        updated_by=actor_user_id,
    )
    db.add(row)
    db.flush()
    sync_field_service_diesel_expense(
        db,
        org_id,
        record_id=row.id,
        record_number=row.record_number,
        service_date=row.service_date,
        asset_id=row.asset_id,
        diesel_amount=row.diesel_amount,
        record_status=row.status,
        actor_user_id=actor_user_id,
    )
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="create",
        entity_id=row.id,
        after=_serialize(row),
        client=client,
        summary=f"Field service {row.record_number} created ({row.service_category})",
    )
    db.commit()
    db.refresh(row)
    return row


def update_field_service_record(
    db: Session,
    org_id: UUID,
    record_id: UUID,
    payload: FieldServiceRecordUpdateRequest,
    actor_user_id: UUID,
    client: ClientContext | None = None,
) -> FieldServiceRecord:
    row = get_field_service_record(db, org_id, record_id)
    before = _serialize(row)

    if payload.activity_type_id is not None or payload.farmer_id is not None or payload.vehicle_type_id is not None:
        _validate_refs(
            db,
            org_id,
            service_category=row.service_category,
            activity_type_id=payload.activity_type_id if payload.activity_type_id is not None else row.activity_type_id,
            farmer_id=payload.farmer_id if payload.farmer_id is not None else row.farmer_id,
            vehicle_type_id=payload.vehicle_type_id
            if payload.vehicle_type_id is not None
            else row.vehicle_type_id,
        )

    updates = payload.model_dump(exclude_unset=True)
    money_fields = {
        "rate_per_unit",
        "diesel_amount",
        "amount_given",
        "advance_amount",
        "total_amount",
        "pending_amount",
    }
    for key, value in updates.items():
        if key in money_fields and value is not None:
            setattr(row, key, _money(value))
        else:
            setattr(row, key, value)
    row.updated_by = actor_user_id
    db.flush()
    sync_field_service_diesel_expense(
        db,
        org_id,
        record_id=row.id,
        record_number=row.record_number,
        service_date=row.service_date,
        asset_id=row.asset_id,
        diesel_amount=row.diesel_amount,
        record_status=row.status,
        actor_user_id=actor_user_id,
    )
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="update",
        entity_id=row.id,
        before=before,
        after=_serialize(row),
        client=client,
        summary=f"Field service {row.record_number} updated",
    )
    db.commit()
    db.refresh(row)
    return row


def delete_field_service_record(
    db: Session,
    org_id: UUID,
    record_id: UUID,
    actor_user_id: UUID,
    client: ClientContext | None = None,
) -> None:
    row = get_field_service_record(db, org_id, record_id)
    before = _serialize(row)
    _soft_delete(row, actor_user_id)
    sync_field_service_diesel_expense(
        db,
        org_id,
        record_id=row.id,
        record_number=row.record_number,
        service_date=row.service_date,
        asset_id=row.asset_id,
        diesel_amount=_ZERO,
        record_status="cancelled",
        actor_user_id=actor_user_id,
    )
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="delete",
        entity_id=row.id,
        before=before,
        client=client,
        summary=f"Field service {row.record_number} deleted",
    )
    db.commit()


def diesel_expense_id_for_record(db: Session, org_id: UUID, record_id: UUID) -> UUID | None:
    expense = find_expense_by_source(db, org_id, FIELD_SERVICE_SOURCE, record_id)
    return expense.id if expense else None


def enrich_records(
    db: Session,
    org_id: UUID,
    rows: list[FieldServiceRecord],
) -> dict[UUID, dict[str, str | None]]:
    farmer_ids = {r.farmer_id for r in rows if r.farmer_id}
    activity_ids = {r.activity_type_id for r in rows if r.activity_type_id}
    vehicle_type_ids = {r.vehicle_type_id for r in rows if r.vehicle_type_id}
    record_ids = [r.id for r in rows]

    farmers: dict[UUID, Farmer] = {}
    if farmer_ids:
        for f in db.query(Farmer).filter(Farmer.org_id == org_id, Farmer.id.in_(farmer_ids)).all():
            farmers[f.id] = f

    activities: dict[UUID, str] = {}
    if activity_ids:
        for aid, name in (
            db.query(ActivityType.id, ActivityType.name)
            .filter(ActivityType.org_id == org_id, ActivityType.id.in_(activity_ids))
            .all()
        ):
            activities[aid] = name

    vehicle_types: dict[UUID, str] = {}
    if vehicle_type_ids:
        for vid, name in (
            db.query(VehicleType.id, VehicleType.name)
            .filter(VehicleType.org_id == org_id, VehicleType.id.in_(vehicle_type_ids))
            .all()
        ):
            vehicle_types[vid] = name

    diesel_expenses: dict[UUID, UUID] = {}
    if record_ids:
        from app.modules.financial.models import Expense

        for source_id, expense_id in (
            db.query(Expense.source_id, Expense.id)
            .filter(
                Expense.org_id == org_id,
                Expense.source_type == FIELD_SERVICE_SOURCE,
                Expense.source_id.in_(record_ids),
                Expense.deleted_at.is_(None),
            )
            .all()
        ):
            if source_id is not None:
                diesel_expenses[source_id] = expense_id

    result: dict[UUID, dict[str, str | None]] = {}
    for row in rows:
        farmer = farmers.get(row.farmer_id) if row.farmer_id else None
        diesel_id = diesel_expenses.get(row.id)
        result[row.id] = {
            "farmer_name": farmer.full_name if farmer else None,
            "farmer_phone": farmer.phone_primary if farmer else None,
            "activity_type_name": activities.get(row.activity_type_id) if row.activity_type_id else None,
            "vehicle_type_name": vehicle_types.get(row.vehicle_type_id) if row.vehicle_type_id else None,
            "diesel_expense_id": str(diesel_id) if diesel_id else None,
        }
    return result
