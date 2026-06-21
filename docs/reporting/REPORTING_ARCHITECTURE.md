# KrishiFarms CRM — Reporting Architecture

**Version:** 1.0  
**Schema baseline:** Alembic migrations through `202506210015`  
**Domain:** Bhairkhanpally village operations; crops Paddy, Corn (and org-configured `crop_types`)

---

## 1. Executive Summary

KrishiFarms CRM reporting is built directly on the operational PostgreSQL schema. There is no separate warehouse today; analytics flow through **parameterized SQL** (see `docs/reporting/sql/`) executed by the API or a BI tool (Metabase, Grafana, Superset) against the same database.

Eight operational dashboards cover procurement, farmer payments, workforce, fleet, rentals, expenses, profitability, and farm operations. All queries enforce **multi-tenant isolation** via `org_id` and respect **partition pruning** on date-keyed tables.

---

## 2. Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Presentation — React dashboards / Metabase / API aggregation endpoints │
├─────────────────────────────────────────────────────────────────────────┤
│  Semantic layer — KPI definitions (kpi_definitions.md), date grains,    │
│                    RBAC dashboard registry, drill-down routes           │
├─────────────────────────────────────────────────────────────────────────┤
│  Reporting views (Phase 1b) — regular views wrapping soft-delete +      │
│                    org filters; optional materialized views (see §6)    │
├─────────────────────────────────────────────────────────────────────────┤
│  Operational tables — partitioned facts + dimension tables (org-scoped) │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Raw tables (facts)

| Fact table | Partition key | Soft delete | Notes |
|------------|---------------|-------------|-------|
| `procurements` | `procurement_date` | Yes | Status: draft/confirmed/cancelled |
| `procurement_deductions` | via FK `procurement_date` | No | Linked to procurement |
| `farmer_ledger_entries` | `entry_date` | No | **Immutable** (trigger `prevent_ledger_mutation`) |
| `farmer_payments` | `payment_date` | No | advance/final/adjustment |
| `farmer_payment_allocations` | `payment_date` | No | Links payments → procurements |
| `attendance_records` | `attendance_date` | No | present/absent/half_day/leave |
| `work_orders` | — (`start_time`) | Yes | Labor cost in `cost` |
| `vehicle_trips` | `trip_date` | No | Fleet cost in `total_cost` |
| `asset_usage_logs` | `usage_date` | No | Machine hours, fuel, revenue |
| `rental_agreements` | — (`start_datetime`) | Yes | `revenue`, `collected_amount`, computed `pending_collection` |
| `expenses` | `expense_date` | Yes | Posted expenses |
| `collections` | `collection_date` | No | Cash in (rentals, etc.) |
| `payments` | `payment_date` | No | General outbound payments |
| `financial_transactions` | `transaction_date` | No | Ledger of record for finance |
| `farm_activities` | `activity_date` | Yes | Field activity log |

### 2.2 Dimension tables

`organizations`, `villages`, `crop_types`, `farmers`, `farms`, `workers`, `assets`, `rental_customers`, `expense_categories`, `activity_types`, `payment_modes`, `users`, `roles`.

Telugu display columns (`*_te`) exist on farmers, workers, villages, assets, expenses, and more — use `COALESCE(name_te, name)` in UI-facing queries when `Accept-Language: te`.

### 2.3 Star schema mapping (logical)

| Fact | Grain | Key dimensions |
|------|-------|----------------|
| Procurement | 1 row / procurement | `date`, `farmer`, `village`, `crop_type`, `org` |
| Farmer payment | 1 row / payment | `date`, `farmer`, `payment_mode`, `org` |
| Work order | 1 row / work order | `date`, `worker`, `farm`, `activity_type`, `org` |
| Attendance | 1 row / worker / day | `date`, `worker`, `farm`, `org` |
| Vehicle trip | 1 row / trip | `date`, `asset`, `driver_worker`, `org` |
| Rental agreement | 1 row / agreement | `customer`, `asset`, `date range`, `org` |
| Expense | 1 row / expense | `date`, `category`, `farm`, `asset`, `org` |
| Collection | 1 row / collection | `date`, `source_type`, `customer`, `org` |

No surrogate `dim_date` table exists yet; reporting derives calendar attributes in CTEs.

---

## 3. Multi-Tenancy

Every query **must** filter `org_id = :org_id`. The application resolves `org_id` from the authenticated JWT (`users.org_id`); never accept `org_id` from untrusted client input without cross-checking.

### 3.1 User scopes (row-level)

`user_scopes` (`scope_type`, `scope_id`) can restrict supervisors to specific farms or villages. Dashboard API should append optional scope predicates:

```sql
-- Example: farm-scoped supervisor
AND f.id IN (SELECT scope_id FROM user_scopes WHERE user_id = :user_id AND scope_type = 'farm')
```

Phase 1 SQL files use org + date filters only; scope filters are noted per dashboard.

### 3.2 Soft delete convention

For tables with `deleted_at` (via `audit_columns()`), reporting excludes deleted rows:

```sql
AND deleted_at IS NULL
```

Tables without `deleted_at` (ledger, payments, trips, attendance) are never soft-deleted at the schema level.

---

## 4. Time Grains

| Grain | Derivation | Use case |
|-------|------------|----------|
| **Daily** | `DATE(column)` | Operational monitoring, trip logs |
| **Weekly** | `DATE_TRUNC('week', column)` | Workforce trends (ISO week, Monday start) |
| **Monthly** | `DATE_TRUNC('month', column)` | Expense budgets, procurement volume |
| **Seasonal** | Telangana crop seasons from date | Procurement & farm ops |
| **Fiscal** | `organizations.fiscal_year_start_month` (default April) | P&L, annual rollups |

### 4.1 Season mapping (Telangana)

| Season | Months | Typical crops |
|--------|--------|---------------|
| **Kharif** | Jun–Oct | Paddy, Corn |
| **Rabi** | Nov–Mar | Paddy (second crop), vegetables |
| **Summer** | Apr–May | Fallow / short crops |

```sql
CASE
  WHEN EXTRACT(MONTH FROM d) BETWEEN 6 AND 10 THEN 'kharif'
  WHEN EXTRACT(MONTH FROM d) IN (11, 12, 1, 2, 3) THEN 'rabi'
  ELSE 'summer'
END AS season
```

Season can also join `farmer_crop_history.season` for farmer-level crop planning reports.

---

## 5. Partition-Aware Query Patterns

Partitioned tables use **RANGE** on the date column with monthly child tables (`{table}_2026_01`, etc.). Created by `create_monthly_partitions()` in `migration_utils.py`.

### 5.1 Rules

1. **Always** include the partition key in `WHERE` with a bounded range:
   ```sql
   AND procurement_date BETWEEN :date_from AND :date_to
   ```
2. Avoid `EXTRACT(YEAR FROM procurement_date) = 2026` without a date range — prevents partition pruning.
3. When joining parent → child on composite PK, include the date column:
   ```sql
   JOIN procurement_deductions pd
     ON pd.procurement_id = p.id AND pd.procurement_date = p.procurement_date
   ```
4. Plan ahead: run a cron job (or Alembic migration) each December to create next year's partitions.

### 5.2 Partitioned tables list

`procurements`, `farmer_ledger_entries`, `farmer_payments`, `attendance_records`, `asset_usage_logs`, `vehicle_trips`, `financial_transactions`.

---

## 6. Performance & Materialized Views

**Target:** 3–10 users scaling to 100+ on single EC2 + Postgres. At current data volumes, indexed base-table queries are sufficient. Materialized views (MVs) become valuable above ~500K procurement rows or when dashboards poll sub-minute intervals.

### 6.1 Recommended MVs (implement first)

| Priority | MV name | Source | Refresh | Rationale |
|----------|---------|--------|---------|-----------|
| **P0** | `mv_daily_procurement_summary` | `procurements` | Hourly + on confirm | Highest query frequency; partition-friendly daily grain |
| **P0** | `mv_daily_financial_summary` | `expenses`, `collections`, `farmer_payments`, `work_orders` | Nightly | Powers profitability dashboard |
| **P1** | `mv_farmer_outstanding_latest` | `farmer_outstanding_snapshots` or ledger | Hourly | Avoids per-farmer ledger scans |
| **P1** | `mv_worker_daily_productivity` | `attendance_records`, `work_orders` | Nightly | Join-heavy workforce metrics |
| **P2** | `mv_vehicle_daily_utilization` | `vehicle_trips`, `assets` | Nightly | Fleet KPIs |
| **P2** | `mv_rental_ar_summary` | `rental_agreements`, `collections` | Hourly | AR aging |

### 6.2 Refresh strategy

| Tier | Method | When |
|------|--------|------|
| Near-real-time | `REFRESH MATERIALIZED VIEW CONCURRENTLY` | After procurement confirm, payment post (event-driven via pg_notify or app job) |
| Batch | `REFRESH MATERIALIZED VIEW` (non-concurrent) | Nightly cron 02:00 IST |
| Snapshot | Insert into `farmer_outstanding_snapshots` | Daily 23:59 IST |

Each MV needs a **unique index** for `CONCURRENTLY` refresh.

### 6.3 Existing indexes leveraged

- `ix_procurements_org_date`, `ix_procurements_confirmed` (partial)
- `ix_expenses_org_date`, `ix_expenses_category_date`
- `ix_collections_org_date`, `ix_payments_org_date`
- `ix_vehicle_trips_asset_date`, `ix_work_orders_worker_status`
- `ix_farm_activities_farm_id`

---

## 7. RBAC & Dashboard Access

Permissions are seeded in `202506210015_seed_permissions_and_roles.py`. There is no per-dashboard permission yet; access is derived from module read permissions plus `dashboard:read`.

| Dashboard | Minimum permission | Roles (default) |
|-----------|-------------------|-----------------|
| Procurement | `procurements:read` | OWNER, MANAGER, SUPERVISOR |
| Farmer Payments | `farmer_payments:read` | OWNER, MANAGER |
| Worker Productivity | `work_orders:read` + `attendance:read` | OWNER, MANAGER, SUPERVISOR |
| Vehicle Utilization | `vehicle_trips:read` + `assets:read` | OWNER, MANAGER, SUPERVISOR |
| Rental Income | `rentals:read` | OWNER, MANAGER |
| Expense | `expenses:read` | OWNER, MANAGER |
| Profitability | `expenses:read` + `collections:read` + `procurements:read` | OWNER, MANAGER |
| Farm Operations | `farms:read` | OWNER, MANAGER, SUPERVISOR |

**Gate:** All dashboards require `dashboard:read`. Profitability is restricted to OWNER/MANAGER by default (supervisors lack `collections:read` and `farmer_payments:read`).

### Phase 2 RBAC

Add granular permissions: `reports:procurement:read`, `reports:financial:read`, etc., mapped in `role_permissions`.

---

## 8. Dashboard Catalog

Detailed KPIs: [`kpi_definitions.md`](./kpi_definitions.md)  
SQL queries: [`sql/`](./sql/)

| # | Dashboard | SQL file | Primary audience |
|---|-----------|----------|------------------|
| 1 | Procurement | `01_procurement.sql` | Procurement manager, owner |
| 2 | Farmer Payments | `02_farmer_payments.sql` | Accounts, owner |
| 3 | Worker Productivity | `03_worker_productivity.sql` | Farm supervisor, manager |
| 4 | Vehicle Utilization | `04_vehicle_utilization.sql` | Fleet manager, supervisor |
| 5 | Rental Income | `05_rental_income.sql` | Rental desk, owner |
| 6 | Expense | `06_expense.sql` | Accountant, manager |
| 7 | Profitability | `07_profitability.sql` | Owner, manager |
| 8 | Farm Operations | `08_farm_operations.sql` | Supervisor, manager |

---

## 9. Dashboard Summaries

### 9.1 Procurement Dashboard

**Purpose:** Monitor crop intake volume, value, quality (moisture), and deductions across villages and crop types.

**Widgets:** KPI cards (volume, value, avg rate), daily trend line, crop mix pie, village bar chart, moisture distribution, top farmers table, deduction breakdown.

**Drill-down:** Dashboard → village/crop slice → farmer list → procurement detail (`procurement_number`).

### 9.2 Farmer Payments Dashboard

**Purpose:** Track payouts, outstanding balances, payment modes, and allocation to procurements.

**Widgets:** Total paid, outstanding, payment trend, mode breakdown, top outstanding farmers, allocation coverage %, ledger activity.

**Drill-down:** Outstanding list → farmer profile → ledger entries → linked payments/allocations.

**Note:** Ledger is immutable; corrections appear as reversal entries (`reversal_of_id`).

### 9.3 Worker Productivity Dashboard

**Purpose:** Attendance compliance, work-order completion, labor cost per farm.

**Widgets:** Attendance rate, work orders completed, hours/duration, cost by farm, worker leaderboard, absenteeism trend.

**Drill-down:** Worker → attendance calendar → work orders → farm activities.

### 9.4 Vehicle Utilization Dashboard

**Purpose:** Fleet usage, trip costs, fuel efficiency, driver assignment.

**Widgets:** Trips count, distance, cost/trip, fuel L/km, asset utilization ranking, route frequency, maintenance overlay.

**Drill-down:** Asset → trip list → trip detail (source/destination, charges).

### 9.5 Rental Income Dashboard

**Purpose:** Rental revenue, collections, accounts receivable on equipment.

**Widgets:** Revenue, collected, pending collection, active agreements, revenue by asset category, customer ranking, collection trend.

**Drill-down:** Pending collections → agreement → customer → linked collections (`source_type` / `source_id`).

### 9.6 Expense Dashboard

**Purpose:** Operating expense tracking by category, farm, asset, vendor.

**Widgets:** Total expense, category breakdown, trend, top vendors, farm allocation, payment mode split.

**Drill-down:** Category → expense list → expense detail.

### 9.7 Profitability Dashboard

**Purpose:** Consolidated view of cash in vs cash out for farm operations.

**Components:**
- **Cash in:** `collections.amount` + rental `collected_amount`
- **Procurement outflow:** confirmed `procurements.net_amount` (farmer COGS)
- **Labor:** `work_orders.cost` (completed)
- **Fleet:** `vehicle_trips.total_cost` + `expenses` tagged to assets (fuel category)
- **Operating expenses:** `expenses` (posted)
- **Net position:** cash in − total outflows (simplified P&L; not full accrual)

**Phase 2:** Crop **sales** revenue (no `crop_sales` table yet) for true gross margin.

### 9.8 Farm Operations Dashboard

**Purpose:** Per-farm activity, acreage utilization, lease status, seasonal work coverage.

**Widgets:** Active farms, total acres, activities this period, work orders by farm, lease expiry alerts, crop history summary.

**Drill-down:** Farm → activities + work orders → workers assigned.

---

## 10. API Integration Pattern (Phase 1b)

```
GET /api/v1/reports/{dashboard}/summary?date_from=&date_to=
GET /api/v1/reports/{dashboard}/widgets/{widget_id}?...
```

- Load SQL from `docs/reporting/sql/` by widget name.
- Bind `:org_id` from JWT, dates from query params.
- Enforce RBAC via `require_permission()` matching dashboard registry (§7).
- Cache responses 5–15 min in Redis (`settings.cache_provider`) for summary endpoints.

---

## 11. Schema Gaps & Phase 2

| Gap | Impact | Proposed schema |
|-----|--------|-----------------|
| No `crop_sales` / buyer table | Cannot report grain sale revenue or true gross margin | `crop_sales(id, org_id, sale_date, crop_type_id, quantity_qtl, rate, buyer_id, …)` partitioned by `sale_date` |
| No `reports:*` permissions | Coarse RBAC | `reports:procurement:read`, `reports:financial:read`, … |
| No `dim_date` / fiscal calendar table | Season/FY logic duplicated in SQL | `dim_date` seed table or `generate_series` view |
| `farmer_ledger_entries.entry_type` not enum-constrained | Reporting must tolerate new values | Document canonical types in app layer |
| No inventory/stock table | Procurement volume ≠ inventory on hand | `inventory_snapshots` by crop and warehouse |
| Rental collections linkage | `collections.source_type` is free-text | Standardize values: `rental_agreement` |
| Worker payroll batch | Payments to workers scattered | `worker_payroll_runs` linking `payments` + `work_orders` |

---

## 12. File Index

```
docs/reporting/
├── REPORTING_ARCHITECTURE.md    ← this document
├── kpi_definitions.md           ← consolidated KPI reference
└── sql/
    ├── 01_procurement.sql
    ├── 02_farmer_payments.sql
    ├── 03_worker_productivity.sql
    ├── 04_vehicle_utilization.sql
    ├── 05_rental_income.sql
    ├── 06_expense.sql
    ├── 07_profitability.sql
    └── 08_farm_operations.sql
```

---

## 13. Example: Reporting View (P0)

```sql
-- Optional migration: reporting.v_procurements_active
CREATE OR REPLACE VIEW reporting.v_procurements_active AS
SELECT
  p.*,
  ct.name   AS crop_name,
  ct.name_te AS crop_name_te,
  v.name    AS village_name,
  v.name_te AS village_name_te,
  f.full_name AS farmer_name,
  f.full_name_te AS farmer_name_te
FROM procurements p
JOIN crop_types ct ON ct.id = p.crop_type_id AND ct.deleted_at IS NULL
JOIN villages v ON v.id = p.village_id AND v.deleted_at IS NULL
JOIN farmers f ON f.id = p.farmer_id AND f.deleted_at IS NULL
WHERE p.deleted_at IS NULL;
```

Application queries filter `org_id` and `procurement_date` on top of this view.
