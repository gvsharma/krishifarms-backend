from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUserContext, get_db, require_permission
from app.modules.master_data import service
from app.modules.master_data.schemas import (
    CropTypeCreateRequest,
    CropTypeListResponse,
    CropTypeResponse,
    CropTypeUpdateRequest,
    VillageCreateRequest,
    VillageListResponse,
    VillageResponse,
    VillageUpdateRequest,
)
from app.shared.schemas.common import APIResponse, MessageResponse

router = APIRouter(tags=["Master Data"])


@router.get("/villages", response_model=APIResponse[VillageListResponse])
def list_villages(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ctx: CurrentUserContext = Depends(require_permission("villages:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_villages(db, ctx.user.org_id, page, page_size)
    return APIResponse(
        data=VillageListResponse(
            items=[VillageResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/villages", response_model=APIResponse[VillageResponse], status_code=201)
def create_village(
    payload: VillageCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("villages:create")),
    db: Session = Depends(get_db),
):
    village = service.create_village(db, ctx.user.org_id, payload, ctx.user.id)
    return APIResponse(data=VillageResponse.model_validate(village))


@router.patch("/villages/{village_id}", response_model=APIResponse[VillageResponse])
def update_village(
    village_id: UUID,
    payload: VillageUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("villages:update")),
    db: Session = Depends(get_db),
):
    village = service.update_village(db, ctx.user.org_id, village_id, payload, ctx.user.id)
    return APIResponse(data=VillageResponse.model_validate(village))


@router.delete("/villages/{village_id}", response_model=APIResponse[MessageResponse])
def delete_village(
    village_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("villages:delete")),
    db: Session = Depends(get_db),
):
    service.delete_village(db, ctx.user.org_id, village_id, ctx.user.id)
    return APIResponse(data=MessageResponse(message="Village deleted"))


@router.get("/crop-types", response_model=APIResponse[CropTypeListResponse])
def list_crop_types(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ctx: CurrentUserContext = Depends(require_permission("crop_types:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_crop_types(db, ctx.user.org_id, page, page_size)
    return APIResponse(
        data=CropTypeListResponse(
            items=[CropTypeResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/crop-types", response_model=APIResponse[CropTypeResponse], status_code=201)
def create_crop_type(
    payload: CropTypeCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("crop_types:create")),
    db: Session = Depends(get_db),
):
    crop_type = service.create_crop_type(db, ctx.user.org_id, payload, ctx.user.id)
    return APIResponse(data=CropTypeResponse.model_validate(crop_type))


@router.patch("/crop-types/{crop_type_id}", response_model=APIResponse[CropTypeResponse])
def update_crop_type(
    crop_type_id: UUID,
    payload: CropTypeUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("crop_types:update")),
    db: Session = Depends(get_db),
):
    crop_type = service.update_crop_type(db, ctx.user.org_id, crop_type_id, payload, ctx.user.id)
    return APIResponse(data=CropTypeResponse.model_validate(crop_type))


@router.delete("/crop-types/{crop_type_id}", response_model=APIResponse[MessageResponse])
def delete_crop_type(
    crop_type_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("crop_types:delete")),
    db: Session = Depends(get_db),
):
    service.delete_crop_type(db, ctx.user.org_id, crop_type_id, ctx.user.id)
    return APIResponse(data=MessageResponse(message="Crop type deleted"))
