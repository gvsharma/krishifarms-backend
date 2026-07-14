# Analytics Hub

**Phase:** 1 (Admin web)  
**Permission:** `dashboard:read`  
**Data plane:** Postgres OLTP + `analytics_daily_org_facts` summary table + Redis/memory cache  
**UI:** `/analytics` (MUI + `@mui/x-charts`)

---

## 1. Information architecture

| Route | Status | Purpose |
|-------|--------|---------|
| `/analytics` | Live | Hub grid of 15 modules |
| `/analytics/executive` | Live | Morning health + money + ops pulse |
| `/analytics/operations` | Live | Day command: tickets, trips, field services |
| `/analytics/procurement` | Live | Volume/value/moisture/crop/village |
| `/analytics/finance` | Live | Expenses, collections, outstanding |
| `/analytics/{scaffold}` | Scaffold | Shell + data-availability (no fake KPIs) |
| `/reports` | Redirect | Merges into Analytics Hub |

Scaffold modules: farming, vehicle, village, farmer, buyer, employee, service, crop-intelligence, inventory, ai-prediction, alerts.

---

## 2. API

| Method | Path | Notes |
|--------|------|-------|
| GET | `/analytics/catalog` | Live vs scaffold registry |
| GET | `/analytics/{module}/summary` | KPIs + series/tables preview |
| GET | `/analytics/{module}/series` | Time series |
| GET | `/analytics/{module}/tables` | Top/bottom tables |
| POST | `/analytics/export` | CSV attachment (Excel/PDF Phase 2) |

Org always from JWT. Filters: `preset` (`today`/`7d`/`30d`/`season`/`custom`), `date_from`, `date_to`, `village_id`, `crop_type_id`, `farmer_id`, `buyer_id`, `asset_id`, `season`.

Cache key: `analytics:{org}:{module}:{kind}:{filter_hash}` · TTL 60–300s · log `analytics.module.latency_ms` + `cache_hit`.

Migration `033`: `analytics_daily_org_facts` for nightly/on-demand rollups; Phase 1 summaries compute live from OLTP (facts table may be empty until job exists).

OpenAPI: `docs/api/paths/analytics.yaml`.

---

## 3. KPI dictionary (Phase 1 live)

### Executive

| KPI | Source | Honesty |
|-----|--------|---------|
| Period revenue | Confirmed procurements `net_amount` + field-service `total_amount` | Labeled estimate |
| Period expenses | Posted `expenses` | Live |
| Gross ops estimate | Revenue − expenses | Estimate (not GAAP) |
| Farmer outstanding | Sum latest `farmer_ledger_entries.balance_after` per farmer | Live |
| Pending farmer payments | Confirmed/`paid_partial` ticket value | Live |
| Active farmers / VIP | `farmers` | Live |
| Vehicles working/idle | Distinct trip assets vs active assets | Live |
| Open procurements | Non-terminal statuses | Live |
| Field services | Non-cancelled in range | Live |
| Cash available | — | **Unavailable** (needs cash book) |
| Weather | — | **Unavailable** |
| Health score | `rules_v1` heuristic | Not ML |

### Operations / Procurement / Finance

Reuse the same OLTP sources. Finance exposes working capital as **unavailable**. Inventory / weather / AI modules never invent numbers.

---

## 4. Data availability matrix

| Source | Executive | Ops | Procurement | Finance | Inventory | AI | Weather |
|--------|-----------|-----|-------------|---------|-----------|----|---------|
| Procurements | ✅ | ✅ | ✅ | ✅ | — | — | — |
| Field services | ✅ | ✅ | — | — | — | — | — |
| Expenses / collections | ✅ | — | — | ✅ | — | — | — |
| Farmer ledger | ✅ | — | — | ✅ | — | — | — |
| Vehicle trips / assets | ✅ | ✅ | — | — | — | — | — |
| Inventory ledger | ❌ | ❌ | ❌ | ❌ | ❌ | — | — |
| Cash book | ❌ | ❌ | ❌ | ❌ | — | — | — |
| Weather / disease | ❌ | ❌ | ❌ | ❌ | — | — | ❌ |
| Model registry | ❌ | ❌ | ❌ | ❌ | — | ❌ | — |

---

## 5. Drill-down & export

KPI cards deep-link to list routes with query filters, e.g. `/procurement?date_from=&date_to=&village_id=`. Procurement + farmers list pages read those params.

CSV export via `POST /analytics/export` and hub **Export CSV** control. Server Excel/PDF + saved-views API → Phase 2. Phase 1 saved views use `localStorage` (`krishi-analytics-filters`).

---

## 6. SLIs

| Metric | Target (demo scale) |
|--------|---------------------|
| Summary p95 cached | &lt; 500ms |
| Summary p95 cold | &lt; 2s |
| Cache TTL | 60–300s |

---

## 7. Frontend layout

```text
frontend/src/app/(app)/analytics/page.tsx
frontend/src/app/(app)/analytics/[module]/page.tsx
frontend/src/features/analytics/
  api.ts, types.ts, filters-store.ts, messages.ts
  components/{AnalyticsShell,KpiGrid,ExportMenu}.tsx
  charts/{LineTrend,BarCompare,DonutShare,HeatmapSimple}.tsx
  modules/{executive,operations,procurement,finance,_scaffold}.tsx
```

Nav: Analytics under Overview for OWNER/MANAGER/ACCOUNTANT (`nav-config.ts`). Telugu chrome keys in `messages.ts`.

---

## 8. Phase 2+

- Vehicle / Village / Farmer / Service / Alerts data-backed subsets  
- Server PDF/Excel; saved views API  
- **Android executive pocket** only (not 15 mobile dashboards) — see [ANDROID_CRM_PARITY.md](./ANDROID_CRM_PARITY.md)  
- Phase 3: inventory schema, weather integrations, ML registry, optional warehouse
