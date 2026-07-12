from __future__ import annotations

import re
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.core.client_context import ClientContext
from app.core.exceptions import ConflictError, NotFoundError
from app.modules.farmer_payments.models import FarmerPayment, FarmerPaymentAllocation
from app.modules.farmer_payments.schemas import (
    FarmerPaymentCreateRequest,
    PaymentAllocateRequest,
    PaymentReverseRequest,
)
from app.modules.farmers.models import Farmer, FarmerBankAccount
from app.modules.platform.models import PaymentMode
from app.modules.procurements.models import FarmerLedgerEntry, Procurement
from app.shared.services.audit import write_activity_feed, write_audit_log

_PAYMENT_NUMBER_PREFIX = "FP-"
_ZERO = Decimal("0")
_TWOPLACES = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(_TWOPLACES, rounding=ROUND_HALF_UP)


def _next_payment_number(db: Session, org_id: UUID) -> str:
    rows = (
        db.query(FarmerPayment.payment_number)
        .filter(
            FarmerPayment.org_id == org_id,
            FarmerPayment.payment_number.like(f"{_PAYMENT_NUMBER_PREFIX}%"),
        )
        .all()
    )
    max_seq = 0
    for (code,) in rows:
        match = re.match(rf"^{re.escape(_PAYMENT_NUMBER_PREFIX)}(\d+)$", code or "")
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return f"{_PAYMENT_NUMBER_PREFIX}{max_seq + 1:04d}"


def _audit(
    db: Session,
    *,
    org_id: UUID,
    actor_user_id: UUID,
    action: str,
    entity_id: UUID,
    before: dict | None = None,
    after: dict | None = None,
    client: ClientContext | None = None,
    summary: str | None = None,
) -> None:
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action=action,
        entity_type="farmer_payment",
        entity_id=entity_id,
        before_state=before,
        after_state=after,
        device_id=client.device_id if client else None,
        client_type=client.client_type if client else None,
        request_id=client.request_id if client else None,
    )
    if summary:
        write_activity_feed(
            db,
            org_id=org_id,
            actor_user_id=actor_user_id,
            summary=summary,
            entity_type="farmer_payment",
            entity_id=entity_id,
            device_id=client.device_id if client else None,
            client_type=client.client_type if client else None,
        )


def _validate_farmer(db: Session, org_id: UUID, farmer_id: UUID) -> Farmer:
    row = (
        db.query(Farmer)
        .filter(Farmer.id == farmer_id, Farmer.org_id == org_id, Farmer.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Farmer not found")
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


def _validate_bank_account(
    db: Session, org_id: UUID, farmer_id: UUID, bank_account_id: UUID
) -> FarmerBankAccount:
    row = (
        db.query(FarmerBankAccount)
        .filter(
            FarmerBankAccount.id == bank_account_id,
            FarmerBankAccount.org_id == org_id,
            FarmerBankAccount.farmer_id == farmer_id,
            FarmerBankAccount.deleted_at.is_(None),
        )
        .first()
    )
    if row is None:
        raise NotFoundError("Bank account not found for farmer")
    return row


def _latest_ledger_balance(db: Session, org_id: UUID, farmer_id: UUID) -> Decimal:
    row = (
        db.query(FarmerLedgerEntry.balance_after)
        .filter(FarmerLedgerEntry.org_id == org_id, FarmerLedgerEntry.farmer_id == farmer_id)
        .order_by(FarmerLedgerEntry.entry_date.desc(), FarmerLedgerEntry.posted_at.desc())
        .first()
    )
    return row[0] if row else _ZERO


def _post_payment_ledger_credit(
    db: Session,
    *,
    org_id: UUID,
    farmer_id: UUID,
    entry_date: date,
    payment_type: str,
    reference_id: UUID,
    amount: Decimal,
    description: str,
    posted_by: UUID,
) -> FarmerLedgerEntry:
    credit = _money(amount)
    balance_after = _money(_latest_ledger_balance(db, org_id, farmer_id) - credit)
    row = FarmerLedgerEntry(
        org_id=org_id,
        farmer_id=farmer_id,
        entry_date=entry_date,
        entry_type=payment_type,
        reference_type="farmer_payment",
        reference_id=reference_id,
        debit=_ZERO,
        credit=credit,
        balance_after=balance_after,
        description=description,
        posted_at=datetime.now(UTC),
        posted_by=posted_by,
    )
    db.add(row)
    db.flush()
    return row


def list_payments(
    db: Session,
    org_id: UUID,
    *,
    page: int,
    page_size: int,
    farmer_id: UUID | None = None,
    payment_type: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[list[FarmerPayment], int]:
    q = db.query(FarmerPayment).filter(FarmerPayment.org_id == org_id)
    if farmer_id:
        q = q.filter(FarmerPayment.farmer_id == farmer_id)
    if payment_type:
        q = q.filter(FarmerPayment.payment_type == payment_type)
    if date_from:
        q = q.filter(FarmerPayment.payment_date >= date_from)
    if date_to:
        q = q.filter(FarmerPayment.payment_date <= date_to)

    total = q.count()
    items = (
        q.order_by(FarmerPayment.payment_date.desc(), FarmerPayment.posted_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_payment(
    db: Session,
    org_id: UUID,
    payment_id: UUID,
    payment_date: date,
) -> FarmerPayment:
    row = (
        db.query(FarmerPayment)
        .options(joinedload(FarmerPayment.allocations))
        .filter(
            FarmerPayment.id == payment_id,
            FarmerPayment.payment_date == payment_date,
            FarmerPayment.org_id == org_id,
        )
        .first()
    )
    if row is None:
        raise NotFoundError("Farmer payment not found")
    return row


def _allocated_total_for_payment(db: Session, payment: FarmerPayment) -> Decimal:
    total = (
        db.query(FarmerPaymentAllocation.allocated_amount)
        .filter(
            FarmerPaymentAllocation.payment_id == payment.id,
            FarmerPaymentAllocation.payment_date == payment.payment_date,
            FarmerPaymentAllocation.org_id == payment.org_id,
        )
        .all()
    )
    return _money(sum((row[0] for row in total), _ZERO))


def _procurement_allocated_total(
    db: Session,
    org_id: UUID,
    procurement_id: UUID,
    procurement_date: date,
) -> Decimal:
    rows = (
        db.query(FarmerPaymentAllocation.allocated_amount)
        .join(
            FarmerPayment,
            (FarmerPayment.id == FarmerPaymentAllocation.payment_id)
            & (FarmerPayment.payment_date == FarmerPaymentAllocation.payment_date),
        )
        .filter(
            FarmerPaymentAllocation.org_id == org_id,
            FarmerPaymentAllocation.procurement_id == procurement_id,
            FarmerPaymentAllocation.procurement_date == procurement_date,
            FarmerPayment.status == "completed",
        )
        .all()
    )
    return _money(sum((row[0] for row in rows), _ZERO))


def _sync_procurement_payment_status(
    db: Session,
    org_id: UUID,
    procurement: Procurement,
    *,
    payment_date: date | None = None,
) -> None:
    if procurement.status not in {"confirmed", "paid_partial", "paid_full"}:
        return

    allocated = _procurement_allocated_total(
        db, org_id, procurement.id, procurement.procurement_date
    )
    if allocated <= _ZERO:
        procurement.status = "confirmed"
        procurement.actual_payment_date = None
    elif allocated >= _money(procurement.net_amount):
        procurement.status = "paid_full"
        if payment_date is not None:
            procurement.actual_payment_date = payment_date
        elif procurement.actual_payment_date is None:
            procurement.actual_payment_date = date.today()
    else:
        procurement.status = "paid_partial"
        if payment_date is not None:
            procurement.actual_payment_date = payment_date


def allocate_payment(
    db: Session,
    org_id: UUID,
    payment_id: UUID,
    payment_date: date,
    payload: PaymentAllocateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> FarmerPayment:
    payment = get_payment(db, org_id, payment_id, payment_date)
    if payment.status != "completed":
        raise ConflictError("Only completed payments can be allocated")

    already = _allocated_total_for_payment(db, payment)
    new_total = _money(sum((_money(item.allocated_amount) for item in payload.allocations), _ZERO))
    if already + new_total > _money(payment.amount):
        raise ConflictError("Allocations exceed payment amount")

    touched: list[Procurement] = []
    for item in payload.allocations:
        amount = _money(item.allocated_amount)
        procurement = (
            db.query(Procurement)
            .filter(
                Procurement.id == item.procurement_id,
                Procurement.procurement_date == item.procurement_date,
                Procurement.org_id == org_id,
                Procurement.deleted_at.is_(None),
            )
            .first()
        )
        if procurement is None:
            raise NotFoundError("Procurement not found")
        if procurement.farmer_id != payment.farmer_id:
            raise ConflictError("Procurement farmer does not match payment farmer")
        if procurement.status not in {"confirmed", "paid_partial", "paid_full"}:
            raise ConflictError(
                f"Procurement {procurement.procurement_number} is not payable (status={procurement.status})"
            )

        remaining = _money(procurement.net_amount) - _procurement_allocated_total(
            db, org_id, procurement.id, procurement.procurement_date
        )
        if amount > remaining:
            raise ConflictError(
                f"Allocation exceeds remaining amount for {procurement.procurement_number}"
            )

        db.add(
            FarmerPaymentAllocation(
                org_id=org_id,
                payment_id=payment.id,
                payment_date=payment.payment_date,
                procurement_id=procurement.id,
                procurement_date=procurement.procurement_date,
                allocated_amount=amount,
            )
        )
        touched.append(procurement)

    db.flush()
    for procurement in touched:
        _sync_procurement_payment_status(
            db, org_id, procurement, payment_date=payment.payment_date
        )

    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="ALLOCATE",
        entity_id=payment.id,
        after={
            "payment_number": payment.payment_number,
            "allocations": [
                {
                    "procurement_id": str(item.procurement_id),
                    "allocated_amount": str(item.allocated_amount),
                }
                for item in payload.allocations
            ],
        },
        client=client,
        summary=f"Farmer payment allocated: {payment.payment_number}",
    )
    db.commit()
    return get_payment(db, org_id, payment_id, payment_date)


def reverse_payment(
    db: Session,
    org_id: UUID,
    payment_id: UUID,
    payment_date: date,
    payload: PaymentReverseRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> FarmerPayment:
    payment = get_payment(db, org_id, payment_id, payment_date)
    if payment.status != "completed":
        raise ConflictError("Only completed payments can be reversed")

    affected = [
        (alloc.procurement_id, alloc.procurement_date)
        for alloc in payment.allocations
        if alloc.procurement_id is not None and alloc.procurement_date is not None
    ]

    for alloc in list(payment.allocations):
        db.delete(alloc)
    db.flush()

    payment.status = "reversed"
    _post_payment_ledger_debit(
        db,
        org_id=org_id,
        farmer_id=payment.farmer_id,
        entry_date=payment.payment_date,
        payment_type=f"{payment.payment_type}_reversal",
        reference_id=payment.id,
        amount=payment.amount,
        description=f"Reversal of {payment.payment_number}: {payload.reason}",
        posted_by=actor_user_id,
    )

    for procurement_id, procurement_date_key in affected:
        procurement = (
            db.query(Procurement)
            .filter(
                Procurement.id == procurement_id,
                Procurement.procurement_date == procurement_date_key,
                Procurement.org_id == org_id,
                Procurement.deleted_at.is_(None),
            )
            .first()
        )
        if procurement is not None:
            _sync_procurement_payment_status(db, org_id, procurement)

    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="REVERSE",
        entity_id=payment.id,
        after={"status": payment.status, "reason": payload.reason},
        client=client,
        summary=f"Farmer payment reversed: {payment.payment_number}",
    )
    db.commit()
    return get_payment(db, org_id, payment_id, payment_date)


def _post_payment_ledger_debit(
    db: Session,
    *,
    org_id: UUID,
    farmer_id: UUID,
    entry_date: date,
    payment_type: str,
    reference_id: UUID,
    amount: Decimal,
    description: str,
    posted_by: UUID,
) -> FarmerLedgerEntry:
    debit = _money(amount)
    balance_after = _money(_latest_ledger_balance(db, org_id, farmer_id) + debit)
    row = FarmerLedgerEntry(
        org_id=org_id,
        farmer_id=farmer_id,
        entry_date=entry_date,
        entry_type=payment_type,
        reference_type="farmer_payment",
        reference_id=reference_id,
        debit=debit,
        credit=_ZERO,
        balance_after=balance_after,
        description=description,
        posted_at=datetime.now(UTC),
        posted_by=posted_by,
    )
    db.add(row)
    db.flush()
    return row


def create_payment(
    db: Session,
    org_id: UUID,
    payload: FarmerPaymentCreateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
    *,
    idempotency_key: str | None = None,
) -> FarmerPayment:
    if idempotency_key:
        existing = (
            db.query(FarmerPayment)
            .filter(
                FarmerPayment.org_id == org_id,
                FarmerPayment.idempotency_key == idempotency_key,
            )
            .first()
        )
        if existing:
            return existing

    amount = _money(payload.amount)
    if amount <= _ZERO:
        raise ConflictError("Payment amount must be greater than zero")

    _validate_farmer(db, org_id, payload.farmer_id)
    _validate_payment_mode(db, org_id, payload.payment_mode_id)
    if payload.bank_account_id is not None:
        _validate_bank_account(db, org_id, payload.farmer_id, payload.bank_account_id)

    payment_number = _next_payment_number(db, org_id)
    row = FarmerPayment(
        org_id=org_id,
        payment_number=payment_number,
        farmer_id=payload.farmer_id,
        payment_type=payload.payment_type,
        payment_date=payload.payment_date,
        amount=amount,
        payment_mode_id=payload.payment_mode_id,
        bank_account_id=payload.bank_account_id,
        reference_no=payload.reference_no,
        notes=payload.notes,
        status="completed",
        idempotency_key=idempotency_key,
        posted_at=datetime.now(UTC),
        posted_by=actor_user_id,
    )
    db.add(row)
    db.flush()

    _post_payment_ledger_credit(
        db,
        org_id=org_id,
        farmer_id=row.farmer_id,
        entry_date=row.payment_date,
        payment_type=row.payment_type,
        reference_id=row.id,
        amount=row.amount,
        description=f"Payment {row.payment_number}",
        posted_by=actor_user_id,
    )

    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_id=row.id,
        after={
            "payment_number": row.payment_number,
            "farmer_id": str(row.farmer_id),
            "payment_type": row.payment_type,
            "amount": str(row.amount),
            "status": row.status,
        },
        client=client,
        summary=f"Farmer payment recorded: {row.payment_number}",
    )
    db.commit()
    db.refresh(row)
    return row
