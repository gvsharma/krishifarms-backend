"""Parse vehicle work details embedded in field-service comments."""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal

_MARKER_START = "[kf:work]"
_MARKER_END = "[/kf:work]"


@dataclass(frozen=True)
class VehicleWorkDetails:
    profile: str
    crop_code: str | None = None
    crop_name: str | None = None
    area_acres: str | None = None
    cultivation_stage: str | None = None
    trips: str | None = None
    purpose: str | None = None
    material: str | None = None
    locality: str | None = None
    distance_km: str | None = None
    weight_kg: str | None = None
    goods_type: str | None = None
    tonnes: str | None = None
    loading_point: str | None = None
    unloading_point: str | None = None
    litres: str | None = None
    spray_type: str | None = None
    bale_count: str | None = None


def parse_work_details_from_comments(comments: str | None) -> tuple[VehicleWorkDetails | None, str]:
    if not comments:
        return None, ""
    start = comments.find(_MARKER_START)
    end = comments.find(_MARKER_END)
    if start == -1 or end == -1 or end <= start:
        return None, comments
    raw = comments[start + len(_MARKER_START) : end].strip()
    free = f"{comments[:start]}{comments[end + len(_MARKER_END) :]}".strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None, comments
    if not isinstance(data, dict) or not data.get("profile"):
        return None, comments
    return VehicleWorkDetails(**{k: data.get(k) for k in VehicleWorkDetails.__dataclass_fields__}), free


def _to_int(value: str | int | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(Decimal(str(value)))
    except Exception:
        return None


def trips_from_work_details(details: VehicleWorkDetails | None) -> int | None:
    if details is None or not details.trips:
        return None
    return _to_int(details.trips)


def bale_count_from_work_details(details: VehicleWorkDetails | None) -> int | None:
    if details is None:
        return None
    if details.bale_count:
        return _to_int(details.bale_count)
    if details.profile == "baler" and details.trips:
        return _to_int(details.trips)
    return None


def strip_work_details_marker(comments: str | None) -> str | None:
    _, free = parse_work_details_from_comments(comments)
    return free or None
