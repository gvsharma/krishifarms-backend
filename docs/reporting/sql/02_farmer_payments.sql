-- =============================================================================
-- Dashboard 2: Farmer Payments
-- Parameters: :org_id UUID, :date_from DATE, :date_to DATE
-- Optional: :farmer_id UUID, :payment_mode_id UUID
-- Partition keys: farmer_payments.payment_date, farmer_ledger_entries.entry_date
-- KPIs: PAY-001 through PAY-012
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Q1: Payment KPI Summary
-- Widget: KPI cards — disbursed, count, advance vs final, allocation coverage
-- -----------------------------------------------------------------------------
WITH payments AS (
    SELECT
        fp.id,
        fp.payment_date,
        fp.amount,
        fp.payment_type,
        fp.status
    FROM farmer_payments fp
    WHERE fp.org_id = :org_id
      AND fp.payment_date BETWEEN :date_from AND :date_to
      AND fp.status = 'completed'
),
allocations AS (
    SELECT
        fpa.payment_id,
        fpa.payment_date,
        SUM(fpa.allocated_amount) AS allocated_amount
    FROM farmer_payment_allocations fpa
    WHERE fpa.org_id = :org_id
      AND fpa.payment_date BETWEEN :date_from AND :date_to
    GROUP BY fpa.payment_id, fpa.payment_date
)
SELECT
    COALESCE(SUM(p.amount), 0)                                               AS total_disbursed_inr,      -- PAY-001
    COUNT(*)                                                                 AS payment_count,            -- PAY-002
    COALESCE(SUM(p.amount) FILTER (WHERE p.payment_type = 'advance'), 0)     AS advance_inr,              -- PAY-003
    COALESCE(SUM(p.amount) FILTER (WHERE p.payment_type = 'final'), 0)       AS final_inr,                -- PAY-004
    COALESCE(SUM(a.allocated_amount), 0)                                     AS total_allocated_inr,
    ROUND(
        COALESCE(SUM(a.allocated_amount), 0)
        / NULLIF(COALESCE(SUM(p.amount), 0), 0) * 100,
        2
    )                                                                        AS allocation_coverage_pct   -- PAY-007
FROM payments p
LEFT JOIN allocations a
  ON a.payment_id = p.id
 AND a.payment_date = p.payment_date;


-- -----------------------------------------------------------------------------
-- Q2: Outstanding Balances (latest snapshot per farmer)
-- Widget: KPI card + AR table
-- Uses farmer_outstanding_snapshots; point-in-time as_of_date <= :date_to
-- -----------------------------------------------------------------------------
WITH latest_snapshot AS (
    SELECT DISTINCT ON (fos.farmer_id)
        fos.farmer_id,
        fos.as_of_date,
        fos.outstanding_amount
    FROM farmer_outstanding_snapshots fos
    WHERE fos.org_id = :org_id
      AND fos.as_of_date <= :date_to
    ORDER BY fos.farmer_id, fos.as_of_date DESC
)
SELECT
    COALESCE(SUM(ls.outstanding_amount), 0)                                  AS total_outstanding_inr,    -- PAY-005
    COUNT(*) FILTER (WHERE ls.outstanding_amount > 0)                        AS farmers_with_outstanding, -- PAY-006
    MAX(ls.as_of_date)                                                       AS snapshot_as_of_date
FROM latest_snapshot ls;


-- -----------------------------------------------------------------------------
-- Q3: Top Outstanding Farmers
-- Widget: Ranked table
-- Drill-down: farmer → ledger entries (Q6) → payments
-- -----------------------------------------------------------------------------
WITH latest_snapshot AS (
    SELECT DISTINCT ON (fos.farmer_id)
        fos.farmer_id,
        fos.as_of_date,
        fos.outstanding_amount
    FROM farmer_outstanding_snapshots fos
    WHERE fos.org_id = :org_id
      AND fos.as_of_date <= :date_to
    ORDER BY fos.farmer_id, fos.as_of_date DESC
)
SELECT
    f.id                                                                     AS farmer_id,
    f.farmer_code,
    COALESCE(f.full_name_te, f.full_name)                                    AS farmer_name,
    COALESCE(v.name_te, v.name)                                              AS village_name,
    ls.outstanding_amount,
    ls.as_of_date
FROM latest_snapshot ls
JOIN farmers f
  ON f.id = ls.farmer_id
 AND f.org_id = :org_id
 AND f.deleted_at IS NULL
JOIN villages v
  ON v.id = f.village_id
 AND v.org_id = :org_id
 AND v.deleted_at IS NULL
WHERE ls.outstanding_amount > 0
ORDER BY ls.outstanding_amount DESC
LIMIT 25;


-- -----------------------------------------------------------------------------
-- Q4: Daily Payment Trend
-- Widget: Area chart
-- -----------------------------------------------------------------------------
SELECT
    fp.payment_date                                                          AS report_date,
    COALESCE(SUM(fp.amount), 0)                                              AS amount_inr,
    COUNT(*)                                                                 AS payment_count
FROM farmer_payments fp
WHERE fp.org_id = :org_id
  AND fp.payment_date BETWEEN :date_from AND :date_to
  AND fp.status = 'completed'
GROUP BY fp.payment_date
ORDER BY fp.payment_date;


-- -----------------------------------------------------------------------------
-- Q5: Payment Mode Breakdown
-- Widget: Pie chart (PAY-009)
-- -----------------------------------------------------------------------------
SELECT
    pm.id                                                                    AS payment_mode_id,
    pm.code                                                                  AS payment_mode_code,
    COALESCE(pm.name_te, pm.name)                                            AS payment_mode_name,
    COALESCE(SUM(fp.amount), 0)                                              AS amount_inr,
    COUNT(*)                                                                 AS payment_count
FROM farmer_payments fp
JOIN payment_modes pm
  ON pm.id = fp.payment_mode_id
 AND pm.org_id = :org_id
 AND pm.deleted_at IS NULL
WHERE fp.org_id = :org_id
  AND fp.payment_date BETWEEN :date_from AND :date_to
  AND fp.status = 'completed'
GROUP BY pm.id, pm.code, pm.name, pm.name_te
ORDER BY amount_inr DESC;


-- -----------------------------------------------------------------------------
-- Q6: Farmer Ledger Activity
-- Widget: Table / timeline per farmer
-- Immutable ledger — filter entry_date for partition pruning
-- Drill-down: entry → reference entity (procurement/payment)
-- -----------------------------------------------------------------------------
SELECT
    fle.id                                                                   AS ledger_entry_id,
    fle.entry_date,
    fle.entry_type,
    fle.reference_type,
    fle.reference_id,
    fle.debit,
    fle.credit,
    fle.balance_after,
    fle.description,
    fle.posted_at
FROM farmer_ledger_entries fle
WHERE fle.org_id = :org_id
  AND fle.entry_date BETWEEN :date_from AND :date_to
  AND (:farmer_id::uuid IS NULL OR fle.farmer_id = :farmer_id)
ORDER BY fle.entry_date DESC, fle.posted_at DESC
LIMIT 500;


-- -----------------------------------------------------------------------------
-- Q7: Ledger Summary by Entry Type
-- Widget: Stacked bar (debits vs credits)
-- -----------------------------------------------------------------------------
SELECT
    fle.entry_type,
    fle.reference_type,
    COALESCE(SUM(fle.debit), 0)                                              AS total_debit_inr,
    COALESCE(SUM(fle.credit), 0)                                             AS total_credit_inr,
    COUNT(*)                                                                 AS entry_count
FROM farmer_ledger_entries fle
WHERE fle.org_id = :org_id
  AND fle.entry_date BETWEEN :date_from AND :date_to
GROUP BY fle.entry_type, fle.reference_type
ORDER BY total_debit_inr + total_credit_inr DESC;


-- -----------------------------------------------------------------------------
-- Q8: Payment Allocation Detail
-- Widget: Table linking payments to procurements
-- KPI: PAY-012 avg days to pay
-- -----------------------------------------------------------------------------
SELECT
    fp.payment_number,
    fp.payment_date,
    fp.payment_type,
    fp.amount                                                                AS payment_amount,
    fpa.allocated_amount,
    p.procurement_number,
    p.procurement_date,
    p.net_amount                                                             AS procurement_net_amount,
    (fp.payment_date - p.procurement_date)                                   AS days_to_pay
FROM farmer_payments fp
JOIN farmer_payment_allocations fpa
  ON fpa.payment_id = fp.id
 AND fpa.payment_date = fp.payment_date
 AND fpa.org_id = :org_id
LEFT JOIN procurements p
  ON p.id = fpa.procurement_id
 AND p.procurement_date = fpa.procurement_date
 AND p.org_id = :org_id
 AND p.deleted_at IS NULL
WHERE fp.org_id = :org_id
  AND fp.payment_date BETWEEN :date_from AND :date_to
  AND fp.status = 'completed'
  AND (:farmer_id::uuid IS NULL OR fp.farmer_id = :farmer_id)
ORDER BY fp.payment_date DESC, fp.payment_number;
