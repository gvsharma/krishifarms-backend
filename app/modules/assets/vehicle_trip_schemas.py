from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VehicleTripCreateRequest(BaseModel):
    asset_id: UUID
    driver_worker_id: UUID | None = None
    source: str = Field(min_length=1, max_length=255)
    source_te: str | None = None
    destination: str = Field(min_length=1, max_length=255)
    destination_te: str | None = None
    trip_date: date
    distance_km: Decimal | None = Field(default=None, ge=0)
    fuel_liters: Decimal | None = Field(default=None, ge=0)
    fuel_cost: Decimal = Field(default=Decimal("0"), ge=0)
    loading_charges: Decimal = Field(default=Decimal("0"), ge=0)
    unloading_charges: Decimal = Field(default=Decimal("0"), ge=0)
    waiting_charges: Decimal = Field(default=Decimal("0"), ge=0)
    other_charges: Decimal = Field(default=Decimal("0"), ge=0)
    notes: str | None = None


class VehicleTripUpdateRequest(BaseModel):
    source: str | None = Field(default=None, min_length=1, max_length=255)
    source_te: str | None = None
    destination: str | None = Field(default=None, min_length=1, max_length=255)
    destination_te: str | None = None
    distance_km: Decimal | None = Field(default=None, ge=0)
    fuel_liters: Decimal | None = Field(default=None, ge=0)
    fuel_cost: Decimal | None = Field(default=None, ge=0)
    loading_charges: Decimal | None = Field(default=None, ge=0)
    unloading_charges: Decimal | None = Field(default=None, ge=0)
    waiting_charges: Decimal | None = Field(default=None, ge=0)
    other_charges: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None
    status: str | None = Field(default=None, pattern="^(completed|cancelled)$")


class VehicleTripResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    trip_number: str
    asset_id: UUID
    driver_worker_id: UUID | None = None
    source: str
    source_te: str | None = None
    destination: str
    destination_te: str | None = None
    trip_date: date
    distance_km: Decimal | None = None
    fuel_liters: Decimal | None = None
    fuel_cost: Decimal
    loading_charges: Decimal
    unloading_charges: Decimal
    waiting_charges: Decimal
    other_charges: Decimal
    total_cost: Decimal
    status: str
    notes: str | None = None
    diesel_expense_id: UUID | None = None


class VehicleTripListResponse(BaseModel):
    items: list[VehicleTripResponse]
    total: int
    page: int
    page_size: int
