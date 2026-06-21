# Frontend Architecture — KrishiFarms CRM Web

**Stack:** Next.js 15 (App Router) · TypeScript · Tailwind CSS · shadcn/ui · TanStack Query · Zustand

Aligned with the [Gamya Couture frontend](https://github.com/gvsharma/gamyaboutique) (`gamya-boutique/frontend/`) deployment pattern: Vercel hosting, `/api/v1` proxy to EC2, Axios + JWT.

---

## Stack decision

| Why Next.js | Detail |
|-------------|--------|
| **Vercel deploy** | `frontend/` already has `vercel.json`; same-origin API proxy avoids mixed content |
| **Gamya parity** | Proven stack in sibling project — App Router, TanStack Query, Zustand, Axios |
| **Dashboard SaaS velocity** | RSC for shell/layout; client components for dense tables, Kanban, command palette |
| **OpenAPI clients** | TypeScript client generation from `docs/api/openapi.bundled.yaml` |

**Mobile:** Responsive web first (breakpoints in [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md)). PWA optional later — **not** Flutter mobile.

**Supersedes:** Earlier Flutter Web architecture docs (`FLUTTER_ARCHITECTURE.md`, `WIDGET_TREE.md`).

---

## 1. Feature-First Folder Structure

```text
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx                    # Root layout, fonts, providers
│   │   ├── globals.css                   # Tailwind + CSS variables (design tokens)
│   │   ├── (auth)/
│   │   │   └── login/page.tsx
│   │   └── (app)/                        # Authenticated shell (route group)
│   │       ├── layout.tsx                # AppShell: sidebar, top nav, breadcrumbs
│   │       ├── dashboard/[dashboardId]/page.tsx
│   │       ├── farmers/
│   │       │   ├── page.tsx
│   │       │   └── [id]/[tab]/page.tsx
│   │       ├── operations/collection-entry/[[...sessionId]]/page.tsx
│   │       ├── procurements/
│   │       ├── finance/payments/
│   │       ├── fleet/
│   │       ├── documents/page.tsx
│   │       └── settings/[section]/page.tsx
│   │
│   ├── components/                       # Design system + shell (presentational)
│   │   ├── ui/                           # shadcn/ui primitives (Button, Input, Sheet, …)
│   │   ├── shell/                        # AppShell, Sidebar, TopNav, Breadcrumbs
│   │   ├── tables/
│   │   ├── filters/
│   │   ├── kpi/
│   │   ├── charts/
│   │   ├── timeline/
│   │   └── overlays/                     # CommandPalette, SlideOver
│   │
│   ├── features/                         # Feature modules (data + feature UI)
│   │   ├── auth/
│   │   │   ├── components/login-form.tsx
│   │   │   ├── hooks/use-login.ts
│   │   │   └── schemas/login.schema.ts
│   │   ├── farmers/
│   │   ├── procurements/
│   │   ├── payments/
│   │   ├── documents/
│   │   ├── dashboard/
│   │   └── settings/
│   │
│   ├── hooks/                            # Shared hooks (use-media-query, use-debounce)
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts                 # Axios instance + interceptors
│   │   │   ├── config.ts                 # API base URL (single source of truth)
│   │   │   ├── endpoints.ts
│   │   │   └── services/                 # auth.service.ts, farmers.service.ts, …
│   │   ├── auth/
│   │   │   └── token-storage.ts
│   │   ├── query/
│   │   │   └── query-keys.ts
│   │   ├── format/
│   │   │   ├── currency.ts               # INR Decimal, en_IN grouping
│   │   │   ├── weight.ts                 # qtl + kg
│   │   │   └── date.ts
│   │   ├── design/tokens.ts              # Programmatic tokens (mirrors globals.css)
│   │   └── feature-flags.ts
│   ├── stores/
│   │   ├── auth-store.ts                 # Session, permissions cache
│   │   ├── locale-store.ts
│   │   ├── density-store.ts
│   │   └── ui-store.ts                   # Sidebar collapsed, command palette open
│   ├── types/                            # Shared TS types (API DTOs, domain)
│   └── constants/routes.ts
│
├── e2e/                                  # Playwright (smoke + critical paths)
├── public/
├── next.config.ts                        # API rewrites (Vercel → EC2)
├── tailwind.config.ts
├── components.json                       # shadcn/ui config
├── package.json
└── tsconfig.json
```

**Convention:** `app/` = routes only; `components/` = reusable presentational; `features/` = feature-specific logic + composed UI; `lib/api` = HTTP boundary.

---

## 2. Layering & Data Flow

```text
page.tsx (Server Component where possible)
  → feature components ('use client' when interactive)
    → hooks (useFarmers, useExecutiveDashboard)
      → TanStack Query
        → lib/api/services/*
          → Axios client (Bearer from auth-store)
```

### Server vs Client Components

| Use RSC (default) | Use `'use client'` |
|-------------------|---------------------|
| App shell layout, static settings nav | Data tables with sort/filter/pagination |
| Initial page structure, metadata | Kanban drag, command palette, slide-overs |
| Permission-gated route shells | Forms with React Hook Form |
| SEO / `generateMetadata` on public routes | Charts, date pickers, collection workflow |

Keep client boundaries **small** — wrap interactive islands, not entire pages, when feasible.

### Domain rules (unchanged from backend)

- Money as `string` / `Decimal` in TS models — never `number` for currency math in UI.
- Ledger views read-only; reversal rows styled distinctly.
- Partitioned entities: pass `date` query param on ID lookups (`/procurements/:id?date=…`).

---

## 3. State Management

### TanStack Query (server/async state)

Primary store for API data: lists, details, dashboards, mutations with cache invalidation.

| Pattern | Use case |
|---------|----------|
| `useQuery(['farmers', filters])` | Paginated farmer list |
| `useQuery(['farmer', id])` | Profile detail |
| `useMutation` + `invalidateQueries` | After confirm procurement, payment allocation |
| `queryKeys` factory in `lib/query/query-keys.ts` | Stable cache keys (Gamya pattern) |

### Zustand (client/UI state)

| Store | Responsibility |
|-------|----------------|
| `auth-store` | JWT, user, permissions; hydrate from `token-storage` |
| `locale-store` | `en` / `te`; drives `Accept-Language` + `next-intl` |
| `density-store` | Compact / comfortable table density |
| `ui-store` | Sidebar collapsed, command palette open, active slide-over |

**Do not** duplicate server data in Zustand — Query is the source of truth for API entities.

### Complex workflows

Collection entry step machine: local `useReducer` or small Zustand slice in `features/procurements/` — not global store.

---

## 4. Routing — Next.js App Router

### Route map (mirrors IA)

```text
/login
/(app)
  /dashboard/:dashboardId
  /farmers
  /farmers/:id/:tab
  /operations/collection-entry/[[...sessionId]]
  /procurements/board | table | map
  /procurements/:id
  /finance/payments
  /finance/payments/:id
  /fleet/...
  /documents
  /settings/:section
```

### Layout groups

| Group | Purpose |
|-------|---------|
| `(auth)` | Login — no shell |
| `(app)` | `AppShell` layout: sidebar, top nav, breadcrumbs |

### Guards

1. **`(app)/layout.tsx`** — read auth from cookie/store; redirect to `/login` if unauthenticated.
2. **Permission checks** — hide nav items server-side or via `permissions` from JWT; route-level guard redirects to `/forbidden`.

### Deep linking

- Shareable tabs: `/farmers/:id/ledger`.
- Partitioned entities: `searchParams.date` on procurement detail.
- Role default home: middleware or `(app)/page.tsx` redirect to persona home (see IA doc).

### Metadata

`export const metadata` / `generateMetadata` per route for document title (`Farmer · KrishiFarms`).

---

## 5. API Client Layer (OpenAPI Alignment)

### Generation

```bash
# From repo root (CI step)
npx @redocly/cli bundle docs/api/openapi.yaml -o docs/api/openapi.bundled.yaml
npx openapi-typescript docs/api/openapi.bundled.yaml -o frontend/src/types/api.generated.ts
```

Hand-maintain service modules in `lib/api/services/` for Phase 1; adopt generated types when Phase 2 stabilizes.

### Axios stack (Gamya pattern)

| Layer | Responsibility |
|-------|----------------|
| `lib/api/config.ts` | `NEXT_PUBLIC_API_BASE_URL` — `/api/v1` on Vercel |
| `lib/api/client.ts` | Base URL, timeouts, interceptors |
| Request interceptor | `Authorization: Bearer`, `Accept-Language` |
| Idempotency header | Financial POSTs |
| Response unwrap | Parse `{ success, data, meta }` before DTO use |

### Phase-aware services

```text
farmers.service.ts
├── live API calls                    — Phase 2+
└── mock adapter (feature flag)       — UI dev / demos
```

`NEXT_PUBLIC_PHASE2_API_ENABLED` switches implementation at module boundary.

### Vercel proxy

Browser → same-origin `/api/v1` → Next.js rewrite → EC2 nginx. Server Components use `API_PROXY_TARGET` for direct backend fetch (see Gamya `ARCHITECTURE.md`).

---

## 6. Theme & Locale

### Theme

- CSS variables in `globals.css` mapped to Tailwind (`tailwind.config.ts`).
- shadcn/ui components consume `--primary`, `--surface`, etc. from [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md).
- `next-themes` for light / dark / system; persist in `localStorage`.

### Locale

| Concern | Implementation |
|---------|----------------|
| UI strings | `next-intl` message files (`messages/en.json`, `messages/te.json`) |
| Entity names | Display `name_te` when locale is `te` and field populated |
| API | `Accept-Language` header on all requests |
| Numbers | `Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' })` |
| Dates | `dd MMM yyyy` display; ISO in API |

Language toggle in profile menu; persist in `locale-store`.

---

## 7. Responsive Strategy

| Breakpoint | Layout (Tailwind) |
|------------|-------------------|
| `< md` (< 768px) | Bottom nav, full-screen sheets, card lists |
| `md`–`lg` | Collapsed sidebar default, 2-column grids |
| `≥ lg` | Full sidebar, data tables, multi-column dashboards |

Use `useMediaQuery` or Tailwind `hidden md:block` for layout swaps:

```tsx
// FarmerListPage: table on desktop, cards on mobile
<FarmerDataTable className="hidden lg:block" />
<FarmerCardList className="lg:hidden" />
```

**Web-specific:** hover row states, Kanban pointer drag, `user-select: none` on drag handles.

---

## 8. Testing Strategy

| Layer | Tool |
|-------|------|
| Unit | Vitest — formatters, permission helpers, error mapper |
| Component | React Testing Library — KPI card states, login form |
| E2E | Playwright — auth flow, document upload (mock presign), collection happy path |
| Visual regression | Optional Chromatic / Playwright screenshots on PR |

### CI

- `npm run lint` (ESLint + `eslint-config-next`)
- `npm run build`
- `npm run test:e2e:smoke` against staging (when app exists)

---

## 9. Cross-Cutting Concerns

| Concern | Approach |
|---------|----------|
| Logging | Client: redact tokens in dev-only logs |
| Analytics | PostHog / Plausible — route transitions, key conversions |
| Error reporting | Sentry Next.js — API 5xx, React error boundaries |
| Offline | Not Phase 1 — optional read cache via Query `staleTime` later |
| Security | JWT in httpOnly cookie (preferred) or `sessionStorage` + short-lived access token |

---

## 10. Deployment

- **Host:** Vercel (`frontend/` root directory).
- **Env:** `NEXT_PUBLIC_API_BASE_URL=/api/v1`, `API_PROXY_TARGET=http://<EC2_IP>`, `NEXT_PUBLIC_SITE_URL`.
- **CORS:** Backend `CORS_ORIGINS` must include Vercel URL.

Reference: [frontend/README.md](../../frontend/README.md), [CI_CD.md](../deploy/CI_CD.md).

---

## Cross-References

- Component trees: [COMPONENT_TREE.md](./COMPONENT_TREE.md)
- Screen specs: [SCREEN_SPECS.md](./SCREEN_SPECS.md)
- Design tokens: [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md)
- API: [API_CONTRACT.md](../api/API_CONTRACT.md)
- Gamya reference: `gamya-boutique/frontend/ARCHITECTURE.md`
