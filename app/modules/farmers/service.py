from __future__ import annotations

import re
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.client_context import ClientContext
from app.core.exceptions import ConflictError, NotFoundError
from app.modules.farmers.models import Farmer, FarmerBankAccount, FarmerLandParcel
from app.modules.farmers.schemas import (
    BankAccountCreateRequest,
    BankAccountResponse,
    BankAccountUpdateRequest,
    LandParcelCreateRequest,
    LandParcelResponse,
    LandParcelUpdateRequest,
    FarmerCreateRequest,
    FarmerUpdateRequest,
)
from app.modules.master_data.models import Village
from app.modules.procurements.models import FarmerLedgerEntry
from app.shared.crypto import decrypt_value, encrypt_value, mask_account_number
from app.shared.services.audit import write_activity_feed, write_audit_log

_FARMER_CODE_PREFIX = "FMR-"
_ZERO = Decimal("0")


def _soft_delete(entity: Farmer, actor_user_id: UUID) -> None:
    entity.deleted_at = datetime.now(UTC)
    entity.updated_by = actor_user_id


def _next_farmer_code(db: Session, org_id: UUID) -> str:
    rows = (
        db.query(Farmer.farmer_code)
        .filter(Farmer.org_id == org_id, Farmer.farmer_code.like(f"{_FARMER_CODE_PREFIX}%"))
        .all()
    )
    max_seq = 0
    for (code,) in rows:
        match = re.match(rf"^{re.escape(_FARMER_CODE_PREFIX)}(\d+)$", code or "")
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return f"{_FARMER_CODE_PREFIX}{max_seq + 1:04d}"


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
        entity_type="farmer",
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
            entity_type="farmer",
            entity_id=entity_id,
        )


def _village_names(db: Session, village_ids: set[UUID]) -> dict[UUID, str]:
    if not village_ids:
        return {}
    rows = db.query(Village.id, Village.name).filter(Village.id.in_(village_ids)).all()
    return {row.id: row.name for row in rows}


def list_farmers(
    db: Session,
    org_id: UUID,
    *,
    page: int,
    page_size: int,
    village_id: UUID | None = None,
    status: str | None = None,
    search: str | None = None,
) -> tuple[list[Farmer], int]:
    q = db.query(Farmer).filter(Farmer.org_id == org_id, Farmer.deleted_at.is_(None))
    if village_id:
        q = q.filter(Farmer.village_id == village_id)
    if status:
        q = q.filter(Farmer.status == status)
    if search:
        term = f"%{search.strip()}%"
        q = q.filter(
            or_(
                Farmer.full_name.ilike(term),
                Farmer.full_name_te.ilike(term),
                Farmer.phone_primary.ilike(term),
                Farmer.farmer_code.ilike(term),
            )
        )
    q = q.order_by(Farmer.full_name)
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_farmer(db: Session, org_id: UUID, farmer_id: UUID) -> Farmer:
    row = (
        db.query(Farmer)
        .filter(Farmer.id == farmer_id, Farmer.org_id == org_id, Farmer.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Farmer not found")
    return row


def create_farmer(
    db: Session,
    org_id: UUID,
    payload: FarmerCreateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> Farmer:
    village = (
        db.query(Village)
        .filter(Village.id == payload.village_id, Village.org_id == org_id, Village.deleted_at.is_(None))
        .first()
    )
    if village is None:
        raise NotFoundError("Village not found")

    phone_conflict = (
        db.query(Farmer)
        .filter(
            Farmer.org_id == org_id,
            Farmer.phone_primary == payload.phone_primary,
            Farmer.deleted_at.is_(None),
        )
        .first()
    )
    if phone_conflict:
        raise ConflictError("Farmer with this phone already exists")

    farmer_code = _next_farmer_code(db, org_id)
    row = Farmer(
        org_id=org_id,
        farmer_code=farmer_code,
        created_by=actor_user_id,
        updated_by=actor_user_id,
        status="active",
        **payload.model_dump(),
    )
    db.add(row)
    db.flush()
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_id=row.id,
        after={"farmer_code": row.farmer_code, "full_name": row.full_name, "village_id": str(row.village_id)},
        client=client,
        summary=f"Farmer registered: {row.full_name} ({row.farmer_code})",
    )
    db.commit()
    db.refresh(row)
    return row


def update_farmer(
    db: Session,
    org_id: UUID,
    farmer_id: UUID,
    payload: FarmerUpdateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> Farmer:
    row = get_farmer(db, org_id, farmer_id)
    before = {"full_name": row.full_name, "status": row.status, "village_id": str(row.village_id)}

    data = payload.model_dump(exclude_unset=True)
    if "village_id" in data and data["village_id"] is not None:
        village = (
            db.query(Village)
            .filter(Village.id == data["village_id"], Village.org_id == org_id, Village.deleted_at.is_(None))
            .first()
        )
        if village is None:
            raise NotFoundError("Village not found")

    if "phone_primary" in data and data["phone_primary"] != row.phone_primary:
        phone_conflict = (
            db.query(Farmer)
            .filter(
                Farmer.org_id == org_id,
                Farmer.phone_primary == data["phone_primary"],
                Farmer.id != farmer_id,
                Farmer.deleted_at.is_(None),
            )
            .first()
        )
        if phone_conflict:
            raise ConflictError("Farmer with this phone already exists")

    for field, value in data.items():
        setattr(row, field, value)
    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_id=row.id,
        before=before,
        after=data,
        client=client,
        summary=f"Farmer updated: {row.full_name}",
    )
    db.commit()
    db.refresh(row)
    return row


def delete_farmer(
    db: Session,
    org_id: UUID,
    farmer_id: UUID,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> None:
    row = get_farmer(db, org_id, farmer_id)
    name = row.full_name
    code = row.farmer_code
    _soft_delete(row, actor_user_id)
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_id=row.id,
        before={"farmer_code": code, "full_name": name},
        client=client,
        summary=f"Farmer deleted: {name}",
    )
    db.commit()


def village_name_map(db: Session, farmers: list[Farmer]) -> dict[UUID, str]:
    return _village_names(db, {f.village_id for f in farmers})


def farmer_outstanding(db: Session, org_id: UUID, farmer_id: UUID) -> Decimal:
    row = (
        db.query(FarmerLedgerEntry.balance_after)
        .filter(FarmerLedgerEntry.org_id == org_id, FarmerLedgerEntry.farmer_id == farmer_id)
        .order_by(FarmerLedgerEntry.entry_date.desc(), FarmerLedgerEntry.posted_at.desc())
        .first()
    )
    return row[0] if row else _ZERO


def _bank_account_response(row: FarmerBankAccount) -> BankAccountResponse:
    account_number = decrypt_value(row.account_number_encrypted)
    return BankAccountResponse(
        id=row.id,
        account_holder_name=row.account_holder_name,
        bank_name=row.bank_name,
        branch=row.branch,
        ifsc=row.ifsc,
        account_number_masked=mask_account_number(account_number),
        is_primary=row.is_primary,
    )


def list_bank_accounts(db: Session, org_id: UUID, farmer_id: UUID) -> list[BankAccountResponse]:
    get_farmer(db, org_id, farmer_id)
    rows = (
        db.query(FarmerBankAccount)
        .filter(
            FarmerBankAccount.org_id == org_id,
            FarmerBankAccount.farmer_id == farmer_id,
            FarmerBankAccount.deleted_at.is_(None),
        )
        .order_by(FarmerBankAccount.is_primary.desc(), FarmerBankAccount.created_at)
        .all()
    )
    return [_bank_account_response(row) for row in rows]


def _clear_primary_bank_accounts(
    db: Session, org_id: UUID, farmer_id: UUID, *, exclude_id: UUID | None = None
) -> None:
    q = db.query(FarmerBankAccount).filter(
        FarmerBankAccount.org_id == org_id,
        FarmerBankAccount.farmer_id == farmer_id,
        FarmerBankAccount.is_primary.is_(True),
        FarmerBankAccount.deleted_at.is_(None),
    )
    if exclude_id:
        q = q.filter(FarmerBankAccount.id != exclude_id)
    for row in q.all():
        row.is_primary = False


def create_bank_account(
    db: Session,
    org_id: UUID,
    farmer_id: UUID,
    payload: BankAccountCreateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> BankAccountResponse:
    get_farmer(db, org_id, farmer_id)
    if payload.is_primary:
        _clear_primary_bank_accounts(db, org_id, farmer_id)
    row = FarmerBankAccount(
        org_id=org_id,
        farmer_id=farmer_id,
        account_holder_name=payload.account_holder_name,
        bank_name=payload.bank_name,
        branch=payload.branch,
        ifsc=payload.ifsc.upper(),
        account_number_encrypted=encrypt_value(payload.account_number),
        is_primary=payload.is_primary,
        created_by=actor_user_id,
        updated_by=actor_user_id,
    )
    db.add(row)
    db.flush()
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_id=farmer_id,
        after={"bank_account_id": str(row.id), "bank_name": row.bank_name},
        client=client,
        summary="Bank account added for farmer",
    )
    db.commit()
    db.refresh(row)
    return _bank_account_response(row)


def update_bank_account(
    db: Session,
    org_id: UUID,
    farmer_id: UUID,
    account_id: UUID,
    payload: BankAccountUpdateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> BankAccountResponse:
    get_farmer(db, org_id, farmer_id)
    row = (
        db.query(FarmerBankAccount)
        .filter(
            FarmerBankAccount.id == account_id,
            FarmerBankAccount.org_id == org_id,
            FarmerBankAccount.farmer_id == farmer_id,
            FarmerBankAccount.deleted_at.is_(None),
        )
        .first()
    )
    if row is None:
        raise NotFoundError("Bank account not found")

    data = payload.model_dump(exclude_unset=True)
    account_number = data.pop("account_number", None)
    if account_number is not None:
        row.account_number_encrypted = encrypt_value(account_number)
    if data.get("is_primary"):
        _clear_primary_bank_accounts(db, org_id, farmer_id, exclude_id=account_id)
    if "ifsc" in data and data["ifsc"] is not None:
        data["ifsc"] = data["ifsc"].upper()
    for field, value in data.items():
        setattr(row, field, value)
    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_id=farmer_id,
        after={"bank_account_id": str(row.id)},
        client=client,
        summary="Farmer bank account updated",
    )
    db.commit()
    db.refresh(row)
    return _bank_account_response(row)


def delete_bank_account(
    db: Session,
    org_id: UUID,
    farmer_id: UUID,
    account_id: UUID,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> None:
    get_farmer(db, org_id, farmer_id)
    row = (
        db.query(FarmerBankAccount)
        .filter(
            FarmerBankAccount.id == account_id,
            FarmerBankAccount.org_id == org_id,
            FarmerBankAccount.farmer_id == farmer_id,
            FarmerBankAccount.deleted_at.is_(None),
        )
        .first()
    )
    if row is None:
        raise NotFoundError("Bank account not found")
    _soft_delete(row, actor_user_id)
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_id=farmer_id,
        before={"bank_account_id": str(row.id)},
        client=client,
        summary="Farmer bank account deleted",
    )
    db.commit()


def list_land_parcels(db: Session, org_id: UUID, farmer_id: UUID) -> list[LandParcelResponse]:
    get_farmer(db, org_id, farmer_id)
    rows = (
        db.query(FarmerLandParcel)
        .filter(
            FarmerLandParcel.org_id == org_id,
            FarmerLandParcel.farmer_id == farmer_id,
            FarmerLandParcel.deleted_at.is_(None),
        )
        .order_by(FarmerLandParcel.survey_number)
        .all()
    )
    return [LandParcelResponse.model_validate(row) for row in rows]


def create_land_parcel(
    db: Session,
    org_id: UUID,
    farmer_id: UUID,
    payload: LandParcelCreateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> LandParcelResponse:
    get_farmer(db, org_id, farmer_id)
    row = FarmerLandParcel(
        org_id=org_id,
        farmer_id=farmer_id,
        created_by=actor_user_id,
        updated_by=actor_user_id,
        **payload.model_dump(),
    )
    db.add(row)
    db.flush()
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_id=farmer_id,
        after={"land_parcel_id": str(row.id), "survey_number": row.survey_number},
        client=client,
        summary=f"Land parcel added: {row.survey_number}",
    )
    db.commit()
    db.refresh(row)
    return LandParcelResponse.model_validate(row)


def update_land_parcel(
    db: Session,
    org_id: UUID,
    farmer_id: UUID,
    parcel_id: UUID,
    payload: LandParcelUpdateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> LandParcelResponse:
    get_farmer(db, org_id, farmer_id)
    row = (
        db.query(FarmerLandParcel)
        .filter(
            FarmerLandParcel.id == parcel_id,
            FarmerLandParcel.org_id == org_id,
            FarmerLandParcel.farmer_id == farmer_id,
            FarmerLandParcel.deleted_at.is_(None),
        )
        .first()
    )
    if row is None:
        raise NotFoundError("Land parcel not found")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(row, field, value)
    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_id=farmer_id,
        after={"land_parcel_id": str(row.id)},
        client=client,
        summary="Farmer land parcel updated",
    )
    db.commit()
    db.refresh(row)
    return LandParcelResponse.model_validate(row)


def delete_land_parcel(
    db: Session,
    org_id: UUID,
    farmer_id: UUID,
    parcel_id: UUID,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> None:
    get_farmer(db, org_id, farmer_id)
    row = (
        db.query(FarmerLandParcel)
        .filter(
            FarmerLandParcel.id == parcel_id,
            FarmerLandParcel.org_id == org_id,
            FarmerLandParcel.farmer_id == farmer_id,
            FarmerLandParcel.deleted_at.is_(None),
        )
        .first()
    )
    if row is None:
        raise NotFoundError("Land parcel not found")
    _soft_delete(row, actor_user_id)
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_id=farmer_id,
        before={"land_parcel_id": str(row.id)},
        client=client,
        summary="Farmer land parcel deleted",
    )
    db.commit()
