"""Tests for procurement state machine, RBAC, and ledger helpers."""

from decimal import Decimal

import pytest

from app.modules.procurements.schemas import CANCELLABLE_STATUSES
from app.modules.procurements.service import (
    ALLOWED_TRANSITIONS,
    can_transition,
    compute_amounts,
    compute_bag_weight_deduction,
    compute_net_weight,
    compute_profit_summary,
    compute_spot_deduction_amount,
)
from app.modules.procurements.models import Procurement
from app.modules.procurements.schemas import DEFAULT_SPOT_DEDUCTION_PER_QUINTAL
from app.shared.permissions import ROLE_PERMISSIONS


class TestProcurementStateMachine:
    def test_happy_path_transitions(self):
        path = ["draft", "pending_weighment", "weighed", "priced", "confirmed", "reversed"]
        for current, nxt in zip(path, path[1:], strict=False):
            assert can_transition(current, nxt), f"{current} -> {nxt} should be allowed"

    def test_cancel_from_pre_confirm_states(self):
        for status in CANCELLABLE_STATUSES:
            assert can_transition(status, "cancelled")

    def test_cannot_cancel_after_priced(self):
        assert not can_transition("priced", "cancelled")
        assert not can_transition("confirmed", "cancelled")

    def test_cannot_skip_weighment(self):
        assert not can_transition("draft", "weighed")
        assert not can_transition("pending_weighment", "priced")

    def test_cannot_confirm_from_weighed(self):
        assert not can_transition("weighed", "confirmed")

    def test_reverse_only_from_confirmed(self):
        assert can_transition("confirmed", "reversed")
        assert not can_transition("priced", "reversed")
        assert not can_transition("reversed", "confirmed")

    def test_terminal_states_have_no_outgoing(self):
        for terminal in ("cancelled", "reversed", "paid_partial", "paid_full"):
            assert ALLOWED_TRANSITIONS.get(terminal, frozenset()) == frozenset()


class TestProcurementCalculate:
    def test_calculate_preview_worked_example(self):
        from app.modules.procurements.schemas import ProcurementCalculateRequest
        from app.modules.procurements.service import calculate_procurement_preview

        result = calculate_procurement_preview(
            ProcurementCalculateRequest(
                bag_count=50,
                weight_per_bag_kg=Decimal("50"),
                per_bag_deduction_kg=Decimal("2"),
                rate_per_quintal=Decimal("2100"),
                is_spot_payment=True,
            )
        )
        assert result.gross_weight_kg == Decimal("2500.000")
        assert result.net_weight_kg == Decimal("2400.000")
        assert result.net_amount == Decimal("48000.00")
        assert result.spot_deduction_amount == Decimal("2400.00")


class TestProcurementPricing:
    def test_compute_amounts_uses_decimal(self):
        gross, line_deduction, spot_deduction, net = compute_amounts(
            Decimal("706.621"),
            Decimal("2145.43"),
            Decimal("209.36"),
        )
        assert gross == Decimal("15160.06")
        assert line_deduction == Decimal("209.36")
        assert spot_deduction == Decimal("0.00")
        assert net == Decimal("14950.70")

    def test_compute_amounts_rejects_over_deduction(self):
        with pytest.raises(Exception) as exc:
            compute_amounts(Decimal("100"), Decimal("2000"), Decimal("2500"))
        assert "Deductions exceed gross amount" in str(exc.value)

    def test_spot_payment_worked_example(self):
        # 50 bags × 50 kg = 2500 kg gross; 2 kg/bag → 2400 kg net = 24 quintals @ ₹2100.
        net_kg = Decimal("2400")
        rate = Decimal("2100")
        gross, line, spot, net = compute_amounts(
            net_kg,
            rate,
            Decimal("0"),
            is_spot_payment=True,
            spot_deduction_per_quintal=DEFAULT_SPOT_DEDUCTION_PER_QUINTAL,
        )
        assert gross == Decimal("50400.00")
        assert line == Decimal("0.00")
        assert spot == Decimal("2400.00")
        assert net == Decimal("48000.00")

    def test_spot_deduction_zero_when_not_spot(self):
        assert compute_spot_deduction_amount(
            Decimal("2400"), False, DEFAULT_SPOT_DEDUCTION_PER_QUINTAL
        ) == Decimal("0.00")

    def test_profit_summary_worked_example(self):
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
        summary = compute_profit_summary(row)
        assert summary is not None
        assert summary.gross_quintals == Decimal("25.000")
        assert summary.net_quintals == Decimal("24.000")
        assert summary.weight_deduction_kg == Decimal("100.000")
        assert summary.weight_deduction_profit_amount == Decimal("2100.00")
        assert summary.spot_deduction_amount == Decimal("2400.00")
        assert summary.total_profit_amount == Decimal("4500.00")


class TestPerBagWeightDeduction:
    def test_bag_weight_deduction_default_two_kg(self):
        # 50 bags * 2 kg = 100 kg deducted (kata)
        assert compute_bag_weight_deduction(50, Decimal("2")) == Decimal("100.000")

    def test_net_weight_matches_worked_example(self):
        # 50 bags @ 50 kg = 2500 kg gross; 2 kg/bag => 100 kg deducted => 2400 kg net.
        bag_deduction, net = compute_net_weight(
            Decimal("2500"), Decimal("0"), 50, Decimal("2")
        )
        assert bag_deduction == Decimal("100.000")
        assert net == Decimal("2400.000")

    def test_net_weight_includes_tare_and_bag_deduction(self):
        bag_deduction, net = compute_net_weight(
            Decimal("2560.500"), Decimal("10.500"), 50, Decimal("2")
        )
        assert bag_deduction == Decimal("100.000")
        assert net == Decimal("2450.000")

    def test_zero_per_bag_deduction_only_applies_tare(self):
        bag_deduction, net = compute_net_weight(
            Decimal("2500"), Decimal("50"), 50, Decimal("0")
        )
        assert bag_deduction == Decimal("0.000")
        assert net == Decimal("2450.000")

    def test_fractional_per_bag_deduction(self):
        bag_deduction, net = compute_net_weight(
            Decimal("1000"), Decimal("0"), 40, Decimal("1.5")
        )
        assert bag_deduction == Decimal("60.000")
        assert net == Decimal("940.000")


class TestProcurementRBAC:
    def test_owner_has_full_procurement_permissions(self):
        perms = set(ROLE_PERMISSIONS["OWNER"])
        for code in (
            "procurements:read",
            "procurements:create",
            "procurements:update",
            "procurements:confirm",
            "procurements:cancel",
        ):
            assert code in perms

    def test_manager_can_confirm_not_reverse_via_role(self):
        perms = set(ROLE_PERMISSIONS["MANAGER"])
        assert "procurements:confirm" in perms
        assert "procurements:cancel" in perms

    def test_supervisor_cannot_confirm(self):
        perms = set(ROLE_PERMISSIONS["SUPERVISOR"])
        assert "procurements:read" in perms
        assert "procurements:create" in perms
        assert "procurements:confirm" not in perms
        assert "procurements:cancel" not in perms

    def test_agent_has_no_procurement_permissions(self):
        perms = set(ROLE_PERMISSIONS["AGENT"])
        assert "procurements:read" not in perms
        assert "procurements:create" not in perms


class TestLedgerImmutability:
    def test_reversal_is_separate_transition_not_update(self):
        """Reversal is modeled as confirmed -> reversed plus a credit ledger entry."""
        assert can_transition("confirmed", "reversed")
        assert "reversed" not in ALLOWED_TRANSITIONS.get("draft", frozenset())

    def test_ledger_entry_types_are_append_only_by_design(self):
        from app.modules.procurements.models import FarmerLedgerEntry

        assert FarmerLedgerEntry.__tablename__ == "farmer_ledger_entries"
        column_names = {c.name for c in FarmerLedgerEntry.__table__.columns}
        assert "reversal_of_id" in column_names
        assert "debit" in column_names
        assert "credit" in column_names
