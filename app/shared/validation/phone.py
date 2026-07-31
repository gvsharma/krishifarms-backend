"""Indian mobile number validation — exactly 10 digits, digits only."""

from __future__ import annotations


def digits_only(phone: str) -> str:
    return "".join(ch for ch in phone if ch.isdigit())


def normalize_indian_mobile(phone: str) -> str:
    """Return exactly 10 digits; accept optional +91 / 91 prefix."""
    digits = digits_only(phone)
    if len(digits) > 10 and digits.startswith("91"):
        digits = digits[-10:]
    if len(digits) != 10:
        raise ValueError("Phone must be exactly 10 digits (numbers only)")
    return digits


def normalize_indian_mobile_optional(phone: str | None) -> str | None:
    if phone is None or not str(phone).strip():
        return None
    return normalize_indian_mobile(str(phone))
