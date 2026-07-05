# Product Roadmap — KrishiFarms CRM

Phased delivery horizons for backend, web admin, and mobile field apps.

## Horizon 1 — Platform foundation (Phase 1 / 1b) ✅

- Auth (password + Firebase OTP), RBAC, org multi-tenancy
- Master data: villages, crop types, expense categories
- Platform admin: buyers, agents, activity types, vehicle types, crop prices
- Polymorphic comments + tags, audit log, activity feed
- Documents (partial), dashboard shell

## Horizon 2 — Core operations (Phase 2a / 2b)

| Track | Scope | Status |
|-------|-------|--------|
| **2a Farmers** | Farmer CRUD, comments/tags, audit | ✅ Python |
| **2b Procurement** | Ticket state machine, pricing snapshot, ledger debit | 📋 spec |
| **2b Farmer payments** | Payments, outstanding, ledger credit | 📋 schema |
| **2b Farmer sub-resources** | Bank accounts, land parcels (GPS), crop history | 📋 schema |

## Horizon 3 — Services & finance

- Workforce: workers, work orders, attendance
- Expenses, collections, operating payments
- Rentals, asset register
- Web admin UI for settings + operational modules

## Horizon 4 — Fleet & farms

- Farms / land blocks
- Vehicle trips, fuel, maintenance
- Asset depreciation

## Horizon 5 — Intelligence & scale

- AI/OCR document ingestion
- Global search, advanced reporting
- Multi-site / multi-org analytics
- Rating engine (farmer reliability from procurement + payment history)

## Dependency graph

```text
Platform (1b) → Farmers (2a) → Procurement (2b) → Ledger/Payments (2b)
                              → Workforce (3)     → Expenses/Finance (3)
                              → Fleet/Assets (4)  → Reporting/AI (5)
```

## Doc index

| Phase | Module docs |
|-------|-------------|
| 1b | [ADMIN_PLATFORM.md](./modules/ADMIN_PLATFORM.md), [CROSS_CUTTING.md](./modules/CROSS_CUTTING.md) |
| 2a | [FARMERS.md](./modules/FARMERS.md) |
| 2b | [PROCUREMENT.md](./modules/PROCUREMENT.md) |

Implementation status: [AGENT_GUIDE.md](./AGENT_GUIDE.md#3-implementation-status-matrix).
