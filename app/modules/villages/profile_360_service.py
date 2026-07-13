"""Village 360° aggregation — farmers, procurement, services, finance by village."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.modules.assets.models import Asset
from app.modules.documents.models import Document, DocumentLink
from app.modules.farmer_payments.models import FarmerPayment
from app.modules.farmers.models import Farmer, FarmerCropHistory, FarmerLandParcel
from app.modules.farmers.profile_360_service import _current_season_bounds, _season_key
from app.modules.farmers.service import farmer_outstanding
from app.modules.farms.models import Farm
from app.modules.field_services.models import FieldServiceRecord
from app.modules.master_data.models import CropType, Village
from app.modules.master_data.service import get_village
from app.modules.platform.models import Buyer, EntityComment, FieldAgent, PaymentMode, VehicleType
from app.modules.procurements.models import Procurement
from app.modules.users.models import User
from app.modules.villages.profile_360_schemas import (
    Village360ProfileResponse,
    Village360Statistics,
    Village360Summary,
    VillageAnalytics,
    VillageBuyerRow,
    VillageCommentRow,
    VillageDocumentRow,
    VillageFarmerRow,
    VillageFarmingRow,
    VillageFinanceRow,
    VillageMapReady,
    VillagePaymentRow,
    VillageProcurementRow,
    VillageReportLink,
    VillageSearchHit,
    VillageSearchResponse,
    VillageServiceRow,
    VillageTimelineEvent,
    VillageVehicleRow,
)

_ZERO = Decimal("0")
_CONFIRMED = frozenset({"confirmed", "paid_partial", "paid_full"})
_PADDY = frozenset({"paddy", "rice"})
_CORN = frozenset({"corn", "maize"})


def _money(value: Decimal | float | int | None) -> Decimal:
    if value is None:
        return _ZERO
    return Decimal(str(value)).quantize(Decimal("0.01"))


def _area(value: Decimal | float | int | None) -> Decimal:
    if value is None:
        return _ZERO
    return Decimal(str(value)).quantize(Decimal("0.001"))


def _crop_bucket(name: str | None) -> str:
    if not name:
        return "other"
    key = name.strip().lower()
    if key in _PADDY or "paddy" in key or "rice" in key:
        return "paddy"
    if key in _CORN or "corn" in key or "maize" in key:
        return "corn"
    return "other"


def _vehicle_kind(code_or_name: str | None) -> str:
    if not code_or_name:
        return "other"
    key = code_or_name.strip().lower()
    for token in ("tractor", "rotavator", "cultivator", "baler", "bolero", "dcm"):
        if token in key:
            return token
    return "other"


def build_village_360(db: Session, org_id: UUID, village_id: UUID) -> Village360ProfileResponse:
    village = get_village(db, org_id, village_id)
    agent_name = None
    if village.agent_id:
        agent = db.query(FieldAgent.name).filter(FieldAgent.id == village.agent_id).first()
        agent_name = agent[0] if agent else None

    summary = Village360Summary(
        id=village.id,
        village_code=village.village_code,
        name=village.name,
        mandal=village.mandal,
        district=village.district,
        state=village.state,
        pincode=village.pincode,
        geo_lat=village.geo_lat,
        geo_lng=village.geo_lng,
        agent_id=village.agent_id,
        agent_name=agent_name,
        status=village.status or "active",
        population=village.population,
        estimated_cultivable_area=village.estimated_cultivable_area,
        notes=village.notes,
    )

    farmers = (
        db.query(Farmer)
        .filter(Farmer.org_id == org_id, Farmer.village_id == village_id, Farmer.deleted_at.is_(None))
        .order_by(Farmer.full_name)
        .all()
    )
    farmer_ids = [f.id for f in farmers]
    farmer_name = {f.id: f.full_name for f in farmers}

    # Land + crop areas
    land_acres = _ZERO
    if farmer_ids:
        land_acres = _area(
            db.query(func.coalesce(func.sum(FarmerLandParcel.acres), 0))
            .filter(
                FarmerLandParcel.org_id == org_id,
                FarmerLandParcel.farmer_id.in_(farmer_ids),
                FarmerLandParcel.deleted_at.is_(None),
            )
            .scalar()
        )

    crop_rows = []
    if farmer_ids:
        crop_rows = (
            db.query(FarmerCropHistory, CropType.name, Farmer.full_name)
            .outerjoin(CropType, CropType.id == FarmerCropHistory.crop_type_id)
            .join(Farmer, Farmer.id == FarmerCropHistory.farmer_id)
            .filter(
                FarmerCropHistory.org_id == org_id,
                FarmerCropHistory.farmer_id.in_(farmer_ids),
                FarmerCropHistory.deleted_at.is_(None),
            )
            .order_by(FarmerCropHistory.year.desc())
            .all()
        )

    paddy = corn = other = _ZERO
    farming_tab: list[VillageFarmingRow] = []
    yields: list[Decimal] = []
    crop_counter: Counter[str] = Counter()
    for row, crop_name, fname in crop_rows:
        acres = _area(row.acres)
        bucket = _crop_bucket(crop_name)
        if bucket == "paddy":
            paddy += acres
        elif bucket == "corn":
            corn += acres
        else:
            other += acres
        if crop_name:
            crop_counter[crop_name] += 1
        if row.actual_yield is not None:
            yields.append(Decimal(str(row.actual_yield)))
        farming_tab.append(
            VillageFarmingRow(
                id=row.id,
                farmer_name=fname,
                crop_name=crop_name,
                season=row.season,
                year=row.year,
                acres=row.acres,
                cultivation_stage=row.cultivation_stage,
                actual_yield=row.actual_yield,
            )
        )

    own_farms = (
        db.query(Farm)
        .filter(Farm.org_id == org_id, Farm.village_id == village_id, Farm.deleted_at.is_(None))
        .all()
    )
    own_area = sum((_area(f.acres) for f in own_farms), _ZERO)

    # Procurements
    proc_rows = (
        db.query(Procurement, CropType.name, Buyer.name, Farmer.full_name)
        .outerjoin(CropType, CropType.id == Procurement.crop_type_id)
        .outerjoin(Buyer, Buyer.id == Procurement.buyer_id)
        .outerjoin(Farmer, Farmer.id == Procurement.farmer_id)
        .filter(
            Procurement.org_id == org_id,
            Procurement.village_id == village_id,
            Procurement.deleted_at.is_(None),
        )
        .order_by(Procurement.procurement_date.desc())
        .limit(200)
        .all()
    )

    today = date.today()
    season_start, season_end = _current_season_bounds(today)
    actual = expected = today_qty = season_qty = revenue = _ZERO
    buyer_qty: dict[UUID, Decimal] = defaultdict(lambda: _ZERO)
    buyer_rate_sum: dict[UUID, Decimal] = defaultdict(lambda: _ZERO)
    buyer_rate_n: dict[UUID, int] = defaultdict(int)
    buyer_last: dict[UUID, date] = {}
    buyer_names: dict[UUID, str] = {}
    farmer_revenue: dict[UUID, Decimal] = defaultdict(lambda: _ZERO)
    farmer_last_proc: dict[UUID, date] = {}
    delays: list[int] = []
    rates: list[Decimal] = []
    season_rev: dict[str, Decimal] = defaultdict(lambda: _ZERO)
    year_rev: dict[str, Decimal] = defaultdict(lambda: _ZERO)
    crop_proc_counter: Counter[str] = Counter()
    buyer_counter: Counter[str] = Counter()

    procurements_tab: list[VillageProcurementRow] = []
    for proc, crop_name, buyer_name, fname in proc_rows:
        qty = _money(proc.net_weight_kg)
        amt = _money(proc.net_amount)
        procurements_tab.append(
            VillageProcurementRow(
                id=proc.id,
                procurement_number=proc.procurement_number,
                procurement_date=proc.procurement_date,
                crop_name=crop_name,
                farmer_name=fname,
                farmer_id=proc.farmer_id,
                buyer_name=buyer_name,
                quantity_kg=qty,
                moisture_pct=proc.moisture_pct,
                rate_per_quintal=_money(proc.rate_per_quintal),
                net_amount=amt,
                payment_terms=proc.payment_terms or proc.payment_terms_custom,
                status=proc.status,
                vehicle=None,
            )
        )
        if proc.status in _CONFIRMED:
            actual += qty
            revenue += amt
            if crop_name:
                crop_proc_counter[crop_name] += 1
            if buyer_name:
                buyer_counter[buyer_name] += 1
            if proc.farmer_id:
                farmer_revenue[proc.farmer_id] += amt
                prev = farmer_last_proc.get(proc.farmer_id)
                if prev is None or proc.procurement_date > prev:
                    farmer_last_proc[proc.farmer_id] = proc.procurement_date
            if proc.buyer_id:
                buyer_qty[proc.buyer_id] += qty
                buyer_names[proc.buyer_id] = buyer_name or "Buyer"
                if proc.rate_per_quintal and proc.rate_per_quintal > 0:
                    buyer_rate_sum[proc.buyer_id] += Decimal(str(proc.rate_per_quintal))
                    buyer_rate_n[proc.buyer_id] += 1
                last = buyer_last.get(proc.buyer_id)
                if last is None or proc.procurement_date > last:
                    buyer_last[proc.buyer_id] = proc.procurement_date
            if proc.rate_per_quintal and proc.rate_per_quintal > 0:
                rates.append(Decimal(str(proc.rate_per_quintal)))
            if proc.expected_payment_date and proc.actual_payment_date:
                delays.append((proc.actual_payment_date - proc.expected_payment_date).days)
            season_rev[_season_key(proc.procurement_date)] += amt
            year_rev[str(proc.procurement_date.year)] += amt
        else:
            expected += qty
        if proc.procurement_date == today:
            today_qty += qty
        if season_start <= proc.procurement_date <= season_end and proc.status in _CONFIRMED:
            season_qty += qty

    # Services via farmers in village
    services_tab: list[VillageServiceRow] = []
    vehicle_agg: dict[str, dict] = defaultdict(
        lambda: {
            "asset_id": None,
            "vehicle_type": None,
            "hours": _ZERO,
            "trips": 0,
            "diesel": _ZERO,
            "revenue": _ZERO,
            "operator": None,
            "status": "active",
        }
    )
    tractor = rotavator = cultivator = baler = diesel = svc_pending = _ZERO
    bolero_trips = dcm_trips = 0
    vehicle_counter: Counter[str] = Counter()
    farmer_last_svc: dict[UUID, date] = {}

    if farmer_ids:
        svc_rows = (
            db.query(FieldServiceRecord, Asset.name, VehicleType.name, VehicleType.code, Farmer.full_name)
            .outerjoin(Asset, Asset.id == FieldServiceRecord.asset_id)
            .outerjoin(VehicleType, VehicleType.id == FieldServiceRecord.vehicle_type_id)
            .outerjoin(Farmer, Farmer.id == FieldServiceRecord.farmer_id)
            .filter(
                FieldServiceRecord.org_id == org_id,
                FieldServiceRecord.farmer_id.in_(farmer_ids),
                FieldServiceRecord.deleted_at.is_(None),
            )
            .order_by(FieldServiceRecord.service_date.desc())
            .limit(200)
            .all()
        )
        for row, asset_name, vt_name, vt_code, fname in svc_rows:
            hours = Decimal(str(row.hours or 0))
            diesel_amt = _money(row.diesel_amount)
            charged = _money(row.total_amount)
            diesel += diesel_amt
            svc_pending += _money(row.pending_amount)
            kind = _vehicle_kind(vt_code or vt_name or asset_name)
            if kind == "tractor":
                tractor += hours
            elif kind == "rotavator":
                rotavator += hours
            elif kind == "cultivator":
                cultivator += hours
            elif kind == "baler":
                baler += hours
            elif kind == "bolero":
                bolero_trips += int(row.bag_count or 1)
            elif kind == "dcm":
                dcm_trips += int(row.bag_count or 1)

            label = asset_name or vt_name or "Unknown vehicle"
            vehicle_counter[label] += 1
            agg = vehicle_agg[label]
            if row.asset_id:
                agg["asset_id"] = row.asset_id
            agg["vehicle_type"] = vt_name
            agg["hours"] += hours
            agg["trips"] += int(row.bag_count or 0)
            agg["diesel"] += diesel_amt
            agg["revenue"] += charged

            if row.farmer_id:
                prev = farmer_last_svc.get(row.farmer_id)
                if prev is None or row.service_date > prev:
                    farmer_last_svc[row.farmer_id] = row.service_date

            services_tab.append(
                VillageServiceRow(
                    id=row.id,
                    record_number=row.record_number,
                    service_date=row.service_date,
                    service_category=row.service_category,
                    farmer_name=fname,
                    vehicle_name=asset_name,
                    vehicle_type=vt_name,
                    hours=row.hours,
                    diesel_amount=diesel_amt,
                    amount_charged=charged,
                    status=row.status,
                )
            )

    vehicles_tab = [
        VillageVehicleRow(
            asset_id=data["asset_id"],
            vehicle_name=name,
            vehicle_type=data["vehicle_type"],
            hours=_money(data["hours"]),
            trips=data["trips"],
            diesel=_money(data["diesel"]),
            revenue=_money(data["revenue"]),
            operator=data["operator"],
            status=data["status"],
            profile_href=f"/vehicles?asset_id={data['asset_id']}" if data["asset_id"] else "/vehicles",
        )
        for name, data in sorted(vehicle_agg.items(), key=lambda x: x[1]["revenue"], reverse=True)
    ]

    # Payments + finance
    payments_tab: list[VillagePaymentRow] = []
    finance_tab: list[VillageFinanceRow] = []
    if farmer_ids:
        pay_rows = (
            db.query(FarmerPayment, Farmer.full_name, PaymentMode.name)
            .join(Farmer, Farmer.id == FarmerPayment.farmer_id)
            .outerjoin(PaymentMode, PaymentMode.id == FarmerPayment.payment_mode_id)
            .filter(FarmerPayment.org_id == org_id, FarmerPayment.farmer_id.in_(farmer_ids))
            .order_by(FarmerPayment.payment_date.desc())
            .limit(100)
            .all()
        )
        for pay, fname, mode_name in pay_rows:
            payments_tab.append(
                VillagePaymentRow(
                    id=pay.id,
                    payment_number=pay.payment_number,
                    payment_date=pay.payment_date,
                    farmer_name=fname,
                    amount=_money(pay.amount),
                    payment_mode=mode_name,
                    status=pay.status,
                )
            )

        fin_rows = (
            db.query(FieldServiceRecord, Farmer.full_name)
            .join(Farmer, Farmer.id == FieldServiceRecord.farmer_id)
            .filter(
                FieldServiceRecord.org_id == org_id,
                FieldServiceRecord.farmer_id.in_(farmer_ids),
                FieldServiceRecord.service_category == "agri_finance",
                FieldServiceRecord.deleted_at.is_(None),
            )
            .order_by(FieldServiceRecord.service_date.desc())
            .all()
        )
        for row, fname in fin_rows:
            finance_tab.append(
                VillageFinanceRow(
                    id=row.id,
                    record_number=row.record_number,
                    loan_date=row.service_date,
                    farmer_name=fname,
                    amount=_money(row.amount_given or row.total_amount),
                    outstanding=_money(row.pending_amount),
                    status=row.status,
                )
            )

    outstanding_total = _ZERO
    farmers_tab: list[VillageFarmerRow] = []
    for f in farmers:
        out = farmer_outstanding(db, org_id, f.id)
        outstanding_total += out
        current_crop = None
        for c, cn, _fn in crop_rows:
            if c.farmer_id == f.id:
                current_crop = cn
                break
        farmers_tab.append(
            VillageFarmerRow(
                id=f.id,
                farmer_code=f.farmer_code,
                full_name=f.full_name,
                phone_primary=f.phone_primary,
                trust_rating=f.trust_rating,
                is_vip=bool(f.is_vip),
                status=f.status,
                current_crop=current_crop,
                outstanding=_money(out),
                lifetime_revenue=_money(farmer_revenue.get(f.id, _ZERO)),
                last_service_date=farmer_last_svc.get(f.id),
                last_procurement_date=farmer_last_proc.get(f.id),
                profile_href=f"/farmers/{f.id}",
            )
        )

    buyers_tab = [
        VillageBuyerRow(
            id=bid,
            name=buyer_names[bid],
            quantity_purchased_kg=_money(buyer_qty[bid]),
            average_rate=(
                (buyer_rate_sum[bid] / buyer_rate_n[bid]).quantize(Decimal("0.01"))
                if buyer_rate_n[bid]
                else None
            ),
            outstanding=_ZERO,
            last_purchase_date=buyer_last.get(bid),
        )
        for bid in buyer_qty
    ]

    # Comments + documents on village entity
    comments = (
        db.query(EntityComment, User.full_name)
        .outerjoin(User, User.id == EntityComment.author_user_id)
        .filter(
            EntityComment.org_id == org_id,
            EntityComment.entity_type == "village",
            EntityComment.entity_id == village_id,
            EntityComment.deleted_at.is_(None),
        )
        .order_by(EntityComment.created_at.desc())
        .limit(50)
        .all()
    )
    comments_tab = [
        VillageCommentRow(id=c.id, body=c.body, author_name=author, created_at=c.created_at)
        for c, author in comments
    ]

    docs = (
        db.query(Document)
        .join(DocumentLink, DocumentLink.document_id == Document.id)
        .filter(
            Document.org_id == org_id,
            DocumentLink.entity_type == "village",
            DocumentLink.entity_id == village_id,
        )
        .order_by(Document.created_at.desc())
        .limit(50)
        .all()
    )
    documents_tab = [
        VillageDocumentRow(
            id=d.id,
            document_type=d.document_type,
            file_name=d.file_name,
            mime_type=d.mime_type,
            created_at=d.created_at,
        )
        for d in docs
    ]

    # Timeline
    timeline: list[VillageTimelineEvent] = [
        VillageTimelineEvent(
            event_type="village_created",
            title="Village registered",
            description=village.name,
            occurred_at=village.created_at if village.created_at.tzinfo else village.created_at.replace(tzinfo=UTC),
            entity_type="village",
            entity_id=village.id,
        )
    ]
    for p in procurements_tab[:40]:
        timeline.append(
            VillageTimelineEvent(
                event_type="procurement",
                title=f"Procurement {p.procurement_number}",
                description=f"{p.farmer_name} · {p.crop_name}",
                occurred_at=datetime.combine(p.procurement_date, datetime.min.time(), tzinfo=UTC),
                entity_type="procurement",
                entity_id=p.id,
                amount=p.net_amount,
            )
        )
    for s in services_tab[:40]:
        timeline.append(
            VillageTimelineEvent(
                event_type="service",
                title=f"Service {s.service_category}",
                description=s.farmer_name,
                occurred_at=datetime.combine(s.service_date, datetime.min.time(), tzinfo=UTC),
                entity_type="field_service",
                entity_id=s.id,
                amount=s.amount_charged,
            )
        )
    for c in comments_tab[:20]:
        timeline.append(
            VillageTimelineEvent(
                event_type="comment",
                title="Comment",
                description=c.body[:160],
                occurred_at=c.created_at if c.created_at.tzinfo else c.created_at.replace(tzinfo=UTC),
                entity_type="comment",
                entity_id=c.id,
            )
        )
    timeline.sort(key=lambda e: e.occurred_at, reverse=True)
    timeline = timeline[:120]

    diesel_cost = diesel  # diesel stored as amount (INR) on field services
    profit = _money(revenue - diesel_cost)  # simplified village P&L proxy

    stats = Village360Statistics(
        total_farmers=len(farmers),
        active_farmers=sum(1 for f in farmers if f.status == "active"),
        vip_farmers=sum(1 for f in farmers if f.is_vip),
        total_cultivated_area=land_acres or (paddy + corn + other),
        own_farming_area=own_area,
        total_paddy_area=paddy,
        total_corn_area=corn,
        total_other_crops_area=other,
        expected_procurement_kg=_money(expected),
        actual_procurement_kg=_money(actual),
        todays_procurement_kg=_money(today_qty),
        current_season_procurement_kg=_money(season_qty),
        total_tractor_hours=_money(tractor),
        total_rotavator_hours=_money(rotavator),
        total_cultivator_hours=_money(cultivator),
        total_baler_hours=_money(baler),
        total_bolero_trips=bolero_trips,
        total_dcm_trips=dcm_trips,
        diesel_consumed=_money(diesel),
        outstanding_payments=_money(outstanding_total),
        revenue=_money(revenue),
        profit=profit,
        pending_collections=_money(svc_pending + outstanding_total),
    )

    top_farmer = None
    if farmer_revenue:
        top_id = max(farmer_revenue.items(), key=lambda x: x[1])[0]
        top_farmer = farmer_name.get(top_id)

    analytics = VillageAnalytics(
        top_crop=(crop_proc_counter or crop_counter).most_common(1)[0][0]
        if (crop_proc_counter or crop_counter)
        else None,
        top_farmer=top_farmer,
        top_buyer=buyer_counter.most_common(1)[0][0] if buyer_counter else None,
        most_used_vehicle=vehicle_counter.most_common(1)[0][0] if vehicle_counter else None,
        average_yield=(sum(yields) / len(yields)).quantize(Decimal("0.001")) if yields else None,
        average_procurement_rate=(sum(rates) / len(rates)).quantize(Decimal("0.01")) if rates else None,
        average_payment_delay_days=(Decimal(sum(delays)) / len(delays)).quantize(Decimal("0.1"))
        if delays
        else None,
        village_growth_farmers=len(farmers),
        revenue_trend={k: _money(v) for k, v in year_rev.items()},
        season_comparison={k: _money(v) for k, v in season_rev.items()},
    )

    farm_gps = sum(1 for f in own_farms if f.geo_lat and f.geo_lng)
    farmer_gps = sum(1 for f in farmers if f.geo_lat and f.geo_lng)

    map_ready = VillageMapReady(
        village_center={"lat": village.geo_lat, "lng": village.geo_lng},
        farmer_locations_count=farmer_gps,
        farm_locations_count=farm_gps,
        supports_boundary=False,
        supports_live_vehicles=False,
    )

    vid = str(village_id)
    reports = [
        VillageReportLink(code="revenue", title="Village Revenue", href=f"/reports?village_id={vid}&type=revenue"),
        VillageReportLink(code="profit", title="Village Profit", href=f"/reports?village_id={vid}&type=profit"),
        VillageReportLink(
            code="procurement", title="Village Procurement", href=f"/reports?village_id={vid}&type=procurement"
        ),
        VillageReportLink(code="farming", title="Village Farming", href=f"/reports?village_id={vid}&type=farming"),
        VillageReportLink(
            code="vehicle_util",
            title="Village Vehicle Utilization",
            href=f"/reports?village_id={vid}&type=vehicle",
        ),
        VillageReportLink(
            code="outstanding", title="Village Outstanding", href=f"/reports?village_id={vid}&type=outstanding"
        ),
        VillageReportLink(
            code="crop_summary", title="Village Crop Summary", href=f"/reports?village_id={vid}&type=crops"
        ),
    ]

    return Village360ProfileResponse(
        summary=summary,
        statistics=stats,
        farmers=farmers_tab,
        procurements=procurements_tab,
        services=services_tab,
        vehicles=vehicles_tab,
        payments=payments_tab,
        finance=finance_tab,
        farming=farming_tab[:100],
        buyers=buyers_tab,
        comments=comments_tab,
        documents=documents_tab,
        timeline=timeline,
        analytics=analytics,
        map=map_ready,
        reports=reports,
    )


def search_villages(db: Session, org_id: UUID, q: str, *, limit: int = 30) -> VillageSearchResponse:
    term = q.strip()
    if not term:
        return VillageSearchResponse(items=[], total=0, q=q)

    like = f"%{term}%"
    # Direct village / mandal / district / code hits
    direct = (
        db.query(Village)
        .filter(
            Village.org_id == org_id,
            Village.deleted_at.is_(None),
            or_(
                Village.name.ilike(like),
                Village.village_code.ilike(like),
                Village.mandal.ilike(like),
                Village.district.ilike(like),
            ),
        )
        .order_by(Village.name)
        .limit(limit)
        .all()
    )
    hits: dict[UUID, VillageSearchHit] = {}
    for v in direct:
        reason = "village"
        if v.mandal and term.lower() in (v.mandal or "").lower():
            reason = "mandal"
        elif v.district and term.lower() in (v.district or "").lower():
            reason = "district"
        hits[v.id] = VillageSearchHit(
            id=v.id,
            village_code=v.village_code,
            name=v.name,
            mandal=v.mandal,
            district=v.district,
            match_reason=reason,
        )

    # Farmer name/phone → villages
    farmer_hits = (
        db.query(Village, Farmer)
        .join(Farmer, Farmer.village_id == Village.id)
        .filter(
            Village.org_id == org_id,
            Village.deleted_at.is_(None),
            Farmer.deleted_at.is_(None),
            or_(Farmer.full_name.ilike(like), Farmer.phone_primary.ilike(like), Farmer.farmer_code.ilike(like)),
        )
        .limit(limit)
        .all()
    )
    for v, farmer in farmer_hits:
        if v.id not in hits:
            hits[v.id] = VillageSearchHit(
                id=v.id,
                village_code=v.village_code,
                name=v.name,
                mandal=v.mandal,
                district=v.district,
                match_reason=f"farmer:{farmer.full_name}",
            )

    # Buyer → villages via procurements
    buyer_hits = (
        db.query(Village, Buyer)
        .join(Procurement, Procurement.village_id == Village.id)
        .join(Buyer, Buyer.id == Procurement.buyer_id)
        .filter(
            Village.org_id == org_id,
            Village.deleted_at.is_(None),
            Buyer.deleted_at.is_(None),
            Buyer.name.ilike(like),
        )
        .limit(limit)
        .all()
    )
    for v, buyer in buyer_hits:
        if v.id not in hits:
            hits[v.id] = VillageSearchHit(
                id=v.id,
                village_code=v.village_code,
                name=v.name,
                mandal=v.mandal,
                district=v.district,
                match_reason=f"buyer:{buyer.name}",
            )

    # Crop → villages via procurements
    crop_hits = (
        db.query(Village, CropType)
        .join(Procurement, Procurement.village_id == Village.id)
        .join(CropType, CropType.id == Procurement.crop_type_id)
        .filter(
            Village.org_id == org_id,
            Village.deleted_at.is_(None),
            CropType.deleted_at.is_(None),
            or_(CropType.name.ilike(like), CropType.code.ilike(like)),
        )
        .limit(limit)
        .all()
    )
    for v, crop in crop_hits:
        if v.id not in hits:
            hits[v.id] = VillageSearchHit(
                id=v.id,
                village_code=v.village_code,
                name=v.name,
                mandal=v.mandal,
                district=v.district,
                match_reason=f"crop:{crop.name}",
            )

    items = list(hits.values())[:limit]
    # attach farmer counts
    if items:
        ids = [i.id for i in items]
        counts = (
            db.query(Farmer.village_id, func.count(Farmer.id))
            .filter(Farmer.org_id == org_id, Farmer.village_id.in_(ids), Farmer.deleted_at.is_(None))
            .group_by(Farmer.village_id)
            .all()
        )
        cmap = {vid: n for vid, n in counts}
        items = [i.model_copy(update={"farmer_count": cmap.get(i.id, 0)}) for i in items]

    return VillageSearchResponse(items=items, total=len(items), q=q)
