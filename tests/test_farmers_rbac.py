"""Tests for farmers RBAC and permission wiring."""

from app.modules.auth.permission_catalog import FARMER_DELETE, FARMER_VIEW
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


def test_agent_has_no_farmer_permissions():
    perms = set(ROLE_PERMISSIONS["AGENT"])
    assert "farmers:read" not in perms
    assert FARMER_VIEW not in perms
    assert FARMER_DELETE not in perms
