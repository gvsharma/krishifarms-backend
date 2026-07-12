# Android ↔ CRM parity

Inventory of create/update/delete (and admin management) capabilities across the Android field app (`krishifarms-mobile`) and this CRM backend + `frontend/`.

**Last reviewed:** 2026-07-12

## Summary

| Area | Android | CRM API | CRM web admin |
|------|---------|---------|---------------|
| Master data (villages, crops, buyers, agents, prices, vehicle types, activity types, expense categories, payment modes) | No admin UI (hardcoded / read-only pickers) | ✅ Live | ✅ Settings → Master data |
| Field services (tractor, transport, fertiliser, seeds, agri-finance, vehicle/godown ops) | Stub / hardcoded | ✅ `/field-services` CRUD | 🟡 List placeholder `/field-services` |
| Users / roles | None (profile read-only) | ✅ Live | ✅ Settings → Users (create/edit) |
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
| Villages | Free-text on farmer form | `/villages` CRUD | `/settings/villages` |
| Crop types | Hardcoded + `GET crop-types` on procurement | `/crop-types` CRUD (seed: paddy, corn, vegetables, pulses, concretework) | `/settings/master-data/crops` |
| Crop price rules | Unused `apply-price` API | `/crop-prices` CRUD | `/settings/master-data/crop-prices` |
| Buyers | — | `/buyers` CRUD | `/settings/master-data/buyers` |
| Field agents | — | `/agents` CRUD | `/settings/master-data/agents` |
| Vehicle types | — (vehicles stub) | `/vehicle-types` CRUD | `/settings/master-data/vehicle-types` |
| Activity types | Hardcoded enum | `/activity-types` CRUD (+ `service_category`) | `/settings/master-data/activity-types` |
| Expense categories | Hardcoded enum | `/expense-categories` CRUD | `/settings/master-data/expense-categories` |
| Payment modes | — | `/payment-modes` CRUD | `/settings/master-data/payment-modes` |
| Users / roles | — | `/users`, `/roles` | `/settings/users` |

## Phase 2+ not yet implementable as live CRM modules

These have migrations + OpenAPI but **no** Python routers in `app/main.py`:

- Farmer payments / ledger reverse flows beyond procurement confirm
- Workers, work orders, attendance
- Expenses, collections, operational payments
- Assets, vehicle trips, rentals, farms
- Global search, AI/OCR extensions

Android already has real UI for **workers / work orders / attendance / expenses**; those are the next highest-value API builds for mobile↔CRM sync. Vehicles/trips remain stubs on both sides.

## Mobile sync note

Android should prefer CRM master-data endpoints over hardcoded enums as those screens are built. Do not regress FCM / locale work on `feature/device-push-notifications`.

## Verify

```bash
# Backend
cd /Users/venkatgorinta/Desktop/CRM
# with API running:
# GET /api/v1/payment-modes, /buyers, /crop-types, /activity-types, /vehicle-types, /crop-prices, /expense-categories

# Frontend
cd frontend && npm run dev
# Sign in → Settings → Users / Villages / Master data — exercise Add / Edit / Delete
# Farmers → Add farmer; Procurement → New draft
```
