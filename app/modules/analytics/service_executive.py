"""Executive analytics — morning health + money + ops pulse."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.analytics import queries as q
from app.modules.analytics.filters import OPEN_PROCUREMENT_STATUSES, drill_query, money, resolve_date_range
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


def build_executive_summary(
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
    farmer_id = filters.farmer_id
    buyer_id = filters.buyer_id

    # Period revenue = confirmed procurements + field-service amounts
    proc_revenue = q.sum_procurement_revenue(
        db,
        org_id,
        date_from,
        date_to,
        village_id=village_id,
        crop_type_id=crop_type_id,
        farmer_id=farmer_id,
        buyer_id=buyer_id,
    )
    proc_gross = q.sum_procurement_gross(
        db,
        org_id,
        date_from,
        date_to,
        village_id=village_id,
        crop_type_id=crop_type_id,
        farmer_id=farmer_id,
        buyer_id=buyer_id,
    )
    proc_margin = q.sum_procurement_margin(
        db,
        org_id,
        date_from,
        date_to,
        village_id=village_id,
        crop_type_id=crop_type_id,
        farmer_id=farmer_id,
        buyer_id=buyer_id,
    )
    fs_revenue = q.sum_field_service_amount(db, org_id, date_from, date_to, farmer_id=farmer_id)
    revenue = money(proc_revenue + fs_revenue)
    expenses = q.sum_expenses(db, org_id, date_from, date_to)
    profit = money(revenue - expenses)
    outstanding = q.sum_org_outstanding(db, org_id)
    pending_count, pending_amount = q.pending_unpaid_procurements(db, org_id, date_from, date_to)
    farmers = q.farmer_counts(db, org_id, village_id=village_id)
    fleet = q.fleet_pulse(db, org_id, date_from, date_to)
    open_procs = q.count_procurements(
        db, org_id, date_from, date_to, statuses=OPEN_PROCUREMENT_STATUSES, village_id=village_id
    )
    fs_count = q.count_field_services(db, org_id, date_from, date_to)

    health = q.rules_v1_health_score(
        outstanding=outstanding,
        revenue=revenue,
        open_procurements=open_procs,
        trips=fleet["trips"],
        field_services=fs_count,
    )

    drill_proc = drill_query(
        "/procurement",
        date_from=date_from,
        date_to=date_to,
        village_id=village_id,
        crop_type_id=crop_type_id,
        farmer_id=farmer_id,
        buyer_id=buyer_id,
    )
    drill_expenses = drill_query("/expenses", date_from=date_from, date_to=date_to)
    drill_farmers = drill_query("/farmers", village_id=village_id)
    drill_payments = drill_query("/payments", date_from=date_from, date_to=date_to)

    kpis = [
        KpiCard(
            id="revenue",
            label="Farmer net (procurement)",
            label_te="రైతుకు చెల్లింపు",
            value=proc_revenue,
            unit="INR",
            format="money",
            status="live",
            note="Sum of confirmed procurement net_amount (payable to farmers).",
            drill=DrillLink(href=drill_proc, label="View procurements"),
        ),
        KpiCard(
            id="procurement_gross",
            label="Procurement gross",
            label_te="స్థూల కొనుగోలు",
            value=proc_gross,
            unit="INR",
            format="money",
            status="live",
            note="Sum of gross_amount before line/spot deductions.",
            drill=DrillLink(href=drill_proc, label="View procurements"),
        ),
        KpiCard(
            id="procurement_margin",
            label="Procurement margin",
            label_te="కొనుగోలు మార్జిన్",
            value=proc_margin,
            unit="INR",
            format="money",
            status="live",
            note="Buyer margin: kata weight profit + spot retention + sale-rate spread.",
            drill=DrillLink(href=drill_proc, label="View procurements"),
        ),
        KpiCard(
            id="expenses",
            label="Period expenses",
            label_te="ఖర్చులు",
            value=expenses,
            unit="INR",
            format="money",
            status="live",
            drill=DrillLink(href=drill_expenses, label="View expenses"),
        ),
        KpiCard(
            id="profit",
            label="Gross ops estimate",
            label_te="స్థూల అంచనా లాభం",
            value=profit,
            unit="INR",
            format="money",
            status="estimate",
            note="Farmer net + field services − expenses. Not GAAP P&L.",
        ),
        KpiCard(
            id="outstanding",
            label="Farmer outstanding",
            label_te="బాకీ",
            value=outstanding,
            unit="INR",
            format="money",
            status="live",
            note="Sum of latest ledger balance_after per farmer.",
            drill=DrillLink(href=drill_payments, label="View payments"),
        ),
        KpiCard(
            id="pending_payments",
            label="Pending farmer payments",
            label_te="పెండింగ్ చెల్లింపులు",
            value=pending_amount,
            unit="INR",
            format="money",
            status="live",
            note=f"{pending_count} confirmed/paid_partial tickets in range.",
            drill=DrillLink(href=drill_proc, label="View procurements"),
        ),
        KpiCard(
            id="farmers_active",
            label="Active farmers",
            label_te="యాక్టివ్ రైతులు",
            value=farmers["active"],
            format="number",
            status="live",
            note=f"Total {farmers['total']}; VIP {farmers['vip']}.",
            drill=DrillLink(href=drill_farmers, label="View farmers"),
        ),
        KpiCard(
            id="fleet",
            label="Vehicles working / idle",
            label_te="వాహనాలు",
            value=f"{fleet['working']} / {fleet['idle']}",
            format="text",
            status="live",
            note=f"{fleet['trips']} trips in range.",
            drill=DrillLink(href="/vehicles", label="View vehicles"),
        ),
        KpiCard(
            id="open_procurements",
            label="Open procurements",
            label_te="ఓపెన్ కొనుగోళ్లు",
            value=open_procs,
            format="number",
            status="live",
            drill=DrillLink(href=drill_proc, label="View procurements"),
        ),
        KpiCard(
            id="farming_activities",
            label="Field services",
            label_te="ఫీల్డ్ సేవలు",
            value=fs_count,
            format="number",
            status="live",
            drill=DrillLink(
                href=drill_query("/field-services", date_from=date_from, date_to=date_to),
                label="View field services",
            ),
        ),
        KpiCard(
            id="cash_available",
            label="Cash available",
            label_te="నగదు",
            value=None,
            format="text",
            status="unavailable",
            note="Requires cash book / bank balance truth — not invented in Phase 1.",
        ),
        KpiCard(
            id="weather",
            label="Weather / disease",
            value=None,
            format="text",
            status="unavailable",
            note="No weather/disease integration.",
        ),
    ]

    series = [
        SeriesPoint(x=d.isoformat(), y=amt, series="procurement_revenue")
        for d, amt in q.revenue_series_by_day(db, org_id, date_from, date_to, village_id=village_id)
    ]
    series.extend(
        SeriesPoint(x=d.isoformat(), y=amt, series="procurement_margin")
        for d, amt in q.procurement_margin_series_by_day(
            db, org_id, date_from, date_to, village_id=village_id
        )
    )
    series.extend(
        SeriesPoint(x=d.isoformat(), y=amt, series="profit")
        for d, amt in q.profit_series_by_day(db, org_id, date_from, date_to, village_id=village_id)
    )
    series.extend(
        SeriesPoint(x=d.isoformat(), y=amt, series="expenses")
        for d, amt in q.expense_series_by_day(db, org_id, date_from, date_to)
    )

    villages = q.top_villages_by_procurement(db, org_id, date_from, date_to, limit=10)
    farmers = q.top_farmers_by_revenue(db, org_id, date_from, date_to, limit=10)
    crops = q.top_crops_by_procurement(db, org_id, date_from, date_to, limit=10)
    tables = [
        TablePage(
            id="top_villages",
            title="Profit by village",
            columns=[
                TableColumn(key="name", label="Village"),
                TableColumn(key="kg", label="Net kg", format="number"),
                TableColumn(key="gross", label="Gross", format="money"),
                TableColumn(key="net", label="Net to farmer", format="money"),
                TableColumn(key="profit", label="Margin", format="money"),
                TableColumn(key="tickets", label="Tickets", format="number"),
            ],
            rows=[
                TableRow(
                    cells={
                        "name": v["name"],
                        "kg": v["kg"],
                        "gross": v["gross"],
                        "net": v["net"],
                        "profit": v["profit"],
                        "tickets": v["tickets"],
                    }
                )
                for v in villages
            ],
            total=len(villages),
        ),
        TablePage(
            id="top_farmers",
            title="Profit by farmer",
            columns=[
                TableColumn(key="name", label="Farmer"),
                TableColumn(key="gross", label="Gross", format="money"),
                TableColumn(key="net", label="Net to farmer", format="money"),
                TableColumn(key="profit", label="Margin", format="money"),
                TableColumn(key="tickets", label="Tickets", format="number"),
            ],
            rows=[
                TableRow(
                    cells={
                        "name": f["name"],
                        "gross": f["gross"],
                        "net": f["net"],
                        "profit": f["profit"],
                        "tickets": f["tickets"],
                    }
                )
                for f in farmers
            ],
            total=len(farmers),
        ),
        TablePage(
            id="top_crops",
            title="Profit by crop",
            columns=[
                TableColumn(key="name", label="Crop"),
                TableColumn(key="gross", label="Gross", format="money"),
                TableColumn(key="net", label="Net to farmer", format="money"),
                TableColumn(key="profit", label="Margin", format="money"),
                TableColumn(key="tickets", label="Tickets", format="number"),
            ],
            rows=[
                TableRow(
                    cells={
                        "name": c["name"],
                        "gross": c["gross"],
                        "net": c["net"],
                        "profit": c["profit"],
                        "tickets": c["tickets"],
                    }
                )
                for c in crops
            ],
            total=len(crops),
        ),
    ]

    return ModuleSummaryResponse(
        module="executive",
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
            DataAvailabilityItem(source="field_service_records", status="available"),
            DataAvailabilityItem(source="expenses", status="available"),
            DataAvailabilityItem(source="farmer_ledger_entries", status="available"),
            DataAvailabilityItem(
                source="cash_book",
                status="missing",
                notes="Cash available / working capital not live",
            ),
            DataAvailabilityItem(source="weather", status="missing"),
        ],
        health_score=health,
        health_score_method="rules_v1",
    )
