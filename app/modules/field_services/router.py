from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.client_context import ClientContext, get_client_context
from app.core.dependencies import CurrentUserContext, get_db, require_permission, require_role
from app.modules.field_services import service
from app.modules.field_services.schemas import (
    FieldServiceRecordCreateRequest,
    FieldServiceRecordListResponse,
    FieldServiceRecordResponse,
    FieldServiceRecordUpdateRequest,
)
from app.modules.users.models import User
from app.shared.schemas.common import APIResponse, MessageResponse

router = APIRouter(tags=["Field Services"])


def _with_audit_names(db: Session, row, enrich: dict[str, str | None]) -> FieldServiceRecordResponse:
    names: dict[UUID, str] = {}
    ids = {x for x in (getattr(row, "created_by", None), getattr(row, "updated_by", None)) if x}
    if ids:
        for uid, name in db.query(User.id, User.full_name).filter(User.id.in_(ids)).all():
            names[uid] = name
    data = FieldServiceRecordResponse.model_validate(row)
    diesel_raw = enrich.get("diesel_expense_id")
    diesel_expense_id = UUID(diesel_raw) if diesel_raw else None
    return data.model_copy(
        update={
            "created_by_name": names.get(row.created_by) if getattr(row, "created_by", None) else None,
            "updated_by_name": names.get(row.updated_by) if getattr(row, "updated_by", None) else None,
            "farmer_name": enrich.get("farmer_name"),
            "farmer_phone": enrich.get("farmer_phone"),
            "activity_type_name": enrich.get("activity_type_name"),
            "vehicle_type_name": enrich.get("vehicle_type_name"),
            "diesel_expense_id": diesel_expense_id,
        }
    )


@router.get("/field-services", response_model=APIResponse[FieldServiceRecordListResponse])
def list_field_services(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    service_category: str | None = Query(
        default=None,
        pattern="^(field_service|tractor_work|transport|fertiliser|seeds|agri_finance|vehicle_ops|godown)$",
    ),
    farmer_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None, pattern="^(open|completed|cancelled)$"),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    ctx: CurrentUserContext = Depends(require_permission("field_services:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_field_service_records(
        db,
        ctx.user.org_id,
        page=page,
        page_size=page_size,
        service_category=service_category,
        farmer_id=farmer_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )
    enrich = service.enrich_records(db, ctx.user.org_id, items)
    return APIResponse(
        data=FieldServiceRecordListResponse(
            items=[_with_audit_names(db, row, enrich.get(row.id, {})) for row in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/field-services", response_model=APIResponse[FieldServiceRecordResponse], status_code=201)
def create_field_service(
    payload: FieldServiceRecordCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("field_services:create")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.create_field_service_record(db, ctx.user.org_id, payload, ctx.user.id, client)
    enrich = service.enrich_records(db, ctx.user.org_id, [row]).get(row.id, {})
    return APIResponse(data=_with_audit_names(db, row, enrich))


@router.get("/field-services/{record_id}", response_model=APIResponse[FieldServiceRecordResponse])
def get_field_service(
    record_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("field_services:read")),
    db: Session = Depends(get_db),
):
    row = service.get_field_service_record(db, ctx.user.org_id, record_id)
    enrich = service.enrich_records(db, ctx.user.org_id, [row]).get(row.id, {})
    return APIResponse(data=_with_audit_names(db, row, enrich))


@router.patch("/field-services/{record_id}", response_model=APIResponse[FieldServiceRecordResponse])
def update_field_service(
    record_id: UUID,
    payload: FieldServiceRecordUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("field_services:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.update_field_service_record(db, ctx.user.org_id, record_id, payload, ctx.user.id, client)
    enrich = service.enrich_records(db, ctx.user.org_id, [row]).get(row.id, {})
    return APIResponse(data=_with_audit_names(db, row, enrich))


@router.delete("/field-services/{record_id}", response_model=APIResponse[MessageResponse])
def delete_field_service(
    record_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("field_services:delete")),
    _: CurrentUserContext = Depends(require_role("OWNER")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    service.delete_field_service_record(db, ctx.user.org_id, record_id, ctx.user.id, client)
    return APIResponse(data=MessageResponse(message="Field service record deleted"))
