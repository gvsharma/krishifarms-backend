#!/usr/bin/env python3
"""Load temporary DEMO data for live API modules (farmers, procurements, platform).

Markers for purge (see scripts/purge_demo_data.py):
  - organization.settings.demo_data_loaded / demo_batch_id
  - notes / body containing [DEMO]
  - user emails ending with @demo.krishifarms.local
  - crop type codes DEMO-PADDY / DEMO-CORN (optional; prefer notes)

Idempotent: skips if org.settings.demo_data_loaded is true (use --force to re-seed after purge).

Usage (requires DATABASE_URL + SECRET_KEY for bank encryption):
  export DATABASE_URL=postgresql+psycopg2://...
  export SECRET_KEY=...
  python scripts/seed_demo_data.py
  python scripts/seed_demo_data.py --force
"""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from uuid import UUID

# Allow `python scripts/seed_demo_data.py` from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import app.models  # noqa: F401 — workers stub + ORM registration
from sqlalchemy.orm import Session

from app.core.client_context import ClientContext
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.farmers import service as farmer_service
from app.modules.farmers.schemas import (
    BankAccountCreateRequest,
    FarmerCreateRequest,
    LandParcelCreateRequest,
)
from app.modules.financial.models import ExpenseCategory
from app.modules.master_data.models import CropType, Village
from app.modules.platform import service as platform_service
from app.modules.platform.schemas import (
    BuyerCreateRequest,
    CommentCreateRequest,
    CropPriceCreateRequest,
    FieldAgentCreateRequest,
    TagCreateRequest,
)
from app.modules.procurements import service as procurement_service
from app.modules.procurements.schemas import ProcurementCreateRequest, WeighmentRequest
from app.modules.users.models import Organization, Permission, Role, User
from app.shared.permissions import ROLE_DEFINITIONS, ROLE_PERMISSIONS

DEMO_CLIENT = ClientContext(device_id="seed-demo", client_type="script", request_id="demo-seed")
DEMO_MARKER = "[DEMO]"
DEMO_BATCH_ID = "DEMO-2026-07"
DEMO_EMAIL_DOMAIN = "@demo.krishifarms.local"
DEMO_PASSWORD = "DemoPass123!"  # documented only; change in production envs

DEMO_VILLAGES = [
    {"name": "Bhairkhanpally", "mandal": "Bhongir", "district": "Yadadri Bhuvanagiri", "state": "Telangana", "pincode": "508116"},
    {"name": "Raigiri", "mandal": "Bhongir", "district": "Yadadri Bhuvanagiri", "state": "Telangana", "pincode": "508116"},
    {"name": "Turkapally", "mandal": "Bhongir", "district": "Yadadri Bhuvanagiri", "state": "Telangana", "pincode": "508116"},
]

DEMO_CROPS = [
    {"name": "Paddy", "code": "PADDY", "default_moisture_pct": 14.0},
    {"name": "Corn", "code": "CORN", "default_moisture_pct": 14.0},
]

DEMO_FARMERS = [
    ("Ramesh Reddy", "ఆర్. రెడ్డి", "9876500001"),
    ("Srinivas Rao", "శ్రీనివాస్ రావు", "9876500002"),
    ("Lakshmi Devi", "లక్ష్మీ దేవి", "9876500003"),
    ("Venkat Goud", "వెంకట్ గౌడ్", "9876500004"),
    ("Anitha Kumari", "అనిత కుమారి", "9876500005"),
    ("Narasimha Rao", "నరసింహ రావు", "9876500006"),
    ("Padma Reddy", "పద్మ రెడ్డి", "9876500007"),
    ("Krishna Murthy", "కృష్ణ మూర్తి", "9876500008"),
    ("Savitri Bai", "సావిత్రి బాయి", "9876500009"),
    ("Mohan Das", "మోహన్ దాస్", "9876500010"),
    ("Gopal Reddy", "గోపాల్ రెడ్డి", "9876500011"),
    ("Sunitha Yadav", "సునీతా యాదవ్", "9876500012"),
    ("Raju Naik", "రాజు నాయక్", "9876500013"),
    ("Bhaskar Rao", "భాస్కర్ రావు", "9876500014"),
    ("Meena Kumari", "మీనా కుమారి", "9876500015"),
]


def _ensure_bootstrap(db: Session) -> tuple[Organization, User]:
    """Create org/roles/owner if missing. Reuses migration-seeded permissions."""
    org = db.query(Organization).filter(Organization.code == "KRISHI").first()
    if org is None:
        org = db.query(Organization).first()

    if org is None:
        org = Organization(
            name=settings.default_org_name,
            code="KRISHI",
            default_locale="en",
            timezone="Asia/Kolkata",
            settings={"currency": "INR"},
            is_active=True,
        )
        db.add(org)
        db.flush()
        print(f"Created organization {org.code} ({org.id})")

        permission_map = {p.code: p for p in db.query(Permission).all()}
        if not permission_map:
            raise RuntimeError(
                "No permissions found. Run `alembic upgrade head` before seeding demo data."
            )

        role_map: dict[str, Role] = {}
        for role_code, role_name in ROLE_DEFINITIONS:
            role = Role(org_id=org.id, code=role_code, name=role_name, is_system=True)
            codes = ROLE_PERMISSIONS.get(role_code, [])
            role.permissions = [permission_map[c] for c in codes if c in permission_map]
            db.add(role)
            role_map[role_code] = role
        db.flush()

        owner = User(
            org_id=org.id,
            email=settings.default_owner_email,
            full_name=settings.default_owner_name,
            password_hash=hash_password(settings.default_owner_password),
            role_id=role_map["OWNER"].id,
            preferred_locale="en",
            is_active=True,
        )
        db.add(owner)
        db.flush()

        for village_data in [
            {"name": "Sample Village", "mandal": "Sample Mandal", "district": "Sample District", "state": "Telangana"},
        ]:
            db.add(Village(org_id=org.id, created_by=owner.id, updated_by=owner.id, **village_data))

        for crop_data in [
            {"name": "Cotton", "code": "COTTON", "default_moisture_pct": 8.0},
            {"name": "Maize", "code": "MAIZE", "default_moisture_pct": 14.0},
        ]:
            db.add(
                CropType(
                    org_id=org.id,
                    created_by=owner.id,
                    updated_by=owner.id,
                    is_active=True,
                    **crop_data,
                )
            )

        for category_data in [
            {"name": "Fuel", "type": "expense"},
            {"name": "Labor", "type": "expense"},
            {"name": "Maintenance", "type": "expense"},
            {"name": "Miscellaneous", "type": "expense"},
        ]:
            db.add(
                ExpenseCategory(
                    org_id=org.id,
                    created_by=owner.id,
                    updated_by=owner.id,
                    **category_data,
                )
            )
        db.commit()
        db.refresh(org)
        print(f"Bootstrap complete. Owner: {settings.default_owner_email} / {settings.default_owner_password}")
    else:
        owner = (
            db.query(User)
            .filter(User.org_id == org.id, User.email == settings.default_owner_email, User.deleted_at.is_(None))
            .first()
        )
        if owner is None:
            owner = (
                db.query(User)
                .join(Role, User.role_id == Role.id)
                .filter(User.org_id == org.id, Role.code == "OWNER", User.deleted_at.is_(None))
                .first()
            )
        if owner is None:
            raise RuntimeError(f"Organization {org.code} exists but no OWNER user found")

    return org, owner


def _role_id(db: Session, org_id: UUID, code: str) -> UUID:
    role = db.query(Role).filter(Role.org_id == org_id, Role.code == code).first()
    if role is None:
        raise RuntimeError(f"Role {code} missing for org {org_id}")
    return role.id


def _ensure_demo_users(db: Session, org: Organization, actor_id: UUID) -> dict[str, User]:
    users: dict[str, User] = {}
    specs = [
        ("manager", "MANAGER", "Demo Manager"),
        ("agent", "AGENT", "Demo Field Agent"),
    ]
    for local, role_code, full_name in specs:
        email = f"{local}{DEMO_EMAIL_DOMAIN}"
        existing = (
            db.query(User)
            .filter(User.org_id == org.id, User.email == email, User.deleted_at.is_(None))
            .first()
        )
        if existing:
            users[role_code] = existing
            continue
        user = User(
            org_id=org.id,
            email=email,
            full_name=full_name,
            password_hash=hash_password(DEMO_PASSWORD),
            role_id=_role_id(db, org.id, role_code),
            preferred_locale="en",
            is_active=True,
            phone=f"90000000{10 if role_code == 'MANAGER' else 11}",
            created_by=actor_id,
            updated_by=actor_id,
        )
        db.add(user)
        db.flush()
        users[role_code] = user
        print(f"  user {email} / {DEMO_PASSWORD} ({role_code})")
    db.commit()
    return users


def _ensure_villages(db: Session, org: Organization, actor_id: UUID) -> list[Village]:
    villages: list[Village] = []
    for data in DEMO_VILLAGES:
        row = (
            db.query(Village)
            .filter(Village.org_id == org.id, Village.name == data["name"], Village.deleted_at.is_(None))
            .first()
        )
        if row is None:
            row = Village(org_id=org.id, created_by=actor_id, updated_by=actor_id, **data)
            db.add(row)
            db.flush()
        villages.append(row)
    db.commit()
    return villages


def _ensure_crops(db: Session, org: Organization, actor_id: UUID) -> list[CropType]:
    crops: list[CropType] = []
    for data in DEMO_CROPS:
        row = (
            db.query(CropType)
            .filter(CropType.org_id == org.id, CropType.code == data["code"], CropType.deleted_at.is_(None))
            .first()
        )
        if row is None:
            row = CropType(
                org_id=org.id,
                created_by=actor_id,
                updated_by=actor_id,
                is_active=True,
                **data,
            )
            db.add(row)
            db.flush()
        crops.append(row)
    db.commit()
    return crops


def seed_demo(db: Session, *, force: bool = False) -> None:
    org, owner = _ensure_bootstrap(db)
    settings_map = dict(org.settings or {})
    if settings_map.get("demo_data_loaded") and not force:
        print("Demo data already loaded (org.settings.demo_data_loaded). Use --force after purge.")
        return

    actor_id = owner.id
    print(f"Seeding demo batch {DEMO_BATCH_ID} for org {org.code}…")

    demo_users = _ensure_demo_users(db, org, actor_id)
    villages = _ensure_villages(db, org, actor_id)
    crops = _ensure_crops(db, org, actor_id)

    # Buyers + agents
    buyers = []
    for i, name in enumerate(["Demo Rice Mill", "Demo Corn Buyer"], start=1):
        buyers.append(
            platform_service.create_buyer(
                db,
                org.id,
                BuyerCreateRequest(
                    name=name,
                    phone=f"98480000{i:02d}",
                    village_id=villages[0].id,
                    notes=f"{DEMO_MARKER} buyer {i}",
                ),
                actor_id,
                DEMO_CLIENT,
            )
        )

    agents = []
    for i, name in enumerate(["Demo Agent One", "Demo Agent Two"], start=1):
        agents.append(
            platform_service.create_agent(
                db,
                org.id,
                FieldAgentCreateRequest(
                    name=name,
                    phone=f"98481000{i:02d}",
                    village_id=villages[i % len(villages)].id,
                    user_id=demo_users["AGENT"].id if i == 1 else None,
                    commission_pct=Decimal("2.00"),
                    notes=f"{DEMO_MARKER} field agent {i}",
                ),
                actor_id,
                DEMO_CLIENT,
            )
        )

    today = date.today()
    for crop in crops:
        rate = Decimal("2200.00") if crop.code == "PADDY" else Decimal("1850.00")
        platform_service.create_crop_price(
            db,
            org.id,
            CropPriceCreateRequest(
                crop_type_id=crop.id,
                village_id=None,
                effective_from=today - timedelta(days=60),
                effective_to=None,
                rate_per_quintal=rate,
                notes=f"{DEMO_MARKER} price rule {crop.code}",
                is_active=True,
            ),
            actor_id,
            DEMO_CLIENT,
        )

    farmers = []
    for idx, (name, name_te, phone) in enumerate(DEMO_FARMERS):
        village = villages[idx % len(villages)]
        farmer = farmer_service.create_farmer(
            db,
            org.id,
            FarmerCreateRequest(
                full_name=name,
                full_name_te=name_te,
                phone_primary=phone,
                village_id=village.id,
                address=f"{DEMO_MARKER} address, {village.name}",
                notes=f"{DEMO_MARKER} farmer seed",
                aadhaar_last4=f"{1000 + idx:04d}"[-4:],
            ),
            actor_id,
            DEMO_CLIENT,
        )
        farmers.append(farmer)

        if idx < 5:
            farmer_service.create_bank_account(
                db,
                org.id,
                farmer.id,
                BankAccountCreateRequest(
                    account_holder_name=name,
                    bank_name="State Bank of India",
                    branch=village.name,
                    ifsc="SBIN0001234",
                    account_number=f"30123456{idx:04d}",
                    is_primary=True,
                ),
                actor_id,
                DEMO_CLIENT,
            )
            farmer_service.create_land_parcel(
                db,
                org.id,
                farmer.id,
                LandParcelCreateRequest(
                    survey_number=f"DEMO-SY-{idx + 1}",
                    acres=Decimal("2.50") + Decimal(idx) * Decimal("0.25"),
                    land_type="dry",
                    location_notes=f"{DEMO_MARKER} parcel",
                ),
                actor_id,
                DEMO_CLIENT,
            )

    # Procurements across workflow states
    # 0-4 draft (create only), 5-9 submitted+weighed path partial, 10-19 full confirm, 20-24 priced only
    statuses_plan = (
        ["draft"] * 5
        + ["weighed"] * 5
        + ["confirmed"] * 10
        + ["priced"] * 5
    )
    procurements = []
    for i, target in enumerate(statuses_plan):
        farmer = farmers[i % len(farmers)]
        crop = crops[i % len(crops)]
        village = next(v for v in villages if v.id == farmer.village_id)
        proc_date = today - timedelta(days=(i % 20))
        row = procurement_service.create_procurement(
            db,
            org.id,
            ProcurementCreateRequest(
                farmer_id=farmer.id,
                crop_type_id=crop.id,
                village_id=village.id,
                procurement_date=proc_date,
                bag_count=10 + i,
                notes=f"{DEMO_MARKER} procurement {i + 1} target={target}",
            ),
            actor_id,
            DEMO_CLIENT,
            idempotency_key=f"demo-{DEMO_BATCH_ID}-{i + 1}",
        )

        if target == "draft":
            procurements.append(row)
            continue

        row = procurement_service.submit_procurement(
            db, org.id, row.id, proc_date, actor_id, DEMO_CLIENT
        )
        gross = Decimal("520.00") + Decimal(i) * Decimal("12.5")
        tare = Decimal("20.00")
        row = procurement_service.record_weighment(
            db,
            org.id,
            row.id,
            proc_date,
            WeighmentRequest(
                gross_weight_kg=gross,
                tare_weight_kg=tare,
                moisture_pct=Decimal("12.5"),
                bag_count=10 + i,
            ),
            actor_id,
            DEMO_CLIENT,
        )
        if target == "weighed":
            procurements.append(row)
            continue

        row = procurement_service.apply_price(
            db, org.id, row.id, proc_date, actor_id, DEMO_CLIENT
        )
        if target == "priced":
            procurements.append(row)
            continue

        row = procurement_service.confirm_procurement(
            db, org.id, row.id, proc_date, actor_id, DEMO_CLIENT
        )
        procurements.append(row)

    # Comments + tags on a few entities
    for farmer in farmers[:3]:
        platform_service.create_comment(
            db,
            org.id,
            CommentCreateRequest(
                entity_type="farmer",
                entity_id=farmer.id,
                body=f"{DEMO_MARKER} Follow up for next harvest",
                body_te=f"{DEMO_MARKER} తదుపరి పంట",
            ),
            actor_id,
            DEMO_CLIENT,
        )
        platform_service.create_tag(
            db,
            org.id,
            TagCreateRequest(entity_type="farmer", entity_id=farmer.id, tag="demo"),
            actor_id,
            DEMO_CLIENT,
        )

    for proc in procurements[:5]:
        platform_service.create_comment(
            db,
            org.id,
            CommentCreateRequest(
                entity_type="procurement",
                entity_id=proc.id,
                body=f"{DEMO_MARKER} Weighment verified on site",
            ),
            actor_id,
            DEMO_CLIENT,
        )
        platform_service.create_tag(
            db,
            org.id,
            TagCreateRequest(entity_type="procurement", entity_id=proc.id, tag="demo"),
            actor_id,
            DEMO_CLIENT,
        )

    settings_map["currency"] = settings_map.get("currency", "INR")
    settings_map["demo_data_loaded"] = True
    settings_map["demo_batch_id"] = DEMO_BATCH_ID
    settings_map["demo_marker"] = DEMO_MARKER
    org.settings = settings_map
    db.add(org)
    db.commit()

    confirmed = sum(1 for p in procurements if p.status == "confirmed")
    print("Demo seed complete:")
    print(f"  villages={len(villages)} crops={len(crops)} farmers={len(farmers)}")
    print(f"  buyers={len(buyers)} agents={len(agents)} procurements={len(procurements)} (confirmed={confirmed})")
    print(f"  OWNER: {settings.default_owner_email} / {settings.default_owner_password}")
    print(f"  MANAGER: manager{DEMO_EMAIL_DOMAIN} / {DEMO_PASSWORD}")
    print(f"  AGENT:   agent{DEMO_EMAIL_DOMAIN} / {DEMO_PASSWORD}")
    print("  Purge with: python scripts/purge_demo_data.py")


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed KrishiFarms DEMO data for live modules")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Load even if demo_data_loaded is set (prefer purge first to avoid duplicates)",
    )
    args = parser.parse_args()
    db = SessionLocal()
    try:
        seed_demo(db, force=args.force)
    finally:
        db.close()


if __name__ == "__main__":
    main()
