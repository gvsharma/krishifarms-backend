"""Tests for vehicle work-details parsing and pricing."""

from decimal import Decimal

from app.modules.field_services.pricing import compute_vehicle_charge
from app.modules.platform.models import VehicleType
from app.shared.work_details import (
    bale_count_from_work_details,
    parse_work_details_from_comments,
    trips_from_work_details,
    VehicleWorkDetails,
)


class TestWorkDetailsParser:
    def test_parse_embedded_json(self):
        comments = '[kf:work]{"profile":"trolley","trips":"3"}[/kf:work]\nFarmer field'
        details, free = parse_work_details_from_comments(comments)
        assert details is not None
        assert details.profile == "trolley"
        assert details.trips == "3"
        assert free == "Farmer field"
        assert trips_from_work_details(details) == 3

    def test_bale_count(self):
        details = VehicleWorkDetails(profile="baler", bale_count="12")
        assert bale_count_from_work_details(details) == 12


class TestVehiclePricing:
    def test_hourly_rate(self):
        vehicle = VehicleType(
            org_id=None,  # type: ignore[arg-type]
            name="Cultivator",
            code="CULTIVATOR",
            default_rate=Decimal("1200"),
            default_rate_unit="hour",
        )
        rate, total = compute_vehicle_charge(vehicle, hours=Decimal("2.5"))
        assert rate == Decimal("1200.00")
        assert total == Decimal("3000.00")

    def test_trip_rate(self):
        vehicle = VehicleType(
            org_id=None,  # type: ignore[arg-type]
            name="Trolley",
            code="TROLLEY",
            default_rate=Decimal("250"),
            default_rate_unit="trip",
        )
        details = VehicleWorkDetails(profile="trolley", trips="4")
        rate, total = compute_vehicle_charge(vehicle, hours=None, work_details=details)
        assert rate == Decimal("250.00")
        assert total == Decimal("1000.00")

    def test_bale_rate(self):
        vehicle = VehicleType(
            org_id=None,  # type: ignore[arg-type]
            name="Baler",
            code="BALER",
            default_rate=Decimal("40"),
            default_rate_unit="bale",
        )
        details = VehicleWorkDetails(profile="baler", bale_count="25")
        rate, total = compute_vehicle_charge(vehicle, hours=None, work_details=details)
        assert rate == Decimal("40.00")
        assert total == Decimal("1000.00")
