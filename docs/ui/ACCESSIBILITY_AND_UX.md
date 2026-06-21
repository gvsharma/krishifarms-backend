# Accessibility & UX Patterns — KrishiFarms CRM

**Target:** WCAG 2.1 Level AA  
**Platform:** Next.js responsive web (keyboard + screen reader + responsive)

---

## 1. WCAG 2.1 AA Targets

### 1.1 Perceivable

| Criterion | Implementation |
|-----------|----------------|
| **1.1.1 Non-text content** | All icons paired with text or `aria-label`; chart data available in table alternate |
| **1.3.1 Info and relationships** | Data tables use semantic headers; form labels always visible (not placeholder-only) |
| **1.4.3 Contrast (Minimum)** | Text ≥ 4.5:1; large text ≥ 3:1 — verify token pairs in [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md) |
| **1.4.4 Resize text** | Support browser zoom to 200% without horizontal scroll on primary flows |
| **1.4.11 Non-text contrast** | UI controls, focus rings ≥ 3:1 against adjacent colors |
| **1.4.13 Content on hover** | Tooltips dismissible, hoverable, persistent until dismissed |

### 1.2 Operable

| Criterion | Implementation |
|-----------|----------------|
| **2.1.1 Keyboard** | All actions reachable without mouse — see §2 |
| **2.1.2 No keyboard trap** | Focus trap only in modals/command palette with Esc exit |
| **2.4.3 Focus order** | DOM order matches visual order; skip link "Skip to main content" |
| **2.4.7 Focus visible** | 2 px `primary` focus ring on all interactive elements |
| **2.5.5 Target size** | Minimum 44 × 44 px touch targets on mobile |

### 1.3 Understandable

| Criterion | Implementation |
|-----------|----------------|
| **3.2.4 Consistent identification** | Same icons/labels for same actions across modules |
| **3.3.1 Error identification** | Form errors: field-level message + summary banner |
| **3.3.2 Labels or instructions** | Moisture %, rate/quintal include unit hints and valid ranges |

### 1.4 Robust

| Criterion | Implementation |
|-----------|----------------|
| **4.1.2 Name, role, value** | Semantic HTML + ARIA on custom components (Kanban, KPI cards); shadcn primitives ship accessible defaults |
| **4.1.3 Status messages** | Toasts use `role="status"` / `aria-live="polite"` (Sonner) |

---

## 2. Keyboard Navigation

### 2.1 Focus management map

| Surface | Tab order | Esc behavior |
|---------|-----------|--------------|
| App shell | Sidebar → top nav → main | — |
| Data table | Header → rows → pagination | Clear row selection |
| Slide-over | Header close → body fields → footer actions | Close if not dirty |
| Command palette | Search → results | Close palette |
| Dialog | Title → content → actions | Close |
| Collection timeline | Steps not in tab order (use shortcuts) | Exit workflow confirm |

### 2.2 Skip links

First focusable element on page load:

```text
[Skip to main content]
```

Hidden until focused; jumps to `#main-content` landmark.

### 2.3 Shortcuts vs screen readers

- Single-key shortcuts (`N`, `J`, `K`) disabled when focus in text field.
- Provide `?` help modal listing all shortcuts.
- Avoid single-character shortcuts without modifier where possible on web (conflict with SR) — use `G` chord pattern for navigation.

---

## 3. Screen Reader Labels — Data Tables

### 3.1 Table semantics

```text
role: table
  caption: "Farmers in Bhairkhanpally, 142 total"
  rowgroup (header)
    row: column headers with sort state announced
  rowgroup (body)
    row: selectable, announced "Row 1 of 20"
```

### 3.2 Cell announcements

| Cell type | SR label pattern |
|-----------|------------------|
| Farmer name | "Rajesh Kumar, farmer code F R M 0042, village Bhairkhanpally" |
| Outstanding | "Outstanding 45,200 rupees" (locale-aware) |
| Status badge | "Status: Active" |
| Sortable header | "Last procurement, sortable, sorted descending" |
| Row selected | "Selected" appended on checkbox toggle |

### 3.3 Live regions

| Event | Announcement |
|-------|--------------|
| Sort applied | "Sorted by outstanding, highest first" |
| Filter applied | "Filter applied: outstanding greater than zero, 28 results" |
| Bulk select | "12 farmers selected" |
| Export complete | "CSV export downloaded" |

### 3.4 Chart alternatives

Every chart widget includes visually hidden `<table summary="...">` or "View data table" toggle exposing the same data for SR and keyboard users.

---

## 4. Mobile Responsive Breakpoints

Behavior aligned with [DESIGN_SYSTEM.md § Breakpoints](./DESIGN_SYSTEM.md#41-breakpoints):

| Breakpoint | Navigation | Tables | Dashboard |
|------------|------------|--------|-----------|
| **< 600 px** | Bottom nav (5 primary) + hamburger overflow | Card lists replace tables; sticky filter sheet | Single column KPIs |
| **600–1024 px** | Collapsed sidebar | Horizontal scroll tables with sticky first column | 2-column KPI grid |
| **≥ 1024 px** | Expanded sidebar | Full data table | 4-column KPI grid |

### 4.1 Touch UX

- Swipe on collection timeline steps (optional) with button alternative.
- Pull-to-refresh on list screens (mobile web).
- No hover-only actions — all actions in `⋮` menu or visible buttons.

### 4.2 Telugu on mobile

- Ensure Noto Sans Telugu renders at ≥ 16 px body to prevent iOS zoom-on-focus.

---

## 5. Export CSV Patterns

### 5.1 Scope

| Export type | Contents |
|-------------|----------|
| **Current view** | Visible columns + active filters |
| **Selection** | Selected rows only (bulk bar) |
| **Full report** | Reports module — async job Phase 2b |

### 5.2 UX flow

1. User clicks **Export CSV** (bulk bar or list header).
2. Dialog: confirm scope, row count, estimated size.
3. Generate client-side for ≤ 1000 rows; server-side job above threshold (future).
4. Toast: "Export ready — 142 farmers" with download link.
5. Filename: `krishifarms-farmers-2026-06-21.csv`

### 5.3 CSV format

- UTF-8 with BOM for Excel Telugu compatibility.
- Headers in user's UI language.
- Amounts as plain decimal strings (no ₹ symbol in cells).
- Dates ISO 8601.

### 5.4 Permissions

Export requires same read permission as list (`farmers:read`, etc.). Audit log entry on bulk export (Phase 2b).

---

## 6. Bulk Actions Patterns

### 6.1 Selection model

- Checkbox column always first.
- Shift+click range select on desktop.
- Select all page vs select all matching filter (explicit second step for > page size).

### 6.2 Action confirmation

| Action severity | Confirmation |
|-----------------|--------------|
| Export | Light dialog with count |
| Assign village | Medium — show preview list |
| Archive / cancel | Strong — type reason or entity count confirm |
| Financial | **Never bulk** confirm procurements/payments in v1 |

### 6.3 Progress

For batch operations > 10 items:

```text
Processing 12 of 45...
[████████░░░░░░░░] Cancel
```

Partial failure summary: "10 succeeded, 2 failed" with downloadable error log.

---

## 7. Color & Motion Accessibility

- Never convey status by color alone — always icon + text label.
- `MediaQuery.disableAnimations` → instant state changes, no slide animations.
- High contrast mode (future): optional theme bumping border weight.

---

## 8. Forms & Financial UX

| Pattern | Accessibility + trust |
|---------|----------------------|
| Amount entry | `Decimal` keyboard; announce formatted value on blur |
| Confirm procurement | Summary read by SR before focus on Confirm button |
| Idempotency | Disable submit after click; announce "Processing payment" |
| Reversal | Destructive styling + reason field required |
| Masked bank accounts | SR reads "Account ending in 4 5 6 7" not full number |

---

## 9. Localization Accessibility

- `lang` attribute on `html` matches app locale (`en` / `te`).
- Mixed-language content: mark Telugu name with `lang="te"` semantics.
- Number reading follows locale (`en_IN` grouping).

---

## 10. Testing Checklist

| Test | Tool / method |
|------|---------------|
| Keyboard-only pass | Manual — all P0 flows |
| Screen reader | VoiceOver (Safari), NVDA (Chrome) |
| Contrast | Figma/token audit + Playwright screenshot regression |
| Zoom 200% | Browser zoom on collection workflow |
| Reduced motion | OS setting + verify |
| CSV Telugu | Open export in Excel with BOM |

---

## Cross-References

- Components: [COMPONENT_LIBRARY.md](./COMPONENT_LIBRARY.md)
- Keyboard map: [NAVIGATION_AND_FLOWS.md § Shortcuts](./NAVIGATION_AND_FLOWS.md#7-keyboard-shortcuts)
- Design tokens: [DESIGN_SYSTEM.md](./DESIGN_SYSTEM.md)
