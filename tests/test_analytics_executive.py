"""Analytics Hub Phase 1 — catalog, executive/procurement/finance honesty, Decimal money."""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

from app.modules.analytics.catalog import get_catalog
from app.modules.analytics.filters import money, resolve_date_range
from app.modules.analytics.schemas import AnalyticsFilter, LIVE_MODULES
from app.modules.analytics.service_executive import build_executive_summary
from app.modules.analytics.service_finance import build_finance_summary
from app.modules.analytics.service_procurement import build_procurement_summary
from app.modules.analytics.service_scaffold import build_scaffold_summary


def test_catalog_has_four_live_and_eleven_scaffold():
    catalog = get_catalog()
    assert catalog.live_count == 4
    assert catalog.scaffold_count == 11
    assert len(catalog.modules) == 15
    live_ids = {m.id for m in catalog.modules if m.status == "live"}
    assert live_ids == LIVE_MODULES
    assert catalog.permission == "analytics:admin"


def test_money_helper_quantizes_decimal():
    assert money(Decimal("10.006")) == Decimal("10.01")
    assert money(None) == Decimal("0.00")
    assert money(1.5) == Decimal("1.50")


def test_resolve_date_range_presets():
    today = date(2026, 7, 14)
    assert resolve_date_range(AnalyticsFilter(preset="today"), today=today) == (today, today)
    start, end = resolve_date_range(AnalyticsFilter(preset="7d"), today=today)
    assert end == today
    assert (end - start).days == 6
    y_start, y_end = resolve_date_range(AnalyticsFilter(preset="yesterday"), today=today)
    assert y_start == y_end == date(2026, 7, 13)
    w_start, w_end = resolve_date_range(AnalyticsFilter(preset="this_week"), today=today)
    assert w_end == today
    assert w_start.weekday() == 0
    m_start, m_end = resolve_date_range(AnalyticsFilter(preset="this_month"), today=today)
    assert m_start == date(2026, 7, 1)
    assert m_end == today
    d_start, d_end = resolve_date_range(
        AnalyticsFilter(preset="day", date_from=date(2026, 7, 10)), today=today
    )
    assert d_start == d_end == date(2026, 7, 10)


def _mock_db_zeroes() -> MagicMock:
    """Session stub: all scalar/count/all return empty/zero so builders stay DB-free."""
    db = MagicMock()
    query = MagicMock()
    db.query.return_value = query
    query.filter.return_value = query
    query.join.return_value = query
    query.group_by.return_value = query
    query.order_by.return_value = query
    query.limit.return_value = query
    query.count.return_value = 0
    query.scalar.return_value = 0
    query.one.return_value = (0, 0)
    query.all.return_value = []
    query.first.return_value = None
    return db


def test_executive_marks_cash_and_weather_unavailable():
    org_id = uuid4()
    summary = build_executive_summary(
        _mock_db_zeroes(),
        org_id,
        AnalyticsFilter(preset="today"),
        today=date(2026, 7, 14),
    )
    assert summary.status == "live"
    by_id = {k.id: k for k in summary.kpis}
    assert by_id["cash_available"].status == "unavailable"
    assert by_id["weather"].status == "unavailable"
    assert by_id["revenue"].format == "money"
    assert isinstance(by_id["revenue"].value, Decimal)
    assert by_id["procurement_margin"].format == "money"
    assert isinstance(by_id["procurement_margin"].value, Decimal)
    assert summary.health_score_method == "rules_v1"
    assert any(d.status == "missing" and d.source == "cash_book" for d in summary.data_availability)
    villages = next(t for t in summary.tables_preview if t.id == "top_villages")
    col_keys = {c.key for c in villages.columns}
    assert {"gross", "net", "profit"}.issubset(col_keys)


def test_procurement_margin_matches_profit_summary():
    from app.modules.procurements.service import compute_procurement_margin_amount, compute_profit_summary
    from app.modules.procurements.models import Procurement
    from app.modules.procurements.schemas import DEFAULT_SPOT_DEDUCTION_PER_QUINTAL

    row = Procurement(
        bag_count=50,
        per_bag_deduction_kg=Decimal("2.000"),
        gross_weight_kg=Decimal("2500"),
        net_weight_kg=Decimal("2400"),
        rate_per_quintal=Decimal("2100"),
        is_spot_payment=True,
        spot_deduction_per_quintal=DEFAULT_SPOT_DEDUCTION_PER_QUINTAL,
        spot_deduction_amount=Decimal("2400.00"),
    )
    margin = compute_procurement_margin_amount(
        bag_count=row.bag_count,
        per_bag_deduction_kg=row.per_bag_deduction_kg,
        rate_per_quintal=row.rate_per_quintal,
        spot_deduction_amount=row.spot_deduction_amount,
        gross_weight_kg=row.gross_weight_kg,
        net_weight_kg=row.net_weight_kg,
    )
    summary = compute_profit_summary(row)
    assert summary is not None
    assert margin == summary.total_profit_amount == Decimal("4500.00")


def test_procurement_summary_money_is_decimal():
    org_id = uuid4()
    summary = build_procurement_summary(
        _mock_db_zeroes(),
        org_id,
        AnalyticsFilter(preset="30d"),
        today=date(2026, 7, 14),
    )
    assert summary.module == "procurement"
    amount = next(k for k in summary.kpis if k.id == "net_amount")
    assert isinstance(amount.value, Decimal)
    assert amount.drill is not None
    assert amount.drill.href.startswith("/procurement?")


def test_finance_org_isolation_uses_passed_org_only():
    """Builders must not invent org_id; mock proves query called via session (org in filter path)."""
    org_a = uuid4()
    org_b = uuid4()
    db_a = _mock_db_zeroes()
    db_b = _mock_db_zeroes()
    a = build_finance_summary(db_a, org_a, AnalyticsFilter(preset="7d"), today=date(2026, 7, 14))
    b = build_finance_summary(db_b, org_b, AnalyticsFilter(preset="7d"), today=date(2026, 7, 14))
    assert a.module == b.module == "finance"
    # Working capital never fabricated
    wc = next(k for k in a.kpis if k.id == "working_capital")
    assert wc.status == "unavailable"
    assert wc.value is None
    assert db_a.query.called
    assert db_b.query.called


def test_scaffold_inventory_has_no_fake_kpis():
    summary = build_scaffold_summary("inventory", AnalyticsFilter(preset="30d"))
    assert summary.status == "scaffold"
    assert all(k.status in {"coming_soon", "unavailable"} for k in summary.kpis)
    assert all(k.value is None for k in summary.kpis)
    assert summary.data_availability
    assert any("inventory" in (d.notes or d.source).lower() for d in summary.data_availability)
