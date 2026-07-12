from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.schemas.common import ORMModel, PaginatedResponse

ASSET_CATEGORIES = ("tractor", "dcm", "baler", "air_machine", "bolero", "implement", "other")
ASSET_STATUSES = ("active", "maintenance", "retired")
FUEL_TYPES = ("tractor", "diesel", "implement")


class AssetResponse(ORMModel):
    id: UUID
    org_id: UUID
    asset_code: str
    name: str
    name_te: str | None = None
    asset_category: str
    vehicle_type_id: UUID | None = None
    vehicle_type_name: str | None = None
    vehicle_type_code: str | None = None
    registration_number: str | None = None
    fuel_type: str | None = None
    driver_name: str | None = None
    purchase_date: date | None = None
    purchase_cost: Decimal | None = None
    status: str
    is_rentable: bool
    hourly_rate: Decimal | None = None
    daily_rate: Decimal | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class AssetCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    asset_code: str | None = Field(default=None, min_length=1, max_length=50)
    name_te: str | None = None
    asset_category: str = Field(pattern="^(tractor|dcm|baler|air_machine|bolero|implement|other)$")
    vehicle_type_id: UUID | None = None
    registration_number: str | None = Field(default=None, max_length=50)
    fuel_type: str | None = Field(default=None, pattern="^(tractor|diesel|implement)$")
    driver_name: str | None = Field(default=None, max_length=200)
    purchase_date: date | None = None
    purchase_cost: Decimal | None = Field(default=None, ge=0)
    status: str = Field(default="active", pattern="^(active|maintenance|retired)$")
    is_rentable: bool = False
    hourly_rate: Decimal | None = Field(default=None, ge=0)
    daily_rate: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None


class AssetUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    asset_code: str | None = Field(default=None, min_length=1, max_length=50)
    name_te: str | None = None
    asset_category: str | None = Field(
        default=None, pattern="^(tractor|dcm|baler|air_machine|bolero|implement|other)$"
    )
    vehicle_type_id: UUID | None = None
    registration_number: str | None = Field(default=None, max_length=50)
    fuel_type: str | None = Field(default=None, pattern="^(tractor|diesel|implement)$")
    driver_name: str | None = Field(default=None, max_length=200)
    purchase_date: date | None = None
    purchase_cost: Decimal | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, pattern="^(active|maintenance|retired)$")
    is_rentable: bool | None = None
    hourly_rate: Decimal | None = Field(default=None, ge=0)
    daily_rate: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None


class AssetListResponse(PaginatedResponse[AssetResponse]):
    pass
