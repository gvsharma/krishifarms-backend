# AGENTS.md — KrishiFarms CRM

Context file for AI coding agents (Cursor, Copilot, Claude Code, etc.). Read this before making changes.

---

## 1. Project Purpose

**KrishiFarms CRM** is a backend API for Indian farm operations management:

- **Procurement** — buy paddy/corn from farmers (weighment, moisture, deductions)
- **Farmer ledger** — immutable credit/debit ledger, outstanding balances, payments
- **Workforce** — workers, attendance, work orders, labor costs
- **Fleet & assets** — tractors, DCM trailers, balers; vehicle trips and usage logs
- **Rentals** — equipment rental agreements and collections
- **Finance** — expenses, collections, payments, financial transactions
- **Documents** — S3-backed bills, receipts, photos with entity linking and OCR (planned)

**Reference domain:** Bhairkhanpally village, Telangana; crops Paddy and Corn; INR currency; bilingual English/Telugu.

---

## 2. Critical State: Schema vs Implementation

Do not assume OpenAPI paths are implemented in Python.

| Layer | Location | Status |
|-------|----------|--------|
| **Live Python routes** | `app/main.py` imports | Phase 1 only (see §4) |
| **Full DB schema** | `alembic/versions/202506210001`–`015` | ✅ All domain tables |
| **Full API contract** | `docs/api/openapi.yaml` + paths | ✅ Spec complete; many endpoints pending code |
| **SQLAlchemy models** | `app/modules/*/models.py` | Partial — only Phase 1 modules have models |
| **Reporting queries** | `docs/reporting/sql/*.sql` | ✅ Ready against schema |
| **Frontend** | `frontend/` | Placeholder config only |
| **Tests** | — | No `tests/` directory yet |

When adding a Phase 2+ feature: check migration for table shape → add model to module → register in `app/models.py` → implement service/router → align with OpenAPI path in `docs/api/paths/`.

---

## 3. How to Navigate the Codebase

```text
Task                          → Start here
────────────────────────────────────────────────────────────
Add/modify endpoint           → app/modules/<module>/router.py
Business logic                → app/modules/<module>/service.py
Request/response shapes       → app/modules/<module>/schemas.py
SQLAlchemy models             → app/modules/<module>/models.py
Register new model for Alembic→ app/models.py (import it)
Auth / permissions            → app/core/dependencies.py, app/shared/permissions.py
Shared response envelope      → app/shared/schemas/common.py
S3 / audit helpers            → app/shared/services/
Config / env vars             → app/core/config.py, .env.example
DB migrations                 → alembic/versions/, migration_utils.py
API contract (source of truth)→ docs/api/openapi.yaml, docs/api/API_CONTRACT.md
RBAC permission seeds         → alembic/versions/202506210015_seed_permissions_and_roles.py
Dashboard/reporting SQL       → docs/reporting/sql/, docs/reporting/kpi_definitions.md
Document module design        → docs/modules/DOCUMENT_MANAGEMENT.md
Deploy / CI                   → docs/deploy/CI_CD.md, deploy/README.md
Seed data                     → scripts/seed.py, scripts/synthetic_seed/
```

**Module layout pattern:** Each domain module has `router.py` (thin), `service.py` (queries + rules), `schemas.py` (Pydantic), `models.py` (SQLAlchemy). Routers use `APIResponse[T]` wrapper and `require_permission("resource:action")`.

---

## 4. Module Map

### Phase 1 — Implemented (Python + routes mounted in `main.py`)

| Module | Path prefix | Permissions (subset) | Notes |
|--------|-------------|---------------------|-------|
| `auth` | `/auth` | Public login/refresh | JWT access + refresh tokens |
| `users` | `/users`, `/roles` | `users:*`, `roles:read` | Org-scoped users, RBAC roles |
| `master_data` | `/villages`, `/crop-types` | `villages:*`, `crop_types:*` | Soft-delete master data |
| `financial` | `/expense-categories` | `expense_categories:*` | Categories only; expenses table exists in DB but no route yet |
| `documents` | `/documents` | `documents:*` | Presign upload, register, list, download, link — see gaps in DOCUMENT_MANAGEMENT.md |
| `audit` | `/audit-logs`, `/activity-feed` | `audit:read` | Immutable audit trail |
| `dashboard` | `/dashboard/summary`, `/health` | `dashboard:read` | Summary stub + health check |

### Phase 2+ — Schema + OpenAPI only (no Python module yet)

| Domain | DB migration | OpenAPI paths | Planned module dir |
|--------|--------------|---------------|------------------|
| Farmers | `202506210004` | `paths/farmers.yaml` | `app/modules/farmers/` |
| Farms | `202506210006` | `paths/farms.yaml` | `app/modules/farms/` |
| Procurements & farmer payments | `202506210008` | `paths/procurement.yaml`, `paths/payments.yaml` | `app/modules/procurement/` |
| Workers & work orders | `202506210005`, `009` | `paths/workers.yaml`, `work-orders.yaml` | `app/modules/workforce/` |
| Assets & vehicle trips | `202506210010` | `paths/assets.yaml`, `vehicles.yaml` | `app/modules/assets/` |
| Rentals | `202506210011` | `paths/rentals.yaml` | `app/modules/rentals/` |
| Expenses, collections, payments | `202506210012` | `paths/expenses.yaml`, `collections.yaml` | extend `financial/` |
| AI / OCR | `202506210014` | stubs in documents | extend `documents/` |
| Global search | — | `paths/search.yaml` | `app/modules/search/` |

Full permission list (including Phase 2+) is seeded in migration `202506210015`. Phase 1 Python seed in `app/shared/permissions.py` covers a smaller subset — extend it when adding routes.

---

## 5. Coding Conventions

### API design (OpenAPI-first)

1. Update or verify `docs/api/paths/<module>.yaml` and schemas before implementing.
2. All routes live under `/api/v1` (mounted sub-app in `app/main.py`).
3. Wrap responses in `APIResponse(data=...)` from `app/shared/schemas/common.py`.
4. Use `AppError` subclasses (`NotFoundError`, `ForbiddenError`, `ConflictError`) — handled by exception handlers in `main.py`.
5. Paginate list endpoints: `page`, `page_size` (max 100), return `PaginatedResponse`.
6. Financial POST endpoints should accept `Idempotency-Key` header (when implemented).
7. Support `Accept-Language: en|te` for bilingual fields where applicable.

### Multi-tenancy

```python
# Always scope queries by org from JWT — never from request body
service.list_villages(db, ctx.user.org_id, page, page_size)
```

Pass `ctx.user.id` as `created_by` / `updated_by` on writes.

### Soft delete

Set `deleted_at = now()` and `updated_by`; do not hard-delete rows with `audit_columns()`. Filter `deleted_at IS NULL` in all reads.

### Money and types

- DB: `NUMERIC(14, 2)` for amounts
- Python: use `Decimal` in business logic where precision matters
- Never use `float` for money

### Module boilerplate for new endpoints

```python
@router.get("/resource", response_model=APIResponse[ResourceListResponse])
def list_resources(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    ctx: CurrentUserContext = Depends(require_permission("resource:read")),
    db: Session = Depends(get_db),
):
    items, total = service.list_resources(db, ctx.user.org_id, page, page_size)
    return APIResponse(data=ResourceListResponse(...))
```

---

## 6. Database Rules

### Migration naming

Format: `YYYYMMDDHHMM_description.py` (e.g. `202506210008_procurements_and_payments.py`).

### Use shared helpers (`migration_utils.py`)

| Helper | Purpose |
|--------|---------|
| `audit_columns()` | `created_by`, `updated_by`, `deleted_at`, timestamps |
| `org_fk()` | FK to `organizations.id` |
| `create_monthly_partitions(table, column, year)` | Monthly range partitions |
| `create_extensions()` | `pgcrypto`, `pg_trgm` |

### Partitioned tables (require date in PK lookups)

`procurements`, `farmer_ledger_entries`, `farmer_payments`, `attendance_records`, `vehicle_trips`, `asset_usage_logs`, `expenses`, `collections`, `payments`, `financial_transactions`, `farm_activities`, and others.

When fetching by ID, also pass the partition date query param (see API_CONTRACT.md §6).

Create new year partitions in migrations when extending beyond seeded years.

### Immutable ledger

`farmer_ledger_entries` has trigger `prevent_ledger_mutation` — **never UPDATE or DELETE**. Corrections use reversing entries.

### Register models for Alembic

Import every new model in `app/models.py` so autogenerate sees metadata.

### After schema change

```bash
alembic upgrade head
# Update docs/reporting if fact tables changed
```

---

## 7. What NOT To Do

| Don't | Why |
|-------|-----|
| Commit `.env`, `application.env`, AWS keys, `SECRET_KEY` | Secrets |
| Hard-delete ledger rows | Immutable by design |
| Hard-delete soft-deletable entities | Use `deleted_at` |
| Accept `org_id` from client without JWT cross-check | Tenant isolation |
| Use float for money | Precision loss |
| Skip `org_id` filter in SQL/reporting | Data leak across tenants |
| Implement endpoints without checking OpenAPI spec | Contract drift |
| Modify `farmer_ledger_entries` directly | Use service layer + ledger entry pattern |
| Load synthetic seed in production without purge plan | Demo data contamination |
| Force-push to `main` | Production deploys on merge |

---

## 8. Common Agent Tasks

### Add a new API endpoint (existing module)

1. Read `docs/api/paths/<module>.yaml` for contract.
2. Add schema in `schemas.py`, logic in `service.py`, route in `router.py`.
3. Ensure permission exists in migration `015` and `require_permission()` matches.
4. Scope all queries by `ctx.user.org_id`.
5. Run `ruff check app`.

### Add a new domain module (Phase 2+)

1. Read relevant migration(s) in `alembic/versions/` for table columns and constraints.
2. Create `app/modules/<name>/` with models, schemas, service, router.
3. Import models in `app/models.py`.
4. Mount router in `app/main.py`.
5. Add permissions to `app/shared/permissions.py` if needed for seed.py roles.
6. Align with OpenAPI; bundle spec if testing in Postman.

### Add an Alembic migration

1. `alembic revision -m "short_description"`
2. Rename file to `YYYYMMDDHHMM_description.py` if needed.
3. Use `migration_utils` helpers; set `down_revision` chain correctly.
4. For partitioned tables, call `create_monthly_partitions`.
5. Test: `alembic upgrade head` and `alembic downgrade -1`.

### Add a dashboard / reporting query

1. Read `docs/reporting/REPORTING_ARCHITECTURE.md` and `kpi_definitions.md`.
2. Add SQL to `docs/reporting/sql/` with `:org_id`, `:date_from`, `:date_to` params.
3. Filter `deleted_at IS NULL` where applicable.
4. Use partition date columns for range filters (partition pruning).

### Extend document management

Read `docs/modules/DOCUMENT_MANAGEMENT.md` §2 for implemented vs gap list. S3 keys: `app/shared/services/s3.py`. Presign → PUT → register pattern.

### Run locally

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up -d --build
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
docker compose -f infra/docker-compose.yml exec api python scripts/seed.py
```

Login: `owner@krishifarms.local` / `ChangeMe123!`

---

## 9. Environment Variables (names only)

Set in `.env` (local) or `/opt/krishifarms/config/application.env` (production). See `.env.example` and `deploy/env/application.env.example`.

| Variable | Purpose |
|----------|---------|
| `APP_NAME` | Display name |
| `APP_ENV` | Environment label |
| `DEBUG` | Swagger + verbose errors |
| `SECRET_KEY` | JWT signing |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL |
| `DATABASE_URL` | PostgreSQL connection string |
| `CACHE_PROVIDER` | `none` / `memory` / `redis` |
| `CACHE_TTL_SECONDS` | Permission cache TTL |
| `REDIS_URL` | Redis connection (if redis provider) |
| `AWS_REGION` | S3 region |
| `AWS_ACCESS_KEY_ID` | Optional (use IAM role on EC2) |
| `AWS_SECRET_ACCESS_KEY` | Optional |
| `S3_BUCKET_NAME` | Document bucket |
| `S3_PRESIGNED_URL_EXPIRE_SECONDS` | Presign TTL |
| `CORS_ORIGINS` | Comma-separated allowed origins |
| `DEFAULT_ORG_NAME` | Seed org name |
| `DEFAULT_OWNER_EMAIL` | Seed owner email |
| `DEFAULT_OWNER_PASSWORD` | Seed owner password |
| `DEFAULT_OWNER_NAME` | Seed owner display name |

Production also uses `POSTGRES_PASSWORD` (see `deploy/env/application.env.example`).

---

## 10. Testing & CI

| Check | Command / location |
|-------|-------------------|
| Lint | `ruff check app` |
| Import sanity | `python -c "from app.main import app"` |
| Docker build | `docker build -t krishifarms-backend:ci .` |
| CI | `.github/workflows/ci.yml` → `validate.yml` |
| Post-deploy smoke | `scripts/smoke-test-api.sh` |
| Unit tests | **Not set up yet** — add `tests/` with pytest when implementing |

---

## 11. Deployment Pointers

- **Branch:** `main` auto-deploys to EC2 on push (after validation).
- **Flow:** GitHub Actions → S3 artifact → SSM Run Command → `deploy/scripts/remote-deploy.sh`.
- **Health check:** `GET /api/v1/health`
- **Frontend (future):** Vercel proxies `/api/v1` to EC2; set `CORS_ORIGINS` accordingly.
- **Rollback:** Automatic on failed health check; manual via backup tarball in `/opt/krishifarms/backup/`.

Details: [docs/deploy/CI_CD.md](./docs/deploy/CI_CD.md), [deploy/README.md](./deploy/README.md).

---

## 12. Cursor / IDE Notes

- `.cursor/settings.json` enables Postman plugin — OpenAPI spec at `docs/api/openapi.yaml`.
- No `.cursor/rules/` directory yet; this file (`AGENTS.md`) is the agent context source. Reference it from prompts: *"Follow AGENTS.md conventions."*
- Bundle OpenAPI for Postman: `npx @redocly/cli bundle docs/api/openapi.yaml -o docs/api/openapi.bundled.yaml`

---

## 13. Quick Reference Links

| Resource | Path |
|----------|------|
| Human README | [README.md](./README.md) |
| API contract | [docs/api/API_CONTRACT.md](./docs/api/API_CONTRACT.md) |
| OpenAPI entry | [docs/api/openapi.yaml](./docs/api/openapi.yaml) |
| Reporting | [docs/reporting/REPORTING_ARCHITECTURE.md](./docs/reporting/REPORTING_ARCHITECTURE.md) |
| Documents | [docs/modules/DOCUMENT_MANAGEMENT.md](./docs/modules/DOCUMENT_MANAGEMENT.md) |
| Synthetic seed | [scripts/synthetic_seed/README.md](./scripts/synthetic_seed/README.md) |
| CI/CD | [docs/deploy/CI_CD.md](./docs/deploy/CI_CD.md) |
