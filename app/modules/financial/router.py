from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUserContext, get_db, require_permission
from app.modules.financial import service
from app.modules.financial.schemas import (
    ExpenseCategoryCreateRequest,
    ExpenseCategoryListResponse,
    ExpenseCategoryResponse,
    ExpenseCategoryUpdateRequest,
)
from app.shared.schemas.common import APIResponse, MessageResponse

router = APIRouter(tags=["Financial"])


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
