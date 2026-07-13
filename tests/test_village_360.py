"""Unit tests for Village 360° helpers and search scaffolding."""

from decimal import Decimal
from uuid import uuid4

from app.modules.villages.profile_360_service import _crop_bucket, _money, _vehicle_kind


class TestVillage360Helpers:
    def test_crop_bucket(self):
        assert _crop_bucket("Paddy") == "paddy"
        assert _crop_bucket("Rice") == "paddy"
        assert _crop_bucket("Corn") == "corn"
        assert _crop_bucket("Maize Hybrid") == "corn"
        assert _crop_bucket("Cotton") == "other"
        assert _crop_bucket(None) == "other"

    def test_vehicle_kind(self):
        assert _vehicle_kind("John Deere Tractor") == "tractor"
        assert _vehicle_kind("rotavator-4ft") == "rotavator"
        assert _vehicle_kind("BOLERO") == "bolero"
        assert _vehicle_kind("Eicher DCM") == "dcm"
        assert _vehicle_kind("baler") == "baler"
        assert _vehicle_kind(None) == "other"

    def test_money_quantize(self):
        assert _money(None) == Decimal("0")
        assert _money("12.344") == Decimal("12.34")
        assert _money(10) == Decimal("10.00")


class TestVillageCodePattern:
    def test_next_code_increments(self):
        from app.modules.master_data.service import _next_village_code

        class FakeQuery:
            def filter(self, *a, **k):
                return self

            def all(self):
                return [("VIL-0001",), ("VIL-0007",), ("OTHER",)]

        class FakeSession:
            def query(self, *a):
                return FakeQuery()

        assert _next_village_code(FakeSession(), uuid4()) == "VIL-0008"
