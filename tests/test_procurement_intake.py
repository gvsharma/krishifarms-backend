"""Tests for procurement intake weighment and per-bag entries."""

from decimal import Decimal

import pytest

from app.modules.procurements.schemas import ProcurementCalculateRequest, WeighmentRequest
from app.modules.procurements.service import compute_net_weight
from app.shared.procurement_notes import rate_per_quintal_from_notes


class TestWeighmentRequest:
    def test_resolved_gross_from_bag_list(self):
        payload = WeighmentRequest(
            bag_weights_kg=[Decimal("50.5"), Decimal("49.5"), Decimal("51")],
        )
        assert payload.resolved_gross_weight_kg() == Decimal("151.0")

    def test_requires_gross_or_bags(self):
        with pytest.raises(ValueError):
            WeighmentRequest()


class TestProcurementCalculateRequest:
    def test_resolved_gross_from_variable_bags(self):
        payload = ProcurementCalculateRequest(
            bag_count=3,
            bag_weights_kg=[Decimal("48"), Decimal("52"), Decimal("50")],
            per_bag_deduction_kg=Decimal("2"),
            rate_per_quintal=Decimal("2100"),
        )
        assert payload.resolved_gross_weight_kg() == Decimal("150")

    def test_bag_count_must_match_list(self):
        with pytest.raises(ValueError):
            ProcurementCalculateRequest(
                bag_count=2,
                bag_weights_kg=[Decimal("50")],
                rate_per_quintal=Decimal("2100"),
            )


class TestProcurementNotesParser:
    def test_rate_from_proc_marker(self):
        notes = '[kf:proc]{"rate_per_quintal":"2150","moisture_pct":"14"}[/kf:proc]'
        assert rate_per_quintal_from_notes(notes) == Decimal("2150")


class TestBagWeightNetFormula:
    def test_variable_bag_sum_with_kata(self):
        bag_weights = [Decimal("48"), Decimal("52"), Decimal("50")]
        gross = sum(bag_weights)
        bag_deduction, net = compute_net_weight(gross, Decimal("0"), len(bag_weights), Decimal("2"))
        assert gross == Decimal("150")
        assert bag_deduction == Decimal("6.000")
        assert net == Decimal("144.000")
