#!/usr/bin/env python3
"""Idempotent seed for KrishiFarms Rangareddy service-area villages.

Populates org-scoped `villages` rows for eight mandals (Keshampet, Kothur, Midjil,
Farooqnagar, Maheshwaram, Talakondapally, Balanagar, Amangal) from Census 2011 /
Telangana revenue records.

Usage (requires DATABASE_URL):
  python scripts/seed_service_area_villages.py
  python scripts/seed_service_area_villages.py --org-code KRISHI

Safe to re-run: upserts by (org_id, name); restores soft-deleted rows.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.modules.master_data.models import Village
from app.modules.users.models import Organization, User
from scripts.data.rangareddy_service_villages import (
    RANGAREDDY_SERVICE_MANDALS,
    flatten_service_villages,
    mandal_village_counts,
)


def _owner_for_org(db: Session, org_id) -> User | None:
    return db.query(User).filter(User.org_id == org_id, User.is_active.is_(True)).order_by(User.created_at).first()


def _upsert_village(
    db: Session,
    org_id,
    owner_id,
    row: dict[str, str],
) -> tuple[str, bool]:
    """Return (action, changed) where action is created|updated|unchanged."""
    existing = (
        db.query(Village)
        .filter(Village.org_id == org_id, Village.name == row["name"])
        .first()
    )
    if existing is None:
        db.add(
            Village(
                org_id=org_id,
                created_by=owner_id,
                updated_by=owner_id,
                **row,
            )
        )
        return "created", True

    changed = False
    for field in ("mandal", "district", "state", "pincode"):
        value = row.get(field)
        if value is not None and getattr(existing, field) != value:
            setattr(existing, field, value)
            changed = True
    if existing.deleted_at is not None:
        existing.deleted_at = None
        changed = True
    if changed:
        existing.updated_by = owner_id
        return "updated", True
    return "unchanged", False


def seed_service_area_villages_for_org(
    db: Session,
    org: Organization,
    owner: User,
    *,
    commit: bool = True,
) -> dict[str, int]:
    stats = {"created": 0, "updated": 0, "unchanged": 0}
    for row in flatten_service_villages():
        action, _ = _upsert_village(db, org.id, owner.id, row)
        stats[action] += 1
    if commit:
        db.commit()
    return stats


def seed_orgs(db: Session, org_code: str | None = None) -> None:
    query = db.query(Organization).filter(Organization.is_active.is_(True))
    if org_code:
        query = query.filter(Organization.code == org_code)
    orgs = query.all()
    if not orgs:
        print("No matching organizations found — run scripts/seed.py first")
        return

    counts = mandal_village_counts()
    total = sum(counts.values())
    print(f"Service-area pack: {len(RANGAREDDY_SERVICE_MANDALS)} mandals, {total} villages")
    for mandal, count in counts.items():
        print(f"  {mandal}: {count}")

    for org in orgs:
        owner = _owner_for_org(db, org.id)
        if owner is None:
            print(f"Skipping org {org.code}: no active user")
            continue
        stats = seed_service_area_villages_for_org(db, org, owner)
        print(
            f"Org {org.code}: created={stats['created']} "
            f"updated={stats['updated']} unchanged={stats['unchanged']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed Rangareddy service-area villages")
    parser.add_argument("--org-code", default=None, help="Limit to one organization code (default: all active orgs)")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        seed_orgs(db, org_code=args.org_code)
    finally:
        db.close()


if __name__ == "__main__":
    main()
