from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class LoginRequest(BaseModel):
    email: EmailStr | None = None
    mobile: str | None = Field(default=None, min_length=10, max_length=15)
    password: str = Field(min_length=8)

    @model_validator(mode="after")
    def require_email_or_mobile(self) -> "LoginRequest":
        if not self.email and not self.mobile:
            raise ValueError("Either email or mobile is required")
        return self

    @field_validator("mobile")
    @classmethod
    def normalize_mobile(cls, value: str | None) -> str | None:
        if value is None:
            return None
        digits = "".join(ch for ch in value if ch.isdigit())
        return digits or value


class RefreshRequest(BaseModel):
    refresh_token: str


class AuthUserResponse(BaseModel):
    id: str
    name: str
    mobile: str
    email: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: AuthUserResponse | None = None
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    accessible_modules: list[str] = Field(default_factory=list, serialization_alias="accessibleModules")

    model_config = {"populate_by_name": True}


class MessageResponse(BaseModel):
    message: str
