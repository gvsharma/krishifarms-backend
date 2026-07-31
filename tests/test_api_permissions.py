"""Tests for API permission loading (DB + role catalog merge)."""

from types import SimpleNamespace
from unittest.mock import MagicMock

from app.core.cache.null import NullCacheProvider
from app.core.dependencies import _load_user_permissions


def _user(role_code: str, db_permissions: list[str]) -> SimpleNamespace:
    perms = [SimpleNamespace(code=c) for c in db_permissions]
    role = SimpleNamespace(code=role_code, permissions=perms)
    return SimpleNamespace(id="user-1", role=role)


def test_load_user_permissions_merges_role_catalog_when_db_sparse():
    user = _user("MANAGER", ["procurements:read"])
    perms = _load_user_permissions(user, NullCacheProvider())
    assert "procurements:read" in perms
    assert "documents:create" in perms
    assert "documents:read" in perms


def test_load_user_permissions_uses_cache_and_still_merges_catalog():
    user = _user("SUPERVISOR", ["procurements:read"])
    cache = MagicMock()
    cache.get.return_value = '["procurements:read"]'
    perms = _load_user_permissions(user, cache)
    assert "procurements:read" in perms
    assert "documents:create" in perms
    cache.set.assert_not_called()
