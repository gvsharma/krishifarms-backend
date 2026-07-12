# Cross-Cutting Patterns

Shared backend patterns for comments, tags, audit metadata, and accountability across all entity modules.

## Audit metadata on responses

Use `AuditMetaMixin` from `app/shared/schemas/audit_meta.py` on Pydantic response models:

```python
from app.shared.schemas.audit_meta import AuditMetaMixin

class FarmerResponse(AuditMetaMixin):
    id: UUID
    full_name: str
    ...
```

Routers resolve `created_by_name` / `updated_by_name` from `users.full_name` when building responses.

## Comments and tags on any entity

Polymorphic tables: `entity_comments`, `entity_tags` (platform module).

### Standalone API

- `GET/POST /comments` — filter by `entity_type` + `entity_id`
- `GET/POST/DELETE /tags`

### Embedded on detail responses

Use `app/shared/services/entity_notes.py`:

```python
from app.shared.services.entity_notes import attach_entity_notes, attach_tags_only

# Detail — full comments + tag strings
response = attach_entity_notes(db, org_id, "farmer", farmer.id, farmer_response)

# List — tags only (lighter)
tag_map = attach_tags_only(db, org_id, "farmer", [f.id for f in items])
```

Entity type strings: `farmer`, `procurement`, `buyer`, `field_agent`, etc. (lowercase snake).

## Client accountability

`ClientContext` (`app/core/client_context.py`) captures:

| Header | Field |
|--------|-------|
| `X-Device-Id` | `device_id` |
| `X-Client-Type` | `client_type` |
| `X-Request-ID` | `request_id` |

Pass to service layer on mutations → `write_audit_log(..., device_id=..., client_type=..., request_id=...)`.
Activity feed: `write_activity_feed(..., device_id=..., client_type=..., summary_te=...)`.

Login / refresh persist `device_id` on `refresh_tokens` (column from migration `002`; no `client_type` on that table).

Push tokens and FCM: see [DEVICES_NOTIFICATIONS.md](./DEVICES_NOTIFICATIONS.md).

## Activity feed + audit log

Every create/update/delete should:

1. `write_audit_log` with `before_state` / `after_state` JSON
2. `write_activity_feed` with human-readable `summary`

See `app/modules/platform/service.py` `_audit()` and `app/modules/farmers/service.py` for templates.

## Adding a new entity module

1. Map SQLAlchemy model to existing migration table
2. Response schema inherits `AuditMetaMixin`
3. Service `_audit()` helper with entity_type string
4. Router: `require_permission("<resource>:action")`; OWNER-only delete via `require_role("OWNER")`
5. Detail route: `attach_entity_notes(...)`
6. Register model in `app/models.py`, router in `app/main.py`
7. Add permissions to `app/shared/permissions.py` + migration if new codes
8. Update AGENT_GUIDE matrix + module doc
