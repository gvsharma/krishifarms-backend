from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.client_context import ClientContext, get_client_context
from app.core.dependencies import CurrentUserContext, get_db, require_permission
from app.modules.hamali import service
from app.modules.hamali.schemas import (
    HamaliDailyEntryCreateRequest,
    HamaliDailyEntryListResponse,
    HamaliDailyEntryResponse,
    HamaliDailyEntryUpdateRequest,
    HamaliWeeklyPaymentCreateRequest,
    HamaliWeeklyPaymentListResponse,
    HamaliWeeklyPaymentMarkPaidRequest,
    HamaliWeeklyPaymentResponse,
    HamaliWeeklySummaryResponse,
    HamaliWorkerCreateRequest,
    HamaliWorkerListResponse,
    HamaliWorkerResponse,
    HamaliWorkerUpdateRequest,
)
from app.modules.users.models import User
from app.shared.schemas.common import APIResponse, MessageResponse

router = APIRouter(tags=["Hamali"])

_PAYMENT_STATUS_PATTERN = "^(pending|scheduled|paid)$"
_WEEKLY_STATUS_PATTERN = "^(draft|paid)$"


def _worker_response(db: Session, row) -> HamaliWorkerResponse:
    from app.modules.users.models import User as UserModel

    names: dict[UUID, str] = {}
    ids = {x for x in (row.created_by, row.updated_by) if x}
    if ids:
        for uid, name in db.query(UserModel.id, UserModel.full_name).filter(UserModel.id.in_(ids)).all():
            names[uid] = name
    data = HamaliWorkerResponse.model_validate(row)
    return data.model_copy(
        update={
            "created_by_name": names.get(row.created_by) if row.created_by else None,
            "updated_by_name": names.get(row.updated_by) if row.updated_by else None,
        }
    )


def _entry_response(db: Session, row) -> HamaliDailyEntryResponse:
    worker = service.worker_name_map(db, {row.hamali_worker_id}).get(row.hamali_worker_id)
    data = HamaliDailyEntryResponse.model_validate(row)
    return data.model_copy(
        update={
            "worker_name": worker.full_name if worker else None,
            "worker_code": worker.worker_code if worker else None,
        }
    )


def _weekly_response(db: Session, row) -> HamaliWeeklyPaymentResponse:
    paid_by_name = None
    if row.paid_by:
        paid_by_name = db.query(User.full_name).filter(User.id == row.paid_by).scalar()
    data = HamaliWeeklyPaymentResponse.model_validate(row)
    return data.model_copy(update={"paid_by_name": paid_by_name})


@router.get("/hamali/workers", response_model=APIResponse[HamaliWorkerListResponse])
def list_hamali_workers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    status: str | None = Query(default=None, pattern="^(active|inactive)$"),
    q: str | None = Query(default=None, min_length=1, max_length=100),
    ctx: CurrentUserContext = Depends(require_permission("hamali:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_workers(
        db, ctx.user.org_id, page=page, page_size=page_size, status=status, q=q
    )
    return APIResponse(
        data=HamaliWorkerListResponse(
            items=[_worker_response(db, w) for w in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/hamali/workers", response_model=APIResponse[HamaliWorkerResponse], status_code=201)
def create_hamali_worker(
    payload: HamaliWorkerCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("hamali:create")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.create_worker(db, ctx.user.org_id, payload, ctx.user.id, client)
    return APIResponse(data=_worker_response(db, row))


@router.patch("/hamali/workers/{worker_id}", response_model=APIResponse[HamaliWorkerResponse])
def update_hamali_worker(
    worker_id: UUID,
    payload: HamaliWorkerUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("hamali:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.update_worker(db, ctx.user.org_id, worker_id, payload, ctx.user.id, client)
    return APIResponse(data=_worker_response(db, row))


@router.delete("/hamali/workers/{worker_id}", response_model=APIResponse[MessageResponse])
def delete_hamali_worker(
    worker_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("hamali:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    service.delete_worker(db, ctx.user.org_id, worker_id, ctx.user.id, client)
    return APIResponse(data=MessageResponse(message="Hamali worker deleted"))


@router.get("/hamali/daily-entries", response_model=APIResponse[HamaliDailyEntryListResponse])
def list_hamali_daily_entries(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    hamali_worker_id: UUID | None = Query(default=None),
    payment_status: str | None = Query(default=None, pattern=_PAYMENT_STATUS_PATTERN),
    ctx: CurrentUserContext = Depends(require_permission("hamali:read")),
    db: Session = Depends(get_db),
):
    items, total, summary = service.list_daily_entries(
        db,
        ctx.user.org_id,
        page=page,
        page_size=page_size,
        date_from=date_from,
        date_to=date_to,
        hamali_worker_id=hamali_worker_id,
        payment_status=payment_status,
    )
    return APIResponse(
        data=HamaliDailyEntryListResponse(
            items=[_entry_response(db, e) for e in items],
            total=total,
            page=page,
            page_size=page_size,
            summary=summary,
        )
    )


@router.post("/hamali/daily-entries", response_model=APIResponse[HamaliDailyEntryResponse], status_code=201)
def create_hamali_daily_entry(
    payload: HamaliDailyEntryCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("hamali:create")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.create_daily_entry(db, ctx.user.org_id, payload, ctx.user.id, client)
    return APIResponse(data=_entry_response(db, row))


@router.patch("/hamali/daily-entries/{entry_id}", response_model=APIResponse[HamaliDailyEntryResponse])
def update_hamali_daily_entry(
    entry_id: UUID,
    payload: HamaliDailyEntryUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("hamali:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.update_daily_entry(db, ctx.user.org_id, entry_id, payload, ctx.user.id, client)
    return APIResponse(data=_entry_response(db, row))


@router.delete("/hamali/daily-entries/{entry_id}", response_model=APIResponse[MessageResponse])
def delete_hamali_daily_entry(
    entry_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("hamali:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    service.delete_daily_entry(db, ctx.user.org_id, entry_id, ctx.user.id, client)
    return APIResponse(data=MessageResponse(message="Hamali daily entry deleted"))


@router.get("/hamali/weekly-summary", response_model=APIResponse[HamaliWeeklySummaryResponse])
def get_hamali_weekly_summary(
    week_start_date: date = Query(...),
    ctx: CurrentUserContext = Depends(require_permission("hamali:read")),
    db: Session = Depends(get_db),
):
    data = service.weekly_summary(db, ctx.user.org_id, week_start_date)
    return APIResponse(data=data)


@router.get("/hamali/weekly-payments", response_model=APIResponse[HamaliWeeklyPaymentListResponse])
def list_hamali_weekly_payments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None, pattern=_WEEKLY_STATUS_PATTERN),
    ctx: CurrentUserContext = Depends(require_permission("hamali:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_weekly_payments(
        db, ctx.user.org_id, page=page, page_size=page_size, status=status
    )
    return APIResponse(
        data=HamaliWeeklyPaymentListResponse(
            items=[_weekly_response(db, p) for p in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/hamali/weekly-payments", response_model=APIResponse[HamaliWeeklyPaymentResponse], status_code=201)
def create_hamali_weekly_payment(
    payload: HamaliWeeklyPaymentCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("hamali:pay")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.create_weekly_payment(db, ctx.user.org_id, payload, ctx.user.id, client)
    return APIResponse(data=_weekly_response(db, row))


@router.post(
    "/hamali/weekly-payments/{payment_id}/mark-paid",
    response_model=APIResponse[HamaliWeeklyPaymentResponse],
)
def mark_hamali_weekly_payment_paid(
    payment_id: UUID,
    payload: HamaliWeeklyPaymentMarkPaidRequest,
    ctx: CurrentUserContext = Depends(require_permission("hamali:pay")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.mark_weekly_payment_paid(
        db, ctx.user.org_id, payment_id, payload, ctx.user.id, client
    )
    return APIResponse(data=_weekly_response(db, row))
