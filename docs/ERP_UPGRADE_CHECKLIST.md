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
| **P0** | Procurement web workflow (submit → weighment → price → confirm) | **Done (web + Android)** — web + Android full actions including cancel/reverse |
| **P0** | Farmer payments / ledger settlement | **Done (web)** — API allocate/reverse + `/payments` list/create + allocate/reverse settlement UI with procurement status chips |
| **P0** | Phone-first login + OTP UI | **Partial** — web phone-or-email password login + **API mandatory phone** on user create/update (10+ digits); Firebase OTP stub + [FIREBASE_OTP.md](./modules/FIREBASE_OTP.md); full web OTP still TODO |
| **P0** | District → Mandal → Village cascaded dropdowns | **Done (web + Android)** — web `LocationCascade`; Android procurement + farmer form |
| **P0** | Individual vehicle/asset registry + trips/diesel | **Partial** — assets CRUD + **`/vehicle-trips`** + diesel→Fuel expense posting (`027`); trip UI still thin |
| **P0** | Android field-service + procurement workflow parity | **Done** — field-services list/create + `[kf:work]` vehicle profiles; procurement submit→confirm + cancel/reverse |

---

## Full requirements checklist

| Requirement | Status | Evidence | Next action |
|-------------|--------|----------|-------------|
| **Business units:** tractor/cultivator/rotavator/baler/trolley/weeder/pump/Bolero/DCM | **Partial** | Fleet seeds + assets + `/vehicle-trips` + diesel expense link | Wire asset picker on field services; trip UI |
| **Business units:** finance | **Partial** | Expenses + collections CRUD (`app/modules/financial/`); migration `027` source link; web `/payments` farmer settlement; web expenses/collections still placeholders | Wire expenses/collections UI; general `/payments` + financial_transactions |
| **Business units:** seeds | **Partial** | `field_service_records.service_category=seeds`; seeds activity types in `scripts/data/fleet_inventory.py` | Inventory/stock tracking if required beyond service records |
| **Business units:** fertilizer | **Partial** | `service_category=fertiliser`; activity types `FERT_*` in fleet seed | Same as seeds — confirm if inventory module needed |
| **Business units:** procurement | **Done (web + Android)** | Full backend + web/Android workflow incl. cancel/reverse; `buyer_id`/terms (`026`); entity document gallery | Optional deductions polish; Android photo attach |
| **Business units:** own farming | **Partial** | Thin API `app/modules/farms/` (CRUD + activities); web placeholder | Own-farming UI |
| **Roles:** Admin | **Done** | `OWNER` display “Admin / Owner” in `ROLE_DEFINITIONS` + migration `024` | — |
| **Roles:** Manager | **Done** | `MANAGER` in `app/shared/permissions.py`, migration `018`/`024` delete restrictions | — |
| **Roles:** Vehicle Supervisor | **Done** | `DRIVER` + `transport:*` / `assets:*`; trips API + auto diesel expense | Trip UI |
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
| **Procurement:** status workflow | **Done** | Web + Android submit/weigh/price/confirm/cancel/reverse | Deductions UI optional |
| **Farming module fields** | **Partial** | Thin API `app/modules/farms/` against migration `006`; no web UI yet | Own-farming UI |
| **Vehicle service module + vehicle-type-specific questions** | **Done (web + Android create)** | Web + Android: Tractor+implements/Harvester, Trolley, Bolero, DCM, Pump, Drone (`[kf:work]`); not first-class schema fields | Optional first-class JSON/columns |
| **Diesel tracking** | **Partial** | Field-service `diesel_amount` + trip fuel + auto Fuel expense (`source_type=vehicle_trip`) | Richer diesel ledger UI |
| **Finance module** | **Partial** | Expenses CRUD + collections list/create/get; `027` RBAC; no `financial_transactions` posting yet | Approval workflows; general payments; web UI |
| **Payments (farmer settlement)** | **Done (web)** | API + `/payments` list/create/allocate/reverse; settlement status chips for `paid_*` / `confirmed` | Android payments parity |
| **Comments timeline** | **Partial** | API + web `CommentThread` on procurement/farmer/field-service detail | Unified activity timeline merging comments + audit + status changes |
| **Audit trail** | **Partial** | API: `app/modules/audit/router.py` (`/audit-logs`, `/activity-feed`); no web UI | Admin audit viewer; surface on entity detail pages |
| **Role dashboards** | **Partial** | Home + Reports wire `/dashboard/summary` ops counts + role welcome hints; admin shortcut grid | Role-specific KPI widgets executing `docs/reporting/sql/` |
| **Android parity** | **Partial** | Field services + `[kf:work]` + farmer village_id + procurement full workflow; expenses/collections API ready for sync | Payments Android; wire expenses client |
| **Reports list** | **Partial** | Web `/reports` registry (8 ERP types) + `GET /dashboard/reports` catalog + extended `/dashboard/summary` KPIs; SQL still in `docs/reporting/sql/` | Period KPI endpoints (procurement/village/crop, outstanding, diesel rollup, vehicle earnings, supervisor productivity) |

---

## Summary by layer

| Layer | Done | Partial | Missing |
|-------|------|---------|---------|
| **Backend API** | Auth, masters, buyers, farmers, procurement (+ buyer/terms `026`), field services, assets, vehicle trips (+ diesel expense), farms thin, farmer payments allocate/reverse, **expenses/collections**, documents entity filter, comments, audit, RBAC (`024`/`025`/`027`) | Dashboard KPIs; docs OCR/archive beyond thin API; no financial_transactions posting | General payments, WhatsApp |
| **Frontend web** | Admin CRUD, farmers, location cascade, procurement workflow + doc gallery, field services, vehicles/assets, phone-or-email login, farmer-payments list/create/**allocate/reverse**, comments, dashboard, **reports registry** | Finance placeholders; OTP stub | Farms/trips UI, audit; full Firebase Web OTP; runnable report charts |
| **Android** | Admin, farmers (`village_id`), field-services list/create + `[kf:work]`, procurement create + full workflow (cancel/reverse) | — | Finance, fleet, payments |
| **Schema** | Broad Phase 1–5; districts/mandals (`023`); procurement buyer/terms (`026`); expenses source link (`027`) | Transport on ticket; village dual text+FK | — |

---

## Recommended implementation order

1. ~~**Web farmer-payment allocate/reverse UI**~~ — **Done** (`/payments` settlement dialogs)  
2. ~~**Android cancel/reverse + richer field-service questions**~~ — **Done**  
3. ~~**Phase 3 finance APIs** (expenses, collections)~~ — **Done** (CRUD; general `/payments` + ledger posting still open)  
4. ~~**Diesel expense posting from vehicle trips**~~ — **Done** (`fuel_cost` → Fuel expense, `source_type=vehicle_trip`)  
5. **Reports UI** — registry + summary KPIs shipped; still need period KPI APIs over `docs/reporting/sql/`  
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
| Farmer payments web settlement UI | `frontend/src/features/farmer-payments/settlement-actions.tsx` + `/payments` Actions column |
| Vehicle trips thin API | `app/modules/assets/vehicle_trip_*.py`; `transport:*`; mounted in `app/main.py` |
| Farms thin API | `app/modules/farms/`; migration `006` |
| Procurement buyer/terms (`026`) | `alembic/versions/202506210026_procurement_buyer_payment_terms.py`; wired in models/schemas/service/OpenAPI |
| Documents list-by-entity | `GET /documents?entity_type=&entity_id=` → `document_links` join; `tests/test_documents.py` |
| Staff phone mandatory (API) | `UserCreateRequest.phone` required; update rejects clear/short; `tests/test_users_schemas.py` |
| Procurement backend + web workflow UI | `app/modules/procurements/`; frontend detail workflow actions |
| Field services backend + expanded vehicle profiles | `app/modules/field_services/`; frontend work profiles |
| Android field-services list/create + farmer village_id + procurement workflow | External `krishifarms-mobile` — `ANDROID_CRM_PARITY.md` |
| Android procurement cancel/reverse + `[kf:work]` vehicle profiles | External `krishifarms-mobile` — detail cancel/reverse; field-service create work questions |
| Crop / fleet master seeds | `scripts/data/crop_catalog.py`, `scripts/data/fleet_inventory.py` |
| Reports registry UI + thin dashboard APIs | `/reports` page; `GET /dashboard/summary` ops counts; `GET /dashboard/reports` catalog; `docs/api/paths/dashboard.yaml` |

### Needs manual verification

| Item | How to verify |
|------|----------------|
| Web owner vs manager delete visibility | Login `owner@krishifarms.local` vs MANAGER; catalog delete buttons hidden for manager |
| Phone-or-email web login | `/login` — use phone digits or email + password; OTP button disabled |
| Location cascade on web forms | Settings villages / farmer / procurement / field-service — confirm cascade (no free-text district/mandal) |
| Procurement web workflow buttons | Detail: submit → weighment → apply-price → confirm / cancel |
| Assets list on `/vehicles` | Live vehicle-types chips + asset instances after seed |
| Farmer payments create | `POST /farmer-payments` + ledger credit |
| Farmer payments allocate / reverse (web) | `/payments` → Allocate (select procurements + amounts) / Reverse (reason); confirm chips show `paid_partial` / `paid_full` / `confirmed` |
| Procurement draft extras round-trip | Create with buyer/terms/moisture; confirm notes contain `[kf:proc]` JSON |
| Field-service vehicle-type questions | Web + Android create Tractor/Trolley/Bolero/DCM; comments `[kf:work]` |
| Android procurement create | Buyer, terms, moisture, cascade; sync draft to API |
| Android procurement cancel/reverse | Detail: Cancel (draft/weighment/weighed) + Reverse (confirmed, OWNER) |
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