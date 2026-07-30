from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.core.client_context import ClientContext, get_client_context
from app.core.dependencies import CurrentUserContext, get_current_user_context, get_db, require_permission, require_role
from app.modules.procurements import service
from app.modules.procurements.schemas import (
    PROCUREMENT_STATUSES,
    ProcurementCancelRequest,
    ProcurementCreateRequest,
    ProcurementDeductionInput,
    ProcurementListItemResponse,
    ProcurementListResponse,
    ProcurementResponse,
    ProcurementReverseRequest,
    ProcurementUpdateRequest,
    WeighmentRequest,
)
from app.modules.users.models import User
from app.shared.locale import normalize_locale
from app.shared.schemas.common import APIResponse
from app.shared.services.entity_notes import attach_entity_notes, attach_tags_only

router = APIRouter(tags=["Procurement"])

_STATUS_PATTERN = "^(" + "|".join(PROCUREMENT_STATUSES) + ")$"


def _audit_names(db: Session, row, response_cls, *, confirmed_by_name: str | None = None):
    names: dict[UUID, str] = {}
    ids = {x for x in (getattr(row, "created_by", None), getattr(row, "updated_by", None)) if x}
    if ids:
        for uid, name in db.query(User.id, User.full_name).filter(User.id.in_(ids)).all():
            names[uid] = name
    data = response_cls.model_validate(row)
    extra = {
        "created_by_name": names.get(row.created_by) if getattr(row, "created_by", None) else None,
        "updated_by_name": names.get(row.updated_by) if getattr(row, "updated_by", None) else None,
    }
    if confirmed_by_name is not None:
        extra["confirmed_by_name"] = confirmed_by_name
    elif getattr(row, "confirmed_by", None):
        conf_name = db.query(User.full_name).filter(User.id == row.confirmed_by).scalar()
        extra["confirmed_by_name"] = conf_name
    return data.model_copy(update=extra)


def _viewer_role_code(ctx: CurrentUserContext) -> str | None:
    role = getattr(ctx.user, "role", None)
    return role.code if role is not None else None


def _response_locale(
    ctx: CurrentUserContext = Depends(get_current_user_context),
    accept_language: str | None = Header(default=None, alias="Accept-Language"),
) -> str:
    return normalize_locale(accept_language or ctx.user.preferred_locale)


def _enrich_response(
    db: Session,
    row,
    *,
    include_deductions: bool = True,
    viewer_role_code: str | None = None,
    locale: str = "en",
) -> ProcurementResponse:
    farmers, villages, crops, buyers = service.related_names(db, [row], locale=locale)
    profit_summary = None
    if viewer_role_code and viewer_role_code.upper() != "FARMER":
        profit_summary = service.compute_profit_summary(row)
    response = _audit_names(db, row, ProcurementResponse).model_copy(
        update={
            "farmer_name": farmers.get(row.farmer_id),
            "village_name": villages.get(row.village_id),
            "crop_type_name": crops.get(row.crop_type_id),
            "buyer_name": buyers.get(row.buyer_id) if row.buyer_id else None,
            "deductions": row.deductions if include_deductions else [],
            "bag_entries": row.bag_entries if include_deductions else [],
            "profit_summary": profit_summary,
        }
    )
    return attach_entity_notes(db, row.org_id, "procurement", row.id, response)


def _list_item(db: Session, row, farmers, villages, crops, buyers, tags) -> ProcurementListItemResponse:
    return _audit_names(db, row, ProcurementListItemResponse).model_copy(
        update={
            "farmer_name": farmers.get(row.farmer_id),
            "crop_type_name": crops.get(row.crop_type_id),
            "buyer_name": buyers.get(row.buyer_id) if row.buyer_id else None,
            "tags": tags.get(row.id, []),
        }
    )


@router.get("/procurements", response_model=APIResponse[ProcurementListResponse])
def list_procurements(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    farmer_id: UUID | None = Query(default=None),
    village_id: UUID | None = Query(default=None),
    crop_type_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None, pattern=_STATUS_PATTERN),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    ctx: CurrentUserContext = Depends(require_permission("procurements:read")),
    db: Session = Depends(get_db),
    locale: str = Depends(_response_locale),
):
    items, total = service.list_procurements(
        db,
        ctx.user.org_id,
        page=page,
        page_size=page_size,
        farmer_id=farmer_id,
        village_id=village_id,
        crop_type_id=crop_type_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )
    farmers, villages, crops, buyers = service.related_names(db, items, locale=locale)
    tag_map = attach_tags_only(db, ctx.user.org_id, "procurement", [p.id for p in items])
    return APIResponse(
        data=ProcurementListResponse(
            items=[_list_item(db, p, farmers, villages, crops, buyers, tag_map) for p in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/procurements", response_model=APIResponse[ProcurementResponse], status_code=201)
def create_procurement(
    payload: ProcurementCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("procurements:create")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    locale: str = Depends(_response_locale),
):
    row = service.create_procurement(
        db, ctx.user.org_id, payload, ctx.user.id, client, idempotency_key=idempotency_key
    )
    return APIResponse(data=_enrich_response(db, row, viewer_role_code=_viewer_role_code(ctx), locale=locale))


@router.get("/procurements/{procurement_id}", response_model=APIResponse[ProcurementResponse])
def get_procurement(
    procurement_id: UUID,
    procurement_date: date = Query(...),
    ctx: CurrentUserContext = Depends(require_permission("procurements:read")),
    db: Session = Depends(get_db),
    locale: str = Depends(_response_locale),
):
    row = service.get_procurement(db, ctx.user.org_id, procurement_id, procurement_date)
    return APIResponse(data=_enrich_response(db, row, viewer_role_code=_viewer_role_code(ctx), locale=locale))


@router.patch("/procurements/{procurement_id}", response_model=APIResponse[ProcurementResponse])
def update_procurement(
    procurement_id: UUID,
    payload: ProcurementUpdateRequest,
    procurement_date: date = Query(...),
    ctx: CurrentUserContext = Depends(require_permission("procurements:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
    locale: str = Depends(_response_locale),
):
    row = service.update_procurement(
        db, ctx.user.org_id, procurement_id, procurement_date, payload, ctx.user.id, client
    )
    return APIResponse(data=_enrich_response(db, row, viewer_role_code=_viewer_role_code(ctx), locale=locale))


@router.post("/procurements/{procurement_id}/submit", response_model=APIResponse[ProcurementResponse])
def submit_procurement(
    procurement_id: UUID,
    procurement_date: date = Query(...),
    ctx: CurrentUserContext = Depends(require_permission("procurements:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
    locale: str = Depends(_response_locale),
):
    row = service.submit_procurement(
        db, ctx.user.org_id, procurement_id, procurement_date, ctx.user.id, client
    )
    return APIResponse(data=_enrich_response(db, row, viewer_role_code=_viewer_role_code(ctx), locale=locale))


@router.post("/procurements/{procurement_id}/weighment", response_model=APIResponse[ProcurementResponse])
def record_weighment(
    procurement_id: UUID,
    payload: WeighmentRequest,
    procurement_date: date = Query(...),
    ctx: CurrentUserContext = Depends(require_permission("procurements:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
    locale: str = Depends(_response_locale),
):
    row = service.record_weighment(
        db, ctx.user.org_id, procurement_id, procurement_date, payload, ctx.user.id, client
    )
    return APIResponse(data=_enrich_response(db, row, viewer_role_code=_viewer_role_code(ctx), locale=locale))


@router.post("/procurements/{procurement_id}/apply-price", response_model=APIResponse[ProcurementResponse])
def apply_price(
    procurement_id: UUID,
    procurement_date: date = Query(...),
    ctx: CurrentUserContext = Depends(require_permission("procurements:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
    locale: str = Depends(_response_locale),
):
    row = service.apply_price(db, ctx.user.org_id, procurement_id, procurement_date, ctx.user.id, client)
    return APIResponse(data=_enrich_response(db, row, viewer_role_code=_viewer_role_code(ctx), locale=locale))


@router.post("/procurements/{procurement_id}/confirm", response_model=APIResponse[ProcurementResponse])
def confirm_procurement(
    procurement_id: UUID,
    procurement_date: date = Query(...),
    ctx: CurrentUserContext = Depends(require_permission("procurements:confirm")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
    locale: str = Depends(_response_locale),
):
    row = service.confirm_procurement(
        db, ctx.user.org_id, procurement_id, procurement_date, ctx.user.id, client
    )
    return APIResponse(data=_enrich_response(db, row, viewer_role_code=_viewer_role_code(ctx), locale=locale))


@router.post("/procurements/{procurement_id}/cancel", response_model=APIResponse[ProcurementResponse])
def cancel_procurement(
    procurement_id: UUID,
    payload: ProcurementCancelRequest,
    procurement_date: date = Query(...),
    ctx: CurrentUserContext = Depends(require_permission("procurements:cancel")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
    locale: str = Depends(_response_locale),
):
    row = service.cancel_procurement(
        db, ctx.user.org_id, procurement_id, procurement_date, payload, ctx.user.id, client
    )
    return APIResponse(data=_enrich_response(db, row, viewer_role_code=_viewer_role_code(ctx), locale=locale))


@router.post("/procurements/{procurement_id}/reverse", response_model=APIResponse[ProcurementResponse])
def reverse_procurement(
    procurement_id: UUID,
    payload: ProcurementReverseRequest,
    procurement_date: date = Query(...),
    _: CurrentUserContext = Depends(require_role("OWNER")),
    ctx: CurrentUserContext = Depends(require_permission("procurements:confirm")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
    locale: str = Depends(_response_locale),
):
    row = service.reverse_procurement(
        db, ctx.user.org_id, procurement_id, procurement_date, payload, ctx.user.id, client
    )
    return APIResponse(data=_enrich_response(db, row, viewer_role_code=_viewer_role_code(ctx), locale=locale))


@router.post(
    "/procurements/{procurement_id}/deductions",
    response_model=APIResponse[ProcurementResponse],
    status_code=201,
)
def add_deduction(
    procurement_id: UUID,
    payload: ProcurementDeductionInput,
    procurement_date: date = Query(...),
    ctx: CurrentUserContext = Depends(require_permission("procurements:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
    locale: str = Depends(_response_locale),
):
    row = service.add_deduction(
        db, ctx.user.org_id, procurement_id, procurement_date, payload, ctx.user.id, client
    )
    return APIResponse(data=_enrich_response(db, row, viewer_role_code=_viewer_role_code(ctx), locale=locale))
