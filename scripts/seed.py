from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.financial.models import ExpenseCategory
from app.modules.master_data.models import CropType, Village
from app.modules.users.models import Organization, Permission, Role, User
from app.shared.permissions import ROLE_DEFINITIONS, ROLE_PERMISSIONS, SYSTEM_PERMISSIONS


DEFAULT_VILLAGES = [
    {"name": "Sample Village", "mandal": "Sample Mandal", "district": "Sample District", "state": "Telangana"},
]

DEFAULT_CROP_TYPES = [
    {"name": "Cotton", "code": "COTTON", "default_moisture_pct": 8.0},
    {"name": "Maize", "code": "MAIZE", "default_moisture_pct": 14.0},
]

DEFAULT_EXPENSE_CATEGORIES = [
    {"name": "Fuel", "type": "expense"},
    {"name": "Labor", "type": "expense"},
    {"name": "Maintenance", "type": "expense"},
    {"name": "Miscellaneous", "type": "expense"},
]


def seed_database(db: Session) -> None:
    existing_org = db.query(Organization).first()
    if existing_org:
        print("Seed skipped: organization already exists")
        return

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

    permission_map: dict[str, Permission] = {}
    for code, description in SYSTEM_PERMISSIONS:
        permission = Permission(code=code, description=description)
        db.add(permission)
        permission_map[code] = permission
    db.flush()

    role_map: dict[str, Role] = {}
    for role_code, role_name in ROLE_DEFINITIONS:
        role = Role(org_id=org.id, code=role_code, name=role_name, is_system=True)
        role.permissions = [permission_map[code] for code in ROLE_PERMISSIONS[role_code]]
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

    for village_data in DEFAULT_VILLAGES:
        db.add(Village(org_id=org.id, created_by=owner.id, updated_by=owner.id, **village_data))

    for crop_data in DEFAULT_CROP_TYPES:
        db.add(CropType(org_id=org.id, created_by=owner.id, updated_by=owner.id, is_active=True, **crop_data))

    for category_data in DEFAULT_EXPENSE_CATEGORIES:
        db.add(
            ExpenseCategory(
                org_id=org.id,
                created_by=owner.id,
                updated_by=owner.id,
                **category_data,
            )
        )

    db.commit()
    print("Seed completed successfully")
    print(f"Owner login: {settings.default_owner_email} / {settings.default_owner_password}")


def main() -> None:
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
