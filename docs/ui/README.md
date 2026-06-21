# KrishiFarms CRM — Next.js UI/UX Design System

**Product:** Enterprise SaaS CRM for agricultural procurement and farm operations  
**Domain:** Bhairkhanpally, Telangana — Paddy & Corn, INR, bilingual EN/TE  
**Platform:** Next.js 15 (App Router) · TypeScript · Tailwind CSS · shadcn/ui · TanStack Query · Zustand  
**Status:** Design documentation only (no implementation in `frontend/` yet)

> **Stack note:** Frontend is **Next.js only** (Vercel). Earlier Flutter Web docs (`FLUTTER_ARCHITECTURE.md`, `WIDGET_TREE.md`) are superseded by [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md) and [COMPONENT_TREE.md](./COMPONENT_TREE.md).

---

## Why Next.js (not Flutter)

| Reason | Detail |
|--------|--------|
| **Vercel deploy** | `frontend/` placeholder + `vercel.json` already target Vercel; same-origin `/api/v1` proxy to EC2 |
| **Gamya parity** | Sibling [Gamya Couture](https://github.com/gvsharma/gamyaboutique) frontend uses the same stack — proven App Router + TanStack Query + Zustand pattern |
| **Dashboard SaaS velocity** | Dense CRM tables, command palette, and role-based shells fit React + shadcn/ui faster than Flutter Web for this team |
| **Mobile** | Responsive web first; optional PWA later — **not** a separate Flutter mobile app |

---

## Design North Star

KrishiFarms CRM should feel like **Linear meets Stripe Dashboard for Indian farm operations** — fast, dense when needed, calm when scanning, and never a generic admin template. Every screen answers an operational question: *How much paddy did we buy today? Who is still owed? Which trip is in transit?*

**Inspiration (patterns, not clones):** Linear (speed, keyboard, detail pages), Stripe (customer 360, metrics strip), Notion (tabs, contextual panels), Ramp/Brex (financial dashboards, approvals), modern ERP (role-based density, audit trails).

---

## Document Index

| Document | Purpose |
|----------|---------|
| [INFORMATION_ARCHITECTURE.md](./INFORMATION_ARCHITECTURE.md) | Nav tree, role matrix, entity relationships, global vs contextual nav |
| [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md) | Tokens, typography, color, grid, Tailwind/shadcn theming, density modes |
| [COMPONENT_LIBRARY.md](./COMPONENT_LIBRARY.md) | App shell, tables, filters, KPIs, timelines, overlays |
| [NAVIGATION_AND_FLOWS.md](./NAVIGATION_AND_FLOWS.md) | Flow diagrams, journeys, keyboard shortcuts, search |
| [WIREFRAMES.md](./WIREFRAMES.md) | ASCII wireframes for key screens |
| [COMPONENT_TREE.md](./COMPONENT_TREE.md) | React component hierarchy per major screen |
| [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md) | Folder structure, RSC strategy, state, routing, API alignment |
| [SCREEN_SPECS.md](./SCREEN_SPECS.md) | Screen-by-screen specs with API sources and states |
| [ACCESSIBILITY_AND_UX.md](./ACCESSIBILITY_AND_UX.md) | WCAG, keyboard, SR, responsive, export patterns |

---

## Core Design Principles

### 1. Operations-first, not CRUD-first

Lists are **work queues** with saved views and smart filters — not bare tables. Detail pages are **360° profiles** with a metrics strip and tabbed context. Workflows (collection entry, payment settlement) use **timelines and status rails**, not multi-step wizards with "Next" buttons.

### 2. Role-native surfaces

A Field Officer lands on **Collection Entry**; an Accountant on **Payments & Outstanding**; the CEO on **Profitability**. Same app shell, different default home and nav emphasis. Hide nav items the role cannot access — never show disabled ghosts that 403 on click.

### 3. Bilingual by design

Primary UI strings via `next-intl` message files (`messages/en.json`, `messages/te.json`). Entity display names prefer `Accept-Language`: show `full_name_te` when locale is Telugu and field is populated. Numbers always use **Indian grouping** (₹12,34,567.00). Weights show **quintals** in labels with kg in detail (`45 qtl · 4,500 kg`).

### 4. Money and ledger integrity

All amounts `Decimal` / string in UI models — never `float`. Ledger views are **read-only** with reversal entries styled distinctly (muted, strikethrough debit/credit). Confirm destructive financial actions with typed confirmation or idempotency awareness.

### 5. Phase-aware data sources

Backend Python is **Phase 1 only**; OpenAPI + DB schema cover Phases 1–5. UI specs mark each component's data source:

| Badge | Meaning |
|-------|---------|
| **P1** | Live API today (`auth`, `users`, `villages`, `crop-types`, `documents`, `audit`, `dashboard/summary` stub) |
| **P2** | OpenAPI ready — farmers, procurements, farmer payments, ledger |
| **P3+** | Collections, expenses, operational payments |
| **P4–5** | Workforce, assets, rentals, global search |

Design full product UX now; implement with feature flags and mock adapters where APIs are not live.

### 6. Performance on low bandwidth

Skeleton loaders over spinners. Paginate at 20–50 rows. Presigned document thumbnails lazy-load. Command palette debounces search 300 ms. Prefer summary KPI cards over chart-heavy pages on first paint.

### 7. Auditability visible in UI

Material changes show **who / when** in slide-over footers. Activity timeline on profiles links to `audit-logs` where permitted. Bulk actions require confirmation with count summary.

---

## Personas (UX roles → backend RBAC)

| UX Persona | Maps to DB role | Primary jobs |
|------------|-----------------|--------------|
| **Super Admin** | `OWNER` | Org setup, users, master data, all dashboards |
| **Procurement Manager** | `MANAGER` (procurement scope) | Intake volume, rates, deductions, dispatch |
| **Accountant** | `MANAGER` (finance scope) | Payments, ledger, expenses, collections, P&L |
| **Field Officer** | `SUPERVISOR` | Collection entry, farmer onboarding, weighment docs |
| **Farm Manager** | `SUPERVISOR` + farms | Workforce, fleet, farm ops, rentals |

Full permission mapping: [INFORMATION_ARCHITECTURE.md § Role matrix](./INFORMATION_ARCHITECTURE.md#role-based-navigation-matrix).

---

## Key Domain Entities (UI vocabulary)

Use consistent labels across nav, search, and command palette:

| Entity | Code example | Notes |
|--------|--------------|-------|
| Farmer | `FRM-0042` | Village, phone, outstanding |
| Procurement | `PR-2026-0142` | Partitioned by `procurement_date` |
| Farmer payment | `FP-2026-0088` | Advance / final / adjustment |
| Collection | Rental / other cash in | Links UPI screenshots |
| Village | Bhairkhanpally | Master data |
| Crop type | Paddy, Corn | Bilingual names |
| Vehicle trip | Trip per `asset_id` | Fuel, loading charges |
| Work order | Linked to farm + worker | Photo evidence |
| Document | `crop_bill`, `upi_screenshot` | S3 presign flow |

---

## Implementation Prioritization (summary)

See [SCREEN_SPECS.md § Phase roadmap](./SCREEN_SPECS.md#implementation-phase-roadmap) for detail.

**Phase 1 screens:** Auth, app shell, settings (users, villages, crops, expense categories), documents library, audit/activity, dashboard shell with P1 KPI placeholders.

**Phase 2 screens:** Farmers 360, procurement board + collection timeline, farmer payments — core revenue path.

**Phase 3+:** Expenses, collections dashboard, fleet, workforce, rentals, global search, full profitability.

---

## Related Backend Docs

- [AGENT_GUIDE.md](../AGENT_GUIDE.md) — implementation status matrix
- [API_CONTRACT.md](../api/API_CONTRACT.md) — endpoints and envelopes
- [kpi_definitions.md](../reporting/kpi_definitions.md) — dashboard KPIs
- [DOCUMENT_MANAGEMENT.md](../modules/DOCUMENT_MANAGEMENT.md) — upload/OCR UX
- [frontend/README.md](../../frontend/README.md) — Vercel placeholder + env vars

---

## Changelog

UI design docs under `docs/ui/` — see [CHANGELOG.md](../CHANGELOG.md).
