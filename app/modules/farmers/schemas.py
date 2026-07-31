from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.platform.schemas import CommentResponse
from app.shared.schemas.audit_meta import AuditMetaMixin
from app.shared.validation.phone import normalize_indian_mobile, normalize_indian_mobile_optional


class FarmerCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    full_name_te: str | None = None
    father_name: str | None = Field(default=None, max_length=200)
    father_name_te: str | None = None
    phone_primary: str = Field(min_length=10, max_length=10)
    phone_secondary: str | None = Field(default=None, max_length=10)
    village_id: UUID
    address: str | None = None
    address_te: str | None = None
    aadhaar_last4: str | None = Field(default=None, min_length=4, max_length=4)
    notes: str | None = None
    preferred_language: str | None = Field(default=None, max_length=10)
    preferred_payment_cycle: str | None = Field(default=None, max_length=50)
    preferred_payment_method: str | None = Field(default=None, max_length=50)
    trust_rating: int | None = Field(default=None, ge=1, le=5)
    is_vip: bool = False
    geo_lat: Decimal | None = None
    geo_lng: Decimal | None = None

    @field_validator("phone_primary")
    @classmethod
    def validate_phone_primary(cls, value: str) -> str:
        return normalize_indian_mobile(value)

    @field_validator("phone_secondary")
    @classmethod
    def validate_phone_secondary(cls, value: str | None) -> str | None:
        return normalize_indian_mobile_optional(value)


class FarmerUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=200)
    full_name_te: str | None = None
    father_name: str | None = Field(default=None, max_length=200)
    father_name_te: str | None = None
    phone_primary: str | None = Field(default=None, min_length=10, max_length=10)
    phone_secondary: str | None = Field(default=None, max_length=10)
    village_id: UUID | None = None
    address: str | None = None
    address_te: str | None = None
    aadhaar_last4: str | None = Field(default=None, min_length=4, max_length=4)
    status: str | None = Field(default=None, pattern="^(active|inactive|blocked)$")
    notes: str | None = None
    preferred_language: str | None = Field(default=None, max_length=10)
    preferred_payment_cycle: str | None = Field(default=None, max_length=50)
    preferred_payment_method: str | None = Field(default=None, max_length=50)
    trust_rating: int | None = Field(default=None, ge=1, le=5)
    is_vip: bool | None = None
    geo_lat: Decimal | None = None
    geo_lng: Decimal | None = None

    @field_validator("phone_primary")
    @classmethod
    def validate_phone_primary(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return normalize_indian_mobile(value)

    @field_validator("phone_secondary")
    @classmethod
    def validate_phone_secondary(cls, value: str | None) -> str | None:
        return normalize_indian_mobile_optional(value)


class FarmerResponse(AuditMetaMixin):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    org_id: UUID
    farmer_code: str
    full_name: str
    full_name_te: str | None
    father_name: str | None
    father_name_te: str | None
    phone_primary: str
    phone_secondary: str | None
    village_id: UUID
    village_name: str | None = None
    address: str | None
    address_te: str | None
    aadhaar_last4: str | None
    status: str
    notes: str | None
    preferred_language: str | None = None
    preferred_payment_cycle: str | None = None
    preferred_payment_method: str | None = None
    trust_rating: int | None = None
    is_vip: bool = False
    geo_lat: Decimal | None = None
    geo_lng: Decimal | None = None
    outstanding_amount: Decimal | None = None
    tags: list[str] = []
    comments: list[CommentResponse] = []


class FarmerListItemResponse(AuditMetaMixin):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    farmer_code: str
    full_name: str
    full_name_te: str | None
    phone_primary: str
    village_id: UUID
    village_name: str | None = None
    status: str
    is_vip: bool = False
    trust_rating: int | None = None
    tags: list[str] = []


class FarmerListResponse(BaseModel):
    items: list[FarmerListItemResponse]
    total: int
    page: int
    page_size: int


class BankAccountCreateRequest(BaseModel):
    account_holder_name: str = Field(min_length=2, max_length=200)
    bank_name: str = Field(min_length=2, max_length=200)
    branch: str | None = Field(default=None, max_length=200)
    ifsc: str = Field(min_length=11, max_length=11)
    account_number: str = Field(min_length=4, max_length=30)
    is_primary: bool = False


class BankAccountUpdateRequest(BaseModel):
    account_holder_name: str | None = Field(default=None, min_length=2, max_length=200)
    bank_name: str | None = Field(default=None, min_length=2, max_length=200)
    branch: str | None = Field(default=None, max_length=200)
    ifsc: str | None = Field(default=None, min_length=11, max_length=11)
    account_number: str | None = Field(default=None, min_length=4, max_length=30)
    is_primary: bool | None = None


class BankAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    account_holder_name: str
    bank_name: str
    branch: str | None
    ifsc: str
    account_number_masked: str
    is_primary: bool


class LandParcelCreateRequest(BaseModel):
    survey_number: str = Field(min_length=1, max_length=100)
    acres: Decimal = Field(gt=0)
    land_type: str | None = Field(default=None, max_length=50)
    location_notes: str | None = None
    geo_lat: Decimal | None = None
    geo_lng: Decimal | None = None
    ownership: str | None = Field(default=None, pattern="^(owned|lease|shared)$")
    irrigation_type: str | None = Field(default=None, max_length=50)
    water_source: str | None = Field(default=None, max_length=50)
    soil_type: str | None = Field(default=None, max_length=50)
    village_name: str | None = Field(default=None, max_length=200)


class LandParcelUpdateRequest(BaseModel):
    survey_number: str | None = Field(default=None, min_length=1, max_length=100)
    acres: Decimal | None = Field(default=None, gt=0)
    land_type: str | None = Field(default=None, max_length=50)
    location_notes: str | None = None
    geo_lat: Decimal | None = None
    geo_lng: Decimal | None = None
    ownership: str | None = Field(default=None, pattern="^(owned|lease|shared)$")
    irrigation_type: str | None = Field(default=None, max_length=50)
    water_source: str | None = Field(default=None, max_length=50)
    soil_type: str | None = Field(default=None, max_length=50)
    village_name: str | None = Field(default=None, max_length=200)


class LandParcelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    survey_number: str
    acres: Decimal
    land_type: str | None
    location_notes: str | None
    geo_lat: Decimal | None
    geo_lng: Decimal | None
    ownership: str | None = None
    irrigation_type: str | None = None
    water_source: str | None = None
    soil_type: str | None = None
    village_name: str | None = None


class CropHistoryCreateRequest(BaseModel):
    crop_type_id: UUID
    season: str = Field(min_length=1, max_length=50)
    year: int = Field(ge=2000, le=2100)
    acres: Decimal | None = Field(default=None, gt=0)
    notes: str | None = None
    survey_number: str | None = Field(default=None, max_length=100)
    village_name: str | None = Field(default=None, max_length=200)
    seed_variety: str | None = Field(default=None, max_length=100)
    seed_supplier: str | None = Field(default=None, max_length=200)
    fertilizer_supplier: str | None = Field(default=None, max_length=200)
    pesticides_used: str | None = None
    cultivation_stage: str | None = Field(default=None, max_length=50)
    expected_yield: Decimal | None = None
    actual_yield: Decimal | None = None
    selling_market: str | None = Field(default=None, max_length=200)
    selling_price: Decimal | None = None
    harvest_date: date | None = None
    geo_lat: Decimal | None = None
    geo_lng: Decimal | None = None


class CropHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    crop_type_id: UUID
    crop_type_name: str | None = None
    season: str
    year: int
    acres: Decimal | None = None
    notes: str | None = None
    survey_number: str | None = None
    village_name: str | None = None
    seed_variety: str | None = None
    seed_supplier: str | None = None
    fertilizer_supplier: str | None = None
    pesticides_used: str | None = None
    cultivation_stage: str | None = None
    expected_yield: Decimal | None = None
    actual_yield: Decimal | None = None
    selling_market: str | None = None
    selling_price: Decimal | None = None
    harvest_date: date | None = None
    geo_lat: Decimal | None = None
    geo_lng: Decimal | None = None


class LedgerEntryResponse(BaseModel):
    id: UUID
    entry_date: date
    entry_type: str
    reference_type: str
    reference_id: UUID
    debit: Decimal
    credit: Decimal
    balance_after: Decimal
    description: str | None = None


class LedgerListResponse(BaseModel):
    items: list[LedgerEntryResponse]
    total: int
    page: int
    page_size: int


class OutstandingResponse(BaseModel):
    farmer_id: UUID
    outstanding_amount: Decimal
    as_of_date: date


class FarmerDetailResponse(FarmerResponse):
    bank_accounts: list[BankAccountResponse] = []
    land_parcels: list[LandParcelResponse] = []
