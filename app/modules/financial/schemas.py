from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.shared.schemas.common import ORMModel, PaginatedResponse


class ExpenseCategoryResponse(ORMModel):
    id: UUID
    org_id: UUID
    name: str
    parent_id: UUID | None = None
    type: str
    created_at: datetime
    updated_at: datetime


class ExpenseCategoryCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    parent_id: UUID | None = None
    type: str = Field(default="expense", pattern="^(expense|income)$")


class ExpenseCategoryUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    parent_id: UUID | None = None
    type: str | None = Field(default=None, pattern="^(expense|income)$")


class ExpenseCategoryListResponse(PaginatedResponse[ExpenseCategoryResponse]):
    pass
