"""Unit tests for mobile RBAC permission catalog and module derivation."""

from types import SimpleNamespace

from app.modules.auth.permission_catalog import (
    EXPENSE_VIEW,
    FARMER_VIEW,
    PROCUREMENT_VIEW,
    ROLE_MOBILE_PERMISSIONS,
    USER_MANAGE,
    WORKER_VIEW,
)
from app.modules.auth.rbac import build_rbac_payload, derive_accessible_modules, resolve_mobile_permissions


def _user(role_code: str, db_permissions: list[str] | None = None) -> SimpleNamespace:
    perms = [SimpleNamespace(code=c) for c in (db_permissions or [])]
    role = SimpleNamespace(code=role_code, permissions=perms)
    return SimpleNamespace(id="user-1", role=role)


def test_owner_has_user_manage():
    perms = resolve_mobile_permissions(_user("OWNER"))
    assert USER_MANAGE in perms


def test_manager_lacks_user_manage():
    perms = resolve_mobile_permissions(_user("MANAGER"))
    assert USER_MANAGE not in perms
    assert FARMER_VIEW in perms
    assert PROCUREMENT_VIEW in perms


def test_worker_has_work_order_permissions_only():
    perms = resolve_mobile_permissions(_user("WORKER"))
    assert FARMER_VIEW not in perms
    assert "WORK_ORDER_VIEW" in perms


def test_accountant_has_expense_permissions():
    perms = resolve_mobile_permissions(_user("ACCOUNTANT"))
    assert EXPENSE_VIEW in perms
    assert PROCUREMENT_VIEW in perms
    assert FARMER_CREATE not in perms


def test_derive_accessible_modules_includes_dashboard():
    modules = derive_accessible_modules({FARMER_VIEW, WORKER_VIEW})
    assert "dashboard" in modules
    assert "farmers" in modules
    assert "workers" in modules


def test_build_rbac_payload_shape():
    payload = build_rbac_payload(_user("MANAGER"))
    assert payload["roles"] == ["MANAGER"]
    assert isinstance(payload["permissions"], list)
    assert isinstance(payload["accessibleModules"], list)
    assert "farmers" in payload["accessibleModules"]


def test_all_catalog_roles_defined():
    for role in ("OWNER", "MANAGER", "WORKER", "ACCOUNTANT"):
        assert role in ROLE_MOBILE_PERMISSIONS
        assert len(ROLE_MOBILE_PERMISSIONS[role]) > 0
