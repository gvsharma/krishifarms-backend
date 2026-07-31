"""Phone normalization for login lookup (Firebase E.164 ↔ stored user.phone)."""

from app.shared.validation.phone import digits_only, normalize_indian_mobile


def normalize_phone_for_lookup(phone: str) -> str:
    """Normalize to digits; Indian numbers use last 10 digits for lookup."""
    digits = digits_only(phone)
    if len(digits) > 10 and digits.startswith("91"):
        return digits[-10:]
    return digits


def validate_login_mobile(phone: str) -> str:
    """Login identifier: exactly 10 digits after normalization."""
    return normalize_indian_mobile(phone)
