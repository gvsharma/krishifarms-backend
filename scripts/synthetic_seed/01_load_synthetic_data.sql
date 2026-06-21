-- Wrapper: run from scripts/synthetic_seed/
\echo 'Loading SYNTHETIC seed data (safe to purge later)...'

BEGIN;

UPDATE organizations
SET settings = COALESCE(settings, '{}'::jsonb) || jsonb_build_object(
    'synthetic_data_loaded', true,
    'synthetic_data_loaded_at', to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'),
    'synthetic_data_marker', 'SYNTHETIC_DATA'
)
WHERE code = 'KRISHI';

\i sql/generated_inserts.sql

COMMIT;

\echo 'SYNTHETIC seed load complete.'
