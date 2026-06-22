# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- `.github/DEPLOY_CONFIG.md` — GitHub Actions secrets/variables from `krishifarms-infra` dev Terraform outputs
- Deploy workflow: `AWS_REGION`, `NGINX_LOCAL_PORT`, and `PUBLIC_HEALTH_CHECK_URL` vars for shared EC2 dev (port 8082)

### Changed

- Deploy workflow: optional `EC2_NAME_TAG` variable; auto-default `gamya-couture-dev-api` when `DEPLOY_BUCKET` contains `krishifarms` (shared Gamya EC2)
- `.github/DEPLOY_CONFIG.md`, `docs/deploy/CI_CD.md`, `deploy/README.md` — `EC2_INSTANCE_ID` and `EC2_HOST` **required** for shared Gamya EC2; shared-host section (port 8082, `/opt/krishifarms`)

### Fixed

- Deploy SSM: auto-create `application.env` from S3 template when bootstrap was skipped; `ssm-kickoff-deploy.sh` marks `deploy.status=failed` on early errors (no more zombie `running`); creates `krishifarms` service user if missing; workflow preflight checks Docker and clears stale deploy PID/status
- Deploy: revert SSM status poll to 36 attempts × 10s; upload `application.env.example` to S3 for kickoff
- Deploy: `infra/docker-compose.prod.yml` maps nginx to host port **8082** (`NGINX_HOST_PORT`, default 8082) on shared Gamya EC2
- Deploy: `remote-deploy.sh` on-host health check uses `http://127.0.0.1:8082/api/v1/health`

- Deploy: EC2 resolution no longer looks up non-existent `krishifarms-dev-api` tag when using shared Gamya host
- Deploy: write `deploy.tar.gz` under `$RUNNER_TEMP` before moving to workspace — GNU tar exits 1 (`file changed as we read it`) when the archive is created inside the tree being packed
- Frontend Vercel: `API_PROXY_TARGET` includes EC2 nginx port `:8082`; `NEXT_PUBLIC_SITE_URL` set to `https://krishifarms-backend.vercel.app`; env templates and `frontend/README.md` aligned
- CI: set dummy `SECRET_KEY` and `DATABASE_URL` in `validate.yml` backend job so import sanity check passes without a `.env` file
- CI: replace `hashFiles` in reusable `validate.yml` with a `detect` job output (GitHub forbids `hashFiles` in `workflow_call`)

### Added

- Auth: mobile login (`LoginRequest.mobile`), enriched `TokenResponse` (user, roles, permissions, accessibleModules), server-owned mobile RBAC catalog (`permission_catalog.py`, `rbac.py`); OpenAPI `auth.yaml` aligned
- Tests: `tests/test_auth_rbac.py` for login/RBAC payload behavior
- Frontend: `frontend/.gitignore` (exclude `node_modules/`, `.next/`, build artifacts)

- Frontend: App Router placeholder pages for all sidebar routes (`PlaceholderPage`); Vercel Next.js build via `npm ci`
- Frontend: Next.js 15 app shell in `frontend/` — Dribbble-inspired Farm Management SaaS UI (sidebar, header, CEO dashboard with 8 KPI cards, chart placeholders, nav placeholders); Plus Jakarta Sans + Noto Sans Telugu; light/dark themes; `package-lock.json` for CI
- Docs: Dribbble-inspired refinements in `docs/ui/DESIGN_SYSTEM.md` and `docs/ui/WIREFRAMES.md` (shell layout, typography, KPI cards)
- Docs: Flutter Web UI/UX design system under `docs/ui/` (IA, design tokens, components, wireframes, widget trees, Flutter architecture, screen specs, accessibility)
- Docs: migrate `docs/ui/` from Flutter Web to **Next.js only** — rename `FLUTTER_ARCHITECTURE.md` → `FRONTEND_ARCHITECTURE.md`, `WIDGET_TREE.md` → `COMPONENT_TREE.md`; update stack references (TanStack Query, Zustand, Tailwind, shadcn/ui); align with Gamya Couture + Vercel `frontend/` placeholder
- Docs: document PR-only branch strategy and merge-to-`main` deploy triggers ([CI_CD.md](./deploy/CI_CD.md), [AGENT_GUIDE.md](./AGENT_GUIDE.md), Cursor rules)
- Comprehensive agent documentation: [AGENT_GUIDE.md](./AGENT_GUIDE.md), [ARCHITECTURE.md](./ARCHITECTURE.md)
- Cursor rules for doc maintenance and project context (`.cursor/rules/`)
- Shortened [AGENTS.md](../AGENTS.md) as scannable entry point
- Frontend: Next.js app shell (sidebar, header, page layout), shadcn-style UI primitives, app providers, Zustand UI store, route constants, design tokens, TanStack Query client, KPI card and empty-state components

---

## [0.1.0] — 2025-06-21

Foundation release (`60bb2b5`). Phase 1 API live; full database schema and OpenAPI contract ahead of Python implementation for Phases 2+.

### Added

#### Phase 1 API (Python)

- **Auth** — JWT login, refresh, logout (`app/modules/auth/`)
- **Users & roles** — org-scoped users, RBAC (`app/modules/users/`)
- **Master data** — villages, crop types (`app/modules/master_data/`)
- **Financial** — expense categories only (`app/modules/financial/`)
- **Documents** — S3 presign upload/download, register, list, link (`app/modules/documents/`)
- **Audit** — audit logs, activity feed (`app/modules/audit/`)
- **Dashboard** — summary stub, health check (`app/modules/dashboard/`)

#### Database (Alembic `202506210001`–`015`)

| Revision | Domain |
|----------|--------|
| `001` | Platform baseline — orgs, IAM, master data, documents, audit |
| `002` | Extensions, Telugu columns, user scopes, triggers |
| `003` | Activity types, payment modes, number sequences |
| `004` | Farmers, bank accounts, land parcels |
| `005` | Workers, skills |
| `006` | Farms, farm activities |
| `007` | Document OCR/locale/archive, link constraints |
| `008` | Procurements, farmer ledger, farmer payments (partitioned) |
| `009` | Work orders, attendance |
| `010` | Assets, maintenance, usage logs, vehicle trips |
| `011` | Rental customers, agreements |
| `012` | Financial transactions, expenses, collections, payments |
| `013` | Audit indexes, sync tables |
| `014` | AI jobs, OCR, WhatsApp, voice, summaries |
| `015` | Global permissions and per-org system roles seed |

- Shared migration helpers in `migration_utils.py` (audit columns, partitions, org FK)
- Monthly partitions seeded for 2026 on high-volume tables

#### API contract

- Modular OpenAPI 3.0 spec: `docs/api/openapi.yaml` + `paths/` + `schemas/`
- Human-readable contract: `docs/api/API_CONTRACT.md`
- Bundled spec for Postman: `docs/api/openapi.bundled.yaml`

#### Reporting

- Architecture doc: `docs/reporting/REPORTING_ARCHITECTURE.md`
- KPI definitions: `docs/reporting/kpi_definitions.md`
- Eight parameterized SQL dashboards: `docs/reporting/sql/01`–`08`

#### Document management design

- Full module design: `docs/modules/DOCUMENT_MANAGEMENT.md` (implemented vs gaps)

#### CI/CD & deployment

- GitHub Actions: `ci.yml`, `validate.yml`, `deploy.yml`
- EC2 deploy via S3 + SSM Run Command (`deploy/scripts/`)
- Production Docker Compose: `infra/docker-compose.prod.yml`
- Post-deploy smoke tests: `scripts/smoke-test-api.sh`
- CI/CD documentation: `docs/deploy/CI_CD.md`, `deploy/README.md`

#### Synthetic seed (UAT demo data)

- Generator: `scripts/synthetic_seed/generate_synthetic_data.py`
- Bhairkhanpally demo: 50 farmers, 200 procurements, ledger, expenses, etc.
- Purge script: `scripts/synthetic_seed/sql/99_purge_synthetic_data.sql`

#### Cache layer

- Pluggable `CacheProvider`: none / memory / redis (`app/core/cache/`)
- Permission cache in `app/core/dependencies.py` (TTL via `CACHE_TTL_SECONDS`)

#### Agent & project docs

- `AGENTS.md` — agent coding guide
- `README.md` — human onboarding, tech stack, quick start

#### Frontend placeholder

- Vercel config stub: `frontend/vercel.json`, `frontend/README.md`

### Added

- `.github/DEPLOY_CONFIG.md` — GitHub Actions secrets/variables from `krishifarms-infra` dev Terraform outputs
- Deploy workflow: `AWS_REGION`, `NGINX_LOCAL_PORT`, and `PUBLIC_HEALTH_CHECK_URL` vars for shared EC2 dev (port 8082)

### Changed

- `app/main.py` — mounts Phase 1 routers under `/api/v1`
- `infra/docker-compose.yml` — optional Redis profile
- `pyproject.toml` — optional `[redis]` extra

### Security

- JWT access + refresh tokens; RBAC via `require_permission()`
- Org-scoped multi-tenancy on all business rows

---

[Unreleased]: https://github.com/gvsharma/krishifarms-backend/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/gvsharma/krishifarms-backend/commit/60bb2b5
