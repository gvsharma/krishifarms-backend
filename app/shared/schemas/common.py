from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    meta: dict | None = None


class TimestampSchema(BaseModel):
    created_at: datetime
    updated_at: datetime


class IDSchema(BaseModel):
    id: UUID
