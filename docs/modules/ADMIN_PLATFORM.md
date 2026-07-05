# Admin Platform — Features, RBAC & Implementation Plan

Org-scoped admin and field operations for KrishiFarms CRM. **Accountability** is cross-cutting: every mutation records actor, timestamp, and client device; comments and tags attach to any entity.

## Role model

| Role | Code | Capabilities |
|------|------|--------------|
| **Admin** | `OWNER` | Full access including user CRUD, all deletes, overrides |
| **Manager** | `MANAGER` | Create/update operational and master data; **no** user create/delete; **no** delete on any resource |
| **Agent** | `AGENT` | Read assigned modules; **comments only** (no create/delete on business records) |
| **Driver** | `DRIVER` | Read fleet/trips; **comments only** |
| **Supervisor** | `SUPERVISOR` | Field lead — create/update farmers, procurement, workforce (no delete) |
| **Worker** | `WORKER` | Work orders, attendance, documents |
| **Accountant** | `ACCOUNTANT` | Finance read/create/approve |

Mobile maps the same role codes via `GET /auth/me` permissions.

## Admin feature matrix

| Feature | API prefix | DB table | Phase 1 Python | Mobile |
|---------|------------|----------|------------------|--------|
| Users & roles | `/users`, `/roles` | `users`, `roles` | ✅ list/create/patch | 🔲 P1 |
| Villages | `/villages` | `villages` | ✅ CRUD | 🔲 P1 |
| Crop types | `/crop-types` | `crop_types` | ✅ CRUD | 🔲 P1 |
| Expense categories | `/expense-categories` | `expense_categories` | ✅ CRUD | 🔲 P1 |
| Crop prices | `/crop-prices` | `crop_price_rules` | ✅ Phase 1b | 🔲 P2 |
| Buyers | `/buyers` | `buyers` | ✅ Phase 1b | 🔲 P2 |
| Field agents | `/agents` | `field_agents` | ✅ Phase 1b | 🔲 P2 |
| Services (baler, tractor, seeds, etc.) | `/activity-types` | `activity_types` | ✅ Phase 1b | 🔲 P2 |
| Vehicle types | `/vehicle-types` | `vehicle_types` | ✅ Phase 1b | 🔲 P2 |
| Comments (any entity) | `/comments` | `entity_comments` | ✅ Phase 1b | 🔲 P1 |
| Tags (any entity) | `/tags` | `entity_tags` | ✅ Phase 1b | 🔲 P2 |
| Audit log | `/audit-logs` | `audit_logs` | ✅ read | 🔲 P2 |
| Activity feed | `/activity-feed` | `activity_feed` | ✅ read | 🔲 P2 |
| Documents | `/documents` | `documents` | 🟡 partial | ✅ |
| Farmers / procurement / fleet / finance | Phase 2–5 paths | migrated | 🟡 farmers CRUD (2a) | 🟡 partial |

## Accountability contract

### Request headers (mobile + web)

| Header | Purpose |
|--------|---------|
| `X-Device-Id` | Stable device identifier (Android `Settings.Secure.ANDROID_ID` or generated UUID) |
| `X-Client-Type` | `mobile` \| `web` \| `api` |
| `X-Request-ID` | Correlation id (optional) |

### Stored on mutations

- `created_by`, `updated_by`, `created_at`, `updated_at` on all master tables (`audit_columns()`)
- `audit_logs.device_id`, `audit_logs.client_type` on writes
- `entity_comments.device_id`, `entity_comments.client_type` on comments
- Activity feed entries on create/update/delete (wired in services)

### API response shape (master data)

List/detail responses include audit metadata where applicable:

```json
{
  "id": "...",
  "name": "...",
  "created_by": "uuid",
  "created_by_name": "Ravi Kumar",
  "updated_by": "uuid",
  "updated_at": "2026-07-05T12:00:00Z",
  "tags": ["paddy", "kharif"]
}
```

## Implementation phases

### Phase 1b (this branch) — Platform foundation

- [x] `entity_comments`, `entity_tags` tables + REST API
- [x] `buyers`, `field_agents`, `vehicle_types`, `crop_price_rules` + REST API
- [x] `activity_types` SQLAlchemy + REST API (table exists from migration 003)
- [x] Client context (`X-Device-Id`, `X-Client-Type`) → audit logs
- [x] RBAC migration: `AGENT`, `DRIVER`; manager no delete / no user create
- [x] OpenAPI path stubs under `docs/api/paths/platform.yaml`

### Phase 2 — Operational CRUD (Python)

Farmers (Phase 2a ✅), procurements, expenses, workers, assets — implement routers per AGENT_GUIDE matrix; wire comments/tags on all entities. See [CROSS_CUTTING.md](./CROSS_CUTTING.md).

### Phase 3 — Web admin UI

Next.js settings screens: users, master data, buyers, prices, audit viewer.

### Phase 4 — Mobile admin shell

- Settings module (`USER_MANAGE`, `SETTINGS_MANAGE`)
- Master data screens gated by permission
- Comment composer on detail screens (all roles with `COMMENT_CREATE`)
- Hide create/delete FABs per role (`ActionPermissions`)

## Permission codes (new)

| Code | OWNER | MANAGER | SUPERVISOR | AGENT | DRIVER |
|------|:-----:|:-------:|:----------:|:-----:|:------:|
| `comments:read` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `comments:create` | ✅ | ✅ | ✅ | ✅ | ✅ |
| `buyers:*` CRUD | ✅ | create/update/read | read | read | — |
| `agents:*` | ✅ | create/update/read | read | read | — |
| `activity_types:*` | ✅ | create/update/read | read | read | — |
| `vehicle_types:*` | ✅ | create/update/read | read | read | read |
| `crop_prices:*` | ✅ | create/update/read | read | — | — |
| `users:create` | ✅ | ❌ | ❌ | ❌ | ❌ |
| `users:delete` | ✅ | ❌ | ❌ | ❌ | ❌ |
| `*:delete` | ✅ | ❌ | ❌ | ❌ | ❌ |

*Manager retains `users:read` and `users:update` for field staff edits, not account provisioning.*
