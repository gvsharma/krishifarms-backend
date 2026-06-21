-- =============================================================================
-- Dashboard 7: Profitability
-- Parameters: :org_id UUID, :date_from DATE, :date_to DATE
-- KPIs: PNL-001 through PNL-012
--
-- Cash-flow P&L model:
--   Cash IN  = collections + rental collected (agreement-level)
--   Cash OUT = procurement COGS (accrual) + labor + fleet + opex + general payments
-- Farmer payments shown separately (cash) — NOT added to COGS to avoid double-count
-- with procurement accrual. See REPORTING_ARCHITECTURE.md §9.7.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Q1: Consolidated P&L Summary
-- Widget: KPI waterfall / summary cards
-- -----------------------------------------------------------------------------
WITH cash_in AS (
    SELECT COALESCE(SUM(c.amount), 0) AS collections_inr
    FROM collections c
    WHERE c.org_id = :org_id
      AND c.collection_date BETWEEN :date_from AND :date_to
      AND c.status = 'posted'
),
rental_collected AS (
    SELECT COALESCE(SUM(ra.collected_amount), 0) AS rental_collected_inr
    FROM rental_agreements ra
    WHERE ra.org_id = :org_id
      AND ra.deleted_at IS NULL
      AND ra.start_datetime::date <= :date_to
      AND (ra.end_datetime IS NULL OR ra.end_datetime::date >= :date_from)
),
procurement_cogs AS (
    SELECT COALESCE(SUM(p.net_amount), 0) AS procurement_cogs_inr
    FROM procurements p
    WHERE p.org_id = :org_id
      AND p.procurement_date BETWEEN :date_from AND :date_to
      AND p.status = 'confirmed'
      AND p.deleted_at IS NULL
),
farmer_payments_cash AS (
    SELECT COALESCE(SUM(fp.amount), 0) AS farmer_payments_inr
    FROM farmer_payments fp
    WHERE fp.org_id = :org_id
      AND fp.payment_date BETWEEN :date_from AND :date_to
      AND fp.status = 'completed'
),
labor AS (
    SELECT COALESCE(SUM(wo.cost), 0) AS labor_cost_inr
    FROM work_orders wo
    WHERE wo.org_id = :org_id
      AND wo.deleted_at IS NULL
      AND wo.status = 'completed'
      AND wo.start_time::date BETWEEN :date_from AND :date_to
      AND wo.cost IS NOT NULL
),
fleet AS (
    SELECT COALESCE(SUM(vt.total_cost), 0) AS fleet_cost_inr
    FROM vehicle_trips vt
    WHERE vt.org_id = :org_id
      AND vt.trip_date BETWEEN :date_from AND :date_to
      AND vt.status = 'completed'
),
opex AS (
    SELECT COALESCE(SUM(e.amount), 0) AS operating_expenses_inr
    FROM expenses e
    WHERE e.org_id = :org_id
      AND e.expense_date BETWEEN :date_from AND :date_to
      AND e.status = 'posted'
      AND e.deleted_at IS NULL
),
general_payments AS (
    SELECT COALESCE(SUM(pay.amount), 0) AS general_payments_inr
    FROM payments pay
    WHERE pay.org_id = :org_id
      AND pay.payment_date BETWEEN :date_from AND :date_to
      AND pay.status = 'posted'
)
SELECT
    ci.collections_inr                                                       AS cash_in_collections_inr,  -- PNL-001
    rc.rental_collected_inr                                                  AS cash_in_rental_collected_inr, -- PNL-002
    ci.collections_inr + rc.rental_collected_inr                             AS total_cash_in_inr,
    pc.procurement_cogs_inr                                                  AS procurement_cogs_inr,     -- PNL-003
    fpc.farmer_payments_inr                                                  AS farmer_payments_cash_inr, -- PNL-004 (informational)
    lb.labor_cost_inr                                                        AS labor_cost_inr,           -- PNL-005
    fl.fleet_cost_inr                                                        AS fleet_cost_inr,           -- PNL-006
    ox.operating_expenses_inr                                                AS operating_expenses_inr,   -- PNL-007
    gp.general_payments_inr                                                  AS general_payments_inr,     -- PNL-008
    -- Total cash out: COGS accrual + labor + fleet + opex + general payments
    pc.procurement_cogs_inr
        + lb.labor_cost_inr
        + fl.fleet_cost_inr
        + ox.operating_expenses_inr
        + gp.general_payments_inr                                            AS total_cash_out_inr,       -- PNL-009
    (ci.collections_inr + rc.rental_collected_inr)
        - (
            pc.procurement_cogs_inr
            + lb.labor_cost_inr
            + fl.fleet_cost_inr
            + ox.operating_expenses_inr
            + gp.general_payments_inr
        )                                                                    AS net_cash_position_inr     -- PNL-010
FROM cash_in ci
CROSS JOIN rental_collected rc
CROSS JOIN procurement_cogs pc
CROSS JOIN farmer_payments_cash fpc
CROSS JOIN labor lb
CROSS JOIN fleet fl
CROSS JOIN opex ox
CROSS JOIN general_payments gp;


-- -----------------------------------------------------------------------------
-- Q2: Daily Cash Flow Trend
-- Widget: Stacked area (in vs out by day)
-- -----------------------------------------------------------------------------
WITH days AS (
    SELECT generate_series(:date_from, :date_to, '1 day'::interval)::date AS report_date
),
daily_in AS (
    SELECT
        c.collection_date                                                    AS report_date,
        COALESCE(SUM(c.amount), 0)                                           AS cash_in_inr
    FROM collections c
    WHERE c.org_id = :org_id
      AND c.collection_date BETWEEN :date_from AND :date_to
      AND c.status = 'posted'
    GROUP BY c.collection_date
),
daily_procurement AS (
    SELECT
        p.procurement_date                                                   AS report_date,
        COALESCE(SUM(p.net_amount), 0)                                       AS procurement_out_inr
    FROM procurements p
    WHERE p.org_id = :org_id
      AND p.procurement_date BETWEEN :date_from AND :date_to
      AND p.status = 'confirmed'
      AND p.deleted_at IS NULL
    GROUP BY p.procurement_date
),
daily_expenses AS (
    SELECT
        e.expense_date                                                       AS report_date,
        COALESCE(SUM(e.amount), 0)                                           AS expense_out_inr
    FROM expenses e
    WHERE e.org_id = :org_id
      AND e.expense_date BETWEEN :date_from AND :date_to
      AND e.status = 'posted'
      AND e.deleted_at IS NULL
    GROUP BY e.expense_date
),
daily_labor AS (
    SELECT
        wo.start_time::date                                                  AS report_date,
        COALESCE(SUM(wo.cost), 0)                                            AS labor_out_inr
    FROM work_orders wo
    WHERE wo.org_id = :org_id
      AND wo.deleted_at IS NULL
      AND wo.status = 'completed'
      AND wo.start_time::date BETWEEN :date_from AND :date_to
      AND wo.cost IS NOT NULL
    GROUP BY wo.start_time::date
),
daily_fleet AS (
    SELECT
        vt.trip_date                                                         AS report_date,
        COALESCE(SUM(vt.total_cost), 0)                                      AS fleet_out_inr
    FROM vehicle_trips vt
    WHERE vt.org_id = :org_id
      AND vt.trip_date BETWEEN :date_from AND :date_to
      AND vt.status = 'completed'
    GROUP BY vt.trip_date
)
SELECT
    d.report_date,
    COALESCE(di.cash_in_inr, 0)                                              AS cash_in_inr,
    COALESCE(dp.procurement_out_inr, 0)
        + COALESCE(de.expense_out_inr, 0)
        + COALESCE(dl.labor_out_inr, 0)
        + COALESCE(df.fleet_out_inr, 0)                                      AS cash_out_inr,
    COALESCE(di.cash_in_inr, 0)
        - (
            COALESCE(dp.procurement_out_inr, 0)
            + COALESCE(de.expense_out_inr, 0)
            + COALESCE(dl.labor_out_inr, 0)
            + COALESCE(df.fleet_out_inr, 0)
        )                                                                    AS net_inr
FROM days d
LEFT JOIN daily_in di ON di.report_date = d.report_date
LEFT JOIN daily_procurement dp ON dp.report_date = d.report_date
LEFT JOIN daily_expenses de ON de.report_date = d.report_date
LEFT JOIN daily_labor dl ON dl.report_date = d.report_date
LEFT JOIN daily_fleet df ON df.report_date = d.report_date
ORDER BY d.report_date;


-- -----------------------------------------------------------------------------
-- Q3: Cost Breakdown (composition)
-- Widget: Donut / waterfall chart
-- -----------------------------------------------------------------------------
WITH costs AS (
    SELECT 'procurement_cogs' AS cost_component,
           COALESCE(SUM(p.net_amount), 0) AS amount_inr
    FROM procurements p
    WHERE p.org_id = :org_id
      AND p.procurement_date BETWEEN :date_from AND :date_to
      AND p.status = 'confirmed'
      AND p.deleted_at IS NULL
    UNION ALL
    SELECT 'labor_work_orders',
           COALESCE(SUM(wo.cost), 0)
    FROM work_orders wo
    WHERE wo.org_id = :org_id
      AND wo.deleted_at IS NULL
      AND wo.status = 'completed'
      AND wo.start_time::date BETWEEN :date_from AND :date_to
      AND wo.cost IS NOT NULL
    UNION ALL
    SELECT 'fleet_trips',
           COALESCE(SUM(vt.total_cost), 0)
    FROM vehicle_trips vt
    WHERE vt.org_id = :org_id
      AND vt.trip_date BETWEEN :date_from AND :date_to
      AND vt.status = 'completed'
    UNION ALL
    SELECT 'operating_expenses',
           COALESCE(SUM(e.amount), 0)
    FROM expenses e
    WHERE e.org_id = :org_id
      AND e.expense_date BETWEEN :date_from AND :date_to
      AND e.status = 'posted'
      AND e.deleted_at IS NULL
    UNION ALL
    SELECT 'general_payments',
           COALESCE(SUM(pay.amount), 0)
    FROM payments pay
    WHERE pay.org_id = :org_id
      AND pay.payment_date BETWEEN :date_from AND :date_to
      AND pay.status = 'posted'
),
totals AS (
    SELECT COALESCE(SUM(amount_inr), 0) AS total_inr FROM costs
)
SELECT
    c.cost_component,
    c.amount_inr,
    ROUND(c.amount_inr / NULLIF(t.total_inr, 0) * 100, 2)                    AS share_pct
FROM costs c
CROSS JOIN totals t
WHERE c.amount_inr > 0
ORDER BY c.amount_inr DESC;


-- -----------------------------------------------------------------------------
-- Q4: Revenue Sources (cash in breakdown)
-- Widget: Bar chart
-- -----------------------------------------------------------------------------
WITH by_source AS (
    SELECT
        c.source_type,
        COALESCE(SUM(c.amount), 0)                                           AS amount_inr,
        COUNT(*)                                                             AS transaction_count
    FROM collections c
    WHERE c.org_id = :org_id
      AND c.collection_date BETWEEN :date_from AND :date_to
      AND c.status = 'posted'
    GROUP BY c.source_type
)
SELECT
    source_type,
    amount_inr,
    transaction_count
FROM by_source
UNION ALL
SELECT
    'rental_agreements_collected'                                            AS source_type,
    COALESCE(SUM(ra.collected_amount), 0)                                    AS amount_inr,
    COUNT(*)                                                                 AS transaction_count
FROM rental_agreements ra
WHERE ra.org_id = :org_id
  AND ra.deleted_at IS NULL
  AND ra.start_datetime::date <= :date_to
  AND (ra.end_datetime IS NULL OR ra.end_datetime::date >= :date_from)
ORDER BY amount_inr DESC;


-- -----------------------------------------------------------------------------
-- Q5: Monthly P&L Trend
-- Widget: Grouped bar (cash in vs out by month)
-- -----------------------------------------------------------------------------
WITH months AS (
    SELECT DATE_TRUNC('month', d)::date AS month_start
    FROM generate_series(:date_from, :date_to, '1 day'::interval) d
    GROUP BY DATE_TRUNC('month', d)
),
monthly_in AS (
    SELECT
        DATE_TRUNC('month', c.collection_date)::date                         AS month_start,
        COALESCE(SUM(c.amount), 0)                                           AS cash_in_inr
    FROM collections c
    WHERE c.org_id = :org_id
      AND c.collection_date BETWEEN :date_from AND :date_to
      AND c.status = 'posted'
    GROUP BY DATE_TRUNC('month', c.collection_date)
),
monthly_out AS (
    SELECT month_start, SUM(amount_inr) AS cash_out_inr
    FROM (
        SELECT DATE_TRUNC('month', p.procurement_date)::date AS month_start,
               SUM(p.net_amount) AS amount_inr
        FROM procurements p
        WHERE p.org_id = :org_id
          AND p.procurement_date BETWEEN :date_from AND :date_to
          AND p.status = 'confirmed'
          AND p.deleted_at IS NULL
        GROUP BY 1
        UNION ALL
        SELECT DATE_TRUNC('month', e.expense_date)::date,
               SUM(e.amount)
        FROM expenses e
        WHERE e.org_id = :org_id
          AND e.expense_date BETWEEN :date_from AND :date_to
          AND e.status = 'posted'
          AND e.deleted_at IS NULL
        GROUP BY 1
        UNION ALL
        SELECT DATE_TRUNC('month', wo.start_time)::date,
               SUM(wo.cost)
        FROM work_orders wo
        WHERE wo.org_id = :org_id
          AND wo.deleted_at IS NULL
          AND wo.status = 'completed'
          AND wo.start_time::date BETWEEN :date_from AND :date_to
          AND wo.cost IS NOT NULL
        GROUP BY 1
        UNION ALL
        SELECT DATE_TRUNC('month', vt.trip_date)::date,
               SUM(vt.total_cost)
        FROM vehicle_trips vt
        WHERE vt.org_id = :org_id
          AND vt.trip_date BETWEEN :date_from AND :date_to
          AND vt.status = 'completed'
        GROUP BY 1
    ) sub
    GROUP BY month_start
)
SELECT
    m.month_start,
    COALESCE(mi.cash_in_inr, 0)                                              AS cash_in_inr,
    COALESCE(mo.cash_out_inr, 0)                                             AS cash_out_inr,
    COALESCE(mi.cash_in_inr, 0) - COALESCE(mo.cash_out_inr, 0)               AS net_inr
FROM months m
LEFT JOIN monthly_in mi ON mi.month_start = m.month_start
LEFT JOIN monthly_out mo ON mo.month_start = m.month_start
ORDER BY m.month_start;


-- -----------------------------------------------------------------------------
-- Q6: Cost per Quintal Procured
-- Widget: KPI card (PNL-012)
-- -----------------------------------------------------------------------------
WITH procurement AS (
    SELECT COALESCE(SUM(p.net_weight_kg), 0) / 100.0                          AS quintals
    FROM procurements p
    WHERE p.org_id = :org_id
      AND p.procurement_date BETWEEN :date_from AND :date_to
      AND p.status = 'confirmed'
      AND p.deleted_at IS NULL
),
indirect_costs AS (
    SELECT
        COALESCE(SUM(wo.cost), 0)
        + COALESCE((
            SELECT SUM(vt.total_cost)
            FROM vehicle_trips vt
            WHERE vt.org_id = :org_id
              AND vt.trip_date BETWEEN :date_from AND :date_to
              AND vt.status = 'completed'
        ), 0)
        + COALESCE((
            SELECT SUM(e.amount)
            FROM expenses e
            WHERE e.org_id = :org_id
              AND e.expense_date BETWEEN :date_from AND :date_to
              AND e.status = 'posted'
              AND e.deleted_at IS NULL
        ), 0)                                                                AS indirect_inr
    FROM work_orders wo
    WHERE wo.org_id = :org_id
      AND wo.deleted_at IS NULL
      AND wo.status = 'completed'
      AND wo.start_time::date BETWEEN :date_from AND :date_to
      AND wo.cost IS NOT NULL
)
SELECT
    pr.quintals                                                              AS total_quintals,
    ic.indirect_inr,
    ROUND(ic.indirect_inr / NULLIF(pr.quintals, 0), 2)                       AS cost_per_quintal_inr
FROM procurement pr
CROSS JOIN indirect_costs ic;


-- -----------------------------------------------------------------------------
-- Q7: Farmer Payment vs Procurement COGS Reconciliation
-- Widget: Table (cash vs accrual gap)
-- Drill-down: farmer → payments + procurements
-- -----------------------------------------------------------------------------
WITH proc_by_farmer AS (
    SELECT
        p.farmer_id,
        COALESCE(SUM(p.net_amount), 0)                                       AS procurement_cogs_inr
    FROM procurements p
    WHERE p.org_id = :org_id
      AND p.procurement_date BETWEEN :date_from AND :date_to
      AND p.status = 'confirmed'
      AND p.deleted_at IS NULL
    GROUP BY p.farmer_id
),
pay_by_farmer AS (
    SELECT
        fp.farmer_id,
        COALESCE(SUM(fp.amount), 0)                                          AS payments_cash_inr
    FROM farmer_payments fp
    WHERE fp.org_id = :org_id
      AND fp.payment_date BETWEEN :date_from AND :date_to
      AND fp.status = 'completed'
    GROUP BY fp.farmer_id
)
SELECT
    f.id                                                                     AS farmer_id,
    f.farmer_code,
    COALESCE(f.full_name_te, f.full_name)                                    AS farmer_name,
    COALESCE(pb.procurement_cogs_inr, 0)                                     AS procurement_cogs_inr,
    COALESCE(py.payments_cash_inr, 0)                                        AS payments_cash_inr,
    COALESCE(pb.procurement_cogs_inr, 0) - COALESCE(py.payments_cash_inr, 0) AS accrual_cash_gap_inr
FROM farmers f
LEFT JOIN proc_by_farmer pb ON pb.farmer_id = f.id
LEFT JOIN pay_by_farmer py ON py.farmer_id = f.id
WHERE f.org_id = :org_id
  AND f.deleted_at IS NULL
  AND (pb.farmer_id IS NOT NULL OR py.farmer_id IS NOT NULL)
ORDER BY ABS(COALESCE(pb.procurement_cogs_inr, 0) - COALESCE(py.payments_cash_inr, 0)) DESC
LIMIT 30;


-- -----------------------------------------------------------------------------
-- Q8: Financial Transactions Ledger (audit trail)
-- Widget: Table for finance users
-- Partition key: transaction_date
-- -----------------------------------------------------------------------------
SELECT
    ft.transaction_number,
    ft.transaction_date,
    ft.transaction_type,
    ft.amount,
    ft.status,
    ft.party_type,
    ft.party_id,
    ft.source_type,
    ft.source_id,
    ft.description,
    ft.posted_at
FROM financial_transactions ft
WHERE ft.org_id = :org_id
  AND ft.transaction_date BETWEEN :date_from AND :date_to
  AND ft.status = 'posted'
ORDER BY ft.transaction_date DESC, ft.posted_at DESC
LIMIT 200;
