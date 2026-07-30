from __future__ import annotations

import re
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.core.client_context import ClientContext
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.modules.farmers.models import Farmer
from app.modules.farmer_payments.models import FarmerPaymentAllocation
from app.modules.master_data.models import CropType, Village
from app.modules.platform.models import Buyer, CropPriceRule
from app.shared.locale import pick_display
from app.modules.procurements.models import FarmerLedgerEntry, Procurement, ProcurementBagEntry, ProcurementDeduction
from app.modules.procurements.schemas import (
    CANCELLABLE_STATUSES,
    DEFAULT_PER_BAG_DEDUCTION_KG,
    DEFAULT_SPOT_DEDUCTION_PER_QUINTAL,
    ProcurementCalculateRequest,
    ProcurementCalculateResponse,
    ProcurementCancelRequest,
    ProcurementCreateRequest,
    ProcurementDeductionInput,
    ProcurementFieldEntryRequest,
    ProcurementProfitSummary,
    ProcurementReverseRequest,
    ProcurementUpdateRequest,
    WeighmentRequest,
)
from app.modules.users.models import User
from app.shared.procurement_notes import moisture_pct_from_notes, rate_per_quintal_from_notes
from app.shared.services.audit import write_activity_feed, write_audit_log


def _notify_farmer_summary(db: Session, row: Procurement, *, actor_user_id: UUID) -> None:
    try:
        from app.modules.devices.service import notify_farmer_procurement_summary

        notify_farmer_procurement_summary(
            db,
            org_id=row.org_id,
            procurement=row,
            actor_user_id=actor_user_id,
        )
    except Exception:
        pass


def _viewer_role_code(user: User) -> str | None:
    role = getattr(user, "role", None)
    return role.code if role is not None else None


def resolve_farmer_list_filter(user: User, farmer_id: UUID | None) -> UUID | None:
    """FARMER role may only list their own tickets; staff may filter freely."""
    if _viewer_role_code(user) == "FARMER":
        if user.farmer_id is None:
            raise ForbiddenError("Farmer account is not linked to a farmer profile")
        if farmer_id is not None and farmer_id != user.farmer_id:
            raise ForbiddenError("Cannot view other farmers' procurements")
        return user.farmer_id
    return farmer_id


def assert_farmer_can_view_procurement(user: User, procurement: Procurement) -> None:
    if _viewer_role_code(user) != "FARMER":
        return
    if user.farmer_id is None:
        raise ForbiddenError("Farmer account is not linked to a farmer profile")
    if procurement.farmer_id != user.farmer_id:
        raise ForbiddenError("Procurement not found")


def calculate_procurement_preview(payload: ProcurementCalculateRequest) -> ProcurementCalculateResponse:
    per_bag = (
        payload.per_bag_deduction_kg
        if payload.per_bag_deduction_kg is not None
        else DEFAULT_PER_BAG_DEDUCTION_KG
    )
    spot_rate = (
        payload.spot_deduction_per_quintal
        if payload.spot_deduction_per_quintal is not None
        else DEFAULT_SPOT_DEDUCTION_PER_QUINTAL
    )
    gross_weight = _weight(Decimal(payload.bag_count) * payload.weight_per_bag_kg)
    bag_deduction, net_weight = compute_net_weight(
        gross_weight, payload.tare_weight_kg, payload.bag_count, per_bag
    )
    gross_amount, line_deduction, spot_deduction, net_amount = compute_amounts(
        net_weight,
        payload.rate_per_quintal,
        payload.line_deduction_amount,
        is_spot_payment=payload.is_spot_payment,
        spot_deduction_per_quintal=spot_rate,
    )
    return ProcurementCalculateResponse(
        gross_weight_kg=gross_weight,
        bag_weight_deduction_kg=bag_deduction,
        net_weight_kg=net_weight,
        net_quintals=_weight(net_weight / _QUINTAL_KG),
        gross_amount=gross_amount,
        line_deduction_amount=line_deduction,
        spot_deduction_amount=spot_deduction,
        net_amount=net_amount,
        moisture_pct=payload.moisture_pct,
    )


def _notify_status(db: Session, row: Procurement, actor_user_id: UUID) -> None:
    try:
        from app.modules.devices.service import notify_procurement_status

        notify_procurement_status(
            db,
            org_id=row.org_id,
            procurement_id=row.id,
            procurement_number=row.procurement_number,
            status=row.status,
            village_id=row.village_id,
            created_by=row.created_by,
            actor_user_id=actor_user_id,
            procurement_date=row.procurement_date,
        )
    except Exception:
        # Push must not fail the business transaction
        pass


_PROCUREMENT_NUMBER_PREFIX = "PR-"
_QUINTAL_KG = Decimal("100")
_ZERO = Decimal("0")
_TWOPLACES = Decimal("0.01")
_THREEPLACES = Decimal("0.001")
_PAYMENT_TERM_DAYS = {
    "one_week": 7,
    "10_days": 10,
    "2_weeks": 14,
    "20_days": 20,
}

ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "draft": frozenset({"pending_weighment", "cancelled"}),
    "pending_weighment": frozenset({"weighed", "cancelled"}),
    "weighed": frozenset({"priced", "cancelled"}),
    "priced": frozenset({"confirmed"}),
    "confirmed": frozenset({"reversed"}),
}


def can_transition(current: str, target: str) -> bool:
    return target in ALLOWED_TRANSITIONS.get(current, frozenset())


def _money(value: Decimal) -> Decimal:
    return value.quantize(_TWOPLACES, rounding=ROUND_HALF_UP)


def _weight(value: Decimal) -> Decimal:
    return value.quantize(_THREEPLACES, rounding=ROUND_HALF_UP)


def _next_procurement_number(db: Session, org_id: UUID) -> str:
    rows = (
        db.query(Procurement.procurement_number)
        .filter(
            Procurement.org_id == org_id,
            Procurement.procurement_number.like(f"{_PROCUREMENT_NUMBER_PREFIX}%"),
        )
        .all()
    )
    max_seq = 0
    for (code,) in rows:
        match = re.match(rf"^{re.escape(_PROCUREMENT_NUMBER_PREFIX)}(\d+)$", code or "")
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return f"{_PROCUREMENT_NUMBER_PREFIX}{max_seq + 1:04d}"


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
        entity_type="procurement",
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
            entity_type="procurement",
            entity_id=entity_id,
            device_id=client.device_id if client else None,
            client_type=client.client_type if client else None,
        )


def _get_procurement(
    db: Session,
    org_id: UUID,
    procurement_id: UUID,
    procurement_date: date,
) -> Procurement:
    row = (
        db.query(Procurement)
        .options(joinedload(Procurement.deductions), joinedload(Procurement.bag_entries))
        .filter(
            Procurement.id == procurement_id,
            Procurement.procurement_date == procurement_date,
            Procurement.org_id == org_id,
            Procurement.deleted_at.is_(None),
        )
        .first()
    )
    if row is None:
        raise NotFoundError("Procurement not found")
    return row


def _validate_farmer(db: Session, org_id: UUID, farmer_id: UUID) -> Farmer:
    row = (
        db.query(Farmer)
        .filter(Farmer.id == farmer_id, Farmer.org_id == org_id, Farmer.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Farmer not found")
    return row


def _validate_village(db: Session, org_id: UUID, village_id: UUID) -> Village:
    row = (
        db.query(Village)
        .filter(Village.id == village_id, Village.org_id == org_id, Village.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Village not found")
    return row


def _validate_crop_type(db: Session, org_id: UUID, crop_type_id: UUID) -> CropType:
    row = (
        db.query(CropType)
        .filter(CropType.id == crop_type_id, CropType.org_id == org_id, CropType.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Crop type not found")
    return row


def _validate_buyer(db: Session, org_id: UUID, buyer_id: UUID) -> Buyer:
    row = (
        db.query(Buyer)
        .filter(
            Buyer.id == buyer_id,
            Buyer.org_id == org_id,
            Buyer.deleted_at.is_(None),
            Buyer.is_active.is_(True),
        )
        .first()
    )
    if row is None:
        raise NotFoundError("Buyer not found")
    return row


def resolve_expected_payment_date(
    procurement_date: date,
    payment_terms: str | None,
    expected_payment_date: date | None = None,
) -> date | None:
    if expected_payment_date is not None:
        return expected_payment_date
    if payment_terms is None or payment_terms == "custom":
        return None
    days = _PAYMENT_TERM_DAYS.get(payment_terms)
    if days is None:
        return None
    return procurement_date + timedelta(days=days)


def resolve_rate_per_quintal(
    db: Session,
    org_id: UUID,
    crop_type_id: UUID,
    village_id: UUID,
    as_of: date,
) -> Decimal:
    rule = (
        db.query(CropPriceRule)
        .filter(
            CropPriceRule.org_id == org_id,
            CropPriceRule.crop_type_id == crop_type_id,
            CropPriceRule.is_active.is_(True),
            CropPriceRule.deleted_at.is_(None),
            CropPriceRule.effective_from <= as_of,
            (CropPriceRule.effective_to.is_(None)) | (CropPriceRule.effective_to >= as_of),
            (CropPriceRule.village_id == village_id) | (CropPriceRule.village_id.is_(None)),
        )
        .order_by(CropPriceRule.village_id.is_(None).asc(), CropPriceRule.effective_from.desc())
        .first()
    )
    if rule is None:
        raise NotFoundError("No active crop price rule for this crop and date")
    return rule.rate_per_quintal


def compute_bag_weight_deduction(bag_count: int, per_bag_deduction_kg: Decimal) -> Decimal:
    """Total weight (kg) deducted for bags (kata) = bag_count * per_bag_deduction_kg."""
    return _weight(Decimal(bag_count) * per_bag_deduction_kg)


def compute_net_weight(
    gross_weight_kg: Decimal,
    tare_weight_kg: Decimal,
    bag_count: int,
    per_bag_deduction_kg: Decimal,
) -> tuple[Decimal, Decimal]:
    """Return (bag_weight_deduction_kg, net_weight_kg).

    net_weight = gross - tare - (bag_count * per_bag_deduction_kg)
    """
    bag_weight_deduction = compute_bag_weight_deduction(bag_count, per_bag_deduction_kg)
    net_weight = _weight(gross_weight_kg - tare_weight_kg - bag_weight_deduction)
    return bag_weight_deduction, net_weight


def compute_spot_deduction_amount(
    net_weight_kg: Decimal,
    is_spot_payment: bool,
    spot_deduction_per_quintal: Decimal,
) -> Decimal:
    """Cash discount when farmer accepts 100% payment on spot: net_quintals × rate."""
    if not is_spot_payment or spot_deduction_per_quintal <= _ZERO:
        return _ZERO
    net_quintals = net_weight_kg / _QUINTAL_KG
    return _money(net_quintals * spot_deduction_per_quintal)


def compute_amounts(
    net_weight_kg: Decimal,
    rate_per_quintal: Decimal,
    line_deduction_amount: Decimal,
    *,
    is_spot_payment: bool = False,
    spot_deduction_per_quintal: Decimal = DEFAULT_SPOT_DEDUCTION_PER_QUINTAL,
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """Return (gross_amount, line_deduction_amount, spot_deduction_amount, net_amount)."""
    gross_amount = _money((net_weight_kg / _QUINTAL_KG) * rate_per_quintal)
    line_deduction_amount = _money(line_deduction_amount)
    spot_deduction_amount = compute_spot_deduction_amount(
        net_weight_kg, is_spot_payment, spot_deduction_per_quintal
    )
    net_amount = _money(gross_amount - line_deduction_amount - spot_deduction_amount)
    if net_amount < _ZERO:
        raise ConflictError("Deductions exceed gross amount")
    return gross_amount, line_deduction_amount, spot_deduction_amount, net_amount


def compute_profit_summary(procurement: Procurement) -> ProcurementProfitSummary | None:
    """Buyer margin from weight kata + spot discount. Requires priced weights/rate."""
    if procurement.rate_per_quintal <= _ZERO or procurement.gross_weight_kg <= _ZERO:
        return None
    rate = procurement.rate_per_quintal
    weight_deduction_kg = compute_bag_weight_deduction(
        procurement.bag_count, procurement.per_bag_deduction_kg
    )
    weight_quintals = weight_deduction_kg / _QUINTAL_KG
    weight_profit = _money(weight_quintals * rate)
    spot_amount = procurement.spot_deduction_amount
    gross_quintals = _weight(procurement.gross_weight_kg / _QUINTAL_KG)
    net_quintals = _weight(procurement.net_weight_kg / _QUINTAL_KG)
    return ProcurementProfitSummary(
        gross_quintals=gross_quintals,
        net_quintals=net_quintals,
        weight_deduction_kg=weight_deduction_kg,
        weight_deduction_profit_amount=weight_profit,
        spot_deduction_amount=spot_amount,
        total_profit_amount=_money(weight_profit + spot_amount),
    )


def _sum_deductions(procurement: Procurement) -> Decimal:
    return _money(sum((d.amount for d in procurement.deductions), _ZERO))


def _sync_amounts(procurement: Procurement) -> None:
    gross_amount, line_deduction, spot_deduction, net_amount = compute_amounts(
        procurement.net_weight_kg,
        procurement.rate_per_quintal,
        _sum_deductions(procurement),
        is_spot_payment=procurement.is_spot_payment,
        spot_deduction_per_quintal=procurement.spot_deduction_per_quintal,
    )
    procurement.gross_amount = gross_amount
    procurement.deduction_amount = line_deduction
    procurement.spot_deduction_amount = spot_deduction
    procurement.net_amount = net_amount


def _latest_ledger_balance(db: Session, org_id: UUID, farmer_id: UUID) -> Decimal:
    row = (
        db.query(FarmerLedgerEntry.balance_after)
        .filter(FarmerLedgerEntry.org_id == org_id, FarmerLedgerEntry.farmer_id == farmer_id)
        .order_by(FarmerLedgerEntry.entry_date.desc(), FarmerLedgerEntry.posted_at.desc())
        .first()
    )
    return row[0] if row else _ZERO


def _post_ledger_entry(
    db: Session,
    *,
    org_id: UUID,
    farmer_id: UUID,
    entry_date: date,
    entry_type: str,
    reference_id: UUID,
    debit: Decimal,
    credit: Decimal,
    description: str,
    posted_by: UUID,
    reversal_of_id: UUID | None = None,
) -> FarmerLedgerEntry:
    balance_after = _money(_latest_ledger_balance(db, org_id, farmer_id) + debit - credit)
    row = FarmerLedgerEntry(
        org_id=org_id,
        farmer_id=farmer_id,
        entry_date=entry_date,
        entry_type=entry_type,
        reference_type="procurement",
        reference_id=reference_id,
        debit=debit,
        credit=credit,
        balance_after=balance_after,
        description=description,
        reversal_of_id=reversal_of_id,
        posted_at=datetime.now(UTC),
        posted_by=posted_by,
    )
    db.add(row)
    db.flush()
    return row


def _transition(procurement: Procurement, target: str) -> None:
    if not can_transition(procurement.status, target):
        raise ConflictError(f"Cannot transition from {procurement.status} to {target}")
    procurement.status = target


def _replace_bag_entries(
    db: Session,
    *,
    org_id: UUID,
    procurement: Procurement,
    weights: list[Decimal],
    actor_user_id: UUID,
) -> None:
    db.query(ProcurementBagEntry).filter(
        ProcurementBagEntry.procurement_id == procurement.id,
        ProcurementBagEntry.procurement_date == procurement.procurement_date,
        ProcurementBagEntry.org_id == org_id,
    ).delete(synchronize_session=False)
    for idx, weight in enumerate(weights, start=1):
        db.add(
            ProcurementBagEntry(
                org_id=org_id,
                procurement_id=procurement.id,
                procurement_date=procurement.procurement_date,
                bag_number=idx,
                weight_kg=_weight(weight),
                created_by=actor_user_id,
                updated_by=actor_user_id,
            )
        )


def _apply_weighment_values(
    db: Session,
    *,
    org_id: UUID,
    row: Procurement,
    payload: WeighmentRequest,
    actor_user_id: UUID,
) -> Decimal:
    gross = _weight(payload.resolved_gross_weight_kg())
    tare = _weight(payload.tare_weight_kg)
    bag_weights = payload.bag_weights_kg
    effective_bag_count = (
        len(bag_weights)
        if bag_weights
        else (payload.bag_count if payload.bag_count is not None else row.bag_count)
    )
    effective_per_bag = (
        payload.per_bag_deduction_kg if payload.per_bag_deduction_kg is not None else row.per_bag_deduction_kg
    )
    bag_weight_deduction, net_weight = compute_net_weight(gross, tare, effective_bag_count, effective_per_bag)
    if net_weight <= _ZERO:
        raise ConflictError("Net weight must be positive after tare and per-bag weight deductions")

    row.gross_weight_kg = gross
    row.tare_weight_kg = tare
    row.net_weight_kg = net_weight
    if payload.moisture_pct is not None:
        row.moisture_pct = payload.moisture_pct
    row.bag_count = effective_bag_count
    row.per_bag_deduction_kg = effective_per_bag
    row.updated_by = actor_user_id

    if bag_weights:
        _replace_bag_entries(
            db,
            org_id=org_id,
            procurement=row,
            weights=bag_weights,
            actor_user_id=actor_user_id,
        )
    return bag_weight_deduction


def _advance_to_weighed(row: Procurement) -> str:
    before_status = row.status
    if row.status == "draft":
        _transition(row, "pending_weighment")
    if row.status == "pending_weighment":
        _transition(row, "weighed")
    return before_status


def _maybe_apply_price_after_weigh(
    db: Session,
    org_id: UUID,
    row: Procurement,
    *,
    rate_override: Decimal | None = None,
) -> None:
    rate = rate_override
    if rate is None or rate <= _ZERO:
        rate = rate_per_quintal_from_notes(row.notes)
    if rate is None or rate <= _ZERO:
        rate = resolve_rate_per_quintal(db, org_id, row.crop_type_id, row.village_id, row.procurement_date)
    if rate <= _ZERO:
        return
    row.rate_per_quintal = rate
    _sync_amounts(row)
    if can_transition(row.status, "priced"):
        _transition(row, "priced")


def _apply_intake_on_create(
    db: Session,
    org_id: UUID,
    row: Procurement,
    payload: ProcurementCreateRequest,
    actor_user_id: UUID,
) -> None:
    if not payload.gross_weight_kg and not payload.bag_weights_kg:
        return

    before_status = _advance_to_weighed(row)
    moisture = payload.moisture_pct
    if moisture is None:
        moisture = moisture_pct_from_notes(payload.notes)

    weighment = WeighmentRequest(
        gross_weight_kg=payload.gross_weight_kg,
        tare_weight_kg=payload.tare_weight_kg or Decimal("0"),
        moisture_pct=moisture,
        bag_count=payload.bag_count or None,
        per_bag_deduction_kg=row.per_bag_deduction_kg,
        bag_weights_kg=payload.bag_weights_kg,
    )
    bag_weight_deduction = _apply_weighment_values(
        db, org_id=org_id, row=row, payload=weighment, actor_user_id=actor_user_id
    )
    _maybe_apply_price_after_weigh(db, org_id, row, rate_override=payload.rate_per_quintal)
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="WEIGH",
        entity_id=row.id,
        before={"status": before_status},
        after={
            "status": row.status,
            "net_weight_kg": str(row.net_weight_kg),
            "bag_count": row.bag_count,
            "bag_weight_deduction_kg": str(bag_weight_deduction),
            "intake_on_create": True,
        },
        client=None,
        summary=f"Intake weighment on create: {row.procurement_number}",
    )


def list_procurements(
    db: Session,
    org_id: UUID,
    *,
    page: int,
    page_size: int,
    farmer_id: UUID | None = None,
    village_id: UUID | None = None,
    crop_type_id: UUID | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    viewer: User | None = None,
) -> tuple[list[Procurement], int]:
    if viewer is not None:
        farmer_id = resolve_farmer_list_filter(viewer, farmer_id)
    q = db.query(Procurement).filter(Procurement.org_id == org_id, Procurement.deleted_at.is_(None))
    if farmer_id:
        q = q.filter(Procurement.farmer_id == farmer_id)
    if village_id:
        q = q.filter(Procurement.village_id == village_id)
    if crop_type_id:
        q = q.filter(Procurement.crop_type_id == crop_type_id)
    if status:
        q = q.filter(Procurement.status == status)
    if date_from:
        q = q.filter(Procurement.procurement_date >= date_from)
    if date_to:
        q = q.filter(Procurement.procurement_date <= date_to)
    q = q.order_by(Procurement.procurement_date.desc(), Procurement.procurement_number.desc())
    total = q.count()
    items = q.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_procurement(
    db: Session,
    org_id: UUID,
    procurement_id: UUID,
    procurement_date: date,
    *,
    viewer: User | None = None,
) -> Procurement:
    row = _get_procurement(db, org_id, procurement_id, procurement_date)
    if viewer is not None:
        assert_farmer_can_view_procurement(viewer, row)
    return row


def create_field_entry(
    db: Session,
    org_id: UUID,
    payload: ProcurementFieldEntryRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
    *,
    idempotency_key: str | None = None,
) -> Procurement:
    """Mobile manager flow: draft → weigh → price → optional confirm in one request."""
    create_payload = ProcurementCreateRequest(
        farmer_id=payload.farmer_id,
        crop_type_id=payload.crop_type_id,
        village_id=payload.village_id,
        procurement_date=payload.procurement_date,
        bag_count=payload.bag_count,
        per_bag_deduction_kg=payload.per_bag_deduction_kg,
        is_spot_payment=payload.is_spot_payment,
        spot_deduction_per_quintal=payload.spot_deduction_per_quintal,
        buyer_id=payload.buyer_id,
        payment_terms=payload.payment_terms,
        payment_terms_custom=payload.payment_terms_custom,
        expected_payment_date=payload.expected_payment_date,
        notes=payload.notes,
        weight_per_bag_kg=payload.weight_per_bag_kg,
    )
    row = create_procurement(
        db, org_id, create_payload, actor_user_id, client, idempotency_key=idempotency_key
    )

    submit_procurement(db, org_id, row.id, row.procurement_date, actor_user_id, client)

    gross_weight = _weight(Decimal(payload.bag_count) * payload.weight_per_bag_kg)
    weigh_payload = WeighmentRequest(
        gross_weight_kg=gross_weight,
        tare_weight_kg=payload.tare_weight_kg,
        moisture_pct=payload.moisture_pct,
        bag_count=payload.bag_count,
        per_bag_deduction_kg=payload.per_bag_deduction_kg,
    )
    record_weighment(
        db, org_id, row.id, row.procurement_date, weigh_payload, actor_user_id, client
    )
    row = _get_procurement(db, org_id, row.id, row.procurement_date)

    for deduction in payload.line_deductions:
        add_deduction(db, org_id, row.id, row.procurement_date, deduction, actor_user_id, client)
        row = _get_procurement(db, org_id, row.id, row.procurement_date)

    apply_price(
        db,
        org_id,
        row.id,
        row.procurement_date,
        actor_user_id,
        client,
        rate_per_quintal=payload.rate_per_quintal,
    )
    row = _get_procurement(db, org_id, row.id, row.procurement_date)

    if payload.auto_confirm:
        confirm_procurement(db, org_id, row.id, row.procurement_date, actor_user_id, client)
        row = _get_procurement(db, org_id, row.id, row.procurement_date)
    elif payload.notify_farmer:
        _notify_farmer_summary(db, row, actor_user_id=actor_user_id)
    return row


def create_procurement(
    db: Session,
    org_id: UUID,
    payload: ProcurementCreateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
    *,
    idempotency_key: str | None = None,
) -> Procurement:
    if idempotency_key:
        existing = (
            db.query(Procurement)
            .filter(Procurement.org_id == org_id, Procurement.idempotency_key == idempotency_key)
            .first()
        )
        if existing:
            return existing

    _validate_farmer(db, org_id, payload.farmer_id)
    _validate_village(db, org_id, payload.village_id)
    _validate_crop_type(db, org_id, payload.crop_type_id)
    if payload.buyer_id is not None:
        _validate_buyer(db, org_id, payload.buyer_id)
    if payload.payment_terms == "custom" and not (payload.payment_terms_custom or "").strip():
        raise ConflictError("payment_terms_custom is required when payment_terms is custom")

    expected = resolve_expected_payment_date(
        payload.procurement_date,
        payload.payment_terms,
        payload.expected_payment_date,
    )

    row = Procurement(
        org_id=org_id,
        procurement_number=_next_procurement_number(db, org_id),
        status="draft",
        bag_count=payload.bag_count,
        per_bag_deduction_kg=(
            payload.per_bag_deduction_kg
            if payload.per_bag_deduction_kg is not None
            else DEFAULT_PER_BAG_DEDUCTION_KG
        ),
        is_spot_payment=payload.is_spot_payment,
        spot_deduction_per_quintal=(
            payload.spot_deduction_per_quintal
            if payload.spot_deduction_per_quintal is not None
            else DEFAULT_SPOT_DEDUCTION_PER_QUINTAL
        ),
        spot_deduction_amount=_ZERO,
        gross_weight_kg=_ZERO,
        net_weight_kg=_ZERO,
        rate_per_quintal=_ZERO,
        gross_amount=_ZERO,
        deduction_amount=_ZERO,
        net_amount=_ZERO,
        buyer_id=payload.buyer_id,
        payment_terms=payload.payment_terms,
        payment_terms_custom=payload.payment_terms_custom,
        expected_payment_date=expected,
        idempotency_key=idempotency_key,
        notes=payload.notes,
        weight_per_bag_kg=payload.weight_per_bag_kg,
        created_by=actor_user_id,
        updated_by=actor_user_id,
        farmer_id=payload.farmer_id,
        crop_type_id=payload.crop_type_id,
        village_id=payload.village_id,
        procurement_date=payload.procurement_date,
    )
    db.add(row)
    db.flush()
    _apply_intake_on_create(db, org_id, row, payload, actor_user_id)
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_id=row.id,
        after={
            "procurement_number": row.procurement_number,
            "status": row.status,
            "buyer_id": str(row.buyer_id) if row.buyer_id else None,
            "payment_terms": row.payment_terms,
        },
        client=client,
        summary=f"Procurement draft created: {row.procurement_number}",
    )
    db.commit()
    db.refresh(row)
    return row


def update_procurement(
    db: Session,
    org_id: UUID,
    procurement_id: UUID,
    procurement_date: date,
    payload: ProcurementUpdateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> Procurement:
    row = _get_procurement(db, org_id, procurement_id, procurement_date)
    if row.status in {"cancelled", "reversed"}:
        raise ConflictError(f"Cannot edit a {row.status} procurement")

    data = payload.model_dump(exclude_unset=True)
    # per_bag_deduction_kg is NOT NULL; ignore an explicit null so it keeps its value.
    if data.get("per_bag_deduction_kg") is None:
        data.pop("per_bag_deduction_kg", None)
    if "farmer_id" in data and data["farmer_id"] is not None:
        _validate_farmer(db, org_id, data["farmer_id"])
    if "village_id" in data and data["village_id"] is not None:
        _validate_village(db, org_id, data["village_id"])
    if "crop_type_id" in data and data["crop_type_id"] is not None:
        _validate_crop_type(db, org_id, data["crop_type_id"])
    if "buyer_id" in data and data["buyer_id"] is not None:
        _validate_buyer(db, org_id, data["buyer_id"])

    # A confirmed ticket has posted to the farmer ledger. Guard its financial integrity.
    if row.status == "confirmed":
        allocated = (
            db.query(FarmerPaymentAllocation)
            .filter(
                FarmerPaymentAllocation.org_id == org_id,
                FarmerPaymentAllocation.procurement_id == row.id,
            )
            .first()
        )
        if allocated is not None:
            raise ConflictError(
                "Cannot edit: a farmer payment is already allocated to this procurement. "
                "Reverse the payment first."
            )
        if (
            "farmer_id" in data
            and data["farmer_id"] is not None
            and data["farmer_id"] != row.farmer_id
        ):
            raise ConflictError(
                "Cannot change the farmer on a confirmed procurement; cancel and re-enter instead."
            )

    payment_terms = data.get("payment_terms", row.payment_terms)
    payment_terms_custom = data.get("payment_terms_custom", row.payment_terms_custom)
    if payment_terms == "custom" and not (payment_terms_custom or "").strip():
        raise ConflictError("payment_terms_custom is required when payment_terms is custom")

    old_net_amount = row.net_amount
    before = {"status": row.status, "farmer_id": str(row.farmer_id), "net_amount": str(old_net_amount)}
    for field, value in data.items():
        setattr(row, field, value)

    if "expected_payment_date" not in data and "payment_terms" in data:
        row.expected_payment_date = resolve_expected_payment_date(
            row.procurement_date,
            row.payment_terms,
            None,
        )

    # Recompute weights + payable for weighed/priced/confirmed tickets whose intake changed.
    if row.status in {"weighed", "priced", "confirmed"} and row.weight_per_bag_kg and row.weight_per_bag_kg > _ZERO:
        gross = _weight(Decimal(row.bag_count) * row.weight_per_bag_kg)
        _bag_ded, net = compute_net_weight(
            gross, row.tare_weight_kg or _ZERO, row.bag_count, row.per_bag_deduction_kg
        )
        if net <= _ZERO:
            raise ConflictError("Net weight must be positive after per-bag weight deductions")
        row.gross_weight_kg = gross
        row.net_weight_kg = net
        _sync_amounts(row)

    # Keep the immutable farmer ledger correct: reverse the old payable, post the new one.
    if row.status == "confirmed" and row.net_amount != old_net_amount:
        _readjust_ledger_on_edit(
            db, org_id=org_id, row=row, old_net_amount=old_net_amount, actor_user_id=actor_user_id
        )

    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_id=row.id,
        before=before,
        after=_audit_safe({**data, "net_amount": str(row.net_amount)}),
        client=client,
        summary=f"Procurement updated: {row.procurement_number}",
    )
    db.commit()
    db.refresh(row)
    return row


def _audit_safe(data: dict) -> dict:
    """Coerce audit payload values (Decimal/UUID/date) to JSON-serializable strings."""
    return {
        key: (str(value) if isinstance(value, (Decimal, UUID, date, datetime)) else value)
        for key, value in data.items()
    }


def _readjust_ledger_on_edit(
    db: Session,
    *,
    org_id: UUID,
    row: Procurement,
    old_net_amount: Decimal,
    actor_user_id: UUID,
) -> None:
    """Confirmed ticket edited: reverse the previously-owed amount and post the corrected one.

    The farmer ledger is append-only, so a value change is expressed as a reversing
    credit (old payable) plus a fresh debit (new payable); the running balance nets to
    the new payable.
    """
    original = (
        db.query(FarmerLedgerEntry)
        .filter(
            FarmerLedgerEntry.org_id == org_id,
            FarmerLedgerEntry.reference_type == "procurement",
            FarmerLedgerEntry.reference_id == row.id,
            FarmerLedgerEntry.debit > _ZERO,
        )
        .order_by(FarmerLedgerEntry.posted_at.desc())
        .first()
    )
    if old_net_amount > _ZERO:
        _post_ledger_entry(
            db,
            org_id=org_id,
            farmer_id=row.farmer_id,
            entry_date=row.procurement_date,
            entry_type="procurement_adjustment",
            reference_id=row.id,
            debit=_ZERO,
            credit=old_net_amount,
            description=f"Edit reversal of {row.procurement_number}",
            posted_by=actor_user_id,
            reversal_of_id=original.id if original else None,
        )
    if row.net_amount > _ZERO:
        _post_ledger_entry(
            db,
            org_id=org_id,
            farmer_id=row.farmer_id,
            entry_date=row.procurement_date,
            entry_type="procurement_adjustment",
            reference_id=row.id,
            debit=row.net_amount,
            credit=_ZERO,
            description=f"Edit adjustment of {row.procurement_number}",
            posted_by=actor_user_id,
        )


def submit_procurement(
    db: Session,
    org_id: UUID,
    procurement_id: UUID,
    procurement_date: date,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> Procurement:
    row = _get_procurement(db, org_id, procurement_id, procurement_date)
    before_status = row.status
    _transition(row, "pending_weighment")
    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="SUBMIT",
        entity_id=row.id,
        before={"status": before_status},
        after={"status": row.status},
        client=client,
        summary=f"Procurement submitted for weighment: {row.procurement_number}",
    )
    db.commit()
    db.refresh(row)
    _notify_status(db, row, actor_user_id)
    return row


def record_weighment(
    db: Session,
    org_id: UUID,
    procurement_id: UUID,
    procurement_date: date,
    payload: WeighmentRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> Procurement:
    row = _get_procurement(db, org_id, procurement_id, procurement_date)
    before_status = row.status
    _advance_to_weighed(row)

    bag_weight_deduction = _apply_weighment_values(
        db, org_id=org_id, row=row, payload=payload, actor_user_id=actor_user_id
    )

    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="WEIGH",
        entity_id=row.id,
        before={"status": before_status},
        after={
            "status": row.status,
            "net_weight_kg": str(row.net_weight_kg),
            "bag_count": row.bag_count,
            "per_bag_deduction_kg": str(row.per_bag_deduction_kg),
            "bag_weight_deduction_kg": str(bag_weight_deduction),
        },
        client=client,
        summary=f"Weighment recorded: {row.procurement_number}",
    )
    db.commit()
    db.refresh(row)
    _notify_status(db, row, actor_user_id)
    return row


def apply_price(
    db: Session,
    org_id: UUID,
    procurement_id: UUID,
    procurement_date: date,
    actor_user_id: UUID,
    client: ClientContext | None,
    *,
    rate_per_quintal: Decimal | None = None,
) -> Procurement:
    row = _get_procurement(db, org_id, procurement_id, procurement_date)
    before_status = row.status
    _transition(row, "priced")

    rate = (
        rate_per_quintal
        if rate_per_quintal is not None
        else resolve_rate_per_quintal(db, org_id, row.crop_type_id, row.village_id, row.procurement_date)
    )
    row.rate_per_quintal = rate
    _sync_amounts(row)
    row.updated_by = actor_user_id

    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="PRICE",
        entity_id=row.id,
        before={"status": before_status},
        after={
            "status": row.status,
            "rate_per_quintal": str(row.rate_per_quintal),
            "net_amount": str(row.net_amount),
        },
        client=client,
        summary=f"Price applied: {row.procurement_number}",
    )
    db.commit()
    db.refresh(row)
    _notify_status(db, row, actor_user_id)
    return row


def confirm_procurement(
    db: Session,
    org_id: UUID,
    procurement_id: UUID,
    procurement_date: date,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> Procurement:
    row = _get_procurement(db, org_id, procurement_id, procurement_date)
    if row.status == "confirmed":
        raise ConflictError("Procurement already confirmed")
    before_status = row.status
    _transition(row, "confirmed")

    if row.rate_per_quintal <= _ZERO or row.net_amount <= _ZERO:
        raise ConflictError("Procurement must be priced before confirmation")

    row.confirmed_at = datetime.now(UTC)
    row.confirmed_by = actor_user_id
    row.updated_by = actor_user_id

    _post_ledger_entry(
        db,
        org_id=org_id,
        farmer_id=row.farmer_id,
        entry_date=row.procurement_date,
        entry_type="procurement",
        reference_id=row.id,
        debit=row.net_amount,
        credit=_ZERO,
        description=f"Procurement {row.procurement_number}",
        posted_by=actor_user_id,
    )

    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CONFIRM",
        entity_id=row.id,
        before={"status": before_status},
        after={"status": row.status, "net_amount": str(row.net_amount)},
        client=client,
        summary=f"Procurement confirmed: {row.procurement_number}",
    )
    db.commit()
    db.refresh(row)
    _notify_status(db, row, actor_user_id)
    _notify_farmer_summary(db, row, actor_user_id=actor_user_id)
    return row


def cancel_procurement(
    db: Session,
    org_id: UUID,
    procurement_id: UUID,
    procurement_date: date,
    payload: ProcurementCancelRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> Procurement:
    row = _get_procurement(db, org_id, procurement_id, procurement_date)
    if row.status not in CANCELLABLE_STATUSES:
        raise ConflictError(f"Cannot cancel procurement in status {row.status}")

    before_status = row.status
    row.status = "cancelled"
    row.cancelled_at = datetime.now(UTC)
    row.cancellation_reason = payload.reason
    row.updated_by = actor_user_id

    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CANCEL",
        entity_id=row.id,
        before={"status": before_status},
        after={"status": row.status, "reason": payload.reason},
        client=client,
        summary=f"Procurement cancelled: {row.procurement_number}",
    )
    db.commit()
    db.refresh(row)
    _notify_status(db, row, actor_user_id)
    return row


def reverse_procurement(
    db: Session,
    org_id: UUID,
    procurement_id: UUID,
    procurement_date: date,
    payload: ProcurementReverseRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> Procurement:
    row = _get_procurement(db, org_id, procurement_id, procurement_date)
    before_status = row.status
    _transition(row, "reversed")

    original_entry = (
        db.query(FarmerLedgerEntry)
        .filter(
            FarmerLedgerEntry.org_id == org_id,
            FarmerLedgerEntry.reference_type == "procurement",
            FarmerLedgerEntry.reference_id == row.id,
            FarmerLedgerEntry.entry_type == "procurement",
            FarmerLedgerEntry.debit > _ZERO,
        )
        .order_by(FarmerLedgerEntry.posted_at.desc())
        .first()
    )
    if original_entry is None:
        raise ConflictError("No ledger entry found for this procurement")

    _post_ledger_entry(
        db,
        org_id=org_id,
        farmer_id=row.farmer_id,
        entry_date=row.procurement_date,
        entry_type="procurement_reversal",
        reference_id=row.id,
        debit=_ZERO,
        credit=row.net_amount,
        description=f"Reversal of {row.procurement_number}: {payload.reason}",
        posted_by=actor_user_id,
        reversal_of_id=original_entry.id,
    )

    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="REVERSE",
        entity_id=row.id,
        before={"status": before_status},
        after={"status": row.status, "reason": payload.reason},
        client=client,
        summary=f"Procurement reversed: {row.procurement_number}",
    )
    db.commit()
    db.refresh(row)
    _notify_status(db, row, actor_user_id)
    return row


def add_deduction(
    db: Session,
    org_id: UUID,
    procurement_id: UUID,
    procurement_date: date,
    payload: ProcurementDeductionInput,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> Procurement:
    row = _get_procurement(db, org_id, procurement_id, procurement_date)
    if row.status not in {"draft", "pending_weighment", "weighed"}:
        raise ConflictError("Deductions can only be added before pricing")

    deduction = ProcurementDeduction(
        org_id=org_id,
        procurement_id=row.id,
        procurement_date=row.procurement_date,
        **payload.model_dump(),
    )
    db.add(deduction)
    db.flush()
    row.deductions.append(deduction)

    if row.status == "weighed" and row.rate_per_quintal > _ZERO:
        _sync_amounts(row)

    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DEDUCTION",
        entity_id=row.id,
        after={"deduction_type": payload.deduction_type, "amount": str(payload.amount)},
        client=client,
        summary=f"Deduction added to {row.procurement_number}",
    )
    db.commit()
    db.refresh(row)
    return row


def related_names(
    db: Session,
    procurements: list[Procurement],
    locale: str = "en",
) -> tuple[dict[UUID, str], dict[UUID, str], dict[UUID, str], dict[UUID, str]]:
    farmer_ids = {p.farmer_id for p in procurements}
    village_ids = {p.village_id for p in procurements}
    crop_ids = {p.crop_type_id for p in procurements}
    buyer_ids = {p.buyer_id for p in procurements if p.buyer_id}

    farmers: dict[UUID, str] = {}
    if farmer_ids:
        for row in db.query(Farmer).filter(Farmer.id.in_(farmer_ids)).all():
            farmers[row.id] = pick_display(row.full_name, row.full_name_te, locale) or row.full_name
    villages: dict[UUID, str] = {}
    if village_ids:
        for row in db.query(Village).filter(Village.id.in_(village_ids)).all():
            villages[row.id] = pick_display(row.name, row.name_te, locale) or row.name
    crops: dict[UUID, str] = {}
    if crop_ids:
        for row in db.query(CropType).filter(CropType.id.in_(crop_ids)).all():
            crops[row.id] = pick_display(row.name, row.name_te, locale) or row.name
    buyers: dict[UUID, str] = {}
    if buyer_ids:
        for row in db.query(Buyer).filter(Buyer.id.in_(buyer_ids)).all():
            buyers[row.id] = pick_display(row.name, row.name_te, locale) or row.name
    return farmers, villages, crops, buyers
