# KrishiFarms CRM — App Inventory

Single reference for **features**, **live APIs**, and **database** as of migration head `202506210030`.

**Base URL:** `/api/v1`  
**Auth:** JWT Bearer (`org_id` from token only)  
**Envelope:** `{ success, data, meta? }` / `{ success: false, error }`  
**Legend:** ✅ Live Python · 🟡 Partial · 📋 DB + OpenAPI only · ⬜ Planned / UI stub

> OpenAPI may list paths that are not mounted in `app/main.py`. Prefer this file + `app/main.py` over the full OpenAPI catalog for “what works today.”

---

## 1. Product features

### 1.1 Live (backend + usable flows)

| Feature | What it does | Primary surfaces |
|---------|--------------|------------------|
| **Auth** | Email/phone+password login, Firebase phone login, refresh/logout, `/auth/me` with roles+permissions | API + web `/login` |
| **Users & roles** | Org users CRUD, sessions, self profile, OWNER delete user, self account delete | `/users`, Settings → Users |
| **Legal (Play Store)** | Public privacy + account-deletion info pages | `GET /legal*` |
| **Location masters** | District → Mandal → Village cascade | Master data APIs + Settings → Villages |
| **Village 360°** | First-class village hub: KPIs, farmers, procurement, services, vehicles, payments, finance, farming, buyers, analytics, timeline, GIS stub, reports | `GET …/profile-360` + `/villages` web orbit |
| **Crop & price masters** | Crop types, crop price rules | Settings → Master data |

| **Platform catalogs** | Buyers, field agents, activity types, payment modes, vehicle types | Settings → Master data |
| **Expense categories** | Fuel/ops category catalog | Settings + expenses |
| **Farmers registry** | CRUD, search, status, bilingual names, soft delete (OWNER) | `/farmers` |
| **Farmer 360°** | Relationship hub: summary, stats, timeline, services/farming/proc/finance/ledger, crop intelligence, analytics, recommendations, quick actions | `GET …/profile-360` + web orbit UI |
| **Bank & land** | Encrypted bank accounts; land parcels (+ ownership/irrigation) | Farmer sub-resources |
| **Crop history** | Season/year farming records with optional agronomy fields | Farmer crop-history APIs |
| **Procurement workflow** | Draft → submit → weighment → apply-price → confirm / cancel / reverse; deductions; buyer + payment terms | `/procurements*` + web detail |
| **Farmer ledger** | Immutable debit/credit with running balance (partitioned) | Written on confirm/payment; `…/ledger`, `…/outstanding` |
| **Farmer payments** | Record payment, allocate to procurements, reverse | `/farmer-payments*` + `/payments` UI |
| **Field services** | Tractor/transport/fertiliser/seeds/agri-finance/vehicle/godown ops; diesel → Fuel expense | `/field-services*` |
| **Assets / fleet** | Asset CRUD (tractor, bolero, DCM, implements, etc.) | `/assets` + `/vehicles` UI |
| **Vehicle trips** | Trip CRUD; `fuel_cost` → Fuel expense | `/vehicle-trips` |
| **Farms (thin)** | Own-farm CRUD + activities | `/farms*` (UI placeholder-ish) |
| **Expenses** | CRUD; source link from diesel (trip / field service) | `/expenses` |
| **Collections** | List/create/get cash collections | `/collections` |
| **Documents** | S3 presign upload, create, list (by entity), download URL, polymorphic link | `/documents*` |
| **Comments & tags** | Polymorphic notes/tags on entities (farmer, procurement, field service, …) | `/comments`, `/tags` |
| **Devices / FCM** | Register/unregister push tokens | `/devices/push-tokens` |
| **Audit & activity** | Audit log + activity feed | `/audit-logs`, `/activity-feed` |
| **Dashboard** | Health, summary KPIs, reports catalog metadata | `/health`, `/dashboard/*`, `/reports` UI |
| **RBAC** | Roles OWNER / MANAGER / SUPERVISOR / DRIVER / AGENT / FARMER (+ soft domain perms) | JWT + `require_permission` |
| **Bilingual EN/TE** | `*_te` columns, Accept-Language patterns | Across masters & farmers |
| **Multi-tenancy** | All business rows scoped by `org_id` | Every module |

### 1.2 Partial / thin

| Feature | Status |
|---------|--------|
| Documents OCR | OpenAPI stubs; no full OCR pipeline in Python |
| Farms UI | API thin CRUD; own-farming UX incomplete |
| Dashboard analytics | Summary + report registry; period KPI APIs pending |
| General `/payments` (non-farmer) | OpenAPI; not the farmer-payment module |
| Asset maintenance / usage logs | Tables exist; dedicated APIs not fully live |

### 1.3 Schema ready, Python not mounted

| Feature | Migration | Notes |
|---------|-----------|-------|
| Workers + skills | `005` | OpenAPI `workers` |
| Work orders + attendance | `009` | OpenAPI `work-orders`, `attendance` |
| Rentals (customers/agreements) | `011` | OpenAPI `rental-*` |
| Financial transactions / general payments | `012` | Expenses/collections live; full GL posting incomplete |
| WhatsApp / AI jobs / suggestions / voice | `014` | Tables only |
| Global search | — | OpenAPI `/search` only |

### 1.4 Web app screens (`frontend/`)

| Route | Status |
|-------|--------|
| `/dashboard` | ✅ summary cards |
| `/farmers`, `/farmers/new`, `/farmers/[id]` | ✅ list/create + **360° orbit profile** |
| `/villages`, `/villages/[id]` | ✅ list/search + **Village 360° orbit** |
| `/procurement`, `/new`, `/[id]` | ✅ list/create + workflow actions |
| `/field-services`, `/new`, `/[id]` | ✅ |
| `/payments` | ✅ farmer payments + allocate/reverse |
| `/expenses`, `/collections` | ✅ / 🟡 |
| `/vehicles` | ✅ types + assets |
| `/reports` | ✅ registry |
| `/farms`, `/workers` | ⬜ placeholders |
| `/settings`, `/settings/users`, `/settings/villages` | ✅ |
| `/settings/master-data/*` | ✅ catalogs |
| `/login` | ✅ phone or email + password |

Android parity is tracked separately in `docs/modules/ANDROID_CRM_PARITY.md` (external mobile repo).

---

## 2. Live APIs (mounted in `app/main.py`)

All paths below are under **`/api/v1`**.

### Auth — `/auth`

| Method | Path |
|--------|------|
| POST | `/auth/login` |
| POST | `/auth/firebase-login` |
| POST | `/auth/refresh` |
| POST | `/auth/logout` |
| GET | `/auth/me` |

### Legal (public)

| Method | Path |
|--------|------|
| GET | `/legal` |
| GET | `/legal/privacy` |
| GET | `/legal/account-deletion` |

### Users & roles

| Method | Path |
|--------|------|
| GET/PATCH/DELETE | `/users/me` |
| GET | `/users/me/sessions` |
| DELETE | `/users/me/sessions/{session_id}` |
| GET/POST | `/users` |
| PATCH/DELETE | `/users/{user_id}` |
| GET | `/roles` |

### Location & master data

| Method | Path |
|--------|------|
| CRUD | `/districts`, `/districts/{id}` |
| CRUD | `/mandals`, `/mandals/{id}` |
| CRUD | `/villages`, `/villages/{id}` |
| GET | `/villages/search?q=` |
| GET | `/villages/{id}/profile-360` |
| CRUD | `/crop-types`, `/crop-types/{id}` |
| CRUD | `/expense-categories`, `/expense-categories/{id}` |

### Platform catalogs & notes

| Method | Path |
|--------|------|
| CRUD | `/activity-types`, `/payment-modes`, `/buyers`, `/agents`, `/vehicle-types`, `/crop-prices` |
| GET/POST | `/comments` |
| GET/POST | `/tags` |
| DELETE | `/tags/{tag_id}` |

### Farmers

| Method | Path |
|--------|------|
| GET/POST | `/farmers` |
| GET/PATCH/DELETE | `/farmers/{farmer_id}` |
| GET | `/farmers/{farmer_id}/profile-360` |
| GET | `/farmers/{farmer_id}/outstanding` |
| GET | `/farmers/{farmer_id}/ledger` |
| GET/POST | `/farmers/{farmer_id}/crop-history` |
| CRUD | `/farmers/{farmer_id}/bank-accounts[/{account_id}]` |
| CRUD | `/farmers/{farmer_id}/land-parcels[/{parcel_id}]` |

### Field services

| Method | Path |
|--------|------|
| GET/POST | `/field-services` |
| GET/PATCH/DELETE | `/field-services/{record_id}` |

### Farms

| Method | Path |
|--------|------|
| CRUD | `/farms`, `/farms/{farm_id}` |
| CRUD | `/farms/{farm_id}/activities[/{activity_id}]` |

### Procurements

| Method | Path |
|--------|------|
| GET/POST | `/procurements` |
| GET/PATCH | `/procurements/{procurement_id}` |
| POST | `…/submit`, `…/weighment`, `…/apply-price`, `…/confirm`, `…/cancel`, `…/reverse` |
| POST | `…/deductions` |

### Farmer payments

| Method | Path |
|--------|------|
| GET/POST | `/farmer-payments` |
| GET | `/farmer-payments/{payment_id}` |
| POST | `…/allocate`, `…/reverse` |

### Assets & trips

| Method | Path |
|--------|------|
| CRUD | `/assets`, `/assets/{asset_id}` |
| GET/POST | `/vehicle-trips` |
| GET/PATCH | `/vehicle-trips/{trip_id}` |

### Finance

| Method | Path |
|--------|------|
| CRUD | `/expenses`, `/expenses/{expense_id}` |
| GET/POST | `/collections` |
| GET | `/collections/{collection_id}` |

### Documents

| Method | Path |
|--------|------|
| POST | `/documents/presign-upload` |
| GET/POST | `/documents` |
| GET | `/documents/{document_id}` |
| GET | `/documents/{document_id}/download-url` |
| POST | `/documents/{document_id}/link` |

### Devices, audit, dashboard

| Method | Path |
|--------|------|
| POST/DELETE | `/devices/push-tokens` |
| GET | `/audit-logs` |
| GET | `/activity-feed` |
| GET | `/health` |
| GET | `/dashboard/summary` |
| GET | `/dashboard/reports` |

### OpenAPI-only (not mounted)

Workers, work-orders, attendance, rental-*, general `/payments`, document OCR verify, `/search`, asset maintenance/usage sub-routes (as specified in OpenAPI but without Python routers in `main.py`).

---

## 3. Database

**Engine:** PostgreSQL (local Docker or Supabase)  
**Migrations:** Alembic `202506210001` → `202506210030`  
**Conventions:** `org_id` on business tables · soft delete `deleted_at` · money `NUMERIC(14,2)` · monthly partitions on high-volume fact tables

### 3.1 Migration map

| Rev | Area |
|-----|------|
| 001 | organizations, users, roles, permissions, villages, crop_types, expense_categories, documents, audit |
| 002 | extensions, Telugu, scopes, triggers |
| 003 | activity_types, payment_modes, number_sequences |
| 004 | farmers, farmer_bank_accounts, farmer_land_parcels, farmer_crop_history |
| 005 | workers, worker_skills |
| 006 | farms, farm_activities |
| 007 | document enhancements / OCR columns |
| 008 | procurements (+ partitions), deductions, farmer_ledger_entries, farmer_payments, allocations |
| 009 | work_orders, attendance, photos |
| 010 | assets, maintenance, usage_logs, vehicle_trips |
| 011 | rental_customers, rental_agreements |
| 012 | financial_transactions, expenses, collections, payments |
| 013 | sync / schema log / audit indexes |
| 014 | whatsapp_messages, ai_jobs, ai_suggestions, OCR/voice/summaries |
| 015 | seed permissions & system roles |
| 016 | Firebase auth columns on users |
| 017 | entity_comments, entity_tags, accountability |
| 018–029 | RBAC grants, field services, districts/mandals, fleet fields, procurement terms, expense source, payment_modes RBAC, field-ops comment/doc RBAC |
| 030 | Farmer 360 columns (prefs, trust, VIP, GPS; land/crop detail) |
| 031 | Village 360 columns (code, GPS, agent, status, population, cultivable area, notes) |

### 3.2 Core tables by domain

| Domain | Tables | Live ORM |
|--------|--------|----------|
| **IAM** | `organizations`, `users`, `roles`, `permissions`, `role_permissions`, `refresh_tokens` | ✅ |
| **Location** | `districts`, `mandals`, `villages` | ✅ |
| **Masters** | `crop_types`, `expense_categories`, `activity_types`, `payment_modes`, `buyers`, `field_agents`, `vehicle_types`, `crop_price_rules` | ✅ |
| **Farmers** | `farmers`, `farmer_bank_accounts`, `farmer_land_parcels`, `farmer_crop_history` | ✅ |
| **Procurement** | `procurements`*, `procurement_deductions`, `farmer_ledger_entries`*, `farmer_payments`*, `farmer_payment_allocations` | ✅ |
| **Field ops** | `field_service_records`, `farms`, `farm_activities` | ✅ |
| **Fleet** | `assets`, `vehicle_trips` (+ maintenance/usage tables) | ✅ assets/trips; maint/usage 📋 |
| **Finance** | `expenses`, `collections` (+ `financial_transactions`, `payments`) | ✅ expenses/collections; GL 📋 |
| **Docs / notes** | `documents`, `document_links`, `entity_comments`, `entity_tags` | ✅ |
| **Devices / audit** | `user_device_tokens`, `audit_logs`, `activity_feed` | ✅ |
| **Workforce** | `workers`, `worker_skills`, `work_orders`, `attendance`, … | 📋 |
| **Rentals** | `rental_customers`, `rental_agreements` | 📋 |
| **AI** | `whatsapp_messages`, `ai_jobs`, `ai_suggestions`, … | 📋 |

\*Partitioned by date (monthly).

### 3.3 Farmer 360 columns (migration 030)

**`farmers` (optional):** `preferred_language`, `preferred_payment_cycle`, `preferred_payment_method`, `trust_rating`, `is_vip`, `geo_lat`, `geo_lng`

**`farmer_land_parcels` (optional):** `ownership`, `irrigation_type`, `water_source`, `soil_type`, `village_name`

**`farmer_crop_history` (optional):** survey, seed/fertilizer/pesticides, stage, yields, market, price, harvest_date, GPS

---

## 4. Cross-cutting platform

| Concern | Implementation |
|---------|----------------|
| Config | `app/core/config.py` + `.env` |
| Cache | none / memory / redis (`app/core/cache/`) |
| Crypto | Bank account encrypt/mask (`app/shared/crypto`) |
| S3 | Presigned uploads (`app/shared/services/s3`) |
| Audit helper | `write_audit_log` / `write_activity_feed` |
| Permissions seed | `app/shared/permissions.py` + Alembic `015+` |
| Deploy | Docker Compose + GitHub Actions → EC2 on merge to `main` |
| Frontend | Next.js 15 on Vercel (`frontend/`) |
| Spec | `docs/api/openapi.yaml` (+ path/schema fragments) |

---

## 5. Roles (system)

| Code | Typical access |
|------|----------------|
| **OWNER** | Full admin including deletes |
| **MANAGER** | Ops + finance + masters (no user create / farmer delete) |
| **SUPERVISOR** | Field / farming ops |
| **DRIVER** | Fleet / vehicle supervisor (assets + field services write) |
| **AGENT** | Field agent (scoped ops; comments/docs for receipts) |
| **FARMER** | Read-oriented + comments create |

Exact grants: `app/shared/permissions.py` and migrations `015`–`029`.

---

## 6. Quick start pointers

```bash
# API
docker compose -f infra/docker-compose.yml up -d --build
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
docker compose -f infra/docker-compose.yml exec api python scripts/seed.py

# Web
cd frontend && npm install && npm run dev
```

Default seed login: `owner@krishifarms.local` / `ChangeMe123!`

---

## 7. Related docs

| Doc | Purpose |
|-----|---------|
| [AGENTS.md](../AGENTS.md) | Agent quick start |
| [AGENT_GUIDE.md](./AGENT_GUIDE.md) | Status matrix + playbooks |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Topology / AWS |
| [api/API_CONTRACT.md](./api/API_CONTRACT.md) | REST standards |
| [modules/FARMERS.md](./modules/FARMERS.md) | Farmer + 360 design |
| [modules/VILLAGES.md](./modules/VILLAGES.md) | Village 360 design |
| [modules/ANDROID_CRM_PARITY.md](./modules/ANDROID_CRM_PARITY.md) | Mobile parity |
| [CHANGELOG.md](./CHANGELOG.md) | What changed |
| [alembic/versions/README.md](../alembic/versions/README.md) | Migration order |
