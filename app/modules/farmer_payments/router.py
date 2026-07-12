from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.core.client_context import ClientContext, get_client_context
from app.core.dependencies import CurrentUserContext, get_db, require_permission
from app.modules.farmer_payments import service
from app.modules.farmer_payments.schemas import (
    PAYMENT_TYPES,
    FarmerPaymentCreateRequest,
    FarmerPaymentListResponse,
    FarmerPaymentResponse,
    PaymentAllocateRequest,
    PaymentReverseRequest,
)
from app.shared.schemas.common import APIResponse

router = APIRouter(tags=["Payments"])

_TYPE_PATTERN = "^(" + "|".join(PAYMENT_TYPES) + ")$"


@router.get("/farmer-payments", response_model=APIResponse[FarmerPaymentListResponse])
def list_farmer_payments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    farmer_id: UUID | None = Query(default=None),
    payment_type: str | None = Query(default=None, pattern=_TYPE_PATTERN),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    ctx: CurrentUserContext = Depends(require_permission("farmer_payments:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_payments(
        db,
        ctx.user.org_id,
        page=page,
        page_size=page_size,
        farmer_id=farmer_id,
        payment_type=payment_type,
        date_from=date_from,
        date_to=date_to,
    )
    return APIResponse(
        data=FarmerPaymentListResponse(
            items=[FarmerPaymentResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/farmer-payments", response_model=APIResponse[FarmerPaymentResponse], status_code=201)
def create_farmer_payment(
    payload: FarmerPaymentCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("farmer_payments:create")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    row = service.create_payment(
        db,
        ctx.user.org_id,
        payload,
        ctx.user.id,
        client,
        idempotency_key=idempotency_key,
    )
    return APIResponse(data=FarmerPaymentResponse.model_validate(row))


@router.get("/farmer-payments/{payment_id}", response_model=APIResponse[FarmerPaymentResponse])
def get_farmer_payment(
    payment_id: UUID,
    payment_date: date = Query(...),
    ctx: CurrentUserContext = Depends(require_permission("farmer_payments:read")),
    db: Session = Depends(get_db),
):
    row = service.get_payment(db, ctx.user.org_id, payment_id, payment_date)
    return APIResponse(data=FarmerPaymentResponse.model_validate(row))


@router.post(
    "/farmer-payments/{payment_id}/allocate",
    response_model=APIResponse[FarmerPaymentResponse],
)
def allocate_farmer_payment(
    payment_id: UUID,
    payload: PaymentAllocateRequest,
    payment_date: date = Query(...),
    ctx: CurrentUserContext = Depends(require_permission("farmer_payments:create")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.allocate_payment(
        db, ctx.user.org_id, payment_id, payment_date, payload, ctx.user.id, client
    )
    return APIResponse(data=FarmerPaymentResponse.model_validate(row))


@router.post(
    "/farmer-payments/{payment_id}/reverse",
    response_model=APIResponse[FarmerPaymentResponse],
)
def reverse_farmer_payment(
    payment_id: UUID,
    payload: PaymentReverseRequest,
    payment_date: date = Query(...),
    ctx: CurrentUserContext = Depends(require_permission("farmer_payments:reverse")),
    client: ClientContext = Depends(get_client_context),
    db: Session = Depends(get_db),
):
    row = service.reverse_payment(
        db, ctx.user.org_id, payment_id, payment_date, payload, ctx.user.id, client
    )
    return APIResponse(data=FarmerPaymentResponse.model_validate(row))
