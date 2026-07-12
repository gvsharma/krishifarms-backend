"""FCM send via Firebase Admin (reuses phone-auth credentials)."""

from __future__ import annotations

import logging

from app.modules.auth.firebase import _ensure_firebase_initialized, firebase_auth_enabled

logger = logging.getLogger(__name__)


def send_fcm_notification(
    *,
    token: str,
    title: str,
    body: str,
    data: dict[str, str] | None = None,
) -> str | None:
    """Send one FCM message. Returns message id, or None if skipped/failed."""
    if not firebase_auth_enabled():
        logger.warning("FCM skipped: Firebase not configured")
        return None

    _ensure_firebase_initialized()
    from firebase_admin import messaging

    message = messaging.Message(
        token=token,
        notification=messaging.Notification(title=title, body=body),
        data={k: str(v) for k, v in (data or {}).items()},
        android=messaging.AndroidConfig(priority="high"),
    )
    try:
        return messaging.send(message)
    except messaging.UnregisteredError:
        raise
    except Exception:
        logger.exception("FCM send failed for token suffix …%s", token[-8:] if len(token) >= 8 else token)
        return None


def is_invalid_token_error(exc: BaseException) -> bool:
    try:
        from firebase_admin import messaging

        return isinstance(exc, (messaging.UnregisteredError, messaging.SenderIdMismatchError))
    except Exception:
        return False
