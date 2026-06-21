from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import CurrentUserContext, get_db, require_permission
from app.modules.audit import service
from app.modules.audit.schemas import ActivityFeedListResponse, ActivityFeedResponse, AuditLogListResponse, AuditLogResponse
from app.shared.schemas.common import APIResponse

router = APIRouter(tags=["Audit"])


@router.get("/audit-logs", response_model=APIResponse[AuditLogListResponse])
def list_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    ctx: CurrentUserContext = Depends(require_permission("audit:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_audit_logs(
        db, ctx.user.org_id, page, page_size, entity_type=entity_type, entity_id=entity_id
    )
    return APIResponse(
        data=AuditLogListResponse(
            items=[AuditLogResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.get("/activity-feed", response_model=APIResponse[ActivityFeedListResponse])
def list_activity_feed(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ctx: CurrentUserContext = Depends(require_permission("audit:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_activity_feed(db, ctx.user.org_id, page, page_size)
    return APIResponse(
        data=ActivityFeedListResponse(
            items=[ActivityFeedResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )
