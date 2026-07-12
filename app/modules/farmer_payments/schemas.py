from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

PAYMENT_TYPES = ("advance", "final", "adjustment")
PAYMENT_STATUSES = ("pending", "completed", "failed", "reversed")


class FarmerPaymentCreateRequest(BaseModel):
    farmer_id: UUID
    payment_type: str = Field(pattern="^(advance|final|adjustment)$")
    payment_date: date
    amount: Decimal = Field(gt=0)
    payment_mode_id: UUID
    bank_account_id: UUID | None = None
    reference_no: str | None = Field(default=None, max_length=100)
    notes: str | None = None


class PaymentAllocationItem(BaseModel):
    procurement_id: UUID
    procurement_date: date
    allocated_amount: Decimal = Field(gt=0)


class PaymentAllocateRequest(BaseModel):
    allocations: list[PaymentAllocationItem] = Field(min_length=1)


class PaymentReverseRequest(BaseModel):
    reason: str = Field(min_length=3)


class FarmerPaymentAllocationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    procurement_id: UUID | None = None
    procurement_date: date | None = None
    allocated_amount: Decimal


class FarmerPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    payment_number: str
    farmer_id: UUID
    payment_type: str
    payment_date: date
    amount: Decimal
    payment_mode_id: UUID
    reference_no: str | None = None
    bank_account_id: UUID | None = None
    status: str
    notes: str | None = None
    allocations: list[FarmerPaymentAllocationResponse] = []


class FarmerPaymentListResponse(BaseModel):
    items: list[FarmerPaymentResponse]
    total: int
    page: int
    page_size: int
