# Android ↔ CRM parity

Inventory of create/update/delete (and admin management) capabilities across the Android field app (`krishifarms-mobile`) and this CRM backend + `frontend/`.

**Android repo path (external):** `/Users/venkatgorinta/StudioProjects/krishifarms-mobile`  
**Branch reviewed:** `feature/device-push-notifications`  
**Last reviewed:** 2026-07-12 (Android cancel/reverse + field-service `[kf:work]` profiles)

## Summary

| Area | Android | CRM API | CRM web admin |
|------|---------|---------|---------------|
| Master data (villages, crops, buyers, agents, prices, vehicle types, activity types, expense categories, payment modes) | ✅ Admin hub (catalog CRUD; villages read-only) | ✅ Live | ✅ Settings → Master data + sidebar |
| Location cascade (District → Mandal → Village) | ✅ Shared `LocationCascade`; procurement + farmer form + field-service create | ✅ `/districts`, `/mandals`, filtered `/villages` | ✅ Wired on villages / farmer / procurement / field-service forms |
| Field services (tractor, transport, fertiliser, seeds, agri-finance, vehicle/godown ops) | ✅ List + create; vehicle-type work profiles (Tractor/Trolley/Bolero/DCM/Pump/Drone) via `[kf:work]` comments | ✅ `/field-services` CRUD | ✅ List + create form with vehicle-type questions |
| Users / roles | ✅ Admin hub; display labels via `RoleLabels` | ✅ Live | ✅ Settings → Users + sidebar |
| Farmers | CRU (+ offline); form sends `village_id` (Room `village_id` col v7) | ✅ Live | ✅ List / detail / create |
| Procurements | ✅ Create + list/detail; draft extras; **full workflow** submit / weigh / price / confirm / **cancel** / **reverse** on detail | ✅ Full workflow | ✅ List / create / detail + workflow actions |
| Workers / work orders / attendance | CRU / CR / CU | 📋 Schema + OpenAPI only | ⬜ Placeholder |
| Expenses | Create + list/detail | 📋 Schema + OpenAPI only | ⬜ Placeholder |
| Farmer payments | Stub | ✅ Thin list/create/allocate/reverse | ✅ List + create on `/payments` (allocate UI deferred) |
| Vehicles / trips / assets / rentals / farms | Stub | ✅ Thin assets/trips/farms APIs | 🟡 Assets list; farms/trips placeholders |
| Documents / comments | Create + list | 🟡 Partial (no entity list filter) / ✅ | 🟡 Comments on detail; upload session-local gallery |
| Devices / FCM | Background register | ✅ Live | N/A |

**Legend:** ✅ Done | 🟡 Partial | 📋 DB + OpenAPI, no Python routes | ⬜ UI placeholder / missing

## Master data detail

| Entity | Android | Backend routes | Web UI |
|--------|---------|----------------|--------|
| Districts / Mandals | `AdminApi` list + `LocationCascade` | `/districts`, `/mandals` CRUD | Cascade selects on forms |
| Villages | Read-only list in Admin; cascade filter on procurement / farmer / field service | `/villages` CRUD (+ filters) | `/settings/villages` |
| Crop types | Admin list + create/edit | `/crop-types` CRUD | `/settings/master-data/crops` |
| Crop price rules | — | `/crop-prices` CRUD | `/settings/master-data/crop-prices` |
| Buyers | Admin list + create/edit; procurement picker | `/buyers` CRUD | `/settings/master-data/buyers` |
| Field agents | Admin list + create/edit | `/agents` CRUD | `/settings/master-data/agents` |
| Vehicle types | Admin list + create/edit | `/vehicle-types` CRUD | `/settings/master-data/vehicle-types` |
| Activity types | Admin list + create/edit | `/activity-types` CRUD | `/settings/master-data/activity-types` |
| Expense categories | Admin list + create/edit | `/expense-categories` CRUD | `/settings/master-data/expense-categories` |
| Payment modes | Admin list + create/edit | `/payment-modes` CRUD | `/settings/master-data/payment-modes` |
| Users / roles | Admin list + create/edit (no delete); `RoleLabels` | `/users`, `/roles` | `/settings/users` |

## RBAC (codes match `app/shared/permissions.py`)

| Role code | Display name | OWNER | MANAGER | Notes |
|-----------|--------------|-------|---------|-------|
| `OWNER` | Admin / Owner | ✅ full | — | Deletes + `users:create` |
| `MANAGER` | Manager | — | ✅ create/update | No `:delete`; no `users:create` |
| `SUPERVISOR` | Farming Supervisor | field lead | farmers / procurement / field services | |
| `DRIVER` | Vehicle Supervisor | fleet soft-wire | transport / diesel / field-service read | |
| `AGENT` | Agent | field services C/U | farmer + location read | Mobile catalog includes `FIELD_SERVICE_*` + `FARMER_VIEW` |
| `FARMER` | Farmer | read-only | portal soft-wire | |
| `WORKER` | Worker | work orders | | |
| `ACCOUNTANT` | Accountant | finance | mobile catalog; DB role optional | |

## Implementation backlog (Android — external repo)

| Priority | Item | Target files (Android) | Depends on CRM |
|----------|------|------------------------|----------------|
| **P1** | Procurement photos (reuse expense `BillAttachmentPicker`) | `ProcurementFormScreen` | documents API partial |
| **P1** | Crop price rules admin catalog | `AdminCatalogType`, `AdminApi` | ✅ `/crop-prices` |
| **P2** | GPS capture on field forms | CameraX / FusedLocation | optional |
| **P2** | Workers / expenses live sync when CRM routers land | existing feature packages | 📋 schema only |
| **P2** | Farmer payments Android | stub → thin API | ✅ `/farmer-payments` |

### Done this iteration (Android)

- Procurement cancel / reverse on detail (`ProcurementApi` + reason dialogs; cancel = `PROCUREMENT_DELETE` / reverse = OWNER + `PROCUREMENT_APPROVE`)
- Field-service vehicle work profiles: Tractor/Trolley/Bolero/DCM/Pump/Drone questions; `[kf:work]` comment codec + `vehicle_type_id` on create
- Prior: Field-services list + create; farmer `village_id` cascade; procurement submit / weigh / price / confirm

## Phase 2+ partial / external

- Entity document gallery needs `GET /documents?entity_type=&entity_id=` (CRM done; Android photo attach optional)
- Finance ops expenses/collections still schema-only on backend (or newly landing — check Android sync)
- WhatsApp / full Firebase OTP UX

## Mobile sync note

Android admin screens call live CRM catalog APIs. Do not regress FCM / locale work on `feature/device-push-notifications`.

## Verify

```bash
# Backend
cd /Users/venkatgorinta/Desktop/CRM
# GET /api/v1/field-services, POST /farmer-payments, GET /farmers

# Frontend
cd frontend && npm run dev
# /payments — list + Record payment; /login phone-or-email Sign in
# Procurement detail workflow + photo upload (session list)

# Android
cd /Users/venkatgorinta/StudioProjects/krishifarms-mobile
# Field services create: pick Tractor/Trolley/Bolero/DCM → work questions; comments contain [kf:work]
# Procurement detail: Cancel (draft/weighment/weighed) + Reverse (confirmed, OWNER)
```
