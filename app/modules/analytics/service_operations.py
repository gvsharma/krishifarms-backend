"""Operations Command Center analytics."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.analytics import queries as q
from app.modules.analytics.filters import OPEN_PROCUREMENT_STATUSES, drill_query, resolve_date_range
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


def build_operations_summary(
    db: Session,
    org_id: UUID,
    filters: AnalyticsFilter,
    *,
    today: date | None = None,
) -> ModuleSummaryResponse:
    today = today or date.today()
    if not filters.preset and not filters.date_from and not filters.date_to:
        filters = filters.model_copy(update={"preset": "today"})
    date_from, date_to = resolve_date_range(filters, today=today)

    open_procs = q.count_procurements(
        db, org_id, date_from, date_to, statuses=OPEN_PROCUREMENT_STATUSES, village_id=filters.village_id
    )
    confirmed = q.count_procurements(
        db,
        org_id,
        date_from,
        date_to,
        statuses=frozenset({"confirmed", "paid_partial", "paid_full"}),
        village_id=filters.village_id,
    )
    fs_count = q.count_field_services(db, org_id, date_from, date_to)
    fleet = q.fleet_pulse(db, org_id, date_from, date_to)
    kg = q.sum_procurement_kg(
        db, org_id, date_from, date_to, village_id=filters.village_id, crop_type_id=filters.crop_type_id
    )

    drill = drill_query(
        "/procurement",
        date_from=date_from,
        date_to=date_to,
        village_id=filters.village_id,
        crop_type_id=filters.crop_type_id,
    )

    kpis = [
        KpiCard(
            id="open_procurements",
            label="Open procurements",
            value=open_procs,
            format="number",
            status="live",
            drill=DrillLink(href=drill),
        ),
        KpiCard(
            id="confirmed_procurements",
            label="Confirmed tickets",
            value=confirmed,
            format="number",
            status="live",
            drill=DrillLink(href=drill),
        ),
        KpiCard(
            id="procurement_kg",
            label="Net weight",
            value=kg,
            unit="kg",
            format="number",
            status="live",
            drill=DrillLink(href=drill),
        ),
        KpiCard(
            id="field_services",
            label="Field services",
            value=fs_count,
            format="number",
            status="live",
            drill=DrillLink(
                href=drill_query("/field-services", date_from=date_from, date_to=date_to),
            ),
        ),
        KpiCard(
            id="trips",
            label="Vehicle trips",
            value=fleet["trips"],
            format="number",
            status="live",
            drill=DrillLink(href="/vehicles"),
        ),
        KpiCard(
            id="fleet_working",
            label="Assets working / idle",
            value=f"{fleet['working']} / {fleet['idle']}",
            format="text",
            status="live",
        ),
    ]

    series = [
        SeriesPoint(x=d.isoformat(), y=amt, series="procurement_revenue")
        for d, amt in q.revenue_series_by_day(
            db, org_id, date_from, date_to, village_id=filters.village_id
        )
    ]

    villages = q.top_villages_by_procurement(db, org_id, date_from, date_to, limit=10)
    tables = [
        TablePage(
            id="ops_top_villages",
            title="Top villages (ops)",
            columns=[
                TableColumn(key="name", label="Village"),
                TableColumn(key="tickets", label="Tickets", format="number"),
                TableColumn(key="kg", label="Net kg", format="number"),
                TableColumn(key="amount", label="Amount", format="money"),
            ],
            rows=[
                TableRow(
                    cells={
                        "name": v["name"],
                        "tickets": v["tickets"],
                        "kg": v["kg"],
                        "amount": v["amount"],
                    }
                )
                for v in villages
            ],
            total=len(villages),
        )
    ]

    return ModuleSummaryResponse(
        module="operations",
        status="live",
        filters=AnalyticsFilter(
            date_from=date_from,
            date_to=date_to,
            village_id=filters.village_id,
            crop_type_id=filters.crop_type_id,
            farmer_id=filters.farmer_id,
            buyer_id=filters.buyer_id,
            asset_id=filters.asset_id,
            season=filters.season,
            preset=filters.preset or "today",
        ),
        kpis=kpis,
        series_preview=series,
        tables_preview=tables,
        data_availability=[
            DataAvailabilityItem(source="procurements", status="available"),
            DataAvailabilityItem(source="field_service_records", status="available"),
            DataAvailabilityItem(source="vehicle_trips", status="available"),
            DataAvailabilityItem(source="assets", status="available"),
        ],
    )
