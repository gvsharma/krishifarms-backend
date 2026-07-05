from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.platform.schemas import CommentResponse
from app.shared.schemas.audit_meta import AuditMetaMixin


class FarmerCreateRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=200)
    full_name_te: str | None = None
    father_name: str | None = Field(default=None, max_length=200)
    father_name_te: str | None = None
    phone_primary: str = Field(min_length=10, max_length=20)
    phone_secondary: str | None = Field(default=None, max_length=20)
    village_id: UUID
    address: str | None = None
    address_te: str | None = None
    aadhaar_last4: str | None = Field(default=None, min_length=4, max_length=4)
    notes: str | None = None


class FarmerUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=200)
    full_name_te: str | None = None
    father_name: str | None = Field(default=None, max_length=200)
    father_name_te: str | None = None
    phone_primary: str | None = Field(default=None, min_length=10, max_length=20)
    phone_secondary: str | None = Field(default=None, max_length=20)
    village_id: UUID | None = None
    address: str | None = None
    address_te: str | None = None
    aadhaar_last4: str | None = Field(default=None, min_length=4, max_length=4)
    status: str | None = Field(default=None, pattern="^(active|inactive|blocked)$")
    notes: str | None = None


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
    tags: list[str] = []


class FarmerListResponse(BaseModel):
    items: list[FarmerListItemResponse]
    total: int
    page: int
    page_size: int
