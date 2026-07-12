from datetime import datetime
from uuid import UUID

from app.shared.schemas.common import ORMModel, PaginatedResponse


class AuditLogResponse(ORMModel):
    id: UUID
    org_id: UUID
    actor_user_id: UUID | None
    action: str
    entity_type: str
    entity_id: UUID | None
    before_state: dict | None
    after_state: dict | None
    ip_address: str | None
    user_agent: str | None
    request_id: str | None
    device_id: str | None = None
    client_type: str | None = None
    occurred_at: datetime


class ActivityFeedResponse(ORMModel):
    id: UUID
    org_id: UUID
    actor_user_id: UUID | None
    summary: str
    summary_te: str | None = None
    entity_type: str
    entity_id: UUID | None
    visibility: str
    device_id: str | None = None
    client_type: str | None = None
    created_at: datetime


class AuditLogListResponse(PaginatedResponse[AuditLogResponse]):
    pass


class ActivityFeedListResponse(PaginatedResponse[ActivityFeedResponse]):
    pass
