"""Tests for farmer sub-resources and outstanding balance."""

from decimal import Decimal

from app.shared.crypto import decrypt_value, encrypt_value, mask_account_number


class TestFarmerCrypto:
    def test_encrypt_decrypt_roundtrip(self):
        ciphertext = encrypt_value("1234567890")
        assert decrypt_value(ciphertext) == "1234567890"

    def test_mask_account_number(self):
        assert mask_account_number("1234567890") == "XXXXXX7890"
        assert mask_account_number("1234") == "XXXX"


class TestFarmerOutstanding:
    def test_outstanding_defaults_to_zero_without_ledger(self):
        from app.modules.farmers.service import farmer_outstanding

        class FakeQuery:
            def filter(self, *args, **kwargs):
                return self

            def order_by(self, *args, **kwargs):
                return self

            def first(self):
                return None

        class FakeSession:
            def query(self, *args):
                return FakeQuery()

        assert farmer_outstanding(FakeSession(), "org", "farmer") == Decimal("0")

    def test_outstanding_reads_latest_balance(self):
        from app.modules.farmers.service import farmer_outstanding

        class FakeQuery:
            def filter(self, *args, **kwargs):
                return self

            def order_by(self, *args, **kwargs):
                return self

            def first(self):
                return (Decimal("1500.50"),)

        class FakeSession:
            def query(self, *args):
                return FakeQuery()

        assert farmer_outstanding(FakeSession(), "org", "farmer") == Decimal("1500.50")
