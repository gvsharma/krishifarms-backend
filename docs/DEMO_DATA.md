# Demo data (temporary — remove before production)

Temporary org-scoped demo pack for **live** Android + CRM modules against Supabase.
**Do not ship this data to production.** Purge before go-live.

Related: [SUPABASE_MIGRATION.md](./deploy/SUPABASE_MIGRATION.md), [AGENT_GUIDE.md](./AGENT_GUIDE.md).

---

## Inventory

| Layer | Approx | Notes |
|-------|--------|--------|
| Alembic base tables | ~60 | Full schema via `alembic upgrade head` |
| Partitioned tables | 7 | Monthly partitions; ID lookups need partition date |
| OpenAPI path templates | ~73 | Spec ahead of Python for Phase 2+ |
| Live FastAPI handlers | ~80+ | Mounted in `app/main.py` |

### Live API prefixes (both clients)

`/api/v1/auth`, `/users`, `/roles`, `/villages`, `/crop-types`, `/buyers`, `/agents`, `/crop-prices`, `/comments`, `/tags`, `/farmers` (+ bank/land/outstanding), `/procurements` (+ workflow), `/documents` (partial), `/dashboard/summary`, `/activity-feed`, `/audit-logs`, `/health`

### Out of scope for this demo pack

Workers, assets, rentals, expenses/collections, farmer payments APIs — schema may exist; no shared live UI yet. Use `scripts/synthetic_seed/` later if needed.

---

## Markers (purge keys)

| Marker | Where |
|--------|--------|
| `[DEMO]` | `notes`, comment `body` / `body_te`, addresses |
| `@demo.krishifarms.local` | Demo MANAGER / AGENT emails |
| `demo-*` | Procurement `idempotency_key` |
| `DEMO-SY-*` | Land parcel survey numbers |
| `98765000xx` | Demo farmer phones |
| `org.settings.demo_data_loaded` | Idempotency flag + `demo_batch_id` |

---

## What gets loaded

- Bootstrap org `KRISHI` + OWNER (if empty; reuses migration permissions)
- Users: `manager@demo.krishifarms.local`, `agent@demo.krishifarms.local` (password `DemoPass123!`)
- Villages: Bhairkhanpally, Raigiri, Turkapally
- Crops: Paddy, Corn + crop price rules
- Buyers / field agents
- ~15 farmers (5 with bank + land)
- ~25 procurements: draft / weighed / priced / confirmed (ledger on confirm)
- Comments + `demo` tags; activity/audit via services

Default OWNER (from settings): `owner@krishifarms.local` / `ChangeMe123!`

---

## Load / purge runbook

Requires `DATABASE_URL` (Supabase pooler) and `SECRET_KEY` (bank encryption). Prefer running **inside the API container** on EC2 so deps match production.

### After deploy (EC2 / SSM)

```bash
# On EC2 (or SSM Run Command)
CID=$(docker compose -f /opt/krishifarms/repo/infra/docker-compose.prod.yml ps -q api)

# After scripts are in the image (or docker cp from a feature branch checkout):
docker compose -f /opt/krishifarms/repo/infra/docker-compose.prod.yml exec -T api \
  python scripts/seed_demo_data.py

# Idempotent: skips if org.settings.demo_data_loaded is true
# Re-seed after purge:
docker compose -f /opt/krishifarms/repo/infra/docker-compose.prod.yml exec -T api \
  python scripts/purge_demo_data.py
docker compose -f /opt/krishifarms/repo/infra/docker-compose.prod.yml exec -T api \
  python scripts/seed_demo_data.py
```

### Local laptop (against Supabase)

```bash
export DATABASE_URL="$(aws ssm get-parameter --name /krishifarms/dev/db/database_url \
  --with-decryption --region ap-south-1 --query Parameter.Value --output text)"
export SECRET_KEY="$(aws ssm get-parameter --name /krishifarms/dev/app/secret_key \
  --with-decryption --region ap-south-1 --query Parameter.Value --output text)"
python scripts/seed_demo_data.py
python scripts/purge_demo_data.py          # or --dry-run
```

Do **not** commit real URLs/passwords.

### Before production

1. `python scripts/purge_demo_data.py`
2. Confirm counts: farmers/procurements with `[DEMO]` = 0; no `@demo.krishifarms.local` users
3. Change OWNER password; remove demo users if any remain
4. Optional: drop `demo_*` keys from `organizations.settings`

---

## Client verification (same org)

CRM and Android share `/api/v1` + the same Supabase DB. `org_id` comes from JWT only.

```bash
BASE=http://13.232.200.243:8082/api/v1
TOKEN=$(curl -sf -X POST "$BASE/auth/login" \
  -H 'Content-Type: application/json' \
  -d '{"email":"owner@krishifarms.local","password":"ChangeMe123!"}' \
  | jq -r '.data.access_token')

curl -sf "$BASE/farmers?page=1&page_size=5" -H "Authorization: Bearer $TOKEN" | jq '.data.total'
curl -sf "$BASE/procurements?page=1&page_size=5" -H "Authorization: Bearer $TOKEN" | jq '.data.total'
curl -sf "$BASE/dashboard/summary" -H "Authorization: Bearer $TOKEN" | jq '.data'
```

Android: Firebase OTP → `POST /auth/firebase-login`, or password/mobile `POST /auth/login` → same farmers/procurements counts for that org.

Verified against EC2 (`:8082`): OWNER/MANAGER email login and AGENT mobile login return the same org-scoped totals (15 farmers, 25 procurements).

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/seed_demo_data.py` | Load demo pack (`--force` after purge) |
| `scripts/purge_demo_data.py` | FK-safe delete by markers (`--dry-run`) |
| `scripts/seed.py` | Minimal bootstrap only (org/OWNER); not the demo pack |
| `scripts/synthetic_seed/` | Broader SYN- UAT set (workers/assets/etc.) |
