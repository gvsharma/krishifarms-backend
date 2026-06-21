from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.schemas.common import ORMModel, PaginatedResponse


class VillageResponse(ORMModel):
    id: UUID
    org_id: UUID
    name: str
    mandal: str | None = None
    district: str | None = None
    state: str | None = None
    pincode: str | None = None
    created_at: datetime
    updated_at: datetime


class VillageCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    mandal: str | None = None
    district: str | None = None
    state: str | None = None
    pincode: str | None = None


class VillageUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    mandal: str | None = None
    district: str | None = None
    state: str | None = None
    pincode: str | None = None


class VillageListResponse(PaginatedResponse[VillageResponse]):
    pass


class CropTypeResponse(ORMModel):
    id: UUID
    org_id: UUID
    name: str
    code: str
    default_moisture_pct: float | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CropTypeCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    code: str = Field(min_length=2, max_length=50)
    default_moisture_pct: float | None = None
    is_active: bool = True


class CropTypeUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    code: str | None = Field(default=None, min_length=2, max_length=50)
    default_moisture_pct: float | None = None
    is_active: bool | None = None


class CropTypeListResponse(PaginatedResponse[CropTypeResponse]):
    pass
