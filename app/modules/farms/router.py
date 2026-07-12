from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUserContext, get_db, require_permission
from app.modules.farms import service
from app.modules.farms.schemas import (
    FarmActivityCreateRequest,
    FarmActivityListResponse,
    FarmActivityResponse,
    FarmActivityUpdateRequest,
    FarmCreateRequest,
    FarmListResponse,
    FarmResponse,
    FarmUpdateRequest,
)
from app.shared.schemas.common import APIResponse, MessageResponse

router = APIRouter(tags=["Farms"])


@router.get("/farms", response_model=APIResponse[FarmListResponse])
def list_farms(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    village_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None, pattern="^(active|inactive)$"),
    q: str | None = Query(default=None),
    ctx: CurrentUserContext = Depends(require_permission("farming:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_farms(
        db,
        ctx.user.org_id,
        page=page,
        page_size=page_size,
        village_id=village_id,
        status=status,
        q=q,
    )
    return APIResponse(
        data=FarmListResponse(
            items=[FarmResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/farms", response_model=APIResponse[FarmResponse], status_code=201)
def create_farm(
    payload: FarmCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("farming:create")),
    db: Session = Depends(get_db),
):
    row = service.create_farm(db, ctx.user.org_id, payload, ctx.user.id)
    return APIResponse(data=FarmResponse.model_validate(row))


@router.get("/farms/{farm_id}", response_model=APIResponse[FarmResponse])
def get_farm(
    farm_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("farming:read")),
    db: Session = Depends(get_db),
):
    row = service.get_farm(db, ctx.user.org_id, farm_id)
    return APIResponse(data=FarmResponse.model_validate(row))


@router.patch("/farms/{farm_id}", response_model=APIResponse[FarmResponse])
def update_farm(
    farm_id: UUID,
    payload: FarmUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("farming:update")),
    db: Session = Depends(get_db),
):
    row = service.update_farm(db, ctx.user.org_id, farm_id, payload, ctx.user.id)
    return APIResponse(data=FarmResponse.model_validate(row))


@router.delete("/farms/{farm_id}", response_model=APIResponse[MessageResponse])
def delete_farm(
    farm_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("farming:update")),
    db: Session = Depends(get_db),
):
    service.delete_farm(db, ctx.user.org_id, farm_id, ctx.user.id)
    return APIResponse(data=MessageResponse(message="Farm deleted"))


@router.get("/farms/{farm_id}/activities", response_model=APIResponse[FarmActivityListResponse])
def list_farm_activities(
    farm_id: UUID,
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    ctx: CurrentUserContext = Depends(require_permission("farming:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_activities(
        db, ctx.user.org_id, farm_id, date_from=date_from, date_to=date_to
    )
    return APIResponse(
        data=FarmActivityListResponse(
            items=[FarmActivityResponse.model_validate(item) for item in items],
            total=total,
        )
    )


@router.post(
    "/farms/{farm_id}/activities",
    response_model=APIResponse[FarmActivityResponse],
    status_code=201,
)
def create_farm_activity(
    farm_id: UUID,
    payload: FarmActivityCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("farming:create")),
    db: Session = Depends(get_db),
):
    row = service.create_activity(db, ctx.user.org_id, farm_id, payload, ctx.user.id)
    return APIResponse(data=FarmActivityResponse.model_validate(row))


@router.patch(
    "/farms/{farm_id}/activities/{activity_id}",
    response_model=APIResponse[FarmActivityResponse],
)
def update_farm_activity(
    farm_id: UUID,
    activity_id: UUID,
    payload: FarmActivityUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("farming:update")),
    db: Session = Depends(get_db),
):
    row = service.update_activity(
        db, ctx.user.org_id, farm_id, activity_id, payload, ctx.user.id
    )
    return APIResponse(data=FarmActivityResponse.model_validate(row))


@router.delete(
    "/farms/{farm_id}/activities/{activity_id}",
    response_model=APIResponse[MessageResponse],
)
def delete_farm_activity(
    farm_id: UUID,
    activity_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("farming:update")),
    db: Session = Depends(get_db),
):
    service.delete_activity(db, ctx.user.org_id, farm_id, activity_id, ctx.user.id)
    return APIResponse(data=MessageResponse(message="Farm activity deleted"))
