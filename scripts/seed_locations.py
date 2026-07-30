"""Idempotent seed for district / mandal / village location masters.

Preloads Rangareddy service-area mandals (Keshampeta, Talakondapally,
Maheshwaram, Kothur, Farooqnagar) and villages with pincodes.

Usage:
    python -m scripts.seed_locations
    # or via docker:
    docker compose -f infra/docker-compose.yml exec api python -m scripts.seed_locations
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.modules.master_data.models import District, Mandal, Village
from app.modules.users.models import Organization, User
from scripts.data.rangareddy_service_villages import DISTRICT, STATE, RANGAREDDY_MANDALS, iter_village_rows


def _owner_for_org(db: Session, org_id) -> User | None:
    return db.query(User).filter(User.org_id == org_id, User.is_active.is_(True)).order_by(User.created_at).first()


def _upsert_district(db: Session, org_id, owner_id, name: str, state: str | None) -> tuple[District, bool]:
    existing = (
        db.query(District)
        .filter(District.org_id == org_id, District.name == name)
        .first()
    )
    if existing:
        changed = False
        if existing.deleted_at is not None:
            existing.deleted_at = None
            changed = True
        if state and existing.state != state:
            existing.state = state
            changed = True
        if changed:
            existing.updated_by = owner_id
        return existing, False
    district = District(
        org_id=org_id,
        name=name,
        state=state,
        created_by=owner_id,
        updated_by=owner_id,
    )
    db.add(district)
    db.flush()
    return district, True


def _upsert_mandal(
    db: Session, org_id, owner_id, district: District, name: str
) -> tuple[Mandal, bool]:
    existing = (
        db.query(Mandal)
        .filter(
            Mandal.org_id == org_id,
            Mandal.district_id == district.id,
            Mandal.name == name,
        )
        .first()
    )
    if existing:
        if existing.deleted_at is not None:
            existing.deleted_at = None
            existing.updated_by = owner_id
        return existing, False
    mandal = Mandal(
        org_id=org_id,
        district_id=district.id,
        name=name,
        created_by=owner_id,
        updated_by=owner_id,
    )
    db.add(mandal)
    db.flush()
    return mandal, True


def _upsert_village(
    db: Session,
    org_id,
    owner_id,
    *,
    name: str,
    name_te: str | None,
    mandal_name: str,
    district_name: str,
    state: str,
    pincode: str | None,
    district: District,
    mandal: Mandal,
) -> bool:
    existing = (
        db.query(Village)
        .filter(Village.org_id == org_id, Village.name == name, Village.mandal == mandal_name)
        .first()
    )
    if existing:
        changed = False
        for key, value in {
            "district": district_name,
            "state": state,
            "pincode": pincode or None,
            "district_id": district.id,
            "mandal_id": mandal.id,
            "mandal": mandal_name,
            "name_te": name_te or None,
        }.items():
            if getattr(existing, key) != value:
                setattr(existing, key, value)
                changed = True
        if existing.deleted_at is not None:
            existing.deleted_at = None
            changed = True
        if changed:
            existing.updated_by = owner_id
        return False
    db.add(
        Village(
            org_id=org_id,
            name=name,
            name_te=name_te or None,
            mandal=mandal_name,
            district=district_name,
            state=state,
            pincode=pincode or None,
            district_id=district.id,
            mandal_id=mandal.id,
            created_by=owner_id,
            updated_by=owner_id,
        )
    )
    return True


def seed_locations_for_org(db: Session, org: Organization, owner: User) -> dict[str, int]:
    stats = {"districts": 0, "mandals": 0, "villages": 0}

    district, created = _upsert_district(db, org.id, owner.id, DISTRICT, STATE)
    if created:
        stats["districts"] += 1

    mandal_map: dict[str, Mandal] = {}
    for mandal_name in RANGAREDDY_MANDALS:
        mandal, created = _upsert_mandal(db, org.id, owner.id, district, mandal_name)
        mandal_map[mandal_name] = mandal
        if created:
            stats["mandals"] += 1

    for row in iter_village_rows():
        mandal = mandal_map[row["mandal"]]
        created = _upsert_village(
            db,
            org.id,
            owner.id,
            name=row["name"],
            name_te=row.get("name_te") or None,
            mandal_name=row["mandal"],
            district_name=row["district"],
            state=row["state"],
            pincode=row.get("pincode"),
            district=district,
            mandal=mandal,
        )
        if created:
            stats["villages"] += 1

    db.commit()
    return stats


def seed_locations(db: Session | None = None) -> None:
    own_session = db is None
    if own_session:
        db = SessionLocal()
    assert db is not None
    try:
        orgs = db.query(Organization).filter(Organization.is_active.is_(True)).all()
        if not orgs:
            print("No organizations found — run scripts/seed.py first")
            return
        for org in orgs:
            owner = _owner_for_org(db, org.id)
            if owner is None:
                print(f"Skip org {org.code}: no active user")
                continue
            stats = seed_locations_for_org(db, org, owner)
            print(
                f"Locations seeded for {org.code}: "
                f"+{stats['districts']} districts, +{stats['mandals']} mandals, "
                f"+{stats['villages']} villages"
            )
    finally:
        if own_session:
            db.close()


def main() -> None:
    seed_locations()


if __name__ == "__main__":
    main()
