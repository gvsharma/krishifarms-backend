-- =============================================================================
-- Dashboard 6: Expense
-- Parameters: :org_id UUID, :date_from DATE, :date_to DATE
-- Optional: :category_id UUID, :farm_id UUID, :asset_id UUID
-- KPIs: EXP-001 through EXP-012
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Q1: Expense KPI Summary
-- Widget: KPI cards
-- -----------------------------------------------------------------------------
SELECT
    COALESCE(SUM(e.amount), 0)                                               AS total_expenses_inr,       -- EXP-001
    COUNT(*)                                                                 AS expense_count,            -- EXP-002
    ROUND(AVG(e.amount), 2)                                                  AS avg_expense_inr,          -- EXP-006
    COALESCE(SUM(e.amount) FILTER (
        WHERE e.farm_id IS NULL AND e.asset_id IS NULL
    ), 0)                                                                    AS unattributed_expenses_inr -- EXP-012
FROM expenses e
WHERE e.org_id = :org_id
  AND e.expense_date BETWEEN :date_from AND :date_to
  AND e.status = 'posted'
  AND e.deleted_at IS NULL;


-- -----------------------------------------------------------------------------
-- Q2: Daily Expense Trend
-- Widget: Line chart
-- -----------------------------------------------------------------------------
SELECT
    e.expense_date                                                           AS report_date,
    COALESCE(SUM(e.amount), 0)                                               AS amount_inr,
    COUNT(*)                                                                 AS expense_count
FROM expenses e
WHERE e.org_id = :org_id
  AND e.expense_date BETWEEN :date_from AND :date_to
  AND e.status = 'posted'
  AND e.deleted_at IS NULL
GROUP BY e.expense_date
ORDER BY e.expense_date;


-- -----------------------------------------------------------------------------
-- Q3: Expense by Category
-- Widget: Donut / treemap (EXP-003)
-- Drill-down: category → expense list (Q7)
-- -----------------------------------------------------------------------------
WITH totals AS (
    SELECT COALESCE(SUM(e.amount), 0) AS total_inr
    FROM expenses e
    WHERE e.org_id = :org_id
      AND e.expense_date BETWEEN :date_from AND :date_to
      AND e.status = 'posted'
      AND e.deleted_at IS NULL
)
SELECT
    ec.id                                                                    AS category_id,
    ec.name                                                                  AS category_name,
    COALESCE(ec.name_te, ec.name)                                            AS category_display,
    ec.type                                                                  AS category_type,
    COALESCE(SUM(e.amount), 0)                                               AS amount_inr,
    COUNT(*)                                                                 AS expense_count,
    ROUND(
        COALESCE(SUM(e.amount), 0) / NULLIF(t.total_inr, 0) * 100,
        2
    )                                                                        AS share_pct
FROM expenses e
JOIN expense_categories ec
  ON ec.id = e.category_id
 AND ec.org_id = :org_id
 AND ec.deleted_at IS NULL
CROSS JOIN totals t
WHERE e.org_id = :org_id
  AND e.expense_date BETWEEN :date_from AND :date_to
  AND e.status = 'posted'
  AND e.deleted_at IS NULL
GROUP BY ec.id, ec.name, ec.name_te, ec.type, t.total_inr
ORDER BY amount_inr DESC;


-- -----------------------------------------------------------------------------
-- Q4: Expense by Farm
-- Widget: Bar chart (EXP-004)
-- -----------------------------------------------------------------------------
SELECT
    f.id                                                                     AS farm_id,
    f.farm_code,
    COALESCE(f.name_te, f.name)                                              AS farm_name,
    COALESCE(SUM(e.amount), 0)                                               AS amount_inr,
    COUNT(*)                                                                 AS expense_count
FROM expenses e
JOIN farms f
  ON f.id = e.farm_id
 AND f.org_id = :org_id
 AND f.deleted_at IS NULL
WHERE e.org_id = :org_id
  AND e.expense_date BETWEEN :date_from AND :date_to
  AND e.status = 'posted'
  AND e.deleted_at IS NULL
  AND e.farm_id IS NOT NULL
GROUP BY f.id, f.farm_code, f.name, f.name_te
ORDER BY amount_inr DESC;


-- -----------------------------------------------------------------------------
-- Q5: Expense by Asset
-- Widget: Bar chart (EXP-005)
-- -----------------------------------------------------------------------------
SELECT
    a.id                                                                     AS asset_id,
    a.asset_code,
    COALESCE(a.name_te, a.name)                                              AS asset_name,
    a.asset_category,
    COALESCE(SUM(e.amount), 0)                                               AS amount_inr,
    COUNT(*)                                                                 AS expense_count
FROM expenses e
JOIN assets a
  ON a.id = e.asset_id
 AND a.org_id = :org_id
 AND a.deleted_at IS NULL
WHERE e.org_id = :org_id
  AND e.expense_date BETWEEN :date_from AND :date_to
  AND e.status = 'posted'
  AND e.deleted_at IS NULL
  AND e.asset_id IS NOT NULL
GROUP BY a.id, a.asset_code, a.name, a.name_te, a.asset_category
ORDER BY amount_inr DESC;


-- -----------------------------------------------------------------------------
-- Q6: Top Vendors
-- Widget: Ranked table (EXP-007)
-- -----------------------------------------------------------------------------
SELECT
    e.vendor_name,
    COALESCE(SUM(e.amount), 0)                                               AS amount_inr,
    COUNT(*)                                                                 AS expense_count
FROM expenses e
WHERE e.org_id = :org_id
  AND e.expense_date BETWEEN :date_from AND :date_to
  AND e.status = 'posted'
  AND e.deleted_at IS NULL
  AND e.vendor_name IS NOT NULL
  AND TRIM(e.vendor_name) <> ''
GROUP BY e.vendor_name
ORDER BY amount_inr DESC
LIMIT 20;


-- -----------------------------------------------------------------------------
-- Q7: Expense Detail List
-- Widget: Paginated table
-- Drill-down: expense_number → full record + linked financial_transaction
-- -----------------------------------------------------------------------------
SELECT
    e.expense_number,
    e.expense_date,
    ec.name                                                                  AS category_name,
    COALESCE(ec.name_te, ec.name)                                            AS category_display,
    e.amount,
    e.vendor_name,
    COALESCE(e.description_te, e.description)                                AS description,
    f.farm_code,
    a.asset_code,
    pm.code                                                                  AS payment_mode_code,
    e.status
FROM expenses e
JOIN expense_categories ec
  ON ec.id = e.category_id
 AND ec.org_id = :org_id
 AND ec.deleted_at IS NULL
JOIN payment_modes pm
  ON pm.id = e.payment_mode_id
 AND pm.org_id = :org_id
 AND pm.deleted_at IS NULL
LEFT JOIN farms f
  ON f.id = e.farm_id
 AND f.org_id = :org_id
 AND f.deleted_at IS NULL
LEFT JOIN assets a
  ON a.id = e.asset_id
 AND a.org_id = :org_id
 AND a.deleted_at IS NULL
WHERE e.org_id = :org_id
  AND e.expense_date BETWEEN :date_from AND :date_to
  AND e.status = 'posted'
  AND e.deleted_at IS NULL
  AND (:category_id::uuid IS NULL OR e.category_id = :category_id)
  AND (:farm_id::uuid IS NULL OR e.farm_id = :farm_id)
  AND (:asset_id::uuid IS NULL OR e.asset_id = :asset_id)
ORDER BY e.expense_date DESC, e.expense_number
LIMIT 200;


-- -----------------------------------------------------------------------------
-- Q8: Month-over-Month Change
-- Widget: KPI sparkline (EXP-009)
-- -----------------------------------------------------------------------------
WITH monthly AS (
    SELECT
        DATE_TRUNC('month', e.expense_date)::date                            AS month_start,
        COALESCE(SUM(e.amount), 0)                                           AS amount_inr
    FROM expenses e
    WHERE e.org_id = :org_id
      AND e.expense_date BETWEEN (:date_from - INTERVAL '1 month')::date AND :date_to
      AND e.status = 'posted'
      AND e.deleted_at IS NULL
    GROUP BY DATE_TRUNC('month', e.expense_date)
)
SELECT
    month_start,
    amount_inr,
    LAG(amount_inr) OVER (ORDER BY month_start)                              AS prior_month_inr,
    ROUND(
        (amount_inr - LAG(amount_inr) OVER (ORDER BY month_start))
        / NULLIF(LAG(amount_inr) OVER (ORDER BY month_start), 0) * 100,
        2
    )                                                                        AS mom_change_pct
FROM monthly
ORDER BY month_start;


-- -----------------------------------------------------------------------------
-- Q9: Payment Mode Split
-- Widget: Pie chart (EXP-008)
-- -----------------------------------------------------------------------------
SELECT
    pm.code                                                                  AS payment_mode_code,
    COALESCE(pm.name_te, pm.name)                                            AS payment_mode_name,
    COALESCE(SUM(e.amount), 0)                                               AS amount_inr,
    COUNT(*)                                                                 AS expense_count
FROM expenses e
JOIN payment_modes pm
  ON pm.id = e.payment_mode_id
 AND pm.org_id = :org_id
 AND pm.deleted_at IS NULL
WHERE e.org_id = :org_id
  AND e.expense_date BETWEEN :date_from AND :date_to
  AND e.status = 'posted'
  AND e.deleted_at IS NULL
GROUP BY pm.code, pm.name, pm.name_te
ORDER BY amount_inr DESC;


-- -----------------------------------------------------------------------------
-- Q10: Fuel & Labor Category Focus
-- Widget: KPI cards (EXP-010, EXP-011)
-- -----------------------------------------------------------------------------
SELECT
    COALESCE(SUM(e.amount) FILTER (
        WHERE LOWER(ec.name) = 'fuel' OR LOWER(ec.code) = 'fuel'
    ), 0)                                                                    AS fuel_expenses_inr,
    COALESCE(SUM(e.amount) FILTER (
        WHERE LOWER(ec.name) = 'labor' OR LOWER(ec.code) = 'labor'
    ), 0)                                                                    AS labor_expenses_inr
FROM expenses e
JOIN expense_categories ec
  ON ec.id = e.category_id
 AND ec.org_id = :org_id
 AND ec.deleted_at IS NULL
WHERE e.org_id = :org_id
  AND e.expense_date BETWEEN :date_from AND :date_to
  AND e.status = 'posted'
  AND e.deleted_at IS NULL;
