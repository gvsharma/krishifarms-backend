from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.shared.schemas.common import ORMModel, PaginatedResponse


class RoleResponse(ORMModel):
    id: UUID
    code: str
    name: str


class PermissionResponse(ORMModel):
    id: UUID
    code: str
    description: str | None = None


class UserResponse(ORMModel):
    id: UUID
    org_id: UUID
    email: EmailStr | None
    phone: str | None
    full_name: str
    preferred_locale: str
    is_active: bool
    role: RoleResponse
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=200)
    phone: str | None = None
    role_id: UUID
    preferred_locale: str = "en"


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=200)
    phone: str | None = None
    role_id: UUID | None = None
    preferred_locale: str | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8)


class UserListResponse(PaginatedResponse[UserResponse]):
    pass
