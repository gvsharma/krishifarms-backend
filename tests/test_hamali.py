"""Tests for HAMALI role and RBAC."""

from types import SimpleNamespace

from app.modules.auth.permission_catalog import HAMALI_VIEW, ROLE_MOBILE_PERMISSIONS, resolve_mobile_permissions
from app.modules.auth.rbac import derive_accessible_modules
from app.shared.permissions import ROLE_DEFINITIONS, ROLE_PERMISSIONS


def _user(role_code: str):
    role = SimpleNamespace(code=role_code, permissions=[])
    return SimpleNamespace(id="u1", role=role, worker_id="worker-1")


def test_hamali_role_defined():
    codes = {code for code, _ in ROLE_DEFINITIONS}
    assert "HAMALI" in codes
    assert ROLE_PERMISSIONS["HAMALI"] == ["hamali_work:read", "dashboard:read"]


def test_hamali_mobile_permissions_read_only():
    perms = resolve_mobile_permissions(_user("HAMALI"))
    assert HAMALI_VIEW in perms
    assert "PROCUREMENT_CREATE" not in perms
    assert "WORK_ORDER_UPDATE" not in perms
    assert "USER_CREATE" not in perms


def test_hamali_accessible_modules():
    modules = derive_accessible_modules(ROLE_MOBILE_PERMISSIONS["HAMALI"])
    assert "hamali" in modules
    assert "dashboard" in modules
    assert "procurement" not in modules
