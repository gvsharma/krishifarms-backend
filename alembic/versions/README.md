# Alembic Migrations

Run all migrations:

```bash
alembic upgrade head
```

Run one step:

```bash
alembic upgrade +1
```

Rollback one step:

```bash
alembic downgrade -1
```

## Migration Order

| Revision | Module | Purpose |
|----------|--------|---------|
| `202506210001` | Platform | Organizations, IAM, master data, documents, audit (Phase 1 baseline) |
| `202506210002` | Platform | Extensions, Telugu columns, user scopes, partial uniques, triggers |
| `202506210003` | Master Data | Activity types, payment modes, number sequences |
| `202506210004` | Farmers | Farmers, bank accounts, land parcels, crop history |
| `202506210005` | Workers | Workers, skills, user linkage |
| `202506210006` | Farms | Farms, farm activities |
| `202506210007` | Documents | OCR/locale/archive columns, link constraints |
| `202506210008` | Procurement | Partitioned procurements, ledger, farmer payments |
| `202506210009` | Workforce | Work orders, attendance, photos |
| `202506210010` | Assets | Assets, maintenance, usage logs, vehicle trips |
| `202506210011` | Rentals | Rental customers and agreements |
| `202506210012` | Financial | Transactions, expenses, collections, payments |
| `202506210013` | Audit/Sync | Audit indexes, sync tables, schema log |
| `202506210014` | AI | WhatsApp, AI jobs, OCR, voice, summaries |
| `202506210015` | Seed Data | Global permissions and per-org system roles |

## Partition Maintenance

Migrations create **2026 monthly partitions** for high-volume tables. Add future partitions with:

```sql
CREATE TABLE procurements_2027_01 PARTITION OF procurements
  FOR VALUES FROM ('2027-01-01') TO ('2027-02-01');
```

Or extend `migration_utils.py#create_monthly_partitions` in a new migration each year.

Shared helpers live in `migration_utils.py` at the project root (imported by version files).

## Notes

- Roles are **org-scoped**; migration `015` seeds roles for every existing organization.
- New organizations created after migration `015` should run `scripts/seed.py` (or equivalent) to create roles.
- Ledger tables are **immutable**; updates/deletes raise an exception via trigger.
