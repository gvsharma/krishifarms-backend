# Admin Platform — Features, RBAC & Implementation Plan

Org-scoped admin and field operations for KrishiFarms CRM. **Accountability** is cross-cutting: every mutation records actor, timestamp, and client device; comments and tags attach to any entity.

## Role model

| Role | Code | Capabilities |
|------|------|--------------|
| **Admin / Owner** | `OWNER` | Full access including user CRUD, all deletes, overrides (`approve`, `delete`) |
| **Manager** | `MANAGER` | Create/update operational and master data; **no** user create/delete; **no** `:delete` |
| **Farming Supervisor** | `SUPERVISOR` | Field lead — farmers, procurement, farming/field services (no delete) |
| **Vehicle Supervisor** | `DRIVER` | Vehicles, assets, transport, diesel, field-service read/write; comments |
| **Agent** | `AGENT` | Field services create/update; location + farmer read; comments |
| **Farmer** | `FARMER` | Read-only soft-wire (farmers, procurements, farming, locations, dashboard) |
| **Worker** | `WORKER` | Work orders, attendance, documents |
| **Accountant** | `ACCOUNTANT` | Finance read/create/approve (mobile catalog; DB role optional) |

Mobile maps the same role codes via `GET /auth/me` permissions. Display names must match `ROLE_DEFINITIONS` in `app/shared/permissions.py` (Android `RoleLabels`, web UI labels).

Field-service mobile permissions: `FIELD_SERVICE_VIEW` / `CREATE` / `UPDATE` / `DELETE` map from `field_services:*` and grant accessible module `field_services`.

## Location hierarchy

District → Mandal → Village masters (org-scoped). Villages keep denormalized `district` / `mandal` strings for backward-compatible clients and gain optional `district_id` / `mandal_id` FKs.

| Feature | API | Permission |
|---------|-----|------------|
| Districts | `GET/POST /districts`, `PATCH/DELETE /districts/{id}` | `districts:*` |
| Mandals | `GET/POST /mandals?district_id=`, `PATCH/DELETE /mandals/{id}` | `mandals:*` |
| Villages | `GET/POST /villages?mandal_id=&district=`, `PATCH/DELETE /villages/{id}` | `villages:*` |

Cascading dropdowns: list districts → list mandals by `district_id` → list villages by `mandal_id`.

**Web:** searchable MUI Autocomplete cascade (`frontend/src/features/master-data/location-cascade.tsx`) on Settings → Villages (District → Mandal when creating villages), Add/Edit farmer, New procurement, and field-service location (DCM loading/unloading from village masters). No free-text district/mandal/village where masters exist.

Seed: `python -m scripts.seed_locations` (Rangareddy: Keshampeta, Talakondapally, Maheshwaram, Kothur, Farooqnagar + villages/pincodes). Also invoked from `scripts/seed.py` on fresh orgs.

## Admin feature matrix

| Feature | API prefix | DB table | Phase 1 Python | Mobile |
|---------|------------|----------|------------------|--------|
| Users & roles | `/users`, `/roles` | `users`, `roles` | ✅ list/create/patch | 🔲 P1 |
| Districts | `/districts` | `districts` | ✅ CRUD | 🔲 P1 (web cascade ✅) |
| Mandals | `/mandals` | `mandals` | ✅ CRUD | 🔲 P1 (web cascade ✅) |
| Villages | `/villages` | `villages` | ✅ CRUD (+ filters) | 🔲 P1 (web cascade ✅) |
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
- [x] Location hierarchy: `districts` / `mandals` + village filters (migration `023`)
- [x] RBAC alignment: Vehicle/Farming Supervisor labels, `FARMER` read-only, soft-wired domain perms (migration `024`)
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

| Code | OWNER | MANAGER | SUPERVISOR | AGENT | DRIVER | FARMER |
|------|:-----:|:-------:|:----------:|:-----:|:------:|:------:|
| `districts:*` / `mandals:*` | ✅ | create/update/read | read | read | read | read |
| `villages:*` | ✅ | create/update/read | read | read | read | read |
| `master_data:read` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `vehicles:read` | ✅ | ✅ | ✅ | — | ✅ | — |
| `assets:*` | ✅ | create/update/read | read | — | create/update/read | — |
| `transport:*` / `diesel:*` | ✅ | create/update/read | — | — | create/update/read | — |
| `field_services:*` | ✅ | create/update/read | create/update/read | create/update/read | create/update/read | read |
| `farming:*` | ✅ | create/update/read | create/update/read | read | — | read |
| `finance:read` | ✅ | ✅ | — | — | — | — |
| `approve` / `delete` | ✅ | approve only | — | — | — | — |
| `comments:read` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `comments:create` | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| `buyers:*` CRUD | ✅ | create/update/read | read | — | — | — |
| `agents:*` | ✅ | create/update/read | read | — | — | — |
| `activity_types:*` | ✅ | create/update/read | read | — | — | — |
| `vehicle_types:*` | ✅ | create/update/read | read | — | read | — |
| `crop_prices:*` | ✅ | create/update/read | read | — | — | read |
| `users:create` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `users:delete` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| `*:delete` | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

*Manager retains `users:read` and `users:update` for field staff edits, not account provisioning.*

Soft-wired permissions (`transport:*`, `diesel:*`, `farming:*`, `finance:read`, `approve`, `delete`) remain for future trip/finance routers. Assets CRUD is live (`/assets`); do not assume other Phase 3+ endpoints exist until listed in `app/main.py`.
