from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.core.client_context import ClientContext
from app.core.exceptions import AppError, NotFoundError
from app.modules.devices.fcm import is_invalid_token_error, send_fcm_notification
from app.modules.devices.models import UserDeviceToken
from app.modules.devices.schemas import PushTokenDeleteRequest, PushTokenRegisterRequest
from app.modules.users.models import Role, User


def upsert_push_token(
    db: Session,
    *,
    org_id: UUID,
    user_id: UUID,
    payload: PushTokenRegisterRequest,
    client: ClientContext,
) -> UserDeviceToken:
    device_id = (payload.device_id or client.device_id or "").strip()[:100]
    if not device_id:
        raise AppError("device_id is required (body or X-Device-Id header)", status_code=400)

    fcm_token = payload.fcm_token.strip()
    platform = (payload.platform or "android").strip().lower()[:30] or "android"
    now = datetime.now(UTC)

    existing_by_device = (
        db.query(UserDeviceToken)
        .filter(
            UserDeviceToken.org_id == org_id,
            UserDeviceToken.user_id == user_id,
            UserDeviceToken.device_id == device_id,
            UserDeviceToken.revoked_at.is_(None),
        )
        .first()
    )
    if existing_by_device:
        existing_by_device.fcm_token = fcm_token
        existing_by_device.platform = platform
        existing_by_device.app_version = payload.app_version
        existing_by_device.last_seen_at = now
        existing_by_device.updated_at = now
        db.commit()
        db.refresh(existing_by_device)
        return existing_by_device

    conflict = (
        db.query(UserDeviceToken)
        .filter(UserDeviceToken.org_id == org_id, UserDeviceToken.fcm_token == fcm_token)
        .first()
    )
    if conflict:
        conflict.user_id = user_id
        conflict.device_id = device_id
        conflict.platform = platform
        conflict.app_version = payload.app_version
        conflict.last_seen_at = now
        conflict.revoked_at = None
        conflict.updated_at = now
        db.commit()
        db.refresh(conflict)
        return conflict

    row = UserDeviceToken(
        org_id=org_id,
        user_id=user_id,
        device_id=device_id,
        fcm_token=fcm_token,
        platform=platform,
        app_version=payload.app_version,
        last_seen_at=now,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def revoke_push_token(
    db: Session,
    *,
    org_id: UUID,
    user_id: UUID,
    payload: PushTokenDeleteRequest,
    client: ClientContext,
) -> None:
    q = db.query(UserDeviceToken).filter(
        UserDeviceToken.org_id == org_id,
        UserDeviceToken.user_id == user_id,
        UserDeviceToken.revoked_at.is_(None),
    )
    if payload.fcm_token:
        q = q.filter(UserDeviceToken.fcm_token == payload.fcm_token.strip())
    else:
        device_id = (payload.device_id or client.device_id or "").strip()
        if not device_id:
            raise AppError("fcm_token or device_id is required", status_code=400)
        q = q.filter(UserDeviceToken.device_id == device_id)

    rows = q.all()
    if not rows:
        raise NotFoundError("Push token not found")
    now = datetime.now(UTC)
    for row in rows:
        row.revoked_at = now
    db.commit()


def _users_by_role_codes(
    db: Session,
    org_id: UUID,
    role_codes: set[str],
    *,
    village_id: UUID | None = None,
) -> list[User]:
    q = (
        db.query(User)
        .join(Role, User.role_id == Role.id)
        .filter(
            User.org_id == org_id,
            User.deleted_at.is_(None),
            User.is_active.is_(True),
            Role.code.in_(role_codes),
        )
        .options(joinedload(User.role))
    )
    users = q.all()
    if village_id is None:
        return users
    matched = [u for u in users if u.village_id is None or u.village_id == village_id]
    return matched or [u for u in users if u.role and u.role.code in {"OWNER", "MANAGER"}]


def notify_users(
    db: Session,
    *,
    org_id: UUID,
    user_ids: set[UUID],
    title_en: str,
    body_en: str,
    title_te: str,
    body_te: str,
    data: dict[str, str],
    skip_user_id: UUID | None = None,
) -> None:
    targets = {uid for uid in user_ids if uid and uid != skip_user_id}
    if not targets:
        return

    users = (
        db.query(User)
        .filter(User.id.in_(targets), User.org_id == org_id, User.deleted_at.is_(None), User.is_active.is_(True))
        .all()
    )
    locale_by_user = {u.id: (u.preferred_locale or "en").lower() for u in users}

    tokens = (
        db.query(UserDeviceToken)
        .filter(
            UserDeviceToken.org_id == org_id,
            UserDeviceToken.user_id.in_(targets),
            UserDeviceToken.revoked_at.is_(None),
        )
        .all()
    )
    now = datetime.now(UTC)
    for row in tokens:
        locale = locale_by_user.get(row.user_id, "en")
        title = title_te if locale.startswith("te") else title_en
        body = body_te if locale.startswith("te") else body_en
        try:
            send_fcm_notification(token=row.fcm_token, title=title, body=body, data=data)
            row.last_seen_at = now
        except Exception as exc:
            if is_invalid_token_error(exc):
                row.revoked_at = now
            # other errors already logged in send_fcm_notification
    db.commit()


def notify_procurement_status(
    db: Session,
    *,
    org_id: UUID,
    procurement_id: UUID,
    procurement_number: str,
    status: str,
    village_id: UUID | None,
    created_by: UUID | None,
    actor_user_id: UUID,
) -> None:
    recipients = {u.id for u in _users_by_role_codes(db, org_id, {"OWNER", "MANAGER", "SUPERVISOR"}, village_id=village_id)}
    if created_by:
        recipients.add(created_by)
    notify_users(
        db,
        org_id=org_id,
        user_ids=recipients,
        title_en="Procurement updated",
        body_en=f"{procurement_number} is now {status}",
        title_te="కొనుగోలు నవీకరించబడింది",
        body_te=f"{procurement_number} ఇప్పుడు {status}",
        data={"type": "procurement", "id": str(procurement_id), "status": status},
        skip_user_id=actor_user_id,
    )


def notify_farmer_comment(
    db: Session,
    *,
    org_id: UUID,
    farmer_id: UUID,
    actor_user_id: UUID,
    preview: str,
) -> None:
    recipients = {u.id for u in _users_by_role_codes(db, org_id, {"OWNER", "MANAGER", "SUPERVISOR"})}
    from app.modules.platform.models import EntityComment

    commenters = (
        db.query(EntityComment.author_user_id)
        .filter(
            EntityComment.org_id == org_id,
            EntityComment.entity_type == "farmer",
            EntityComment.entity_id == farmer_id,
            EntityComment.deleted_at.is_(None),
        )
        .distinct()
        .all()
    )
    recipients |= {c[0] for c in commenters}
    snippet = (preview or "")[:80]
    notify_users(
        db,
        org_id=org_id,
        user_ids=recipients,
        title_en="New farmer comment",
        body_en=snippet or "A new comment was added",
        title_te="రైతు వ్యాఖ్య",
        body_te=snippet or "కొత్త వ్యాఖ్య జోడించబడింది",
        data={"type": "farmer_comment", "farmer_id": str(farmer_id)},
        skip_user_id=actor_user_id,
    )


def notify_document_uploaded(
    db: Session,
    *,
    org_id: UUID,
    document_id: UUID,
    file_name: str,
    actor_user_id: UUID,
) -> None:
    recipients = {u.id for u in _users_by_role_codes(db, org_id, {"OWNER", "MANAGER"})}
    notify_users(
        db,
        org_id=org_id,
        user_ids=recipients,
        title_en="Document uploaded",
        body_en=file_name,
        title_te="పత్రం అప్‌లోడ్ అయింది",
        body_te=file_name,
        data={"type": "document", "id": str(document_id)},
        skip_user_id=actor_user_id,
    )
