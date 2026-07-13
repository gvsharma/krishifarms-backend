"""Unit tests for Play Store legal APIs and OWNER-only user delete RBAC."""

from app.core.config import settings
from app.modules.legal import service as legal_service
from app.shared.permissions import ROLE_PERMISSIONS, SYSTEM_PERMISSIONS


def test_only_owner_has_delete_permissions_including_users_delete():
    delete_perms = {code for code, _ in SYSTEM_PERMISSIONS if code.endswith(":delete")}
    assert "users:delete" in delete_perms

    for role, perms in ROLE_PERMISSIONS.items():
        role_deletes = {p for p in perms if p.endswith(":delete")}
        if role == "OWNER":
            assert "users:delete" in perms
            assert delete_perms <= set(perms)
            assert role_deletes == delete_perms
        else:
            assert "users:delete" not in perms
            assert not role_deletes, f"{role} must not have :delete permissions"


def test_legal_privacy_uses_configured_urls():
    privacy = legal_service.privacy_policy()
    assert privacy.url == settings.privacy_policy_url
    assert privacy.support_email == settings.support_email
    assert privacy.url.startswith("https://")


def test_legal_account_deletion_uses_configured_urls():
    info = legal_service.account_deletion_info()
    assert info.url == settings.account_deletion_url
    assert info.support_email == settings.support_email
    assert info.supports_in_app_deletion is True
    assert info.in_app_path == "DELETE /users/me"


def test_legal_links_bundle():
    bundle = legal_service.legal_links()
    assert bundle.privacy.url == settings.privacy_policy_url
    assert bundle.account_deletion.url == settings.account_deletion_url


def test_default_play_store_legal_urls():
    assert settings.privacy_policy_url == "https://krishifarms-privacy.vercel.app"
    assert settings.account_deletion_url == "https://krishifarms-privacy.vercel.app/delete-account"
    assert settings.support_email == "support@krishifarms.com"
