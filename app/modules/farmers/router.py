from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.client_context import ClientContext, get_client_context
from app.core.dependencies import CurrentUserContext, get_db, require_permission, require_role
from app.modules.farmers import service
from app.modules.farmers.schemas import (
    BankAccountCreateRequest,
    BankAccountResponse,
    BankAccountUpdateRequest,
    FarmerCreateRequest,
    FarmerDetailResponse,
    FarmerListItemResponse,
    FarmerListResponse,
    FarmerResponse,
    FarmerUpdateRequest,
    LandParcelCreateRequest,
    LandParcelResponse,
    LandParcelUpdateRequest,
    OutstandingResponse,
)
from app.modules.users.models import User
from app.shared.schemas.common import APIResponse, MessageResponse
from app.shared.services.entity_notes import attach_entity_notes, attach_tags_only

router = APIRouter(tags=["Farmers"])


def _audit_names(db: Session, row, response_cls):
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


@router.get("/farmers", response_model=APIResponse[FarmerListResponse])
def list_farmers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    village_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None, pattern="^(active|inactive|blocked)$"),
    q: str | None = Query(default=None, min_length=1, max_length=100),
    ctx: CurrentUserContext = Depends(require_permission("farmers:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_farmers(
        db, ctx.user.org_id, page=page, page_size=page_size, village_id=village_id, status=status, search=q
    )
    villages = service.village_name_map(db, items)
    tag_map = attach_tags_only(db, ctx.user.org_id, "farmer", [f.id for f in items])
    return APIResponse(
        data=FarmerListResponse(
            items=[
                _audit_names(db, f, FarmerListItemResponse).model_copy(
                    update={
                        "village_name": villages.get(f.village_id),
                        "tags": tag_map.get(f.id, []),
                    }
                )
                for f in items
            ],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/farmers", response_model=APIResponse[FarmerResponse], status_code=201)
def create_farmer(
    payload: FarmerCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("farmers:create")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.create_farmer(db, ctx.user.org_id, payload, ctx.user.id, client)
    villages = service.village_name_map(db, [row])
    response = _audit_names(db, row, FarmerResponse).model_copy(
        update={"village_name": villages.get(row.village_id), "tags": [], "comments": []}
    )
    return APIResponse(data=response)


@router.get("/farmers/{farmer_id}", response_model=APIResponse[FarmerDetailResponse])
def get_farmer(
    farmer_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("farmers:read")),
    db: Session = Depends(get_db),
):
    row = service.get_farmer(db, ctx.user.org_id, farmer_id)
    villages = service.village_name_map(db, [row])
    outstanding = service.farmer_outstanding(db, ctx.user.org_id, farmer_id)
    response = _audit_names(db, row, FarmerDetailResponse).model_copy(
        update={
            "village_name": villages.get(row.village_id),
            "outstanding_amount": outstanding,
            "bank_accounts": service.list_bank_accounts(db, ctx.user.org_id, farmer_id),
            "land_parcels": service.list_land_parcels(db, ctx.user.org_id, farmer_id),
        }
    )
    response = attach_entity_notes(db, ctx.user.org_id, "farmer", row.id, response)
    return APIResponse(data=response)


@router.patch("/farmers/{farmer_id}", response_model=APIResponse[FarmerResponse])
def update_farmer(
    farmer_id: UUID,
    payload: FarmerUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("farmers:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.update_farmer(db, ctx.user.org_id, farmer_id, payload, ctx.user.id, client)
    villages = service.village_name_map(db, [row])
    response = _audit_names(db, row, FarmerResponse).model_copy(
        update={"village_name": villages.get(row.village_id)}
    )
    response = attach_entity_notes(db, ctx.user.org_id, "farmer", row.id, response)
    return APIResponse(data=response)


@router.delete("/farmers/{farmer_id}", response_model=APIResponse[MessageResponse])
def delete_farmer(
    farmer_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("farmers:delete")),
    _: CurrentUserContext = Depends(require_role("OWNER")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    service.delete_farmer(db, ctx.user.org_id, farmer_id, ctx.user.id, client)
    return APIResponse(data=MessageResponse(message="Farmer deleted"))


@router.get("/farmers/{farmer_id}/outstanding", response_model=APIResponse[OutstandingResponse])
def get_farmer_outstanding(
    farmer_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("farmers:read")),
    db: Session = Depends(get_db),
):
    service.get_farmer(db, ctx.user.org_id, farmer_id)
    amount = service.farmer_outstanding(db, ctx.user.org_id, farmer_id)
    return APIResponse(
        data=OutstandingResponse(
            farmer_id=farmer_id,
            outstanding_amount=amount,
            as_of_date=date.today(),
        )
    )


@router.get("/farmers/{farmer_id}/bank-accounts", response_model=APIResponse[list[BankAccountResponse]])
def list_farmer_bank_accounts(
    farmer_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("farmers:read")),
    db: Session = Depends(get_db),
):
    items = service.list_bank_accounts(db, ctx.user.org_id, farmer_id)
    return APIResponse(data=items)


@router.post("/farmers/{farmer_id}/bank-accounts", response_model=APIResponse[BankAccountResponse], status_code=201)
def create_farmer_bank_account(
    farmer_id: UUID,
    payload: BankAccountCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("farmers:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.create_bank_account(db, ctx.user.org_id, farmer_id, payload, ctx.user.id, client)
    return APIResponse(data=row)


@router.patch(
    "/farmers/{farmer_id}/bank-accounts/{account_id}",
    response_model=APIResponse[BankAccountResponse],
)
def update_farmer_bank_account(
    farmer_id: UUID,
    account_id: UUID,
    payload: BankAccountUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("farmers:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.update_bank_account(
        db, ctx.user.org_id, farmer_id, account_id, payload, ctx.user.id, client
    )
    return APIResponse(data=row)


@router.delete(
    "/farmers/{farmer_id}/bank-accounts/{account_id}",
    response_model=APIResponse[MessageResponse],
)
def delete_farmer_bank_account(
    farmer_id: UUID,
    account_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("farmers:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    service.delete_bank_account(db, ctx.user.org_id, farmer_id, account_id, ctx.user.id, client)
    return APIResponse(data=MessageResponse(message="Bank account deleted"))


@router.get("/farmers/{farmer_id}/land-parcels", response_model=APIResponse[list[LandParcelResponse]])
def list_farmer_land_parcels(
    farmer_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("farmers:read")),
    db: Session = Depends(get_db),
):
    items = service.list_land_parcels(db, ctx.user.org_id, farmer_id)
    return APIResponse(data=items)


@router.post("/farmers/{farmer_id}/land-parcels", response_model=APIResponse[LandParcelResponse], status_code=201)
def create_farmer_land_parcel(
    farmer_id: UUID,
    payload: LandParcelCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("farmers:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.create_land_parcel(db, ctx.user.org_id, farmer_id, payload, ctx.user.id, client)
    return APIResponse(data=row)


@router.patch(
    "/farmers/{farmer_id}/land-parcels/{parcel_id}",
    response_model=APIResponse[LandParcelResponse],
)
def update_farmer_land_parcel(
    farmer_id: UUID,
    parcel_id: UUID,
    payload: LandParcelUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("farmers:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.update_land_parcel(
        db, ctx.user.org_id, farmer_id, parcel_id, payload, ctx.user.id, client
    )
    return APIResponse(data=row)


@router.delete(
    "/farmers/{farmer_id}/land-parcels/{parcel_id}",
    response_model=APIResponse[MessageResponse],
)
def delete_farmer_land_parcel(
    farmer_id: UUID,
    parcel_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("farmers:update")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    service.delete_land_parcel(db, ctx.user.org_id, farmer_id, parcel_id, ctx.user.id, client)
    return APIResponse(data=MessageResponse(message="Land parcel deleted"))
