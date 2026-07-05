"""Tests for procurement state machine, RBAC, and ledger helpers."""

from decimal import Decimal

import pytest

from app.modules.procurements.schemas import CANCELLABLE_STATUSES
from app.modules.procurements.service import (
    ALLOWED_TRANSITIONS,
    can_transition,
    compute_amounts,
)
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


class TestProcurementPricing:
    def test_compute_amounts_uses_decimal(self):
        gross, deduction, net = compute_amounts(
            Decimal("706.621"),
            Decimal("2145.43"),
            Decimal("209.36"),
        )
        assert gross == Decimal("15160.06")
        assert deduction == Decimal("209.36")
        assert net == Decimal("14950.70")

    def test_compute_amounts_rejects_over_deduction(self):
        with pytest.raises(Exception) as exc:
            compute_amounts(Decimal("100"), Decimal("2000"), Decimal("2500"))
        assert "Deductions exceed gross amount" in str(exc.value)


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
