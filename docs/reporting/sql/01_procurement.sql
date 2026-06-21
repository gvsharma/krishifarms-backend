-- =============================================================================
-- Dashboard 1: Procurement
-- Parameters: :org_id UUID, :date_from DATE, :date_to DATE
-- Optional: :village_id UUID, :crop_type_id UUID
-- Partition key: procurements.procurement_date
-- KPIs: PROC-001 through PROC-012 (see kpi_definitions.md)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Q1: KPI Summary Cards — volume, value, bags, avg rate, moisture, deductions
-- Widget: KPI row (6 cards)
-- -----------------------------------------------------------------------------
WITH confirmed AS (
    SELECT
        p.id,
        p.procurement_date,
        p.bag_count,
        p.net_weight_kg,
        p.gross_amount,
        p.deduction_amount,
        p.net_amount,
        p.moisture_pct
    FROM procurements p
    WHERE p.org_id = :org_id
      AND p.procurement_date BETWEEN :date_from AND :date_to
      AND p.status = 'confirmed'
      AND p.deleted_at IS NULL
)
SELECT
    COALESCE(SUM(net_weight_kg), 0)                                          AS total_volume_kg,          -- PROC-001
    COALESCE(SUM(net_amount), 0)                                             AS total_value_inr,          -- PROC-002
    COALESCE(SUM(bag_count), 0)                                              AS total_bags,               -- PROC-003
    ROUND(
        COALESCE(SUM(net_amount), 0)
        / NULLIF(COALESCE(SUM(net_weight_kg), 0) / 100.0, 0),
        2
    )                                                                        AS avg_rate_per_quintal_inr, -- PROC-004
    ROUND(AVG(moisture_pct), 2)                                              AS avg_moisture_pct,         -- PROC-005
    COALESCE(SUM(deduction_amount), 0)                                       AS total_deductions_inr,     -- PROC-006
    ROUND(
        COALESCE(SUM(deduction_amount), 0)
        / NULLIF(COALESCE(SUM(gross_amount), 0), 0) * 100,
        2
    )                                                                        AS deduction_rate_pct,       -- PROC-007
    COUNT(*)                                                                 AS confirmed_count           -- PROC-008
FROM confirmed;


-- -----------------------------------------------------------------------------
-- Q2: Daily Procurement Trend — volume and value
-- Widget: Dual-axis line chart (kg + INR by day)
-- Drill-down: click day → Q7 farmer list for that date
-- -----------------------------------------------------------------------------
SELECT
    p.procurement_date                                                       AS report_date,
    COALESCE(SUM(p.net_weight_kg), 0)                                        AS volume_kg,
    COALESCE(SUM(p.net_amount), 0)                                             AS value_inr,
    COUNT(*)                                                                 AS transaction_count
FROM procurements p
WHERE p.org_id = :org_id
  AND p.procurement_date BETWEEN :date_from AND :date_to
  AND p.status = 'confirmed'
  AND p.deleted_at IS NULL
GROUP BY p.procurement_date
ORDER BY p.procurement_date;


-- -----------------------------------------------------------------------------
-- Q3: Crop Mix — weight and value share
-- Widget: Donut chart (PROC-011)
-- Drill-down: crop slice → Q7 filtered by crop_type_id
-- -----------------------------------------------------------------------------
WITH totals AS (
    SELECT
        COALESCE(SUM(p.net_weight_kg), 0) AS total_kg,
        COALESCE(SUM(p.net_amount), 0)     AS total_inr
    FROM procurements p
    WHERE p.org_id = :org_id
      AND p.procurement_date BETWEEN :date_from AND :date_to
      AND p.status = 'confirmed'
      AND p.deleted_at IS NULL
),
by_crop AS (
    SELECT
        ct.id                                                                AS crop_type_id,
        ct.code                                                              AS crop_code,
        COALESCE(ct.name_te, ct.name)                                        AS crop_name,
        COALESCE(SUM(p.net_weight_kg), 0)                                    AS volume_kg,
        COALESCE(SUM(p.net_amount), 0)                                       AS value_inr,
        COUNT(*)                                                             AS transaction_count
    FROM procurements p
    JOIN crop_types ct
      ON ct.id = p.crop_type_id
     AND ct.org_id = :org_id
     AND ct.deleted_at IS NULL
    WHERE p.org_id = :org_id
      AND p.procurement_date BETWEEN :date_from AND :date_to
      AND p.status = 'confirmed'
      AND p.deleted_at IS NULL
    GROUP BY ct.id, ct.code, ct.name, ct.name_te
)
SELECT
    b.crop_type_id,
    b.crop_code,
    b.crop_name,
    b.volume_kg,
    b.value_inr,
    b.transaction_count,
    ROUND(b.volume_kg / NULLIF(t.total_kg, 0) * 100, 2)                      AS volume_share_pct,
    ROUND(b.value_inr / NULLIF(t.total_inr, 0) * 100, 2)                     AS value_share_pct
FROM by_crop b
CROSS JOIN totals t
ORDER BY b.volume_kg DESC;


-- -----------------------------------------------------------------------------
-- Q4: Village Breakdown
-- Widget: Horizontal bar chart (PROC-012)
-- Drill-down: village → farmer list (Q7 with village filter)
-- -----------------------------------------------------------------------------
WITH totals AS (
    SELECT COALESCE(SUM(p.net_amount), 0) AS total_inr
    FROM procurements p
    WHERE p.org_id = :org_id
      AND p.procurement_date BETWEEN :date_from AND :date_to
      AND p.status = 'confirmed'
      AND p.deleted_at IS NULL
)
SELECT
    v.id                                                                     AS village_id,
    COALESCE(v.name_te, v.name)                                              AS village_name,
    COALESCE(SUM(p.net_weight_kg), 0)                                        AS volume_kg,
    COALESCE(SUM(p.net_amount), 0)                                           AS value_inr,
    COUNT(DISTINCT p.farmer_id)                                              AS farmer_count,
    COUNT(*)                                                                 AS transaction_count,
    ROUND(
        COALESCE(SUM(p.net_amount), 0) / NULLIF(t.total_inr, 0) * 100,
        2
    )                                                                        AS value_share_pct
FROM procurements p
JOIN villages v
  ON v.id = p.village_id
 AND v.org_id = :org_id
 AND v.deleted_at IS NULL
CROSS JOIN totals t
WHERE p.org_id = :org_id
  AND p.procurement_date BETWEEN :date_from AND :date_to
  AND p.status = 'confirmed'
  AND p.deleted_at IS NULL
GROUP BY v.id, v.name, v.name_te, t.total_inr
ORDER BY value_inr DESC;


-- -----------------------------------------------------------------------------
-- Q5: Seasonal Summary (Kharif / Rabi / Summer)
-- Widget: Grouped bar chart by season
-- -----------------------------------------------------------------------------
WITH proc AS (
    SELECT
        p.procurement_date,
        p.net_weight_kg,
        p.net_amount,
        CASE
            WHEN EXTRACT(MONTH FROM p.procurement_date) BETWEEN 6 AND 10 THEN 'kharif'
            WHEN EXTRACT(MONTH FROM p.procurement_date) IN (11, 12, 1, 2, 3) THEN 'rabi'
            ELSE 'summer'
        END                                                                  AS season
    FROM procurements p
    WHERE p.org_id = :org_id
      AND p.procurement_date BETWEEN :date_from AND :date_to
      AND p.status = 'confirmed'
      AND p.deleted_at IS NULL
)
SELECT
    season,
    COALESCE(SUM(net_weight_kg), 0)                                          AS volume_kg,
    COALESCE(SUM(net_amount), 0)                                             AS value_inr,
    COUNT(*)                                                                 AS transaction_count
FROM proc
GROUP BY season
ORDER BY
    CASE season
        WHEN 'kharif' THEN 1
        WHEN 'rabi'   THEN 2
        ELSE 3
    END;


-- -----------------------------------------------------------------------------
-- Q6: Deduction Breakdown by Type
-- Widget: Stacked bar or table
-- -----------------------------------------------------------------------------
SELECT
    pd.deduction_type,
    COALESCE(pd.deduction_type_te, pd.deduction_type)                        AS deduction_type_display,
    COALESCE(SUM(pd.amount), 0)                                              AS total_deduction_inr,
    COUNT(*)                                                                 AS line_count
FROM procurement_deductions pd
JOIN procurements p
  ON p.id = pd.procurement_id
 AND p.procurement_date = pd.procurement_date
 AND p.org_id = :org_id
WHERE pd.org_id = :org_id
  AND p.procurement_date BETWEEN :date_from AND :date_to
  AND p.status = 'confirmed'
  AND p.deleted_at IS NULL
GROUP BY pd.deduction_type, pd.deduction_type_te
ORDER BY total_deduction_inr DESC;


-- -----------------------------------------------------------------------------
-- Q7: Top Farmers by Procurement Value
-- Widget: Ranked table (top 20)
-- Drill-down: farmer_id → procurement list → single procurement detail
-- -----------------------------------------------------------------------------
SELECT
    f.id                                                                     AS farmer_id,
    f.farmer_code,
    COALESCE(f.full_name_te, f.full_name)                                    AS farmer_name,
    COALESCE(v.name_te, v.name)                                              AS village_name,
    COALESCE(SUM(p.net_weight_kg), 0)                                        AS volume_kg,
    COALESCE(SUM(p.net_amount), 0)                                           AS value_inr,
    COUNT(*)                                                                 AS transaction_count,
    ROUND(AVG(p.moisture_pct), 2)                                            AS avg_moisture_pct
FROM procurements p
JOIN farmers f
  ON f.id = p.farmer_id
 AND f.org_id = :org_id
 AND f.deleted_at IS NULL
JOIN villages v
  ON v.id = p.village_id
 AND v.org_id = :org_id
 AND v.deleted_at IS NULL
WHERE p.org_id = :org_id
  AND p.procurement_date BETWEEN :date_from AND :date_to
  AND p.status = 'confirmed'
  AND p.deleted_at IS NULL
  -- Optional filters (bind NULL to skip):
  AND (:village_id::uuid IS NULL OR p.village_id = :village_id)
  AND (:crop_type_id::uuid IS NULL OR p.crop_type_id = :crop_type_id)
GROUP BY f.id, f.farmer_code, f.full_name, f.full_name_te, v.name, v.name_te
ORDER BY value_inr DESC
LIMIT 20;


-- -----------------------------------------------------------------------------
-- Q8: Draft Backlog & Status Pipeline
-- Widget: Funnel / status counts (PROC-009)
-- -----------------------------------------------------------------------------
SELECT
    p.status,
    COUNT(*)                                                                 AS transaction_count,
    COALESCE(SUM(p.net_weight_kg), 0)                                        AS volume_kg,
    COALESCE(SUM(p.net_amount), 0)                                           AS value_inr
FROM procurements p
WHERE p.org_id = :org_id
  AND p.procurement_date BETWEEN :date_from AND :date_to
  AND p.deleted_at IS NULL
GROUP BY p.status
ORDER BY
    CASE p.status
        WHEN 'draft'     THEN 1
        WHEN 'confirmed' THEN 2
        WHEN 'cancelled' THEN 3
        ELSE 4
    END;
