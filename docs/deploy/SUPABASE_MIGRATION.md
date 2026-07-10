# Migrate KrishiFarms CRM database to Supabase

Cutover from **Docker Postgres on EC2** (current production) to **Supabase** managed Postgres. Aurora/RDS is **not** in use for KrishiFarms today.

See also: [CI_CD.md](./CI_CD.md), [deploy/README.md](../../deploy/README.md).

---

## Target Supabase project (provided)

| Field | Value |
|-------|--------|
| Dashboard | https://supabase.com/dashboard/project/ucvwtoziiqgmcyzxkwxe |
| Project ref | `ucvwtoziiqgmcyzxkwxe` |
| Direct host | `db.ucvwtoziiqgmcyzxkwxe.supabase.co:5432` |
| DB name | `postgres` |
| DB user (direct) | `postgres` |

**Password:** not stored in git. Use the Database password from Project Settings → Database (reset if lost). URL-encode special characters (`@`, `#`, `%`, etc.).

### Exact URI templates (password placeholder only)

Direct (recommended for Alembic + app):

```text
postgresql://postgres:[YOUR-PASSWORD]@db.ucvwtoziiqgmcyzxkwxe.supabase.co:5432/postgres
```

App / SQLAlchemy form (always add SSL):

```text
postgresql+psycopg2://postgres:[YOUR-PASSWORD]@db.ucvwtoziiqgmcyzxkwxe.supabase.co:5432/postgres?sslmode=require
```

Session pooler (also fine for Alembic; replace `<REGION>` e.g. `ap-south-1`):

```text
postgresql+psycopg2://postgres.ucvwtoziiqgmcyzxkwxe:[YOUR-PASSWORD]@aws-0-<REGION>.pooler.supabase.com:5432/postgres?sslmode=require
```

Transaction pooler (port **6543**): app-only — **avoid for Alembic**.

**Do not commit** the real URL or password. Store in SSM (below) or EC2 `application.env` only.

---

## Current architecture (verified 2026-07-10)

| Fact | Detail |
|------|--------|
| Prod DB | Docker `postgres:16-alpine` on EC2 `i-0426cdc00ff15bfe9` (`infra-postgres-1`, volume `infra_pgdata`) |
| `DATABASE_URL` on EC2 | `postgresql+psycopg2://krishi:***@postgres:5432/krishifarms` |
| Aurora | **None** |
| RDS in account | `gamya-couture-dev-pg` (Gamya Terraform) — remove via [GAMYA_RDS_REMOVAL.md](./GAMYA_RDS_REMOVAL.md) |
| SSM DB secret | `/krishifarms/dev/db/password` → builds Docker `DATABASE_URL` |
| SSM override (this cutover) | `/krishifarms/dev/db/database_url` → full Supabase URL when set (structure via `ensure-ssm-parameters.sh`; real value via `put-supabase-database-url-ssm.sh`) |
| Extensions needed | `pgcrypto`, `pg_trgm` (Alembic `create_extensions()`) — both available on Supabase |
| Partitions | Native monthly `RANGE` partitions — supported on Supabase Postgres |
| Docker data | Often empty / re-seedable — prefer **fresh Alembic + seed** unless you confirm real data to keep |

---

## Cutover checklist

### 1. Prerequisites

- [x] Supabase project created — ref `ucvwtoziiqgmcyzxkwxe`
- [ ] This branch merged to `main` (Compose no longer hardcodes Docker `DATABASE_URL`; SSM sync supports full URL)
- [ ] Database **password** in SSM `/krishifarms/dev/db/database_url` (not `REPLACE_ME`) — **required before GitHub deploy will pass health check**
- [ ] Confirm **fresh Alembic + seed** (recommended) vs dump/restore from Docker

### 2. Put URL in AWS SSM (automated on deploy)

**Preferred:** add GitHub secret **`SUPABASE_DB_PASSWORD`** (repo → Settings → Secrets → Actions). Each push to `main` runs `github-predeploy.sh` which:

1. Ensures SSM keys exist (`ensure-ssm-parameters.sh`)
2. Writes `/krishifarms/dev/db/database_url` with `sslmode=require`
3. Configures EC2-only cost scheduler (drops RDS from daily cron)

**Manual fallback** (local machine with AWS CLI):

```bash
SUPABASE_DB_PASSWORD='...' bash deploy/scripts/put-supabase-database-url-ssm.sh
```

When `/krishifarms/dev/db/database_url` is set, `sync-env-from-ssm.sh` uses it and **does not** overwrite with the Docker Postgres URL.

Keep `/krishifarms/dev/db/password` for rollback to local Docker if needed.

### 3. Schema + seed on Supabase (before or during cutover)

From a machine that can reach Supabase (laptop or EC2):

```bash
export DATABASE_URL='postgresql+psycopg2://postgres:[YOUR-PASSWORD]@db.ucvwtoziiqgmcyzxkwxe.supabase.co:5432/postgres?sslmode=require'
# From repo root with venv / or inside a one-off api container with that env:
alembic upgrade head
python scripts/seed.py
```

Confirm extensions: `pgcrypto`, `pg_trgm` (created by migrations).

**Recommendation:** use fresh Alembic + seed. Recent Docker Postgres on prod had empty/missing users; dump/restore is only needed if you confirm real data to keep.

### 4. Optional: copy data from Docker Postgres

Only if you have real data to keep:

```bash
# On EC2 — dump from local Docker
docker compose -f /opt/krishifarms/repo/infra/docker-compose.prod.yml \
  exec -T postgres pg_dump -U krishi -d krishifarms --no-owner --no-acl > /tmp/krishi.dump.sql

# Restore into Supabase (psql with SSL)
psql "postgresql://postgres:[YOUR-PASSWORD]@db.ucvwtoziiqgmcyzxkwxe.supabase.co:5432/postgres?sslmode=require" \
  -f /tmp/krishi.dump.sql
# Prefer schema via Alembic first, then data-only dump, to avoid extension/owner conflicts.
```

If empty: skip dump; Alembic + seed is enough.

### 5. Point EC2 at Supabase

```bash
# Session Manager on i-0426cdc00ff15bfe9
sudo APP_PATH=/opt/krishifarms bash /opt/krishifarms/scripts/sync-env-from-ssm.sh
# Or edit manually:
sudo nano /opt/krishifarms/config/application.env
# Set DATABASE_URL=...sslmode=require

cd /opt/krishifarms/repo
sudo cp /opt/krishifarms/config/application.env .env
sudo docker compose -f infra/docker-compose.prod.yml up -d --build
sudo docker compose -f infra/docker-compose.prod.yml exec -T api alembic upgrade head
# Optional seed if not done in step 3:
# sudo docker compose -f infra/docker-compose.prod.yml exec -T api python scripts/seed.py
```

### 6. Verify

```bash
curl -sf http://127.0.0.1:8082/api/v1/health
# Login: owner@krishifarms.local / ChangeMe123! (or your seeded owner)
```

### 7. EC2 start/stop cron — keep EC2, drop RDS

Daily EventBridge Scheduler jobs (06:00 / 11:00 IST) should **still start/stop EC2** `i-0426cdc00ff15bfe9` but **not** RDS `gamya-couture-dev-pg` after Supabase cutover:

```bash
bash deploy/scripts/configure-compute-scheduler-ec2-only.sh
# Preview: bash deploy/scripts/configure-compute-scheduler-ec2-only.sh --dry-run
```

This removes `DB_INSTANCE_IDENTIFIER` from Lambda `gamya-couture-dev-cost-scheduler` and deletes the disabled orphan `shutdown-ec2` schedule.

### 8. Optional cleanup (Docker Postgres on EC2)

```bash
# Free RAM on t3.small — local DB unused after cutover
sudo docker compose -f infra/docker-compose.prod.yml stop postgres
# Keep volume `infra_pgdata` until you are sure you will not roll back
```

### 9. Rollback

1. Remove or empty SSM `/krishifarms/dev/db/database_url` (or unset `DATABASE_URL` override)
2. Re-run `sync-env-from-ssm.sh` so Docker URL is rebuilt from `/krishifarms/dev/db/password`
3. `docker compose ... start postgres && up -d` and verify health

---

## Blockers / ask the user

Still needed before anyone can finish cutover on EC2/SSM:

1. Database **password** — paste here, **or** confirm you will run the `aws ssm put-parameter` command yourself
2. Confirm **fresh Alembic + seed** (recommended) vs migrate existing Docker data
