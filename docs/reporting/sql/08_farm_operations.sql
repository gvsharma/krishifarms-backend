-- =============================================================================
-- Dashboard 8: Farm Operations
-- Parameters: :org_id UUID, :date_from DATE, :date_to DATE
-- Optional: :farm_id UUID, :village_id UUID
-- KPIs: FARM-001 through FARM-012
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Q1: Farm Operations KPI Summary
-- Widget: KPI cards
-- -----------------------------------------------------------------------------
WITH active_farms AS (
    SELECT
        COUNT(*)                                                             AS active_farm_count,
        COALESCE(SUM(f.acres), 0)                                            AS total_acres
    FROM farms f
    WHERE f.org_id = :org_id
      AND f.deleted_at IS NULL
      AND f.status = 'active'
      AND (:farm_id::uuid IS NULL OR f.id = :farm_id)
),
activities AS (
    SELECT COUNT(*) AS activity_count
    FROM farm_activities fa
    WHERE fa.org_id = :org_id
      AND fa.deleted_at IS NULL
      AND fa.activity_date BETWEEN :date_from AND :date_to
      AND (:farm_id::uuid IS NULL OR fa.farm_id = :farm_id)
),
leases AS (
    SELECT
        COUNT(*) FILTER (WHERE f.lease_start_date IS NOT NULL)               AS leased_farm_count,
        COUNT(*) FILTER (
            WHERE f.lease_end_date IS NOT NULL
              AND f.lease_end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 30
        )                                                                    AS lease_expiring_soon
    FROM farms f
    WHERE f.org_id = :org_id
      AND f.deleted_at IS NULL
      AND f.status = 'active'
)
SELECT
    af.active_farm_count,                                                    -- FARM-001
    af.total_acres,                                                          -- FARM-002
    ac.activity_count,                                                       -- FARM-003
    ls.leased_farm_count,                                                    -- FARM-008
    ls.lease_expiring_soon                                                   -- FARM-009
FROM active_farms af
CROSS JOIN activities ac
CROSS JOIN leases ls;


-- -----------------------------------------------------------------------------
-- Q2: Farm Overview Table
-- Widget: Master table with key metrics per farm
-- Drill-down: farm row → activities (Q4) + work orders (Q5)
-- -----------------------------------------------------------------------------
SELECT
    f.id                                                                     AS farm_id,
    f.farm_code,
    COALESCE(f.name_te, f.name)                                              AS farm_name,
    f.acres,
    COALESCE(v.name_te, v.name)                                              AS village_name,
    f.status,
    f.lease_start_date,
    f.lease_end_date,
    f.lease_amount,
    COALESCE((
        SELECT COUNT(*)
        FROM farm_activities fa
        WHERE fa.farm_id = f.id
          AND fa.org_id = :org_id
          AND fa.deleted_at IS NULL
          AND fa.activity_date BETWEEN :date_from AND :date_to
    ), 0)                                                                    AS activity_count,
    COALESCE((
        SELECT COUNT(*)
        FROM work_orders wo
        WHERE wo.farm_id = f.id
          AND wo.org_id = :org_id
          AND wo.deleted_at IS NULL
          AND wo.start_time::date BETWEEN :date_from AND :date_to
    ), 0)                                                                    AS work_order_count,
    COALESCE((
        SELECT SUM(wo.cost)
        FROM work_orders wo
        WHERE wo.farm_id = f.id
          AND wo.org_id = :org_id
          AND wo.deleted_at IS NULL
          AND wo.status = 'completed'
          AND wo.start_time::date BETWEEN :date_from AND :date_to
    ), 0)                                                                    AS labor_cost_inr,
    COALESCE((
        SELECT SUM(e.amount)
        FROM expenses e
        WHERE e.farm_id = f.id
          AND e.org_id = :org_id
          AND e.deleted_at IS NULL
          AND e.status = 'posted'
          AND e.expense_date BETWEEN :date_from AND :date_to
    ), 0)                                                                    AS expense_inr
FROM farms f
LEFT JOIN villages v
  ON v.id = f.village_id
 AND v.org_id = :org_id
 AND v.deleted_at IS NULL
WHERE f.org_id = :org_id
  AND f.deleted_at IS NULL
  AND (:farm_id::uuid IS NULL OR f.id = :farm_id)
  AND (:village_id::uuid IS NULL OR f.village_id = :village_id)
ORDER BY f.farm_code;


-- -----------------------------------------------------------------------------
-- Q3: Cost per Acre by Farm
-- Widget: Bar chart (FARM-012)
-- -----------------------------------------------------------------------------
WITH farm_costs AS (
    SELECT
        f.id                                                                 AS farm_id,
        f.farm_code,
        COALESCE(f.name_te, f.name)                                          AS farm_name,
        f.acres,
        COALESCE(SUM(wo.cost) FILTER (
            WHERE wo.status = 'completed'
              AND wo.start_time::date BETWEEN :date_from AND :date_to
        ), 0)                                                                AS labor_cost_inr,
        COALESCE((
            SELECT SUM(e.amount)
            FROM expenses e
            WHERE e.farm_id = f.id
              AND e.org_id = :org_id
              AND e.deleted_at IS NULL
              AND e.status = 'posted'
              AND e.expense_date BETWEEN :date_from AND :date_to
        ), 0)                                                                AS expense_inr
    FROM farms f
    LEFT JOIN work_orders wo
      ON wo.farm_id = f.id
     AND wo.org_id = :org_id
     AND wo.deleted_at IS NULL
    WHERE f.org_id = :org_id
      AND f.deleted_at IS NULL
      AND f.status = 'active'
    GROUP BY f.id, f.farm_code, f.name, f.name_te, f.acres
)
SELECT
    farm_id,
    farm_code,
    farm_name,
    acres,
    labor_cost_inr,
    expense_inr,
    labor_cost_inr + expense_inr                                             AS total_cost_inr,
    ROUND((labor_cost_inr + expense_inr) / NULLIF(acres, 0), 2)              AS cost_per_acre_inr
FROM farm_costs
ORDER BY cost_per_acre_inr DESC;


-- -----------------------------------------------------------------------------
-- Q4: Farm Activities Log
-- Widget: Timeline / table (FARM-003, FARM-011)
-- -----------------------------------------------------------------------------
SELECT
    fa.activity_date,
    f.farm_code,
    COALESCE(f.name_te, f.name)                                              AS farm_name,
    COALESCE(at.name_te, at.name)                                            AS activity_type,
    COALESCE(fa.description_te, fa.description)                              AS description,
    COALESCE(w.full_name_te, w.full_name)                                    AS performed_by
FROM farm_activities fa
JOIN farms f
  ON f.id = fa.farm_id
 AND f.org_id = :org_id
 AND f.deleted_at IS NULL
LEFT JOIN activity_types at
  ON at.id = fa.activity_type_id
 AND at.org_id = :org_id
 AND at.deleted_at IS NULL
LEFT JOIN workers w
  ON w.id = fa.performed_by_worker_id
 AND w.org_id = :org_id
 AND w.deleted_at IS NULL
WHERE fa.org_id = :org_id
  AND fa.deleted_at IS NULL
  AND fa.activity_date BETWEEN :date_from AND :date_to
  AND (:farm_id::uuid IS NULL OR fa.farm_id = :farm_id)
ORDER BY fa.activity_date DESC, f.farm_code
LIMIT 200;


-- -----------------------------------------------------------------------------
-- Q5: Work Orders by Farm
-- Widget: Stacked bar by status (FARM-004, FARM-005)
-- -----------------------------------------------------------------------------
SELECT
    f.farm_code,
    COALESCE(f.name_te, f.name)                                              AS farm_name,
    wo.status,
    COUNT(*)                                                                 AS work_order_count,
    COALESCE(SUM(wo.cost) FILTER (WHERE wo.status = 'completed'), 0)        AS labor_cost_inr,
    COALESCE(SUM(wo.duration_minutes) FILTER (WHERE wo.status = 'completed'), 0) AS duration_minutes
FROM work_orders wo
JOIN farms f
  ON f.id = wo.farm_id
 AND f.org_id = :org_id
 AND f.deleted_at IS NULL
WHERE wo.org_id = :org_id
  AND wo.deleted_at IS NULL
  AND wo.start_time::date BETWEEN :date_from AND :date_to
  AND (:farm_id::uuid IS NULL OR wo.farm_id = :farm_id)
GROUP BY f.farm_code, f.name, f.name_te, wo.status
ORDER BY f.farm_code, wo.status;


-- -----------------------------------------------------------------------------
-- Q6: Attendance at Farms
-- Widget: Heatmap data (FARM-007)
-- Partition key: attendance_date
-- -----------------------------------------------------------------------------
SELECT
    f.farm_code,
    COALESCE(f.name_te, f.name)                                              AS farm_name,
    ar.attendance_date,
    COUNT(*) FILTER (WHERE ar.status IN ('present', 'half_day'))             AS present_count,
    COUNT(*) FILTER (WHERE ar.status = 'absent')                             AS absent_count,
    COUNT(DISTINCT ar.worker_id)                                           AS workers_count
FROM attendance_records ar
JOIN farms f
  ON f.id = ar.farm_id
 AND f.org_id = :org_id
 AND f.deleted_at IS NULL
WHERE ar.org_id = :org_id
  AND ar.attendance_date BETWEEN :date_from AND :date_to
  AND ar.farm_id IS NOT NULL
  AND (:farm_id::uuid IS NULL OR ar.farm_id = :farm_id)
GROUP BY f.farm_code, f.name, f.name_te, ar.attendance_date
ORDER BY ar.attendance_date DESC, f.farm_code;


-- -----------------------------------------------------------------------------
-- Q7: Lease Expiry Alerts
-- Widget: Alert table (FARM-009)
-- -----------------------------------------------------------------------------
SELECT
    f.farm_code,
    COALESCE(f.name_te, f.name)                                              AS farm_name,
    f.acres,
    COALESCE(farmer.full_name_te, farmer.full_name)                          AS owner_farmer_name,
    f.lease_start_date,
    f.lease_end_date,
    f.lease_amount,
    (f.lease_end_date - CURRENT_DATE)                                        AS days_until_expiry
FROM farms f
LEFT JOIN farmers farmer
  ON farmer.id = f.owner_farmer_id
 AND farmer.org_id = :org_id
 AND farmer.deleted_at IS NULL
WHERE f.org_id = :org_id
  AND f.deleted_at IS NULL
  AND f.status = 'active'
  AND f.lease_end_date IS NOT NULL
  AND f.lease_end_date BETWEEN CURRENT_DATE AND CURRENT_DATE + 90
ORDER BY f.lease_end_date ASC;


-- -----------------------------------------------------------------------------
-- Q8: Crop History by Season (linked via owner farmer)
-- Widget: Seasonal summary (FARM-010)
-- Phase note: uses farmer_crop_history for farms with owner_farmer_id
-- -----------------------------------------------------------------------------
SELECT
    f.farm_code,
    COALESCE(f.name_te, f.name)                                              AS farm_name,
    fch.season,
    fch.year,
    ct.code                                                                  AS crop_code,
    COALESCE(ct.name_te, ct.name)                                            AS crop_name,
    COALESCE(SUM(fch.acres), 0)                                              AS crop_acres
FROM farms f
JOIN farmers farmer
  ON farmer.id = f.owner_farmer_id
 AND farmer.org_id = :org_id
 AND farmer.deleted_at IS NULL
JOIN farmer_crop_history fch
  ON fch.farmer_id = farmer.id
 AND fch.org_id = :org_id
 AND fch.deleted_at IS NULL
JOIN crop_types ct
  ON ct.id = fch.crop_type_id
 AND ct.org_id = :org_id
 AND ct.deleted_at IS NULL
WHERE f.org_id = :org_id
  AND f.deleted_at IS NULL
  AND (:farm_id::uuid IS NULL OR f.id = :farm_id)
GROUP BY f.farm_code, f.name, f.name_te, fch.season, fch.year, ct.code, ct.name, ct.name_te
ORDER BY fch.year DESC, fch.season, f.farm_code;
