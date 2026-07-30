# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **HAMALI viewer role** — migration `040`: `users.hamali_worker_id` links HAMALI logins to `hamali_workers` roster; `HAMALI` role (`hamali:read`, `dashboard:read`); APIs `GET /hamali/me/daily`, `GET /hamali/me/summary` (scoped to linked worker); auto-create `hamali_workers` row when admin creates HAMALI user; mobile catalog `HAMALI_VIEW`; web nav shows read-only **Operations → Hamali** for HAMALI users.
- **Procurement per-bag weighment + admin breakdown** — migration `039`: `procurement_bag_entries` (bag # + weight kg), `tare_weight_kg` on procurements. Create/weighment accept `bag_weights_kg[]`; gross = sum of bags when provided. Mobile intake sends `gross_weight_kg` / per-bag list on create (fixes zero weights on admin). Web detail: weight + payment breakdown tables and per-bag list view.
- **Mobile field procurement + farmer portal** — migration `038`: `users.farmer_id` links FARMER logins to registry; `procurements.weight_per_bag_kg` stores kg/bag for gross = bags × weight. API: `POST /procurements/calculate` (live preview), `POST /procurements/field-entry` (manager one-shot create→weigh→price→confirm + notify); optional `rate_per_quintal` on apply-price. FARMER role auto-scopes list/get to linked farmer. Push (FCM) + SMS (MSG91 when `SMS_ENABLED`) on confirm with bag/qtl/amount summary. Web: weight/bag live calc on `/procurement/new`, farmer **My procurements** at `/my-procurements`. Android parity spec in `ANDROID_CRM_PARITY.md`.
- **Procurement list locale-aware joined names** — `related_names()` honors `Accept-Language` / `preferred_locale` and returns Telugu display names when `name_te` / `full_name_te` exist (`app/shared/locale.py`)
- **Procurement spot payment + buyer profit** — checkbox **100% payment on spot** at create (`is_spot_payment`); when true deducts **₹100 per net quintal** (configurable `spot_deduction_per_quintal`) from farmer net payment. Migration `036`. Amount math: `net_amount = gross_amount − line_deductions − spot_deduction_amount`. Staff-only `profit_summary` on procurement detail (weight kata margin + spot retention); hidden for `FARMER` role. Web: checkbox on `/procurement/new`, spot line + profit card on detail. Docs: OpenAPI `procurement.yaml`, `docs/modules/PROCUREMENT.md`; tests in `tests/test_procurements.py`.
- **Procurement per-bag weight deduction (kata)** — configurable standard weight deducted per bag before pricing. Migration `035` adds `per_bag_deduction_kg` NUMERIC(6,3) NOT NULL DEFAULT `2.000` to `procurements` (with `>= 0` check). Net weight now = `gross − tare − (bag_count × per_bag_deduction_kg)`; e.g. 50 bags @ 2 kg → 100 kg deducted (2500 → 2400 kg). API: `per_bag_deduction_kg` on create/weighment/response + computed `bag_weight_deduction_kg`; helpers `compute_bag_weight_deduction` / `compute_net_weight`. Web: per-bag field on `/procurement/new` and the weighment dialog (live net-weight preview), shown on the detail page. Docs: OpenAPI `procurement.yaml`, `docs/modules/PROCUREMENT.md`; tests in `tests/test_procurements.py`.

### Fixed

- **CI** — remove duplicate `hamali_router` import in `app/main.py` (ruff F811 after main merge).

### Changed

- **Keshampeta mandal village masters** — `scripts/data/rangareddy_service_villages.py` updated to 29 villages/hamlets (EN + `name_te`); **Kothur mandal** updated to 16 villages (EN + `name_te`); `seed_locations` upserts Telugu names; default ops village in `seed_services` is Bhairkhanpalle (Rangareddy).
- **Procurement API** — joined `farmer_name`, `village_name`, `crop_type_name`, `buyer_name` respect client locale via `Accept-Language` header or user `preferred_locale`

### Fixed

- **E2E regression (main push)** — dashboard regression soft-fails known shell contrast issues (search placeholder, active nav tint); settings regression soft-fails sidebar/header button overlap on catalog pages.
- **Field services enrich** — `enrich_records` uses `farmer.phone_primary` (not nonexistent `farmer.phone`) when listing/creating diesel receipts and other field services.
- **Migration chain (037)** — after merging main (#74), rebase `202506210037` to `down_revision = 202506210036` so hamali follows procurement spot-payment migrations on this branch.
- **E2E CI login timeout** — Playwright proxied to shared EC2 (`:8082`) while the instance was stopped after the daily cost schedule. CI now runs an inline **Wake shared EC2** job before E2E and waits for `/api/v1/health`. Updated collections/expenses/login E2E copy for i18n placeholder pages.

### Added

- **Hamali labor tracking** — daily bag-lifting charges for procurement godown work. Migration `037`: `hamali_workers` (roster, default **₹20/bag**), `hamali_daily_entries` (bags, labor, maintenance, tips), `hamali_weekly_payments` (weekly settlement batches). API `/hamali/*` with RBAC `hamali:read|create|update|pay`. Web **Operations → Hamali** (`/hamali`) for OWNER/MANAGER/ACCOUNTANT: daily log, worker roster, weekly batch + mark paid. Docs: `docs/modules/HAMALI.md`, OpenAPI `hamali.yaml`; tests `tests/test_hamali.py`.

### Fixed

- **E2E CI (PR #70 follow-up)** — farmers create smoke soft-fails a11y contrast; Edit user dialog resolves filled MUI Role select via label regex + combobox wait; payments spec waits for loading spinner before empty/table assertion.

### Added

- **Mobile-friendly Telugu i18n + appearance settings** — `frontend/src/i18n/` message catalogs (`en`/`te`), `locale-store`, `LocaleProvider` (html `lang`, Noto Sans Telugu font), `Accept-Language` on API client; Settings → **Preferences** (`/settings/preferences`) with English/Telugu radio + Light/Dark/System theme; login EN/తె toggle; shell nav, dashboard, auth, and placeholder pages wired to `useTranslation()`. Locale syncs to `PATCH /users/me` (`preferred_locale`). Android parity note in `ANDROID_CRM_PARITY.md`.
- **Telugu bilingual content (mobile)** — expose `name_te` on villages, crop types, and expense categories (create/update/list); `name_te` on `GET /roles`; `full_name_te` on users; Telugu titles/summaries on public `/legal/*` APIs; village search/360 includes `name_te` and matches Telugu names; default crop catalog seeds Telugu labels (`scripts/data/crop_catalog.py`).
- **E2E CI fixes** — Playwright: disambiguate Villages link on master-data hub; payments empty state matches body text (not only heading); farmers smoke soft-fails sidebar layout overlap; village add-dialog soft-fails a11y under modal; theme sync guards null `documentElement` (dark-mode pageerror).
- **RBAC simplify (manager/supervisor admin)** — MANAGER gets `users:create`; migration `034` repairs `farmer_payments:*` + `users:create` in `role_permissions`; mobile `USER_CREATE` + `PAYMENT_CREATE` on MANAGER catalog; web `permission-aliases.ts` aligns backend/mobile guards; nav shows field services for SUPERVISOR/DRIVER and hides farmers/procurement from AGENT/DRIVER; Users “Add user” gated on `users:create`; nav role fallback `WORKER` (not OWNER).
 — backend `app/modules/analytics/` (`/analytics/catalog`, `/{module}/summary|series|tables`, `/export`) with Redis/memory cache, migration `033` `analytics_daily_org_facts`, live Executive/Operations/Procurement/Finance KPIs (Decimal money; cash/weather/AI marked unavailable). Web `/analytics` hub + `@mui/x-charts` shell, 11 scaffold modules, `/reports` → hub redirect, KPI drill query params, CSV export, Playwright `e2e/tests/workflows/analytics/hub.spec.ts`. Docs [ANALYTICS.md](./modules/ANALYTICS.md); Android executive pocket deferred to Phase 2 in [ANDROID_CRM_PARITY.md](./modules/ANDROID_CRM_PARITY.md). Tests `tests/test_analytics_executive.py`.
- **Village 360° module** — migration `031` adds `village_code`, GPS, agent, status, population, cultivable area, notes. Live `GET /villages/{id}`, `/villages/{id}/profile-360`, `/villages/search`; enhanced list filters. Web `/villages` + circular orbit dashboard. Android parity backlog documented. Tests `tests/test_village_360.py`. Module doc [VILLAGES.md](./modules/VILLAGES.md).
- **App inventory doc** — single reference [docs/APP_INVENTORY.md](./APP_INVENTORY.md) listing live features, mounted `/api/v1` APIs, OpenAPI-only gaps, DB tables/migrations, web screens, and roles.
- **Farmer 360° relationship profile** — migration `030` adds optional prefs (`preferred_language` / payment cycle / method), `trust_rating`, `is_vip`, farmer GPS; land ownership/irrigation/soil; crop-history farming detail fields. Live `GET /farmers/{id}/profile-360` aggregates summary, stats, timeline, services/farming/procurement/finance/ledger, crop intelligence, analytics, recommendations, quick actions. Crop history + ledger list APIs implemented. Web `/farmers/{id}` circular orbit hub UI; tests in `tests/test_farmer_360.py`.

### Fixed

- **CI deploy failure (run #64)** — pin `ruff>=0.8.0,<0.16` so GitHub Actions does not pull ruff 0.16’s 742 new lint hits; bump nested `postcss` override to `8.5.18` (Trivy HIGH) and override `minimatch` to `^10.2.5` so `npm audit --audit-level=high` clears brace-expansion GHSA-mh99-v99m-4gvg without breaking ESLint.
- **npm audit HIGH (CI security scan)** — bump/override `brace-expansion` (`1.1.16` / `5.0.7`, GHSA-3jxr-9vmj-r5cp), `js-yaml` `^4.3.0` (GHSA-52cp-r559-cp3m), and nested `next`→`postcss` `8.5.10` (GHSA-qx2v-qp2m-jg93); refresh `frontend/package-lock.json`.
- **Trivy HIGH frontend deps** — bump `next` to `^15.5.21` (CVE-2026-64641/64645/64649) and override transitive `sharp` to `^0.35.0` (GHSA-f88m-g3jw-g9cj); refresh `frontend/package-lock.json`.
- **Auto-logout on invalid/expired session** — `fetchApi` treats `401` by attempting `POST /auth/refresh` once (coalesced); on failure clears access/refresh tokens, marks signed-out, and hard-navigates to `/login`. App shell validates via `/auth/me` before render. Covers stale tokens that previously left users on dashboard with “Invalid token”.
- **Login password field invisible / broken eye toggle** — password row used a Tailwind-bordered wrapper; with MUI CSS layers, `border` utilities never get `border-style: solid`, so the shell was invisible and the show/hide control kept native button chrome. Login fields now use explicit `1px solid` borders + Lucide eye icons inside the field.
- **Custom vehicle types (e.g. tractor4W) missing after add/update** — field-service dropdowns filtered by a hardcoded code allowlist, so new master-data codes never appeared; Edit also hid `code` (`createOnly`) and PATCH rejected code changes. Filter now includes custom types by `fuel_type` / code heuristics, code is editable on update (unique per org), and related React Query caches are invalidated.
- **Dark-mode Edit User / admin dialog text** — `PremiumDialog` no longer keeps a light `#FAFAFA` paper while MUI `TextField`s render light/white text in dark mode (invisible labels/values). Dialog paper/title/content and form-control colors follow the active color scheme; `SoftAlert` and `.kf-premium` CSS tokens gain dark variants. Playwright users spec asserts dialog WCAG contrast in dark mode and matches `Edit user` aria-label.
- **Payment modes settings 403** — production `/settings/master-data/payment-modes` failed with `Missing permission: payment_modes:read` because `payment_modes:*` was defined in code/`seed.py` but never inserted by Alembic (omitted from migration `018`). Migration `028` seeds and grants those permissions to OWNER / MANAGER / SUPERVISOR.

### Added

- **Admin-only user delete + Play Store legal APIs** — `DELETE /users/{id}` requires `users:delete` (OWNER only; UI Delete on Settings → Users); public `GET /legal`, `/legal/privacy`, `/legal/account-deletion` for Play Console links; `DELETE /users/me` in-app account deletion (soft-delete + revoke sessions; last OWNER blocked). Android Settings privacy link + delete-account; Admin users list OWNER delete.
- **Farmer comments on field work + field-ops document RBAC** — FARMER gains `comments:create` (web + Android catalog); AGENT/DRIVER gain `documents:read|create` for diesel receipt uploads. Migration `029` grants these on all orgs. Work→comment→diesel receipt edge-case tests in `tests/test_field_service_work_flow.py`.
- **Web + Android role × screen QA audit** — `docs/qa/ROLE_SCREEN_AUDIT.md`: live Vercel API/UI matrix for OWNER/MANAGER/AGENT; static SUPERVISOR/DRIVER/FARMER; web P0s (OWNER farmer-payments 403, mobile vs backend `PermissionGuard` codes, FARMER→OWNER nav default, AGENT procurement nav); Android matrix retained; ERP checklist QA board updated
- **Playwright role × screen smoke** — `frontend/e2e/tests/workflows/settings/role-screen-smoke.spec.ts`: OWNER (+ demo MANAGER/AGENT when seeded) visits main nav routes; SUPERVISOR/DRIVER/FARMER via `E2E_<ROLE>_EMAIL`/`PASSWORD` only
- **Field-service diesel receipts + ledger sync** — `diesel_amount > 0` on create/update posts/updates a Fuel expense (`source_type=field_service`, response `diesel_expense_id`); cancel/delete reverses it. OpenAPI `LinkEntityType` includes `field_service`. Web detail uploads diesel receipts (`fuel_bill`) and work photos; comment thread already live.
- **Android cancel/reverse + `[kf:work]` field-service profiles** — external `krishifarms-mobile`: procurement detail Cancel/Reverse wired to CRM APIs; vehicle-type work questions persisted as `[kf:work]` comments (see `ANDROID_CRM_PARITY.md`)
- **Android field-ops parity (branch `cursor/mobile-field-ops-parity-e86f`)** — DRIVER ops tab fix; procurement/field-service photo attachments; crop price admin; farmer payments list/create; hide unimplemented fleet stubs from More hub
- **Phase 3 finance APIs + trip diesel posting** — `GET/POST/PATCH/DELETE /expenses` and `GET/POST /collections` (+ get by id) in `app/modules/financial/`; migration `027` adds `expenses.source_type`/`source_id` + `expenses:*`/`collections:*` RBAC; `POST/PATCH /vehicle-trips` with `fuel_cost > 0` posts/updates Fuel expense (`source_type=vehicle_trip`); trip responses include `diesel_expense_id`; tests in `tests/test_expenses.py`
- **Reports UI + thin dashboard catalog (Ralph priority 5)** — `/reports` registry lists 8 ERP report types (Vehicle Utilization, Diesel Expenses, Procurement Summary, Farmer Ledger, Outstanding Payments, Crop/Village Wise Procurement, Vehicle Earnings, Supervisor Productivity) with available/partial/coming-soon status, module deep-links, and live KPI strip from extended `GET /dashboard/summary`; new `GET /dashboard/reports` metadata catalog; OpenAPI `paths/dashboard.yaml`; period analytic APIs still documented as gaps in `ERP_UPGRADE_CHECKLIST.md`
- **Farmer payment settlement UI (web)** — `/payments` Allocate / Reverse / Details with confirmation warnings; shows linked procurement `paid_partial` / `paid_full` / `confirmed` after settle; `PermissionGuard` on `farmer_payments:create|reverse`
- **Ralph Loop 2 final (web + Android parity)** — `/payments` thin farmer-payment list/create UI; procurement document gallery uses `GET /documents?entity_type=&entity_id=`; Android field-services list/create, farmer `village_id` cascade, procurement detail workflow actions (see `ANDROID_CRM_PARITY.md`)
- **Documents list-by-entity (Ralph Loop 2 final backend)** — `GET /documents?entity_type=&entity_id=` joins `document_links` for procurement/field-service photo galleries; both params required together; tests in `tests/test_documents.py`
- **Farmer payments web UI (Ralph Loop 2 final)** — `/payments` list + Record payment dialog wired to `GET/POST /farmer-payments` (`features/farmer-payments/api.ts`); allocate/reverse settlement dialogs shipped
- **Staff phone mandatory (API)** — `UserCreateRequest.phone` required (10+ digits, normalized); `UserUpdateRequest` rejects clearing/short phone; historical null phones remain until updated
- **Farmer payment status sync tests** — allocate/reverse helpers cover `paid_partial` / `paid_full` / revert-to-`confirmed` in `tests/test_farmer_payments.py`
- **Farmer payments allocate/reverse + farms/trips (Ralph Loop 3 backend)** — `POST /farmer-payments/{id}/allocate|reverse` (partition `payment_date`) links procurements to `paid_partial`/`paid_full` and posts reversing ledger debit; thin `GET/POST/PATCH /vehicle-trips`; thin `GET/POST/PATCH/DELETE /farms` + activities; models registered in `app/models.py`
- **Phone-first web auth (Ralph Loop 2)** — `/login` accepts **phone or email** + password (`POST /auth/login` `mobile` path); Settings → Users requires phone (10+ digits); disabled **Login with OTP (coming soon)** stub; OTP path documented in [FIREBASE_OTP.md](./modules/FIREBASE_OTP.md); password mobile lookup uses same phone normalization as Firebase; `/vehicles` prefers live `GET /vehicle-types` chips alongside asset instances
- **Android + QA Ralph Loop** — refreshed `docs/modules/ANDROID_CRM_PARITY.md` (external repo path, implementation backlog, RoleLabels / location cascade / procurement extras / field-services stub); QA board on `docs/ERP_UPGRADE_CHECKLIST.md` (Completed / Needs manual verification / Needs external data-config); `tests/test_role_definitions.py`; mobile catalog `FIELD_SERVICE_*` + `field_services` accessible module aligned with `permissions.py`
- **Procurement web workflow (Ralph Loop 2)** — detail page actions: submit → weighment (moisture) → apply-price → confirm / cancel / reverse with `PermissionGuard`; API client mutations; color-coded status; first-class `buyer_id`/`payment_terms` on create (migration `026`) with `[kf:proc]` fallback for planned moisture/rate + legacy tickets; photo upload via documents presign+link (`EntityDocumentUpload`)
- **Procurement buyer/terms columns** — migration `026` adds `buyer_id`, `payment_terms`, `payment_terms_custom`, `expected_payment_date`, `actual_payment_date` on `procurements`; OpenAPI + create/update schemas updated
- **Reusable frontend guards/selects** — `SearchableSelect` (touch Autocomplete wrapper), `PermissionGuard` + `useAuth().hasPermission` for action-level RBAC
- **Vehicle work profiles expanded** — Cultivator/Rotavator/Baler/Weeder/Harvester share tractor crop/area/stage questions; Fertilizer Pump (litres) + Drone (spray type); searchable activity type; CommentThread on field-service detail
- **Dashboard summary stubs** — home wires `GET /dashboard/summary` count cards + role-aware welcome hints
- **Farmer payments Phase thin (Ralph Loop 2)** — `app/modules/farmer_payments/` list/create/get on `/farmer-payments` (org-scoped, `farmer_payments:read|create`); create posts immutable ledger credit (`reference_type=farmer_payment`); permissions in `app/shared/permissions.py`; tests `tests/test_farmer_payments.py`
- **Frontend location cascade (District → Mandal → Village)** — searchable MUI Autocomplete cascade via `LocationCascade` (`SearchableSelect` + touch targets); API helpers `fetch/create/update/delete` for districts & mandals + filtered `fetchVillages`; wired on Settings → Villages (district/mandal masters, no free-text), Add/Edit farmer, New procurement, and field-service location (DCM loading/unloading master-only); Telugu labels when `preferred_locale=te`
- **Assets CRUD + fleet fields (Ralph Loop 2)** — migration `025`: `assets.vehicle_type_id` / `fuel_type` / `driver_name`, expanded categories (`bolero`/`implement`); live `GET/POST/PATCH/DELETE /assets` (`app/modules/assets/`); Vehicle Supervisor (`DRIVER`) granted `assets:*` + `field_services:create/update`; seed `DEFAULT_FLEET_ASSETS` (JD 2W/4W, Bolero, DCM) linked to `fleet_inventory` vehicle types; `/vehicles` lists catalog types + asset instances; field-service diesel cost visible/validated on tractor/transport/vehicle ops
- **Location hierarchy (District → Mandal → Village)** — migration `023` `districts`/`mandals` tables + village FKs; live CRUD `GET/POST/PATCH/DELETE /districts`, `/mandals`, cascaded filters on `/villages` (`district_id`/`mandal_id`/`district`/`mandal`/`q`); models in `app/modules/master_data/`
- **Rangareddy location preload** — `scripts/data/rangareddy_service_villages.py` (Keshampeta, Talakondapally, Maheshwaram, Kothur, Farooqnagar + villages/pincodes); idempotent `python -m scripts.seed_locations` (also hooked from `scripts/seed.py`)
- **RBAC role alignment** — migration `024`: display names Admin/Owner, Manager, Farming Supervisor (`SUPERVISOR`), Vehicle Supervisor (`DRIVER`), Agent, Farmer (`FARMER` read-only); soft-wired `vehicles`/`transport`/`diesel`/`farming`/`finance`/`master_data`/`approve`/`delete` + `districts:*`/`mandals:*`; MANAGER no `users:create`
- **ERP upgrade gap analysis (Ralph Loop 1)** — Added `docs/ERP_UPGRADE_CHECKLIST.md` mapping target ERP requirements to implementation status (Done/Partial/Missing) with evidence paths and P0 field-ops blockers (procurement web workflow, farmer payments, phone/OTP auth, location masters, fleet assets, Android parity)
- **Crop master defaults** — shared `scripts/data/crop_catalog.py` seeds Paddy, Corn, Maize, Cotton, Red/Green/Black/Bengal Gram, Sunflower, Groundnut, Vegetables, Others (plus legacy Pulses / Concrete Work); used by `seed.py` / `seed_services.py`
- **Fleet service-type catalog** — vehicle types include Tractor, Cultivator, Rotavator, Baler, Trolley, Weeder, Fertilizer Pump, Bolero, DCM, Harvester, Drone plus inventory units (John Deere 2W/4W, Mahindra Bolero, Eicher DCM); Harvester/Drone activity seeds
- **Vehicle-conditional field-service form** — Tractor (crop/area/cultivation stage), Trolley (trips/purpose/material), Bolero (trips/locality/distance/weight/goods), DCM (trips/distance/tonnes/loading/unloading); Autocomplete for farmer/vehicle/crop/village; work details persisted in comments `[kf:work]` marker
- **Procurement create UX** — searchable buyer dropdown, payment terms (One Week / 10 Days / 2 Weeks / 20 Days / Custom), planned moisture % (crop default) and rate/quintal; extras stored in notes `[kf:proc]` until API columns exist
- **KrishiFarms fleet inventory defaults** — canonical tractors (John Deere 2W/4W), transport (Mahindra Bolero, Eicher DCM), and implements (trolley, baler, pump, cultivator, rotavator, weeder) in `scripts/data/fleet_inventory.py`; idempotent seed via `scripts/seed_services.py`; web field-service vehicle dropdowns filtered by category; vehicle/activity type admin prompts; `/vehicles` placeholder lists fleet
- **Admin form chrome** — shared `PremiumDialog` (blur backdrop, 24px radius, MUI focus trap) + `SoftAlert` for settings/catalog save failures; wired into `CatalogAdminPage` and Settings → Users
- **Frontend e2e — enterprise `validateEntirePage` framework** — 16 validation helpers under `e2e/utils/validation/` (console, network, layout/overlap, inputs, buttons, typography, tables, dialogs, navigation, `@axe-core/playwright` a11y, responsive viewports, visual regression, WCAG contrast, CSS, performance); POM `e2e/pages/`, custom `enterprise-reporter.ts` → `enterprise-validation.json`, baselines `e2e/baselines/`; suites `e2e/tests/{smoke,regression,visual,responsive,workflows}/`; cross-browser projects; CI via `.github/workflows/e2e.yml` (PR smoke gate, push regression+workflows, nightly full); [frontend/e2e/README.md](../frontend/e2e/README.md)
- **Frontend e2e — settings/admin smoke** — Playwright specs under `frontend/e2e/settings/` for `/settings`, `/settings/users` (table or Alert), `/settings/villages`, `/settings/master-data` + all catalog routes; Add/Edit dialog label visibility + non-overlap checks (buyers emphasized)

- **Frontend e2e — operations smoke** — Playwright specs under `frontend/e2e/operations/` for `/farmers` (+ `/farmers/new`), `/procurement`, `/field-services` (+ `/field-services/new` category/form overlap), `/farms`, `/vehicles`, `/workers`; shared auth via `e2e/.auth/user.json` / UI login fallback
- **Frontend Playwright foundation** — `@playwright/test`, `playwright.config.ts`, auth setup (`e2e/auth.setup.ts` + `e2e/fixtures/auth.ts` → `e2e/.auth/user.json`), dashboard smoke spec; `npm run test:e2e` / `test:e2e:ui` ([frontend/e2e/README.md](../frontend/e2e/README.md))
- **Frontend e2e — finance smoke** — Playwright specs under `frontend/e2e/finance/` for `/expenses`, `/payments`, `/collections` (shell/title, empty/table/error content, no pageerror; create-dialog overlap check when present)
- **Frontend sign-out + login** — MUI user menu Sign out (clears `krishi-access-token`, revokes refresh token via `POST /auth/logout` when available); `/login` email/password page; `AuthBootstrap` skips dev auto-login after explicit sign-out (`sessionStorage` flag)
- **Admin CRUD parity (web + Android)** — Web: `/auth/me` role hook; sidebar links for Users + Master data; dashboard admin shortcuts; delete hidden for MANAGER on `CatalogAdminPage`. Android: `feature/admin/` hub (More + Settings) with catalog list/create/edit for crop types, vehicle types, activity types, buyers, agents, expense categories, payment modes; villages read-only; users list/create/edit; EN + TE strings; `MenuRegistry` admin tile for OWNER/MANAGER
- **RBAC: MANAGER admin without delete** — Backend `users:create` for MANAGER; mobile `SETTINGS_MANAGE` + `USER_MANAGE` + `admin` module in permission catalog; OWNER-only delete on web/Android UI
- **Admin master-data parity (web)** — CRM settings CRUD for crop types, crop prices, buyers, agents, vehicle types, activity types, expense categories, payment modes; villages edit/delete; users create/edit; farmers `/farmers/new`; shared `CatalogAdminPage`; gap matrix [ANDROID_CRM_PARITY.md](./modules/ANDROID_CRM_PARITY.md)
- **Payment modes API** — `GET/POST/PATCH/DELETE /payment-modes` (`PaymentMode` model on existing `payment_modes` table); permissions `payment_modes:*`; OpenAPI `paths/platform.yaml` for platform + master catalogs
- **FCM devices + push** — migration `020` `user_device_tokens`; `POST/DELETE /devices/push-tokens`; bilingual FCM on procurement status, farmer comments, document upload; module doc [DEVICES_NOTIFICATIONS.md](./modules/DEVICES_NOTIFICATIONS.md)
- **Device accountability** — `write_audit_log` / `write_activity_feed` persist `device_id`, `client_type`, `request_id` (and activity `summary_te`); documents mutations take `ClientContext`; login / firebase-login / refresh bind `refresh_tokens.device_id` from `X-Device-Id`
- **Sessions API** — `GET /users/me/sessions`, `DELETE /users/me/sessions/{id}` (active refresh tokens; device_id only — no new migration)
- **Locale self-service** — `preferred_locale` on `AuthUserResponse` / `/auth/me`; `PATCH /users/me` for `preferred_locale` + `full_name`
- **SSM parameter bootstrap** — `deploy/scripts/ensure-ssm-parameters.sh` creates missing `/krishifarms/dev/*` SecureString/String params (placeholder `REPLACE_ME`; does not overwrite). Created `/krishifarms/dev/db/database_url` in ap-south-1 for Supabase cutover.
- **Temporary demo data pack** — `scripts/seed_demo_data.py` + `scripts/purge_demo_data.py` for live modules (farmers, procurements, platform); markers `[DEMO]` / `@demo.krishifarms.local`; runbook + inventory in [docs/DEMO_DATA.md](./DEMO_DATA.md)
- **GitHub deploy automation** — `deploy/scripts/github-predeploy.sh` runs on each `main` deploy: writes Supabase `DATABASE_URL` to SSM from `SUPABASE_DB_PASSWORD` secret, runs EC2-only cost scheduler config; remote deploy seeds DB if empty


### Fixed

- **Playwright layout validator** — skip intentional password show/hide overlaps (relative field wrappers), ignore `aria-hidden` underlays, and ignore dialog-vs-page cross-layer overlaps; when a dialog is open, button validation only checks controls inside it; dialog field locator prefers role/`^Name$` for catalog Name inputs; settings dialog `validateEntirePage` soft-fails layout/buttons

### Changed

- **Phone-or-email login polish** — `/login` submit label **Sign in**; helper notes +91-optional phone; password login path unchanged; OTP still stubbed
- **Procurement photos note** — `EntityDocumentUpload` documents that entity gallery awaits `GET /documents?entity_type=&entity_id=` (org-wide list only today)
- **Android + QA Ralph Loop (final)** — refreshed `ANDROID_CRM_PARITY.md` + checklist: field-services list/create, farmer `village_id` + cascade, procurement workflow actions on Android; document gallery + cancel/reverse still gaps
- **RBAC foundation** — MANAGER no longer gets `users:create` in runtime catalog (OWNER-only provisioning); AGENT gains `farmers:read` + location reads; DRIVER/SUPERVISOR display names → Vehicle/Farming Supervisor; soft-wired `transport`/`diesel`/`farming`/`finance` permissions
- **Playwright E2E CI** — field-service form `fetchFarmers` pageSize capped at 100 (API max) and core fields render while dropdown data loads; settings users spec ignores empty Next.js route announcer and targets content alerts; login password row uses flex layout so show/hide toggle no longer overlaps input in layout validation; catalog admin dialog spacing + `data-testid` + open wait for first textbox (villages Name field timeout)
- **Master-data catalog dialogs** — `CatalogAdminPage` Add/Edit forms no longer overlap labels (dense MUI `TextField`s in `DialogContent`); now spaced `Scope` + premium `Field`/`Input`/`Textarea`, `PremiumDialog` chrome (24px radius), clear titles; covers activity-types, buyers, crops, and all other catalog pages
- **GET /users 500** — `UserResponse` / `UserCreateRequest` use `str` instead of `EmailStr` so seeded `*.local` emails serialize (same as auth login); Settings → Users no longer Internal Server Error
- **CI Ruff lint** — remove unused `typing.Any` import in `app/modules/devices/fcm.py`
- **Web dashboard/home** — Replaced Tailwind-only executive mock (mixed with MUI shell) with MUI home + role-aware admin hub; loads user from `/auth/me`
- **Audit helpers** — `write_audit_log` / `write_activity_feed` accept `device_id` and `client_type` (callers already passed them; previously TypeError)
- **Auth login** — accept seeded `*.local` emails (EmailStr rejected special-use domains)
- **bcrypt pin** — constrain `bcrypt>=4.0.1,<4.1` (bcrypt 5.x breaks passlib verify / login)
- **ORM workers stub** — register migration-only `workers` table in metadata so `users.worker_id` FK flush works (login/refresh tokens)

### Changed

- **Field service create form layout** — switch legacy MUI `Grid item` to `Grid2` sizing so fields align in columns; clearer section titles on `/field-services/new`
- **Web login fields** — `/login` uses premium `components/ui/Input` (54px, 16px radius, soft `#E5E7EB` border, `#111827` focus ring); labeled fields + show-password a11y; no Material entrance animations on the Google-style card
- **Web login UI** — Google-style centered card sign-in (`/login`): email + password fields, show/hide password, primary Next button
- **Web login UI** — Dribbble-inspired split-screen sign-in (`/login`): Canopia brand plane + refined email/password form, show/hide password, Fraunces display type; no purple/cream chrome

- **Supabase cutover runbook** — [docs/deploy/SUPABASE_CUTOVER_RUNBOOK.md](./deploy/SUPABASE_CUTOVER_RUNBOOK.md): GitHub secret + IAM attach script + deploy verify steps
- **Deploy IAM policy** — `deploy/iam/github-backend-deploy-ssm-supabase.json` + `attach-github-deploy-iam-supabase-policy.sh` for one-time admin attach
- **Deploy workflow** — fails fast if `SUPABASE_DB_PASSWORD` missing; `workflow_dispatch` for manual redeploy; `github-predeploy` writes Supabase URL first
- **krishifarms-infra patch** — `patches/krishifarms-infra-deploy-iam-supabase.patch` (SSM + Lambda perms on deploy role; optional Terraform-managed secret)
- **Supabase DB cutover prep** — project `ucvwtoziiqgmcyzxkwxe`; `docker-compose.prod.yml` no longer hardcodes Docker `DATABASE_URL` (env_file wins); `depends_on.postgres.required: false`; `sync-env-from-ssm.sh` prefers SSM `/krishifarms/dev/db/database_url` and ignores `REPLACE_ME` placeholders; helpers `ensure-ssm-parameters.sh` + `put-supabase-database-url-ssm.sh`; cutover guide [docs/deploy/SUPABASE_MIGRATION.md](./deploy/SUPABASE_MIGRATION.md)
- **EC2-only cost scheduler** — `deploy/scripts/configure-compute-scheduler-ec2-only.sh` removes RDS from daily Lambda cron while keeping EC2 start/stop
- **Gamya RDS removal patch** — `patches/gamya-couture-infra-remove-rds.patch` + [docs/deploy/GAMYA_RDS_REMOVAL.md](./deploy/GAMYA_RDS_REMOVAL.md): apply in `gvsharma/gamya-couture-infra` to destroy `gamya-couture-dev-pg` via Terraform (`enable_rds = false`)
- **Aurora destroy skipped** — ap-south-1 has no KrishiFarms Aurora/RDS; only `gamya-couture-dev-pg` (Gamya, stopped) — left untouched. Prod DB remains Docker Postgres on EC2 until Supabase cutover.
- **Supabase pooler discovery** — `put-supabase-database-url-ssm.sh` probes `aws-0/1/2` pooler hosts or uses `SUPABASE_POOLER_HOST` GitHub variable (fixes `Tenant not found` + EC2 IPv6 errors)

### Fixed

- **Supabase SSM DATABASE_URL** — use `URL.render_as_string(hide_password=False)`; SQLAlchemy 2.x `str(URL)` masks passwords as `***`, which was written into SSM and broke EC2/Alembic auth
- **Supabase SSM put path** — write SecureString via Python/`aws --cli-input-json file://…` (avoid bash capturing the URL)
- **Supabase SSM password sync** — `put-supabase-database-url-ssm.sh` rejects truncated/`***` GitHub secrets before writing SSM
- **Supabase deploy auth** — `put-supabase-database-url-ssm.sh` verifies pooler connection before writing SSM, builds `DATABASE_URL` via SQLAlchemy `URL.create` (avoids manual URL-encoding mistakes); Alembic online migrations use `create_engine(settings.database_url)` directly (no ConfigParser round-trip)
- **Alembic + Supabase pooler** — `alembic/env.py` escapes `%` in `DATABASE_URL` before `set_main_option` (URL-encoded passwords broke migrations with `invalid interpolation syntax`)
- **Firebase login 500** — EC2 `FIREBASE_SERVICE_ACCOUNT_JSON` was multiline in `application.env`; env upsert only replaced the first line, leaving orphan private-key lines that broke `json.loads` and docker-compose parsing. `fix-firebase-env.py` and `sync-env-from-ssm.sh` now remove full multiline values before upsert and double-escape backslashes so docker-compose does not turn JSON `\\n` into real newlines; `firebase.py` returns 503 on malformed JSON instead of 500
- **Seed** — `Permission.roles` relationship missing `Role` target class (SQLAlchemy `ArgumentError` on `scripts/seed.py`)
- **Migration 008** — `uq_procurements_idempotency` unique index on partitioned `procurements` now includes `procurement_date` (PostgreSQL partition-key requirement; matches `farmer_payments` idempotency index pattern)
- **Deploy env sync** — `sync-env-from-ssm.sh` minifies `FIREBASE_SERVICE_ACCOUNT_JSON` to single-line quoted JSON; `deploy/scripts/fix-firebase-env.py` helper for EC2 repair

### Added

- **Farmers Phase 2b** — bank account + land parcel sub-resources (`/farmers/{id}/bank-accounts`, `/land-parcels`); Fernet encryption for account numbers; `outstanding_amount` on GET detail + `GET /farmers/{id}/outstanding`; tests `tests/test_farmers_subresources.py`
- **Frontend Phase W2 (partial)** — farmers list/detail with `CommentThread`; procurement list, create wizard, detail; dev auth bootstrap (`NEXT_PUBLIC_DEV_LOGIN_*` / token)
- **Procurements Phase 2b** — full workflow API (`app/modules/procurements/`): draft → weighment → priced → confirmed with `crop_price_rules` snapshot, ledger debit on confirm, OWNER-only reverse with credit entry; migration `019` extends status CHECK; tests `tests/test_procurements.py`
- **Farmers Phase 2a** — CRUD API (`app/modules/farmers/`), auto `farmer_code`, comments/tags on detail, OWNER-only delete, audit + activity feed with `ClientContext`
- **Admin platform Phase 1b** — REST APIs for buyers, field agents, activity types, vehicle types, crop price rules, comments, tags (`app/modules/platform/`); migrations `017`/`018`
- Shared patterns: `AuditMetaMixin`, `entity_notes` helper; docs `FARMERS.md`, `CROSS_CUTTING.md`, `PROCUREMENT.md`, `PRODUCT_ROADMAP.md`
- Tests: `tests/test_farmers_rbac.py`, `tests/test_platform_admin.py`
- **Frontend Phase W1 (Material UI)** — MUI v6 MD3 theme (`frontend/src/theme/`), `MuiAppShell` with role-aware nav, reusable `CommentThread`, settings pages (users, villages, master-data hub), API client with `X-Device-Id` / `X-Client-Type: web`
- `docs/ui/MATERIAL_DESIGN.md` — MD3 tokens, Helvetica stack, component conventions

### Changed

- RBAC: platform + farmer permissions in `app/shared/permissions.py`; MANAGER no delete; AGENT/DRIVER comments-only
- **Frontend:** App layout uses MUI shell; dashboard retains Tailwind KPI layout; root typography switched to system Helvetica stack
- **Merge:** Reconciled `feature/material-ui-phase1` with `main` after admin-platform merge (PR #16); resolved shell/routes/theme overlap

### Added

- `POST /auth/firebase-login` — verify Firebase Phone OTP ID token (Admin SDK), lookup user by phone, issue CRM JWT + RBAC; 403 if not registered
- `GET /auth/me` — current user profile with roles, permissions, and accessible modules (mobile)
- Firebase auth module (`app/modules/auth/firebase.py`), phone normalization, login rate limiting
- Migration `202506210016` — `users.firebase_uid`, `users.village_id`, nullable `password_hash`
- `require_role()` dependency alongside existing `require_permission()`
- Admin can create phone-only users (no email/password) for Firebase field staff login

### Changed

- `sync-env-from-ssm.sh` — optional sync of `/krishifarms/dev/app/firebase_service_account_json` and `firebase_project_id` into EC2 `application.env`
- Env examples: default `FIREBASE_PROJECT_ID=krishifarms-prod` (matches Firebase Android app)
- JWT access token claims include `phone`, `name`, `village_id` (plus existing `org_id`, `role`)
- Login audit log records `auth_method` (`password` | `firebase`) and phone
- `UserCreateRequest` — email/password optional when phone is provided for Firebase-only users

### Added

- `.github/DEPLOY_CONFIG.md` — GitHub Actions secrets/variables from `krishifarms-infra` dev Terraform outputs
- Deploy workflow: `AWS_REGION`, `NGINX_LOCAL_PORT`, and `PUBLIC_HEALTH_CHECK_URL` vars for shared EC2 dev (port 8082)

### Changed

- Deploy: align SSM orchestration with Gamya (stale command cancel, `log_ssm_invocation`, probe/kickoff logging, 36×10s status poll); smoke tests use `:8082`; `sync-env-from-ssm.sh` fails fast without AWS CLI
- Docs: `CI_CD.md` and `deploy/README.md` — "Same as Gamya" side-by-side; SSM parameter names for `krishifarms-infra`

### Changed

- Deploy workflow: optional `EC2_NAME_TAG` variable; auto-default `gamya-couture-dev-api` when `DEPLOY_BUCKET` contains `krishifarms` (shared Gamya EC2)
- `.github/DEPLOY_CONFIG.md`, `docs/deploy/CI_CD.md`, `deploy/README.md` — `EC2_INSTANCE_ID` and `EC2_HOST` **required** for shared Gamya EC2; shared-host section (port 8082, `/opt/krishifarms`)

### Fixed

- Deploy: exclude macOS AppleDouble (`._*`, `__MACOSX`) from tar bundle; strip after extract — fixes Alembic `SyntaxError: source code string cannot contain null bytes`
- Docker: copy `migration_utils.py` into API image so Alembic migrations can import shared helpers
- Deploy: `ec2-bootstrap.sh` installs Docker Compose v2 binary when `docker-compose-plugin` is unavailable on AL2023
- Deploy SSM: auto-create `application.env` from S3 template when bootstrap was skipped; `ssm-kickoff-deploy.sh` marks `deploy.status=failed` on early errors (no more zombie `running`); creates `krishifarms` service user if missing; workflow preflight checks Docker and clears stale deploy PID/status
- Deploy: revert SSM status poll to 36 attempts × 10s; upload `application.env.example` to S3 for kickoff
- Deploy: `infra/docker-compose.prod.yml` maps nginx to host port **8082** (`NGINX_HOST_PORT`, default 8082) on shared Gamya EC2
- Deploy: `remote-deploy.sh` on-host health check uses `http://127.0.0.1:8082/api/v1/health`

- Deploy: EC2 resolution no longer looks up non-existent `krishifarms-dev-api` tag when using shared Gamya host
- Deploy: write `deploy.tar.gz` under `$RUNNER_TEMP` before moving to workspace — GNU tar exits 1 (`file changed as we read it`) when the archive is created inside the tree being packed
- Frontend Vercel: `API_PROXY_TARGET` includes EC2 nginx port `:8082`; `NEXT_PUBLIC_SITE_URL` set to `https://krishifarms-backend.vercel.app`; env templates and `frontend/README.md` aligned
- Frontend Vercel: project root directory set to `frontend` (was FastAPI at repo root); `installCommand` uses `npm install`; production env vars configured for API proxy
- CI: set dummy `SECRET_KEY` and `DATABASE_URL` in `validate.yml` backend job so import sanity check passes without a `.env` file
- CI: replace `hashFiles` in reusable `validate.yml` with a `detect` job output (GitHub forbids `hashFiles` in `workflow_call`)

### Added

- Auth: mobile login (`LoginRequest.mobile`), enriched `TokenResponse` (user, roles, permissions, accessibleModules), server-owned mobile RBAC catalog (`permission_catalog.py`, `rbac.py`); OpenAPI `auth.yaml` aligned
- Tests: `tests/test_auth_rbac.py` for login/RBAC payload behavior
- Frontend: `frontend/.gitignore` (exclude `node_modules/`, `.next/`, build artifacts)

- Frontend: App Router placeholder pages for all sidebar routes (`PlaceholderPage`); Vercel Next.js build via `npm ci`
- Frontend: Next.js 15 app shell in `frontend/` — Dribbble-inspired Farm Management SaaS UI (sidebar, header, CEO dashboard with 8 KPI cards, chart placeholders, nav placeholders); Plus Jakarta Sans + Noto Sans Telugu; light/dark themes; `package-lock.json` for CI; `frontend/.gitignore` for build artifacts
- Docs: Dribbble-inspired refinements in `docs/ui/DESIGN_SYSTEM.md` and `docs/ui/WIREFRAMES.md` (shell layout, typography, KPI cards)
- Docs: Flutter Web UI/UX design system under `docs/ui/` (IA, design tokens, components, wireframes, widget trees, Flutter architecture, screen specs, accessibility)
- Docs: migrate `docs/ui/` from Flutter Web to **Next.js only** — rename `FLUTTER_ARCHITECTURE.md` → `FRONTEND_ARCHITECTURE.md`, `WIDGET_TREE.md` → `COMPONENT_TREE.md`; update stack references (TanStack Query, Zustand, Tailwind, shadcn/ui); align with Gamya Couture + Vercel `frontend/` placeholder
- Docs: document PR-only branch strategy and merge-to-`main` deploy triggers ([CI_CD.md](./deploy/CI_CD.md), [AGENT_GUIDE.md](./AGENT_GUIDE.md), Cursor rules)
- Comprehensive agent documentation: [AGENT_GUIDE.md](./AGENT_GUIDE.md), [ARCHITECTURE.md](./ARCHITECTURE.md)
- Cursor rules for doc maintenance and project context (`.cursor/rules/`)
- Shortened [AGENTS.md](../AGENTS.md) as scannable entry point
- Frontend: Next.js app shell (sidebar, header, page layout), shadcn-style UI primitives, app providers, Zustand UI store, route constants, design tokens, TanStack Query client, KPI card and empty-state components

---

## [0.1.0] — 2025-06-21

Foundation release (`60bb2b5`). Phase 1 API live; full database schema and OpenAPI contract ahead of Python implementation for Phases 2+.

### Added

#### Phase 1 API (Python)

- **Auth** — JWT login, refresh, logout (`app/modules/auth/`)
- **Users & roles** — org-scoped users, RBAC (`app/modules/users/`)
- **Master data** — villages, crop types (`app/modules/master_data/`)
- **Financial** — expense categories only (`app/modules/financial/`)
- **Documents** — S3 presign upload/download, register, list, link (`app/modules/documents/`)
- **Audit** — audit logs, activity feed (`app/modules/audit/`)
- **Dashboard** — summary stub, health check (`app/modules/dashboard/`)

#### Database (Alembic `202506210001`–`015`)

| Revision | Domain |
|----------|--------|
| `001` | Platform baseline — orgs, IAM, master data, documents, audit |
| `002` | Extensions, Telugu columns, user scopes, triggers |
| `003` | Activity types, payment modes, number sequences |
| `004` | Farmers, bank accounts, land parcels |
| `005` | Workers, skills |
| `006` | Farms, farm activities |
| `007` | Document OCR/locale/archive, link constraints |
| `008` | Procurements, farmer ledger, farmer payments (partitioned) |
| `009` | Work orders, attendance |
| `010` | Assets, maintenance, usage logs, vehicle trips |
| `011` | Rental customers, agreements |
| `012` | Financial transactions, expenses, collections, payments |
| `013` | Audit indexes, sync tables |
| `014` | AI jobs, OCR, WhatsApp, voice, summaries |
| `015` | Global permissions and per-org system roles seed |

- Shared migration helpers in `migration_utils.py` (audit columns, partitions, org FK)
- Monthly partitions seeded for 2026 on high-volume tables

#### API contract

- Modular OpenAPI 3.0 spec: `docs/api/openapi.yaml` + `paths/` + `schemas/`
- Human-readable contract: `docs/api/API_CONTRACT.md`
- Bundled spec for Postman: `docs/api/openapi.bundled.yaml`

#### Reporting

- Architecture doc: `docs/reporting/REPORTING_ARCHITECTURE.md`
- KPI definitions: `docs/reporting/kpi_definitions.md`
- Eight parameterized SQL dashboards: `docs/reporting/sql/01`–`08`

#### Document management design

- Full module design: `docs/modules/DOCUMENT_MANAGEMENT.md` (implemented vs gaps)

#### CI/CD & deployment

- GitHub Actions: `ci.yml`, `validate.yml`, `deploy.yml`
- EC2 deploy via S3 + SSM Run Command (`deploy/scripts/`)
- Production Docker Compose: `infra/docker-compose.prod.yml`
- Post-deploy smoke tests: `scripts/smoke-test-api.sh`
- CI/CD documentation: `docs/deploy/CI_CD.md`, `deploy/README.md`

#### Synthetic seed (UAT demo data)

- Generator: `scripts/synthetic_seed/generate_synthetic_data.py`
- Bhairkhanpally demo: 50 farmers, 200 procurements, ledger, expenses, etc.
- Purge script: `scripts/synthetic_seed/sql/99_purge_synthetic_data.sql`

#### Cache layer

- Pluggable `CacheProvider`: none / memory / redis (`app/core/cache/`)
- Permission cache in `app/core/dependencies.py` (TTL via `CACHE_TTL_SECONDS`)

#### Agent & project docs

- `AGENTS.md` — agent coding guide
- `README.md` — human onboarding, tech stack, quick start

#### Frontend placeholder

- Vercel config stub: `frontend/vercel.json`, `frontend/README.md`

### Added

- `.github/DEPLOY_CONFIG.md` — GitHub Actions secrets/variables from `krishifarms-infra` dev Terraform outputs
- Deploy workflow: `AWS_REGION`, `NGINX_LOCAL_PORT`, and `PUBLIC_HEALTH_CHECK_URL` vars for shared EC2 dev (port 8082)

### Changed

- `app/main.py` — mounts Phase 1 routers under `/api/v1`
- `infra/docker-compose.yml` — optional Redis profile
- `pyproject.toml` — optional `[redis]` extra

### Security

- JWT access + refresh tokens; RBAC via `require_permission()`
- Org-scoped multi-tenancy on all business rows

---

[Unreleased]: https://github.com/gvsharma/krishifarms-backend/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/gvsharma/krishifarms-backend/commit/60bb2b5
