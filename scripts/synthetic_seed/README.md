# KrishiFarms CRM — Synthetic Seed Data

**⚠️ ALL data in this folder is SYNTHETIC demo data.**  
It is safe to load for development/UAT and **must be purged** before entering real production records.

## Synthetic identification (triple marker)

| Marker | Example |
|--------|---------|
| Code prefix | `SYN-FMR-001`, `SYN-PROC-2026-0042`, `SYN-AST-TRC-001` |
| `notes` field | `SYNTHETIC_DATA — safe to delete before loading real production data` |
| CSV column | `data_source=synthetic` |
| Org setting | `organizations.settings.synthetic_data_loaded = true` |

## Record counts

| Entity | Count |
|--------|------:|
| Farmers | 50 |
| Workers | 10 |
| Farms | 5 |
| Assets | 6 (3 tractors, 1 DCM, 1 baler, 1 Bolero) |
| Procurements | 200 |
| Farmer ledger entries | 207 (confirmed procurements + farmer payments) |
| Farmer payments | 30 |
| Operational payments | 20 |
| **Total payments** | **50** |
| Expenses | 100 |
| Collections | 50 |
| Rental customers | 10 (supporting collections) |
| Rental agreements | 15 (supporting collections) |

**Village:** Bhairkhanpally, Telangana  
**Crops:** Paddy (₹2100–2400/quintal), Corn (₹1800–2100/quintal)  
**Procurement dates:** Jan–Jun 2026 (partition year)

## Files

```text
scripts/synthetic_seed/
  generate_synthetic_data.py   # Regenerate CSV + SQL
  manifest.json              # UUIDs and counts (after generate)
  csv/                       # One CSV per entity
  sql/
    00_prerequisites.sql     # Village, crops, payment modes
    01_load_synthetic_data.sql
    generated_inserts.sql    # Auto-generated INSERTs
    99_purge_synthetic_data.sql
```

## Load instructions

```bash
# 1. Database ready
alembic upgrade head
python scripts/seed.py

# 2. Generate CSV + SQL (deterministic, seed=42)
python scripts/synthetic_seed/generate_synthetic_data.py

# 3. Load prerequisites + data (run from scripts/synthetic_seed/)
cd scripts/synthetic_seed
psql "$DATABASE_URL" -f 00_prerequisites.sql
psql "$DATABASE_URL" -f 01_load_synthetic_data.sql
```

### Docker Compose

```bash
docker compose -f infra/docker-compose.yml exec -T postgres \
  psql -U krishi -d krishifarms -f - < scripts/synthetic_seed/sql/00_prerequisites.sql

# Copy generated SQL into container or mount volume, then:
docker compose -f infra/docker-compose.yml exec -T postgres \
  psql -U krishi -d krishifarms -f /path/to/01_load_synthetic_data.sql
```

## Purge instructions (before real data)

```bash
cd scripts/synthetic_seed
psql "$DATABASE_URL" -f 99_purge_synthetic_data.sql
```

This removes all rows with `SYN-` codes or `SYNTHETIC_DATA` notes.  
**Master data** (Bhairkhanpally village, Paddy/Corn crop types) is retained.

## Regenerate

```bash
python scripts/synthetic_seed/generate_synthetic_data.py
```

Uses fixed random seed `42` for reproducible UUIDs and amounts.

## Asset inventory

| Code | Asset | Category |
|------|-------|----------|
| SYN-AST-TRC-001 | Mahindra 575 DI | tractor |
| SYN-AST-TRC-002 | Swaraj 744 FE | tractor |
| SYN-AST-TRC-003 | John Deere 5050D | tractor |
| SYN-AST-DCM-001 | DCM Trailer | dcm |
| SYN-AST-BAL-001 | Balers Pack-Master | baler |
| SYN-AST-BOL-001 | Mahindra Bolero Pickup | other |
