from __future__ import annotations

import re
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ConflictError, NotFoundError
from app.modules.assets.models import Asset
from app.modules.documents.models import Document, DocumentLink
from app.modules.farms.models import Farm
from app.modules.financial.models import Expense, ExpenseCategory
from app.modules.financial.schemas import (
    FIELD_SERVICE_SOURCE,
    FUEL_CATEGORY_NAME,
    VEHICLE_TRIP_SOURCE,
    ExpenseCreateRequest,
    ExpenseUpdateRequest,
)
from app.modules.platform.models import PaymentMode
from app.shared.services.audit import write_audit_log

_EXPENSE_PREFIX = "EXP-"
_ZERO = Decimal("0")
_TWOPLACES = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(_TWOPLACES, rounding=ROUND_HALF_UP)


def _next_expense_number(db: Session, org_id: UUID) -> str:
    rows = (
        db.query(Expense.expense_number)
        .filter(Expense.org_id == org_id, Expense.expense_number.like(f"{_EXPENSE_PREFIX}%"))
        .all()
    )
    max_seq = 0
    for (code,) in rows:
        match = re.match(rf"^{re.escape(_EXPENSE_PREFIX)}(\d+)$", code or "")
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return f"{_EXPENSE_PREFIX}{max_seq + 1:04d}"


def _validate_category(db: Session, org_id: UUID, category_id: UUID) -> ExpenseCategory:
    row = (
        db.query(ExpenseCategory)
        .filter(
            ExpenseCategory.id == category_id,
            ExpenseCategory.org_id == org_id,
            ExpenseCategory.deleted_at.is_(None),
        )
        .first()
    )
    if row is None:
        raise NotFoundError("Expense category not found")
    return row


def _validate_payment_mode(db: Session, org_id: UUID, payment_mode_id: UUID) -> PaymentMode:
    row = (
        db.query(PaymentMode)
        .filter(
            PaymentMode.id == payment_mode_id,
            PaymentMode.org_id == org_id,
            PaymentMode.deleted_at.is_(None),
            PaymentMode.is_active.is_(True),
        )
        .first()
    )
    if row is None:
        raise NotFoundError("Payment mode not found")
    return row


def _validate_farm(db: Session, org_id: UUID, farm_id: UUID) -> None:
    row = (
        db.query(Farm)
        .filter(Farm.id == farm_id, Farm.org_id == org_id, Farm.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Farm not found")


def _validate_asset(db: Session, org_id: UUID, asset_id: UUID) -> None:
    row = (
        db.query(Asset)
        .filter(Asset.id == asset_id, Asset.org_id == org_id, Asset.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Asset not found")


def _link_documents(
    db: Session,
    org_id: UUID,
    expense_id: UUID,
    document_ids: list[UUID],
) -> None:
    if not document_ids:
        return
    docs = (
        db.query(Document)
        .filter(Document.id.in_(document_ids), Document.org_id == org_id)
        .all()
    )
    found = {d.id for d in docs}
    missing = [str(i) for i in document_ids if i not in found]
    if missing:
        raise NotFoundError(f"Document(s) not found: {', '.join(missing)}")
    for doc_id in document_ids:
        db.add(
            DocumentLink(
                document_id=doc_id,
                entity_type="expense",
                entity_id=expense_id,
                link_role="primary_attachment",
            )
        )


def _category_name_map(db: Session, org_id: UUID, category_ids: set[UUID]) -> dict[UUID, str]:
    if not category_ids:
        return {}
    rows = (
        db.query(ExpenseCategory.id, ExpenseCategory.name)
        .filter(
            ExpenseCategory.org_id == org_id,
            ExpenseCategory.id.in_(category_ids),
        )
        .all()
    )
    return {row.id: row.name for row in rows}


def expense_to_response(db: Session, org_id: UUID, row: Expense) -> dict:
    names = _category_name_map(db, org_id, {row.category_id})
    return {
        "id": row.id,
        "expense_number": row.expense_number,
        "category_id": row.category_id,
        "category_name": names.get(row.category_id),
        "expense_date": row.expense_date,
        "amount": row.amount,
        "vendor_name": row.vendor_name,
        "payment_mode_id": row.payment_mode_id,
        "farm_id": row.farm_id,
        "asset_id": row.asset_id,
        "description": row.description,
        "description_te": row.description_te,
        "status": row.status,
        "source_type": row.source_type,
        "source_id": row.source_id,
    }


def list_expenses(
    db: Session,
    org_id: UUID,
    *,
    page: int,
    page_size: int,
    category_id: UUID | None = None,
    farm_id: UUID | None = None,
    asset_id: UUID | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    source_type: str | None = None,
    source_id: UUID | None = None,
) -> tuple[list[Expense], int]:
    q = db.query(Expense).filter(Expense.org_id == org_id, Expense.deleted_at.is_(None))
    if category_id:
        q = q.filter(Expense.category_id == category_id)
    if farm_id:
        q = q.filter(Expense.farm_id == farm_id)
    if asset_id:
        q = q.filter(Expense.asset_id == asset_id)
    if status:
        q = q.filter(Expense.status == status)
    if date_from:
        q = q.filter(Expense.expense_date >= date_from)
    if date_to:
        q = q.filter(Expense.expense_date <= date_to)
    if source_type:
        q = q.filter(Expense.source_type == source_type)
    if source_id:
        q = q.filter(Expense.source_id == source_id)
    total = q.count()
    items = (
        q.order_by(Expense.expense_date.desc(), Expense.expense_number.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_expense(db: Session, org_id: UUID, expense_id: UUID) -> Expense:
    row = (
        db.query(Expense)
        .filter(Expense.id == expense_id, Expense.org_id == org_id, Expense.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Expense not found")
    return row


def create_expense(
    db: Session,
    org_id: UUID,
    payload: ExpenseCreateRequest,
    actor_user_id: UUID,
    *,
    commit: bool = True,
    source_type: str | None = None,
    source_id: UUID | None = None,
) -> Expense:
    _validate_category(db, org_id, payload.category_id)
    _validate_payment_mode(db, org_id, payload.payment_mode_id)
    if payload.farm_id:
        _validate_farm(db, org_id, payload.farm_id)
    if payload.asset_id:
        _validate_asset(db, org_id, payload.asset_id)

    amount = _money(payload.amount)
    if amount <= _ZERO:
        raise AppError("Amount must be greater than zero", status_code=400)

    row = Expense(
        org_id=org_id,
        expense_number=_next_expense_number(db, org_id),
        category_id=payload.category_id,
        expense_date=payload.expense_date,
        amount=amount,
        vendor_name=payload.vendor_name,
        payment_mode_id=payload.payment_mode_id,
        farm_id=payload.farm_id,
        asset_id=payload.asset_id,
        description=payload.description,
        description_te=payload.description_te,
        status=payload.status,
        source_type=source_type,
        source_id=source_id,
        created_by=actor_user_id,
        updated_by=actor_user_id,
    )
    db.add(row)
    db.flush()
    _link_documents(db, org_id, row.id, payload.document_ids)
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="expense",
        entity_id=row.id,
        after_state={
            "expense_number": row.expense_number,
            "amount": str(row.amount),
            "status": row.status,
            "source_type": source_type,
            "source_id": str(source_id) if source_id else None,
        },
    )
    if commit:
        db.commit()
        db.refresh(row)
    return row


def update_expense(
    db: Session,
    org_id: UUID,
    expense_id: UUID,
    payload: ExpenseUpdateRequest,
    actor_user_id: UUID,
) -> Expense:
    row = get_expense(db, org_id, expense_id)
    if row.status != "draft":
        raise ConflictError("Only draft expenses can be updated")

    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data and data["category_id"] is not None:
        _validate_category(db, org_id, data["category_id"])
    if "payment_mode_id" in data and data["payment_mode_id"] is not None:
        _validate_payment_mode(db, org_id, data["payment_mode_id"])
    if "farm_id" in data and data["farm_id"] is not None:
        _validate_farm(db, org_id, data["farm_id"])
    if "asset_id" in data and data["asset_id"] is not None:
        _validate_asset(db, org_id, data["asset_id"])
    if "amount" in data and data["amount"] is not None:
        data["amount"] = _money(data["amount"])

    before = {"amount": str(row.amount), "status": row.status}
    for field, value in data.items():
        setattr(row, field, value)
    row.updated_by = actor_user_id
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_type="expense",
        entity_id=row.id,
        before_state=before,
        after_state={k: (str(v) if isinstance(v, Decimal) else v) for k, v in data.items()},
    )
    db.commit()
    db.refresh(row)
    return row


def delete_expense(db: Session, org_id: UUID, expense_id: UUID, actor_user_id: UUID) -> None:
    row = get_expense(db, org_id, expense_id)
    row.deleted_at = datetime.now(UTC)
    row.updated_by = actor_user_id
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_type="expense",
        entity_id=row.id,
    )
    db.commit()


def find_expense_by_source(
    db: Session,
    org_id: UUID,
    source_type: str,
    source_id: UUID,
    *,
    include_deleted: bool = False,
) -> Expense | None:
    q = db.query(Expense).filter(
        Expense.org_id == org_id,
        Expense.source_type == source_type,
        Expense.source_id == source_id,
    )
    if not include_deleted:
        q = q.filter(Expense.deleted_at.is_(None))
    return q.order_by(Expense.created_at.desc()).first()


def _fuel_category(db: Session, org_id: UUID) -> ExpenseCategory:
    row = (
        db.query(ExpenseCategory)
        .filter(
            ExpenseCategory.org_id == org_id,
            ExpenseCategory.name == FUEL_CATEGORY_NAME,
            ExpenseCategory.deleted_at.is_(None),
        )
        .first()
    )
    if row is None:
        raise NotFoundError(
            f"Expense category '{FUEL_CATEGORY_NAME}' not found — seed expense categories first"
        )
    return row


def _default_cash_payment_mode(db: Session, org_id: UUID) -> PaymentMode:
    row = (
        db.query(PaymentMode)
        .filter(
            PaymentMode.org_id == org_id,
            PaymentMode.code == "cash",
            PaymentMode.deleted_at.is_(None),
            PaymentMode.is_active.is_(True),
        )
        .first()
    )
    if row is None:
        row = (
            db.query(PaymentMode)
            .filter(
                PaymentMode.org_id == org_id,
                PaymentMode.deleted_at.is_(None),
                PaymentMode.is_active.is_(True),
            )
            .order_by(PaymentMode.name)
            .first()
        )
    if row is None:
        raise NotFoundError("No active payment mode found — seed payment modes first")
    return row


def sync_vehicle_trip_diesel_expense(
    db: Session,
    org_id: UUID,
    *,
    trip_id: UUID,
    trip_number: str,
    trip_date: date,
    asset_id: UUID,
    fuel_cost: Decimal,
    fuel_liters: Decimal | None,
    trip_status: str,
    actor_user_id: UUID,
) -> Expense | None:
    """Create/update/soft-delete Fuel expense linked to a vehicle trip. Flush only (no commit)."""
    existing = find_expense_by_source(db, org_id, VEHICLE_TRIP_SOURCE, trip_id)
    amount = _money(fuel_cost)
    should_post = trip_status != "cancelled" and amount > _ZERO

    if not should_post:
        if existing is not None:
            existing.deleted_at = datetime.now(UTC)
            existing.updated_by = actor_user_id
            existing.status = "reversed"
        return None

    liters_bit = f", {fuel_liters} L" if fuel_liters is not None else ""
    description = f"Diesel for trip {trip_number}{liters_bit}"

    if existing is not None:
        existing.amount = amount
        existing.expense_date = trip_date
        existing.asset_id = asset_id
        existing.description = description
        existing.status = "posted"
        existing.updated_by = actor_user_id
        existing.deleted_at = None
        return existing

    category = _fuel_category(db, org_id)
    payment_mode = _default_cash_payment_mode(db, org_id)
    payload = ExpenseCreateRequest(
        category_id=category.id,
        expense_date=trip_date,
        amount=amount,
        payment_mode_id=payment_mode.id,
        asset_id=asset_id,
        description=description,
        status="posted",
    )
    return create_expense(
        db,
        org_id,
        payload,
        actor_user_id,
        commit=False,
        source_type=VEHICLE_TRIP_SOURCE,
        source_id=trip_id,
    )


def sync_field_service_diesel_expense(
    db: Session,
    org_id: UUID,
    *,
    record_id: UUID,
    record_number: str,
    service_date: date,
    asset_id: UUID | None,
    diesel_amount: Decimal,
    record_status: str,
    actor_user_id: UUID,
) -> Expense | None:
    """Create/update/soft-delete Fuel expense linked to a field-service record. Flush only (no commit)."""
    # Include soft-deleted so cancel→reopen reactivates instead of orphaning a second row.
    existing = find_expense_by_source(
        db, org_id, FIELD_SERVICE_SOURCE, record_id, include_deleted=True
    )
    amount = _money(diesel_amount)
    should_post = record_status != "cancelled" and amount > _ZERO

    if not should_post:
        if existing is not None and existing.deleted_at is None:
            existing.deleted_at = datetime.now(UTC)
            existing.updated_by = actor_user_id
            existing.status = "reversed"
        return None

    description = f"Diesel for field service {record_number}"

    if existing is not None:
        existing.amount = amount
        existing.expense_date = service_date
        existing.asset_id = asset_id
        existing.description = description
        existing.status = "posted"
        existing.updated_by = actor_user_id
        existing.deleted_at = None
        return existing

    category = _fuel_category(db, org_id)
    payment_mode = _default_cash_payment_mode(db, org_id)
    payload = ExpenseCreateRequest(
        category_id=category.id,
        expense_date=service_date,
        amount=amount,
        payment_mode_id=payment_mode.id,
        asset_id=asset_id,
        description=description,
        status="posted",
    )
    return create_expense(
        db,
        org_id,
        payload,
        actor_user_id,
        commit=False,
        source_type=FIELD_SERVICE_SOURCE,
        source_id=record_id,
    )
