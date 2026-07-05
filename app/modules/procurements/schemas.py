from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.platform.schemas import CommentResponse
from app.shared.schemas.audit_meta import AuditMetaMixin

PROCUREMENT_STATUSES = (
    "draft",
    "pending_weighment",
    "weighed",
    "priced",
    "confirmed",
    "paid_partial",
    "paid_full",
    "cancelled",
    "reversed",
)

CANCELLABLE_STATUSES = frozenset({"draft", "pending_weighment", "weighed"})


class ProcurementDeductionInput(BaseModel):
    deduction_type: str = Field(min_length=1, max_length=100)
    deduction_type_te: str | None = None
    amount: Decimal = Field(ge=0)
    notes: str | None = None


class ProcurementDeductionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    deduction_type: str
    deduction_type_te: str | None
    amount: Decimal
    notes: str | None


class ProcurementCreateRequest(BaseModel):
    farmer_id: UUID
    crop_type_id: UUID
    village_id: UUID
    procurement_date: date
    bag_count: int = Field(default=0, ge=0)
    notes: str | None = None


class ProcurementUpdateRequest(BaseModel):
    farmer_id: UUID | None = None
    crop_type_id: UUID | None = None
    village_id: UUID | None = None
    bag_count: int | None = Field(default=None, ge=0)
    notes: str | None = None


class WeighmentRequest(BaseModel):
    gross_weight_kg: Decimal = Field(gt=0)
    tare_weight_kg: Decimal = Field(default=Decimal("0"), ge=0)
    moisture_pct: Decimal | None = Field(default=None, ge=0, le=100)
    bag_count: int | None = Field(default=None, ge=0)


class ProcurementCancelRequest(BaseModel):
    reason: str = Field(min_length=3)


class ProcurementReverseRequest(BaseModel):
    reason: str = Field(min_length=3)


class ProcurementResponse(AuditMetaMixin):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    org_id: UUID
    procurement_number: str
    farmer_id: UUID
    farmer_name: str | None = None
    crop_type_id: UUID
    crop_type_name: str | None = None
    village_id: UUID
    village_name: str | None = None
    procurement_date: date
    bag_count: int
    gross_weight_kg: Decimal
    moisture_pct: Decimal | None
    net_weight_kg: Decimal
    rate_per_quintal: Decimal
    gross_amount: Decimal
    deduction_amount: Decimal
    net_amount: Decimal
    status: str
    confirmed_at: datetime | None = None
    confirmed_by: UUID | None = None
    confirmed_by_name: str | None = None
    cancelled_at: datetime | None = None
    cancellation_reason: str | None = None
    notes: str | None
    deductions: list[ProcurementDeductionResponse] = []
    tags: list[str] = []
    comments: list[CommentResponse] = []


class ProcurementListItemResponse(AuditMetaMixin):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    procurement_number: str
    farmer_id: UUID
    farmer_name: str | None = None
    crop_type_id: UUID
    crop_type_name: str | None = None
    village_id: UUID
    procurement_date: date
    net_weight_kg: Decimal
    net_amount: Decimal
    status: str
    tags: list[str] = []


class ProcurementListResponse(BaseModel):
    items: list[ProcurementListItemResponse]
    total: int
    page: int
    page_size: int
