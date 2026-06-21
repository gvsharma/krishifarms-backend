import json
from collections.abc import Generator
from uuid import UUID

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session, joinedload

from app.core.cache import get_cache_provider
from app.core.cache.base import CacheProvider
from app.core.cache.keys import user_permissions_key
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import TokenValidationError, get_token_subject
from app.modules.users.models import Role, User

bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_cache() -> CacheProvider:
    return get_cache_provider()


def get_request_id(
    x_request_id: str | None = Header(default=None, alias="X-Request-ID"),
) -> str | None:
    return x_request_id


class CurrentUserContext:
    def __init__(self, user: User, permissions: set[str]):
        self.user = user
        self.permissions = permissions

    def require_permission(self, permission: str) -> None:
        if permission not in self.permissions:
            raise ForbiddenError(f"Missing permission: {permission}")


def _load_user_permissions(
    user: User,
    cache: CacheProvider,
) -> set[str]:
    cache_key = user_permissions_key(user.id)
    cached_permissions = cache.get(cache_key)
    if cached_permissions is not None:
        return set(json.loads(cached_permissions))

    permissions = {perm.code for perm in user.role.permissions}
    cache.set(
        cache_key,
        json.dumps(sorted(permissions)),
        ttl_seconds=settings.cache_ttl_seconds,
    )
    return permissions


def get_current_user_context(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    cache: CacheProvider = Depends(get_cache),
) -> CurrentUserContext:
    if credentials is None:
        raise UnauthorizedError("Authentication required")

    try:
        user_id = get_token_subject(credentials.credentials, expected_type="access")
    except TokenValidationError as exc:
        raise UnauthorizedError(str(exc)) from exc

    user = (
        db.query(User)
        .options(joinedload(User.role).joinedload(Role.permissions))
        .filter(User.id == user_id, User.is_active.is_(True))
        .first()
    )
    if user is None:
        raise UnauthorizedError("User not found or inactive")

    permissions = _load_user_permissions(user, cache)
    return CurrentUserContext(user=user, permissions=permissions)


def require_permission(permission: str):
    def dependency(
        ctx: CurrentUserContext = Depends(get_current_user_context),
    ) -> CurrentUserContext:
        ctx.require_permission(permission)
        return ctx

    return dependency


def get_optional_user_id(request: Request) -> UUID | None:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.removeprefix("Bearer ").strip()
    try:
        return get_token_subject(token, expected_type="access")
    except TokenValidationError:
        return None
