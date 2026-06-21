-- =============================================================================
-- Dashboard 3: Worker Productivity
-- Parameters: :org_id UUID, :date_from DATE, :date_to DATE
-- Optional: :farm_id UUID, :worker_id UUID
-- Partition key: attendance_records.attendance_date
-- KPIs: WRK-001 through WRK-012
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Q1: Workforce KPI Summary
-- Widget: KPI cards
-- -----------------------------------------------------------------------------
WITH attendance AS (
    SELECT
        ar.worker_id,
        ar.attendance_date,
        ar.status,
        CASE ar.status
            WHEN 'present'   THEN 1.0
            WHEN 'half_day'  THEN 0.5
            ELSE 0.0
        END                                                                  AS present_weight
    FROM attendance_records ar
    WHERE ar.org_id = :org_id
      AND ar.attendance_date BETWEEN :date_from AND :date_to
      AND (:farm_id::uuid IS NULL OR ar.farm_id = :farm_id)
),
work AS (
    SELECT
        wo.id,
        wo.worker_id,
        wo.farm_id,
        wo.status,
        wo.cost,
        wo.duration_minutes,
        wo.rate_type
    FROM work_orders wo
    WHERE wo.org_id = :org_id
      AND wo.deleted_at IS NULL
      AND wo.start_time::date BETWEEN :date_from AND :date_to
      AND (:farm_id::uuid IS NULL OR wo.farm_id = :farm_id)
      AND (:worker_id::uuid IS NULL OR wo.worker_id = :worker_id)
)
SELECT
    ROUND(
        COALESCE(SUM(a.present_weight), 0)
        / NULLIF(COUNT(*), 0) * 100,
        2
    )                                                                        AS attendance_rate_pct,      -- WRK-001
    COUNT(*) FILTER (WHERE a.status IN ('present', 'half_day'))              AS present_days,             -- WRK-002
    COUNT(*) FILTER (WHERE a.status = 'absent')                              AS absent_days,              -- WRK-003
    (SELECT COUNT(*) FROM work w WHERE w.status = 'completed')               AS work_orders_completed,    -- WRK-004
    (SELECT COUNT(*) FROM work w WHERE w.status IN ('open', 'in_progress'))  AS work_orders_open,         -- WRK-005
    COALESCE((SELECT SUM(w.cost) FROM work w WHERE w.status = 'completed'), 0) AS total_labor_cost_inr,   -- WRK-006
    COALESCE((SELECT SUM(w.duration_minutes) FROM work w WHERE w.status = 'completed'), 0) AS total_duration_min, -- WRK-007
    COUNT(DISTINCT a.worker_id) FILTER (WHERE a.status IN ('present', 'half_day')) AS active_workers      -- WRK-012
FROM attendance a;


-- -----------------------------------------------------------------------------
-- Q2: Daily Attendance Trend
-- Widget: Stacked bar (present / absent / half_day / leave)
-- -----------------------------------------------------------------------------
SELECT
    ar.attendance_date                                                       AS report_date,
    COUNT(*) FILTER (WHERE ar.status = 'present')                            AS present_count,
    COUNT(*) FILTER (WHERE ar.status = 'half_day')                           AS half_day_count,
    COUNT(*) FILTER (WHERE ar.status = 'absent')                             AS absent_count,
    COUNT(*) FILTER (WHERE ar.status = 'leave')                              AS leave_count,
    COUNT(DISTINCT ar.worker_id)                                             AS workers_recorded
FROM attendance_records ar
WHERE ar.org_id = :org_id
  AND ar.attendance_date BETWEEN :date_from AND :date_to
  AND (:farm_id::uuid IS NULL OR ar.farm_id = :farm_id)
GROUP BY ar.attendance_date
ORDER BY ar.attendance_date;


-- -----------------------------------------------------------------------------
-- Q3: Worker Leaderboard
-- Widget: Ranked table
-- Drill-down: worker → attendance calendar + work orders
-- -----------------------------------------------------------------------------
WITH attendance AS (
    SELECT
        ar.worker_id,
        COUNT(*) FILTER (WHERE ar.status IN ('present', 'half_day'))         AS present_days,
        COUNT(*) FILTER (WHERE ar.status = 'absent')                         AS absent_days
    FROM attendance_records ar
    WHERE ar.org_id = :org_id
      AND ar.attendance_date BETWEEN :date_from AND :date_to
    GROUP BY ar.worker_id
),
work AS (
    SELECT
        wo.worker_id,
        COUNT(*) FILTER (WHERE wo.status = 'completed')                      AS completed_orders,
        COALESCE(SUM(wo.cost) FILTER (WHERE wo.status = 'completed'), 0)     AS labor_cost_inr,
        COALESCE(SUM(wo.duration_minutes) FILTER (WHERE wo.status = 'completed'), 0) AS duration_minutes
    FROM work_orders wo
    WHERE wo.org_id = :org_id
      AND wo.deleted_at IS NULL
      AND wo.start_time::date BETWEEN :date_from AND :date_to
    GROUP BY wo.worker_id
)
SELECT
    w.id                                                                     AS worker_id,
    w.worker_code,
    COALESCE(w.full_name_te, w.full_name)                                    AS worker_name,
    COALESCE(a.present_days, 0)                                              AS present_days,
    COALESCE(a.absent_days, 0)                                               AS absent_days,
    COALESCE(wk.completed_orders, 0)                                         AS completed_work_orders,
    COALESCE(wk.labor_cost_inr, 0)                                           AS labor_cost_inr,
    COALESCE(wk.duration_minutes, 0)                                         AS duration_minutes,
    ROUND(
        COALESCE(wk.completed_orders, 0)::numeric
        / NULLIF(COALESCE(a.present_days, 0), 0),
        2
    )                                                                        AS orders_per_present_day    -- WRK-010 proxy
FROM workers w
LEFT JOIN attendance a ON a.worker_id = w.id
LEFT JOIN work wk ON wk.worker_id = w.id
WHERE w.org_id = :org_id
  AND w.deleted_at IS NULL
  AND w.status = 'active'
  AND (:worker_id::uuid IS NULL OR w.id = :worker_id)
ORDER BY labor_cost_inr DESC, completed_work_orders DESC
LIMIT 30;


-- -----------------------------------------------------------------------------
-- Q4: Labor Cost by Farm
-- Widget: Bar chart (WRK-009)
-- Drill-down: farm → work orders list
-- -----------------------------------------------------------------------------
SELECT
    f.id                                                                     AS farm_id,
    f.farm_code,
    COALESCE(f.name_te, f.name)                                              AS farm_name,
    COUNT(*) FILTER (WHERE wo.status = 'completed')                          AS completed_work_orders,
    COALESCE(SUM(wo.cost) FILTER (WHERE wo.status = 'completed'), 0)         AS labor_cost_inr,
    COALESCE(SUM(wo.duration_minutes) FILTER (WHERE wo.status = 'completed'), 0) AS duration_minutes
FROM work_orders wo
JOIN farms f
  ON f.id = wo.farm_id
 AND f.org_id = :org_id
 AND f.deleted_at IS NULL
WHERE wo.org_id = :org_id
  AND wo.deleted_at IS NULL
  AND wo.start_time::date BETWEEN :date_from AND :date_to
GROUP BY f.id, f.farm_code, f.name, f.name_te
ORDER BY labor_cost_inr DESC;


-- -----------------------------------------------------------------------------
-- Q5: Work Orders by Activity Type
-- Widget: Donut chart
-- -----------------------------------------------------------------------------
SELECT
    at.id                                                                    AS activity_type_id,
    at.code                                                                  AS activity_code,
    COALESCE(at.name_te, at.name)                                            AS activity_name,
    COUNT(*)                                                                 AS work_order_count,
    COALESCE(SUM(wo.cost) FILTER (WHERE wo.status = 'completed'), 0)         AS labor_cost_inr,
    COALESCE(SUM(wo.duration_minutes) FILTER (WHERE wo.status = 'completed'), 0) AS duration_minutes
FROM work_orders wo
LEFT JOIN activity_types at
  ON at.id = wo.activity_type_id
 AND at.org_id = :org_id
 AND at.deleted_at IS NULL
WHERE wo.org_id = :org_id
  AND wo.deleted_at IS NULL
  AND wo.start_time::date BETWEEN :date_from AND :date_to
GROUP BY at.id, at.code, at.name, at.name_te
ORDER BY work_order_count DESC;


-- -----------------------------------------------------------------------------
-- Q6: Weekly Productivity Trend
-- Widget: Line chart (completed orders + labor cost by week)
-- -----------------------------------------------------------------------------
SELECT
    DATE_TRUNC('week', wo.start_time)::date                                   AS week_start,
    COUNT(*) FILTER (WHERE wo.status = 'completed')                          AS completed_orders,
    COALESCE(SUM(wo.cost) FILTER (WHERE wo.status = 'completed'), 0)         AS labor_cost_inr,
    COALESCE(SUM(wo.duration_minutes) FILTER (WHERE wo.status = 'completed'), 0) AS duration_minutes
FROM work_orders wo
WHERE wo.org_id = :org_id
  AND wo.deleted_at IS NULL
  AND wo.start_time::date BETWEEN :date_from AND :date_to
GROUP BY DATE_TRUNC('week', wo.start_time)
ORDER BY week_start;


-- -----------------------------------------------------------------------------
-- Q7: Hourly Rate Efficiency
-- Widget: Table for hourly work orders (WRK-011)
-- -----------------------------------------------------------------------------
SELECT
    wo.work_order_number,
    wo.worker_id,
    wo.start_time,
    wo.end_time,
    wo.duration_minutes,
    wo.rate,
    wo.cost,
    ROUND(
        wo.cost / NULLIF(wo.duration_minutes / 60.0, 0),
        2
    )                                                                        AS effective_hourly_rate_inr
FROM work_orders wo
WHERE wo.org_id = :org_id
  AND wo.deleted_at IS NULL
  AND wo.rate_type = 'hourly'
  AND wo.status = 'completed'
  AND wo.start_time::date BETWEEN :date_from AND :date_to
  AND wo.duration_minutes IS NOT NULL
  AND wo.cost IS NOT NULL
ORDER BY wo.start_time DESC
LIMIT 100;


-- -----------------------------------------------------------------------------
-- Q8: Open Work Orders Backlog
-- Widget: Table with aging
-- -----------------------------------------------------------------------------
SELECT
    wo.work_order_number,
    wo.worker_id,
    wo.farm_id,
    wo.status,
    wo.start_time,
    wo.rate_type,
    wo.rate,
    (CURRENT_DATE - wo.start_time::date)                                     AS days_open
FROM work_orders wo
WHERE wo.org_id = :org_id
  AND wo.deleted_at IS NULL
  AND wo.status IN ('open', 'in_progress')
ORDER BY wo.start_time ASC;
