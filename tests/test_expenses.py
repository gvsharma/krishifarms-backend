"""Tests for expenses/collections helpers and diesel expense sync."""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.modules.financial.expense_service import _money, sync_vehicle_trip_diesel_expense
from app.modules.financial.models import Collection, Expense
from app.modules.financial.schemas import EXPENSE_STATUSES, VEHICLE_TRIP_SOURCE
from app.shared.permissions import ROLE_PERMISSIONS, SYSTEM_PERMISSIONS


class TestExpenseMoney:
    def test_money_quantizes_to_two_places(self):
        assert _money(Decimal("100.456")) == Decimal("100.46")
        assert _money(Decimal("100.454")) == Decimal("100.45")


class TestExpenseSchemaContract:
    def test_statuses(self):
        assert set(EXPENSE_STATUSES) == {"draft", "posted", "reversed"}

    def test_expense_has_soft_delete_and_source(self):
        cols = {c.name for c in Expense.__table__.columns}
        assert "deleted_at" in cols
        assert "source_type" in cols
        assert "source_id" in cols
        assert "amount" in cols

    def test_collection_has_no_soft_delete(self):
        cols = {c.name for c in Collection.__table__.columns}
        assert "deleted_at" not in cols
        assert "source_type" in cols
        assert "collection_number" in cols


class TestFinanceRBAC:
    def test_permissions_registered(self):
        codes = {code for code, _ in SYSTEM_PERMISSIONS}
        for code in (
            "expenses:read",
            "expenses:create",
            "expenses:update",
            "expenses:delete",
            "collections:read",
            "collections:create",
        ):
            assert code in codes

    def test_manager_can_manage_expenses_not_delete(self):
        manager = set(ROLE_PERMISSIONS["MANAGER"])
        assert "expenses:read" in manager
        assert "expenses:create" in manager
        assert "expenses:update" in manager
        assert "expenses:delete" not in manager
        assert "collections:create" in manager

    def test_owner_has_expense_delete(self):
        assert "expenses:delete" in ROLE_PERMISSIONS["OWNER"]


class TestDieselExpenseSync:
    def test_zero_fuel_skips_create(self):
        db = MagicMock()
        with patch(
            "app.modules.financial.expense_service.find_expense_by_source",
            return_value=None,
        ) as find:
            result = sync_vehicle_trip_diesel_expense(
                db,
                uuid4(),
                trip_id=uuid4(),
                trip_number="VT-0001",
                trip_date=date(2026, 7, 12),
                asset_id=uuid4(),
                fuel_cost=Decimal("0"),
                fuel_liters=None,
                trip_status="completed",
                actor_user_id=uuid4(),
            )
        assert result is None
        find.assert_called_once()

    def test_cancel_soft_deletes_existing(self):
        existing = MagicMock()
        existing.deleted_at = None
        existing.status = "posted"
        db = MagicMock()
        with patch(
            "app.modules.financial.expense_service.find_expense_by_source",
            return_value=existing,
        ):
            result = sync_vehicle_trip_diesel_expense(
                db,
                uuid4(),
                trip_id=uuid4(),
                trip_number="VT-0002",
                trip_date=date(2026, 7, 12),
                asset_id=uuid4(),
                fuel_cost=Decimal("500.00"),
                fuel_liters=Decimal("20"),
                trip_status="cancelled",
                actor_user_id=uuid4(),
            )
        assert result is None
        assert existing.status == "reversed"
        assert existing.deleted_at is not None

    def test_positive_fuel_updates_existing(self):
        existing = MagicMock()
        existing.deleted_at = None
        db = MagicMock()
        trip_id = uuid4()
        with patch(
            "app.modules.financial.expense_service.find_expense_by_source",
            return_value=existing,
        ) as find:
            result = sync_vehicle_trip_diesel_expense(
                db,
                uuid4(),
                trip_id=trip_id,
                trip_number="VT-0003",
                trip_date=date(2026, 7, 12),
                asset_id=uuid4(),
                fuel_cost=Decimal("250.50"),
                fuel_liters=Decimal("10.5"),
                trip_status="completed",
                actor_user_id=uuid4(),
            )
        assert result is existing
        assert existing.amount == Decimal("250.50")
        assert existing.status == "posted"
        assert "VT-0003" in existing.description
        find.assert_called_once()
        assert find.call_args.args[2] == VEHICLE_TRIP_SOURCE
        assert find.call_args.args[3] == trip_id
