"""Derive mobile RBAC payload from authenticated user."""

from __future__ import annotations

from app.modules.auth.permission_catalog import (
    BACKEND_TO_MOBILE,
    MODULE_ORDER,
    MODULE_VIEW_PERMISSIONS,
    ROLE_MOBILE_PERMISSIONS,
)
from app.modules.users.models import User


def _permissions_from_role(role_code: str) -> set[str]:
    return set(ROLE_MOBILE_PERMISSIONS.get(role_code.upper(), ROLE_MOBILE_PERMISSIONS["WORKER"]))


def _permissions_from_db(user: User) -> set[str]:
    mobile: set[str] = set()
    for perm in user.role.permissions:
        mapped = BACKEND_TO_MOBILE.get(perm.code)
        if mapped:
            mobile.add(mapped)
    return mobile


def resolve_mobile_permissions(user: User) -> set[str]:
    """Permissions are authoritative — derived from role catalog, merged with DB mapping."""
    role_code = user.role.code.upper() if user.role else "WORKER"
    role_based = _permissions_from_role(role_code)
    db_based = _permissions_from_db(user)
    return role_based | db_based


def derive_accessible_modules(permissions: set[str]) -> list[str]:
    modules: list[str] = ["dashboard"]
    for module, required in MODULE_VIEW_PERMISSIONS.items():
        if module == "dashboard":
            continue
        if permissions.intersection(required):
            modules.append(module)
    return sorted(set(modules), key=lambda m: MODULE_ORDER.get(m, 999))


def build_rbac_payload(user: User) -> dict:
    permissions = sorted(resolve_mobile_permissions(user))
    roles = [user.role.code] if user.role else []
    return {
        "roles": roles,
        "permissions": permissions,
        "accessibleModules": derive_accessible_modules(set(permissions)),
    }


def build_auth_user(user: User) -> dict:
    return {
        "id": str(user.id),
        "name": user.full_name,
        "mobile": user.phone or "",
        "email": user.email,
    }
