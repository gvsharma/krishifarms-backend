-- =============================================================================
-- Dashboard 5: Rental Income
-- Parameters: :org_id UUID, :date_from DATE, :date_to DATE
-- Optional: :asset_id UUID, :customer_id UUID
-- KPIs: RENT-001 through RENT-012
-- Note: rental_agreements use start_datetime for period overlap (not partitioned)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Q1: Rental KPI Summary
-- Widget: KPI cards — revenue, collected, pending, collection rate
-- Agreements overlapping the date range are included
-- -----------------------------------------------------------------------------
WITH agreements AS (
    SELECT
        ra.id,
        ra.revenue,
        ra.collected_amount,
        ra.pending_collection,
        ra.status
    FROM rental_agreements ra
    WHERE ra.org_id = :org_id
      AND ra.deleted_at IS NULL
      AND ra.start_datetime::date <= :date_to
      AND (ra.end_datetime IS NULL OR ra.end_datetime::date >= :date_from)
      AND (:asset_id::uuid IS NULL OR ra.asset_id = :asset_id)
      AND (:customer_id::uuid IS NULL OR ra.customer_id = :customer_id)
)
SELECT
    COALESCE(SUM(revenue), 0)                                                AS total_revenue_inr,        -- RENT-001
    COALESCE(SUM(collected_amount), 0)                                       AS total_collected_inr,      -- RENT-002
    COALESCE(SUM(pending_collection), 0)                                     AS total_pending_inr,        -- RENT-003
    ROUND(
        COALESCE(SUM(collected_amount), 0)
        / NULLIF(COALESCE(SUM(revenue), 0), 0) * 100,
        2
    )                                                                        AS collection_rate_pct,      -- RENT-004
    COUNT(*) FILTER (WHERE status = 'active')                                AS active_agreements,        -- RENT-005
    COUNT(*) FILTER (WHERE status = 'completed')                             AS completed_agreements,     -- RENT-006
    COUNT(*) FILTER (WHERE pending_collection > 0)                           AS agreements_with_ar        -- RENT-012
FROM agreements;


-- -----------------------------------------------------------------------------
-- Q2: Pending Collections (AR)
-- Widget: Priority table
-- Drill-down: agreement → customer → collections (Q7)
-- -----------------------------------------------------------------------------
SELECT
    ra.agreement_number,
    ra.id                                                                    AS agreement_id,
    rc.customer_code,
    COALESCE(rc.name_te, rc.name)                                            AS customer_name,
    rc.phone,
    a.asset_code,
    COALESCE(a.name_te, a.name)                                              AS asset_name,
    ra.start_datetime,
    ra.end_datetime,
    ra.revenue,
    ra.collected_amount,
    ra.pending_collection,
    ra.status
FROM rental_agreements ra
JOIN rental_customers rc
  ON rc.id = ra.customer_id
 AND rc.org_id = :org_id
 AND rc.deleted_at IS NULL
JOIN assets a
  ON a.id = ra.asset_id
 AND a.org_id = :org_id
 AND a.deleted_at IS NULL
WHERE ra.org_id = :org_id
  AND ra.deleted_at IS NULL
  AND ra.pending_collection > 0
ORDER BY ra.pending_collection DESC;


-- -----------------------------------------------------------------------------
-- Q3: Revenue by Asset Category
-- Widget: Bar chart (RENT-007)
-- -----------------------------------------------------------------------------
SELECT
    a.asset_category,
    COUNT(ra.id)                                                             AS agreement_count,
    COALESCE(SUM(ra.revenue), 0)                                             AS revenue_inr,
    COALESCE(SUM(ra.collected_amount), 0)                                    AS collected_inr,
    COALESCE(SUM(ra.pending_collection), 0)                                  AS pending_inr
FROM rental_agreements ra
JOIN assets a
  ON a.id = ra.asset_id
 AND a.org_id = :org_id
 AND a.deleted_at IS NULL
WHERE ra.org_id = :org_id
  AND ra.deleted_at IS NULL
  AND ra.start_datetime::date <= :date_to
  AND (ra.end_datetime IS NULL OR ra.end_datetime::date >= :date_from)
GROUP BY a.asset_category
ORDER BY revenue_inr DESC;


-- -----------------------------------------------------------------------------
-- Q4: Top Customers by Revenue
-- Widget: Ranked table (RENT-008)
-- -----------------------------------------------------------------------------
SELECT
    rc.id                                                                    AS customer_id,
    rc.customer_code,
    COALESCE(rc.name_te, rc.name)                                            AS customer_name,
    rc.phone,
    COUNT(ra.id)                                                             AS agreement_count,
    COALESCE(SUM(ra.revenue), 0)                                             AS revenue_inr,
    COALESCE(SUM(ra.collected_amount), 0)                                    AS collected_inr,
    COALESCE(SUM(ra.pending_collection), 0)                                  AS pending_inr
FROM rental_agreements ra
JOIN rental_customers rc
  ON rc.id = ra.customer_id
 AND rc.org_id = :org_id
 AND rc.deleted_at IS NULL
WHERE ra.org_id = :org_id
  AND ra.deleted_at IS NULL
  AND ra.start_datetime::date <= :date_to
  AND (ra.end_datetime IS NULL OR ra.end_datetime::date >= :date_from)
GROUP BY rc.id, rc.customer_code, rc.name, rc.name_te, rc.phone
ORDER BY revenue_inr DESC
LIMIT 20;


-- -----------------------------------------------------------------------------
-- Q5: Monthly Rental Revenue Trend
-- Widget: Area chart (revenue vs collected by month)
-- -----------------------------------------------------------------------------
SELECT
    DATE_TRUNC('month', ra.start_datetime)::date                             AS month_start,
    COALESCE(SUM(ra.revenue), 0)                                             AS revenue_inr,
    COALESCE(SUM(ra.collected_amount), 0)                                    AS collected_inr,
    COUNT(*)                                                                 AS agreement_count
FROM rental_agreements ra
WHERE ra.org_id = :org_id
  AND ra.deleted_at IS NULL
  AND ra.start_datetime::date <= :date_to
  AND (ra.end_datetime IS NULL OR ra.end_datetime::date >= :date_from)
GROUP BY DATE_TRUNC('month', ra.start_datetime)
ORDER BY month_start;


-- -----------------------------------------------------------------------------
-- Q6: Rentable Asset Inventory
-- Widget: KPI + table (RENT-011)
-- -----------------------------------------------------------------------------
SELECT
    a.id                                                                     AS asset_id,
    a.asset_code,
    COALESCE(a.name_te, a.name)                                              AS asset_name,
    a.asset_category,
    a.hourly_rate,
    a.daily_rate,
    a.status,
    EXISTS (
        SELECT 1
        FROM rental_agreements ra
        WHERE ra.asset_id = a.id
          AND ra.org_id = :org_id
          AND ra.deleted_at IS NULL
          AND ra.status = 'active'
    )                                                                        AS currently_rented
FROM assets a
WHERE a.org_id = :org_id
  AND a.deleted_at IS NULL
  AND a.is_rentable = TRUE
ORDER BY a.asset_category, a.asset_code;


-- -----------------------------------------------------------------------------
-- Q7: Rental Collections (cash)
-- Widget: Table — collections linked to rental source
-- Partition-independent; filter collection_date
-- -----------------------------------------------------------------------------
SELECT
    c.collection_number,
    c.collection_date,
    c.source_type,
    c.source_id,
    c.amount,
    pm.code                                                                  AS payment_mode_code,
    COALESCE(pm.name_te, pm.name)                                            AS payment_mode_name,
    COALESCE(rc.name_te, rc.name)                                            AS customer_name,
    c.reference_no,
    c.status
FROM collections c
LEFT JOIN payment_modes pm
  ON pm.id = c.payment_mode_id
 AND pm.org_id = :org_id
 AND pm.deleted_at IS NULL
LEFT JOIN rental_customers rc
  ON rc.id = c.customer_id
 AND rc.org_id = :org_id
 AND rc.deleted_at IS NULL
WHERE c.org_id = :org_id
  AND c.collection_date BETWEEN :date_from AND :date_to
  AND c.status = 'posted'
  AND (
      c.source_type ILIKE '%rental%'
      OR c.customer_id IS NOT NULL
  )
ORDER BY c.collection_date DESC;


-- -----------------------------------------------------------------------------
-- Q8: Agreement Detail with Hourly Efficiency
-- Widget: Table (RENT-010)
-- -----------------------------------------------------------------------------
SELECT
    ra.agreement_number,
    ra.rate_type,
    ra.hourly_rate,
    ra.total_hours,
    ra.revenue,
    ra.collected_amount,
    ra.pending_collection,
    ROUND(
        ra.revenue / NULLIF(ra.total_hours, 0),
        2
    )                                                                        AS revenue_per_hour_inr,
    ra.status,
    ra.start_datetime,
    ra.end_datetime
FROM rental_agreements ra
WHERE ra.org_id = :org_id
  AND ra.deleted_at IS NULL
  AND ra.start_datetime::date <= :date_to
  AND (ra.end_datetime IS NULL OR ra.end_datetime::date >= :date_from)
ORDER BY ra.start_datetime DESC
LIMIT 100;
