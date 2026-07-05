# Material Design 3 — KrishiFarms Web

**Phase W1** foundation for the Next.js CRM shell using **MUI v6** with MD3 color schemes, **Helvetica** typography, and shared comment/settings patterns.

---

## Stack

| Package | Role |
|---------|------|
| `@mui/material@6` | Components, MD3 `createTheme` + `colorSchemes` |
| `@mui/material-nextjs` | `AppRouterCacheProvider` for App Router SSR |
| `@mui/icons-material` | Nav and action icons |
| `@emotion/react` / `@emotion/cache` | CSS-in-JS runtime |

Tailwind + legacy shadcn-style components remain for the dashboard (W1 incremental migration). New admin/settings surfaces use MUI.

---

## Theme tokens

Defined in `frontend/src/theme/material-theme.ts`.

### Color (agri green)

| Token | Light | Usage |
|-------|-------|--------|
| `primary.main` | `#2D6A4F` | Brand, nav active, CTAs |
| `primary.light` | `#40916C` | Hover, charts |
| `primary.dark` | `#1B4332` | Pressed states |
| `background.default` | `#FAFAF9` | Page canvas |
| `background.paper` | `#FFFFFF` | Cards, drawer, app bar |

Dark scheme inverts greens to `#52B788` / `#0F1410` surfaces. Synced with `next-themes` via `class="dark"` on `<html>`.

### Typography

Primary stack (system Helvetica — no font files):

```css
"Helvetica Neue", Helvetica, Arial, sans-serif
```

Telugu copy uses `--font-noto-telugu` (Noto Sans Telugu via `next/font`).

### Layout

| Constant | Value |
|----------|-------|
| `DRAWER_WIDTH` | 260px |
| `DRAWER_WIDTH_COLLAPSED` | 72px |
| App bar height | 64px |
| Max content width | 1440px (`MuiPageShell`) |

---

## Provider wiring

```text
QueryClientProvider
  └── next-themes ThemeProvider (class strategy)
        └── ThemeRegistry
              ├── AppRouterCacheProvider
              ├── MUI ThemeProvider (cssVariables + colorSchemes)
              └── CssBaseline
```

File: `frontend/src/theme/theme-registry.tsx`

---

## Shell

`MuiAppShell` (`frontend/src/components/shell/mui-app-shell.tsx`):

- Permanent drawer (temporary on mobile)
- Role-filtered nav from `NAV_SECTIONS` in `constants/routes.ts`
- App bar: search placeholder, notifications, theme toggle, user menu

Nav groups (W1 placeholders): **Dashboard**, **Farmers**, **Procurement**, **Services**, **Finance**, **Settings**.

---

## Comments pattern

Reusable `CommentThread` — `frontend/src/components/comments/CommentThread.tsx`

| Prop | Type | Description |
|------|------|-------------|
| `entityType` | `string` | e.g. `farmer`, `procurement` |
| `entityId` | `string` | UUID of parent record |
| `title` | `string?` | Section heading |

API: `frontend/src/features/comments/api.ts` → `GET/POST /comments`

Client headers on POST (audit accountability):

- `X-Device-Id` — stable UUID in `localStorage` (`krishi-device-id`)
- `X-Client-Type: web`

---

## Settings (W1)

| Route | Component | API |
|-------|-----------|-----|
| `/settings` | Hub cards | — |
| `/settings/users` | MUI Table | `GET /users` |
| `/settings/villages` | Table + add dialog stub | `GET/POST /villages` |
| `/settings/master-data` | Link hub | crops/buyers/agents → W2 |

---

## Conventions

1. **New admin UI** → MUI + `MuiPageShell`; keep dashboard on Tailwind until W2.
2. **API calls** → `fetchApi` from `lib/api/client.ts` (JWT from `krishi-access-token`).
3. **Lists** → TanStack Query; invalidate on mutation.
4. **Dark mode** → toggle sets `next-themes` class; MUI reads via `colorSchemeSelector: "class"`.
5. **Do not** pass `org_id` from client — JWT only.

---

## W2 follow-ups

- Wire JWT auth context → real role nav filtering
- Migrate dashboard KPI/cards to MUI
- Master-data CRUD pages (crops, buyers, agents)
- Embed `CommentThread` on farmer/procurement detail pages
- OpenAPI-generated types for API envelopes
