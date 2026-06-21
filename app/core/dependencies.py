from collections.abc import Generator
from uuid import UUID

from fastapi import Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import TokenValidationError, get_token_subject
from app.modules.users.models import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


def get_current_user_context(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUserContext:
    if credentials is None:
        raise UnauthorizedError("Authentication required")

    try:
        user_id = get_token_subject(credentials.credentials, expected_type="access")
    except TokenValidationError as exc:
        raise UnauthorizedError(str(exc)) from exc

    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if user is None:
        raise UnauthorizedError("User not found or inactive")

    permissions = {perm.code for perm in user.role.permissions}
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
