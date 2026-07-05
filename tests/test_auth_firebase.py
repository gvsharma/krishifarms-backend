"""Tests for Firebase phone login and phone normalization."""

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.modules.auth.firebase import FirebaseClaims
from app.modules.auth.phone import normalize_phone_for_lookup
from app.modules.auth.rate_limit import check_firebase_login_rate_limit
from app.modules.auth.service import firebase_login


def test_normalize_phone_strips_india_country_code():
    assert normalize_phone_for_lookup("+919876543210") == "9876543210"
    assert normalize_phone_for_lookup("9876543210") == "9876543210"


def test_normalize_phone_digits_only():
    assert normalize_phone_for_lookup("+91 98765 43210") == "9876543210"


@patch("app.modules.auth.service._find_active_user_by_phone")
@patch("app.modules.auth.firebase.verify_firebase_id_token")
def test_firebase_login_rejects_unregistered_phone(mock_verify, mock_find):
    mock_verify.return_value = FirebaseClaims(uid="fb-1", phone_number="+919876543210")
    mock_find.return_value = None
    db = MagicMock()

    with pytest.raises(ForbiddenError, match="User not registered"):
        firebase_login(db, firebase_id_token="token")


@patch("app.modules.auth.service._find_active_user_by_phone")
@patch("app.modules.auth.firebase.verify_firebase_id_token")
@patch("app.modules.auth.service.issue_tokens")
@patch("app.modules.auth.service.log_login")
def test_firebase_login_issues_tokens_for_registered_user(
    mock_log, mock_issue, mock_verify, mock_find
):
    mock_verify.return_value = FirebaseClaims(uid="fb-1", phone_number="+919876543210")
    user = SimpleNamespace(
        id="u1",
        phone="9876543210",
        firebase_uid=None,
        org_id="org1",
        role=SimpleNamespace(code="WORKER"),
    )
    mock_find.return_value = user
    db = MagicMock()
    mock_issue.return_value = {"access_token": "a", "refresh_token": "r", "token_type": "bearer"}

    result = firebase_login(db, firebase_id_token="token", ip_address="1.2.3.4")

    assert result["access_token"] == "a"
    assert user.firebase_uid == "fb-1"
    mock_log.assert_called_once()


@patch("app.modules.auth.firebase.verify_firebase_id_token")
def test_firebase_login_requires_verified_phone(mock_verify):
    mock_verify.return_value = FirebaseClaims(uid="fb-1", phone_number=None)
    db = MagicMock()

    with pytest.raises(UnauthorizedError, match="verified phone"):
        firebase_login(db, firebase_id_token="token")


def test_firebase_login_rate_limit_blocks_after_threshold():
    from app.core.cache.memory import InMemoryCacheProvider

    with patch("app.modules.auth.rate_limit.get_cache_provider", return_value=InMemoryCacheProvider()):
        with patch("app.modules.auth.rate_limit.settings.firebase_login_rate_limit_per_minute", 2):
            check_firebase_login_rate_limit("1.2.3.4")
            check_firebase_login_rate_limit("1.2.3.4")
            with pytest.raises(Exception) as exc:
                check_firebase_login_rate_limit("1.2.3.4")
            assert exc.value.status_code == 429
