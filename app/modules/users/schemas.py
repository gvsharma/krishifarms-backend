from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator

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
    village_id: UUID | None = None
    preferred_locale: str
    is_active: bool
    role: RoleResponse
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class UserCreateRequest(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8)
    full_name: str = Field(min_length=2, max_length=200)
    phone: str | None = None
    role_id: UUID
    village_id: UUID | None = None
    preferred_locale: str = "en"

    @model_validator(mode="after")
    def validate_credentials(self) -> "UserCreateRequest":
        if not self.email and not self.phone:
            raise ValueError("Either email or phone is required")
        if self.email and not self.password:
            raise ValueError("Password is required when email is provided")
        return self


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=200)
    phone: str | None = None
    village_id: UUID | None = None
    role_id: UUID | None = None
    preferred_locale: str | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8)


class UserListResponse(PaginatedResponse[UserResponse]):
    pass
