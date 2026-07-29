# AGENTS.md — KrishiFarms CRM

**Quick entry for AI coding agents.** For comprehensive reference, see **[docs/AGENT_GUIDE.md](./docs/AGENT_GUIDE.md)**.

---

## What This Is

Backend API for Indian farm operations: procurement, farmer ledger, workforce, fleet, rentals, finance, documents. Domain: Bhairkhanpally (Telangana), Paddy/Corn, INR, bilingual EN/TE.

**Critical:** Full DB schema + OpenAPI exist for Phases 1–5. **Python routes through Phase 2b** (farmers, procurements, platform admin). Check [implementation matrix](./docs/AGENT_GUIDE.md#3-implementation-status-matrix) before assuming an endpoint exists.

---

## Read Order

1. This file (5 min)
2. [docs/AGENT_GUIDE.md](./docs/AGENT_GUIDE.md) — status matrix + relevant playbook
3. Module doc / migration / OpenAPI path for your task

| Doc | Purpose |
|-----|---------|
| [docs/APP_INVENTORY.md](./docs/APP_INVENTORY.md) | Features, live APIs, DB tables — single inventory |
| [docs/AGENT_GUIDE.md](./docs/AGENT_GUIDE.md) | Master agent reference |
| [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | System topology, AWS, data flow |
| [docs/CHANGELOG.md](./docs/CHANGELOG.md) | What changed (update on every change) |
| [docs/api/API_CONTRACT.md](./docs/api/API_CONTRACT.md) | REST standards, endpoints |
| [docs/modules/DOCUMENT_MANAGEMENT.md](./docs/modules/DOCUMENT_MANAGEMENT.md) | Documents design |
| [docs/reporting/REPORTING_ARCHITECTURE.md](./docs/reporting/REPORTING_ARCHITECTURE.md) | Dashboard SQL |
| [docs/deploy/CI_CD.md](./docs/deploy/CI_CD.md) | CI/CD pipeline |
| [docs/deploy/SUPABASE_MIGRATION.md](./docs/deploy/SUPABASE_MIGRATION.md) | Cutover Docker Postgres → Supabase |
| [docs/DEMO_DATA.md](./docs/DEMO_DATA.md) | Temporary demo seed/purge for live modules (Android + CRM) |
| [docs/ui/README.md](./docs/ui/README.md) | Next.js UI/UX design system (IA, tokens, components, wireframes) |

---

## Navigate the Codebase

```text
Add/modify endpoint     → app/modules/<module>/router.py
Business logic          → app/modules/<module>/service.py
Schemas                 → app/modules/<module>/schemas.py
Models                  → app/modules/<module>/models.py
Register model          → app/models.py
Auth / permissions      → app/core/dependencies.py, app/shared/permissions.py
API contract            → docs/api/openapi.yaml, docs/api/paths/
Migrations              → alembic/versions/, migration_utils.py
Mount routers           → app/main.py
```

**Pattern:** `router` (thin) → `service` (org-scoped queries) → `APIResponse[T]` + `require_permission("resource:action")`.

---

## Phase 1 — Live in Python

| Module | Prefix |
|--------|--------|
| auth | `/auth` |
| users | `/users`, `/roles` |
| master_data | `/villages` (+ search, **profile-360**), `/crop-types`, districts/mandals |
| financial | `/expense-categories` |
| documents | `/documents` (partial — see DOCUMENT_MANAGEMENT.md) |
| audit | `/audit-logs`, `/activity-feed` |
| dashboard | `/dashboard/summary`, `/health` |
| platform | `/buyers`, `/field-agents`, comments, tags, price rules |
| farmers | `/farmers` (+ bank accounts, land parcels, outstanding, **profile-360**, crop-history, ledger) |
| procurements | `/procurements` (full workflow) |

Phase 2+ remaining (workforce, rentals, general payments): schema + OpenAPI ready; expenses/collections live — see [AGENT_GUIDE §11](./docs/AGENT_GUIDE.md#11-common-agent-workflows).

---

## Frontend (Phase 1 shell)

**Next.js 15** on Vercel — `frontend/` has app shell, CEO dashboard, and nav placeholders (Dribbble-inspired). UI/UX specs: [docs/ui/](./docs/ui/) · architecture: [FRONTEND_ARCHITECTURE.md](./docs/ui/FRONTEND_ARCHITECTURE.md). Stack: App Router, TypeScript, Tailwind, shadcn-style components, TanStack Query, Zustand, next-themes.

```bash
cd frontend && npm install && npm run dev
```

---

## Key Conventions

| Rule | Detail |
|------|--------|
| Multi-tenancy | `org_id` from JWT only — never trust client body |
| Money | `NUMERIC(14,2)` / `Decimal` — never `float` |
| Soft delete | `deleted_at`; filter `IS NULL` in reads |
| Ledger | `farmer_ledger_entries` immutable — reversing entries only |
| Partitions | Monthly on date keys; ID lookups need partition date |
| OpenAPI-first | Update spec before implementing endpoints |
| Responses | `APIResponse` envelope from `app/shared/schemas/common.py` |

---

## Quick Commands

```bash
cp .env.example .env
docker compose -f infra/docker-compose.yml up -d --build
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
docker compose -f infra/docker-compose.yml exec api python scripts/seed.py
ruff check app
```

Login: `owner@krishifarms.local` / `ChangeMe123!`

---

## What NOT To Do

- Commit secrets (`.env`, `application.env`, `SECRET_KEY`)
- Hard-delete ledger or soft-deletable rows
- Skip `org_id` filter in queries/reporting
- Implement without checking OpenAPI + migration
- Force-push `main` (auto-deploys to EC2)

Full list: [AGENT_GUIDE §15](./docs/AGENT_GUIDE.md#15-anti-patterns-and-gotchas).

---

## Doc Maintenance

**On every code/config change:** update [docs/CHANGELOG.md](./docs/CHANGELOG.md) and any affected docs. Cursor rule `.cursor/rules/maintain-agent-docs.mdc` enforces this. See [AGENT_GUIDE §12](./docs/AGENT_GUIDE.md#12-documentation-maintenance).

---

## Cursor / IDE

- Rules auto-load from `.cursor/rules/`
- OpenAPI: `docs/api/openapi.yaml` (Postman plugin in `.cursor/settings.json`)
- Bundle spec: `npx @redocly/cli bundle docs/api/openapi.yaml -o docs/api/openapi.bundled.yaml`

---

## Cursor Cloud specific instructions

The cloud VM runs the stack **natively (no Docker)** — Docker is not installed. The startup update script only refreshes deps: it creates `.venv` and runs `pip install -e ".[dev,redis]"`, plus `npm --prefix frontend install`. Everything below (Postgres + services) must be started manually; it is **not** in the update script.

**Services & how to run them (three long-running processes, use tmux):**

| Service | Start command | Port |
|---------|---------------|------|
| PostgreSQL 16 | `sudo pg_ctlcluster 16 main start` | 5432 |
| Backend API | `source .venv/bin/activate && PYTHONPATH=/workspace uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` | 8000 |
| Frontend | `npm --prefix frontend run dev` | 3000 |

**Non-obvious caveats:**

- **DB connection:** local Postgres uses role/pw/db `krishi` / `krishi` / `krishifarms`. Set `.env` `DATABASE_URL=postgresql+psycopg2://krishi:krishi@localhost:5432/krishifarms` (the `.env.example` default points at host `postgres`, which only resolves inside Docker Compose). Copy `.env.example` → `.env` and also set a non-placeholder `SECRET_KEY`.
- **`PYTHONPATH=/workspace` is required** to run `uvicorn`, `scripts/*.py`, and `pytest` (the `scripts` package and top-level imports are not installed on the path).
- **Migrations:** `alembic upgrade head` (loads `.env` via `alembic/env.py`).
- **Seeding gotcha:** `python scripts/seed.py` **fails on a fresh DB** with `UniqueViolation: permissions_code_key` — migration `015` (and later) already seed the `permissions` rows (`ON CONFLICT`), but `seed.py` re-inserts them with a plain ORM insert. To seed, create the org/roles/owner while **linking roles to the already-present permissions** instead of inserting them (query existing `Permission` rows into the role map; also `import app.models` first so FK targets like `field_agents` are registered in metadata). Once seeded, the data persists in the VM snapshot, so re-seeding is usually unnecessary.
- **Frontend → API wiring:** nginx is not needed. `frontend/.env.local` sets `NEXT_PUBLIC_API_BASE_URL=/api/v1` and `API_PROXY_TARGET=http://localhost:8000`, so the browser hits same-origin `:3000/api/v1` which Next rewrites to the API (no CORS).
- **Login:** `owner@krishifarms.local` / `ChangeMe123!`.
- **Tests:** `PYTHONPATH=/workspace pytest`. Two tests currently fail independent of setup — `tests/test_farmers_rbac.py::test_farmer_role_is_read_only` and `tests/test_platform_admin.py::test_manager_backend_cannot_create_or_delete_users` — because `app/shared/permissions.py` now grants `comments:create` (FARMER) and `users:create` (MANAGER) while those assertions still expect the old read-only sets.
- **Lint:** `ruff check app`.
