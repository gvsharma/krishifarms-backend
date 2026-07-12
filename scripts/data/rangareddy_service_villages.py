"""Rangareddy district service-area location masters (district → mandal → village).

Idempotent seed source for KrishiFarms ops around Keshampeta, Talakondapally,
Maheshwaram, Kothur, and Farooqnagar mandals. Pincodes included where known.
"""

from __future__ import annotations

STATE = "Telangana"
DISTRICT = "Rangareddy"

# Mandal → list of villages {name, pincode?}
RANGAREDDY_MANDALS: dict[str, list[dict[str, str]]] = {
    "Keshampeta": [
        {"name": "Keshampeta", "pincode": "509408"},
        {"name": "Kakloor", "pincode": "509408"},
        {"name": "Lingampally", "pincode": "509408"},
        {"name": "Chowderpally", "pincode": "509408"},
        {"name": "Ippalapally", "pincode": "509408"},
        {"name": "Lemoor", "pincode": "509408"},
        {"name": "Boduppal", "pincode": "509408"},
    ],
    "Talakondapally": [
        {"name": "Talakondapally", "pincode": "509320"},
        {"name": "Antharam", "pincode": "509320"},
        {"name": "Chowderguda", "pincode": "509320"},
        {"name": "Gundlapochampally", "pincode": "509320"},
        {"name": "Serilingampally", "pincode": "509320"},
        {"name": "Ravalkole", "pincode": "509320"},
    ],
    "Maheshwaram": [
        {"name": "Maheshwaram", "pincode": "501359"},
        {"name": "Imamguda", "pincode": "501359"},
        {"name": "Thummaloor", "pincode": "501359"},
        {"name": "Sardarnagar", "pincode": "501359"},
        {"name": "Kongarakalan", "pincode": "501359"},
        {"name": "Mansanpally", "pincode": "501359"},
        {"name": "Raviryal", "pincode": "501359"},
    ],
    "Kothur": [
        {"name": "Kothur", "pincode": "509228"},
        {"name": "Penjerla", "pincode": "509228"},
        {"name": "Thimmapur", "pincode": "509228"},
        {"name": "Edulabad", "pincode": "509228"},
        {"name": "Nandigama", "pincode": "509228"},
        {"name": "Pudugur", "pincode": "509228"},
    ],
    "Farooqnagar": [
        {"name": "Farooqnagar", "pincode": "509216"},
        {"name": "Burgula", "pincode": "509216"},
        {"name": "Solipur", "pincode": "509216"},
        {"name": "Chinchode", "pincode": "509216"},
        {"name": "Elikatta", "pincode": "509216"},
        {"name": "Raikal", "pincode": "509216"},
        {"name": "Shadnagar", "pincode": "509216"},
    ],
}


def iter_village_rows() -> list[dict[str, str]]:
    """Flat village rows suitable for Village upsert (name, mandal, district, state, pincode)."""
    rows: list[dict[str, str]] = []
    for mandal, villages in RANGAREDDY_MANDALS.items():
        for village in villages:
            rows.append(
                {
                    "name": village["name"],
                    "mandal": mandal,
                    "district": DISTRICT,
                    "state": STATE,
                    "pincode": village.get("pincode", ""),
                }
            )
    return rows
