-- 99_purge_synthetic_data.sql
-- Remove ALL synthetic demo data from KrishiFarms CRM
--
-- Identification markers:
--   - Codes prefixed with SYN-
--   - notes containing SYNTHETIC_DATA
--   - organization.settings.synthetic_data_marker = SYNTHETIC_DATA
--
-- Run: psql -f sql/99_purge_synthetic_data.sql

BEGIN;

\echo 'Purging SYNTHETIC data...'

-- Child / financial tables first
DELETE FROM collections
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND (collection_number LIKE 'SYN-%' OR notes LIKE '%SYNTHETIC_DATA%');

DELETE FROM payments
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND (payment_number LIKE 'SYN-%' OR notes LIKE '%SYNTHETIC_DATA%');

DELETE FROM expenses
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND (expense_number LIKE 'SYN-%' OR notes LIKE '%SYNTHETIC_DATA%');

DELETE FROM farmer_payment_allocations
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND payment_id IN (
    SELECT id FROM farmer_payments
    WHERE payment_number LIKE 'SYN-%' OR notes LIKE '%SYNTHETIC_DATA%'
  );

DELETE FROM farmer_payments
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND (payment_number LIKE 'SYN-%' OR notes LIKE '%SYNTHETIC_DATA%');

DELETE FROM procurement_deductions
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND procurement_id IN (
    SELECT id FROM procurements WHERE procurement_number LIKE 'SYN-%'
  );

-- Ledger is immutable; disable trigger for synthetic purge only
ALTER TABLE farmer_ledger_entries DISABLE TRIGGER trg_farmer_ledger_immutable;

DELETE FROM farmer_ledger_entries
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND (description LIKE '%SYNTHETIC%' OR reference_id IN (
    SELECT id FROM procurements WHERE procurement_number LIKE 'SYN-%'
    UNION SELECT id FROM farmer_payments WHERE payment_number LIKE 'SYN-%'
  ));

ALTER TABLE farmer_ledger_entries ENABLE TRIGGER trg_farmer_ledger_immutable;

DELETE FROM procurements
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND (procurement_number LIKE 'SYN-%' OR notes LIKE '%SYNTHETIC_DATA%');

DELETE FROM rental_agreements
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND (agreement_number LIKE 'SYN-%' OR notes LIKE '%SYNTHETIC_DATA%');

DELETE FROM rental_customers
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND customer_code LIKE 'SYN-%';

DELETE FROM asset_usage_logs
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND asset_id IN (SELECT id FROM assets WHERE asset_code LIKE 'SYN-%');

DELETE FROM maintenance_records
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND asset_id IN (SELECT id FROM assets WHERE asset_code LIKE 'SYN-%');

DELETE FROM vehicle_trips
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND trip_number LIKE 'SYN-%';

DELETE FROM assets
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND (asset_code LIKE 'SYN-%' OR notes LIKE '%SYNTHETIC_DATA%');

DELETE FROM farm_activities
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND farm_id IN (SELECT id FROM farms WHERE farm_code LIKE 'SYN-%');

DELETE FROM farms
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND farm_code LIKE 'SYN-%';

DELETE FROM worker_skills
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND worker_id IN (SELECT id FROM workers WHERE worker_code LIKE 'SYN-%');

DELETE FROM work_orders
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND work_order_number LIKE 'SYN-%';

DELETE FROM attendance_records
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND worker_id IN (SELECT id FROM workers WHERE worker_code LIKE 'SYN-%');

DELETE FROM workers
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND worker_code LIKE 'SYN-%';

DELETE FROM farmer_crop_history
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND farmer_id IN (SELECT id FROM farmers WHERE farmer_code LIKE 'SYN-%');

DELETE FROM farmer_land_parcels
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND farmer_id IN (SELECT id FROM farmers WHERE farmer_code LIKE 'SYN-%');

DELETE FROM farmer_bank_accounts
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND farmer_id IN (SELECT id FROM farmers WHERE farmer_code LIKE 'SYN-%');

DELETE FROM farmers
WHERE org_id = (SELECT id FROM organizations WHERE code = 'KRISHI')
  AND (farmer_code LIKE 'SYN-%' OR notes LIKE '%SYNTHETIC_DATA%');

-- Clear org flag (keep village/crops — shared master data)
UPDATE organizations
SET settings = COALESCE(settings, '{}'::jsonb) || jsonb_build_object(
    'synthetic_data_loaded', false,
    'synthetic_data_purged_at', to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"')
)
WHERE code = 'KRISHI';

COMMIT;

\echo 'SYNTHETIC data purge complete.'
