"""Phone validation helpers."""

from app.shared.validation.phone import normalize_indian_mobile, normalize_indian_mobile_optional


def test_normalize_indian_mobile_exact_ten():
    assert normalize_indian_mobile("9876543210") == "9876543210"


def test_normalize_indian_mobile_strips_prefix():
    assert normalize_indian_mobile("+919876543210") == "9876543210"


def test_normalize_indian_mobile_rejects_short():
    try:
        normalize_indian_mobile("12345")
        assert False, "expected ValueError"
    except ValueError as exc:
        assert "10 digits" in str(exc)


def test_normalize_indian_mobile_optional_empty():
    assert normalize_indian_mobile_optional(None) is None
    assert normalize_indian_mobile_optional("  ") is None
