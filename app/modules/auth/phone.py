"""Phone normalization for login lookup (Firebase E.164 ↔ stored user.phone)."""


def normalize_phone_for_lookup(phone: str) -> str:
    """Normalize to digits; Indian numbers use last 10 digits for lookup."""
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) > 10 and digits.startswith("91"):
        return digits[-10:]
    return digits
