from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.shared.schemas.audit_meta import AuditMetaMixin

DEFAULT_RATE_PER_BAG = Decimal("20.00")

HAMALI_WORKER_STATUSES = ("active", "inactive")
_PAYMENT_STATUS = ("pending", "scheduled", "paid")
_WEEKLY_STATUS = ("draft", "paid")


class HamaliWorkerCreateRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    full_name_te: str | None = None
    phone: str | None = Field(default=None, max_length=20)
    default_rate_per_bag: Decimal | None = Field(default=None, ge=0)


class HamaliWorkerUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=200)
    full_name_te: str | None = None
    phone: str | None = Field(default=None, max_length=20)
    default_rate_per_bag: Decimal | None = Field(default=None, ge=0)
    status: str | None = Field(default=None, pattern="^(active|inactive)$")


class HamaliWorkerResponse(AuditMetaMixin):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    worker_code: str
    full_name: str
    full_name_te: str | None
    phone: str | None
    default_rate_per_bag: Decimal
    status: str


class HamaliWorkerListResponse(BaseModel):
    items: list[HamaliWorkerResponse]
    total: int
    page: int
    page_size: int


class HamaliDailyEntryCreateRequest(BaseModel):
    hamali_worker_id: UUID
    entry_date: date
    bags_lifted: int = Field(ge=0)
    rate_per_bag: Decimal | None = Field(default=None, ge=0)
    maintenance_amount: Decimal = Field(default=Decimal("0"), ge=0)
    tip_amount: Decimal = Field(default=Decimal("0"), ge=0)
    procurement_id: UUID | None = None
    procurement_date: date | None = None
    notes: str | None = None


class HamaliDailyEntryUpdateRequest(BaseModel):
    bags_lifted: int | None = Field(default=None, ge=0)
    rate_per_bag: Decimal | None = Field(default=None, ge=0)
    maintenance_amount: Decimal | None = Field(default=None, ge=0)
    tip_amount: Decimal | None = Field(default=None, ge=0)
    notes: str | None = None


class HamaliDailyEntryResponse(AuditMetaMixin):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    hamali_worker_id: UUID
    worker_name: str | None = None
    worker_code: str | None = None
    entry_date: date
    bags_lifted: int
    rate_per_bag: Decimal
    labor_amount: Decimal
    maintenance_amount: Decimal
    tip_amount: Decimal
    total_amount: Decimal
    payment_status: str
    weekly_payment_id: UUID | None
    procurement_id: UUID | None
    procurement_date: date | None
    notes: str | None


class HamaliDailyEntryListResponse(BaseModel):
    items: list[HamaliDailyEntryResponse]
    total: int
    page: int
    page_size: int
    summary: "HamaliDailySummary"


class HamaliDailySummary(BaseModel):
    total_bags: int
    total_labor_amount: Decimal
    total_maintenance_amount: Decimal
    total_tip_amount: Decimal
    total_amount: Decimal


class HamaliWeeklySummaryResponse(BaseModel):
    week_start_date: date
    week_end_date: date
    pending_entries: int
    total_bags: int
    total_labor_amount: Decimal
    total_maintenance_amount: Decimal
    total_tip_amount: Decimal
    total_amount: Decimal
    by_worker: list["HamaliWorkerWeekSummary"]


class HamaliWorkerWeekSummary(BaseModel):
    hamali_worker_id: UUID
    worker_name: str
    worker_code: str
    days_worked: int
    total_bags: int
    total_labor_amount: Decimal
    total_maintenance_amount: Decimal
    total_tip_amount: Decimal
    total_amount: Decimal


class HamaliWeeklyPaymentCreateRequest(BaseModel):
    week_start_date: date
    notes: str | None = None


class HamaliWeeklyPaymentMarkPaidRequest(BaseModel):
    payment_reference: str | None = Field(default=None, max_length=100)
    notes: str | None = None


class HamaliWeeklyPaymentResponse(AuditMetaMixin):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    payment_number: str
    week_start_date: date
    week_end_date: date
    total_bags: int
    total_labor_amount: Decimal
    total_maintenance_amount: Decimal
    total_tip_amount: Decimal
    total_amount: Decimal
    status: str
    paid_at: datetime | None
    paid_by: UUID | None
    paid_by_name: str | None = None
    payment_reference: str | None
    notes: str | None


class HamaliWeeklyPaymentListResponse(BaseModel):
    items: list[HamaliWeeklyPaymentResponse]
    total: int
    page: int
    page_size: int


_UNSPECIFIED_FARMER_ID = UUID("00000000-0000-0000-0000-000000000000")


class HamaliMeDailyLine(BaseModel):
    farmer_id: UUID
    farmer_name: str
    bag_count: int
    tip_amount: Decimal


class HamaliMeDailyResponse(BaseModel):
    work_date: date
    total_bags: int
    total_tips: Decimal
    lines: list[HamaliMeDailyLine]


class HamaliMeFarmerSummary(BaseModel):
    farmer_id: UUID
    farmer_name: str
    bag_count: int
    tip_amount: Decimal


class HamaliMeSummaryResponse(BaseModel):
    period: str
    date_from: date
    date_to: date
    total_bags: int
    total_tips: Decimal
    days_worked: int
    by_farmer: list[HamaliMeFarmerSummary]
    by_day: list[HamaliMeDailyResponse]
