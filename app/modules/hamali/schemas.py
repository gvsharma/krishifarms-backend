from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.schemas.common import ORMModel, PaginatedResponse


class WorkerResponse(ORMModel):
    id: UUID
    worker_code: str
    full_name: str
    phone: str | None = None
    status: str


class WorkerCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    phone: str | None = Field(default=None, max_length=20)
    village_id: UUID | None = None


class HamaliWorkEntryResponse(ORMModel):
    id: UUID
    worker_id: UUID
    farmer_id: UUID
    work_date: date
    bag_count: int
    tip_amount: Decimal
    procurement_id: UUID | None = None
    notes: str | None = None
    worker_name: str | None = None
    farmer_name: str | None = None


class HamaliWorkEntryCreateRequest(BaseModel):
    worker_id: UUID
    farmer_id: UUID
    work_date: date
    bag_count: int = Field(ge=0)
    tip_amount: Decimal = Field(default=Decimal("0"), ge=0)
    procurement_id: UUID | None = None
    notes: str | None = None


class HamaliWorkEntryUpdateRequest(BaseModel):
    farmer_id: UUID | None = None
    work_date: date | None = None
    bag_count: int | None = Field(default=None, ge=0)
    tip_amount: Decimal | None = Field(default=None, ge=0)
    procurement_id: UUID | None = None
    notes: str | None = None


class HamaliWorkEntryListResponse(PaginatedResponse[HamaliWorkEntryResponse]):
    pass


class HamaliDailyLineResponse(BaseModel):
    farmer_id: UUID
    farmer_name: str
    bag_count: int
    tip_amount: Decimal


class HamaliDailyResponse(BaseModel):
    work_date: date
    total_bags: int
    total_tips: Decimal
    lines: list[HamaliDailyLineResponse]


class HamaliTipByFarmerResponse(BaseModel):
    farmer_id: UUID
    farmer_name: str
    bag_count: int
    tip_amount: Decimal


class HamaliSummaryPeriodResponse(BaseModel):
    period: str
    date_from: date
    date_to: date
    total_bags: int
    total_tips: Decimal
    days_worked: int
    by_farmer: list[HamaliTipByFarmerResponse]
    by_day: list[HamaliDailyResponse]
