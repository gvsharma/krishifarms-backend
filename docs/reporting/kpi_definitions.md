# KrishiFarms CRM — KPI Definitions

Consolidated reference for all reporting dashboards.  
**Conventions:** Money = INR (`NUMERIC(14,2)`); weight = kg unless noted; all KPIs scoped by `org_id` and active (non-deleted) dimension rows where applicable.

**Standard parameters**

| Parameter | Type | Description |
|-----------|------|-------------|
| `:org_id` | UUID | Organization tenant |
| `:date_from` | DATE | Inclusive start (partition key) |
| `:date_to` | DATE | Inclusive end (partition key) |

---

## 1. Procurement Dashboard

| KPI ID | Name | Formula | Unit | Grain | Filters |
|--------|------|---------|------|-------|---------|
| PROC-001 | Total Procurement Volume | `SUM(net_weight_kg)` | kg | daily/weekly/monthly/seasonal | `status = 'confirmed'`, `deleted_at IS NULL` |
| PROC-002 | Total Procurement Value | `SUM(net_amount)` | INR | same | confirmed procurements |
| PROC-003 | Total Bag Count | `SUM(bag_count)` | bags | same | confirmed |
| PROC-004 | Average Rate per Quintal | `SUM(net_amount) / NULLIF(SUM(net_weight_kg) / 100, 0)` | INR/quintal | period | confirmed |
| PROC-005 | Average Moisture % | `AVG(moisture_pct)` | % | period | confirmed, `moisture_pct IS NOT NULL` |
| PROC-006 | Total Deductions | `SUM(deduction_amount)` or `SUM(pd.amount)` from `procurement_deductions` | INR | period | confirmed |
| PROC-007 | Deduction Rate | `SUM(deduction_amount) / NULLIF(SUM(gross_amount), 0) * 100` | % | period | confirmed |
| PROC-008 | Confirmed Transaction Count | `COUNT(*)` | count | period | `status = 'confirmed'` |
| PROC-009 | Draft Backlog Count | `COUNT(*)` WHERE `status = 'draft'` | count | point-in-time | `procurement_date <= :date_to` |
| PROC-010 | Active Farmer Count | `COUNT(DISTINCT farmer_id)` | farmers | period | confirmed |
| PROC-011 | Crop Mix Share | `SUM(net_weight_kg) / total * 100` per `crop_type_id` | % | period | confirmed |
| PROC-012 | Village Share | `SUM(net_amount) / total * 100` per `village_id` | % | period | confirmed |

---

## 2. Farmer Payments Dashboard

| KPI ID | Name | Formula | Unit | Grain | Filters |
|--------|------|---------|------|-------|---------|
| PAY-001 | Total Payments Disbursed | `SUM(amount)` | INR | daily/monthly | `farmer_payments.status = 'completed'`, `payment_date` range |
| PAY-002 | Payment Count | `COUNT(*)` | count | period | completed |
| PAY-003 | Advance Payments | `SUM(amount)` WHERE `payment_type = 'advance'` | INR | period | completed |
| PAY-004 | Final Payments | `SUM(amount)` WHERE `payment_type = 'final'` | INR | period | completed |
| PAY-005 | Total Outstanding | `SUM(outstanding_amount)` from latest `farmer_outstanding_snapshots` per farmer | INR | point-in-time | `as_of_date = MAX(as_of_date)` |
| PAY-006 | Farmers with Outstanding | `COUNT(*)` WHERE `outstanding_amount > 0` | count | point-in-time | snapshots |
| PAY-007 | Allocation Coverage % | `SUM(allocated_amount) / NULLIF(SUM(fp.amount), 0) * 100` | % | period | completed payments with allocations |
| PAY-008 | Unallocated Payment Amount | `SUM(fp.amount) - COALESCE(SUM(fpa.allocated_amount), 0)` | INR | period | completed |
| PAY-009 | Payment Mode Mix | `SUM(amount)` GROUP BY `payment_mode_id` | INR | period | completed |
| PAY-010 | Ledger Credits (payments) | `SUM(credit)` WHERE `entry_type` relates to payment | INR | period | `entry_date` range |
| PAY-011 | Ledger Debits (procurement) | `SUM(debit)` WHERE `reference_type = 'procurement'` | INR | period | immutable ledger |
| PAY-012 | Avg Days to Pay | `AVG(payment_date - procurement_date)` via allocations | days | period | matched pairs |

---

## 3. Worker Productivity Dashboard

| KPI ID | Name | Formula | Unit | Grain | Filters |
|--------|------|---------|------|-------|---------|
| WRK-001 | Attendance Rate | `COUNT(present + 0.5*half_day) / NULLIF(COUNT(*), 0) * 100` | % | daily/weekly | `attendance_records` in range |
| WRK-002 | Present Days | `COUNT(*)` WHERE `status IN ('present','half_day')` | days | period | — |
| WRK-003 | Absent Days | `COUNT(*)` WHERE `status = 'absent'` | days | period | — |
| WRK-004 | Work Orders Completed | `COUNT(*)` WHERE `status = 'completed'` | count | period | `work_orders.deleted_at IS NULL` |
| WRK-005 | Work Orders Open | `COUNT(*)` WHERE `status IN ('open','in_progress')` | count | point-in-time | — |
| WRK-006 | Total Labor Cost | `SUM(cost)` | INR | period | completed work orders, `cost IS NOT NULL` |
| WRK-007 | Total Work Duration | `SUM(duration_minutes)` | minutes | period | completed |
| WRK-008 | Avg Cost per Work Order | `SUM(cost) / NULLIF(COUNT(*), 0)` | INR | period | completed |
| WRK-009 | Labor Cost per Farm | `SUM(cost)` GROUP BY `farm_id` | INR | period | completed |
| WRK-010 | Worker Utilization | `days_with_work_order / days_present` per worker | ratio | period | — |
| WRK-011 | Avg Hourly Effective Rate | `SUM(cost) / NULLIF(SUM(duration_minutes)/60.0, 0)` | INR/hour | period | hourly rate_type |
| WRK-012 | Active Workers | `COUNT(DISTINCT worker_id)` | count | period | attendance present |

---

## 4. Vehicle Utilization Dashboard

| KPI ID | Name | Formula | Unit | Grain | Filters |
|--------|------|---------|------|-------|---------|
| VEH-001 | Total Trips | `COUNT(*)` | trips | daily/monthly | `vehicle_trips.status = 'completed'`, `trip_date` range |
| VEH-002 | Total Distance | `SUM(distance_km)` | km | period | completed |
| VEH-003 | Total Trip Cost | `SUM(total_cost)` | INR | period | completed |
| VEH-004 | Avg Cost per Trip | `SUM(total_cost) / NULLIF(COUNT(*), 0)` | INR | period | completed |
| VEH-005 | Avg Cost per km | `SUM(total_cost) / NULLIF(SUM(distance_km), 0)` | INR/km | period | `distance_km > 0` |
| VEH-006 | Total Fuel Liters | `SUM(fuel_liters)` | liters | period | completed |
| VEH-007 | Fuel Efficiency | `SUM(distance_km) / NULLIF(SUM(fuel_liters), 0)` | km/L | period | — |
| VEH-008 | Fleet Utilization Rate | `days_with_trip / days_in_period` per asset | % | period | active assets |
| VEH-009 | Active Vehicles | `COUNT(DISTINCT asset_id)` | count | period | completed trips |
| VEH-010 | Loading/Unloading Charges | `SUM(loading_charges + unloading_charges)` | INR | period | — |
| VEH-011 | Maintenance Cost (period) | `SUM(cost)` from `maintenance_records` | INR | period | `maintenance_date` range |
| VEH-012 | Revenue per Machine Hour | `SUM(revenue_generated) / NULLIF(SUM(machine_hours), 0)` from `asset_usage_logs` | INR/hour | period | usage logs |

---

## 5. Rental Income Dashboard

| KPI ID | Name | Formula | Unit | Grain | Filters |
|--------|------|---------|------|-------|---------|
| RENT-001 | Total Rental Revenue | `SUM(revenue)` | INR | period | `rental_agreements.deleted_at IS NULL`, overlap with date range |
| RENT-002 | Total Collected | `SUM(collected_amount)` | INR | period | agreements in range |
| RENT-003 | Pending Collection (AR) | `SUM(pending_collection)` | INR | point-in-time | `pending_collection > 0` |
| RENT-004 | Collection Rate | `SUM(collected_amount) / NULLIF(SUM(revenue), 0) * 100` | % | period | — |
| RENT-005 | Active Agreements | `COUNT(*)` WHERE `status = 'active'` | count | point-in-time | — |
| RENT-006 | Completed Agreements | `COUNT(*)` WHERE `status = 'completed'` | count | period | — |
| RENT-007 | Revenue by Asset Category | `SUM(revenue)` GROUP BY `assets.asset_category` | INR | period | — |
| RENT-008 | Revenue by Customer | `SUM(revenue)` GROUP BY `customer_id` | INR | period | top N |
| RENT-009 | Collections (cash) | `SUM(amount)` from `collections` WHERE `source_type` indicates rental | INR | period | `collection_date` range |
| RENT-010 | Avg Revenue per Hour | `SUM(revenue) / NULLIF(SUM(total_hours), 0)` | INR/hour | period | hourly rate_type |
| RENT-011 | Rentable Asset Count | `COUNT(*)` FROM `assets` WHERE `is_rentable AND status = 'active'` | count | point-in-time | — |
| RENT-012 | Agreements with Pending AR | `COUNT(*)` WHERE `pending_collection > 0` | count | point-in-time | — |

---

## 6. Expense Dashboard

| KPI ID | Name | Formula | Unit | Grain | Filters |
|--------|------|---------|------|-------|---------|
| EXP-001 | Total Expenses | `SUM(amount)` | INR | daily/monthly | `expenses.status = 'posted'`, `deleted_at IS NULL` |
| EXP-002 | Expense Count | `COUNT(*)` | count | period | posted |
| EXP-003 | Expense by Category | `SUM(amount)` GROUP BY `category_id` | INR | period | posted |
| EXP-004 | Expense by Farm | `SUM(amount)` GROUP BY `farm_id` | INR | period | `farm_id IS NOT NULL` |
| EXP-005 | Expense by Asset | `SUM(amount)` GROUP BY `asset_id` | INR | period | `asset_id IS NOT NULL` |
| EXP-006 | Avg Expense Amount | `AVG(amount)` | INR | period | posted |
| EXP-007 | Top Vendor Spend | `SUM(amount)` GROUP BY `vendor_name` | INR | period | `vendor_name IS NOT NULL` |
| EXP-008 | Payment Mode Split | `SUM(amount)` GROUP BY `payment_mode_id` | INR | period | — |
| EXP-009 | MoM Expense Change | `(current - prior) / NULLIF(prior, 0) * 100` | % | monthly | posted |
| EXP-010 | Fuel Expenses | `SUM(amount)` WHERE category name/code = 'Fuel' | INR | period | joins `expense_categories` |
| EXP-011 | Labor Expenses (booked) | `SUM(amount)` WHERE category type/name = 'Labor' | INR | period | excludes work_order accrual |
| EXP-012 | Unattributed Expenses | `SUM(amount)` WHERE `farm_id IS NULL AND asset_id IS NULL` | INR | period | posted |

---

## 7. Profitability Dashboard

| KPI ID | Name | Formula | Unit | Grain | Filters |
|--------|------|---------|------|-------|---------|
| PNL-001 | Total Cash In (Collections) | `SUM(collections.amount)` | INR | period | `status = 'posted'` |
| PNL-002 | Rental Cash Collected | `SUM(rental_agreements.collected_amount)` or rental collections | INR | period | — |
| PNL-003 | Procurement Outflow (Farmer COGS) | `SUM(procurements.net_amount)` | INR | period | confirmed procurements |
| PNL-004 | Farmer Payments (cash) | `SUM(farmer_payments.amount)` | INR | period | completed |
| PNL-005 | Labor Cost (work orders) | `SUM(work_orders.cost)` | INR | period | completed |
| PNL-006 | Fleet Cost (trips) | `SUM(vehicle_trips.total_cost)` | INR | period | completed |
| PNL-007 | Operating Expenses | `SUM(expenses.amount)` | INR | period | posted |
| PNL-008 | General Payments Out | `SUM(payments.amount)` | INR | period | posted |
| PNL-009 | Total Cash Out | PNL-003..008 (configurable double-count rules) | INR | period | see SQL — avoid double-counting farmer_payments vs procurements |
| PNL-010 | Net Cash Position | PNL-001 − Total Cash Out | INR | period | — |
| PNL-011 | Gross Margin (Phase 2) | `(crop_sales_revenue - procurement_cogs) / crop_sales_revenue` | % | period | requires `crop_sales` table |
| PNL-012 | Cost per Quintal Procured | `(labor + fleet + opex) / (procurement_qtl)` | INR/quintal | period | — |

**Double-counting note:** `farmer_payments` cash out may overlap with procurement accrual in `farmer_ledger_entries`. Profitability SQL uses **procurement net_amount as COGS accrual** and **collections as cash in**; farmer payments shown separately as cash-flow, not added to COGS.

---

## 8. Farm Operations Dashboard

| KPI ID | Name | Formula | Unit | Grain | Filters |
|--------|------|---------|------|-------|---------|
| FARM-001 | Active Farms | `COUNT(*)` WHERE `status = 'active'` | count | point-in-time | `farms.deleted_at IS NULL` |
| FARM-002 | Total Farm Acreage | `SUM(acres)` | acres | point-in-time | active farms |
| FARM-003 | Farm Activities Count | `COUNT(*)` from `farm_activities` | count | period | `activity_date` range |
| FARM-004 | Work Orders per Farm | `COUNT(*)` GROUP BY `farm_id` | count | period | work orders |
| FARM-005 | Labor Spend per Farm | `SUM(work_orders.cost)` GROUP BY `farm_id` | INR | period | completed |
| FARM-006 | Expenses per Farm | `SUM(expenses.amount)` GROUP BY `farm_id` | INR | period | posted |
| FARM-007 | Attendance at Farm | `COUNT(*)` WHERE `farm_id IS NOT NULL` | days | period | attendance |
| FARM-008 | Leased Farms | `COUNT(*)` WHERE `lease_start_date IS NOT NULL` | count | point-in-time | — |
| FARM-009 | Lease Expiring Soon | `COUNT(*)` WHERE `lease_end_date BETWEEN today AND today+30` | count | point-in-time | — |
| FARM-010 | Crop History Acres | `SUM(acres)` from `farmer_crop_history` by season/year | acres | seasonal | linked via `owner_farmer_id` |
| FARM-011 | Activities by Type | `COUNT(*)` GROUP BY `activity_type_id` | count | period | — |
| FARM-012 | Cost per Acre | `(labor + expenses) / farm.acres` | INR/acre | period | per farm |

---

## Appendix: Status Enumerations

| Entity | Values |
|--------|--------|
| `procurements.status` | draft, confirmed, cancelled |
| `farmer_payments.status` | pending, completed, failed, reversed |
| `farmer_payments.payment_type` | advance, final, adjustment |
| `work_orders.status` | open, in_progress, completed, cancelled |
| `work_orders.rate_type` | hourly, daily, fixed |
| `attendance_records.status` | present, absent, half_day, leave |
| `vehicle_trips.status` | completed (default), others as used |
| `rental_agreements.status` | active, completed, cancelled |
| `expenses.status` | posted (default), draft if used |
| `assets.asset_category` | tractor, dcm, baler, air_machine, other |
| `expense_categories.type` | expense, income |
