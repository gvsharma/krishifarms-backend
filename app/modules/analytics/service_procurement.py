"""Procurement analytics module."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.analytics import queries as q
from app.modules.analytics.filters import CONFIRMED_PROCUREMENT_STATUSES, drill_query, resolve_date_range
from app.modules.analytics.schemas import (
    AnalyticsFilter,
    DataAvailabilityItem,
    DrillLink,
    KpiCard,
    ModuleSummaryResponse,
    SeriesPoint,
    TableColumn,
    TablePage,
    TableRow,
)


def build_procurement_summary(
    db: Session,
    org_id: UUID,
    filters: AnalyticsFilter,
    *,
    today: date | None = None,
) -> ModuleSummaryResponse:
    today = today or date.today()
    date_from, date_to = resolve_date_range(filters, today=today)
    village_id = filters.village_id
    crop_type_id = filters.crop_type_id
    buyer_id = filters.buyer_id
    farmer_id = filters.farmer_id

    amount = q.sum_procurement_revenue(
        db,
        org_id,
        date_from,
        date_to,
        village_id=village_id,
        crop_type_id=crop_type_id,
        farmer_id=farmer_id,
        buyer_id=buyer_id,
    )
    weight = q.sum_procurement_kg(
        db, org_id, date_from, date_to, village_id=village_id, crop_type_id=crop_type_id
    )
    tickets = q.count_procurements(
        db, org_id, date_from, date_to, statuses=CONFIRMED_PROCUREMENT_STATUSES, village_id=village_id
    )
    moisture = q.avg_moisture(db, org_id, date_from, date_to)
    pending_count, pending_amount = q.pending_unpaid_procurements(db, org_id, date_from, date_to)

    drill = drill_query(
        "/procurement",
        date_from=date_from,
        date_to=date_to,
        village_id=village_id,
        crop_type_id=crop_type_id,
        farmer_id=farmer_id,
        buyer_id=buyer_id,
    )

    kpis = [
        KpiCard(
            id="net_amount",
            label="Confirmed value",
            label_te="నిర్ధారిత విలువ",
            value=amount,
            unit="INR",
            format="money",
            status="live",
            drill=DrillLink(href=drill),
        ),
        KpiCard(
            id="net_weight",
            label="Confirmed weight",
            value=weight,
            unit="kg",
            format="number",
            status="live",
            drill=DrillLink(href=drill),
        ),
        KpiCard(
            id="tickets",
            label="Confirmed tickets",
            value=tickets,
            format="number",
            status="live",
            drill=DrillLink(href=drill),
        ),
        KpiCard(
            id="avg_moisture",
            label="Avg moisture",
            value=moisture if moisture is not None else "—",
            unit="%",
            format="number" if moisture is not None else "text",
            status="live" if moisture is not None else "unavailable",
        ),
        KpiCard(
            id="unpaid",
            label="Unpaid / partial",
            value=pending_amount,
            unit="INR",
            format="money",
            status="live",
            note=f"{pending_count} tickets",
            drill=DrillLink(href=drill),
        ),
    ]

    series = [
        SeriesPoint(x=d.isoformat(), y=amt, series="procurement_revenue")
        for d, amt in q.revenue_series_by_day(db, org_id, date_from, date_to, village_id=village_id)
    ]

    crops = q.top_crops_by_procurement(db, org_id, date_from, date_to, limit=10)
    villages = q.top_villages_by_procurement(db, org_id, date_from, date_to, limit=10)
    tables = [
        TablePage(
            id="top_crops",
            title="Top crops",
            columns=[
                TableColumn(key="name", label="Crop"),
                TableColumn(key="kg", label="Net kg", format="number"),
                TableColumn(key="amount", label="Amount", format="money"),
                TableColumn(key="tickets", label="Tickets", format="number"),
            ],
            rows=[
                TableRow(
                    cells={"name": c["name"], "kg": c["kg"], "amount": c["amount"], "tickets": c["tickets"]}
                )
                for c in crops
            ],
            total=len(crops),
        ),
        TablePage(
            id="top_villages",
            title="Top villages",
            columns=[
                TableColumn(key="name", label="Village"),
                TableColumn(key="kg", label="Net kg", format="number"),
                TableColumn(key="amount", label="Amount", format="money"),
                TableColumn(key="tickets", label="Tickets", format="number"),
            ],
            rows=[
                TableRow(
                    cells={"name": v["name"], "kg": v["kg"], "amount": v["amount"], "tickets": v["tickets"]}
                )
                for v in villages
            ],
            total=len(villages),
        ),
    ]

    return ModuleSummaryResponse(
        module="procurement",
        status="live",
        filters=AnalyticsFilter(
            date_from=date_from,
            date_to=date_to,
            village_id=village_id,
            crop_type_id=crop_type_id,
            farmer_id=farmer_id,
            buyer_id=buyer_id,
            asset_id=filters.asset_id,
            season=filters.season,
            preset=filters.preset,
        ),
        kpis=kpis,
        series_preview=series,
        tables_preview=tables,
        data_availability=[
            DataAvailabilityItem(source="procurements", status="available"),
            DataAvailabilityItem(source="procurement_deductions", status="partial", notes="Not yet rolled into KPIs"),
        ],
    )
