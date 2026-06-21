from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUserContext, get_current_user_context, get_db, require_permission
from app.modules.users import service
from app.modules.users.schemas import RoleResponse, UserCreateRequest, UserListResponse, UserResponse, UserUpdateRequest
from app.shared.schemas.common import APIResponse

router = APIRouter(tags=["Users"])


@router.get("/users/me", response_model=APIResponse[UserResponse])
def get_me(ctx: CurrentUserContext = Depends(get_current_user_context), db: Session = Depends(get_db)):
    user = service.get_current_profile(db, ctx.user.id)
    return APIResponse(data=UserResponse.model_validate(user))


@router.get("/users", response_model=APIResponse[UserListResponse])
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ctx: CurrentUserContext = Depends(require_permission("users:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_users(db, ctx.user.org_id, page, page_size)
    return APIResponse(
        data=UserListResponse(
            items=[UserResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.post("/users", response_model=APIResponse[UserResponse], status_code=201)
def create_user(
    payload: UserCreateRequest,
    ctx: CurrentUserContext = Depends(require_permission("users:create")),
    db: Session = Depends(get_db),
):
    user = service.create_user(db, ctx.user.org_id, payload, ctx.user.id)
    return APIResponse(data=UserResponse.model_validate(user))


@router.patch("/users/{user_id}", response_model=APIResponse[UserResponse])
def update_user(
    user_id: UUID,
    payload: UserUpdateRequest,
    ctx: CurrentUserContext = Depends(require_permission("users:update")),
    db: Session = Depends(get_db),
):
    user = service.update_user(db, ctx.user.org_id, user_id, payload, ctx.user.id)
    return APIResponse(data=UserResponse.model_validate(user))


@router.get("/roles", response_model=APIResponse[list[RoleResponse]])
def list_roles(
    ctx: CurrentUserContext = Depends(require_permission("roles:read")),
    db: Session = Depends(get_db),
):
    roles = service.list_roles(db, ctx.user.org_id)
    return APIResponse(data=[RoleResponse.model_validate(role) for role in roles])
