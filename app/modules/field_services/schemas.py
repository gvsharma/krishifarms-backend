from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.shared.schemas.audit_meta import AuditMetaMixin


class FieldServiceRecordCreateRequest(BaseModel):
    service_category: str = Field(
        pattern="^(field_service|tractor_work|transport|fertiliser|seeds|agri_finance|vehicle_ops|godown)$"
    )
    activity_type_id: UUID | None = None
    farmer_id: UUID | None = None
    asset_id: UUID | None = None
    vehicle_type_id: UUID | None = None
    service_date: date
    location: str | None = Field(default=None, max_length=255)
    location_te: str | None = None
    hours: Decimal | None = Field(default=None, ge=0)
    bag_count: int | None = Field(default=None, ge=0)
    quantity: Decimal | None = Field(default=None, ge=0)
    quantity_unit: str | None = Field(default=None, max_length=20)
    rate_per_unit: Decimal | None = Field(default=None, ge=0)
    diesel_amount: Decimal = Field(default=Decimal("0"), ge=0)
    amount_given: Decimal = Field(default=Decimal("0"), ge=0)
    advance_amount: Decimal = Field(default=Decimal("0"), ge=0)
    total_amount: Decimal = Field(default=Decimal("0"), ge=0)
    pending_amount: Decimal = Field(default=Decimal("0"), ge=0)
    cleaning_status: str | None = Field(default=None, pattern="^(pending|done|not_required)$")
    facility_status: str | None = Field(default=None, pattern="^(active|repair|maintenance|cleaning)$")
    status: str = Field(default="open", pattern="^(open|completed|cancelled)$")
    comments: str | None = None
    comments_te: str | None = None


class FieldServiceRecordUpdateRequest(BaseModel):
    activity_type_id: UUID | None = None
    farmer_id: UUID | None = None
    asset_id: UUID | None = None
    vehicle_type_id: UUID | None = None
    service_date: date | None = None
    location: str | None = Field(default=None, max_length=255)
    location_te: str | None = None
    hours: Decimal | None = Field(default=None, ge=0)
    bag_count: int | None = Field(default=None, ge=0)
    quantity: Decimal | None = Field(default=None, ge=0)
    quantity_unit: str | None = Field(default=None, max_length=20)
    rate_per_unit: Decimal | None = Field(default=None, ge=0)
    diesel_amount: Decimal | None = Field(default=None, ge=0)
    amount_given: Decimal | None = Field(default=None, ge=0)
    advance_amount: Decimal | None = Field(default=None, ge=0)
    total_amount: Decimal | None = Field(default=None, ge=0)
    pending_amount: Decimal | None = Field(default=None, ge=0)
    cleaning_status: str | None = Field(default=None, pattern="^(pending|done|not_required)$")
    facility_status: str | None = Field(default=None, pattern="^(active|repair|maintenance|cleaning)$")
    status: str | None = Field(default=None, pattern="^(open|completed|cancelled)$")
    comments: str | None = None
    comments_te: str | None = None


class FieldServiceRecordResponse(AuditMetaMixin):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    record_number: str
    service_category: str
    activity_type_id: UUID | None
    activity_type_name: str | None = None
    farmer_id: UUID | None
    farmer_name: str | None = None
    farmer_phone: str | None = None
    asset_id: UUID | None
    vehicle_type_id: UUID | None
    vehicle_type_name: str | None = None
    service_date: date
    location: str | None
    location_te: str | None
    hours: Decimal | None
    bag_count: int | None
    quantity: Decimal | None
    quantity_unit: str | None
    rate_per_unit: Decimal | None
    diesel_amount: Decimal
    amount_given: Decimal
    advance_amount: Decimal
    total_amount: Decimal
    pending_amount: Decimal
    cleaning_status: str | None
    facility_status: str | None
    status: str
    comments: str | None
    comments_te: str | None
    diesel_expense_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class FieldServiceRecordListResponse(BaseModel):
    items: list[FieldServiceRecordResponse]
    total: int
    page: int
    page_size: int
