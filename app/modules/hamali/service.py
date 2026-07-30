from __future__ import annotations

import re
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.modules.farmers.models import Farmer
from app.modules.hamali.models import HamaliWorkEntry, Worker
from app.modules.hamali.schemas import (
    HamaliDailyLineResponse,
    HamaliDailyResponse,
    HamaliSummaryPeriodResponse,
    HamaliTipByFarmerResponse,
    HamaliWorkEntryCreateRequest,
    HamaliWorkEntryUpdateRequest,
    WorkerCreateRequest,
)
from app.modules.users.models import User


def _next_worker_code(db: Session, org_id: UUID) -> str:
    rows = (
        db.query(Worker.worker_code)
        .filter(Worker.org_id == org_id, Worker.worker_code.like("HML-%"))
        .all()
    )
    max_seq = 0
    for (code,) in rows:
        match = re.match(r"^HML-(\d+)$", code or "")
        if match:
            max_seq = max(max_seq, int(match.group(1)))
    return f"HML-{max_seq + 1:04d}"


def _require_worker_link(user: User) -> UUID:
    if user.worker_id is None:
        raise ForbiddenError("Hamali login is not linked to a worker profile. Contact your admin.")
    return user.worker_id


def _period_bounds(period: str, anchor: date) -> tuple[date, date]:
    if period == "week":
        start = anchor - timedelta(days=anchor.weekday())
        end = start + timedelta(days=6)
        return start, end
    if period == "month":
        start = anchor.replace(day=1)
        if anchor.month == 12:
            end = date(anchor.year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(anchor.year, anchor.month + 1, 1) - timedelta(days=1)
        return start, end
    raise ConflictError("period must be 'week' or 'month'")


def _enrich_entry(row: HamaliWorkEntry, worker_name: str | None, farmer_name: str | None) -> dict:
    data = {
        "id": row.id,
        "worker_id": row.worker_id,
        "farmer_id": row.farmer_id,
        "work_date": row.work_date,
        "bag_count": row.bag_count,
        "tip_amount": row.tip_amount,
        "procurement_id": row.procurement_id,
        "notes": row.notes,
        "worker_name": worker_name,
        "farmer_name": farmer_name,
    }
    return data


def list_workers(db: Session, org_id: UUID, page: int, page_size: int) -> tuple[list[Worker], int]:
    query = (
        db.query(Worker)
        .filter(Worker.org_id == org_id, Worker.deleted_at.is_(None), Worker.status == "active")
        .order_by(Worker.full_name.asc())
    )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def create_worker(db: Session, org_id: UUID, payload: WorkerCreateRequest, actor_user_id: UUID) -> Worker:
    row = Worker(
        org_id=org_id,
        worker_code=_next_worker_code(db, org_id),
        full_name=payload.full_name,
        phone=payload.phone,
        village_id=payload.village_id,
        status="active",
        created_by=actor_user_id,
        updated_by=actor_user_id,
    )
    db.add(row)
    db.flush()
    return row


def create_worker_for_hamali_user(
    db: Session,
    org_id: UUID,
    *,
    full_name: str,
    phone: str | None,
    actor_user_id: UUID,
) -> Worker:
    return create_worker(
        db,
        org_id,
        WorkerCreateRequest(full_name=full_name, phone=phone),
        actor_user_id,
    )


def list_work_entries(
    db: Session,
    org_id: UUID,
    *,
    page: int,
    page_size: int,
    worker_id: UUID | None = None,
    work_date: date | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[list[dict], int]:
    query = (
        db.query(HamaliWorkEntry, Worker.full_name, Farmer.full_name)
        .join(Worker, HamaliWorkEntry.worker_id == Worker.id)
        .join(Farmer, HamaliWorkEntry.farmer_id == Farmer.id)
        .filter(HamaliWorkEntry.org_id == org_id, HamaliWorkEntry.deleted_at.is_(None))
    )
    if worker_id:
        query = query.filter(HamaliWorkEntry.worker_id == worker_id)
    if work_date:
        query = query.filter(HamaliWorkEntry.work_date == work_date)
    if date_from:
        query = query.filter(HamaliWorkEntry.work_date >= date_from)
    if date_to:
        query = query.filter(HamaliWorkEntry.work_date <= date_to)
    total = query.count()
    rows = (
        query.order_by(HamaliWorkEntry.work_date.desc(), HamaliWorkEntry.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [_enrich_entry(entry, wname, fname) for entry, wname, fname in rows]
    return items, total


def create_work_entry(
    db: Session,
    org_id: UUID,
    payload: HamaliWorkEntryCreateRequest,
    actor_user_id: UUID,
) -> dict:
    worker = (
        db.query(Worker)
        .filter(Worker.id == payload.worker_id, Worker.org_id == org_id, Worker.deleted_at.is_(None))
        .first()
    )
    if worker is None:
        raise NotFoundError("Worker not found")
    farmer = (
        db.query(Farmer)
        .filter(Farmer.id == payload.farmer_id, Farmer.org_id == org_id, Farmer.deleted_at.is_(None))
        .first()
    )
    if farmer is None:
        raise NotFoundError("Farmer not found")

    row = HamaliWorkEntry(
        org_id=org_id,
        worker_id=payload.worker_id,
        farmer_id=payload.farmer_id,
        work_date=payload.work_date,
        bag_count=payload.bag_count,
        tip_amount=payload.tip_amount,
        procurement_id=payload.procurement_id,
        notes=payload.notes,
        created_by=actor_user_id,
        updated_by=actor_user_id,
    )
    db.add(row)
    db.flush()
    return _enrich_entry(row, worker.full_name, farmer.full_name)


def update_work_entry(
    db: Session,
    org_id: UUID,
    entry_id: UUID,
    payload: HamaliWorkEntryUpdateRequest,
    actor_user_id: UUID,
) -> dict:
    row = (
        db.query(HamaliWorkEntry)
        .filter(HamaliWorkEntry.id == entry_id, HamaliWorkEntry.org_id == org_id, HamaliWorkEntry.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Work entry not found")

    if payload.farmer_id is not None:
        farmer = (
            db.query(Farmer)
            .filter(Farmer.id == payload.farmer_id, Farmer.org_id == org_id, Farmer.deleted_at.is_(None))
            .first()
        )
        if farmer is None:
            raise NotFoundError("Farmer not found")
        row.farmer_id = payload.farmer_id
    if payload.work_date is not None:
        row.work_date = payload.work_date
    if payload.bag_count is not None:
        row.bag_count = payload.bag_count
    if payload.tip_amount is not None:
        row.tip_amount = payload.tip_amount
    if payload.procurement_id is not None:
        row.procurement_id = payload.procurement_id
    if payload.notes is not None:
        row.notes = payload.notes
    row.updated_by = actor_user_id
    db.flush()

    worker = db.query(Worker).filter(Worker.id == row.worker_id).first()
    farmer = db.query(Farmer).filter(Farmer.id == row.farmer_id).first()
    return _enrich_entry(row, worker.full_name if worker else None, farmer.full_name if farmer else None)


def delete_work_entry(db: Session, org_id: UUID, entry_id: UUID, actor_user_id: UUID) -> None:
    row = (
        db.query(HamaliWorkEntry)
        .filter(HamaliWorkEntry.id == entry_id, HamaliWorkEntry.org_id == org_id, HamaliWorkEntry.deleted_at.is_(None))
        .first()
    )
    if row is None:
        raise NotFoundError("Work entry not found")
    row.deleted_at = datetime.now(UTC)
    row.updated_by = actor_user_id


def _aggregate_daily(db: Session, org_id: UUID, worker_id: UUID, work_date: date) -> HamaliDailyResponse:
    rows = (
        db.query(
            HamaliWorkEntry.farmer_id,
            Farmer.full_name,
            func.sum(HamaliWorkEntry.bag_count),
            func.sum(HamaliWorkEntry.tip_amount),
        )
        .join(Farmer, HamaliWorkEntry.farmer_id == Farmer.id)
        .filter(
            HamaliWorkEntry.org_id == org_id,
            HamaliWorkEntry.worker_id == worker_id,
            HamaliWorkEntry.work_date == work_date,
            HamaliWorkEntry.deleted_at.is_(None),
        )
        .group_by(HamaliWorkEntry.farmer_id, Farmer.full_name)
        .all()
    )
    lines = [
        HamaliDailyLineResponse(
            farmer_id=fid,
            farmer_name=fname,
            bag_count=int(bags or 0),
            tip_amount=Decimal(tips or 0),
        )
        for fid, fname, bags, tips in rows
    ]
    total_bags = sum(line.bag_count for line in lines)
    total_tips = sum((line.tip_amount for line in lines), Decimal("0"))
    return HamaliDailyResponse(
        work_date=work_date,
        total_bags=total_bags,
        total_tips=total_tips,
        lines=lines,
    )


def get_my_daily(db: Session, org_id: UUID, user: User, work_date: date) -> HamaliDailyResponse:
    worker_id = _require_worker_link(user)
    return _aggregate_daily(db, org_id, worker_id, work_date)


def get_my_summary(
    db: Session,
    org_id: UUID,
    user: User,
    *,
    period: str,
    anchor_date: date,
) -> HamaliSummaryPeriodResponse:
    worker_id = _require_worker_link(user)
    date_from, date_to = _period_bounds(period, anchor_date)

    by_farmer_rows = (
        db.query(
            HamaliWorkEntry.farmer_id,
            Farmer.full_name,
            func.sum(HamaliWorkEntry.bag_count),
            func.sum(HamaliWorkEntry.tip_amount),
        )
        .join(Farmer, HamaliWorkEntry.farmer_id == Farmer.id)
        .filter(
            HamaliWorkEntry.org_id == org_id,
            HamaliWorkEntry.worker_id == worker_id,
            HamaliWorkEntry.work_date >= date_from,
            HamaliWorkEntry.work_date <= date_to,
            HamaliWorkEntry.deleted_at.is_(None),
        )
        .group_by(HamaliWorkEntry.farmer_id, Farmer.full_name)
        .all()
    )
    by_farmer = [
        HamaliTipByFarmerResponse(
            farmer_id=fid,
            farmer_name=fname,
            bag_count=int(bags or 0),
            tip_amount=Decimal(tips or 0),
        )
        for fid, fname, bags, tips in by_farmer_rows
    ]

    day_rows = (
        db.query(HamaliWorkEntry.work_date)
        .filter(
            HamaliWorkEntry.org_id == org_id,
            HamaliWorkEntry.worker_id == worker_id,
            HamaliWorkEntry.work_date >= date_from,
            HamaliWorkEntry.work_date <= date_to,
            HamaliWorkEntry.deleted_at.is_(None),
        )
        .distinct()
        .all()
    )
    by_day = [_aggregate_daily(db, org_id, worker_id, d) for (d,) in sorted(day_rows, key=lambda x: x[0])]

    total_bags = sum(f.bag_count for f in by_farmer)
    total_tips = sum((f.tip_amount for f in by_farmer), Decimal("0"))

    return HamaliSummaryPeriodResponse(
        period=period,
        date_from=date_from,
        date_to=date_to,
        total_bags=total_bags,
        total_tips=total_tips,
        days_worked=len(by_day),
        by_farmer=by_farmer,
        by_day=by_day,
    )
