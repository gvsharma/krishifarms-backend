"""Tests for hamali labor charge calculations."""

from datetime import date
from decimal import Decimal

from app.modules.hamali.service import compute_entry_amounts, week_bounds


class TestHamaliCalculations:
    def test_labor_per_bag_default_twenty(self):
        labor, maint, tip, total = compute_entry_amounts(
            50, Decimal("20.00"), Decimal("0"), Decimal("0")
        )
        assert labor == Decimal("1000.00")
        assert total == Decimal("1000.00")
        assert maint == Decimal("0.00")
        assert tip == Decimal("0.00")

    def test_includes_maintenance_and_tip(self):
        labor, maint, tip, total = compute_entry_amounts(
            10, Decimal("20.00"), Decimal("150.00"), Decimal("50.00")
        )
        assert labor == Decimal("200.00")
        assert maint == Decimal("150.00")
        assert tip == Decimal("50.00")
        assert total == Decimal("400.00")

    def test_week_bounds_monday_to_sunday(self):
        start, end = week_bounds(date(2026, 7, 27))
        assert start == date(2026, 7, 27)
        assert end == date(2026, 8, 2)
