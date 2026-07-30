from __future__ import annotations

import re
from datetime import UTC, date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.client_context import ClientContext
from app.core.exceptions import ConflictError, NotFoundError
from app.modules.farmers.models import Farmer
from app.modules.hamali.models import HamaliDailyEntry, HamaliWeeklyPayment, HamaliWorker
from app.modules.hamali.schemas import (
    DEFAULT_RATE_PER_BAG,
    HamaliDailyEntryCreateRequest,
    HamaliDailyEntryUpdateRequest,
    HamaliDailySummary,
    HamaliMeDailyLine,
    HamaliMeDailyResponse,
    HamaliMeFarmerSummary,
    HamaliMeSummaryResponse,
    HamaliWeeklyPaymentCreateRequest,
    HamaliWeeklyPaymentMarkPaidRequest,
    HamaliWorkerCreateRequest,
    HamaliWorkerUpdateRequest,
    HamaliWorkerWeekSummary,
    HamaliWeeklySummaryResponse,
    _UNSPECIFIED_FARMER_ID,
)
from app.modules.procurements.models import Procurement
from app.modules.users.models import User
from app.shared.services.audit import write_activity_feed, write_audit_log

_WORKER_CODE_PREFIX = "HML-"
_PAYMENT_NUMBER_PREFIX = "HWP-"
_ZERO = Decimal("0")
_TWOPLACES = Decimal("0.01")


def _money(value: Decimal) -> Decimal:
    return value.quantize(_TWOPLACES, rounding=ROUND_HALF_UP)


def week_bounds(week_start: date) -> tuple[date, date]:
    """Week runs Monday (inclusive) through Sunday (inclusive)."""
    return week_start, week_start + timedelta(days=6)


def monday_of(d: date) -> date:
    return d - timedelta(days=d.weekday())


def compute_entry_amounts(
    bags_lifted: int,
    rate_per_bag: Decimal,
    maintenance_amount: Decimal,
    tip_amount: Decimal,
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    labor = _money(Decimal(bags_lifted) * rate_per_bag)
    maintenance = _money(maintenance_amount)
    tip = _money(tip_amount)
    total = _money(labor + maintenance + tip)
    return labor, maintenance, tip, total


def _next_worker_code(db: Session, org_id: UUID) -> str:
    rows = (
        db.query(HamaliWorker.worker_code)
        .filter(
            HamaliWorker.org_id == org_id,
            HamaliWorker.worker_code.like(f"{_WORKER_CODE_PREFIX}%"),
            HamaliWorker.deleted_at.is_(None),
        )
        .all()
    )
    max_seq = 0
    for (code,) in rows:
        match = re.match(rf"^{re.escape(_WORKER_CODE_PREFIX)}(\d+)$", code or "")
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return f"{_WORKER_CODE_PREFIX}{max_seq + 1:04d}"


def _next_payment_number(db: Session, org_id: UUID) -> str:
    rows = (
        db.query(HamaliWeeklyPayment.payment_number)
        .filter(
            HamaliWeeklyPayment.org_id == org_id,
            HamaliWeeklyPayment.payment_number.like(f"{_PAYMENT_NUMBER_PREFIX}%"),
            HamaliWeeklyPayment.deleted_at.is_(None),
        )
        .all()
    )
    max_seq = 0
    for (num,) in rows:
        match = re.match(rf"^{re.escape(_PAYMENT_NUMBER_PREFIX)}(\d+)$", num or "")
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return f"{_PAYMENT_NUMBER_PREFIX}{max_seq + 1:04d}"


def _audit(
    db: Session,
    *,
    org_id: UUID,
    actor_user_id: UUID,
    action: str,
    entity_type: str,
    entity_id: UUID,
    after: dict | None = None,
    before: dict | None = None,
    client: ClientContext | None = None,
    summary: str | None = None,
) -> None:
    write_audit_log(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
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
            entity_type=entity_type,
            entity_id=entity_id,
            summary=summary,
        )


def _get_worker(db: Session, org_id: UUID, worker_id: UUID) -> HamaliWorker:
    row = (
        db.query(HamaliWorker)
        .filter(
            HamaliWorker.org_id == org_id,
            HamaliWorker.id == worker_id,
            HamaliWorker.deleted_at.is_(None),
        )
        .first()
    )
    if not row:
        raise NotFoundError("Hamali worker not found")
    return row


def _get_entry(db: Session, org_id: UUID, entry_id: UUID) -> HamaliDailyEntry:
    row = (
        db.query(HamaliDailyEntry)
        .filter(
            HamaliDailyEntry.org_id == org_id,
            HamaliDailyEntry.id == entry_id,
            HamaliDailyEntry.deleted_at.is_(None),
        )
        .first()
    )
    if not row:
        raise NotFoundError("Hamali daily entry not found")
    return row


def _get_weekly_payment(db: Session, org_id: UUID, payment_id: UUID) -> HamaliWeeklyPayment:
    row = (
        db.query(HamaliWeeklyPayment)
        .filter(
            HamaliWeeklyPayment.org_id == org_id,
            HamaliWeeklyPayment.id == payment_id,
            HamaliWeeklyPayment.deleted_at.is_(None),
        )
        .first()
    )
    if not row:
        raise NotFoundError("Hamali weekly payment not found")
    return row


def list_workers(
    db: Session,
    org_id: UUID,
    *,
    page: int,
    page_size: int,
    status: str | None = None,
    q: str | None = None,
) -> tuple[list[HamaliWorker], int]:
    query = db.query(HamaliWorker).filter(
        HamaliWorker.org_id == org_id,
        HamaliWorker.deleted_at.is_(None),
    )
    if status:
        query = query.filter(HamaliWorker.status == status)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            HamaliWorker.full_name.ilike(like)
            | HamaliWorker.worker_code.ilike(like)
            | HamaliWorker.phone.ilike(like)
        )
    total = query.count()
    items = (
        query.order_by(HamaliWorker.full_name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def create_worker(
    db: Session,
    org_id: UUID,
    payload: HamaliWorkerCreateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> HamaliWorker:
    row = HamaliWorker(
        org_id=org_id,
        worker_code=_next_worker_code(db, org_id),
        full_name=payload.full_name.strip(),
        full_name_te=payload.full_name_te,
        phone=payload.phone,
        default_rate_per_bag=payload.default_rate_per_bag or DEFAULT_RATE_PER_BAG,
        status="active",
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
        entity_type="hamali_worker",
        entity_id=row.id,
        after={"worker_code": row.worker_code, "full_name": row.full_name},
        client=client,
        summary=f"Hamali worker added: {row.full_name}",
    )
    db.commit()
    db.refresh(row)
    return row


def update_worker(
    db: Session,
    org_id: UUID,
    worker_id: UUID,
    payload: HamaliWorkerUpdateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> HamaliWorker:
    row = _get_worker(db, org_id, worker_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(row, field, value)
    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_type="hamali_worker",
        entity_id=row.id,
        after=data,
        client=client,
        summary=f"Hamali worker updated: {row.full_name}",
    )
    db.commit()
    db.refresh(row)
    return row


def delete_worker(
    db: Session,
    org_id: UUID,
    worker_id: UUID,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> None:
    row = _get_worker(db, org_id, worker_id)
    pending = (
        db.query(HamaliDailyEntry)
        .filter(
            HamaliDailyEntry.hamali_worker_id == worker_id,
            HamaliDailyEntry.payment_status == "pending",
            HamaliDailyEntry.deleted_at.is_(None),
        )
        .count()
    )
    if pending:
        raise ConflictError("Cannot delete worker with pending daily entries")
    row.deleted_at = datetime.now(UTC)
    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_type="hamali_worker",
        entity_id=row.id,
        client=client,
        summary=f"Hamali worker removed: {row.full_name}",
    )
    db.commit()


def worker_name_map(db: Session, worker_ids: set[UUID]) -> dict[UUID, HamaliWorker]:
    if not worker_ids:
        return {}
    rows = db.query(HamaliWorker).filter(HamaliWorker.id.in_(worker_ids)).all()
    return {r.id: r for r in rows}


def _summarize_entries(entries: list[HamaliDailyEntry]) -> HamaliDailySummary:
    total_bags = sum(e.bags_lifted for e in entries)
    return HamaliDailySummary(
        total_bags=total_bags,
        total_labor_amount=_money(sum((e.labor_amount for e in entries), _ZERO)),
        total_maintenance_amount=_money(sum((e.maintenance_amount for e in entries), _ZERO)),
        total_tip_amount=_money(sum((e.tip_amount for e in entries), _ZERO)),
        total_amount=_money(sum((e.total_amount for e in entries), _ZERO)),
    )


def list_daily_entries(
    db: Session,
    org_id: UUID,
    *,
    page: int,
    page_size: int,
    date_from: date | None = None,
    date_to: date | None = None,
    hamali_worker_id: UUID | None = None,
    payment_status: str | None = None,
) -> tuple[list[HamaliDailyEntry], int, HamaliDailySummary]:
    query = db.query(HamaliDailyEntry).filter(
        HamaliDailyEntry.org_id == org_id,
        HamaliDailyEntry.deleted_at.is_(None),
    )
    if date_from:
        query = query.filter(HamaliDailyEntry.entry_date >= date_from)
    if date_to:
        query = query.filter(HamaliDailyEntry.entry_date <= date_to)
    if hamali_worker_id:
        query = query.filter(HamaliDailyEntry.hamali_worker_id == hamali_worker_id)
    if payment_status:
        query = query.filter(HamaliDailyEntry.payment_status == payment_status)

    total = query.count()
    agg = query.with_entities(
        func.coalesce(func.sum(HamaliDailyEntry.bags_lifted), 0),
        func.coalesce(func.sum(HamaliDailyEntry.labor_amount), 0),
        func.coalesce(func.sum(HamaliDailyEntry.maintenance_amount), 0),
        func.coalesce(func.sum(HamaliDailyEntry.tip_amount), 0),
        func.coalesce(func.sum(HamaliDailyEntry.total_amount), 0),
    ).one()
    summary = HamaliDailySummary(
        total_bags=int(agg[0] or 0),
        total_labor_amount=_money(Decimal(str(agg[1] or 0))),
        total_maintenance_amount=_money(Decimal(str(agg[2] or 0))),
        total_tip_amount=_money(Decimal(str(agg[3] or 0))),
        total_amount=_money(Decimal(str(agg[4] or 0))),
    )
    items = (
        db.query(HamaliDailyEntry)
        .filter(
            HamaliDailyEntry.org_id == org_id,
            HamaliDailyEntry.deleted_at.is_(None),
        )
    )
    if date_from:
        items = items.filter(HamaliDailyEntry.entry_date >= date_from)
    if date_to:
        items = items.filter(HamaliDailyEntry.entry_date <= date_to)
    if hamali_worker_id:
        items = items.filter(HamaliDailyEntry.hamali_worker_id == hamali_worker_id)
    if payment_status:
        items = items.filter(HamaliDailyEntry.payment_status == payment_status)
    items = (
        items.order_by(HamaliDailyEntry.entry_date.desc(), HamaliDailyEntry.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total, summary


def create_daily_entry(
    db: Session,
    org_id: UUID,
    payload: HamaliDailyEntryCreateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> HamaliDailyEntry:
    worker = _get_worker(db, org_id, payload.hamali_worker_id)
    if worker.status != "active":
        raise ConflictError("Hamali worker is not active")

    duplicate = (
        db.query(HamaliDailyEntry)
        .filter(
            HamaliDailyEntry.org_id == org_id,
            HamaliDailyEntry.hamali_worker_id == payload.hamali_worker_id,
            HamaliDailyEntry.entry_date == payload.entry_date,
            HamaliDailyEntry.deleted_at.is_(None),
        )
        .first()
    )
    if duplicate:
        raise ConflictError("Daily entry already exists for this worker and date")

    rate = payload.rate_per_bag if payload.rate_per_bag is not None else worker.default_rate_per_bag
    labor, maintenance, tip, total = compute_entry_amounts(
        payload.bags_lifted,
        rate,
        payload.maintenance_amount,
        payload.tip_amount,
    )
    row = HamaliDailyEntry(
        org_id=org_id,
        hamali_worker_id=payload.hamali_worker_id,
        entry_date=payload.entry_date,
        bags_lifted=payload.bags_lifted,
        rate_per_bag=rate,
        labor_amount=labor,
        maintenance_amount=maintenance,
        tip_amount=tip,
        total_amount=total,
        payment_status="pending",
        procurement_id=payload.procurement_id,
        procurement_date=payload.procurement_date,
        notes=payload.notes,
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
        entity_type="hamali_daily_entry",
        entity_id=row.id,
        after={
            "entry_date": str(row.entry_date),
            "bags_lifted": row.bags_lifted,
            "total_amount": str(row.total_amount),
        },
        client=client,
        summary=f"Hamali daily entry: {worker.full_name} · {row.bags_lifted} bags",
    )
    db.commit()
    db.refresh(row)
    return row


def update_daily_entry(
    db: Session,
    org_id: UUID,
    entry_id: UUID,
    payload: HamaliDailyEntryUpdateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> HamaliDailyEntry:
    row = _get_entry(db, org_id, entry_id)
    if row.payment_status == "paid":
        raise ConflictError("Paid entries cannot be edited")
    if row.weekly_payment_id is not None:
        raise ConflictError("Entry is linked to a weekly payment batch — unpay or recreate batch first")

    data = payload.model_dump(exclude_unset=True)
    bags = data.get("bags_lifted", row.bags_lifted)
    rate = data.get("rate_per_bag", row.rate_per_bag)
    maintenance = data.get("maintenance_amount", row.maintenance_amount)
    tip = data.get("tip_amount", row.tip_amount)
    labor, maintenance, tip, total = compute_entry_amounts(bags, rate, maintenance, tip)
    row.bags_lifted = bags
    row.rate_per_bag = rate
    row.labor_amount = labor
    row.maintenance_amount = maintenance
    row.tip_amount = tip
    row.total_amount = total
    if "notes" in data:
        row.notes = data["notes"]
    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="UPDATE",
        entity_type="hamali_daily_entry",
        entity_id=row.id,
        after=data,
        client=client,
        summary=f"Hamali entry updated: {row.entry_date}",
    )
    db.commit()
    db.refresh(row)
    return row


def delete_daily_entry(
    db: Session,
    org_id: UUID,
    entry_id: UUID,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> None:
    row = _get_entry(db, org_id, entry_id)
    if row.payment_status == "paid":
        raise ConflictError("Paid entries cannot be deleted")
    if row.weekly_payment_id is not None:
        raise ConflictError("Entry is linked to a weekly payment batch")
    row.deleted_at = datetime.now(UTC)
    row.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="DELETE",
        entity_type="hamali_daily_entry",
        entity_id=row.id,
        client=client,
        summary=f"Hamali entry removed: {row.entry_date}",
    )
    db.commit()


def weekly_summary(
    db: Session,
    org_id: UUID,
    week_start_date: date,
) -> HamaliWeeklySummaryResponse:
    week_start, week_end = week_bounds(week_start_date)
    entries = (
        db.query(HamaliDailyEntry)
        .filter(
            HamaliDailyEntry.org_id == org_id,
            HamaliDailyEntry.entry_date >= week_start,
            HamaliDailyEntry.entry_date <= week_end,
            HamaliDailyEntry.payment_status == "pending",
            HamaliDailyEntry.deleted_at.is_(None),
        )
        .all()
    )
    workers = worker_name_map(db, {e.hamali_worker_id for e in entries})
    by_worker: dict[UUID, list[HamaliDailyEntry]] = {}
    for entry in entries:
        by_worker.setdefault(entry.hamali_worker_id, []).append(entry)

    worker_summaries: list[HamaliWorkerWeekSummary] = []
    for worker_id, worker_entries in sorted(
        by_worker.items(), key=lambda x: workers.get(x[0]).full_name if workers.get(x[0]) else ""
    ):
        worker = workers[worker_id]
        worker_summaries.append(
            HamaliWorkerWeekSummary(
                hamali_worker_id=worker_id,
                worker_name=worker.full_name,
                worker_code=worker.worker_code,
                days_worked=len(worker_entries),
                total_bags=sum(e.bags_lifted for e in worker_entries),
                total_labor_amount=_money(sum((e.labor_amount for e in worker_entries), _ZERO)),
                total_maintenance_amount=_money(
                    sum((e.maintenance_amount for e in worker_entries), _ZERO)
                ),
                total_tip_amount=_money(sum((e.tip_amount for e in worker_entries), _ZERO)),
                total_amount=_money(sum((e.total_amount for e in worker_entries), _ZERO)),
            )
        )

    summary = _summarize_entries(entries)
    return HamaliWeeklySummaryResponse(
        week_start_date=week_start,
        week_end_date=week_end,
        pending_entries=len(entries),
        total_bags=summary.total_bags,
        total_labor_amount=summary.total_labor_amount,
        total_maintenance_amount=summary.total_maintenance_amount,
        total_tip_amount=summary.total_tip_amount,
        total_amount=summary.total_amount,
        by_worker=worker_summaries,
    )


def create_weekly_payment(
    db: Session,
    org_id: UUID,
    payload: HamaliWeeklyPaymentCreateRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> HamaliWeeklyPayment:
    week_start = monday_of(payload.week_start_date)
    week_start, week_end = week_bounds(week_start)

    existing = (
        db.query(HamaliWeeklyPayment)
        .filter(
            HamaliWeeklyPayment.org_id == org_id,
            HamaliWeeklyPayment.week_start_date == week_start,
            HamaliWeeklyPayment.deleted_at.is_(None),
            HamaliWeeklyPayment.status != "paid",
        )
        .first()
    )
    if existing:
        raise ConflictError("A draft weekly payment already exists for this week")

    entries = (
        db.query(HamaliDailyEntry)
        .filter(
            HamaliDailyEntry.org_id == org_id,
            HamaliDailyEntry.entry_date >= week_start,
            HamaliDailyEntry.entry_date <= week_end,
            HamaliDailyEntry.payment_status == "pending",
            HamaliDailyEntry.deleted_at.is_(None),
        )
        .all()
    )
    if not entries:
        raise ConflictError("No pending daily entries for this week")

    summary = _summarize_entries(entries)
    row = HamaliWeeklyPayment(
        org_id=org_id,
        payment_number=_next_payment_number(db, org_id),
        week_start_date=week_start,
        week_end_date=week_end,
        total_bags=summary.total_bags,
        total_labor_amount=summary.total_labor_amount,
        total_maintenance_amount=summary.total_maintenance_amount,
        total_tip_amount=summary.total_tip_amount,
        total_amount=summary.total_amount,
        status="draft",
        notes=payload.notes,
        created_by=actor_user_id,
        updated_by=actor_user_id,
    )
    db.add(row)
    db.flush()
    for entry in entries:
        entry.weekly_payment_id = row.id
        entry.payment_status = "scheduled"
        entry.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="CREATE",
        entity_type="hamali_weekly_payment",
        entity_id=row.id,
        after={"payment_number": row.payment_number, "total_amount": str(row.total_amount)},
        client=client,
        summary=f"Weekly hamali batch {row.payment_number}: {summary.total_bags} bags",
    )
    db.commit()
    db.refresh(row)
    return row


def list_weekly_payments(
    db: Session,
    org_id: UUID,
    *,
    page: int,
    page_size: int,
    status: str | None = None,
) -> tuple[list[HamaliWeeklyPayment], int]:
    query = db.query(HamaliWeeklyPayment).filter(
        HamaliWeeklyPayment.org_id == org_id,
        HamaliWeeklyPayment.deleted_at.is_(None),
    )
    if status:
        query = query.filter(HamaliWeeklyPayment.status == status)
    total = query.count()
    items = (
        query.order_by(HamaliWeeklyPayment.week_start_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def mark_weekly_payment_paid(
    db: Session,
    org_id: UUID,
    payment_id: UUID,
    payload: HamaliWeeklyPaymentMarkPaidRequest,
    actor_user_id: UUID,
    client: ClientContext | None,
) -> HamaliWeeklyPayment:
    row = _get_weekly_payment(db, org_id, payment_id)
    if row.status == "paid":
        raise ConflictError("Weekly payment is already marked paid")

    entries = (
        db.query(HamaliDailyEntry)
        .filter(
            HamaliDailyEntry.weekly_payment_id == row.id,
            HamaliDailyEntry.deleted_at.is_(None),
        )
        .all()
    )
    now = datetime.now(UTC)
    row.status = "paid"
    row.paid_at = now
    row.paid_by = actor_user_id
    if payload.payment_reference:
        row.payment_reference = payload.payment_reference.strip()
    if payload.notes:
        row.notes = payload.notes
    row.updated_by = actor_user_id
    for entry in entries:
        entry.payment_status = "paid"
        entry.updated_by = actor_user_id
    _audit(
        db,
        org_id=org_id,
        actor_user_id=actor_user_id,
        action="PAY",
        entity_type="hamali_weekly_payment",
        entity_id=row.id,
        after={"status": "paid", "total_amount": str(row.total_amount)},
        client=client,
        summary=f"Hamali weekly payment settled: {row.payment_number}",
    )
    db.commit()
    db.refresh(row)
    return row


def _require_linked_worker(user: User) -> UUID:
    if user.hamali_worker_id is None:
        raise NotFoundError("Hamali worker profile not linked to this user")
    return user.hamali_worker_id


def _farmer_lookup(
    db: Session,
    org_id: UUID,
    procurement_ids: set[UUID],
) -> dict[UUID, tuple[UUID, str]]:
    if not procurement_ids:
        return {}
    rows = (
        db.query(Procurement.id, Procurement.farmer_id, Farmer.full_name)
        .join(Farmer, Farmer.id == Procurement.farmer_id)
        .filter(
            Procurement.org_id == org_id,
            Procurement.id.in_(procurement_ids),
            Farmer.org_id == org_id,
        )
        .all()
    )
    return {proc_id: (farmer_id, name) for proc_id, farmer_id, name in rows}


def _entry_to_lines(
    db: Session,
    org_id: UUID,
    entry: HamaliDailyEntry | None,
) -> list[HamaliMeDailyLine]:
    if entry is None:
        return []
    if entry.procurement_id:
        farmers = _farmer_lookup(db, org_id, {entry.procurement_id})
        if entry.procurement_id in farmers:
            farmer_id, farmer_name = farmers[entry.procurement_id]
            return [
                HamaliMeDailyLine(
                    farmer_id=farmer_id,
                    farmer_name=farmer_name,
                    bag_count=entry.bags_lifted,
                    tip_amount=entry.tip_amount,
                )
            ]
    return [
        HamaliMeDailyLine(
            farmer_id=_UNSPECIFIED_FARMER_ID,
            farmer_name="—",
            bag_count=entry.bags_lifted,
            tip_amount=entry.tip_amount,
        )
    ]


def _daily_response(
    db: Session,
    org_id: UUID,
    work_date: date,
    entry: HamaliDailyEntry | None,
) -> HamaliMeDailyResponse:
    lines = _entry_to_lines(db, org_id, entry)
    total_bags = entry.bags_lifted if entry else 0
    total_tips = entry.tip_amount if entry else _ZERO
    return HamaliMeDailyResponse(
        work_date=work_date,
        total_bags=total_bags,
        total_tips=_money(total_tips),
        lines=lines,
    )


def get_my_daily(
    db: Session,
    org_id: UUID,
    user: User,
    work_date: date | None = None,
) -> HamaliMeDailyResponse:
    worker_id = _require_linked_worker(user)
    target = work_date or date.today()
    entry = (
        db.query(HamaliDailyEntry)
        .filter(
            HamaliDailyEntry.org_id == org_id,
            HamaliDailyEntry.hamali_worker_id == worker_id,
            HamaliDailyEntry.entry_date == target,
            HamaliDailyEntry.deleted_at.is_(None),
        )
        .first()
    )
    return _daily_response(db, org_id, target, entry)


def _period_bounds(period: str, anchor: date) -> tuple[date, date]:
    if period == "week":
        start = monday_of(anchor)
        return week_bounds(start)
    if period == "month":
        start = anchor.replace(day=1)
        if start.month == 12:
            end = start.replace(year=start.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = start.replace(month=start.month + 1, day=1) - timedelta(days=1)
        return start, end
    raise ConflictError("period must be week or month")


def get_my_summary(
    db: Session,
    org_id: UUID,
    user: User,
    *,
    period: str,
    anchor_date: date | None = None,
) -> HamaliMeSummaryResponse:
    worker_id = _require_linked_worker(user)
    anchor = anchor_date or date.today()
    date_from, date_to = _period_bounds(period, anchor)
    entries = (
        db.query(HamaliDailyEntry)
        .filter(
            HamaliDailyEntry.org_id == org_id,
            HamaliDailyEntry.hamali_worker_id == worker_id,
            HamaliDailyEntry.entry_date >= date_from,
            HamaliDailyEntry.entry_date <= date_to,
            HamaliDailyEntry.deleted_at.is_(None),
        )
        .order_by(HamaliDailyEntry.entry_date.asc())
        .all()
    )
    by_farmer_map: dict[UUID, HamaliMeFarmerSummary] = {}
    by_day: list[HamaliMeDailyResponse] = []
    total_bags = 0
    total_tips = _ZERO
    for entry in entries:
        total_bags += entry.bags_lifted
        total_tips += entry.tip_amount
        by_day.append(_daily_response(db, org_id, entry.entry_date, entry))
        for line in _entry_to_lines(db, org_id, entry):
            existing = by_farmer_map.get(line.farmer_id)
            if existing:
                by_farmer_map[line.farmer_id] = HamaliMeFarmerSummary(
                    farmer_id=line.farmer_id,
                    farmer_name=line.farmer_name,
                    bag_count=existing.bag_count + line.bag_count,
                    tip_amount=_money(existing.tip_amount + line.tip_amount),
                )
            else:
                by_farmer_map[line.farmer_id] = HamaliMeFarmerSummary(
                    farmer_id=line.farmer_id,
                    farmer_name=line.farmer_name,
                    bag_count=line.bag_count,
                    tip_amount=line.tip_amount,
                )
    return HamaliMeSummaryResponse(
        period=period,
        date_from=date_from,
        date_to=date_to,
        total_bags=total_bags,
        total_tips=_money(total_tips),
        days_worked=len(entries),
        by_farmer=sorted(by_farmer_map.values(), key=lambda x: x.farmer_name),
        by_day=by_day,
    )
