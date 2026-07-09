"""Firebase Admin SDK — verify ID tokens (phone OTP). Firebase is not the user database."""

from __future__ import annotations

import json
from dataclasses import dataclass

from app.core.config import settings
from app.core.exceptions import AppError, UnauthorizedError

_firebase_ready = False


@dataclass(frozen=True)
class FirebaseClaims:
    uid: str
    phone_number: str | None


def firebase_auth_enabled() -> bool:
    return settings.firebase_enabled


def _ensure_firebase_initialized() -> None:
    global _firebase_ready
    if _firebase_ready:
        return
    if not settings.firebase_enabled:
        raise AppError(
            "Firebase authentication is not configured on this server",
            status_code=503,
        )

    import firebase_admin
    from firebase_admin import credentials

    if firebase_admin._apps:
        _firebase_ready = True
        return

    if settings.firebase_service_account_json:
        try:
            cred_dict = json.loads(settings.firebase_service_account_json)
        except json.JSONDecodeError as exc:
            raise AppError(
                "Firebase service account JSON is malformed on this server",
                status_code=503,
            ) from exc
        cred = credentials.Certificate(cred_dict)
    elif settings.firebase_credentials_path:
        cred = credentials.Certificate(settings.firebase_credentials_path)
    else:
        raise AppError("Firebase credentials are missing", status_code=503)

    options = {}
    if settings.firebase_project_id:
        options["projectId"] = settings.firebase_project_id
    firebase_admin.initialize_app(cred, options or None)
    _firebase_ready = True


def verify_firebase_id_token(id_token: str) -> FirebaseClaims:
    """Verify Firebase ID token server-side; never trust client-supplied phone."""
    _ensure_firebase_initialized()

    from firebase_admin import auth as firebase_auth

    try:
        decoded = firebase_auth.verify_id_token(id_token, check_revoked=True)
    except firebase_auth.RevokedIdTokenError as exc:
        raise UnauthorizedError("Firebase token has been revoked") from exc
    except firebase_auth.ExpiredIdTokenError as exc:
        raise UnauthorizedError("Firebase token has expired") from exc
    except firebase_auth.InvalidIdTokenError as exc:
        raise UnauthorizedError("Invalid Firebase token") from exc
    except Exception as exc:
        raise UnauthorizedError("Firebase token verification failed") from exc

    uid = decoded.get("uid") or decoded.get("sub")
    if not uid:
        raise UnauthorizedError("Firebase token missing uid")

    phone = decoded.get("phone_number")
    return FirebaseClaims(uid=str(uid), phone_number=str(phone) if phone else None)
