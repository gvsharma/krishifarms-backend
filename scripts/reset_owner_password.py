#!/usr/bin/env python3
"""Reset OWNER password (default email from settings). Usage: python scripts/reset_owner_password.py [new_password]"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.modules.users.models import User


def main() -> None:
    new_password = sys.argv[1] if len(sys.argv) > 1 else settings.default_owner_password
    db = SessionLocal()
    try:
        user = (
            db.query(User)
            .filter(User.email == settings.default_owner_email, User.deleted_at.is_(None))
            .first()
        )
        if user is None:
            print(f"ERROR: user not found: {settings.default_owner_email}", file=sys.stderr)
            sys.exit(1)
        user.password_hash = hash_password(new_password)
        user.is_active = True
        db.commit()
        print(f"Password reset for {user.email} (role_id={user.role_id}, active={user.is_active})")
    finally:
        db.close()


if __name__ == "__main__":
    main()
