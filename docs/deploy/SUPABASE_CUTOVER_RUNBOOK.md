# Supabase cutover — complete these steps once

Production is still on **Docker Postgres** until all three steps below succeed and deploy goes green.

## Step 1 — GitHub secret (krishifarms-backend)

**Repo:** [gvsharma/krishifarms-backend](https://github.com/gvsharma/krishifarms-backend)  
**Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|------|--------|
| `SUPABASE_DB_PASSWORD` | Supabase project `ucvwtoziiqgmcyzxkwxe` database password |

Use the **raw database password** from Dashboard → Project Settings → Database — not API keys, not a URL-encoded copy. Pre-deploy verifies the password against the pooler before writing SSM; deploy fails early with a clear error if auth fails.

Deploy will **fail fast** with a clear error if this secret is missing.

**Optional (Terraform):** add the same secret on `gvsharma/krishifarms-infra` and apply the IAM patch — Terraform can sync it to the backend repo automatically.

## Step 2 — IAM on deploy role (one-time, admin AWS)

The GitHub OIDC role must write SSM and optionally update the shared cost Lambda.

**Role:** `krishifarms-dev-gh-be-deploy-20260621161619959700000003`  
**Account:** `085863558134` · **Region:** `ap-south-1`

### Option A — script (fastest)

```bash
cd krishifarms-backend
bash deploy/scripts/attach-github-deploy-iam-supabase-policy.sh
```

Uses policy file `deploy/iam/github-backend-deploy-ssm-supabase.json`.

### Option B — Terraform (durable)

```bash
git clone https://github.com/gvsharma/krishifarms-infra.git
cd krishifarms-infra
git apply /path/to/krishifarms-backend/patches/krishifarms-infra-deploy-iam-supabase.patch
# Add SUPABASE_DB_PASSWORD secret on krishifarms-infra repo, then:
git push && merge → Terraform apply on main
```

## Step 3 — Deploy

After steps 1–2:

1. Merge [PR #27](https://github.com/gvsharma/krishifarms-backend/pull/27) (or latest Supabase cutover PR) to `main`, **or**
2. **Actions → Deploy Backend to EC2 → Run workflow** (`workflow_dispatch`)

### What deploy does

1. `github-predeploy.sh` writes `/krishifarms/dev/db/database_url` (Supabase + `sslmode=require`)
2. EC2 kickoff runs `sync-env-from-ssm.sh` → updates `application.env`
3. `alembic upgrade head` + `seed.py` against Supabase
4. Health check `http://13.232.200.243:8082/api/v1/health`

## Verify cutover

```bash
# EC2 (Session Manager) — host must be supabase.co, not postgres:
sudo grep DATABASE_URL /opt/krishifarms/config/application.env

# Public health
curl -sf https://krishifarms-backend.vercel.app/api/v1/health
```

Supabase dashboard → Table Editor → confirm `users`, `organizations`, etc. exist after seed.

## Rollback

1. Remove or empty SSM `/krishifarms/dev/db/database_url`
2. Ensure `/krishifarms/dev/db/password` has Docker Postgres password
3. Re-deploy — `sync-env-from-ssm.sh` rebuilds `postgresql+psycopg2://krishi:...@postgres:5432/krishifarms`

See [SUPABASE_MIGRATION.md](./SUPABASE_MIGRATION.md) for full detail.
