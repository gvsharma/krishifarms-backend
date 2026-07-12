from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

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
    # str (not EmailStr): seeded *.local addresses are reserved domains EmailStr rejects
    email: str | None
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
    # str (not EmailStr) so seeded *.local demo/dev addresses are accepted.
    email: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8)
    full_name: str = Field(min_length=2, max_length=200)
    phone: str | None = None
    role_id: UUID
    village_id: UUID | None = None
    preferred_locale: str = "en"

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str | None) -> str | None:
        if value is None:
            return None
        email = value.strip().lower()
        if not email:
            return None
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            raise ValueError("Invalid email address")
        return email

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


class UserSelfUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=200)
    preferred_locale: str | None = Field(default=None, min_length=2, max_length=10)


class SessionResponse(ORMModel):
    id: UUID
    device_id: str | None = None
    created_at: datetime
    expires_at: datetime


class SessionListResponse(BaseModel):
    items: list[SessionResponse]


class UserListResponse(PaginatedResponse[UserResponse]):
    pass
