from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FarmCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    name_te: str | None = None
    acres: Decimal = Field(gt=0)
    location: str | None = None
    village_id: UUID | None = None
    owner_farmer_id: UUID | None = None
    lease_start_date: date | None = None
    lease_end_date: date | None = None
    lease_amount: Decimal | None = Field(default=None, ge=0)
    lease_notes: str | None = None
    farm_code: str | None = Field(default=None, max_length=50)
    geo_lat: Decimal | None = None
    geo_lng: Decimal | None = None


class FarmUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    name_te: str | None = None
    acres: Decimal | None = Field(default=None, gt=0)
    location: str | None = None
    village_id: UUID | None = None
    owner_farmer_id: UUID | None = None
    lease_start_date: date | None = None
    lease_end_date: date | None = None
    lease_amount: Decimal | None = Field(default=None, ge=0)
    lease_notes: str | None = None
    status: str | None = Field(default=None, pattern="^(active|inactive)$")
    geo_lat: Decimal | None = None
    geo_lng: Decimal | None = None


class FarmResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    org_id: UUID
    farm_code: str
    name: str
    name_te: str | None = None
    acres: Decimal
    location: str | None = None
    village_id: UUID | None = None
    owner_farmer_id: UUID | None = None
    lease_start_date: date | None = None
    lease_end_date: date | None = None
    lease_amount: Decimal | None = None
    lease_notes: str | None = None
    status: str
    geo_lat: Decimal | None = None
    geo_lng: Decimal | None = None


class FarmListResponse(BaseModel):
    items: list[FarmResponse]
    total: int
    page: int
    page_size: int


class FarmActivityCreateRequest(BaseModel):
    activity_date: date
    activity_type_id: UUID | None = None
    description: str | None = None
    description_te: str | None = None
    performed_by_worker_id: UUID | None = None


class FarmActivityUpdateRequest(BaseModel):
    activity_date: date | None = None
    activity_type_id: UUID | None = None
    description: str | None = None
    description_te: str | None = None
    performed_by_worker_id: UUID | None = None


class FarmActivityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farm_id: UUID
    activity_type_id: UUID | None = None
    activity_date: date
    description: str | None = None
    description_te: str | None = None
    performed_by_worker_id: UUID | None = None


class FarmActivityListResponse(BaseModel):
    items: list[FarmActivityResponse]
    total: int
