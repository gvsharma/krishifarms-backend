from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.modules.auth import service
from app.modules.auth.schemas import LoginRequest, RefreshRequest, TokenResponse
from app.shared.schemas.common import APIResponse, MessageResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=APIResponse[TokenResponse])
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    user = service.authenticate_user(
        db,
        email=payload.email,
        mobile=payload.mobile,
        password=payload.password,
    )
    tokens = service.issue_tokens(db, user)
    service.log_login(
        db,
        user,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
    )
    return APIResponse(data=TokenResponse(**tokens))


@router.post("/refresh", response_model=APIResponse[TokenResponse])
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    tokens = service.refresh_access_token(db, payload.refresh_token)
    return APIResponse(data=TokenResponse(**tokens))


@router.post("/logout", response_model=APIResponse[MessageResponse])
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    service.revoke_refresh_token(db, payload.refresh_token)
    return APIResponse(data=MessageResponse(message="Logged out successfully"))
