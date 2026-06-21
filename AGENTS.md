# AGENTS.md — KrishiFarms CRM

**Quick entry for AI coding agents.** For comprehensive reference, see **[docs/AGENT_GUIDE.md](./docs/AGENT_GUIDE.md)**.

---

## What This Is

Backend API for Indian farm operations: procurement, farmer ledger, workforce, fleet, rentals, finance, documents. Domain: Bhairkhanpally (Telangana), Paddy/Corn, INR, bilingual EN/TE.

**Critical:** Full DB schema + OpenAPI exist for Phases 1–5. **Python routes are Phase 1 only.** Check [implementation matrix](./docs/AGENT_GUIDE.md#3-implementation-status-matrix) before assuming an endpoint exists.

---

## Read Order

1. This file (5 min)
2. [docs/AGENT_GUIDE.md](./docs/AGENT_GUIDE.md) — status matrix + relevant playbook
3. Module doc / migration / OpenAPI path for your task

| Doc | Purpose |
|-----|---------|
| [docs/AGENT_GUIDE.md](./docs/AGENT_GUIDE.md) | Master agent reference |
| [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | System topology, AWS, data flow |
| [docs/CHANGELOG.md](./docs/CHANGELOG.md) | What changed (update on every change) |
| [docs/api/API_CONTRACT.md](./docs/api/API_CONTRACT.md) | REST standards, endpoints |
| [docs/modules/DOCUMENT_MANAGEMENT.md](./docs/modules/DOCUMENT_MANAGEMENT.md) | Documents design |
| [docs/reporting/REPORTING_ARCHITECTURE.md](./docs/reporting/REPORTING_ARCHITECTURE.md) | Dashboard SQL |
| [docs/deploy/CI_CD.md](./docs/deploy/CI_CD.md) | CI/CD pipeline |
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
| master_data | `/villages`, `/crop-types` |
| financial | `/expense-categories` |
| documents | `/documents` (partial — see DOCUMENT_MANAGEMENT.md) |
| audit | `/audit-logs`, `/activity-feed` |
| dashboard | `/dashboard/summary`, `/health` |

Phase 2+ (farmers, procurement, workforce, assets, rentals, expenses): schema + OpenAPI ready; implement per [AGENT_GUIDE §11](./docs/AGENT_GUIDE.md#11-common-agent-workflows).

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
