from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUserContext, get_db, require_permission
from app.modules.assets import service
from app.modules.assets.schemas import (
    AssetCreateRequest,
    AssetListResponse,
    AssetResponse,
    AssetUpdateRequest,
)
from app.shared.schemas.common import APIResponse, MessageResponse

router = APIRouter(tags=["Assets"])


@router.get("/assets", response_model=APIResponse[AssetListResponse])
def list_assets(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    asset_category: str | None = Query(default=None),
    status: str | None = Query(default=None),
    vehicle_type_id: UUID | None = Query(default=None),
    ctx: CurrentUserContext = Depends(require_permission("assets:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_assets(
        db,
        ctx.user.org_id,
        page,
        page_size,
        asset_category=asset_category,
        status=status,
        vehicle_type_id=vehicle_type_id,
    )
    return APIResponse(
        data=AssetListResponse(
            items=[AssetResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/assets", response_model=APIResponse[AssetResponse], status_code=201)
def create_asset(
    payload: AssetCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("assets:create")),
    db: Session = Depends(get_db),
):
    row = service.create_asset(db, ctx.user.org_id, payload, ctx.user.id)
    return APIResponse(data=AssetResponse.model_validate(row))


@router.get("/assets/{asset_id}", response_model=APIResponse[AssetResponse])
def get_asset(
    asset_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("assets:read")),
    db: Session = Depends(get_db),
):
    row = service.get_asset(db, ctx.user.org_id, asset_id)
    return APIResponse(data=AssetResponse.model_validate(row))


@router.patch("/assets/{asset_id}", response_model=APIResponse[AssetResponse])
def update_asset(
    asset_id: UUID,
    payload: AssetUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("assets:update")),
    db: Session = Depends(get_db),
):
    row = service.update_asset(db, ctx.user.org_id, asset_id, payload, ctx.user.id)
    return APIResponse(data=AssetResponse.model_validate(row))


@router.delete("/assets/{asset_id}", response_model=APIResponse[MessageResponse])
def delete_asset(
    asset_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("assets:update")),
    db: Session = Depends(get_db),
):
    service.delete_asset(db, ctx.user.org_id, asset_id, ctx.user.id)
    return APIResponse(data=MessageResponse(message="Asset deleted"))
