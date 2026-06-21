# KrishiFarms CRM

Farm procurement, logistics, workforce, rental, and financial management CRM for Indian farm operations.

**Domain context:** Operations centered on villages like Bhairkhanpally (Telangana), crops such as Paddy and Corn, bilingual English/Telugu UI, INR money, and org-scoped multi-tenancy.

**Repository:** [gvsharma/krishifarms-backend](https://github.com/gvsharma/krishifarms-backend)  
**Agent context:** See [AGENTS.md](./AGENTS.md) for AI coding agent orientation.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12 |
| API | FastAPI, Uvicorn |
| Database | PostgreSQL 16, SQLAlchemy 2.x, Alembic |
| Auth | JWT (access + refresh), RBAC |
| Cache | Pluggable `CacheProvider` (none / memory / redis) |
| Documents | AWS S3 presigned upload/download (`ap-south-1`) |
| Infra | Docker Compose (local + EC2 production) |
| CI/CD | GitHub Actions → S3 → SSM → EC2 |
| Frontend | Next.js placeholder (`frontend/`) — not implemented yet |

---

## Implementation Status

| Area | Status |
|------|--------|
| **Phase 1 API** (live) | Auth, Users/Roles, Villages, Crop Types, Expense Categories, Documents (partial), Audit, Dashboard |
| **Database schema** | Full schema through Alembic `202506210015` (farmers, procurements, fleet, rentals, ledger, etc.) |
| **OpenAPI contract** | Full API spec in `docs/api/` — ahead of Python implementation |
| **Reporting SQL** | Parameterized dashboard queries in `docs/reporting/sql/` |
| **Synthetic seed** | Demo data loader for UAT (`scripts/synthetic_seed/`) |
| **Phase 2+ API** | Farmers, Procurement, Payments, Workforce, Assets, Rentals — schema ready, routes pending |

---

## Repository Structure

```text
app/
  main.py                 # FastAPI app; mounts /api/v1 sub-app
  models.py               # Alembic model registry (import all models here)
  core/
    config.py             # pydantic-settings from .env
    database.py           # SQLAlchemy engine + SessionLocal
    dependencies.py       # get_db, JWT auth, require_permission()
    security.py           # JWT + password hashing
    exceptions.py         # AppError hierarchy
    cache/                # CacheProvider abstraction (none/memory/redis)
  modules/                # Domain modules (router → service → models/schemas)
    auth/                 # Login, refresh, logout
    users/                # Users, roles, organizations
    master_data/          # Villages, crop types
    financial/            # Expense categories (Phase 1)
    documents/            # S3 presign, register, list, link
    audit/                # Audit logs, activity feed
    dashboard/            # Summary + /health
  shared/
    permissions.py        # SYSTEM_PERMISSIONS, ROLE_PERMISSIONS (Phase 1 subset)
    schemas/common.py     # APIResponse, PaginatedResponse
    services/s3.py        # S3 presigned URLs
    services/audit.py     # write_audit_log helper

alembic/
  versions/               # Migrations 202506210001–015
  env.py                  # Uses app.models.Base metadata

migration_utils.py        # Shared Alembic helpers (audit_columns, partitions)

docs/
  api/                    # OpenAPI spec + API_CONTRACT.md
  modules/                # DOCUMENT_MANAGEMENT.md
  reporting/              # REPORTING_ARCHITECTURE.md, kpi_definitions.md, sql/
  deploy/                 # CI_CD.md

infra/
  docker-compose.yml      # Local dev (postgres, api, nginx; optional redis profile)
  docker-compose.prod.yml # Production EC2 stack
  nginx/                  # Reverse proxy config
  scripts/backup.sh       # pg_dump cron helper

deploy/
  README.md               # EC2 bootstrap + deploy flow
  env/application.env.example
  scripts/                # ec2-bootstrap, remote-deploy, SSM kickoff

scripts/
  seed.py                 # Default org, roles, owner user, master data
  smoke-test-api.sh       # Post-deploy API smoke tests
  synthetic_seed/         # Synthetic demo data (see README inside)

frontend/                 # Vercel config placeholder (Next.js planned)

.github/workflows/
  ci.yml                  # PR + push to main → validate
  validate.yml            # Ruff, Docker build, Trivy, optional frontend
  deploy.yml              # Push to main → S3 + SSM deploy
```

---

## Quick Start (Local)

### Prerequisites

- Docker and Docker Compose
- Python 3.12 (optional, for running scripts outside Docker)

### 1. Configure environment

```bash
cp .env.example .env
# Edit SECRET_KEY and other values as needed
```

### 2. Start stack

```bash
docker compose -f infra/docker-compose.yml up -d --build
```

### 3. Run migrations and seed

```bash
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
docker compose -f infra/docker-compose.yml exec api python scripts/seed.py
```

### 4. Verify

| Endpoint | URL |
|----------|-----|
| Root | http://localhost:8000/ |
| API base | http://localhost:8000/api/v1 |
| Swagger (debug mode) | http://localhost:8000/api/v1/docs |
| Health | http://localhost:8000/api/v1/health |
| Nginx proxy | http://localhost:8080/api/v1 |

### 5. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@krishifarms.local","password":"ChangeMe123!"}'
```

### Default credentials (change immediately in production)

| Field | Value |
|-------|-------|
| Email | `owner@krishifarms.local` |
| Password | `ChangeMe123!` |
| Organization | Krishi Farms (`KRISHI`) |

Configurable via `DEFAULT_OWNER_EMAIL`, `DEFAULT_OWNER_PASSWORD`, `DEFAULT_ORG_NAME` in `.env`.

### Optional: synthetic demo data

See [scripts/synthetic_seed/README.md](./scripts/synthetic_seed/README.md) for Bhairkhanpally demo data (50 farmers, 200 procurements, etc.). **Purge before real production data.**

### Optional: Redis cache

```bash
pip install 'krishifarms-backend[redis]'
# In .env: CACHE_PROVIDER=redis, REDIS_URL=redis://redis:6379/0
docker compose -f infra/docker-compose.yml --profile redis up -d
```

---

## Key Conventions

These apply across schema, API, and reporting. Full detail in [AGENTS.md](./AGENTS.md) and [docs/api/API_CONTRACT.md](./docs/api/API_CONTRACT.md).

| Convention | Rule |
|------------|------|
| Multi-tenancy | Every business row has `org_id`; resolve from JWT, never trust client-supplied org |
| Primary keys | UUID (`gen_random_uuid()` / `pgcrypto`) |
| Money | `NUMERIC(14,2)` — never float |
| Weight | kg in DB; quintals in UI where noted |
| Soft delete | `deleted_at` via `audit_columns()`; filter `deleted_at IS NULL` in queries |
| Bilingual | Telugu columns (`*_te`) on farmers, workers, villages, assets, etc. |
| Partitioned tables | Monthly partitions on date keys (`procurement_date`, `payment_date`, etc.) |
| Immutable ledger | `farmer_ledger_entries` — trigger `prevent_ledger_mutation`; no UPDATE/DELETE |
| API envelope | `{ success, data, meta }` / `{ success: false, error: { message, details } }` |
| RBAC | Permission codes like `farmers:read`; enforce via `require_permission()` |

---

## Cache Provider

| Setting | Default | Description |
|---------|---------|-------------|
| `CACHE_PROVIDER` | `memory` | `none`, `memory`, or `redis` |
| `CACHE_TTL_SECONDS` | `300` | Permission cache TTL |
| `REDIS_URL` | empty | Required when `CACHE_PROVIDER=redis` |

---

## Documentation Index

| Document | Purpose |
|----------|---------|
| [AGENTS.md](./AGENTS.md) | AI agent coding guide (start here for Cursor/Copilot) |
| [docs/api/API_CONTRACT.md](./docs/api/API_CONTRACT.md) | REST standards, endpoint catalog, RBAC |
| [docs/api/openapi.yaml](./docs/api/openapi.yaml) | Modular OpenAPI 3.0 spec |
| [docs/modules/DOCUMENT_MANAGEMENT.md](./docs/modules/DOCUMENT_MANAGEMENT.md) | S3 storage, OCR, tagging, linking |
| [docs/reporting/REPORTING_ARCHITECTURE.md](./docs/reporting/REPORTING_ARCHITECTURE.md) | Dashboard SQL, partitions, KPIs |
| [docs/reporting/kpi_definitions.md](./docs/reporting/kpi_definitions.md) | KPI formulas per dashboard |
| [docs/deploy/CI_CD.md](./docs/deploy/CI_CD.md) | GitHub Actions, EC2, Vercel pairing |
| [deploy/README.md](./deploy/README.md) | EC2 bootstrap and rollback |
| [scripts/synthetic_seed/README.md](./scripts/synthetic_seed/README.md) | Demo data load/purge |
| [frontend/README.md](./frontend/README.md) | Planned Vercel/Next.js setup |

---

## Branch & Deployment

| Item | Value |
|------|-------|
| Production branch | `main` — merge triggers CI + deploy |
| Current dev branch | `cursor/phase-1-backend-foundation` |
| Deploy target | EC2 (`ap-south-1`) via S3 + SSM Run Command |
| Frontend (planned) | Vercel with `/api/v1` proxy to EC2 |

Merge to `main` runs validation (Ruff, Docker build, Trivy) then deploys to EC2. See [docs/deploy/CI_CD.md](./docs/deploy/CI_CD.md).

---

## Development Commands

```bash
# Lint
pip install ".[dev]"
ruff check app

# Migrations (inside api container or with DATABASE_URL set)
alembic upgrade head
alembic revision -m "description"   # follow YYYYMMDDHHMM naming

# Local without Docker
pip install -e .
uvicorn app.main:app --reload --port 8000
```

---

## EC2 Production Notes

- Single EC2 instance with `infra/docker-compose.prod.yml`
- PostgreSQL data on EBS (`pgdata` volume)
- Use IAM instance role for S3 (leave AWS keys empty in production `.env`)
- Set `DEBUG=false` and a strong `SECRET_KEY`
- Schedule `infra/scripts/backup.sh` for nightly `pg_dump`
- Runtime config: `/opt/krishifarms/config/application.env` (never commit)

---

## Roadmap (API modules)

- **Phase 1** ✅ Auth, Users, Master Data, Expense Categories, Documents (partial), Audit, Dashboard
- **Phase 2** Farmers, Procurement, Farmer Ledger/Payments
- **Phase 3** Expenses, Collections, General Payments
- **Phase 4** Farms, Workers, Work Orders, Attendance
- **Phase 5+** Fleet, Rentals, AI/OCR integrations, global search

Database migrations for Phases 2–5 tables already exist; Python routes follow in upcoming phases.
