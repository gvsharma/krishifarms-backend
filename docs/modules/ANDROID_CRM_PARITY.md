# Android ↔ CRM parity

Inventory of create/update/delete (and admin management) capabilities across the Android field app (`krishifarms-mobile`) and this CRM backend + `frontend/`.

**Last reviewed:** 2026-07-12

## Summary

| Area | Android | CRM API | CRM web admin |
|------|---------|---------|---------------|
| Master data (villages, crops, buyers, agents, prices, vehicle types, activity types, expense categories, payment modes) | ✅ Admin hub (catalog CRUD; villages read-only) | ✅ Live | ✅ Settings → Master data + sidebar |
| Field services (tractor, transport, fertiliser, seeds, agri-finance, vehicle/godown ops) | Stub / hardcoded | ✅ `/field-services` CRUD | 🟡 List placeholder `/field-services` |
| Users / roles | ✅ Admin hub list/create/edit (no delete) | ✅ Live | ✅ Settings → Users + sidebar |
| Farmers | CRU (+ offline) | ✅ Live | ✅ List / detail / create |
| Procurements | Create + list/detail | ✅ Full workflow | 🟡 List / create draft / detail (no workflow buttons) |
| Workers / work orders / attendance | CRU / CR / CU | 📋 Schema + OpenAPI only | ⬜ Placeholder |
| Expenses | Create + list/detail | 📋 Schema + OpenAPI only | ⬜ Placeholder |
| Farmer payments / collections / payments | Stub | 📋 Schema + OpenAPI only | ⬜ Placeholder |
| Vehicles / trips / assets / rentals / farms | Stub | 📋 Schema + OpenAPI only | ⬜ Placeholder |
| Documents / comments | Create + list | 🟡 Partial / ✅ | 🟡 Comments on detail; documents not in web nav |
| Devices / FCM | Background register | ✅ Live | N/A |

**Legend:** ✅ Done | 🟡 Partial | 📋 DB + OpenAPI, no Python routes | ⬜ UI placeholder / missing

## Master data detail

| Entity | Android | Backend routes | Web UI |
|--------|---------|----------------|--------|
| Villages | Read-only list in Admin | `/villages` CRUD | `/settings/villages` |
| Crop types | Admin list + create/edit | `/crop-types` CRUD | `/settings/master-data/crops` |
| Crop price rules | — | `/crop-prices` CRUD | `/settings/master-data/crop-prices` |
| Buyers | Admin list + create/edit | `/buyers` CRUD | `/settings/master-data/buyers` |
| Field agents | Admin list + create/edit | `/agents` CRUD | `/settings/master-data/agents` |
| Vehicle types | Admin list + create/edit | `/vehicle-types` CRUD | `/settings/master-data/vehicle-types` |
| Activity types | Admin list + create/edit | `/activity-types` CRUD | `/settings/master-data/activity-types` |
| Expense categories | Admin list + create/edit | `/expense-categories` CRUD | `/settings/master-data/expense-categories` |
| Payment modes | Admin list + create/edit | `/payment-modes` CRUD | `/settings/master-data/payment-modes` |
| Users / roles | Admin list + create/edit (no delete) | `/users`, `/roles` | `/settings/users` |

## RBAC (OWNER vs MANAGER)

| Action | OWNER | MANAGER |
|--------|-------|---------|
| View admin / master data | ✅ | ✅ |
| Create / edit catalogs | ✅ | ✅ |
| Delete catalogs | ✅ | ❌ (UI hidden; API 403) |
| Create / edit users | ✅ | ✅ |
| Delete users | N/A (no API) | N/A |

Android: **More** hub and **Settings → Open admin hub** for OWNER/MANAGER; delete icon owner-only. Web: sidebar **Users** + **Master data**; dashboard admin cards; delete buttons owner-only via `/auth/me` roles.

## Phase 2+ not yet implementable as live CRM modules

These have migrations + OpenAPI but **no** Python routers in `app/main.py`:

- Farmer payments / ledger reverse flows beyond procurement confirm
- Workers, work orders, attendance
- Expenses, collections, operational payments
- Assets, vehicle trips, rentals, farms
- Global search, AI/OCR extensions

Android already has real UI for **workers / work orders / attendance / expenses**; those are the next highest-value API builds for mobile↔CRM sync. Vehicles/trips remain stubs on both sides.

## Mobile sync note

Android admin screens call live CRM catalog APIs. Do not regress FCM / locale work on `feature/device-push-notifications`.

## Verify

```bash
# Backend
cd /Users/venkatgorinta/Desktop/CRM
# with API running:
# GET /api/v1/payment-modes, /buyers, /crop-types, /activity-types, /vehicle-types, /crop-prices, /expense-categories

# Frontend (Owner)
cd frontend && npm run dev
# Sign in as owner@krishifarms.local → Home admin cards / sidebar Users + Master data → Add / Edit / Delete

# Frontend (Manager) — create manager user or use seeded role
# Same flows; Delete buttons must be hidden

# Android
# Login as OWNER or MANAGER → More → Admin (or Settings → Open admin hub)
# Exercise catalog list + FAB create + edit; villages read-only; users create/edit
```
