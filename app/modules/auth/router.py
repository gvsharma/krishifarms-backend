from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

from app.core.client_context import ClientContext, get_client_context
from app.core.dependencies import CurrentUserContext, get_current_user_context, get_db
from app.core.exceptions import UnauthorizedError
from app.modules.auth import service
from app.modules.auth.rbac import build_auth_user, build_rbac_payload
from app.modules.auth.rate_limit import check_firebase_login_rate_limit
from app.modules.auth.schemas import AuthMeResponse, AuthUserResponse, LoginRequest, RefreshRequest, TokenResponse
from app.modules.users import service as users_service
from app.shared.schemas.common import APIResponse, MessageResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


def _client_ip(request: Request) -> str | None:
    return request.client.host if request.client else None


def get_firebase_id_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError("Firebase ID token required in Authorization header")
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise UnauthorizedError("Firebase ID token required in Authorization header")
    return token


@router.post("/login", response_model=APIResponse[TokenResponse])
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
    client: ClientContext = Depends(get_client_context),
):
    user = service.authenticate_user(
        db,
        email=payload.email,
        mobile=payload.mobile,
        password=payload.password,
    )
    tokens = service.issue_tokens(db, user, device_id=client.device_id)
    service.log_login(
        db,
        user,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        auth_method="password",
        device_id=client.device_id,
        client_type=client.client_type,
        request_id=client.request_id,
    )
    return APIResponse(data=TokenResponse(**tokens))


@router.post("/firebase-login", response_model=APIResponse[TokenResponse])
def firebase_login(
    request: Request,
    db: Session = Depends(get_db),
    firebase_id_token: str = Depends(get_firebase_id_token),
    client: ClientContext = Depends(get_client_context),
):
    client_key = _client_ip(request) or "unknown"
    check_firebase_login_rate_limit(client_key)
    tokens = service.firebase_login(
        db,
        firebase_id_token=firebase_id_token,
        ip_address=_client_ip(request),
        user_agent=request.headers.get("User-Agent"),
        device_id=client.device_id,
        client_type=client.client_type,
        request_id=client.request_id,
    )
    return APIResponse(data=TokenResponse(**tokens))


@router.post("/refresh", response_model=APIResponse[TokenResponse])
def refresh(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
    client: ClientContext = Depends(get_client_context),
):
    tokens = service.refresh_access_token(db, payload.refresh_token, device_id=client.device_id)
    return APIResponse(data=TokenResponse(**tokens))


@router.post("/logout", response_model=APIResponse[MessageResponse])
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    service.revoke_refresh_token(db, payload.refresh_token)
    return APIResponse(data=MessageResponse(message="Logged out successfully"))


@router.get("/me", response_model=APIResponse[AuthMeResponse])
def auth_me(
    ctx: CurrentUserContext = Depends(get_current_user_context),
    db: Session = Depends(get_db),
):
    user = users_service.get_current_profile(db, ctx.user.id)
    rbac = build_rbac_payload(user)
    profile = build_auth_user(user)
    return APIResponse(
        data=AuthMeResponse(
            user=AuthUserResponse(**profile),
            roles=rbac["roles"],
            permissions=rbac["permissions"],
            accessible_modules=rbac["accessibleModules"],
        )
    )
