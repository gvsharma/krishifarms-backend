-- =============================================================================
-- Dashboard 4: Vehicle Utilization
-- Parameters: :org_id UUID, :date_from DATE, :date_to DATE
-- Optional: :asset_id UUID, :asset_category TEXT
-- Partition keys: vehicle_trips.trip_date, asset_usage_logs.usage_date
-- KPIs: VEH-001 through VEH-012
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Q1: Fleet KPI Summary
-- Widget: KPI cards
-- -----------------------------------------------------------------------------
WITH trips AS (
    SELECT
        vt.id,
        vt.asset_id,
        vt.trip_date,
        vt.distance_km,
        vt.fuel_liters,
        vt.total_cost,
        vt.loading_charges,
        vt.unloading_charges
    FROM vehicle_trips vt
    WHERE vt.org_id = :org_id
      AND vt.trip_date BETWEEN :date_from AND :date_to
      AND vt.status = 'completed'
      AND (:asset_id::uuid IS NULL OR vt.asset_id = :asset_id)
),
maint AS (
    SELECT COALESCE(SUM(mr.cost), 0) AS maintenance_cost_inr
    FROM maintenance_records mr
    WHERE mr.org_id = :org_id
      AND mr.maintenance_date BETWEEN :date_from AND :date_to
      AND (:asset_id::uuid IS NULL OR mr.asset_id = :asset_id)
)
SELECT
    COUNT(*)                                                                 AS total_trips,              -- VEH-001
    COALESCE(SUM(t.distance_km), 0)                                          AS total_distance_km,        -- VEH-002
    COALESCE(SUM(t.total_cost), 0)                                           AS total_trip_cost_inr,      -- VEH-003
    ROUND(
        COALESCE(SUM(t.total_cost), 0) / NULLIF(COUNT(*), 0),
        2
    )                                                                        AS avg_cost_per_trip_inr,    -- VEH-004
    ROUND(
        COALESCE(SUM(t.total_cost), 0) / NULLIF(COALESCE(SUM(t.distance_km), 0), 0),
        2
    )                                                                        AS cost_per_km_inr,          -- VEH-005
    COALESCE(SUM(t.fuel_liters), 0)                                          AS total_fuel_liters,        -- VEH-006
    ROUND(
        COALESCE(SUM(t.distance_km), 0) / NULLIF(COALESCE(SUM(t.fuel_liters), 0), 0),
        2
    )                                                                        AS fuel_efficiency_km_per_l, -- VEH-007
    COUNT(DISTINCT t.asset_id)                                               AS active_vehicles,          -- VEH-009
    COALESCE(SUM(t.loading_charges + t.unloading_charges), 0)                AS loading_unloading_inr,    -- VEH-010
    (SELECT maintenance_cost_inr FROM maint)                                 AS maintenance_cost_inr      -- VEH-011
FROM trips t;


-- -----------------------------------------------------------------------------
-- Q2: Daily Trip Trend
-- Widget: Dual line (trips count + cost)
-- -----------------------------------------------------------------------------
SELECT
    vt.trip_date                                                             AS report_date,
    COUNT(*)                                                                 AS trip_count,
    COALESCE(SUM(vt.distance_km), 0)                                         AS distance_km,
    COALESCE(SUM(vt.total_cost), 0)                                          AS total_cost_inr,
    COALESCE(SUM(vt.fuel_liters), 0)                                         AS fuel_liters
FROM vehicle_trips vt
WHERE vt.org_id = :org_id
  AND vt.trip_date BETWEEN :date_from AND :date_to
  AND vt.status = 'completed'
GROUP BY vt.trip_date
ORDER BY vt.trip_date;


-- -----------------------------------------------------------------------------
-- Q3: Utilization by Asset
-- Widget: Horizontal bar (trips, km, cost per vehicle)
-- Drill-down: asset → trip list (Q6)
-- -----------------------------------------------------------------------------
WITH period_days AS (
    SELECT GREATEST((:date_to - :date_from + 1), 1) AS days_in_period
)
SELECT
    a.id                                                                     AS asset_id,
    a.asset_code,
    COALESCE(a.name_te, a.name)                                              AS asset_name,
    a.asset_category,
    a.registration_number,
    COUNT(vt.id)                                                             AS trip_count,
    COALESCE(SUM(vt.distance_km), 0)                                         AS distance_km,
    COALESCE(SUM(vt.total_cost), 0)                                          AS total_cost_inr,
    COUNT(DISTINCT vt.trip_date)                                             AS days_with_trips,
    ROUND(
        COUNT(DISTINCT vt.trip_date)::numeric / pd.days_in_period * 100,
        2
    )                                                                        AS utilization_rate_pct      -- VEH-008
FROM assets a
CROSS JOIN period_days pd
LEFT JOIN vehicle_trips vt
  ON vt.asset_id = a.id
 AND vt.org_id = :org_id
 AND vt.trip_date BETWEEN :date_from AND :date_to
 AND vt.status = 'completed'
WHERE a.org_id = :org_id
  AND a.deleted_at IS NULL
  AND a.status = 'active'
  AND a.asset_category IN ('tractor', 'dcm', 'baler', 'air_machine', 'other')
  AND (:asset_id::uuid IS NULL OR a.id = :asset_id)
  AND (:asset_category::text IS NULL OR a.asset_category = :asset_category)
GROUP BY a.id, a.asset_code, a.name, a.name_te, a.asset_category, a.registration_number, pd.days_in_period
ORDER BY trip_count DESC, distance_km DESC;


-- -----------------------------------------------------------------------------
-- Q4: Asset Category Summary
-- Widget: Grouped bar chart
-- -----------------------------------------------------------------------------
SELECT
    a.asset_category,
    COUNT(vt.id)                                                             AS trip_count,
    COALESCE(SUM(vt.distance_km), 0)                                         AS distance_km,
    COALESCE(SUM(vt.total_cost), 0)                                          AS total_cost_inr,
    COUNT(DISTINCT a.id)                                                     AS asset_count
FROM assets a
LEFT JOIN vehicle_trips vt
  ON vt.asset_id = a.id
 AND vt.org_id = :org_id
 AND vt.trip_date BETWEEN :date_from AND :date_to
 AND vt.status = 'completed'
WHERE a.org_id = :org_id
  AND a.deleted_at IS NULL
GROUP BY a.asset_category
ORDER BY total_cost_inr DESC;


-- -----------------------------------------------------------------------------
-- Q5: Top Routes (source → destination)
-- Widget: Table / chord diagram data
-- -----------------------------------------------------------------------------
SELECT
    vt.source,
    COALESCE(vt.source_te, vt.source)                                          AS source_display,
    vt.destination,
    COALESCE(vt.destination_te, vt.destination)                              AS destination_display,
    COUNT(*)                                                                 AS trip_count,
    COALESCE(SUM(vt.distance_km), 0)                                         AS distance_km,
    COALESCE(SUM(vt.total_cost), 0)                                          AS total_cost_inr
FROM vehicle_trips vt
WHERE vt.org_id = :org_id
  AND vt.trip_date BETWEEN :date_from AND :date_to
  AND vt.status = 'completed'
GROUP BY vt.source, vt.source_te, vt.destination, vt.destination_te
ORDER BY trip_count DESC
LIMIT 20;


-- -----------------------------------------------------------------------------
-- Q6: Trip Detail List
-- Widget: Paginated table
-- Drill-down: trip_number → full trip record
-- -----------------------------------------------------------------------------
SELECT
    vt.trip_number,
    vt.trip_date,
    a.asset_code,
    COALESCE(a.name_te, a.name)                                              AS asset_name,
    COALESCE(w.full_name_te, w.full_name)                                    AS driver_name,
    vt.source,
    vt.destination,
    vt.distance_km,
    vt.fuel_liters,
    vt.fuel_cost,
    vt.loading_charges,
    vt.unloading_charges,
    vt.waiting_charges,
    vt.other_charges,
    vt.total_cost,
    vt.status
FROM vehicle_trips vt
JOIN assets a
  ON a.id = vt.asset_id
 AND a.org_id = :org_id
 AND a.deleted_at IS NULL
LEFT JOIN workers w
  ON w.id = vt.driver_worker_id
 AND w.org_id = :org_id
 AND w.deleted_at IS NULL
WHERE vt.org_id = :org_id
  AND vt.trip_date BETWEEN :date_from AND :date_to
  AND (:asset_id::uuid IS NULL OR vt.asset_id = :asset_id)
ORDER BY vt.trip_date DESC, vt.trip_number
LIMIT 200;


-- -----------------------------------------------------------------------------
-- Q7: Asset Usage Logs (machine hours & revenue)
-- Widget: Table overlay on fleet chart (VEH-012)
-- Partition key: usage_date
-- -----------------------------------------------------------------------------
SELECT
    aul.usage_date,
    a.asset_code,
    COALESCE(a.name_te, a.name)                                              AS asset_name,
    aul.machine_hours,
    aul.revenue_generated,
    aul.fuel_cost,
    aul.maintenance_cost,
    ROUND(
        aul.revenue_generated / NULLIF(aul.machine_hours, 0),
        2
    )                                                                        AS revenue_per_machine_hour_inr
FROM asset_usage_logs aul
JOIN assets a
  ON a.id = aul.asset_id
 AND a.org_id = :org_id
 AND a.deleted_at IS NULL
WHERE aul.org_id = :org_id
  AND aul.usage_date BETWEEN :date_from AND :date_to
  AND (:asset_id::uuid IS NULL OR aul.asset_id = :asset_id)
ORDER BY aul.usage_date DESC, a.asset_code;


-- -----------------------------------------------------------------------------
-- Q8: Maintenance History
-- Widget: Timeline / table
-- -----------------------------------------------------------------------------
SELECT
    mr.maintenance_date,
    a.asset_code,
    COALESCE(a.name_te, a.name)                                              AS asset_name,
    mr.description,
    mr.vendor_name,
    mr.cost,
    mr.odometer_km,
    mr.machine_hours
FROM maintenance_records mr
JOIN assets a
  ON a.id = mr.asset_id
 AND a.org_id = :org_id
 AND a.deleted_at IS NULL
WHERE mr.org_id = :org_id
  AND mr.maintenance_date BETWEEN :date_from AND :date_to
  AND (:asset_id::uuid IS NULL OR mr.asset_id = :asset_id)
ORDER BY mr.maintenance_date DESC;
