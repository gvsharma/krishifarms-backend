from uuid import UUID

from sqlalchemy.orm import Session

from app.modules.audit.models import ActivityFeed, AuditLog


def write_audit_log(
    db: Session,
    *,
    org_id: UUID,
    actor_user_id: UUID | None,
    action: str,
    entity_type: str,
    entity_id: UUID | None = None,
    before_state: dict | None = None,
    after_state: dict | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    request_id: str | None = None,
) -> AuditLog:
    entry = AuditLog(
        org_id=org_id,
        actor_user_id=actor_user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        before_state=before_state,
        after_state=after_state,
        ip_address=ip_address,
        user_agent=user_agent,
        request_id=request_id,
    )
    db.add(entry)
    return entry


def write_activity_feed(
    db: Session,
    *,
    org_id: UUID,
    actor_user_id: UUID | None,
    summary: str,
    entity_type: str,
    entity_id: UUID | None = None,
    visibility: str = "org",
) -> ActivityFeed:
    entry = ActivityFeed(
        org_id=org_id,
        actor_user_id=actor_user_id,
        summary=summary,
        entity_type=entity_type,
        entity_id=entity_id,
        visibility=visibility,
    )
    db.add(entry)
    return entry
