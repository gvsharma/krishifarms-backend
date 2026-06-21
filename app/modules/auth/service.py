from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_token,
    verify_password,
    verify_token_hash,
)
from app.core.security import TokenValidationError, get_token_subject
from app.core.exceptions import NotFoundError, UnauthorizedError
from app.modules.auth.rbac import build_auth_user, build_rbac_payload
from app.modules.users.models import RefreshToken, Role, User
from app.shared.services.audit import write_audit_log


def authenticate_user(
    db: Session,
    *,
    email: str | None = None,
    mobile: str | None = None,
    password: str,
) -> User:
    query = (
        db.query(User)
        .options(joinedload(User.role).joinedload(Role.permissions))
        .filter(User.deleted_at.is_(None), User.is_active.is_(True))
    )
    if email:
        query = query.filter(User.email == email)
    elif mobile:
        query = query.filter(User.phone == mobile)
    else:
        raise UnauthorizedError("Email or mobile is required")

    user = query.first()
    if user is None or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid credentials")
    return user


def issue_tokens(db: Session, user: User) -> dict:
    access_token = create_access_token(
        str(user.id),
        extra_claims={"org_id": str(user.org_id), "role": user.role.code},
    )
    refresh_token = create_refresh_token(str(user.id))
    refresh_entry = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(refresh_token),
        expires_at=datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(refresh_entry)
    user.last_login_at = datetime.now(UTC)
    db.commit()

    rbac = build_rbac_payload(user)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": build_auth_user(user),
        **rbac,
    }


def refresh_access_token(db: Session, refresh_token: str) -> dict:
    try:
        user_id = get_token_subject(refresh_token, expected_type="refresh")
    except TokenValidationError as exc:
        raise UnauthorizedError("Invalid refresh token") from exc

    active_tokens = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.now(UTC),
        )
        .all()
    )
    matched = next(
        (token for token in active_tokens if verify_token_hash(refresh_token, token.token_hash)),
        None,
    )
    if matched is None:
        raise UnauthorizedError("Refresh token not found or expired")

    user = (
        db.query(User)
        .options(joinedload(User.role).joinedload(Role.permissions))
        .filter(User.id == user_id, User.is_active.is_(True))
        .first()
    )
    if user is None:
        raise UnauthorizedError("User not found")

    matched.revoked_at = datetime.now(UTC)
    return issue_tokens(db, user)


def revoke_refresh_token(db: Session, refresh_token: str) -> None:
    try:
        user_id = get_token_subject(refresh_token, expected_type="refresh")
    except TokenValidationError as exc:
        raise UnauthorizedError("Invalid refresh token") from exc

    tokens = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked_at.is_(None),
    )
    for token in tokens:
        if verify_token_hash(refresh_token, token.token_hash):
            token.revoked_at = datetime.now(UTC)
            db.commit()
            return
    raise NotFoundError("Refresh token not found")


def log_login(db: Session, user: User, ip_address: str | None, user_agent: str | None) -> None:
    write_audit_log(
        db,
        org_id=user.org_id,
        actor_user_id=user.id,
        action="LOGIN",
        entity_type="user",
        entity_id=user.id,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.commit()
