"""Idempotent seed for farm services master data (crop types, activity types, vehicle types)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.modules.financial.models import ExpenseCategory
from app.modules.master_data.models import CropType, Village
from app.modules.platform.models import ActivityType, PaymentMode, VehicleType
from app.modules.users.models import Organization, User

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

DEFAULT_VEHICLE_TYPES = [
    {"code": "BOLERO", "name": "Bolero", "name_te": "బోలేరో", "fuel_type": "diesel"},
    {"code": "DCM", "name": "DCM", "name_te": "డీసీఎం", "fuel_type": "diesel"},
    {"code": "CULTIVATOR", "name": "Cultivator", "name_te": "కల్టివేటర్", "fuel_type": "tractor"},
    {"code": "ROTAVATOR", "name": "Rotavator", "name_te": "రోటవేటర్", "fuel_type": "tractor"},
    {"code": "TROLLEY", "name": "Trolley", "name_te": "ట్రాలీ", "fuel_type": "tractor"},
    {"code": "BALER", "name": "Baler", "name_te": "బేలర్", "fuel_type": "tractor"},
    {"code": "CLEANING_MACHINE", "name": "Cleaning Machine", "name_te": "క్లీనింగ్ మెషిన్", "fuel_type": "diesel"},
]

DEFAULT_ACTIVITY_TYPES = [
    # Field services
    {"code": "FIELD_PLOUGHING", "name": "Ploughing", "name_te": "దున్నుట", "service_category": "field_service", "default_rate_type": "hourly"},
    {"code": "FIELD_SPRAYING", "name": "Spraying", "name_te": "పిచికారీ", "service_category": "field_service", "default_rate_type": "hourly"},
    {"code": "FIELD_OTHER", "name": "Other Field Service", "name_te": "ఇతర ఫీల్డ్ సేవ", "service_category": "field_service", "default_rate_type": "fixed"},
    # Tractor work
    {"code": "TRACTOR_CULTIVATOR", "name": "Cultivator Work", "name_te": "కల్టివేటర్ పని", "service_category": "tractor_work", "default_rate_type": "hourly"},
    {"code": "TRACTOR_ROTAVATOR", "name": "Rotavator Work", "name_te": "రోటవేటర్ పని", "service_category": "tractor_work", "default_rate_type": "hourly"},
    {"code": "TRACTOR_TROLLEY", "name": "Trolley Work", "name_te": "ట్రాలీ పని", "service_category": "tractor_work", "default_rate_type": "fixed"},
    {"code": "TRACTOR_BALER", "name": "Baler Work", "name_te": "బేలర్ పని", "service_category": "tractor_work", "default_rate_type": "fixed"},
    {"code": "TRACTOR_CLEANING", "name": "Cleaning Machine Work", "name_te": "క్లీనింగ్ మెషిన్ పని", "service_category": "tractor_work", "default_rate_type": "hourly"},
    # Transport
    {"code": "TRANSPORT_BOLERO", "name": "Bolero Carrying", "name_te": "బోలేరో రవాణా", "service_category": "transport", "default_rate_type": "fixed"},
    {"code": "TRANSPORT_DCM", "name": "DCM Carrying", "name_te": "డీసీఎం రవాణా", "service_category": "transport", "default_rate_type": "fixed"},
    # Fertiliser
    {"code": "FERT_UREA", "name": "Urea Supply", "name_te": "యూరియా సరఫరా", "service_category": "fertiliser", "default_rate_type": "fixed"},
    {"code": "FERT_DAP", "name": "DAP Supply", "name_te": "డీఏపీ సరఫరా", "service_category": "fertiliser", "default_rate_type": "fixed"},
    {"code": "FERT_OTHER", "name": "Other Fertiliser", "name_te": "ఇతర ఎరువులు", "service_category": "fertiliser", "default_rate_type": "fixed"},
    # Seeds
    {"code": "SEED_PADDY", "name": "Paddy Seeds", "name_te": "వరి విత్తనాలు", "service_category": "seeds", "default_rate_type": "fixed"},
    {"code": "SEED_CORN", "name": "Corn Seeds", "name_te": "మొక్కజొన్న విత్తనాలు", "service_category": "seeds", "default_rate_type": "fixed"},
    {"code": "SEED_OTHER", "name": "Other Seeds", "name_te": "ఇతర విత్తనాలు", "service_category": "seeds", "default_rate_type": "fixed"},
    # Agri-finance
    {"code": "AGRI_FINANCE_LOAN", "name": "Agri Finance Loan", "name_te": "వ్యవసాయ రుణం", "service_category": "agri_finance", "default_rate_type": "fixed"},
    {"code": "AGRI_FINANCE_ADVANCE", "name": "Agri Finance Advance", "name_te": "వ్యవసాయ అడ్వాన్స్", "service_category": "agri_finance", "default_rate_type": "fixed"},
    # Vehicle ops
    {"code": "VEHICLE_REPAIR", "name": "Vehicle Repair", "name_te": "వాహన మరమ్మతు", "service_category": "vehicle_ops", "default_rate_type": "fixed"},
    {"code": "VEHICLE_MAINTENANCE", "name": "Vehicle Maintenance", "name_te": "వాహన నిర్వహణ", "service_category": "vehicle_ops", "default_rate_type": "fixed"},
    {"code": "VEHICLE_CLEANING", "name": "Vehicle Cleaning", "name_te": "వాహన శుభ్రత", "service_category": "vehicle_ops", "default_rate_type": "fixed"},
    # Godown
    {"code": "GODOWN_REPAIR", "name": "Godown Repair", "name_te": "గోడౌన్ మరమ్మతు", "service_category": "godown", "default_rate_type": "fixed"},
    {"code": "GODOWN_PURCHASE", "name": "Godown Purchase", "name_te": "గోడౌన్ కొనుగోలు", "service_category": "godown", "default_rate_type": "fixed"},
    {"code": "GODOWN_CLEANING", "name": "Godown Cleaning", "name_te": "గోడౌన్ శుభ్రత", "service_category": "godown", "default_rate_type": "fixed"},
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
