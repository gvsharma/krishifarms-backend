from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUserContext, get_db, require_permission
from app.modules.hamali import service
from app.modules.hamali.schemas import (
    HamaliDailyResponse,
    HamaliSummaryPeriodResponse,
    HamaliWorkEntryCreateRequest,
    HamaliWorkEntryListResponse,
    HamaliWorkEntryResponse,
    HamaliWorkEntryUpdateRequest,
    WorkerCreateRequest,
    WorkerResponse,
)
from app.shared.schemas.common import APIResponse, PaginatedResponse

router = APIRouter(tags=["Hamali"])


@router.get("/hamali/me/daily", response_model=APIResponse[HamaliDailyResponse])
def get_my_hamali_daily(
    work_date: date | None = Query(default=None),
    ctx: CurrentUserContext = Depends(require_permission("hamali_work:read")),
    db: Session = Depends(get_db),
):
    target = work_date or date.today()
    data = service.get_my_daily(db, ctx.user.org_id, ctx.user, target)
    return APIResponse(data=data)


@router.get("/hamali/me/summary", response_model=APIResponse[HamaliSummaryPeriodResponse])
def get_my_hamali_summary(
    period: str = Query(default="week", pattern="^(week|month)$"),
    anchor_date: date | None = Query(default=None),
    ctx: CurrentUserContext = Depends(require_permission("hamali_work:read")),
    db: Session = Depends(get_db),
):
    anchor = anchor_date or date.today()
    data = service.get_my_summary(db, ctx.user.org_id, ctx.user, period=period, anchor_date=anchor)
    return APIResponse(data=data)


@router.get("/hamali/workers", response_model=APIResponse[PaginatedResponse[WorkerResponse]])
def list_hamali_workers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    ctx: CurrentUserContext = Depends(require_permission("workers:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_workers(db, ctx.user.org_id, page, page_size)
    return APIResponse(
        data=PaginatedResponse(
            items=[WorkerResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/hamali/workers", response_model=APIResponse[WorkerResponse], status_code=201)
def create_hamali_worker(
    payload: WorkerCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("workers:create")),
    db: Session = Depends(get_db),
):
    row = service.create_worker(db, ctx.user.org_id, payload, ctx.user.id)
    db.commit()
    db.refresh(row)
    return APIResponse(data=WorkerResponse.model_validate(row))


@router.get("/hamali/work-entries", response_model=APIResponse[HamaliWorkEntryListResponse])
def list_hamali_work_entries(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    worker_id: UUID | None = Query(default=None),
    work_date: date | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    ctx: CurrentUserContext = Depends(require_permission("hamali_work:read")),
    db: Session = Depends(get_db),
):
    if ctx.user.role and ctx.user.role.code == "HAMALI":
        worker_id = ctx.user.worker_id
    items, total = service.list_work_entries(
        db,
        ctx.user.org_id,
        page=page,
        page_size=page_size,
        worker_id=worker_id,
        work_date=work_date,
        date_from=date_from,
        date_to=date_to,
    )
    return APIResponse(
        data=HamaliWorkEntryListResponse(
            items=[HamaliWorkEntryResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/hamali/work-entries", response_model=APIResponse[HamaliWorkEntryResponse], status_code=201)
def create_hamali_work_entry(
    payload: HamaliWorkEntryCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("hamali_work:create")),
    db: Session = Depends(get_db),
):
    row = service.create_work_entry(db, ctx.user.org_id, payload, ctx.user.id)
    db.commit()
    return APIResponse(data=HamaliWorkEntryResponse.model_validate(row))


@router.patch("/hamali/work-entries/{entry_id}", response_model=APIResponse[HamaliWorkEntryResponse])
def update_hamali_work_entry(
    entry_id: UUID,
    payload: HamaliWorkEntryUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("hamali_work:update")),
    db: Session = Depends(get_db),
):
    row = service.update_work_entry(db, ctx.user.org_id, entry_id, payload, ctx.user.id)
    db.commit()
    return APIResponse(data=HamaliWorkEntryResponse.model_validate(row))


@router.delete("/hamali/work-entries/{entry_id}", response_model=APIResponse[dict])
def delete_hamali_work_entry(
    entry_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("hamali_work:delete")),
    db: Session = Depends(get_db),
):
    service.delete_work_entry(db, ctx.user.org_id, entry_id, ctx.user.id)
    db.commit()
    return APIResponse(data={"deleted": True})
