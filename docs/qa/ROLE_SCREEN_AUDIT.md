# Role × Screen Audit — KrishiFarms Mobile

**Android repo:** `/Users/venkatgorinta/StudioProjects/krishifarms-mobile`  
**Sources of truth:** `Permission.kt`, `MenuRegistry` / `DynamicMenuProvider`, `MainBottomNav`, `NavigationGuard` / `ScreenAccess`, CRM `app/modules/auth/permission_catalog.py` + `rbac.py`  
**Parity cross-check:** [docs/modules/ANDROID_CRM_PARITY.md](../modules/ANDROID_CRM_PARITY.md)  
**Audited:** 2026-07-13  
**Scope:** OWNER/Admin, MANAGER, SUPERVISOR (Farming), DRIVER (Vehicle Supervisor), AGENT, FARMER

---

## 1. RBAC / navigation shell (how visibility works)

| Layer | Behavior |
|-------|----------|
| Login payload | CRM `build_rbac_payload` → `roles`, `permissions` (mobile codes), `accessibleModules` |
| Module list | `derive_accessible_modules`: module shown if user has any of `MODULE_VIEW_PERMISSIONS[module]` |
| Drawer + More hub | `DynamicMenuProvider.visibleEntries` — dashboard always; else module in `accessibleModules` **or** matching view permission |
| Bottom nav | `MainBottomNav`: **Home** + **More** always; Ops / Collect / Finance if any of their `moduleIds` intersect `accessibleModules` |
| Route guard | `NavigationGuard` + `ScreenAccess` — empty required set → authenticated only (Dashboard, More) |
| Action gates | Per-screen (`FIELD_SERVICE_CREATE`, `PROCUREMENT_DELETE`, Admin `SETTINGS_MANAGE` / `USER_MANAGE`, etc.) |

**Bottom-nav groups**

| Tab | Module IDs | Default landing (`firstAccessibleRoute`) |
|-----|------------|------------------------------------------|
| Home | `dashboard` | Dashboard |
| Operations | farmers, farms, procurement, field_services, workers, work_orders, attendance | farmers → procurement → workers **only** (no `field_services`) |
| Collect | collections, farmer_payments | collections → farmer_payments |
| Finance | expenses, payments | expenses → payments |
| More | documents, settings, sync, vehicles, assets, rentals (+ hub shows all non-dashboard menu entries) | `Routes.MORE` |

**Feature UI status (Android `MainNavGraph`)**

| Status | Modules |
|--------|---------|
| **Live** | dashboard, farmers, procurement, field_services, workers, work_orders, attendance, expenses, documents, admin, settings, sync |
| **Stub** (`FeatureStubScreen`) | farms, farmer_payments, collections, payments, vehicles, vehicle_trips, assets, rentals |

---

## 2. Accessible modules by role (from CRM mobile catalog)

Derived via `ROLE_MOBILE_PERMISSIONS` → `derive_accessible_modules` (matches production login when DB role code is set).

| Role | Bottom tabs | Accessible modules |
|------|-------------|-------------------|
| **OWNER** | Home, Ops, Collect, Finance, More | all 20 modules |
| **MANAGER** | Home, Ops, Collect, Finance, More | same as OWNER (no deletes in catalog; still has admin/user manage) |
| **SUPERVISOR** | Home, Ops, More | dashboard, farmers, farms, procurement, field_services, workers, work_orders, attendance, vehicles, vehicle_trips, assets, documents, settings, sync |
| **DRIVER** | Home, Ops, More | dashboard, field_services, vehicles, vehicle_trips, assets, settings, sync |
| **AGENT** | Home, Ops, More | dashboard, farmers, field_services, settings, sync |
| **FARMER** | Home, Ops, More | dashboard, farmers, farms, procurement, field_services, documents, settings, sync |

---

## 3. Role × Module matrix

Legend: **V** = visible + live UI · **S** = visible but stub · **H** = hidden · **M** = missing / broken for role intent

| Module | OWNER | MANAGER | SUPERVISOR | DRIVER | AGENT | FARMER |
|--------|:-----:|:-------:|:----------:|:------:|:-----:|:------:|
| dashboard | V | V | V | V | V | V |
| farmers | V | V | V | H | V (read) | V (read) |
| farms | S | S | S | H | H | S |
| procurement | V | V | V | H | H | V (read) |
| field_services | V | V | V | V | V | V (read; no create) |
| farmer_payments | S | S | H | H | H | H |
| workers | V† | V† | V† | H | H | H |
| work_orders | V† | V† | V† | H | H | H |
| attendance | V† | V† | V† | H | H | H |
| expenses | V | V | H | H | H | H |
| collections | S | S | H | H | H | H |
| payments | S | S | H | H | H | H |
| vehicles | S | S | S | S (**M**) | H | H |
| vehicle_trips | S | S | S | S (**M**) | H | H |
| assets | S | S | S | S (**M**) | H | H |
| rentals | S | S | H | H | H | H |
| documents | V | V | V | H | H | V |
| admin | V | V | H | H | H | H |
| settings | V | V | V | V | V | V |
| sync | V | V | V‡ | V‡ | V‡ | V‡ |

† Workforce screens are implemented locally; CRM workforce routers still schema/OpenAPI-ahead (parity).  
‡ `sync` module granted via `SETTINGS_VIEW` intersection in `MODULE_VIEW_PERMISSIONS` — Sync **debug** screen reachable for all roles with settings.

---

## 4. Per-role screen map (bottom nav / More / features)

### OWNER / Admin & MANAGER

- **Bottom:** all five tabs.
- **Ops landing:** Farmers (live).
- **Collect / Finance:** tabs visible; Collect → collections **stub**; Finance → expenses **live** (payments stub still in More).
- **More / drawer:** full module grid including Admin hub (catalogs + users).
- **Parity:** Admin CRUD + procurement workflow + field services align with parity doc. Fleet / rentals / farmer payments still stub on Android despite CRM thin APIs for some.

### SUPERVISOR (Farming)

- **Bottom:** Home, Ops, More (no Collect/Finance).
- **Should see (and does):** farmers, procurement, field_services, documents, workforce trio, settings.
- **Also sees stubs:** farms, vehicles, trips, assets (catalog grants view; UI stub).
- **Gap vs CRM `permissions.py`:** API role lacks `workers:*` / `work_orders:*`; mobile catalog still grants `WORKER_*` / `WORK_ORDER_*` / `ATTENDANCE_*` — menu can show workforce while API calls may 403 if only DB role permissions apply on those routes.

### DRIVER (Vehicle Supervisor) — field ops critical

- **Bottom:** Home, Ops, More.
- **Live only:** field_services (+ dashboard / settings / sync).
- **Intended core:** vehicles, trips, assets → all **stubs** while CRM has thin assets/trips APIs (parity backlog / soft-wire).
- **P0 bug:** Ops tab `moduleIds` includes `field_services`, but `firstAccessibleRoute` candidates are only farmers / procurement / workers. DRIVER has none → **fallback navigates to `farmers`** → `NavigationGuard` denies → snackbar. Ops tab is effectively broken for DRIVER.
- **More hub:** field services live; fleet tiles stub.

### AGENT — field ops critical

- **Bottom:** Home, Ops, More.
- **Visible live:** farmers (read-only), field_services (create/update), settings, sync.
- **Ops landing:** farmers (OK because `FARMER_VIEW` present).
- **Hidden by design (catalog):** procurement, documents, workforce, finance, fleet.
- **Gaps:** no farmer create; no documents attach from agent flows; no agent-scoped “my assignments” UX — org-wide farmer list + field-service C/U only. CRM `permissions.py` AGENT also lacks `documents:*` (aligned).

### FARMER — field ops / portal critical

- **Bottom:** Home, Ops, More.
- **Visible:** farmers, farms (**stub**), procurement (read), field_services (read, no FAB), documents, settings, sync.
- **Catalog:** read-only soft-wire (no create/update).
- **Gaps:** no farmer-portal scoping (no evidence of “self only” filters on farmers/procurements/field-services APIs); farms stub clutters Ops/More; no outstanding / ledger / “my payments” surface on mobile (web has farmer payments; Android stub for staff payments only and FARMER lacks `PAYMENT_VIEW`).

---

## 5. Unit tests run

| Suite | Result |
|-------|--------|
| Android `com.krishifarms.mobile.core.security.rbac.*` (`PermissionManagerTest`, `MenuRegistryTest`, `DynamicMenuProviderTest`, `NavigationGuardTest`, `RoleLabelsTest`) | **PASS** (`./gradlew :app:testDebugUnitTest --tests '…rbac.*'`) |
| CRM `tests/test_auth_rbac.py` (catalog roles, agent field_services module, farmer read-only) | Present; not re-run in this pass (logic exercised via `python3` module derivation) |

**Not covered by unit tests (needs emulator / device):**

- Bottom-nav Ops landing bug for DRIVER
- More hub tile layout / copy per role
- Guarded deep links + forbidden snackbar UX
- Live API 403 vs menu visibility (SUPERVISOR workforce, DRIVER assets create)
- Offline sync + FCM deep links
- Field-service create with `[kf:work]` profiles end-to-end
- Farmer portal data isolation

---

## 6. Critical gaps — field ops roles

### P0

1. **DRIVER Ops tab broken** — `MainBottomNav.firstAccessibleRoute` omits `field_services` (and farms / attendance / work_orders); DRIVER Ops click → farmers → forbidden.
2. **DRIVER fleet UX missing** — vehicles / trips / assets are stubs; Vehicle Supervisor cannot run fleet workflows on device despite CRM thin APIs + role intent in parity.

### P1

3. **AGENT cannot create farmers** — field onboarding may require OWNER/MANAGER/SUPERVISOR; agent limited to field-service C/U + farmer read.
4. **AGENT / FARMER lack documents module** — cannot attach photos from More; may rely on nested entity flows only where wired.
5. **FARMER portal soft-wire only** — org-wide lists likely; no self-scoped home, outstanding, or payments.
6. **SUPERVISOR sees fleet stubs + farms stub** — noisy More hub; farms never implemented on Android.
7. **Sync debug exposed** to AGENT/DRIVER/SUPERVISOR/FARMER via `SETTINGS_VIEW` → `sync` module mapping.

### P2 / parity drift

8. Android farmer_payments / collections still stub while CRM `/farmer-payments` and collections APIs are live (staff roles).
9. Mobile catalog vs `permissions.py` mismatch for SUPERVISOR workforce permissions.
10. Ops landing preference order ignores `field_services` even for AGENT when farmers module removed in future.

---

## 7. Recommended fixes (Android — no code in this audit)

1. Extend Ops `firstAccessibleRoute` candidates:  
   `field_services` → `farmers` → `procurement` → `workers` → `work_orders` → `attendance` → `farms`.
2. Wire DRIVER fleet screens to CRM assets / vehicle-trips (or hide stub modules until ready).
3. Tighten `MODULE_VIEW_PERMISSIONS["sync"]` to `SYNC_MANAGE` only (or gate SyncDebug behind debug build).
4. Farmer portal: filter lists by linked farmer/user; hide farms stub until live.
5. Align SUPERVISOR mobile catalog with API RBAC (grant or remove workforce).

---

## 8. Device test checklist (manual)

- [ ] Login as each of 6 roles; photograph bottom nav + More grid
- [ ] DRIVER: tap Ops — expect Field Services (after fix), not forbidden
- [ ] AGENT: create field service with Tractor `[kf:work]`; confirm no procurement tile
- [ ] SUPERVISOR: create farmer + procurement submit; open workers (note API errors if any)
- [ ] FARMER: confirm no create FABs; attempt deep-link to create routes → forbidden
- [ ] OWNER: Admin hub catalogs + user manage

---

## 9. Pre-publish QA (automated)

Yes — exercise screens/RBAC with existing frameworks before publishing. Full 6-role UI coverage is partial today; use this stack.

### Web (Playwright — `frontend/e2e/`)

```bash
cd frontend && npm install && npx playwright install chromium

# Role smoke before release (OWNER always; MANAGER/AGENT if demo seed present)
npm run test:e2e:smoke
npx playwright test e2e/tests/workflows/settings/role-screen-smoke.spec.ts --project=workflow

# Broader pre-publish web gate
npm run test:e2e:workflow
```

| Suite | Command | Notes |
|-------|---------|--------|
| Smoke | `npm run test:e2e:smoke` | Login, dashboard, nav (~OWNER storageState) |
| Role × screen | `npx playwright test e2e/tests/workflows/settings/role-screen-smoke.spec.ts --project=workflow` | OWNER + demo MANAGER/AGENT; SUPERVISOR/DRIVER/FARMER only if `E2E_<ROLE>_EMAIL` + `E2E_<ROLE>_PASSWORD` set |
| Workflows | `npm run test:e2e:workflow` | Settings/ops/finance journeys |

**Extend later:** a dedicated role × screen project that logs in as all six roles and asserts 200 / visible heading / no permission toast on key routes — blocked today because e2e fixtures only guarantee OWNER (`E2E_EMAIL` / `ChangeMe123!`); demo seed adds MANAGER + AGENT (`DemoPass123!`); SUPERVISOR/DRIVER/FARMER need seed + env credentials (do not invent passwords).

Local UI: `PLAYWRIGHT_BASE_URL=http://localhost:3000` (see [frontend/e2e/README.md](../../frontend/e2e/README.md)).

### Backend (pytest RBAC)

```bash
pytest tests/test_auth_rbac.py tests/test_role_definitions.py tests/test_farmers_rbac.py -q
# Optional broader gate:
pytest tests/test_expenses.py tests/test_field_services.py tests/test_procurements.py -q
```

### Android (external `krishifarms-mobile`)

- **Have:** unit/catalog RBAC tests aligned with CRM `permission_catalog.py` / `ROLE_DEFINITIONS`.
- **Gap:** no Espresso / Compose UI suite that logs in per role and walks bottom-nav + More routes (manual §8 until added).

### Minimal pre-publish checklist

```bash
# 1) Backend RBAC
pytest tests/test_auth_rbac.py tests/test_role_definitions.py tests/test_farmers_rbac.py -q

# 2) Web smoke + role screen smoke
cd frontend && npm run test:e2e:smoke
npx playwright test e2e/tests/workflows/settings/role-screen-smoke.spec.ts --project=workflow

# 3) Android — unit RBAC in mobile repo + manual §8 for DRIVER Ops / AGENT / FARMER
```
