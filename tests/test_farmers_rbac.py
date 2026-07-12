"""Tests for farmers RBAC and permission wiring."""

from app.modules.auth.permission_catalog import FARMER_DELETE
from app.shared.permissions import ROLE_PERMISSIONS


def test_owner_has_farmer_delete():
    perms = set(ROLE_PERMISSIONS["OWNER"])
    assert "farmers:delete" in perms
    assert "farmers:read" in perms


def test_manager_has_farmer_crud_except_delete():
    perms = set(ROLE_PERMISSIONS["MANAGER"])
    assert "farmers:read" in perms
    assert "farmers:create" in perms
    assert "farmers:update" in perms
    assert "farmers:delete" not in perms


def test_supervisor_can_create_farmers_not_delete():
    perms = set(ROLE_PERMISSIONS["SUPERVISOR"])
    assert "farmers:read" in perms
    assert "farmers:create" in perms
    assert "farmers:update" in perms
    assert "farmers:delete" not in perms


def test_agent_has_farmer_read_only():
    perms = set(ROLE_PERMISSIONS["AGENT"])
    assert "farmers:read" in perms
    assert "farmers:create" not in perms
    assert "farmers:delete" not in perms
    assert FARMER_DELETE not in perms


def test_farmer_role_is_read_only():
    perms = set(ROLE_PERMISSIONS["FARMER"])
    assert "farmers:read" in perms
    assert "procurements:read" in perms
    assert "districts:read" in perms
    assert not any(p.endswith(":create") or p.endswith(":update") or p.endswith(":delete") for p in perms)
