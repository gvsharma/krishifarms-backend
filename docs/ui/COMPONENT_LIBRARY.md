# Component Library — KrishiFarms CRM

Enterprise component specs for Next.js implementation (shadcn/ui + Tailwind). All components use design tokens from [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md).

---

## 1. App Shell

### Anatomy

```text
┌──────────────────────────────────────────────────────────────┐
│ [Logo] KrishiFarms    [Search... ⌘K]    [+] [🔔] [Profile]   │  Top Nav (56px)
├──────────┬───────────────────────────────────────────────────┤
│ Sidebar  │ Breadcrumbs                                       │
│ (260px)  ├───────────────────────────────────────────────────┤
│          │                                                   │
│ Nav      │              Main Content Area                    │
│ groups   │              (scroll)                             │
│          │                                                   │
│ [◀]      │                                                   │
└──────────┴───────────────────────────────────────────────────┘
```

### Variants

| Variant | Breakpoint | Behavior |
|---------|------------|----------|
| Standard | desktop | Expanded sidebar + content |
| Collapsed | user toggle | 72 px icons + tooltips |
| Mobile | < 600 px | Bottom nav (5 items) + hamburger for rest |

### States

- **Loading:** Sidebar skeleton; content area shimmer.
- **Unauthorized route:** Redirect to login; preserve intended URL.
- **403 module:** Inline "No access" panel with request-access copy (no crash).

### Usage rules

- One app shell wraps all authenticated routes via `ShellRoute`.
- Main content never scrolls under fixed top bar — use `padding-top: 56px`.
- Org name truncates with tooltip; show village context chip for Field Officer optional scope.

---

## 2. Sidebar

### Anatomy

- Org header (logo + name)
- Group labels: Home · Operations · Finance · Fleet · Workforce · Rentals · Farms · Reports · Settings
- Nav item: icon + label + optional badge count
- Collapse control at bottom
- User mini-card (avatar, role, locale toggle)

### States

| State | Visual |
|-------|--------|
| Default | `onSurfaceVariant` icon |
| Hover | `surfaceContainerHigh` bg |
| Active | `primaryContainer` bg, `primary` icon + label |
| Disabled | hidden (not rendered) per RBAC |
| Badge | `error` or `warning` pill — max "99+" |

### Variants

- **Role-filtered:** Same component, items list from `NavConfig.forRole(role)`.
- **Collapsed:** Icon only; `Tooltip` on hover.

---

## 3. Top Nav

### Elements (left → right)

1. Mobile menu (mobile only)
2. Global search trigger (expands or opens overlay)
3. Spacer
4. Quick create `+` menu (role-filtered actions)
5. Notifications bell (activity feed preview) — P1 `GET /activity-feed`
6. Profile menu: language (EN/TE), density, theme, logout

### Interaction

- Search field: click or `/` focuses; `Escape` closes.
- Profile avatar shows initials from user name.

---

## 4. Search Bar

### Anatomy

```text
┌─ 🔍  Search farmers, procurements, documents...        ⌘K ─┐
└─────────────────────────────────────────────────────────────┘
```

### Behavior

| Context | Scope |
|---------|-------|
| In list page | Filters current list (`q=` param) |
| In top bar | Opens command palette with search mode |
| Mobile | Full-width overlay |

### States

- **Idle:** Placeholder rotates examples every 8 s ("Search Bhairkhanpally farmers…").
- **Typing:** Debounce 300 ms.
- **Results:** Grouped list below input (max 8 per group).
- **Empty:** "No results — try farmer phone or PR number."
- **Loading:** 3-row skeleton in dropdown.

---

## 5. Command Palette

### Anatomy (640 px overlay, E3)

```text
┌─────────────────────────────────────────────┐
│ 🔍  Type a command or search...              │
├─────────────────────────────────────────────┤
│ RECENT                                       │
│   → Rajesh Kumar (Farmer)                    │
│ ACTIONS                                      │
│   ⊕ New collection entry                     │
│   ⊕ Upload document                          │
│ NAVIGATION                                   │
│   Go to Procurement Board                    │
│ ENTITIES (when query ≥ 2 chars)              │
│   Farmer · FRM-0042 · Bhairkhanpally         │
└─────────────────────────────────────────────┘
│ ↑↓ navigate · ↵ open · esc close            │
└─────────────────────────────────────────────┘
```

### Variants

- **Navigation mode** (default): actions + routes.
- **Search mode** (`/` or click search): entity results from `GET /search` (P5).
- **Action mode** (`>` prefix): run commands ("Confirm procurement").

### States

- Selected row: `primaryContainer` highlight.
- Disabled action: shown gray with permission tooltip.

---

## 6. Data Table

Premium enterprise table — not raw `DataTable`.

### Anatomy

```text
┌─ [☐] Farmer          Village      Outstanding   Last proc.  ⋮ ─┐
├──────────────────────────────────────────────────────────────────┤
│ [☐] Rajesh Kumar     Bhairkhan…   ₹45,200       12 Jun 2026  ⋮ │
│ [☐] Lakshmi Devi     Bhairkhan…   ₹0            10 Jun 2026  ⋮ │
└──────────────────────────────────────────────────────────────────┘
│ ← sticky ID/name          → scroll columns →    sticky actions │
```

### Features

| Feature | Spec |
|---------|------|
| Sorting | Click header; `sort=-created_at`; indicator arrow |
| Selection | Checkbox column; shift-click range |
| Inline actions | `⋮` menu: View, Edit, Record payment |
| Sticky columns | First 1–2 columns + actions column |
| Row hover | `surfaceContainerHigh`; click row → detail |
| Pagination | Bottom bar: page size, total count, prev/next |
| Column resize | desktop only; persist in saved view |
| Empty | Custom empty state component |

### States

- **Loading:** `TableSkeleton` 10 rows.
- **Error:** Inline retry banner above table.
- **Partial load:** Infinite scroll optional on mobile lists.

### Density

Compact 40 px · Comfortable 52 px row height.

---

## 7. Smart Filters

### Anatomy

Horizontal filter bar above table:

```text
[Village ▾] [Crop ▾] [Status ▾] [Date range ▾] [Outstanding > 0 ☐]  Clear · Save view
```

### Filter types

| Type | UI control |
|------|------------|
| Enum | Multi-select chip dropdown |
| Date range | Presets: Today, This week, Season, Custom |
| Numeric | Min/max inputs (moisture %, amount) |
| Boolean | Toggle chip |
| Search | `q` synced with search bar |

### Behavior

- Filters sync to URL query string (shareable).
- Active filter count badge on filter icon mobile.
- **Clear all** resets to role default view.

---

## 8. Saved Views

### Anatomy

Dropdown adjacent to filter bar: `View: All farmers ▾` → list of saved views + "Save current filters…"

### Saved view record

- Name, icon, filter JSON, sort, column visibility, density, creator, shared flag.

### States

- **Default view:** Star icon; auto-applied on entry.
- **Modified:** Dot on view name; prompt to save or discard on navigate away.

### Usage

Per-user locally Phase 1; sync to backend `user_preferences` Phase 2+.

---

## 9. KPI Cards

### Anatomy

```text
┌─────────────────────────┐
│ Total Procurement Value │  label-sm, onSurfaceVariant
│ ₹12,34,567              │  display-sm or heading-lg, tabular
│ ↑ 8.2% vs last week     │  body-sm, success/error color
│ ▁▂▃▅▇ sparkline         │  optional 7-day sparkline
└─────────────────────────┘
```

### Variants

| Variant | Usage |
|---------|-------|
| Metric | Single value + delta |
| Comparison | Two values side by side (Advance vs Final pay) |
| Progress | Bar toward target (collection rate RENT-004) |
| Alert | Warning border when threshold exceeded (moisture) |

### KPI mapping

Align IDs with [kpi_definitions.md](../reporting/kpi_definitions.md): PROC-002, PAY-005, PNL-010, VEH-001, etc.

### States

- Loading: gray shimmer block for value.
- Error: `--` with retry icon.
- Stale: clock icon if data > 5 min old (cached).

---

## 10. Charts

Built with `fl_chart` or similar; follow chart color series from design system.

### Line chart

- **Use:** Daily procurement volume (PROC-001), payment trend (PAY-001).
- **Anatomy:** X = date, Y = value, tooltip on hover, crosshair on desktop.
- **Mobile:** Simplify to 7-day window; horizontal scroll for 30-day.

### Bar chart

- **Use:** Village share (PROC-012), expense by category (EXP-003).
- **Variant:** Horizontal bars for long Telugu village names.

### Donut chart

- **Use:** Crop mix (PROC-011), payment mode mix (PAY-009).
- **Center label:** Total value.
- **Legend:** Right desktop, bottom mobile.
- **Accessibility:** Table alternate hidden for SR (see ACCESSIBILITY doc).

### Sparkline

- Embedded in KPI card footer; no axes; 48 × 24 px.
- Color follows delta (green up, red down — configurable for "lower is better" metrics).

---

## 11. Activity Timeline

### Anatomy

Vertical timeline with nodes:

```text
● 12 Jun 2026 10:42  Procurement PR-2026-0142 confirmed
│                    by Venkat · 45 qtl paddy · ₹1,12,500
● 12 Jun 2026 09:15  Document crop_bill uploaded
│                    Weighment slip · OCR pending
○ 11 Jun 2026 16:00  Farmer profile updated
                     Phone number changed
```

### Variants

- **Profile activity tab:** All entity events + linked entities.
- **Collection workflow:** Horizontal step timeline (see §12 workflow).
- **Audit mode:** Expand row → JSON diff (admin only).

### Node types

| Type | Icon color |
|------|------------|
| Create | info |
| Confirm / complete | success |
| Payment | primary |
| Document | secondary |
| Reversal | error muted |
| System | onSurfaceVariant |

---

## 12. Drawer Panels & Slide-over Forms

### Drawer (right, 480 px)

- **Use:** Quick view procurement, edit farmer field, document metadata.
- **Header:** Entity ID mono + status badge + close.
- **Body:** Scrollable sections.
- **Footer:** Sticky actions (Cancel, Save).

### Full slide-over (collection workflow)

- 600 px desktop; 100% mobile.
- Timeline header fixed; step content scrolls.

### States

- **Dirty form:** Confirm on close.
- **Submitting:** Disable footer; linear progress top edge.
- **Success:** Toast + auto-close or navigate to detail.

---

## 13. Collection Workflow Timeline (composite)

Not a wizard — a **status rail** with editable steps:

| Step | Label | Primary action |
|------|-------|----------------|
| 1 Entry | Farmer & crop | Select farmer, village, crop type |
| 2 Quality | Moisture & deductions | Moisture %, deduction lines |
| 3 Weight | Weighment | Bags, gross/net kg, rate/quintal |
| 4 Payment approval | Review & confirm | Summary, documents, confirm → ledger |

Steps can be revisited; completed steps show checkmark. Current step highlighted with `primary` ring.

---

## 14. Empty States

### Anatomy

```text
        [illustration]
   No procurements in Draft
   Start a collection entry to record today's paddy intake.
        [Start collection entry]
```

### Variants by module

| Module | Message tone |
|--------|--------------|
| Farmers | Onboard first Bhairkhanpally farmer |
| Payments | All caught up — no pending settlements |
| Documents | Drop weighment slips here |
| Search | Refine query or check spelling (Telugu names) |

Never show empty table with zero column headers — always branded empty component.

---

## 15. Skeleton Loaders

| Pattern | Structure |
|---------|-----------|
| KPI row | 4 rounded rects, pulse animation |
| Table | Header + 8 rows of 3 cell bars |
| Profile header | Circle + 2 lines + 4 metric blocks |
| Kanban | 3 columns × 3 card skeletons |
| Timeline | 4 nodes with alternating line |

Use `Shimmer` with `surfaceContainerHigh` → `surface` gradient; 1.2 s period.

---

## 16. Bulk Action Bar

### Anatomy

Appears when table selection ≥ 1:

```text
┌──────────────────────────────────────────────────────────────┐
│ 12 selected   [Export CSV]  [Assign village]  [Archive]  ✕   │
└──────────────────────────────────────────────────────────────┘
```

- Fixed bottom desktop (above content padding); sticky bottom mobile.
- `✕` clears selection.
- Destructive actions use `error` color + confirmation dialog.

### Rules

- Max bulk size 100 rows; warn if more on current page.
- Export respects current filters + selection.

---

## 17. Toast / Snackbar Patterns

| Type | Duration | Icon |
|------|----------|------|
| Success | 4 s | check_circle |
| Error | 8 s or persistent | error — include action "Retry" |
| Warning | 6 s | warning |
| Info | 4 s | info |

**Position:** Bottom-right desktop (stack max 3); bottom center mobile.

**Financial success:** "Procurement PR-2026-0142 confirmed · ₹1,12,500 posted to ledger" — include entity link action.

**Undo:** Only for non-financial deletes (document archive) — 5 s undo window.

---

## 18. Procurement Kanban Card (domain component)

```text
┌─────────────────────────┐
│ PR-2026-0142      Draft │
│ Rajesh Kumar            │
│ Paddy · 45 qtl          │
│ ₹1,12,500               │
│ Bhairkhanpally    ⋮     │
└─────────────────────────┘
```

Columns: **Draft · Confirmed · Dispatched · Delivered · Closed**

Note: API status enum is `draft | confirmed | cancelled` (P2). UI columns **Dispatched / Delivered / Closed** are operational extensions — store in `metadata.dispatch_status` or future API; show badge "UI-only" in dev mode.

---

## Component Checklist for Implementation

| Priority | Component |
|----------|-----------|
| P0 | App shell, sidebar, top nav, data table, skeleton, empty, toast |
| P1 | Command palette, smart filters, KPI cards, slide-over |
| P2 | Collection timeline, Kanban card, activity timeline, bulk bar |
| P3 | Charts, saved views, dispatch map pin card |

---

## Cross-References

- Wireframes: [WIREFRAMES.md](./WIREFRAMES.md)
- Component trees: [COMPONENT_TREE.md](./COMPONENT_TREE.md)
