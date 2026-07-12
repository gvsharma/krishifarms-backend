"""Thin dashboard summary + report registry."""

from app.modules.dashboard.schemas import DashboardSummaryResponse
from app.modules.dashboard.service import REPORT_CATALOG, get_report_catalog


def test_report_catalog_covers_erp_types():
    catalog = get_report_catalog()
    ids = {item.id for item in catalog.items}
    assert ids == {
        "vehicle_utilization",
        "diesel_expenses",
        "procurement_summary",
        "farmer_ledger",
        "outstanding_payments",
        "crop_village_procurement",
        "vehicle_earnings",
        "supervisor_productivity",
    }
    assert all(item.status in {"available", "partial", "coming_soon"} for item in REPORT_CATALOG)
    assert catalog.summary_endpoint == "/dashboard/summary"


def test_dashboard_summary_schema_includes_ops_counts():
    payload = DashboardSummaryResponse(
        users=1,
        villages=2,
        crop_types=3,
        documents=4,
        farmers=5,
        procurements=6,
        assets=7,
        farmer_payments=8,
        field_services=9,
        vehicle_trips=10,
    )
    assert payload.farmers == 5
    assert payload.vehicle_trips == 10
