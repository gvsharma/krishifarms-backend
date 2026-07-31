"""Shared analytics SQL aggregations (org-scoped, soft-delete aware)."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.modules.analytics.filters import CONFIRMED_PROCUREMENT_STATUSES, kg, money
from app.modules.assets.models import Asset
from app.modules.assets.vehicle_trip_models import VehicleTrip
from app.modules.farmers.models import Farmer
from app.modules.field_services.models import FieldServiceRecord
from app.modules.financial.models import Collection, Expense
from app.modules.master_data.models import CropType, Village
from app.modules.procurements.models import FarmerLedgerEntry, Procurement

_ZERO = Decimal("0.00")


def sum_procurement_revenue(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
    *,
    village_id: UUID | None = None,
    crop_type_id: UUID | None = None,
    farmer_id: UUID | None = None,
    buyer_id: UUID | None = None,
) -> Decimal:
    q = db.query(func.coalesce(func.sum(Procurement.net_amount), 0)).filter(
        Procurement.org_id == org_id,
        Procurement.deleted_at.is_(None),
        Procurement.procurement_date >= date_from,
        Procurement.procurement_date <= date_to,
        Procurement.status.in_(CONFIRMED_PROCUREMENT_STATUSES),
    )
    if village_id:
        q = q.filter(Procurement.village_id == village_id)
    if crop_type_id:
        q = q.filter(Procurement.crop_type_id == crop_type_id)
    if farmer_id:
        q = q.filter(Procurement.farmer_id == farmer_id)
    if buyer_id:
        q = q.filter(Procurement.buyer_id == buyer_id)
    return money(q.scalar())


def sum_procurement_kg(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
    *,
    village_id: UUID | None = None,
    crop_type_id: UUID | None = None,
) -> Decimal:
    q = db.query(func.coalesce(func.sum(Procurement.net_weight_kg), 0)).filter(
        Procurement.org_id == org_id,
        Procurement.deleted_at.is_(None),
        Procurement.procurement_date >= date_from,
        Procurement.procurement_date <= date_to,
        Procurement.status.in_(CONFIRMED_PROCUREMENT_STATUSES),
    )
    if village_id:
        q = q.filter(Procurement.village_id == village_id)
    if crop_type_id:
        q = q.filter(Procurement.crop_type_id == crop_type_id)
    return kg(q.scalar())


def count_procurements(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
    *,
    statuses: frozenset[str] | None = None,
    village_id: UUID | None = None,
) -> int:
    q = db.query(func.count(Procurement.id)).filter(
        Procurement.org_id == org_id,
        Procurement.deleted_at.is_(None),
        Procurement.procurement_date >= date_from,
        Procurement.procurement_date <= date_to,
    )
    if statuses:
        q = q.filter(Procurement.status.in_(statuses))
    if village_id:
        q = q.filter(Procurement.village_id == village_id)
    return int(q.scalar() or 0)


def sum_field_service_amount(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
    *,
    farmer_id: UUID | None = None,
) -> Decimal:
    q = db.query(func.coalesce(func.sum(FieldServiceRecord.total_amount), 0)).filter(
        FieldServiceRecord.org_id == org_id,
        FieldServiceRecord.deleted_at.is_(None),
        FieldServiceRecord.service_date >= date_from,
        FieldServiceRecord.service_date <= date_to,
        FieldServiceRecord.status != "cancelled",
    )
    if farmer_id:
        q = q.filter(FieldServiceRecord.farmer_id == farmer_id)
    return money(q.scalar())


def count_field_services(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
) -> int:
    return int(
        db.query(func.count(FieldServiceRecord.id))
        .filter(
            FieldServiceRecord.org_id == org_id,
            FieldServiceRecord.deleted_at.is_(None),
            FieldServiceRecord.service_date >= date_from,
            FieldServiceRecord.service_date <= date_to,
            FieldServiceRecord.status != "cancelled",
        )
        .scalar()
        or 0
    )


def sum_expenses(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
) -> Decimal:
    return money(
        db.query(func.coalesce(func.sum(Expense.amount), 0))
        .filter(
            Expense.org_id == org_id,
            Expense.deleted_at.is_(None),
            Expense.expense_date >= date_from,
            Expense.expense_date <= date_to,
            Expense.status == "posted",
        )
        .scalar()
    )


def sum_collections(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
) -> Decimal:
    return money(
        db.query(func.coalesce(func.sum(Collection.amount), 0))
        .filter(
            Collection.org_id == org_id,
            Collection.collection_date >= date_from,
            Collection.collection_date <= date_to,
            Collection.status == "posted",
        )
        .scalar()
    )


def sum_org_outstanding(db: Session, org_id: UUID) -> Decimal:
    """Latest ledger balance_after per farmer, summed (positive = org owed to / by farmers)."""
    latest = (
        select(
            FarmerLedgerEntry.farmer_id.label("farmer_id"),
            FarmerLedgerEntry.balance_after.label("balance_after"),
            func.row_number()
            .over(
                partition_by=FarmerLedgerEntry.farmer_id,
                order_by=(FarmerLedgerEntry.entry_date.desc(), FarmerLedgerEntry.posted_at.desc()),
            )
            .label("rn"),
        )
        .where(FarmerLedgerEntry.org_id == org_id)
        .subquery()
    )
    total = db.query(func.coalesce(func.sum(latest.c.balance_after), 0)).filter(latest.c.rn == 1).scalar()
    return money(total)


def farmer_counts(db: Session, org_id: UUID, *, village_id: UUID | None = None) -> dict[str, int]:
    base = db.query(Farmer).filter(Farmer.org_id == org_id, Farmer.deleted_at.is_(None))
    if village_id:
        base = base.filter(Farmer.village_id == village_id)
    total = base.count()
    active = base.filter(Farmer.status == "active").count()
    vip = base.filter(Farmer.is_vip.is_(True)).count()
    return {"total": total, "active": active, "vip": vip}


def fleet_pulse(db: Session, org_id: UUID, date_from: date, date_to: date) -> dict[str, int]:
    assets_q = db.query(Asset).filter(Asset.org_id == org_id, Asset.deleted_at.is_(None))
    total_assets = assets_q.count()
    active_assets = assets_q.filter(Asset.status == "active").count()
    trips = int(
        db.query(func.count(VehicleTrip.id))
        .filter(
            VehicleTrip.org_id == org_id,
            VehicleTrip.trip_date >= date_from,
            VehicleTrip.trip_date <= date_to,
        )
        .scalar()
        or 0
    )
    working = (
        db.query(func.count(func.distinct(VehicleTrip.asset_id)))
        .filter(
            VehicleTrip.org_id == org_id,
            VehicleTrip.trip_date >= date_from,
            VehicleTrip.trip_date <= date_to,
        )
        .scalar()
        or 0
    )
    idle = max(active_assets - int(working), 0)
    return {
        "assets_total": total_assets,
        "assets_active": active_assets,
        "working": int(working),
        "idle": idle,
        "trips": trips,
    }


def pending_unpaid_procurements(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
) -> tuple[int, Decimal]:
    """Confirmed tickets not yet paid_full."""
    q = db.query(
        func.count(Procurement.id),
        func.coalesce(func.sum(Procurement.net_amount), 0),
    ).filter(
        Procurement.org_id == org_id,
        Procurement.deleted_at.is_(None),
        Procurement.procurement_date >= date_from,
        Procurement.procurement_date <= date_to,
        Procurement.status.in_(("confirmed", "paid_partial")),
    )
    count, amount = q.one()
    return int(count or 0), money(amount)


def revenue_series_by_day(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
    *,
    village_id: UUID | None = None,
) -> list[tuple[date, Decimal]]:
    q = (
        db.query(Procurement.procurement_date, func.coalesce(func.sum(Procurement.net_amount), 0))
        .filter(
            Procurement.org_id == org_id,
            Procurement.deleted_at.is_(None),
            Procurement.procurement_date >= date_from,
            Procurement.procurement_date <= date_to,
            Procurement.status.in_(CONFIRMED_PROCUREMENT_STATUSES),
        )
        .group_by(Procurement.procurement_date)
        .order_by(Procurement.procurement_date)
    )
    if village_id:
        q = q.filter(Procurement.village_id == village_id)
    return [(row[0], money(row[1])) for row in q.all()]


def expense_series_by_day(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
) -> list[tuple[date, Decimal]]:
    q = (
        db.query(Expense.expense_date, func.coalesce(func.sum(Expense.amount), 0))
        .filter(
            Expense.org_id == org_id,
            Expense.deleted_at.is_(None),
            Expense.expense_date >= date_from,
            Expense.expense_date <= date_to,
            Expense.status == "posted",
        )
        .group_by(Expense.expense_date)
        .order_by(Expense.expense_date)
    )
    return [(row[0], money(row[1])) for row in q.all()]


def top_villages_by_procurement(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
    *,
    limit: int = 10,
) -> list[dict]:
    rows = (
        db.query(
            Village.id,
            Village.name,
            func.coalesce(func.sum(Procurement.net_weight_kg), 0).label("kg"),
            func.coalesce(func.sum(Procurement.net_amount), 0).label("amount"),
            func.count(Procurement.id).label("tickets"),
        )
        .join(Procurement, and_(Procurement.village_id == Village.id, Procurement.org_id == org_id))
        .filter(
            Village.org_id == org_id,
            Village.deleted_at.is_(None),
            Procurement.deleted_at.is_(None),
            Procurement.procurement_date >= date_from,
            Procurement.procurement_date <= date_to,
            Procurement.status.in_(CONFIRMED_PROCUREMENT_STATUSES),
        )
        .group_by(Village.id, Village.name)
        .order_by(func.sum(Procurement.net_amount).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "village_id": str(r.id),
            "name": r.name,
            "kg": kg(r.kg),
            "amount": money(r.amount),
            "profit": money(r.amount),
            "tickets": int(r.tickets),
        }
        for r in rows
    ]


def top_crops_by_procurement(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
    *,
    limit: int = 10,
) -> list[dict]:
    rows = (
        db.query(
            CropType.id,
            CropType.name,
            func.coalesce(func.sum(Procurement.net_weight_kg), 0).label("kg"),
            func.coalesce(func.sum(Procurement.net_amount), 0).label("amount"),
            func.count(Procurement.id).label("tickets"),
        )
        .join(Procurement, and_(Procurement.crop_type_id == CropType.id, Procurement.org_id == org_id))
        .filter(
            CropType.org_id == org_id,
            CropType.deleted_at.is_(None),
            Procurement.deleted_at.is_(None),
            Procurement.procurement_date >= date_from,
            Procurement.procurement_date <= date_to,
            Procurement.status.in_(CONFIRMED_PROCUREMENT_STATUSES),
        )
        .group_by(CropType.id, CropType.name)
        .order_by(func.sum(Procurement.net_amount).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "crop_type_id": str(r.id),
            "name": r.name,
            "kg": kg(r.kg),
            "amount": money(r.amount),
            "profit": money(r.amount),
            "tickets": int(r.tickets),
        }
        for r in rows
    ]


def top_farmers_by_revenue(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
    *,
    limit: int = 10,
) -> list[dict]:
    proc_rows = (
        db.query(
            Farmer.id,
            Farmer.full_name,
            func.coalesce(func.sum(Procurement.net_amount), 0).label("proc_amount"),
            func.coalesce(func.sum(Procurement.net_weight_kg), 0).label("kg"),
            func.count(Procurement.id).label("tickets"),
        )
        .join(Procurement, and_(Procurement.farmer_id == Farmer.id, Procurement.org_id == org_id))
        .filter(
            Farmer.org_id == org_id,
            Farmer.deleted_at.is_(None),
            Procurement.deleted_at.is_(None),
            Procurement.procurement_date >= date_from,
            Procurement.procurement_date <= date_to,
            Procurement.status.in_(CONFIRMED_PROCUREMENT_STATUSES),
        )
        .group_by(Farmer.id, Farmer.full_name)
        .all()
    )
    fs_rows = (
        db.query(
            Farmer.id,
            func.coalesce(func.sum(FieldServiceRecord.total_amount), 0).label("fs_amount"),
        )
        .join(
            FieldServiceRecord,
            and_(FieldServiceRecord.farmer_id == Farmer.id, FieldServiceRecord.org_id == org_id),
        )
        .filter(
            Farmer.org_id == org_id,
            Farmer.deleted_at.is_(None),
            FieldServiceRecord.deleted_at.is_(None),
            FieldServiceRecord.service_date >= date_from,
            FieldServiceRecord.service_date <= date_to,
            FieldServiceRecord.status != "cancelled",
        )
        .group_by(Farmer.id)
        .all()
    )
    fs_map = {r.id: money(r.fs_amount) for r in fs_rows}
    merged: dict[UUID, dict] = {}
    for r in proc_rows:
        proc_amt = money(r.proc_amount)
        fs_amt = fs_map.get(r.id, _ZERO)
        revenue = money(proc_amt + fs_amt)
        merged[r.id] = {
            "farmer_id": str(r.id),
            "name": r.full_name,
            "kg": kg(r.kg),
            "revenue": revenue,
            "profit": revenue,
            "tickets": int(r.tickets),
        }
    for fid, fs_amt in fs_map.items():
        if fid in merged:
            continue
        farmer = db.query(Farmer.full_name).filter(Farmer.id == fid, Farmer.org_id == org_id).first()
        if not farmer:
            continue
        merged[fid] = {
            "farmer_id": str(fid),
            "name": farmer.full_name,
            "kg": kg(0),
            "revenue": fs_amt,
            "profit": fs_amt,
            "tickets": 0,
        }
    ranked = sorted(merged.values(), key=lambda x: x["revenue"], reverse=True)[:limit]
    return ranked


def profit_series_by_day(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
    *,
    village_id: UUID | None = None,
) -> list[tuple[date, Decimal]]:
    rev_by_day = {
        d: amt for d, amt in revenue_series_by_day(db, org_id, date_from, date_to, village_id=village_id)
    }
    exp_by_day = {d: amt for d, amt in expense_series_by_day(db, org_id, date_from, date_to)}
    days = sorted(set(rev_by_day) | set(exp_by_day))
    return [(d, money(rev_by_day.get(d, _ZERO) - exp_by_day.get(d, _ZERO))) for d in days]


def expense_by_category(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
    *,
    limit: int = 10,
) -> list[dict]:
    from app.modules.financial.models import ExpenseCategory

    rows = (
        db.query(
            ExpenseCategory.id,
            ExpenseCategory.name,
            func.coalesce(func.sum(Expense.amount), 0).label("amount"),
            func.count(Expense.id).label("count"),
        )
        .join(Expense, Expense.category_id == ExpenseCategory.id)
        .filter(
            Expense.org_id == org_id,
            Expense.deleted_at.is_(None),
            Expense.expense_date >= date_from,
            Expense.expense_date <= date_to,
            Expense.status == "posted",
            ExpenseCategory.org_id == org_id,
            ExpenseCategory.deleted_at.is_(None),
        )
        .group_by(ExpenseCategory.id, ExpenseCategory.name)
        .order_by(func.sum(Expense.amount).desc())
        .limit(limit)
        .all()
    )
    return [
        {"category_id": str(r.id), "name": r.name, "amount": money(r.amount), "count": int(r.count)}
        for r in rows
    ]


def avg_moisture(
    db: Session,
    org_id: UUID,
    date_from: date,
    date_to: date,
) -> Decimal | None:
    val = (
        db.query(func.avg(Procurement.moisture_pct))
        .filter(
            Procurement.org_id == org_id,
            Procurement.deleted_at.is_(None),
            Procurement.procurement_date >= date_from,
            Procurement.procurement_date <= date_to,
            Procurement.status.in_(CONFIRMED_PROCUREMENT_STATUSES),
            Procurement.moisture_pct.isnot(None),
        )
        .scalar()
    )
    if val is None:
        return None
    return money(val)


def rules_v1_health_score(
    *,
    outstanding: Decimal,
    revenue: Decimal,
    open_procurements: int,
    trips: int,
    field_services: int,
) -> int:
    """Weighted 0–100 heuristic — labeled rules_v1, not ML."""
    score = 70
    if revenue > 0 and outstanding > revenue:
        score -= 15
    elif outstanding > money(0):
        score -= 5
    if open_procurements > 20:
        score -= 10
    elif open_procurements > 5:
        score -= 5
    activity = trips + field_services
    if activity >= 10:
        score += 10
    elif activity >= 3:
        score += 5
    elif activity == 0:
        score -= 10
    return max(0, min(100, score))
