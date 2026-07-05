from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.client_context import ClientContext, get_client_context
from app.core.dependencies import CurrentUserContext, get_db, require_permission, require_role
from app.modules.farmers import service
from app.modules.farmers.schemas import (
    FarmerCreateRequest,
    FarmerListItemResponse,
    FarmerListResponse,
    FarmerResponse,
    FarmerUpdateRequest,
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


@router.get("/farmers/{farmer_id}", response_model=APIResponse[FarmerResponse])
def get_farmer(
    farmer_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("farmers:read")),
    db: Session = Depends(get_db),
):
    row = service.get_farmer(db, ctx.user.org_id, farmer_id)
    villages = service.village_name_map(db, [row])
    response = _audit_names(db, row, FarmerResponse).model_copy(
        update={"village_name": villages.get(row.village_id)}
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
