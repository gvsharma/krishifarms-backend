from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.financial.models import ExpenseCategory
from app.modules.financial.schemas import ExpenseCategoryCreateRequest, ExpenseCategoryUpdateRequest
from app.shared.services.audit import write_audit_log


def list_expense_categories(
    db: Session, org_id: UUID, page: int, page_size: int
) -> tuple[list[ExpenseCategory], int]:
    query = (
        db.query(ExpenseCategory)
        .filter(ExpenseCategory.org_id == org_id, ExpenseCategory.deleted_at.is_(None))
        .order_by(ExpenseCategory.name)
    )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def create_expense_category(
    db: Session, org_id: UUID, payload: ExpenseCategoryCreateRequest, actor_user_id: UUID
) -> ExpenseCategory:
    existing = (
        db.query(ExpenseCategory)
        .filter(
            ExpenseCategory.org_id == org_id,
            ExpenseCategory.name == payload.name,
            ExpenseCategory.deleted_at.is_(None),
        )
        .first()
    )
    if existing:
        raise ConflictError("Expense category already exists")

    category = ExpenseCategory(
        org_id=org_id,
        created_by=actor_user_id,
        updated_by=actor_user_id,
        **payload.model_dump(),
    )
    db.add(category)
    db.flush()
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="expense_category",
        entity_id=category.id,
        after_state=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(category)
    return category


def update_expense_category(
    db: Session,
    org_id: UUID,
    category_id: UUID,
    payload: ExpenseCategoryUpdateRequest,
    actor_user_id: UUID,
) -> ExpenseCategory:
    category = (
        db.query(ExpenseCategory)
        .filter(
            ExpenseCategory.id == category_id,
            ExpenseCategory.org_id == org_id,
            ExpenseCategory.deleted_at.is_(None),
        )
        .first()
    )
    if category is None:
        raise NotFoundError("Expense category not found")

    before = {"name": category.name, "type": category.type}
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    category.updated_by = actor_user_id
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_type="expense_category",
        entity_id=category.id,
        before_state=before,
        after_state=payload.model_dump(exclude_unset=True, mode="json"),
    )
    db.commit()
    db.refresh(category)
    return category


def delete_expense_category(
    db: Session, org_id: UUID, category_id: UUID, actor_user_id: UUID
) -> None:
    category = (
        db.query(ExpenseCategory)
        .filter(
            ExpenseCategory.id == category_id,
            ExpenseCategory.org_id == org_id,
            ExpenseCategory.deleted_at.is_(None),
        )
        .first()
    )
    if category is None:
        raise NotFoundError("Expense category not found")

    category.deleted_at = datetime.now(UTC)
    category.updated_by = actor_user_id
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_type="expense_category",
        entity_id=category.id,
    )
    db.commit()
