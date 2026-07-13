"""Unit tests for Farmer 360° aggregation helpers."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

from app.modules.farmers.profile_360_schemas import (
    FarmingHistoryItem,
    ProcurementHistoryItem,
    ServiceHistoryItem,
)
from app.modules.farmers.profile_360_service import (
    _crop_intelligence,
    _recommendations,
    _season_key,
    _statistics,
    _status_label,
)


class TestFarmer360Helpers:
    def test_status_label_vip_and_blacklisted(self):
        assert _status_label("blocked", False) == "Blacklisted"
        assert _status_label("active", True) == "VIP Farmer"
        assert _status_label("active", False) == "Active"
        assert _status_label("inactive", False) == "Inactive"

    def test_season_key_kharif_rabi(self):
        assert _season_key(date(2026, 7, 15)).startswith("Kharif")
        assert _season_key(date(2026, 12, 1)).startswith("Rabi")
        assert _season_key(date(2026, 2, 1)).startswith("Rabi")
        assert _season_key(date(2026, 4, 10)).startswith("Summer")

    def test_crop_intelligence_from_history(self):
        crop_id = uuid4()
        farming = [
            FarmingHistoryItem(
                id=uuid4(),
                crop_type_id=crop_id,
                crop_type_name="Paddy",
                season="Kharif",
                year=2025,
                acres=Decimal("2.5"),
                actual_yield=Decimal("40"),
            ),
            FarmingHistoryItem(
                id=uuid4(),
                crop_type_id=crop_id,
                crop_type_name="Paddy",
                season="Kharif",
                year=2026,
                acres=Decimal("3"),
                actual_yield=Decimal("50"),
            ),
            FarmingHistoryItem(
                id=uuid4(),
                crop_type_id=uuid4(),
                crop_type_name="Corn",
                season="Rabi",
                year=2026,
                acres=Decimal("1"),
                actual_yield=Decimal("20"),
            ),
        ]
        procurements = [
            ProcurementHistoryItem(
                id=uuid4(),
                procurement_number="PR-1",
                procurement_date=date(2026, 7, 1),
                crop_name="Paddy",
                quantity_kg=Decimal("1000"),
                rate_per_quintal=Decimal("2200"),
                net_amount=Decimal("22000"),
                buyer_name="Miller A",
                status="confirmed",
            ),
            ProcurementHistoryItem(
                id=uuid4(),
                procurement_number="PR-2",
                procurement_date=date(2026, 8, 1),
                crop_name="Paddy",
                quantity_kg=Decimal("500"),
                rate_per_quintal=Decimal("2100"),
                net_amount=Decimal("10500"),
                buyer_name="Miller A",
                status="paid_full",
            ),
        ]
        intel = _crop_intelligence(farming, procurements)
        assert intel.most_cultivated_crop == "Paddy"
        assert intel.preferred_buyer == "Miller A"
        assert intel.most_profitable_crop == "Paddy"
        assert intel.procurement_frequency == 2
        assert intel.average_yield == Decimal("36.667")  # (40+50+20)/3

    def test_statistics_and_recommendations(self):
        class FakeFarmer:
            id = uuid4()
            preferred_payment_method = "UPI"
            trust_rating = 4
            is_vip = True

        farmer = FakeFarmer()
        services = [
            ServiceHistoryItem(
                id=uuid4(),
                record_number="FS-1",
                service_date=date(2025, 1, 1),
                service_category="tractor_work",
                vehicle_type="Tractor",
                diesel_amount=Decimal("500"),
                amount_charged=Decimal("2000"),
                pending_amount=Decimal("0"),
                payment_status="paid",
                status="closed",
            )
        ]
        farming = [
            FarmingHistoryItem(
                id=uuid4(),
                crop_type_id=uuid4(),
                crop_type_name="Paddy",
                season="Kharif",
                year=2026,
                acres=Decimal("4"),
                cultivation_stage="flowering",
            )
        ]
        procurements = [
            ProcurementHistoryItem(
                id=uuid4(),
                procurement_number="PR-9",
                procurement_date=date(2026, 7, 10),
                crop_name="Paddy",
                quantity_kg=Decimal("800"),
                net_amount=Decimal("16000"),
                status="confirmed",
            )
        ]
        stats = _statistics(
            farmer,
            services,
            farming,
            procurements,
            outstanding=Decimal("5000"),
            amount_paid=Decimal("10000"),
        )
        assert stats.total_services_availed == 1
        assert stats.total_farming_area == Decimal("4")
        assert stats.lifetime_business_value == Decimal("16000.00")
        assert stats.preferred_vehicle == "Tractor"
        assert stats.current_crop == "Paddy"
        assert stats.outstanding_amount == Decimal("5000.00")

        from app.modules.farmers.profile_360_schemas import Farmer360Analytics

        analytics = Farmer360Analytics(current_outstanding=Decimal("5000"))
        intel = _crop_intelligence(farming, procurements)
        recs = _recommendations(farmer, stats, analytics, farming, intel)
        codes = {r.code for r in recs}
        assert "pending_collection" in codes
        assert "farm_visit" in codes  # last service > 45 days ago
        assert "retention_score" in codes
        assert "likely_crop" in codes
