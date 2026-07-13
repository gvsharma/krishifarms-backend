# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed

- **Login password field invisible / broken eye toggle** — password row used a Tailwind-bordered wrapper; with MUI CSS layers, `border` utilities never get `border-style: solid`, so the shell was invisible and the show/hide control kept native button chrome. Login fields now use explicit `1px solid` borders + Lucide eye icons inside the field.
- **Custom vehicle types (e.g. tractor4W) missing after add/update** — field-service dropdowns filtered by a hardcoded code allowlist, so new master-data codes never appeared; Edit also hid `code` (`createOnly`) and PATCH rejected code changes. Filter now includes custom types by `fuel_type` / code heuristics, code is editable on update (unique per org), and related React Query caches are invalidated.
- **Dark-mode Edit User / admin dialog text** — `PremiumDialog` no longer keeps a light `#FAFAFA` paper while MUI `TextField`s render light/white text in dark mode (invisible labels/values). Dialog paper/title/content and form-control colors follow the active color scheme; `SoftAlert` and `.kf-premium` CSS tokens gain dark variants. Playwright users spec asserts dialog WCAG contrast in dark mode and matches `Edit user` aria-label.
- **Payment modes settings 403** — production `/settings/master-data/payment-modes` failed with `Missing permission: payment_modes:read` because `payment_modes:*` was defined in code/`seed.py` but never inserted by Alembic (omitted from migration `018`). Migration `028` seeds and grants those permissions to OWNER / MANAGER / SUPERVISOR.

### Added

- **Farmer comments on field work + field-ops document RBAC** — FARMER gains `comments:create` (web + Android catalog); AGENT/DRIVER gain `documents:read|create` for diesel receipt uploads. Migration `029` grants these on all orgs. Work→comment→diesel receipt edge-case tests in `tests/test_field_service_work_flow.py`.
- **Android role × screen QA audit** — `docs/qa/ROLE_SCREEN_AUDIT.md`: Role × Module matrix (V/S/H) for OWNER/MANAGER/SUPERVISOR/DRIVER/AGENT/FARMER vs mobile catalog + nav shell; P0 DRIVER Ops-tab landing bug and fleet stubs for field ops; §9 Pre-publish QA (Playwright smoke/role-screen, pytest RBAC, Android unit vs Espresso/Compose gap)
- **Playwright role × screen smoke** — `frontend/e2e/tests/workflows/settings/role-screen-smoke.spec.ts`: OWNER (+ demo MANAGER/AGENT when seeded) visits main nav routes; SUPERVISOR/DRIVER/FARMER via `E2E_<ROLE>_EMAIL`/`PASSWORD` only
- **Field-service diesel receipts + ledger sync** — `diesel_amount > 0` on create/update posts/updates a Fuel expense (`source_type=field_service`, response `diesel_expense_id`); cancel/delete reverses it. OpenAPI `LinkEntityType` includes `field_service`. Web detail uploads diesel receipts (`fuel_bill`) and work photos; comment thread already live.
- **Android cancel/reverse + `[kf:work]` field-service profiles** — external `krishifarms-mobile`: procurement detail Cancel/Reverse wired to CRM APIs; vehicle-type work questions persisted as `[kf:work]` comments (see `ANDROID_CRM_PARITY.md`)
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
