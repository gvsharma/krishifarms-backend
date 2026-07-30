"""Aggregate Farmer 360° relationship profile from linked modules."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.modules.assets.models import Asset
from app.modules.documents.models import Document, DocumentLink
from app.modules.farmer_payments.models import FarmerPayment
from app.modules.farmers.models import Farmer, FarmerCropHistory, FarmerLandParcel
from app.modules.farmers.profile_360_schemas import (
    CommunicationItem,
    CropIntelligence,
    Farmer360Analytics,
    Farmer360DocumentItem,
    Farmer360LandItem,
    Farmer360ProfileResponse,
    Farmer360Statistics,
    Farmer360Summary,
    FarmingHistoryItem,
    FinanceHistoryItem,
    LedgerHistoryItem,
    ProcurementHistoryItem,
    QuickActionItem,
    RecommendationItem,
    ServiceHistoryItem,
    TimelineEvent,
)
from app.modules.farmers.service import farmer_outstanding, get_farmer, list_bank_accounts
from app.modules.field_services.models import FieldServiceRecord
from app.modules.master_data.models import CropType, Village
from app.modules.platform.models import ActivityType, Buyer, EntityComment, PaymentMode, VehicleType
from app.modules.procurements.models import FarmerLedgerEntry, Procurement
from app.modules.users.models import User
from app.shared.work_details import (
    bale_count_from_work_details,
    parse_work_details_from_comments,
    strip_work_details_marker,
    trips_from_work_details,
)

_ZERO = Decimal("0")
_CONFIRMED_PROC = frozenset({"confirmed", "paid_partial", "paid_full"})


def _money(value: Decimal | float | int | None) -> Decimal:
    if value is None:
        return _ZERO
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _status_label(status: str, is_vip: bool) -> str:
    if status == "blocked":
        return "Blacklisted"
    if is_vip and status == "active":
        return "VIP Farmer"
    return {"active": "Active", "inactive": "Inactive"}.get(status, status.title())


def _season_key(d: date) -> str:
    # Indian agri seasons (approx): Kharif Jun–Oct, Rabi Nov–Mar, Summer Apr–May
    if 6 <= d.month <= 10:
        return f"Kharif {d.year}"
    if d.month >= 11:
        return f"Rabi {d.year}"
    if d.month <= 3:
        return f"Rabi {d.year - 1}"
    return f"Summer {d.year}"


def _current_season_bounds(today: date | None = None) -> tuple[date, date]:
    today = today or date.today()
    if 6 <= today.month <= 10:
        return date(today.year, 6, 1), date(today.year, 10, 31)
    if today.month >= 11:
        return date(today.year, 11, 1), date(today.year + 1, 3, 31)
    if today.month <= 3:
        return date(today.year - 1, 11, 1), date(today.year, 3, 31)
    return date(today.year, 4, 1), date(today.year, 5, 31)


def _location_for_village(db: Session, village_id: UUID) -> tuple[str | None, str | None, str | None]:
    village = db.query(Village).filter(Village.id == village_id).first()
    if village is None:
        return None, None, None
    return village.name, village.mandal, village.district


def _build_summary(db: Session, farmer: Farmer, tags: list[str]) -> Farmer360Summary:
    village_name, mandal, district = _location_for_village(db, farmer.village_id)
    return Farmer360Summary(
        id=farmer.id,
        farmer_code=farmer.farmer_code,
        full_name=farmer.full_name,
        full_name_te=farmer.full_name_te,
        phone_primary=farmer.phone_primary,
        phone_secondary=farmer.phone_secondary,
        village_id=farmer.village_id,
        village_name=village_name,
        mandal=mandal,
        district=district,
        address=farmer.address,
        geo_lat=farmer.geo_lat,
        geo_lng=farmer.geo_lng,
        preferred_language=farmer.preferred_language,
        preferred_payment_cycle=farmer.preferred_payment_cycle,
        preferred_payment_method=farmer.preferred_payment_method,
        trust_rating=farmer.trust_rating,
        status=farmer.status,
        is_vip=bool(farmer.is_vip),
        status_label=_status_label(farmer.status, bool(farmer.is_vip)),
        tags=tags,
    )


def _services(db: Session, org_id: UUID, farmer_id: UUID) -> list[ServiceHistoryItem]:
    rows = (
        db.query(FieldServiceRecord, Asset.name, VehicleType.name, ActivityType.name)
        .outerjoin(Asset, Asset.id == FieldServiceRecord.asset_id)
        .outerjoin(VehicleType, VehicleType.id == FieldServiceRecord.vehicle_type_id)
        .outerjoin(ActivityType, ActivityType.id == FieldServiceRecord.activity_type_id)
        .filter(
            FieldServiceRecord.org_id == org_id,
            FieldServiceRecord.farmer_id == farmer_id,
            FieldServiceRecord.deleted_at.is_(None),
        )
        .order_by(FieldServiceRecord.service_date.desc(), FieldServiceRecord.created_at.desc())
        .limit(100)
        .all()
    )
    items: list[ServiceHistoryItem] = []
    for row, asset_name, vt_name, activity_name in rows:
        pending = row.pending_amount or _ZERO
        payment_status = "paid" if pending == 0 else ("partial" if (row.advance_amount or _ZERO) > 0 else "pending")
        work_details, _free = parse_work_details_from_comments(row.comments)
        trips = row.bag_count if row.service_category == "transport" else trips_from_work_details(work_details)
        bales = bale_count_from_work_details(work_details)
        remarks = strip_work_details_marker(row.comments)
        items.append(
            ServiceHistoryItem(
                id=row.id,
                record_number=row.record_number,
                service_date=row.service_date,
                service_category=row.service_category,
                vehicle_name=asset_name,
                vehicle_type=vt_name,
                activity_type=activity_name,
                operator=None,
                hours=row.hours,
                trips=trips,
                bales=bales,
                area_covered=row.quantity if row.quantity_unit in (None, "acres", "acre") else None,
                diesel_amount=_money(row.diesel_amount),
                amount_charged=_money(row.total_amount),
                pending_amount=_money(pending),
                payment_status=payment_status,
                status=row.status,
                remarks=remarks,
            )
        )
    return items


def _farming(db: Session, org_id: UUID, farmer_id: UUID) -> list[FarmingHistoryItem]:
    rows = (
        db.query(FarmerCropHistory, CropType.name)
        .outerjoin(CropType, CropType.id == FarmerCropHistory.crop_type_id)
        .filter(
            FarmerCropHistory.org_id == org_id,
            FarmerCropHistory.farmer_id == farmer_id,
            FarmerCropHistory.deleted_at.is_(None),
        )
        .order_by(FarmerCropHistory.year.desc(), FarmerCropHistory.season)
        .all()
    )
    return [
        FarmingHistoryItem(
            id=row.id,
            crop_type_id=row.crop_type_id,
            crop_type_name=crop_name,
            season=row.season,
            year=row.year,
            acres=row.acres,
            survey_number=row.survey_number,
            village_name=row.village_name,
            seed_variety=row.seed_variety,
            seed_supplier=row.seed_supplier,
            fertilizer_supplier=row.fertilizer_supplier,
            pesticides_used=row.pesticides_used,
            cultivation_stage=row.cultivation_stage,
            expected_yield=row.expected_yield,
            actual_yield=row.actual_yield,
            selling_market=row.selling_market,
            selling_price=row.selling_price,
            harvest_date=row.harvest_date,
            geo_lat=row.geo_lat,
            geo_lng=row.geo_lng,
            notes=row.notes,
        )
        for row, crop_name in rows
    ]


def _procurements(db: Session, org_id: UUID, farmer_id: UUID) -> list[ProcurementHistoryItem]:
    rows = (
        db.query(Procurement, CropType.name, Buyer.name)
        .outerjoin(CropType, CropType.id == Procurement.crop_type_id)
        .outerjoin(Buyer, Buyer.id == Procurement.buyer_id)
        .filter(
            Procurement.org_id == org_id,
            Procurement.farmer_id == farmer_id,
            Procurement.deleted_at.is_(None),
        )
        .order_by(Procurement.procurement_date.desc())
        .limit(100)
        .all()
    )
    return [
        ProcurementHistoryItem(
            id=row.id,
            procurement_number=row.procurement_number,
            procurement_date=row.procurement_date,
            crop_name=crop_name,
            quantity_kg=_money(row.net_weight_kg),
            moisture_pct=row.moisture_pct,
            rate_per_quintal=_money(row.rate_per_quintal),
            net_amount=_money(row.net_amount),
            buyer_name=buyer_name,
            payment_terms=row.payment_terms or row.payment_terms_custom,
            expected_payment_date=row.expected_payment_date,
            actual_payment_date=row.actual_payment_date,
            status=row.status,
            remarks=row.notes,
        )
        for row, crop_name, buyer_name in rows
    ]


def _finance(db: Session, org_id: UUID, farmer_id: UUID) -> list[FinanceHistoryItem]:
    rows = (
        db.query(FieldServiceRecord)
        .filter(
            FieldServiceRecord.org_id == org_id,
            FieldServiceRecord.farmer_id == farmer_id,
            FieldServiceRecord.service_category == "agri_finance",
            FieldServiceRecord.deleted_at.is_(None),
        )
        .order_by(FieldServiceRecord.service_date.desc())
        .all()
    )
    return [
        FinanceHistoryItem(
            id=row.id,
            record_number=row.record_number,
            loan_date=row.service_date,
            amount=_money(row.amount_given or row.total_amount),
            purpose=row.comments,
            paid_amount=_money((row.total_amount or _ZERO) - (row.pending_amount or _ZERO)),
            outstanding=_money(row.pending_amount),
            status=row.status,
            remarks=row.comments,
        )
        for row in rows
    ]


def _ledger(db: Session, org_id: UUID, farmer_id: UUID) -> list[LedgerHistoryItem]:
    rows = (
        db.query(FarmerLedgerEntry)
        .filter(FarmerLedgerEntry.org_id == org_id, FarmerLedgerEntry.farmer_id == farmer_id)
        .order_by(FarmerLedgerEntry.entry_date.desc(), FarmerLedgerEntry.posted_at.desc())
        .limit(100)
        .all()
    )
    payment_mode_by_ref: dict[UUID, str] = {}
    payment_ids = [r.reference_id for r in rows if r.reference_type == "farmer_payment"]
    if payment_ids:
        pay_rows = (
            db.query(FarmerPayment.id, PaymentMode.name, FarmerPayment.reference_no)
            .outerjoin(PaymentMode, PaymentMode.id == FarmerPayment.payment_mode_id)
            .filter(FarmerPayment.org_id == org_id, FarmerPayment.id.in_(payment_ids))
            .all()
        )
        for pid, mode_name, _ref in pay_rows:
            payment_mode_by_ref[pid] = mode_name or ""

    items: list[LedgerHistoryItem] = []
    for row in rows:
        mode = payment_mode_by_ref.get(row.reference_id) if row.reference_type == "farmer_payment" else None
        items.append(
            LedgerHistoryItem(
                id=row.id,
                entry_date=row.entry_date,
                entry_type=row.entry_type,
                reference_type=row.reference_type,
                reference_id=row.reference_id,
                debit=_money(row.debit),
                credit=_money(row.credit),
                balance_after=_money(row.balance_after),
                description=row.description,
                payment_mode=mode or None,
                reference_number=None,
            )
        )
    return items


def _land(db: Session, org_id: UUID, farmer_id: UUID) -> list[Farmer360LandItem]:
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
    return [Farmer360LandItem.model_validate(row) for row in rows]


def _documents(db: Session, org_id: UUID, farmer_id: UUID) -> list[Farmer360DocumentItem]:
    rows = (
        db.query(Document, DocumentLink.link_role)
        .join(DocumentLink, DocumentLink.document_id == Document.id)
        .filter(
            Document.org_id == org_id,
            DocumentLink.entity_type == "farmer",
            DocumentLink.entity_id == farmer_id,
        )
        .order_by(Document.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        Farmer360DocumentItem(
            id=doc.id,
            document_type=doc.document_type,
            file_name=doc.file_name,
            mime_type=doc.mime_type,
            link_role=link_role,
            created_at=doc.created_at,
        )
        for doc, link_role in rows
    ]


def _communication(db: Session, org_id: UUID, farmer_id: UUID) -> list[CommunicationItem]:
    rows = (
        db.query(EntityComment, User.full_name)
        .outerjoin(User, User.id == EntityComment.author_user_id)
        .filter(
            EntityComment.org_id == org_id,
            EntityComment.entity_type == "farmer",
            EntityComment.entity_id == farmer_id,
            EntityComment.deleted_at.is_(None),
        )
        .order_by(EntityComment.created_at.desc())
        .limit(50)
        .all()
    )
    return [
        CommunicationItem(
            id=row.id,
            kind="comment",
            body=row.body,
            author_name=author,
            created_at=row.created_at,
        )
        for row, author in rows
    ]


def _crop_intelligence(
    farming: list[FarmingHistoryItem],
    procurements: list[ProcurementHistoryItem],
) -> CropIntelligence:
    crop_counter: Counter[str] = Counter()
    yields: list[Decimal] = []
    for item in farming:
        if item.crop_type_name:
            crop_counter[item.crop_type_name] += 1
        if item.actual_yield is not None:
            yields.append(Decimal(str(item.actual_yield)))

    buyer_counter: Counter[str] = Counter()
    season_counter: Counter[str] = Counter()
    crop_revenue: dict[str, Decimal] = defaultdict(lambda: _ZERO)
    qty_values: list[Decimal] = []
    for proc in procurements:
        if proc.status not in _CONFIRMED_PROC and proc.status != "draft":
            pass
        if proc.buyer_name:
            buyer_counter[proc.buyer_name] += 1
        season_counter[_season_key(proc.procurement_date)] += 1
        if proc.crop_name:
            crop_revenue[proc.crop_name] += proc.net_amount
        qty_values.append(proc.quantity_kg)

    most_profitable = max(crop_revenue.items(), key=lambda x: x[1])[0] if crop_revenue else None
    avg_yield = (sum(yields) / len(yields)).quantize(Decimal("0.001")) if yields else None
    avg_proc = (sum(qty_values) / len(qty_values)).quantize(Decimal("0.01")) if qty_values else None

    return CropIntelligence(
        most_cultivated_crop=crop_counter.most_common(1)[0][0] if crop_counter else None,
        average_yield=avg_yield,
        average_procurement_kg=avg_proc,
        preferred_buyer=buyer_counter.most_common(1)[0][0] if buyer_counter else None,
        preferred_selling_season=season_counter.most_common(1)[0][0] if season_counter else None,
        most_profitable_crop=most_profitable,
        procurement_frequency=len(procurements),
    )


def _statistics(
    farmer: Farmer,
    services: list[ServiceHistoryItem],
    farming: list[FarmingHistoryItem],
    procurements: list[ProcurementHistoryItem],
    outstanding: Decimal,
    amount_paid: Decimal,
) -> Farmer360Statistics:
    season_start, season_end = _current_season_bounds()
    current_season_qty = sum(
        (p.quantity_kg for p in procurements if season_start <= p.procurement_date <= season_end),
        _ZERO,
    )
    confirmed = [p for p in procurements if p.status in _CONFIRMED_PROC]
    lifetime = sum((p.net_amount for p in confirmed), _ZERO)
    farming_area = sum((f.acres or _ZERO for f in farming), _ZERO)
    land_fallback = farming_area  # also summed from parcels in caller if needed

    current_crop = None
    if farming:
        latest = max(farming, key=lambda f: (f.year, f.season))
        current_crop = latest.crop_type_name

    vehicle_counter: Counter[str] = Counter(
        s.vehicle_type or s.vehicle_name for s in services if s.vehicle_type or s.vehicle_name
    )
    preferred_vehicle = vehicle_counter.most_common(1)[0][0] if vehicle_counter else None

    last_service = max((s.service_date for s in services), default=None)
    pending_svc = sum((s.pending_amount for s in services), _ZERO)

    return Farmer360Statistics(
        total_services_availed=len(services),
        total_farming_area=land_fallback,
        total_crops_sold=len(confirmed),
        total_procurement_quantity_kg=sum((p.quantity_kg for p in confirmed), _ZERO),
        lifetime_business_value=_money(lifetime),
        outstanding_amount=_money(outstanding),
        amount_paid=_money(amount_paid),
        current_season_procurement_kg=_money(current_season_qty),
        last_service_date=last_service,
        last_payment_date=None,  # filled by caller
        pending_payments=_money(pending_svc + outstanding if outstanding > 0 else pending_svc),
        current_crop=current_crop,
        preferred_vehicle=preferred_vehicle,
        preferred_payment_method=farmer.preferred_payment_method,
    )


def _analytics(
    services: list[ServiceHistoryItem],
    procurements: list[ProcurementHistoryItem],
    outstanding: Decimal,
) -> Farmer360Analytics:
    confirmed = [p for p in procurements if p.status in _CONFIRMED_PROC]
    revenue = sum((p.net_amount for p in confirmed), _ZERO)
    diesel = sum((s.diesel_amount for s in services), _ZERO)
    tractor_services = [s for s in services if s.service_category == "tractor_work"]
    hours = sum((s.hours or _ZERO for s in tractor_services), _ZERO)
    trips = sum((s.trips or 0 for s in services), 0)

    delays: list[int] = []
    for p in confirmed:
        if p.expected_payment_date and p.actual_payment_date:
            delays.append((p.actual_payment_date - p.expected_payment_date).days)
    avg_delay = (
        (Decimal(sum(delays)) / len(delays)).quantize(Decimal("0.1")) if delays else None
    )
    rates = [p.rate_per_quintal for p in confirmed if p.rate_per_quintal > 0]
    avg_rate = (sum(rates) / len(rates)).quantize(Decimal("0.01")) if rates else None
    costs = [s.amount_charged for s in services if s.amount_charged > 0]
    avg_svc = (sum(costs) / len(costs)).quantize(Decimal("0.01")) if costs else None

    season_rev: dict[str, Decimal] = defaultdict(lambda: _ZERO)
    year_rev: dict[str, Decimal] = defaultdict(lambda: _ZERO)
    for p in confirmed:
        season_rev[_season_key(p.procurement_date)] += p.net_amount
        year_rev[str(p.procurement_date.year)] += p.net_amount

    return Farmer360Analytics(
        total_revenue=_money(revenue),
        total_diesel_consumed=_money(diesel),
        total_tractor_hours=_money(hours),
        total_trips=trips,
        average_payment_delay_days=avg_delay,
        average_procurement_rate=avg_rate,
        average_service_cost=avg_svc,
        current_outstanding=_money(outstanding),
        season_wise_revenue={k: _money(v) for k, v in season_rev.items()},
        year_wise_revenue={k: _money(v) for k, v in year_rev.items()},
    )


def _recommendations(
    farmer: Farmer,
    stats: Farmer360Statistics,
    analytics: Farmer360Analytics,
    farming: list[FarmingHistoryItem],
    intelligence: CropIntelligence,
) -> list[RecommendationItem]:
    items: list[RecommendationItem] = []
    fid = str(farmer.id)

    if stats.outstanding_amount > 0:
        items.append(
            RecommendationItem(
                code="pending_collection",
                title="Pending collection reminder",
                rationale=f"Outstanding balance of ₹{stats.outstanding_amount}",
                priority="high",
                action_href=f"/payments?farmer_id={fid}",
            )
        )

    if stats.last_service_date is None or (date.today() - stats.last_service_date).days > 45:
        items.append(
            RecommendationItem(
                code="farm_visit",
                title="Farm visit reminder",
                rationale="No recent field service — schedule a relationship visit",
                priority="medium",
                action_href=f"/field-services/new?farmer_id={fid}",
            )
        )

    if intelligence.most_cultivated_crop:
        items.append(
            RecommendationItem(
                code="likely_crop",
                title="Likely crop to cultivate",
                rationale=f"Historical preference: {intelligence.most_cultivated_crop}",
                priority="low",
            )
        )

    if farming:
        with_harvest = [f for f in farming if f.harvest_date is None and f.cultivation_stage]
        if with_harvest:
            items.append(
                RecommendationItem(
                    code="expected_harvest",
                    title="Expected harvest follow-up",
                    rationale=f"Active crop stage: {with_harvest[0].cultivation_stage}",
                    priority="medium",
                    action_href=f"/farmers/{fid}",
                )
            )

    if stats.preferred_vehicle:
        items.append(
            RecommendationItem(
                code="recommended_service",
                title="Recommended services",
                rationale=f"Preferred equipment: {stats.preferred_vehicle}",
                priority="low",
                action_href=f"/field-services/new?farmer_id={fid}",
            )
        )

    # Simple retention score 0–100 from trust, activity, and outstanding
    score = 50
    if farmer.trust_rating:
        score += farmer.trust_rating * 6
    if farmer.is_vip:
        score += 10
    if stats.outstanding_amount > 10000:
        score -= 15
    if stats.total_services_availed + stats.total_crops_sold > 5:
        score += 10
    score = max(0, min(100, score))
    items.append(
        RecommendationItem(
            code="retention_score",
            title="Customer retention score",
            rationale=f"Score {score}/100 based on trust, activity, and outstanding",
            priority="low",
        )
    )

    if analytics.average_payment_delay_days and analytics.average_payment_delay_days > 7:
        items.append(
            RecommendationItem(
                code="upcoming_procurement",
                title="Upcoming procurement opportunity",
                rationale="Monitor harvest window; prior payment delays suggest early settlement planning",
                priority="medium",
                action_href=f"/procurement/new?farmer_id={fid}",
            )
        )

    return items


def _quick_actions(farmer_id: UUID) -> list[QuickActionItem]:
    fid = str(farmer_id)
    bookings = [
        ("tractor", "Book Tractor"),
        ("rotavator", "Book Rotavator"),
        ("cultivator", "Book Cultivator"),
        ("trolley", "Book Trolley"),
        ("bolero", "Book Bolero"),
        ("dcm", "Book DCM"),
        ("baler", "Book Baler"),
        ("weeder", "Book Weeder"),
        ("fertilizer_pump", "Book Fertilizer Pump"),
    ]
    actions = [
        QuickActionItem(
            code=f"book_{code}",
            label=label,
            href=f"/field-services/new?farmer_id={fid}&vehicle={code}",
            category="booking",
        )
        for code, label in bookings
    ]
    actions.extend(
        [
            QuickActionItem(
                code="start_procurement",
                label="Start Procurement",
                href=f"/procurement/new?farmer_id={fid}",
                category="procurement",
            ),
            QuickActionItem(
                code="add_farming",
                label="Add Farming Activity",
                href=f"/farmers/{fid}?tab=farming",
                category="farming",
            ),
            QuickActionItem(
                code="record_payment",
                label="Record Payment",
                href=f"/payments?farmer_id={fid}",
                category="finance",
            ),
            QuickActionItem(
                code="give_finance",
                label="Give Finance",
                href=f"/field-services/new?farmer_id={fid}&category=agri_finance",
                category="finance",
            ),
            QuickActionItem(
                code="collect_outstanding",
                label="Collect Outstanding",
                href=f"/payments?farmer_id={fid}&intent=collect",
                category="finance",
            ),
            QuickActionItem(
                code="upload_photo",
                label="Upload Photo",
                href=f"/farmers/{fid}?tab=documents",
                category="docs",
            ),
            QuickActionItem(
                code="add_comment",
                label="Add Comment",
                href=f"/farmers/{fid}?tab=communication",
                category="comms",
            ),
            QuickActionItem(
                code="call_farmer",
                label="Call Farmer",
                href="tel:",
                category="comms",
            ),
            QuickActionItem(
                code="navigate_farm",
                label="Navigate to Farm",
                href=f"/farmers/{fid}?tab=land",
                category="location",
            ),
        ]
    )
    return actions


def _timeline(
    farmer: Farmer,
    services: list[ServiceHistoryItem],
    farming: list[FarmingHistoryItem],
    procurements: list[ProcurementHistoryItem],
    finance: list[FinanceHistoryItem],
    ledger: list[LedgerHistoryItem],
    communication: list[CommunicationItem],
    documents: list[Farmer360DocumentItem],
) -> list[TimelineEvent]:
    events: list[TimelineEvent] = [
        TimelineEvent(
            event_type="farmer_created",
            title="Farmer created",
            description=f"{farmer.full_name} ({farmer.farmer_code}) registered",
            occurred_at=farmer.created_at if farmer.created_at.tzinfo else farmer.created_at.replace(tzinfo=UTC),
            entity_type="farmer",
            entity_id=farmer.id,
        )
    ]

    for s in services:
        title_bits = [s.service_category.replace("_", " ").title()]
        if s.vehicle_type:
            title_bits.append(s.vehicle_type)
        elif s.activity_type:
            title_bits.append(s.activity_type)
        events.append(
            TimelineEvent(
                event_type="service",
                title=f"Service: {' · '.join(title_bits)}",
                description=s.record_number,
                occurred_at=datetime.combine(s.service_date, datetime.min.time(), tzinfo=UTC),
                entity_type="field_service",
                entity_id=s.id,
                amount=s.amount_charged,
                meta={"status": s.status, "category": s.service_category},
            )
        )
        if s.diesel_amount > 0:
            events.append(
                TimelineEvent(
                    event_type="diesel",
                    title="Diesel entry",
                    description=f"₹{s.diesel_amount} on {s.record_number}",
                    occurred_at=datetime.combine(s.service_date, datetime.min.time(), tzinfo=UTC),
                    entity_type="field_service",
                    entity_id=s.id,
                    amount=s.diesel_amount,
                )
            )

    for f in farming:
        events.append(
            TimelineEvent(
                event_type="crop_update",
                title=f"Crop: {f.crop_type_name or 'Unknown'} ({f.season} {f.year})",
                description=f.cultivation_stage or f.notes,
                occurred_at=datetime(f.year, 6, 1, tzinfo=UTC),
                entity_type="crop_history",
                entity_id=f.id,
            )
        )

    for p in procurements:
        events.append(
            TimelineEvent(
                event_type="procurement",
                title=f"Procurement {p.procurement_number}",
                description=f"{p.crop_name or 'Crop'} · {p.quantity_kg} kg · {p.status}",
                occurred_at=datetime.combine(p.procurement_date, datetime.min.time(), tzinfo=UTC),
                entity_type="procurement",
                entity_id=p.id,
                amount=p.net_amount,
                meta={"status": p.status},
            )
        )

    for fin in finance:
        events.append(
            TimelineEvent(
                event_type="finance_given",
                title="Finance given",
                description=fin.purpose,
                occurred_at=datetime.combine(fin.loan_date, datetime.min.time(), tzinfo=UTC),
                entity_type="field_service",
                entity_id=fin.id,
                amount=fin.amount,
            )
        )

    for entry in ledger:
        kind = "payment_received" if entry.credit > 0 else "payment_made"
        events.append(
            TimelineEvent(
                event_type=kind,
                title="Ledger credit" if entry.credit > 0 else "Ledger debit",
                description=entry.description,
                occurred_at=datetime.combine(entry.entry_date, datetime.min.time(), tzinfo=UTC),
                entity_type="ledger",
                entity_id=entry.id,
                amount=entry.credit if entry.credit > 0 else entry.debit,
            )
        )

    for c in communication:
        events.append(
            TimelineEvent(
                event_type="comment",
                title="Comment",
                description=c.body[:200],
                occurred_at=c.created_at if c.created_at.tzinfo else c.created_at.replace(tzinfo=UTC),
                entity_type="comment",
                entity_id=c.id,
            )
        )

    for d in documents:
        if d.created_at:
            events.append(
                TimelineEvent(
                    event_type="document",
                    title=f"Document: {d.document_type}",
                    description=d.file_name,
                    occurred_at=d.created_at if d.created_at.tzinfo else d.created_at.replace(tzinfo=UTC),
                    entity_type="document",
                    entity_id=d.id,
                )
            )

    events.sort(key=lambda e: e.occurred_at, reverse=True)
    return events[:150]


def build_farmer_360(db: Session, org_id: UUID, farmer_id: UUID, tags: list[str] | None = None) -> Farmer360ProfileResponse:
    farmer = get_farmer(db, org_id, farmer_id)
    services = _services(db, org_id, farmer_id)
    farming = _farming(db, org_id, farmer_id)
    procurements = _procurements(db, org_id, farmer_id)
    finance = _finance(db, org_id, farmer_id)
    ledger = _ledger(db, org_id, farmer_id)
    land = _land(db, org_id, farmer_id)
    documents = _documents(db, org_id, farmer_id)
    communication = _communication(db, org_id, farmer_id)
    outstanding = farmer_outstanding(db, org_id, farmer_id)

    paid_row = (
        db.query(func.coalesce(func.sum(FarmerPayment.amount), 0))
        .filter(
            FarmerPayment.org_id == org_id,
            FarmerPayment.farmer_id == farmer_id,
            FarmerPayment.status == "completed",
        )
        .scalar()
    )
    amount_paid = _money(paid_row)

    last_payment = (
        db.query(FarmerPayment.payment_date)
        .filter(FarmerPayment.org_id == org_id, FarmerPayment.farmer_id == farmer_id)
        .order_by(FarmerPayment.payment_date.desc())
        .first()
    )

    # Prefer land parcel acres for farming area when crop history empty
    land_acres = sum((p.acres for p in land), _ZERO)

    summary = _build_summary(db, farmer, tags or [])
    stats = _statistics(farmer, services, farming, procurements, outstanding, amount_paid)
    if land_acres > 0 and stats.total_farming_area == 0:
        stats = stats.model_copy(update={"total_farming_area": land_acres})
    elif land_acres > stats.total_farming_area:
        stats = stats.model_copy(update={"total_farming_area": land_acres})
    if last_payment:
        stats = stats.model_copy(update={"last_payment_date": last_payment[0]})

    intelligence = _crop_intelligence(farming, procurements)
    analytics = _analytics(services, procurements, outstanding)
    recommendations = _recommendations(farmer, stats, analytics, farming, intelligence)
    timeline = _timeline(
        farmer, services, farming, procurements, finance, ledger, communication, documents
    )
    banks = list_bank_accounts(db, org_id, farmer_id)

    # Wire call action with phone
    actions = _quick_actions(farmer_id)
    actions = [
        a.model_copy(update={"href": f"tel:{farmer.phone_primary}"}) if a.code == "call_farmer" else a
        for a in actions
    ]
    if farmer.geo_lat and farmer.geo_lng:
        actions = [
            a.model_copy(
                update={"href": f"https://maps.google.com/?q={farmer.geo_lat},{farmer.geo_lng}"}
            )
            if a.code == "navigate_farm"
            else a
            for a in actions
        ]

    return Farmer360ProfileResponse(
        summary=summary,
        statistics=stats,
        timeline=timeline,
        services=services,
        farming=farming,
        procurements=procurements,
        finance=finance,
        ledger=ledger,
        crop_intelligence=intelligence,
        land=land,
        documents=documents,
        communication=communication,
        analytics=analytics,
        recommendations=recommendations,
        quick_actions=actions,
        bank_accounts_count=len(banks),
    )
