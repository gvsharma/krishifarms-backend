"""Default crop types for procurement and field-service dropdowns."""

from __future__ import annotations

DEFAULT_CROP_TYPES: list[dict] = [
    {"name": "Paddy", "name_te": "వరి", "code": "PADDY", "default_moisture_pct": 17.0},
    {"name": "Corn", "name_te": "మొక్కజొన్న", "code": "CORN", "default_moisture_pct": 14.0},
    {"name": "Maize", "name_te": "మొక్కజొన్న", "code": "MAIZE", "default_moisture_pct": 14.0},
    {"name": "Cotton", "name_te": "పత్తి", "code": "COTTON", "default_moisture_pct": 8.0},
    {"name": "Red Gram", "name_te": "కంది", "code": "RED_GRAM", "default_moisture_pct": 12.0},
    {"name": "Green Gram", "name_te": "పెసర", "code": "GREEN_GRAM", "default_moisture_pct": 12.0},
    {"name": "Black Gram", "name_te": "మినుములు", "code": "BLACK_GRAM", "default_moisture_pct": 12.0},
    {"name": "Bengal Gram", "name_te": "శనగ", "code": "BENGAL_GRAM", "default_moisture_pct": 12.0},
    {"name": "Sunflower", "name_te": "సూర్యకాంతం", "code": "SUNFLOWER", "default_moisture_pct": 9.0},
    {"name": "Groundnut", "name_te": "వేరుశనగ", "code": "GROUNDNUT", "default_moisture_pct": 8.0},
    {"name": "Vegetables", "name_te": "కూరగాయలు", "code": "VEGETABLES", "default_moisture_pct": None},
    {"name": "Others", "name_te": "ఇతర", "code": "OTHERS", "default_moisture_pct": None},
    # Legacy operational / non-grain entries kept for existing orgs
    {"name": "Pulses", "name_te": "పప్పులు", "code": "PULSES", "default_moisture_pct": None},
    {"name": "Concrete Work", "name_te": "కాంక్రీట్ పని", "code": "CONCRETEWORK", "default_moisture_pct": None},
]
