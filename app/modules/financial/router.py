from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUserContext, get_db, require_permission
from app.modules.financial import collection_service, expense_service, service
from app.modules.financial.schemas import (
    CollectionCreateRequest,
    CollectionListResponse,
    CollectionResponse,
    ExpenseCategoryCreateRequest,
    ExpenseCategoryListResponse,
    ExpenseCategoryResponse,
    ExpenseCategoryUpdateRequest,
    ExpenseCreateRequest,
    ExpenseListResponse,
    ExpenseResponse,
    ExpenseUpdateRequest,
)
from app.shared.schemas.common import APIResponse, MessageResponse

router = APIRouter(tags=["Financial"])

_EXPENSE_STATUS_PATTERN = "^(draft|posted|reversed)$"
_COLLECTION_SOURCE_PATTERN = "^(rental|other)$"


@router.get("/expense-categories", response_model=APIResponse[ExpenseCategoryListResponse])
def list_expense_categories(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ctx: CurrentUserContext = Depends(require_permission("expense_categories:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_expense_categories(db, ctx.user.org_id, page, page_size)
    return APIResponse(
        data=ExpenseCategoryListResponse(
            items=[ExpenseCategoryResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/expense-categories", response_model=APIResponse[ExpenseCategoryResponse], status_code=201)
def create_expense_category(
    payload: ExpenseCategoryCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("expense_categories:create")),
    db: Session = Depends(get_db),
):
    category = service.create_expense_category(db, ctx.user.org_id, payload, ctx.user.id)
    return APIResponse(data=ExpenseCategoryResponse.model_validate(category))


@router.patch("/expense-categories/{category_id}", response_model=APIResponse[ExpenseCategoryResponse])
def update_expense_category(
    category_id: UUID,
    payload: ExpenseCategoryUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("expense_categories:update")),
    db: Session = Depends(get_db),
):
    category = service.update_expense_category(db, ctx.user.org_id, category_id, payload, ctx.user.id)
    return APIResponse(data=ExpenseCategoryResponse.model_validate(category))


@router.delete("/expense-categories/{category_id}", response_model=APIResponse[MessageResponse])
def delete_expense_category(
    category_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("expense_categories:delete")),
    db: Session = Depends(get_db),
):
    service.delete_expense_category(db, ctx.user.org_id, category_id, ctx.user.id)
    return APIResponse(data=MessageResponse(message="Expense category deleted"))


@router.get("/expenses", response_model=APIResponse[ExpenseListResponse], tags=["Expenses"])
def list_expenses(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category_id: UUID | None = Query(default=None),
    farm_id: UUID | None = Query(default=None),
    asset_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None, pattern=_EXPENSE_STATUS_PATTERN),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    source_type: str | None = Query(default=None),
    source_id: UUID | None = Query(default=None),
    ctx: CurrentUserContext = Depends(require_permission("expenses:read")),
    db: Session = Depends(get_db),
):
    items, total = expense_service.list_expenses(
        db,
        ctx.user.org_id,
        page=page,
        page_size=page_size,
        category_id=category_id,
        farm_id=farm_id,
        asset_id=asset_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        source_type=source_type,
        source_id=source_id,
    )
    return APIResponse(
        data=ExpenseListResponse(
            items=[
                ExpenseResponse.model_validate(expense_service.expense_to_response(db, ctx.user.org_id, item))
                for item in items
            ],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/expenses", response_model=APIResponse[ExpenseResponse], status_code=201, tags=["Expenses"])
def create_expense(
    payload: ExpenseCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("expenses:create")),
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    _ = idempotency_key  # reserved for financial idempotency store
    row = expense_service.create_expense(db, ctx.user.org_id, payload, ctx.user.id)
    return APIResponse(
        data=ExpenseResponse.model_validate(expense_service.expense_to_response(db, ctx.user.org_id, row))
    )


@router.get("/expenses/{expense_id}", response_model=APIResponse[ExpenseResponse], tags=["Expenses"])
def get_expense(
    expense_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("expenses:read")),
    db: Session = Depends(get_db),
):
    row = expense_service.get_expense(db, ctx.user.org_id, expense_id)
    return APIResponse(
        data=ExpenseResponse.model_validate(expense_service.expense_to_response(db, ctx.user.org_id, row))
    )


@router.patch("/expenses/{expense_id}", response_model=APIResponse[ExpenseResponse], tags=["Expenses"])
def update_expense(
    expense_id: UUID,
    payload: ExpenseUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("expenses:update")),
    db: Session = Depends(get_db),
):
    row = expense_service.update_expense(db, ctx.user.org_id, expense_id, payload, ctx.user.id)
    return APIResponse(
        data=ExpenseResponse.model_validate(expense_service.expense_to_response(db, ctx.user.org_id, row))
    )


@router.delete("/expenses/{expense_id}", response_model=APIResponse[MessageResponse], tags=["Expenses"])
def delete_expense(
    expense_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("expenses:delete")),
    db: Session = Depends(get_db),
):
    expense_service.delete_expense(db, ctx.user.org_id, expense_id, ctx.user.id)
    return APIResponse(data=MessageResponse(message="Expense deleted"))


@router.get("/collections", response_model=APIResponse[CollectionListResponse], tags=["Collections"])
def list_collections(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    source_type: str | None = Query(default=None, pattern=_COLLECTION_SOURCE_PATTERN),
    customer_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    ctx: CurrentUserContext = Depends(require_permission("collections:read")),
    db: Session = Depends(get_db),
):
    items, total = collection_service.list_collections(
        db,
        ctx.user.org_id,
        page=page,
        page_size=page_size,
        source_type=source_type,
        customer_id=customer_id,
        date_from=date_from,
        date_to=date_to,
    )
    return APIResponse(
        data=CollectionListResponse(
            items=[CollectionResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post(
    "/collections",
    response_model=APIResponse[CollectionResponse],
    status_code=201,
    tags=["Collections"],
)
def create_collection(
    payload: CollectionCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("collections:create")),
    db: Session = Depends(get_db),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    _ = idempotency_key
    row = collection_service.create_collection(db, ctx.user.org_id, payload, ctx.user.id)
    return APIResponse(data=CollectionResponse.model_validate(row))


@router.get(
    "/collections/{collection_id}",
    response_model=APIResponse[CollectionResponse],
    tags=["Collections"],
)
def get_collection(
    collection_id: UUID,
    ctx: CurrentUserContext = Depends(require_permission("collections:read")),
    db: Session = Depends(get_db),
):
    row = collection_service.get_collection(db, ctx.user.org_id, collection_id)
    return APIResponse(data=CollectionResponse.model_validate(row))
