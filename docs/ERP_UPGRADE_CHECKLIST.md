# ERP Upgrade Checklist

**Ralph Loop 1 — Gap Analysis** · **Ralph Loop 2 — Phone auth + assets foundation** · **Ralph Loop 2 final — Backend + Frontend/Android closeout**  
**Baseline date:** 2026-07-12  
**Repo:** KrishiFarms CRM (`app/`, `frontend/`, `docs/`; Android in external `krishifarms-mobile`)

**Baseline:** Backend Phase 1–2b live in `app/main.py` (auth, users, villages/crops, platform catalogs, farmers, procurements, field services, **assets CRUD**, documents + entity list filter, audit, dashboard counts, financial expense-categories). Phase 3–5 tables exist in Alembic; many lack full Python routers/UI. Android lives in external repo `krishifarms-mobile` (documented in `docs/modules/ANDROID_CRM_PARITY.md`).

Status legend: **Done** | **Partial** | **Missing**

---

## P0 blockers (daily field ops)

| Priority | Gap | Impact |
|----------|-----|--------|
| **P0** | Procurement web workflow (submit → weighment → price → confirm) | **Done (web + Android)** — web full actions; Android submit/weigh/price/confirm when synced; cancel/reverse Android still web-only |
| **P0** | Farmer payments / ledger settlement | **Partial** — API allocate/reverse live; web thin list/create on `/payments`; allocate UI deferred |
| **P0** | Phone-first login + OTP UI | **Partial** — web phone-or-email password login + **API mandatory phone** on user create/update (10+ digits); Firebase OTP stub + [FIREBASE_OTP.md](./modules/FIREBASE_OTP.md); full web OTP still TODO |
| **P0** | District → Mandal → Village cascaded dropdowns | **Done (web + Android)** — web `LocationCascade`; Android procurement + farmer form |
| **P0** | Individual vehicle/asset registry + trips/diesel | **Partial** — assets CRUD + **`/vehicle-trips` API**; diesel primarily via field services; expense posting deferred |
| **P0** | Android field-service + procurement workflow parity | **Partial** — field-services list/create live; procurement workflow on synced tickets; cancel/reverse + rich vehicle questions still open |

---

## Full requirements checklist

| Requirement | Status | Evidence | Next action |
|-------------|--------|----------|-------------|
| **Business units:** tractor/cultivator/rotavator/baler/trolley/weeder/pump/Bolero/DCM | **Partial** | Fleet seeds + assets + `/vehicle-trips`; field-service categories | Wire asset picker on field services; diesel expense posting |
| **Business units:** finance | **Missing** | `alembic/versions/202506210012_financial_core.py`; `app/modules/financial/` (expense-categories only); web `/payments` thin farmer-payments; placeholders expenses/collections | Expenses/collections routers + allocate UI |
| **Business units:** seeds | **Partial** | `field_service_records.service_category=seeds`; seeds activity types in `scripts/data/fleet_inventory.py` | Inventory/stock tracking if required beyond service records |
| **Business units:** fertilizer | **Partial** | `service_category=fertiliser`; activity types `FERT_*` in fleet seed | Same as seeds — confirm if inventory module needed |
| **Business units:** procurement | **Done (web)** | Full backend + web workflow; `buyer_id`/terms (`026`); entity document gallery | Android cancel/reverse; optional deductions polish |
| **Business units:** own farming | **Partial** | Thin API `app/modules/farms/` (CRUD + activities); web placeholder | Own-farming UI |
| **Roles:** Admin | **Done** | `OWNER` display “Admin / Owner” in `ROLE_DEFINITIONS` + migration `024` | — |
| **Roles:** Manager | **Done** | `MANAGER` in `app/shared/permissions.py`, migration `018`/`024` delete restrictions | — |
| **Roles:** Vehicle Supervisor | **Done** | `DRIVER` + `transport:*` / `assets:*`; trips API live | Trip UI / diesel expense posting |
| **Roles:** Farming Supervisor | **Done** | `SUPERVISOR` code; display “Farming Supervisor”; `farming:*` + field ops in `permissions.py` | — |
| **Roles:** Agent | **Done** | `AGENT` + location/farmer/field-service perms in `permissions.py` + `024` | Expand if ERP needs procurement create |
| **Roles:** Farmer (login) | **Done** | `FARMER` in `ROLE_DEFINITIONS` / `ROLE_PERMISSIONS` (read-only) + mobile `_FARMER`; migration `024` seeds role | Portal login UX still future |
| **Roles:** Permissions matrix | **Done** | Runtime `app/shared/permissions.py` aligned with `024`/`025`; matrix in [ADMIN_PLATFORM.md](./modules/ADMIN_PLATFORM.md); `ACCOUNTANT` mobile-only | Optional: seed ACCOUNTANT in DB |
| **Auth:** phone mandatory | **Done (API + web form)** | Backend `UserCreateRequest.phone` required (10+ digits, normalized); update rejects clear/short; web Settings → Users requires phone; `/login` phone-or-email password | Historical null phones allowed until PATCH; Android create parity; full OTP still TODO |
| **Auth:** password | **Done** | `POST /auth/login` (`app/modules/auth/router.py`), bcrypt in `app/core/security.py`; web + mobile identifier | — |
| **Auth:** OTP-ready | **Partial** | `POST /auth/firebase-login`, `firebase.py`, `phone.py`; web stub + [FIREBASE_OTP.md](./modules/FIREBASE_OTP.md) | Wire Firebase Web SDK OTP → `firebase-login`; Android OTP UX verify |
| **Auth:** WhatsApp (future) | **Missing** | Schema only: `alembic/versions/202506210014_ai_support_tables.py` (`whatsapp_messages`); `docs/modules/DOCUMENT_MANAGEMENT.md` P2 note | Implement inbound pipeline when prioritized |
| **Location masters:** District → Mandal → Village (dropdown only) | **Done** | Migration `023`; live APIs; web + Android cascade on farmer / procurement / field-service | — |
| **Location masters:** Rangareddy preload | **Done** | `scripts/data/rangareddy_service_villages.py` + idempotent `scripts/seed_locations.py` (hooked from `seed.py`) | — |
| **Vehicle master + types (Tractor → Drone)** | **Partial** | Types CRUD + asset instances: `/vehicle-types`, `/assets` (`025`), seeds in `fleet_inventory.py` / `DEFAULT_FLEET_ASSETS`; `/vehicles` UI | Maintenance/usage logs; richer admin create UI |
| **Crop master list** | **Done** | `app/modules/master_data/` `/crop-types`; web `frontend/src/app/(app)/settings/master-data/crops/page.tsx` | — |
| **Buyer master** | **Done** | `app/modules/platform/models.py` (`Buyer`); `/buyers` API; web `frontend/src/app/(app)/settings/master-data/buyers/page.tsx` | — |
| **Buyer inline add from procurement** | **Done** | Web searchable buyer + inline Add; `buyer_id` FK on `procurements` (migration `026`) | Optional: true modal create without leaving form polish |
| **Procurement:** moisture | **Partial** | Backend weighment + web weighment dialog + detail display; planned moisture in `[kf:proc]` notes | Optional first-class planned moisture column |
| **Procurement:** payment terms | **Done** | Columns + API (`026`); web create/detail | — |
| **Procurement:** photos | **Done (web)** | Upload + entity gallery via `GET /documents?entity_type=&entity_id=` | Android photo attach optional |
| **Procurement:** transport | **Missing** | Transport is separate field-service category, not on procurement ticket | Add transport fields or link to field service / trip |
| **Procurement:** status workflow | **Done** | Web full; Android submit/weigh/price/confirm (cancel/reverse web) | Deductions UI optional |
| **Farming module fields** | **Partial** | Thin API `app/modules/farms/` against migration `006`; no web UI yet | Own-farming UI |
| **Vehicle service module + vehicle-type-specific questions** | **Partial** | Web: Tractor+implements/Harvester, Trolley, Bolero, DCM, Pump, Drone (`[kf:work]`); not first-class schema fields | Persist type-specific fields in structured JSON/columns |
| **Diesel tracking** | **Partial** | Field-service `diesel_amount` + `/vehicle-trips` fuel liters/cost | Expense posting from trips; richer diesel ledger UI |
| **Finance module** | **Missing** | Tables in migration `012`; `app/modules/financial/` = expense-categories catalog only; web placeholders for expenses/payments/collections | Phase 3 Python routers + approval workflows |
| **Payments (farmer settlement)** | **Partial** | API + web list/create on `/payments`; allocate/reverse API live | Web allocate UI |
| **Comments timeline** | **Partial** | API + web `CommentThread` on procurement/farmer/field-service detail | Unified activity timeline merging comments + audit + status changes |
| **Audit trail** | **Partial** | API: `app/modules/audit/router.py` (`/audit-logs`, `/activity-feed`); no web UI | Admin audit viewer; surface on entity detail pages |
| **Role dashboards** | **Partial** | Home wires `/dashboard/summary` counts + role welcome hints; admin shortcut grid | Role-specific KPI widgets using `docs/reporting/sql/` |
| **Android parity** | **Partial** | Field services + farmer village_id + procurement workflow done; finance/fleet stubs | Cancel/reverse; payments Android; expenses API |
| **Reports list** | **Partial** | SQL dashboards documented: `docs/reporting/REPORTING_ARCHITECTURE.md`, `docs/reporting/sql/*.sql`; web `frontend/src/app/(app)/reports/page.tsx` placeholder; no report API endpoints | Report registry UI + `/dashboard/*` or dedicated report routes |

---

## Summary by layer

| Layer | Done | Partial | Missing |
|-------|------|---------|---------|
| **Backend API** | Auth, masters, buyers, farmers, procurement (+ buyer/terms `026`), field services, assets, vehicle trips, farms thin, farmer payments allocate/reverse, documents entity filter, comments, audit, RBAC (`024`/`025`) | Dashboard KPIs, expense-categories; docs OCR/archive beyond thin API | Finance ops, WhatsApp |
| **Frontend web** | Admin CRUD, farmers, location cascade, procurement workflow + doc gallery, field services, vehicles/assets, phone-or-email login, farmer-payments list/create, comments, dashboard | Finance placeholders; OTP stub | Farms/trips UI, allocate UI, reports, audit; full Firebase Web OTP |
| **Android** | Admin, farmers (`village_id`), field-services list/create, procurement create + workflow | Cancel/reverse | Finance, fleet, payments |
| **Schema** | Broad Phase 1–5; districts/mandals (`023`); procurement buyer/terms (`026`) | Transport on ticket; village dual text+FK | — |

---

## Recommended implementation order

1. **Web farmer-payment allocate/reverse UI** — APIs live; thin create shipped  
2. **Android cancel/reverse + richer field-service questions**  
3. **Phase 3 finance APIs** (expenses, collections) for Android sync  
4. **Diesel expense posting from vehicle trips**  
5. **Reports UI** wired to existing SQL dashboards  
6. Optional: seed `ACCOUNTANT` role in DB (mobile catalog already has it)

---

## Related docs

- [ANDROID_CRM_PARITY.md](./modules/ANDROID_CRM_PARITY.md)
- [FIREBASE_OTP.md](./modules/FIREBASE_OTP.md)
- [AGENT_GUIDE.md](./AGENT_GUIDE.md)
- [REPORTING_ARCHITECTURE.md](./reporting/REPORTING_ARCHITECTURE.md)
- [PRODUCT_ROADMAP.md](./PRODUCT_ROADMAP.md)

---

## QA status board (Ralph Loop — Android + QA)

### Completed (with evidence)

| Item | Evidence |
|------|----------|
| Location hierarchy APIs (District → Mandal → Village) | `alembic/versions/202506210023_location_hierarchy.py`; `app/modules/master_data/router.py` |
| Frontend location cascade | `frontend/src/features/master-data/` cascade helpers; wired on villages / farmer / procurement / field-service forms |
| Rangareddy location seed data | `scripts/data/rangareddy_service_villages.py`; `scripts/seed_locations.py` |
| RBAC role codes + display names | `app/shared/permissions.py`; migration `024`; `docs/modules/ADMIN_PLATFORM.md` |
| Mobile RBAC catalog (field services module) | `app/modules/auth/permission_catalog.py`; `tests/test_auth_rbac.py`, `tests/test_role_definitions.py` |
| Assets CRUD + DRIVER fleet perms | `app/modules/assets/`; migration `025`; `permissions.py` DRIVER `assets:*` |
| Phone-first web login + mandatory user phone | `frontend/src/app/login/page.tsx`; Settings → Users; API `UserCreateRequest.phone` required; `docs/modules/FIREBASE_OTP.md` |
| Farmer payments thin API | `app/modules/farmer_payments/`; `tests/test_farmer_payments.py` |
| Farmer payments allocate/reverse → `paid_*` | `app/modules/farmer_payments/service.py` allocate/reverse; OpenAPI `paths/payments.yaml`; status sync tests in `tests/test_farmer_payments.py` |
| Vehicle trips thin API | `app/modules/assets/vehicle_trip_*.py`; `transport:*`; mounted in `app/main.py` |
| Farms thin API | `app/modules/farms/`; migration `006` |
| Procurement buyer/terms (`026`) | `alembic/versions/202506210026_procurement_buyer_payment_terms.py`; wired in models/schemas/service/OpenAPI |
| Documents list-by-entity | `GET /documents?entity_type=&entity_id=` → `document_links` join; `tests/test_documents.py` |
| Staff phone mandatory (API) | `UserCreateRequest.phone` required; update rejects clear/short; `tests/test_users_schemas.py` |
| Procurement backend + web workflow UI | `app/modules/procurements/`; frontend detail workflow actions |
| Field services backend + expanded vehicle profiles | `app/modules/field_services/`; frontend work profiles |
| Android field-services list/create + farmer village_id + procurement workflow | External `krishifarms-mobile` — `ANDROID_CRM_PARITY.md` |
| Crop / fleet master seeds | `scripts/data/crop_catalog.py`, `scripts/data/fleet_inventory.py` |

### Needs manual verification

| Item | How to verify |
|------|----------------|
| Web owner vs manager delete visibility | Login `owner@krishifarms.local` vs MANAGER; catalog delete buttons hidden for manager |
| Phone-or-email web login | `/login` — use phone digits or email + password; OTP button disabled |
| Location cascade on web forms | Settings villages / farmer / procurement / field-service — confirm cascade (no free-text district/mandal) |
| Procurement web workflow buttons | Detail: submit → weighment → apply-price → confirm / cancel |
| Assets list on `/vehicles` | Live vehicle-types chips + asset instances after seed |
| Farmer payments create | `POST /farmer-payments` + ledger credit |
| Procurement draft extras round-trip | Create with buyer/terms/moisture; confirm notes contain `[kf:proc]` JSON |
| Field-service vehicle-type questions | Web create Tractor/Trolley/Bolero/DCM; comments `[kf:work]` |
| Android procurement create | Buyer, terms, moisture, cascade; sync draft to API |
| Android AGENT field services list/create | Login as AGENT → More → Field services → list + FAB create |
| Android role labels | Settings shows “Admin / Owner”, “Vehicle Supervisor”, etc. |
| Seeded Rangareddy villages in target env | After `seed.py` / `seed_locations`, `GET /districts` + mandals for Rangareddy |
| RBAC regression suite | `pytest tests/test_auth_rbac.py tests/test_role_definitions.py tests/test_farmers_rbac.py -q` |

### Needs external data / config

| Item | Notes |
|------|-------|
| **Android repo not in CRM workspace** | Implement/release from `krishifarms-mobile` (`StudioProjects`); CRM can only document parity |
| Firebase Phone Auth / OTP | Backend `POST /auth/firebase-login` live; web OTP stub — see [FIREBASE_OTP.md](./modules/FIREBASE_OTP.md); needs Firebase project + `google-services.json` / web config; SMS quota (Blaze) |
| WhatsApp inbound | Schema only (`whatsapp_messages`); provider credentials TBD |
| Secrets / deploy | `.env`, SSM `/krishifarms/dev/*`, Supabase `DATABASE_URL`, FCM server key — never commit |
| Rangareddy data on **production** | Seeded via scripts locally/dev; confirm prod seed/migrate run after deploy |
| `ACCOUNTANT` DB role | Mobile catalog has it; optional Alembic seed in DB |
| Asset instance / trip data | Assets API live (`025`); vehicle trips thin API live (`/vehicle-trips`) |
| Camera / GPS permissions on device | Android runtime permissions; Play policy for location if GPS added |