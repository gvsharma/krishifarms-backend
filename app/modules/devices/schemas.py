from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.schemas.common import ORMModel


class PushTokenRegisterRequest(BaseModel):
    fcm_token: str = Field(min_length=10, max_length=512)
    platform: str = Field(default="android", max_length=30)
    app_version: str | None = Field(default=None, max_length=50)
    device_id: str | None = Field(default=None, max_length=100)


class PushTokenDeleteRequest(BaseModel):
    fcm_token: str | None = Field(default=None, max_length=512)
    device_id: str | None = Field(default=None, max_length=100)


class PushTokenResponse(ORMModel):
    id: UUID
    device_id: str
    platform: str
    app_version: str | None
    last_seen_at: datetime
    created_at: datetime
