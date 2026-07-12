"""Tests for farmer payment settlement helpers and RBAC."""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import uuid4

from app.modules.farmer_payments.models import FarmerPayment
from app.modules.farmer_payments.schemas import PAYMENT_STATUSES, PAYMENT_TYPES
from app.modules.farmer_payments.service import _money, _sync_procurement_payment_status
from app.modules.procurements.schemas import PAYMENT_TERMS
from app.modules.procurements.service import resolve_expected_payment_date
from app.shared.permissions import ROLE_PERMISSIONS, SYSTEM_PERMISSIONS


class TestFarmerPaymentMoney:
    def test_money_quantizes_to_two_places(self):
        assert _money(Decimal("100.456")) == Decimal("100.46")
        assert _money(Decimal("100.454")) == Decimal("100.45")


class TestProcurementPaymentStatusSync:
    def _procurement(self, *, status: str = "confirmed", net: str = "100.00"):
        row = MagicMock()
        row.status = status
        row.net_amount = Decimal(net)
        row.actual_payment_date = None
        row.id = uuid4()
        row.procurement_date = date(2026, 7, 1)
        return row

    def test_partial_allocation_sets_paid_partial(self):
        procurement = self._procurement()
        with patch(
            "app.modules.farmer_payments.service._procurement_allocated_total",
            return_value=Decimal("40.00"),
        ):
            _sync_procurement_payment_status(
                MagicMock(),
                uuid4(),
                procurement,
                payment_date=date(2026, 7, 12),
            )
        assert procurement.status == "paid_partial"
        assert procurement.actual_payment_date == date(2026, 7, 12)

    def test_full_allocation_sets_paid_full(self):
        procurement = self._procurement()
        with patch(
            "app.modules.farmer_payments.service._procurement_allocated_total",
            return_value=Decimal("100.00"),
        ):
            _sync_procurement_payment_status(
                MagicMock(),
                uuid4(),
                procurement,
                payment_date=date(2026, 7, 12),
            )
        assert procurement.status == "paid_full"
        assert procurement.actual_payment_date == date(2026, 7, 12)

    def test_zero_allocation_reverts_to_confirmed(self):
        procurement = self._procurement(status="paid_partial")
        procurement.actual_payment_date = date(2026, 7, 12)
        with patch(
            "app.modules.farmer_payments.service._procurement_allocated_total",
            return_value=Decimal("0.00"),
        ):
            _sync_procurement_payment_status(MagicMock(), uuid4(), procurement)
        assert procurement.status == "confirmed"
        assert procurement.actual_payment_date is None

    def test_ignores_non_payable_statuses(self):
        procurement = self._procurement(status="draft")
        with patch(
            "app.modules.farmer_payments.service._procurement_allocated_total",
            return_value=Decimal("50.00"),
        ) as allocated:
            _sync_procurement_payment_status(MagicMock(), uuid4(), procurement)
        allocated.assert_not_called()
        assert procurement.status == "draft"


class TestFarmerPaymentSchemaContract:
    def test_payment_types_match_db_check(self):
        assert set(PAYMENT_TYPES) == {"advance", "final", "adjustment"}

    def test_payment_statuses_match_db_check(self):
        assert set(PAYMENT_STATUSES) == {"pending", "completed", "failed", "reversed"}

    def test_model_has_no_soft_delete(self):
        column_names = {c.name for c in FarmerPayment.__table__.columns}
        assert "deleted_at" not in column_names
        assert "amount" in column_names
        assert "payment_date" in column_names
        assert "reversal_of_id" in column_names


class TestProcurementPaymentTerms:
    def test_known_terms(self):
        assert set(PAYMENT_TERMS) == {"one_week", "10_days", "2_weeks", "20_days", "custom"}

    def test_resolve_expected_payment_date(self):
        base = date(2026, 7, 1)
        assert resolve_expected_payment_date(base, "one_week") == date(2026, 7, 8)
        assert resolve_expected_payment_date(base, "10_days") == date(2026, 7, 11)
        assert resolve_expected_payment_date(base, "2_weeks") == date(2026, 7, 15)
        assert resolve_expected_payment_date(base, "20_days") == date(2026, 7, 21)
        assert resolve_expected_payment_date(base, "custom") is None
        assert resolve_expected_payment_date(base, "one_week", date(2026, 8, 1)) == date(2026, 8, 1)


class TestFarmerPaymentRBAC:
    def test_permissions_registered(self):
        codes = {code for code, _ in SYSTEM_PERMISSIONS}
        for code in (
            "farmer_payments:read",
            "farmer_payments:create",
            "farmer_payments:reverse",
        ):
            assert code in codes

    def test_owner_has_payment_permissions(self):
        perms = set(ROLE_PERMISSIONS["OWNER"])
        assert "farmer_payments:read" in perms
        assert "farmer_payments:create" in perms
        assert "farmer_payments:reverse" in perms

    def test_manager_can_create_not_reverse(self):
        perms = set(ROLE_PERMISSIONS["MANAGER"])
        assert "farmer_payments:read" in perms
        assert "farmer_payments:create" in perms
        assert "farmer_payments:reverse" not in perms

    def test_supervisor_has_no_payment_permissions(self):
        perms = set(ROLE_PERMISSIONS["SUPERVISOR"])
        assert "farmer_payments:read" not in perms
        assert "farmer_payments:create" not in perms
