from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditMetaMixin(BaseModel):
    """Audit actor + timestamp fields for org-scoped entity responses."""

    model_config = ConfigDict(from_attributes=True)

    created_by: UUID | None = None
    created_by_name: str | None = None
    updated_by: UUID | None = None
    updated_by_name: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
