"""Finance dashboard analytics."""

from __future__ import annotations

from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.analytics import queries as q
from app.modules.analytics.filters import drill_query, money, resolve_date_range
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


def build_finance_summary(
    db: Session,
    org_id: UUID,
    filters: AnalyticsFilter,
    *,
    today: date | None = None,
) -> ModuleSummaryResponse:
    today = today or date.today()
    date_from, date_to = resolve_date_range(filters, today=today)

    expenses = q.sum_expenses(db, org_id, date_from, date_to)
    collections = q.sum_collections(db, org_id, date_from, date_to)
    outstanding = q.sum_org_outstanding(db, org_id)
    pending_count, pending_amount = q.pending_unpaid_procurements(db, org_id, date_from, date_to)
    proc_revenue = q.sum_procurement_revenue(db, org_id, date_from, date_to)
    net_ops = money(proc_revenue + collections - expenses)

    kpis = [
        KpiCard(
            id="expenses",
            label="Posted expenses",
            label_te="ఖర్చులు",
            value=expenses,
            unit="INR",
            format="money",
            status="live",
            drill=DrillLink(href=drill_query("/expenses", date_from=date_from, date_to=date_to)),
        ),
        KpiCard(
            id="collections",
            label="Collections",
            label_te="వసూళ్లు",
            value=collections,
            unit="INR",
            format="money",
            status="live",
            drill=DrillLink(href=drill_query("/collections", date_from=date_from, date_to=date_to)),
        ),
        KpiCard(
            id="outstanding",
            label="Farmer outstanding",
            value=outstanding,
            unit="INR",
            format="money",
            status="live",
            note="Latest ledger balance_after per farmer.",
            drill=DrillLink(href=drill_query("/payments", date_from=date_from, date_to=date_to)),
        ),
        KpiCard(
            id="pending_farmer_pay",
            label="Pending farmer pay",
            value=pending_amount,
            unit="INR",
            format="money",
            status="live",
            note=f"{pending_count} tickets",
            drill=DrillLink(
                href=drill_query("/procurement", date_from=date_from, date_to=date_to),
            ),
        ),
        KpiCard(
            id="ops_cash_flow_est",
            label="Ops cash-flow estimate",
            value=net_ops,
            unit="INR",
            format="money",
            status="estimate",
            note="Procurement revenue + collections − expenses (not bank cash).",
        ),
        KpiCard(
            id="working_capital",
            label="Working capital / cash book",
            value=None,
            format="text",
            status="unavailable",
            note="Requires cash book — not invented in Phase 1.",
        ),
    ]

    exp_series = [
        SeriesPoint(x=d.isoformat(), y=amt, series="expenses")
        for d, amt in q.expense_series_by_day(db, org_id, date_from, date_to)
    ]
    rev_series = [
        SeriesPoint(x=d.isoformat(), y=amt, series="procurement_revenue")
        for d, amt in q.revenue_series_by_day(db, org_id, date_from, date_to)
    ]

    categories = q.expense_by_category(db, org_id, date_from, date_to, limit=10)
    tables = [
        TablePage(
            id="expense_categories",
            title="Expenses by category",
            columns=[
                TableColumn(key="name", label="Category"),
                TableColumn(key="amount", label="Amount", format="money"),
                TableColumn(key="count", label="Count", format="number"),
            ],
            rows=[
                TableRow(cells={"name": c["name"], "amount": c["amount"], "count": c["count"]})
                for c in categories
            ],
            total=len(categories),
        )
    ]

    return ModuleSummaryResponse(
        module="finance",
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
            preset=filters.preset,
        ),
        kpis=kpis,
        series_preview=exp_series + rev_series,
        tables_preview=tables,
        data_availability=[
            DataAvailabilityItem(source="expenses", status="available"),
            DataAvailabilityItem(source="collections", status="available"),
            DataAvailabilityItem(source="farmer_ledger_entries", status="available"),
            DataAvailabilityItem(source="procurements", status="available"),
            DataAvailabilityItem(
                source="cash_book",
                status="missing",
                notes="Working capital / cash available not live",
            ),
        ],
    )
