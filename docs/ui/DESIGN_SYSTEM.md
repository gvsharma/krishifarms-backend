# Design System — KrishiFarms CRM

**Foundation:** shadcn/ui + Tailwind CSS, Dribbble-inspired Farm Management SaaS aesthetic  
**Inspiration:** [Farm Management SaaS Dashboard](https://dribbble.com/shots/27437443-Farm-Management-SaaS-Dashboard) — soft greens, warm neutrals, spacious sidebar, large rounded KPI cards  
**Platform:** Next.js · CSS variables in `globals.css` + `tailwind.config.ts` · implemented in `frontend/src/`

---

## 1. Design Tokens

### 1.1 Spacing scale (4 px base)

| Token | Value | Usage |
|-------|-------|-------|
| `space-0` | 0 | Flush |
| `space-1` | 4 px | Icon padding, tight inline |
| `space-2` | 8 px | Chip gaps, compact table cell padding |
| `space-3` | 12 px | Form field vertical rhythm |
| `space-4` | 16 px | Card padding (compact), section gap |
| `space-5` | 20 px | List item padding (comfortable) |
| `space-6` | 24 px | Card padding (comfortable), modal padding |
| `space-8` | 32 px | Section separation |
| `space-10` | 40 px | Page header margin |
| `space-12` | 48 px | Dashboard KPI row gap |
| `space-16` | 64 px | Hero / empty state vertical |

**Layout constants**

| Token | Value |
|-------|-------|
| Sidebar expanded | 260 px |
| Sidebar collapsed | 72 px |
| Top bar height | 56 px |
| Slide-over width | 480 px (tablet: 100%) |
| Command palette width | 640 px |
| Max content width | 1440 px (centered on wide) |

### 1.2 Border radius

| Token | Value | Usage |
|-------|-------|-------|
| `radius-xs` | 4 px | Badges, tags |
| `radius-sm` | 6 px | Inputs, chips |
| `radius-md` | 8 px | Cards, buttons |
| `radius-lg` | 12 px | Modals, command palette |
| `radius-xl` | 16 px | KPI cards, dashboard widgets (Dribbble: generous rounding) |
| `radius-full` | 9999 px | Avatars, pills |

Tailwind mapping: `rounded-md` as default for cards; `rounded-lg` for KPI tiles.

### 1.3 Elevation & shadows

Prefer **surface tint + border** over heavy shadows (Linear/Stripe aesthetic).

| Level | Shadow | Border | Usage |
|-------|--------|--------|-------|
| E0 | none | `outlineVariant` 1 px | Tables, flat panels |
| E1 | `0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(45,106,79,0.06)` | optional | Cards, KPI tiles (green-tinted shadow) |
| E2 | `0 4px 12px rgba(0,0,0,0.08)` | — | Dropdowns, popovers |
| E3 | `0 8px 24px rgba(0,0,0,0.12)` | — | Command palette, modals |
| E4 | `0 16px 48px rgba(0,0,0,0.16)` | — | Full-screen overlay |

Dark theme: reduce shadow opacity 50%; increase border contrast.

### 1.4 Motion

| Token | Duration | Curve | Usage |
|-------|----------|-------|-------|
| `motion-instant` | 100 ms | `easeOut` | Hover states, checkbox |
| `motion-fast` | 150 ms | `easeOutCubic` | Tooltips, snackbars |
| `motion-normal` | 250 ms | `easeInOutCubic` | Slide-over, tab switch |
| `motion-slow` | 350 ms | `easeInOutCubic` | Sidebar collapse, page transition |
| `motion-stagger` | 50 ms | per child | KPI card load-in |

**Reduced motion:** Respect `prefers-reduced-motion` — cross-fade instead of slide (`motion-reduce:transition-none`).

---

## 2. Typography

### 2.1 Font stacks

| Role | English | Telugu fallback | Mono |
|------|---------|-----------------|------|
| Primary | **Plus Jakarta Sans** | **Noto Sans Telugu** | **JetBrains Mono** |
| Fallback | system-ui, sans-serif | Noto Sans, sans-serif | ui-monospace |

Load via `next/font` (`Plus_Jakarta_Sans`, `Noto_Sans_Telugu`, `JetBrains_Mono`). When locale `te`, apply Noto Sans Telugu to `body` and headings; keep Jakarta for Latin numerals in tables if needed for alignment.

**Dribbble direction:** Clean geometric sans (Plus Jakarta Sans) for headings and UI — modern SaaS feel with agricultural warmth, not corporate blue.

### 2.2 Type scale

| Style | Size / Line | Weight | Usage |
|-------|-------------|--------|-------|
| `display-lg` | 36 / 44 | 600 | CEO dashboard hero metric |
| `display-sm` | 28 / 36 | 600 | Section hero |
| `heading-lg` | 22 / 28 | 600 | Page title |
| `heading-md` | 18 / 24 | 600 | Card title, drawer header |
| `heading-sm` | 16 / 22 | 600 | Tab label, column header |
| `body-lg` | 16 / 24 | 400 | Primary body |
| `body-md` | 14 / 20 | 400 | Table cells, forms |
| `body-sm` | 12 / 16 | 400 | Captions, metadata |
| `label-md` | 12 / 16 | 500 | Buttons, chips |
| `label-sm` | 11 / 14 | 500 | Badges, table header |
| `mono-md` | 13 / 20 | 400 | IDs (`PR-2026-0142`), amounts in tables |

**Telugu:** Increase line-height +2 px for `body-lg` and `body-md` to avoid matra clipping.

### 2.3 Numeric typography

- Tabular figures (`font-variant-numeric: tabular-nums` / Tailwind `tabular-nums`) on all amount/weight columns.
- Currency: always prefix `₹` with thin space.
- Weights: primary unit **quintals** in headings; kg in secondary `body-sm`.

---

## 3. Color System

Seed color: **agricultural green** with warm neutral surfaces — trustworthy, not "startup neon." Matches Dribbble Farm SaaS shot: `#2D6A4F` primary on `#FAFAF9` page canvas, white card surfaces, subtle green-tinted shadows.

### 3.1 Brand & semantic (light theme)

| Token | Hex | Usage |
|-------|-----|-------|
| `primary` | `#2D6A4F` | Primary actions, active nav, links |
| `onPrimary` | `#FFFFFF` | Text on primary |
| `primaryContainer` | `#D8F3DC` | Selected rows, chip bg |
| `onPrimaryContainer` | `#1B4332` | Text on primary container |
| `secondary` | `#40916C` | Secondary actions, accents |
| `tertiary` | `#BC6C25` | Harvest / corn accent, warnings alt |
| `error` | `#BA1A1A` | Errors, destructive |
| `errorContainer` | `#FFDAD6` | Error banners |
| `success` | `#1B7F5A` | Confirmed, completed |
| `successContainer` | `#D1FAE5` | Success toast bg |
| `warning` | `#B45309` | Draft, pending approval |
| `warningContainer` | `#FEF3C7` | Outstanding highlights |
| `info` | `#0369A1` | Informational banners |
| `surface` | `#FAFAF9` | Page background |
| `surfaceContainerLow` | `#FFFFFF` | Cards |
| `surfaceContainerHigh` | `#F5F5F4` | Sidebar, table header |
| `outline` | `#D6D3D1` | Borders |
| `outlineVariant` | `#E7E5E4` | Subtle dividers |
| `onSurface` | `#1C1917` | Primary text |
| `onSurfaceVariant` | `#57534E` | Secondary text |
| `inverseSurface` | `#292524` | Command palette (optional dark popover) |

### 3.2 Domain semantic colors

| Domain | Color | Badge example |
|--------|-------|---------------|
| Procurement draft | `#B45309` | Draft |
| Procurement confirmed | `#1B7F5A` | Confirmed |
| Procurement cancelled | `#78716C` | Cancelled |
| Payment pending | `#D97706` | Pending |
| Payment completed | `#1B7F5A` | Completed |
| Payment reversed | `#78716C` strikethrough | Reversed |
| Ledger debit | `#BA1A1A` | Debit |
| Ledger credit | `#1B7F5A` | Credit |
| Moisture high | `#DC2626` | > 17% |
| Crop paddy | `#2D6A4F` | Chip |
| Crop corn | `#CA8A04` | Chip |

### 3.3 Dark theme palette

| Token | Hex |
|-------|-----|
| `primary` | `#74C69D` |
| `onPrimary` | `#003822` |
| `primaryContainer` | `#1B4332` |
| `surface` | `#0C0A09` |
| `surfaceContainerLow` | `#1C1917` |
| `surfaceContainerHigh` | `#292524` |
| `onSurface` | `#FAFAF9` |
| `onSurfaceVariant` | `#A8A29E` |
| `outline` | `#44403C` |

Chart series (both themes): `#2D6A4F`, `#40916C`, `#52B788`, `#BC6C25`, `#CA8A04`, `#0369A1`, `#7C3AED`.

---

## 4. Responsive Grid

### 4.1 Breakpoints

| Name | Width | Layout |
|------|-------|--------|
| **mobile** | < 600 px | Bottom nav, single column, full-screen drawers |
| **tablet** | 600–1024 px | Collapsible sidebar, 2-col dashboard |
| **desktop** | 1024–1440 px | Expanded sidebar, 3-col dashboard |
| **wide** | > 1440 px | Max-width container, 4-col KPI row |

### 4.2 Grid columns

| Breakpoint | Columns | Gutter | Margin |
|------------|---------|--------|--------|
| mobile | 4 | 16 px | 16 px |
| tablet | 8 | 24 px | 24 px |
| desktop | 12 | 24 px | 32 px |
| wide | 12 | 32 px | auto (centered) |

**Dashboard KPI row:** 1 col mobile · 2 tablet · 4 desktop · 4 wide (equal flex).

**Farmer profile:** Header full width; tabs scroll horizontal on mobile; metrics strip 2×2 grid mobile, 1×4 desktop.

---

## 5. Tailwind + shadcn/ui Theming

### 5.1 CSS variables (`globals.css`)

Map design tokens to shadcn semantic variables:

```css
:root {
  --primary: 152 45% 30%;           /* #2D6A4F */
  --primary-foreground: 0 0% 100%;
  --secondary: 152 35% 42%;         /* #40916C */
  --background: 60 9% 98%;          /* #FAFAF9 surface */
  --card: 0 0% 100%;
  --muted: 60 5% 96%;               /* surfaceContainerHigh */
  --border: 20 6% 84%;              /* outline */
  --radius: 0.5rem;                 /* radius-md */
  /* … success, warning, error, chart series */
}
```

Programmatic mirror: `src/lib/design/tokens.ts` (Gamya pattern).

### 5.4 App shell (Dribbble-inspired)

Implemented in `frontend/src/components/shell/`.

| Element | Spec |
|---------|------|
| **Sidebar** | Fixed left, 260 px expanded / 72 px collapsed; white surface, border-r; section labels (Overview, Operations, Finance, Insights, System); active item = filled primary green pill with icon + label |
| **Header** | Sticky 64 px; breadcrumbs left; centered global search with ⌘K hint; quick action, notifications bell (badge), theme toggle, avatar dropdown |
| **KPI cards** | `rounded-2xl`, white surface, icon in green-tinted circle, large tabular value, delta badge (success/destructive) |
| **Page canvas** | Warm `#FAFAF9` background; max-width 1440 px centered content |
| **Collapse** | Sidebar collapse persisted in Zustand `ui-store` |

Reference shot: [Dribbble #27437443](https://dribbble.com/shots/27437443-Farm-Management-SaaS-Dashboard)

### 5.5 Component theme overrides

| shadcn / custom | Customization |
|-----------------|---------------|
| `Sidebar` / `KrishiSidebar` | `bg-muted`, no shadow, border-r |
| `Button` variant `default` | `rounded-md`, h-10 (compact h-9) |
| `Button` variant `outline` | 1 px `border` |
| `KrishiDataTable` | Custom table — see [COMPONENT_LIBRARY.md](./COMPONENT_LIBRARY.md) |
| `Card` | `shadow-sm`, `rounded-lg` |
| `Tabs` | 2 px primary indicator, scrollable on mobile |
| `Dialog` / `Sheet` | `rounded-lg`, max-w-lg (560 px) |
| `Sonner` toast | Bottom-right desktop; bottom-center mobile |

### 5.6 Theme modes

- **Light** default (field officers often outdoors — high contrast).
- **Dark** optional (office/accounting) via `next-themes`.
- **System** follows OS.
- Persist preference in `localStorage` / Zustand `ui-store`.

---

## 6. Iconography

- **Set:** [Lucide React](https://lucide.dev) (default); outline style for inactive nav.
- **Size:** 20 px inline · 24 px nav · 32 px empty states.
- **Domain icons**

| Entity | Icon |
|--------|------|
| Farmer | `person_outline` |
| Procurement | `scale` / `inventory_2` |
| Payment | `payments` |
| Collection | `account_balance_wallet` |
| Trip | `local_shipping` |
| Document | `description` |
| Paddy | custom SVG grain stalk (monochrome) |
| Corn | `grain` |

Never rely on color alone — pair icon + label for status.

---

## 7. Data Density Modes

User preference + auto compact on `< tablet`.

| Aspect | Compact | Comfortable |
|--------|---------|-------------|
| Table row height | 40 px | 52 px |
| Table cell padding | 8 × 12 | 12 × 16 |
| KPI card height | 88 px | 112 px |
| Font in tables | `body-sm` | `body-md` |
| Sidebar item height | 36 px | 44 px |
| Default page size | 50 | 20 |

Toggle: Settings → Appearance · shortcut `D` then `C` in command palette.

---

## 8. Elevation of Brand Moments

| Moment | Treatment |
|--------|-----------|
| Collection confirmed | Success toast + subtle confetti-free pulse on timeline step |
| Payment reversed | Muted banner + ledger reversal row animation |
| CEO net cash | `display-lg` in primary green/red delta |
| Empty farmers | Illustration: Telangana field line art, minimal |

Avoid gratuitous animation on financial confirm — use explicit confirmation dialogs.

---

## Cross-References

- Components: [COMPONENT_LIBRARY.md](./COMPONENT_LIBRARY.md)
- Frontend theme wiring: [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md)
- Accessibility contrast: [ACCESSIBILITY_AND_UX.md](./ACCESSIBILITY_AND_UX.md)
