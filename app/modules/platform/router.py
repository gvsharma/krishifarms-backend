from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.client_context import ClientContext, get_client_context
from app.core.dependencies import CurrentUserContext, get_db, require_permission
from app.modules.platform import service
from app.modules.platform.schemas import (
    ActivityTypeCreateRequest,
    ActivityTypeListResponse,
    ActivityTypeResponse,
    ActivityTypeUpdateRequest,
    BuyerCreateRequest,
    BuyerListResponse,
    BuyerResponse,
    BuyerUpdateRequest,
    CommentCreateRequest,
    CommentListResponse,
    CommentResponse,
    CropPriceCreateRequest,
    CropPriceListResponse,
    CropPriceResponse,
    CropPriceUpdateRequest,
    FieldAgentCreateRequest,
    FieldAgentListResponse,
    FieldAgentResponse,
    FieldAgentUpdateRequest,
    PaymentModeCreateRequest,
    PaymentModeListResponse,
    PaymentModeResponse,
    PaymentModeUpdateRequest,
    TagCreateRequest,
    TagListResponse,
    TagResponse,
    VehicleTypeCreateRequest,
    VehicleTypeListResponse,
    VehicleTypeResponse,
    VehicleTypeUpdateRequest,
)
from app.modules.users.models import User
from app.shared.schemas.common import APIResponse, MessageResponse

router = APIRouter(tags=["Platform"])


def _with_audit_names(db: Session, row, response_cls):
    names: dict[UUID, str] = {}
    ids = {x for x in (getattr(row, "created_by", None), getattr(row, "updated_by", None)) if x}
    if ids:
        for uid, name in db.query(User.id, User.full_name).filter(User.id.in_(ids)).all():
            names[uid] = name
    data = response_cls.model_validate(row)
    return data.model_copy(
        update={
            "created_by_name": names.get(row.created_by) if getattr(row, "created_by", None) else None,
            "updated_by_name": names.get(row.updated_by) if getattr(row, "updated_by", None) else None,
        }
    )


# --- Activity types ---


@router.get("/activity-types", response_model=APIResponse[ActivityTypeListResponse])
def list_activity_types(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ctx: CurrentUserContext = Depends(require_permission("activity_types:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_activity_types(db, ctx.user.org_id, page, page_size)
    return APIResponse(
        data=ActivityTypeListResponse(
            items=[_with_audit_names(db, i, ActivityTypeResponse) for i in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/activity-types", response_model=APIResponse[ActivityTypeResponse], status_code=201)
def create_activity_type(
    payload: ActivityTypeCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("activity_types:create")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.create_activity_type(db, ctx.user.org_id, payload, ctx.user.id, client)
    return APIResponse(data=_with_audit_names(db, row, ActivityTypeResponse))


@router.patch("/activity-types/{row_id}", response_model=APIResponse[ActivityTypeResponse])
def update_activity_type(
    row_id: UUID,
    payload: ActivityTypeUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("activity_types:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.update_activity_type(db, ctx.user.org_id, row_id, payload, ctx.user.id, client)
    return APIResponse(data=_with_audit_names(db, row, ActivityTypeResponse))


@router.delete("/activity-types/{row_id}", response_model=APIResponse[MessageResponse])
def delete_activity_type(
    row_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("activity_types:delete")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    service.delete_activity_type(db, ctx.user.org_id, row_id, ctx.user.id, client)
    return APIResponse(data=MessageResponse(message="Activity type deleted"))


# --- Payment modes ---


@router.get("/payment-modes", response_model=APIResponse[PaymentModeListResponse])
def list_payment_modes(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ctx: CurrentUserContext = Depends(require_permission("payment_modes:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_payment_modes(db, ctx.user.org_id, page, page_size)
    return APIResponse(
        data=PaymentModeListResponse(
            items=[_with_audit_names(db, i, PaymentModeResponse) for i in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/payment-modes", response_model=APIResponse[PaymentModeResponse], status_code=201)
def create_payment_mode(
    payload: PaymentModeCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("payment_modes:create")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.create_payment_mode(db, ctx.user.org_id, payload, ctx.user.id, client)
    return APIResponse(data=_with_audit_names(db, row, PaymentModeResponse))


@router.patch("/payment-modes/{row_id}", response_model=APIResponse[PaymentModeResponse])
def update_payment_mode(
    row_id: UUID,
    payload: PaymentModeUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("payment_modes:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.update_payment_mode(db, ctx.user.org_id, row_id, payload, ctx.user.id, client)
    return APIResponse(data=_with_audit_names(db, row, PaymentModeResponse))


@router.delete("/payment-modes/{row_id}", response_model=APIResponse[MessageResponse])
def delete_payment_mode(
    row_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("payment_modes:delete")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    service.delete_payment_mode(db, ctx.user.org_id, row_id, ctx.user.id, client)
    return APIResponse(data=MessageResponse(message="Payment mode deleted"))


# --- Buyers ---


@router.get("/buyers", response_model=APIResponse[BuyerListResponse])
def list_buyers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ctx: CurrentUserContext = Depends(require_permission("buyers:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_buyers(db, ctx.user.org_id, page, page_size)
    return APIResponse(
        data=BuyerListResponse(
            items=[_with_audit_names(db, i, BuyerResponse) for i in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/buyers", response_model=APIResponse[BuyerResponse], status_code=201)
def create_buyer(
    payload: BuyerCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("buyers:create")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.create_buyer(db, ctx.user.org_id, payload, ctx.user.id, client)
    return APIResponse(data=_with_audit_names(db, row, BuyerResponse))


@router.patch("/buyers/{row_id}", response_model=APIResponse[BuyerResponse])
def update_buyer(
    row_id: UUID,
    payload: BuyerUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("buyers:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.update_buyer(db, ctx.user.org_id, row_id, payload, ctx.user.id, client)
    return APIResponse(data=_with_audit_names(db, row, BuyerResponse))


@router.delete("/buyers/{row_id}", response_model=APIResponse[MessageResponse])
def delete_buyer(
    row_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("buyers:delete")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    service.delete_buyer(db, ctx.user.org_id, row_id, ctx.user.id, client)
    return APIResponse(data=MessageResponse(message="Buyer deleted"))


# --- Field agents ---


@router.get("/agents", response_model=APIResponse[FieldAgentListResponse])
def list_agents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ctx: CurrentUserContext = Depends(require_permission("agents:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_agents(db, ctx.user.org_id, page, page_size)
    return APIResponse(
        data=FieldAgentListResponse(
            items=[_with_audit_names(db, i, FieldAgentResponse) for i in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/agents", response_model=APIResponse[FieldAgentResponse], status_code=201)
def create_agent(
    payload: FieldAgentCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("agents:create")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.create_agent(db, ctx.user.org_id, payload, ctx.user.id, client)
    return APIResponse(data=_with_audit_names(db, row, FieldAgentResponse))


@router.patch("/agents/{row_id}", response_model=APIResponse[FieldAgentResponse])
def update_agent(
    row_id: UUID,
    payload: FieldAgentUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("agents:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.update_agent(db, ctx.user.org_id, row_id, payload, ctx.user.id, client)
    return APIResponse(data=_with_audit_names(db, row, FieldAgentResponse))


@router.delete("/agents/{row_id}", response_model=APIResponse[MessageResponse])
def delete_agent(
    row_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("agents:delete")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    service.delete_agent(db, ctx.user.org_id, row_id, ctx.user.id, client)
    return APIResponse(data=MessageResponse(message="Agent deleted"))


# --- Vehicle types ---


@router.get("/vehicle-types", response_model=APIResponse[VehicleTypeListResponse])
def list_vehicle_types(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ctx: CurrentUserContext = Depends(require_permission("vehicle_types:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_vehicle_types(db, ctx.user.org_id, page, page_size)
    return APIResponse(
        data=VehicleTypeListResponse(
            items=[_with_audit_names(db, i, VehicleTypeResponse) for i in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/vehicle-types", response_model=APIResponse[VehicleTypeResponse], status_code=201)
def create_vehicle_type(
    payload: VehicleTypeCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("vehicle_types:create")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.create_vehicle_type(db, ctx.user.org_id, payload, ctx.user.id, client)
    return APIResponse(data=_with_audit_names(db, row, VehicleTypeResponse))


@router.patch("/vehicle-types/{row_id}", response_model=APIResponse[VehicleTypeResponse])
def update_vehicle_type(
    row_id: UUID,
    payload: VehicleTypeUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("vehicle_types:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.update_vehicle_type(db, ctx.user.org_id, row_id, payload, ctx.user.id, client)
    return APIResponse(data=_with_audit_names(db, row, VehicleTypeResponse))


@router.delete("/vehicle-types/{row_id}", response_model=APIResponse[MessageResponse])
def delete_vehicle_type(
    row_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("vehicle_types:delete")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    service.delete_vehicle_type(db, ctx.user.org_id, row_id, ctx.user.id, client)
    return APIResponse(data=MessageResponse(message="Vehicle type deleted"))


# --- Crop prices ---


@router.get("/crop-prices", response_model=APIResponse[CropPriceListResponse])
def list_crop_prices(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ctx: CurrentUserContext = Depends(require_permission("crop_prices:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_crop_prices(db, ctx.user.org_id, page, page_size)
    return APIResponse(
        data=CropPriceListResponse(
            items=[_with_audit_names(db, i, CropPriceResponse) for i in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/crop-prices", response_model=APIResponse[CropPriceResponse], status_code=201)
def create_crop_price(
    payload: CropPriceCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("crop_prices:create")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.create_crop_price(db, ctx.user.org_id, payload, ctx.user.id, client)
    return APIResponse(data=_with_audit_names(db, row, CropPriceResponse))


@router.patch("/crop-prices/{row_id}", response_model=APIResponse[CropPriceResponse])
def update_crop_price(
    row_id: UUID,
    payload: CropPriceUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("crop_prices:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.update_crop_price(db, ctx.user.org_id, row_id, payload, ctx.user.id, client)
    return APIResponse(data=_with_audit_names(db, row, CropPriceResponse))


@router.delete("/crop-prices/{row_id}", response_model=APIResponse[MessageResponse])
def delete_crop_price(
    row_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("crop_prices:delete")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    service.delete_crop_price(db, ctx.user.org_id, row_id, ctx.user.id, client)
    return APIResponse(data=MessageResponse(message="Crop price rule deleted"))


# --- Comments ---


@router.get("/comments", response_model=APIResponse[CommentListResponse])
def list_comments(
    entity_type: str | None = Query(default=None),
    entity_id: UUID | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ctx: CurrentUserContext = Depends(require_permission("comments:read")),
    db: Session = Depends(get_db),
):
    items, total, names = service.list_comments(db, ctx.user.org_id, entity_type, entity_id, page, page_size)
    return APIResponse(
        data=CommentListResponse(
            items=[
                CommentResponse.model_validate(i).model_copy(update={"author_name": names.get(i.author_user_id)})
                for i in items
            ],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/comments", response_model=APIResponse[CommentResponse], status_code=201)
def create_comment(
    payload: CommentCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("comments:create")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.create_comment(db, ctx.user.org_id, payload, ctx.user.id, client)
    return APIResponse(
        data=CommentResponse.model_validate(row).model_copy(update={"author_name": ctx.user.full_name})
    )


# --- Tags ---


@router.get("/tags", response_model=APIResponse[TagListResponse])
def list_tags(
    entity_type: str | None = Query(default=None),
    entity_id: UUID | None = Query(default=None),
    ctx: CurrentUserContext = Depends(require_permission("tags:read")),
    db: Session = Depends(get_db),
):
    items, names = service.list_tags(db, ctx.user.org_id, entity_type, entity_id)
    return APIResponse(
        data=TagListResponse(
            items=[
                TagResponse.model_validate(i).model_copy(
                    update={"created_by_name": names.get(i.created_by) if i.created_by else None}
                )
                for i in items
            ],
            total=len(items),
        )
    )


@router.post("/tags", response_model=APIResponse[TagResponse], status_code=201)
def create_tag(
    payload: TagCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("tags:create")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.create_tag(db, ctx.user.org_id, payload, ctx.user.id, client)
    return APIResponse(
        data=TagResponse.model_validate(row).model_copy(update={"created_by_name": ctx.user.full_name})
    )


@router.delete("/tags/{tag_id}", response_model=APIResponse[MessageResponse])
def delete_tag(
    tag_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("tags:delete")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    service.delete_tag(db, ctx.user.org_id, tag_id, ctx.user.id, client)
    return APIResponse(data=MessageResponse(message="Tag removed"))
