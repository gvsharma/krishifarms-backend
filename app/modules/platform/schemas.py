from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.shared.schemas.audit_meta import AuditMetaMixin
from app.shared.validation.phone import normalize_indian_mobile_optional


class AuditMetaResponse(AuditMetaMixin):
    """Backward-compatible alias used by platform module responses."""

    pass


class ActivityTypeCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    name_te: str | None = None
    code: str = Field(min_length=1, max_length=50)
    service_category: str | None = Field(
        default=None,
        pattern="^(field_service|tractor_work|transport|fertiliser|seeds|agri_finance|vehicle_ops|godown)$",
    )
    default_rate_type: str | None = Field(default=None, pattern="^(hourly|daily|fixed)$")
    is_active: bool = True


class ActivityTypeUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    name_te: str | None = None
    service_category: str | None = Field(
        default=None,
        pattern="^(field_service|tractor_work|transport|fertiliser|seeds|agri_finance|vehicle_ops|godown)$",
    )
    default_rate_type: str | None = Field(default=None, pattern="^(hourly|daily|fixed)$")
    is_active: bool | None = None


class ActivityTypeResponse(AuditMetaResponse):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    name_te: str | None
    code: str
    service_category: str | None
    default_rate_type: str | None
    is_active: bool


class ActivityTypeListResponse(BaseModel):
    items: list[ActivityTypeResponse]
    total: int
    page: int
    page_size: int


class PaymentModeCreateRequest(BaseModel):
    code: str = Field(min_length=1, max_length=30)
    name: str = Field(min_length=1, max_length=100)
    name_te: str | None = None
    is_active: bool = True


class PaymentModeUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    name_te: str | None = None
    is_active: bool | None = None


class PaymentModeResponse(AuditMetaResponse):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    name_te: str | None
    is_active: bool


class PaymentModeListResponse(BaseModel):
    items: list[PaymentModeResponse]
    total: int
    page: int
    page_size: int


class BuyerCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    name_te: str | None = None
    phone: str | None = Field(default=None, max_length=10)
    gstin: str | None = Field(default=None, max_length=20)
    contact_person: str | None = Field(default=None, max_length=200)
    address: str | None = None
    village_id: UUID | None = None
    notes: str | None = None
    is_active: bool = True

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return normalize_indian_mobile_optional(value)


class BuyerUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    name_te: str | None = None
    phone: str | None = Field(default=None, max_length=10)
    gstin: str | None = Field(default=None, max_length=20)
    contact_person: str | None = Field(default=None, max_length=200)
    address: str | None = None
    village_id: UUID | None = None
    notes: str | None = None
    is_active: bool | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return normalize_indian_mobile_optional(value)


class BuyerResponse(AuditMetaResponse):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    name_te: str | None
    phone: str | None
    gstin: str | None
    contact_person: str | None
    address: str | None
    village_id: UUID | None
    notes: str | None
    is_active: bool


class BuyerListResponse(BaseModel):
    items: list[BuyerResponse]
    total: int
    page: int
    page_size: int


class FieldAgentCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    name_te: str | None = None
    phone: str | None = Field(default=None, max_length=10)
    user_id: UUID | None = None
    village_id: UUID | None = None
    commission_pct: Decimal | None = Field(default=None, ge=0, le=100)
    notes: str | None = None
    is_active: bool = True

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return normalize_indian_mobile_optional(value)


class FieldAgentUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    name_te: str | None = None
    phone: str | None = Field(default=None, max_length=10)
    user_id: UUID | None = None
    village_id: UUID | None = None
    commission_pct: Decimal | None = Field(default=None, ge=0, le=100)
    notes: str | None = None
    is_active: bool | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        return normalize_indian_mobile_optional(value)


class FieldAgentResponse(AuditMetaResponse):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    name_te: str | None
    phone: str | None
    user_id: UUID | None
    village_id: UUID | None
    commission_pct: Decimal | None
    notes: str | None
    is_active: bool


class FieldAgentListResponse(BaseModel):
    items: list[FieldAgentResponse]
    total: int
    page: int
    page_size: int


class VehicleTypeCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    name_te: str | None = None
    code: str = Field(min_length=1, max_length=50)
    capacity_quintals: Decimal | None = Field(default=None, ge=0)
    fuel_type: str | None = Field(default=None, max_length=30)
    default_rate: Decimal | None = Field(default=None, ge=0)
    default_rate_unit: str | None = Field(default=None, pattern="^(hour|trip|bale)$")
    notes: str | None = None
    is_active: bool = True


class VehicleTypeUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    name_te: str | None = None
    code: str | None = Field(default=None, min_length=1, max_length=50)
    capacity_quintals: Decimal | None = Field(default=None, ge=0)
    fuel_type: str | None = Field(default=None, max_length=30)
    default_rate: Decimal | None = Field(default=None, ge=0)
    default_rate_unit: str | None = Field(default=None, pattern="^(hour|trip|bale)$")
    notes: str | None = None
    is_active: bool | None = None


class VehicleTypeResponse(AuditMetaResponse):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    name_te: str | None
    code: str
    capacity_quintals: Decimal | None
    fuel_type: str | None
    default_rate: Decimal | None = None
    default_rate_unit: str | None = None
    notes: str | None
    is_active: bool


class VehicleTypeListResponse(BaseModel):
    items: list[VehicleTypeResponse]
    total: int
    page: int
    page_size: int


class CropPriceCreateRequest(BaseModel):
    crop_type_id: UUID
    village_id: UUID | None = None
    effective_from: date
    effective_to: date | None = None
    rate_per_quintal: Decimal = Field(gt=0)
    notes: str | None = None
    is_active: bool = True


class CropPriceUpdateRequest(BaseModel):
    village_id: UUID | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    rate_per_quintal: Decimal | None = Field(default=None, gt=0)
    notes: str | None = None
    is_active: bool | None = None


class CropPriceResponse(AuditMetaResponse):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    crop_type_id: UUID
    village_id: UUID | None
    effective_from: date
    effective_to: date | None
    rate_per_quintal: Decimal
    notes: str | None
    is_active: bool


class CropPriceListResponse(BaseModel):
    items: list[CropPriceResponse]
    total: int
    page: int
    page_size: int


class CommentCreateRequest(BaseModel):
    entity_type: str = Field(min_length=1, max_length=50)
    entity_id: UUID
    body: str = Field(min_length=1)
    body_te: str | None = None


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    entity_type: str
    entity_id: UUID
    body: str
    body_te: str | None
    author_user_id: UUID
    author_name: str | None = None
    device_id: str | None
    client_type: str | None
    created_at: datetime


class CommentListResponse(BaseModel):
    items: list[CommentResponse]
    total: int
    page: int
    page_size: int


class TagCreateRequest(BaseModel):
    entity_type: str = Field(min_length=1, max_length=50)
    entity_id: UUID
    tag: str = Field(min_length=1, max_length=50)


class TagResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    entity_type: str
    entity_id: UUID
    tag: str
    created_by: UUID | None
    created_by_name: str | None = None
    device_id: str | None
    created_at: datetime


class TagListResponse(BaseModel):
    items: list[TagResponse]
    total: int
