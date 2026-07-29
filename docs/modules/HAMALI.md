# Hamali (porter) labor — procurement bag handling

Track daily hamali work at the godown: bags lifted, labor pay (default **₹20/bag**), maintenance charges, and tips. Settle on a **weekly** basis (Monday–Sunday).

## Data model (migration `037`)

| Table | Purpose |
|-------|---------|
| `hamali_workers` | Roster — `HML-0001` codes, `default_rate_per_bag` (default 20.00) |
| `hamali_daily_entries` | One row per worker per day — bags, labor, maintenance, tip, payment status |
| `hamali_weekly_payments` | Weekly batch — aggregates pending entries, marks paid |

### Daily entry amounts

```
labor_amount = bags_lifted × rate_per_bag
total_amount = labor_amount + maintenance_amount + tip_amount
```

### Payment flow

1. **Log daily work** — `payment_status = pending`
2. **Create weekly batch** — links pending entries in the week; status → `scheduled`
3. **Mark batch paid** — entries → `paid`; batch → `paid`

## API (`/api/v1/hamali/…`)

| Method | Path | Permission |
|--------|------|------------|
| GET/POST | `/hamali/workers` | read / create |
| PATCH/DELETE | `/hamali/workers/{id}` | update |
| GET/POST | `/hamali/daily-entries` | read / create |
| PATCH/DELETE | `/hamali/daily-entries/{id}` | update |
| GET | `/hamali/weekly-summary?week_start_date=` | read |
| GET/POST | `/hamali/weekly-payments` | read / pay |
| POST | `/hamali/weekly-payments/{id}/mark-paid` | pay |

## Web UI

- Nav: **Operations → Hamali** (`/hamali`) — OWNER, MANAGER, ACCOUNTANT
- Tabs: Daily entries · Workers · Weekly payments

## Related

- Procurement bag count: [PROCUREMENT.md](./PROCUREMENT.md) (farmer weight kata — separate from hamali pay)
- General workforce (Phase 4): `workers` / `work_orders` OpenAPI — farm labor, not godown hamali
