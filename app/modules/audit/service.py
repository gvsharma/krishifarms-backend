from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.audit.models import ActivityFeed, AuditLog


def list_audit_logs(
    db: Session,
    org_id: UUID,
    page: int,
    page_size: int,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
) -> tuple[list[AuditLog], int]:
    query = db.query(AuditLog).filter(AuditLog.org_id == org_id).order_by(AuditLog.occurred_at.desc())
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def list_activity_feed(db: Session, org_id: UUID, page: int, page_size: int) -> tuple[list[ActivityFeed], int]:
    query = (
        db.query(ActivityFeed)
        .filter(ActivityFeed.org_id == org_id)
        .order_by(ActivityFeed.created_at.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total
