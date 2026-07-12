from __future__ import annotations

import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import AppError, NotFoundError
from app.modules.documents.models import Document, DocumentLink
from app.modules.financial.models import Collection
from app.modules.financial.schemas import CollectionCreateRequest
from app.modules.platform.models import PaymentMode
from app.shared.services.audit import write_audit_log

_COLLECTION_PREFIX = "COL-"
_ZERO = Decimal("0")
_TWOPLACES = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(_TWOPLACES, rounding=ROUND_HALF_UP)


def _next_collection_number(db: Session, org_id: UUID) -> str:
    rows = (
        db.query(Collection.collection_number)
        .filter(
            Collection.org_id == org_id,
            Collection.collection_number.like(f"{_COLLECTION_PREFIX}%"),
        )
        .all()
    )
    max_seq = 0
    for (code,) in rows:
        match = re.match(rf"^{re.escape(_COLLECTION_PREFIX)}(\d+)$", code or "")
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return f"{_COLLECTION_PREFIX}{max_seq + 1:04d}"


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


def _link_documents(
    db: Session,
    org_id: UUID,
    collection_id: UUID,
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
                entity_type="collection",
                entity_id=collection_id,
                link_role="primary_attachment",
            )
        )


def list_collections(
    db: Session,
    org_id: UUID,
    *,
    page: int,
    page_size: int,
    source_type: str | None = None,
    customer_id: UUID | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[list[Collection], int]:
    q = db.query(Collection).filter(Collection.org_id == org_id)
    if source_type:
        q = q.filter(Collection.source_type == source_type)
    if customer_id:
        q = q.filter(Collection.customer_id == customer_id)
    if date_from:
        q = q.filter(Collection.collection_date >= date_from)
    if date_to:
        q = q.filter(Collection.collection_date <= date_to)
    total = q.count()
    items = (
        q.order_by(Collection.collection_date.desc(), Collection.collection_number.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_collection(db: Session, org_id: UUID, collection_id: UUID) -> Collection:
    row = (
        db.query(Collection)
        .filter(Collection.id == collection_id, Collection.org_id == org_id)
        .first()
    )
    if row is None:
        raise NotFoundError("Collection not found")
    return row


def create_collection(
    db: Session,
    org_id: UUID,
    payload: CollectionCreateRequest,
    actor_user_id: UUID,
) -> Collection:
    _validate_payment_mode(db, org_id, payload.payment_mode_id)
    amount = _money(payload.amount)
    if amount <= _ZERO:
        raise AppError("Amount must be greater than zero", status_code=400)

    # Rental customer validation deferred until rentals module is live.
    if payload.source_type == "rental" and payload.customer_id is None:
        raise AppError("customer_id is required when source_type is rental", status_code=400)

    row = Collection(
        org_id=org_id,
        collection_number=_next_collection_number(db, org_id),
        source_type=payload.source_type,
        source_id=payload.source_id,
        customer_id=payload.customer_id,
        collection_date=payload.collection_date,
        amount=amount,
        payment_mode_id=payload.payment_mode_id,
        reference_no=payload.reference_no,
        notes=payload.notes,
        status="posted",
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
        entity_type="collection",
        entity_id=row.id,
        after_state={
            "collection_number": row.collection_number,
            "amount": str(row.amount),
            "source_type": row.source_type,
        },
    )
    db.commit()
    db.refresh(row)
    return row
