"""Parse procurement draft extras embedded in notes ([kf:proc])."""

from __future__ import annotations

import json
from decimal import Decimal

_MARKER_START = "[kf:proc]"
_MARKER_END = "[/kf:proc]"


def parse_procurement_extras_from_notes(notes: str | None) -> dict:
    if not notes:
        return {}
    start = notes.find(_MARKER_START)
    end = notes.find(_MARKER_END)
    if start == -1 or end == -1 or end <= start:
        return {}
    raw = notes[start + len(_MARKER_START) : end].strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def rate_per_quintal_from_notes(notes: str | None) -> Decimal | None:
    extras = parse_procurement_extras_from_notes(notes)
    raw = extras.get("rate_per_quintal")
    if raw is None or raw == "":
        return None
    try:
        value = Decimal(str(raw))
    except Exception:
        return None
    return value if value > 0 else None


def moisture_pct_from_notes(notes: str | None) -> Decimal | None:
    extras = parse_procurement_extras_from_notes(notes)
    raw = extras.get("moisture_pct")
    if raw is None or raw == "":
        return None
    try:
        return Decimal(str(raw))
    except Exception:
        return None
