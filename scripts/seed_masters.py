#!/usr/bin/env python3
"""Idempotent master-data seed: locations, crops, services, expense categories.

Run after DB purge or on deploy so Keshampeta / Kothur villages and dropdown
masters repopulate without manual entry.

Usage:
  python scripts/seed_masters.py
  docker compose -f infra/docker-compose.prod.yml exec -T api python scripts/seed_masters.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app.models  # noqa: F401 — register FK targets before ORM flush

from app.core.database import SessionLocal
from app.modules.users.models import Organization, User
from scripts.seed_locations import seed_locations_for_org
from scripts.seed_services import seed_services_for_org


def _owner_for_org(db, org_id) -> User | None:
    return db.query(User).filter(User.org_id == org_id, User.is_active.is_(True)).order_by(User.created_at).first()


def seed_masters(db=None) -> None:
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
            loc = seed_locations_for_org(db, org, owner)
            svc = seed_services_for_org(db, org, owner)
            print(
                f"Masters seeded for {org.code}: "
                f"locations +{loc['districts']}d +{loc['mandals']}m +{loc['villages']}v; "
                f"services created={svc['created']} updated={svc['updated']}"
            )
    finally:
        if own_session:
            db.close()


def main() -> None:
    seed_masters()


if __name__ == "__main__":
    main()
