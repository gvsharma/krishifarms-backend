-- 00_prerequisites.sql
-- KrishiFarms CRM — synthetic seed prerequisites
-- Run AFTER: alembic upgrade head && python scripts/seed.py

BEGIN;

-- Flag organization as having synthetic demo data loaded
UPDATE organizations
SET settings = COALESCE(settings, '{}'::jsonb) || jsonb_build_object(
    'synthetic_data_loaded', false,
    'synthetic_data_marker', 'SYNTHETIC_DATA',
    'synthetic_village', 'Bhairkhanpally'
)
WHERE code = 'KRISHI';

-- Village: Bhairkhanpally (deterministic UUID — uuid5 from generate_synthetic_data.py)
INSERT INTO villages (id, org_id, name, name_te, mandal, district, state, pincode, created_by, updated_by)
SELECT
    '97bc8297-5f82-5ad6-8e5c-de4c04c0e7d6'::uuid,
    o.id,
    'Bhairkhanpally',
    'భైర్ఖాన్‌పల్లి',
    'Medak',
    'Medak',
    'Telangana',
    '502334',
    u.id,
    u.id
FROM organizations o
CROSS JOIN users u
WHERE o.code = 'KRISHI' AND u.email = 'owner@krishifarms.local'
  AND NOT EXISTS (
    SELECT 1 FROM villages v WHERE v.org_id = o.id AND v.name = 'Bhairkhanpally' AND v.deleted_at IS NULL
  );

-- Crop types: Paddy and Corn (deterministic UUIDs from generator)
INSERT INTO crop_types (id, org_id, name, name_te, code, default_moisture_pct, is_active, created_by, updated_by)
SELECT '545639a0-04e6-569d-b274-0e961b102b71'::uuid, o.id, 'Paddy', 'వరి', 'PADDY', 14.0, true, u.id, u.id
FROM organizations o CROSS JOIN users u
WHERE o.code = 'KRISHI' AND u.email = 'owner@krishifarms.local'
  AND NOT EXISTS (SELECT 1 FROM crop_types c WHERE c.org_id = o.id AND c.code = 'PADDY' AND c.deleted_at IS NULL);

INSERT INTO crop_types (id, org_id, name, name_te, code, default_moisture_pct, is_active, created_by, updated_by)
SELECT '9f8db97a-41f6-5609-9d0d-82930861f14c'::uuid, o.id, 'Corn', 'మొక్కజొన్న', 'CORN', 12.0, true, u.id, u.id
FROM organizations o CROSS JOIN users u
WHERE o.code = 'KRISHI' AND u.email = 'owner@krishifarms.local'
  AND NOT EXISTS (SELECT 1 FROM crop_types c WHERE c.org_id = o.id AND c.code = 'CORN' AND c.deleted_at IS NULL);

-- Payment modes
INSERT INTO payment_modes (id, org_id, code, name, name_te, is_active, created_by, updated_by)
SELECT gen_random_uuid(), o.id, pm.code, pm.name, pm.name_te, true, u.id, u.id
FROM organizations o
CROSS JOIN users u
CROSS JOIN (VALUES
    ('cash', 'Cash', 'నగదు'),
    ('upi', 'UPI', 'యూపీఐ'),
    ('bank_transfer', 'Bank Transfer', 'బ్యాంక్ బదిలీ')
) AS pm(code, name, name_te)
WHERE o.code = 'KRISHI' AND u.email = 'owner@krishifarms.local'
  AND NOT EXISTS (
    SELECT 1 FROM payment_modes p WHERE p.org_id = o.id AND p.code = pm.code AND p.deleted_at IS NULL
  );

COMMIT;
