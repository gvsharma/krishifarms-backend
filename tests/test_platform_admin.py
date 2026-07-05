"""Tests for platform admin RBAC and permission catalog."""

from types import SimpleNamespace

from app.modules.auth.permission_catalog import (
    COMMENT_CREATE,
    COMMENT_VIEW,
    FARMER_DELETE,
    ROLE_MOBILE_PERMISSIONS,
    SETTINGS_MANAGE,
    USER_MANAGE,
)
from app.modules.auth.rbac import resolve_mobile_permissions
from app.shared.permissions import ROLE_PERMISSIONS


def _user(role_code: str) -> SimpleNamespace:
    role = SimpleNamespace(code=role_code, permissions=[])
    return SimpleNamespace(id="user-1", role=role)


def test_manager_backend_cannot_create_or_delete_users():
    perms = set(ROLE_PERMISSIONS["MANAGER"])
    assert "users:create" not in perms
    assert "users:delete" not in perms
    assert "users:read" in perms


def test_manager_backend_has_no_delete_permissions():
    perms = set(ROLE_PERMISSIONS["MANAGER"])
    assert not any(p.endswith(":delete") for p in perms)


def test_agent_mobile_comment_only():
    perms = resolve_mobile_permissions(_user("AGENT"))
    assert COMMENT_VIEW in perms
    assert COMMENT_CREATE in perms
    assert SETTINGS_MANAGE not in perms
    assert USER_MANAGE not in perms


def test_driver_mobile_comment_and_vehicle_view():
    perms = resolve_mobile_permissions(_user("DRIVER"))
    assert COMMENT_CREATE in perms
    assert "VEHICLE_VIEW" in perms
    assert FARMER_DELETE not in perms


def test_owner_has_all_platform_mobile_permissions():
    perms = resolve_mobile_permissions(_user("OWNER"))
    assert COMMENT_CREATE in perms
    assert "TAG_MANAGE" in perms


def test_agent_and_driver_roles_in_catalog():
    assert "AGENT" in ROLE_MOBILE_PERMISSIONS
    assert "DRIVER" in ROLE_MOBILE_PERMISSIONS
