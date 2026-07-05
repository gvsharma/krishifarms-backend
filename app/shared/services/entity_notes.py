"""Attach polymorphic comments and tags to entity detail/list responses."""

from __future__ import annotations

from typing import TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.modules.platform import service as platform_service
from app.modules.platform.schemas import CommentResponse

T = TypeVar("T", bound=BaseModel)


class EntityNotesMixin(BaseModel):
    comments: list[CommentResponse] = []
    tags: list[str] = []


def attach_entity_notes(
    db: Session,
    org_id: UUID,
    entity_type: str,
    entity_id: UUID,
    response: T,
    *,
    include_comments: bool = True,
    include_tags: bool = True,
    comment_limit: int = 20,
) -> T:
    updates: dict = {}

    if include_comments:
        comments, _, names = platform_service.list_comments(
            db, org_id, entity_type, entity_id, page=1, page_size=comment_limit
        )
        updates["comments"] = [
            CommentResponse.model_validate(c).model_copy(update={"author_name": names.get(c.author_user_id)})
            for c in comments
        ]

    if include_tags:
        tag_rows, tag_names = platform_service.list_tags(db, org_id, entity_type, entity_id)
        updates["tags"] = [t.tag for t in tag_rows]
        if include_comments and "comments" not in updates:
            pass
        _ = tag_names  # names available for TagResponse if full objects needed later

    if not updates:
        return response
    return response.model_copy(update=updates)


def attach_tags_only(
    db: Session,
    org_id: UUID,
    entity_type: str,
    entity_ids: list[UUID],
) -> dict[UUID, list[str]]:
    if not entity_ids:
        return {}
    result: dict[UUID, list[str]] = {eid: [] for eid in entity_ids}
    tag_rows, _ = platform_service.list_tags(db, org_id, entity_type, None)
    for row in tag_rows:
        if row.entity_id in result:
            result[row.entity_id].append(row.tag)
    return result
