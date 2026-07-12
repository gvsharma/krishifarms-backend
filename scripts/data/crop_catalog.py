"""Default crop types for procurement and field-service dropdowns."""

from __future__ import annotations

DEFAULT_CROP_TYPES: list[dict] = [
    {"name": "Paddy", "code": "PADDY", "default_moisture_pct": 17.0},
    {"name": "Corn", "code": "CORN", "default_moisture_pct": 14.0},
    {"name": "Maize", "code": "MAIZE", "default_moisture_pct": 14.0},
    {"name": "Cotton", "code": "COTTON", "default_moisture_pct": 8.0},
    {"name": "Red Gram", "code": "RED_GRAM", "default_moisture_pct": 12.0},
    {"name": "Green Gram", "code": "GREEN_GRAM", "default_moisture_pct": 12.0},
    {"name": "Black Gram", "code": "BLACK_GRAM", "default_moisture_pct": 12.0},
    {"name": "Bengal Gram", "code": "BENGAL_GRAM", "default_moisture_pct": 12.0},
    {"name": "Sunflower", "code": "SUNFLOWER", "default_moisture_pct": 9.0},
    {"name": "Groundnut", "code": "GROUNDNUT", "default_moisture_pct": 8.0},
    {"name": "Vegetables", "code": "VEGETABLES", "default_moisture_pct": None},
    {"name": "Others", "code": "OTHERS", "default_moisture_pct": None},
    # Legacy operational / non-grain entries kept for existing orgs
    {"name": "Pulses", "code": "PULSES", "default_moisture_pct": None},
    {"name": "Concrete Work", "code": "CONCRETEWORK", "default_moisture_pct": None},
]
