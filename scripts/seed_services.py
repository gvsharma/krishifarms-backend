"""Idempotent seed for farm services master data (crop types, activity types, vehicle types)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.modules.financial.models import ExpenseCategory
from app.modules.master_data.models import CropType, Village
from app.modules.platform.models import ActivityType, PaymentMode, VehicleType
from app.modules.users.models import Organization, User
from scripts.data.fleet_inventory import DEFAULT_ACTIVITY_TYPES, DEFAULT_VEHICLE_TYPES

DEFAULT_VILLAGES = [
    {
        "name": "Bhairkhanpally",
        "mandal": "Nizamabad",
        "district": "Nizamabad",
        "state": "Telangana",
    },
]

DEFAULT_CROP_TYPES = [
    {"name": "Paddy", "code": "PADDY", "default_moisture_pct": 17.0},
    {"name": "Corn", "code": "CORN", "default_moisture_pct": 14.0},
    {"name": "Vegetables", "code": "VEGETABLES", "default_moisture_pct": None},
    {"name": "Pulses", "code": "PULSES", "default_moisture_pct": None},
    {"name": "Concrete Work", "code": "CONCRETEWORK", "default_moisture_pct": None},
]

DEFAULT_EXPENSE_CATEGORIES = [
    {"name": "Fuel", "type": "expense"},
    {"name": "Diesel", "type": "expense"},
    {"name": "Labor", "type": "expense"},
    {"name": "Maintenance", "type": "expense"},
    {"name": "Vehicle Repairs", "type": "expense"},
    {"name": "Godown Maintenance", "type": "expense"},
    {"name": "Miscellaneous", "type": "expense"},
]

DEFAULT_PAYMENT_MODES = [
    {"code": "cash", "name": "Cash", "name_te": "నగదు"},
    {"code": "upi", "name": "UPI", "name_te": "యూపీఐ"},
    {"code": "bank_transfer", "name": "Bank Transfer", "name_te": "బ్యాంక్ బదిలీ"},
]


def _owner_for_org(db: Session, org_id) -> User | None:
    return db.query(User).filter(User.org_id == org_id, User.is_active.is_(True)).order_by(User.created_at).first()


def _upsert_by_code(db: Session, model, org_id, owner_id, code_field: str, rows: list[dict]) -> tuple[int, int]:
    created = 0
    updated = 0
    for row in rows:
        code = row[code_field]
        existing = (
            db.query(model)
            .filter(getattr(model, "org_id") == org_id, getattr(model, code_field) == code)
            .first()
        )
        if existing:
            changed = False
            for key, value in row.items():
                if key == code_field:
                    continue
                if getattr(existing, key) != value:
                    setattr(existing, key, value)
                    changed = True
            if hasattr(existing, "deleted_at") and existing.deleted_at is not None:
                existing.deleted_at = None
                changed = True
            if hasattr(existing, "is_active") and not existing.is_active:
                existing.is_active = True
                changed = True
            if changed and hasattr(existing, "updated_by"):
                existing.updated_by = owner_id
                updated += 1
            continue
        payload = {**row, "org_id": org_id}
        if hasattr(model, "is_active"):
            payload["is_active"] = True
        if hasattr(model, "created_by"):
            payload["created_by"] = owner_id
            payload["updated_by"] = owner_id
        db.add(model(**payload))
        created += 1
    return created, updated


def _upsert_by_name(db: Session, model, org_id, owner_id, rows: list[dict]) -> tuple[int, int]:
    created = 0
    updated = 0
    for row in rows:
        existing = (
            db.query(model)
            .filter(model.org_id == org_id, model.name == row["name"])
            .first()
        )
        if existing:
            changed = False
            for key, value in row.items():
                if getattr(existing, key) != value:
                    setattr(existing, key, value)
                    changed = True
            if hasattr(existing, "deleted_at") and existing.deleted_at is not None:
                existing.deleted_at = None
                changed = True
            if changed and hasattr(existing, "updated_by"):
                existing.updated_by = owner_id
                updated += 1
            continue
        payload = {**row, "org_id": org_id}
        if hasattr(model, "created_by"):
            payload["created_by"] = owner_id
            payload["updated_by"] = owner_id
        db.add(model(**payload))
        created += 1
    return created, updated


def seed_services_for_org(db: Session, org: Organization, owner: User) -> dict[str, int]:
    stats = {"created": 0, "updated": 0}

    for village_data in DEFAULT_VILLAGES:
        existing = (
            db.query(Village)
            .filter(Village.org_id == org.id, Village.name == village_data["name"], Village.deleted_at.is_(None))
            .first()
        )
        if not existing:
            db.add(Village(org_id=org.id, created_by=owner.id, updated_by=owner.id, **village_data))
            stats["created"] += 1

    c, u = _upsert_by_code(db, CropType, org.id, owner.id, "code", DEFAULT_CROP_TYPES)
    stats["created"] += c
    stats["updated"] += u

    c, u = _upsert_by_name(db, ExpenseCategory, org.id, owner.id, DEFAULT_EXPENSE_CATEGORIES)
    stats["created"] += c
    stats["updated"] += u

    c, u = _upsert_by_code(db, PaymentMode, org.id, owner.id, "code", DEFAULT_PAYMENT_MODES)
    stats["created"] += c
    stats["updated"] += u

    c, u = _upsert_by_code(db, VehicleType, org.id, owner.id, "code", DEFAULT_VEHICLE_TYPES)
    stats["created"] += c
    stats["updated"] += u

    c, u = _upsert_by_code(db, ActivityType, org.id, owner.id, "code", DEFAULT_ACTIVITY_TYPES)
    stats["created"] += c
    stats["updated"] += u

    db.commit()
    return stats


def seed_all_orgs(db: Session) -> None:
    orgs = db.query(Organization).filter(Organization.is_active.is_(True)).all()
    if not orgs:
        print("No organizations found — run scripts/seed.py first")
        return
    for org in orgs:
        owner = _owner_for_org(db, org.id)
        if not owner:
            print(f"Skipping org {org.code}: no active user")
            continue
        stats = seed_services_for_org(db, org, owner)
        print(f"Org {org.code}: created={stats['created']} updated={stats['updated']}")


def main() -> None:
    db = SessionLocal()
    try:
        seed_all_orgs(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
