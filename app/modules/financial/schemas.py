from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.schemas.common import ORMModel, PaginatedResponse

EXPENSE_STATUSES = ("draft", "posted", "reversed")
COLLECTION_SOURCE_TYPES = ("rental", "other")
COLLECTION_STATUSES = ("draft", "posted", "reversed")
VEHICLE_TRIP_SOURCE = "vehicle_trip"
FIELD_SERVICE_SOURCE = "field_service"
FUEL_CATEGORY_NAME = "Fuel"


class ExpenseCategoryResponse(ORMModel):
    id: UUID
    org_id: UUID
    name: str
    name_te: str | None = None
    parent_id: UUID | None = None
    type: str
    created_at: datetime
    updated_at: datetime


class ExpenseCategoryCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    name_te: str | None = None
    parent_id: UUID | None = None
    type: str = Field(default="expense", pattern="^(expense|income)$")


class ExpenseCategoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    name_te: str | None = None
    parent_id: UUID | None = None
    type: str | None = Field(default=None, pattern="^(expense|income)$")


class ExpenseCategoryListResponse(PaginatedResponse[ExpenseCategoryResponse]):
    pass


class ExpenseCreateRequest(BaseModel):
    category_id: UUID
    expense_date: date
    amount: Decimal = Field(gt=0)
    payment_mode_id: UUID
    vendor_name: str | None = Field(default=None, max_length=200)
    farm_id: UUID | None = None
    asset_id: UUID | None = None
    description: str | None = None
    description_te: str | None = None
    status: str = Field(default="posted", pattern="^(draft|posted)$")
    document_ids: list[UUID] = Field(default_factory=list)


class ExpenseUpdateRequest(BaseModel):
    category_id: UUID | None = None
    expense_date: date | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    payment_mode_id: UUID | None = None
    vendor_name: str | None = Field(default=None, max_length=200)
    farm_id: UUID | None = None
    asset_id: UUID | None = None
    description: str | None = None
    description_te: str | None = None


class ExpenseResponse(ORMModel):
    id: UUID
    expense_number: str
    category_id: UUID
    category_name: str | None = None
    expense_date: date
    amount: Decimal
    vendor_name: str | None = None
    payment_mode_id: UUID
    farm_id: UUID | None = None
    asset_id: UUID | None = None
    description: str | None = None
    description_te: str | None = None
    status: str
    source_type: str | None = None
    source_id: UUID | None = None


class ExpenseListResponse(PaginatedResponse[ExpenseResponse]):
    pass


class CollectionCreateRequest(BaseModel):
    source_type: str = Field(pattern="^(rental|other)$")
    source_id: UUID
    collection_date: date
    amount: Decimal = Field(gt=0)
    payment_mode_id: UUID
    customer_id: UUID | None = None
    reference_no: str | None = Field(default=None, max_length=100)
    notes: str | None = None
    document_ids: list[UUID] = Field(default_factory=list)


class CollectionResponse(ORMModel):
    id: UUID
    collection_number: str
    source_type: str
    source_id: UUID
    customer_id: UUID | None = None
    collection_date: date
    amount: Decimal
    payment_mode_id: UUID
    reference_no: str | None = None
    notes: str | None = None
    status: str


class CollectionListResponse(PaginatedResponse[CollectionResponse]):
    pass
