"""Tests for vehicle trip cost helpers and farms schema contract."""

from decimal import Decimal

from app.modules.assets.vehicle_trip_service import _total_cost
from app.modules.farms.models import Farm, FarmActivity
from app.shared.permissions import ROLE_PERMISSIONS, SYSTEM_PERMISSIONS


class TestVehicleTripCosts:
    def test_total_cost_sums_charges(self):
        assert _total_cost(
            Decimal("100.10"),
            Decimal("20.20"),
            Decimal("30.30"),
            Decimal("5.05"),
            Decimal("4.40"),
        ) == Decimal("160.05")


class TestFarmsSchemaContract:
    def test_farm_soft_delete_column(self):
        assert "deleted_at" in {c.name for c in Farm.__table__.columns}
        assert "farm_code" in {c.name for c in Farm.__table__.columns}

    def test_farm_activity_soft_delete_column(self):
        assert "deleted_at" in {c.name for c in FarmActivity.__table__.columns}
        assert "farm_id" in {c.name for c in FarmActivity.__table__.columns}


class TestFarmsAndTransportRBAC:
    def test_transport_permissions_registered(self):
        codes = {code for code, _ in SYSTEM_PERMISSIONS}
        assert "transport:read" in codes
        assert "transport:create" in codes
        assert "transport:update" in codes

    def test_farming_permissions_registered(self):
        codes = {code for code, _ in SYSTEM_PERMISSIONS}
        assert "farming:read" in codes
        assert "farming:create" in codes
        assert "farming:update" in codes

    def test_driver_can_manage_trips(self):
        perms = set(ROLE_PERMISSIONS["DRIVER"])
        assert "transport:read" in perms
        assert "transport:create" in perms
        assert "transport:update" in perms

    def test_supervisor_can_manage_farms(self):
        perms = set(ROLE_PERMISSIONS["SUPERVISOR"])
        assert "farming:read" in perms
        assert "farming:create" in perms
        assert "farming:update" in perms
