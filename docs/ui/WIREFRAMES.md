# Wireframes — KrishiFarms CRM

ASCII layout wireframes for key screens. Premium SaaS density — not generic CRUD.

**Legend:** `[...]` interactive · `(...)` metadata · `===` section divider · `│║` borders

---

## 1. CEO / Executive Dashboard

Route: `/dashboard/executive` · Persona: Super Admin · KPIs: PNL-*, PROC-*, PAY-* (P2+)

```text
┌─ Top Nav ─────────────────────────────────────────────────────────────────────┐
│ KrishiFarms          [Search farmers, trips...  ⌘K]     [+]  🔔  VG ▾         │
├──────────┬────────────────────────────────────────────────────────────────────┤
│ SIDEBAR  │ Home › Executive Dashboard          [Jun 2026 ▾] [All villages ▾]  │
│          ├────────────────────────────────────────────────────────────────────┤
│ ● Home   │                                                                    │
│   Exec   │  Net Cash Position (PNL-010)                                       │
│   Proc   │  ┌─────────────────────────────────────────────────────────────┐   │
│   Pay    │  │  ₹8,45,230                                    ↑ 12.4% MoM    │   │
│ ○ Profit │  │  ▁▂▃▄▅▆▇ 30-day cash trend                                  │   │
│          │  └─────────────────────────────────────────────────────────────┘   │
│ Operations│                                                                   │
│ Finance  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │
│ ...      │  │ Proc Volume  │ │ Proc Value   │ │ Paid Farmers │ │ Outstanding│ │
│          │  │ PROC-001     │ │ PROC-002     │ │ PAY-001      │ │ PAY-005    │ │
│          │  │ 12,450 qtl   │ │ ₹32.4L       │ │ ₹18.2L       │ │ ₹4.1L      │ │
│          │  │ ↑ 5%         │ │ ↑ 3%         │ │ 142 pays     │ │ 28 farmers │ │
│          │  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │
│          │                                                                    │
│          │  ┌─ Cash In vs Out (line) ─────────┐ ┌─ Crop Mix (donut) ────────┐ │
│          │  │ Collections ───                  │ │ Paddy 68%                 │ │
│          │  │ Proc COGS ───                    │ │ Corn 32%                  │ │
│          │  └──────────────────────────────────┘ └───────────────────────────┘ │
│          │                                                                    │
│          │  ┌─ Requires Attention ──────────────────────────────────────────┐ │
│          │  │ ⚠ 12 draft procurements (PROC-009)     [Review board →]       │ │
│          │  │ ⚠ ₹2.1L unallocated payments (PAY-008) [Settle →]           │ │
│          │  │ ⚠ 3 trips idle > 2 days (VEH-008)      [Fleet →]            │ │
│          │  └─────────────────────────────────────────────────────────────┘ │
│          │                                                                    │
│          │  ┌─ Recent Activity (timeline) ──────────────────────────────────┐ │
│          │  │ ● PR-2026-0142 confirmed · Rajesh · 45 qtl · 10 min ago     │ │
│          │  │ ● FP-2026-0088 completed · ₹50,000 · 1 hr ago               │ │
│          │  └─────────────────────────────────────────────────────────────┘ │
└──────────┴────────────────────────────────────────────────────────────────────┘
```

**P1 note:** KPI values show skeleton or stub from `GET /dashboard/summary` until Phase 2 reporting API.

---

## 2. Farmer List (Smart Filters + Saved Views)

Route: `/farmers` · P2

```text
┌─ Main ────────────────────────────────────────────────────────────────────────┐
│ Farmers                                                    [+ Add farmer]       │
│                                                                               │
│ View: [Active in season ▾]  [🔍 Search name, phone, code...]                  │
│                                                                               │
│ [Village ▾ Bhairkhanpally] [Crop ▾] [Outstanding ▾ > ₹0] [Status ▾ Active]   │
│ 4 filters active                                    [Clear] [Save view...]    │
│ ───────────────────────────────────────────────────────────────────────────── │
│ ☐  FARMER            VILLAGE         OUTSTANDING    LAST PROC      STATUS     │
│ ───────────────────────────────────────────────────────────────────────────── │
│ ☐  Rajesh Kumar      Bhairkhanpally  ₹45,200       12 Jun 2026    ● Active   │
│    FRM-0042 · 9876543210                                                      │
│ ☐  Lakshmi Devi      Bhairkhanpally  ₹0            10 Jun 2026    ● Active   │
│ ☐  Srinivas Reddy    Yellareddypet   ₹12,800       05 Jun 2026    ● Active   │
│ ...                                                                           │
│ ───────────────────────────────────────────────────────────────────────────── │
│ Showing 1–20 of 142                              [20 ▾]  ← 1 2 3 ... 8 →      │
└───────────────────────────────────────────────────────────────────────────────┘

Bulk bar (when selected):
┌───────────────────────────────────────────────────────────────────────────────┐
│ 3 selected    [Export CSV]  [Send to collection queue]              Clear ✕   │
└───────────────────────────────────────────────────────────────────────────────┘
```

**Differentiation:** Saved view "Outstanding > 0" is default for Accountant; "My village today" for Field Officer.

---

## 3. Farmer Profile 360 (7 Tabs)

Route: `/farmers/{id}/{tab}` · Stripe/Linear-style detail page · P2

```text
┌─ Profile Header ──────────────────────────────────────────────────────────────┐
│ ← Farmers    FRM-0042                                    [Record payment] [⋮]   │
│                                                                               │
│  (avatar)  Rajesh Kumar / రాజేష్ కుమార్                                        │
│            Bhairkhanpally · 9876543210 · Active                               │
│                                                                               │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐                  │
│  │ Outstanding│ │ Total proc │ │ YTD paid   │ │ Last visit │                  │
│  │ ₹45,200    │ │ 128 qtl    │ │ ₹3.2L      │ │ 12 Jun     │                  │
│  │ PAY-005    │ │ PROC-001   │ │ PAY-001    │ │            │                  │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘                  │
├───────────────────────────────────────────────────────────────────────────────┤
│ [Overview] [Procurements] [Ledger] [Land & Crops] [Documents] [Activity] [Bank]│
╞═══════════════════════════════════════════════════════════════════════════════╡
│ OVERVIEW TAB                                                                  │
│ ┌─ Contact & Identity ──────────────┐ ┌─ Quick Actions ────────────────────┐  │
│ │ Phone, alternate, address         │ │ [Start collection] [Upload doc]    │  │
│ │ Farmer code, created 2024         │ │ [View outstanding breakdown]       │  │
│ └───────────────────────────────────┘ └────────────────────────────────────┘  │
│ ┌─ Recent Procurements (mini table) ────────────────────────────────────────┐ │
│ │ PR-2026-0142 · 45 qtl Paddy · ₹1,12,500 · Confirmed                       │ │
│ │ PR-2026-0098 · 32 qtl Paddy · ₹78,400 · Confirmed                         │ │
│ └───────────────────────────────────────────────────────────────────────────┘ │
│ ┌─ Land summary ────────────────────────────────────────────────────────────┐ │
│ │ 2 parcels · 3.5 acres · Paddy current season                              │ │
│ └───────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘
```

### Tab content blocks

| Tab | Primary blocks |
|-----|----------------|
| **Overview** | Contact, quick actions, recent procurements, land summary |
| **Procurements** | Full filterable table → slide-over detail |
| **Ledger** | Immutable ledger table; debits red, credits green; reversal rows muted |
| **Land & Crops** | Parcel cards + crop history season grid |
| **Documents** | Linked docs grid; upload; OCR status chips |
| **Activity** | Unified timeline (audit + transactions) |
| **Bank** | Masked account numbers; add/edit in slide-over |

---

## 4. Collection Entry Workflow (Timeline)

Route: `/operations/collection-entry` · P2

```text
┌─ Collection Entry ──────────────────────────────────────────── [Save draft] ──┐
│                                                                               │
│   ●──────────●──────────●──────────○                                          │
│   Entry      Quality    Weight     Payment Approval                           │
│   ✓          ✓          (current)  pending                                    │
│                                                                               │
│ ═══ Step 3: Weight ═══════════════════════════════════════════════════════════│
│                                                                               │
│  Farmer: Rajesh Kumar (FRM-0042)          Crop: Paddy · Bhairkhanpally        │
│                                                                               │
│  ┌─ Weighment ─────────────────────┐  ┌─ Live calculation ────────────────┐   │
│  │ Bag count        [  90  ]       │  │ Gross        4,520 kg             │   │
│  │ Gross weight kg  [4520  ]       │  │ Deductions   − 20 kg              │   │
│  │ Net weight kg    [4500  ]       │  │ Net          4,500 kg = 45 qtl   │   │
│  │ Rate/quintal ₹   [2500  ]       │  │ Amount       ₹1,12,500            │   │
│  └──────────────────────────────────┘  └───────────────────────────────────┘   │
│                                                                               │
│  ┌─ Attachments ─────────────────────────────────────────────────────────────┐ │
│  │ [+ crop_bill photo]  weighment_slip.jpg ✓  OCR: completed              │ │
│  └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│                                        [← Quality]  [Continue to Approval →]   │
└───────────────────────────────────────────────────────────────────────────────┘
```

Step 4 Approval shows read-only summary + Confirm button (`procurements:confirm` permission).

---

## 5. Procurement — Kanban + Table + Dispatch Map

Route: `/procurements/board` · P2

### 5a Kanban view

```text
┌─ Procurements ────────────────────────────────────────────────────────────────┐
│ [Board ●] [Table] [Map]              [Jun 2026 ▾] [Village ▾] [+ Collection]  │
│                                                                               │
│ ┌─ Draft (9) ──────┐ ┌─ Confirmed ────┐ ┌─ Dispatched ─┐ ┌─ Delivered ─┐ ...  │
│ │ PR-2026-0150     │ │ PR-2026-0142   │ │ PR-2026-0130│ │ PR-2026-0120│     │
│ │ Rajesh · Paddy   │ │ 45 qtl ₹1.12L  │ │ Trip T-442  │ │ ✓ Closed    │     │
│ │ 38 qtl           │ │ Bhairkhanpally │ │ En route →  │ │             │     │
│ │ [Continue →]     │ │                │ │             │ │             │     │
│ │ PR-2026-0149     │ │ PR-2026-0140   │ │             │ │             │     │
│ │ ...              │ │ ...            │ │             │ │             │     │
│ └──────────────────┘ └────────────────┘ └─────────────┘ └─────────────┘     │
└───────────────────────────────────────────────────────────────────────────────┘
```

### 5b Dispatch map (split)

```text
┌─ Map View ────────────────────────────────────────────────────────────────────┐
│ ┌─ Map (60%) ────────────────────────┐ ┌─ Active Dispatches ────────────────┐ │
│ │     📍 Bhairkhanpally (origin)      │ │ PR-2026-0130 · Trip T-442         │ │
│ │        ╲                            │ │ Driver: Ramesh · Tractor MH-12     │ │
│ │         ╲── 🚛 en route             │ │ ETA: 45 min · [Track] [Call]      │ │
│ │              📍 Mill (dest)         │ │ PR-2026-0125 · Delivered ✓        │ │
│ └─────────────────────────────────────┘ └────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Payments Financial Dashboard

Route: `/finance/payments` · Accountant · P2

```text
┌─ Farmer Payments ─────────────────────────────────────────────────────────────┐
│                                                                               │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│ │ Disbursed   │ │ Outstanding │ │ Unallocated │ │ Avg days    │               │
│ │ PAY-001     │ │ PAY-005     │ │ PAY-008     │ │ PAY-012     │               │
│ │ ₹18.2L      │ │ ₹4.1L       │ │ ₹2.1L       │ │ 4.2 days    │               │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘               │
│                                                                               │
│ [Unallocated ●] [Outstanding] [Completed] [Reversed]     [+ Record payment]   │
│                                                                               │
│ ┌─ Settlement Queue ──────────────────────────────────────────────────────────┐ │
│ │ FP-2026-0090 · Pending · Rajesh · ₹50,000 advance · [Allocate →]         │ │
│ │ FP-2026-0088 · Completed · Lakshmi · ₹32,000 final · 100% allocated ✓    │ │
│ └───────────────────────────────────────────────────────────────────────────┘ │
│                                                                               │
│ ┌─ Payment mode mix (donut) ──────┐ ┌─ Top outstanding farmers (bar) ──────┐ │
│ │ UPI 45% · NEFT 35% · Cash 20%   │ │ Rajesh ₹45k │ Srinivas ₹12k │ ...    │ │
│ └─────────────────────────────────┘ └──────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────────┘
```

Allocation slide-over: split panel with procurement checklist + running total.

---

## 7. Vehicle Fleet Management

Route: `/fleet/overview` · P5 · VEH-* KPIs

```text
┌─ Fleet & Trips ───────────────────────────────────────────────────────────────┐
│                                                                               │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐                           │
│ │ Trips    │ │ Distance │ │ Trip cost│ │ km/L     │                           │
│ │ VEH-001  │ │ VEH-002  │ │ VEH-003  │ │ VEH-007  │                           │
│ │ 48       │ │ 1,240 km │ │ ₹84,200  │ │ 4.2      │                           │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘                           │
│                                                                               │
│ ┌─ Asset Cards ──────────────────────────────────────────────────────────────┐│
│ │ 🚜 Tractor T-01    Active   12 trips · ₹22k cost · Maint due in 5d  [→]   ││
│ │ 🚜 DCM D-02        Active   8 trips  · ₹18k cost · Fuel eff 3.8    [→]   ││
│ │ 🚜 Baler B-01      Idle     0 trips  · Rental available            [→]   ││
│ └────────────────────────────────────────────────────────────────────────────┘│
│                                                                               │
│ ┌─ Recent Trips ─────────────────────────────────────────────────────────────┐│
│ │ T-442 · 12 Jun · Bhairkhanpally → Mill · 28 km · ₹850 · Completed         ││
│ └────────────────────────────────────────────────────────────────────────────┘│
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## 8. Command Palette + Global Search Overlay

Triggered: `⌘K` or `/`

```text
                    ┌─────────────────────────────────────────┐
                    │ 🔍  pr-2026                        esc  │
                    ├─────────────────────────────────────────┤
                    │ PROCUREMENTS                            │
                    │  ↵ PR-2026-0142 · Rajesh · ₹1,12,500    │
                    │    Confirmed · Paddy · Bhairkhanpally     │
                    │  → PR-2026-0140 · Lakshmi · ₹78,400     │
                    ├─────────────────────────────────────────┤
                    │ NAVIGATION                              │
                    │  Go to Procurement Board                │
                    │  Go to Collection Entry                 │
                    ├─────────────────────────────────────────┤
                    │ ACTIONS                                 │
                    │  ⊕ New collection entry                 │
                    └─────────────────────────────────────────┘
                    ↑↓ navigate · ↵ open · ⌘↵ open in new tab
```

Dark scrim `rgba(0,0,0,0.4)` behind palette; focus trapped inside.

---

## 9. Mobile Adaptations (Farmer List example)

```text
┌─────────────────────┐
│ ☰  Farmers     [+]  │
│ [🔍 Search...]      │
│ [Filters (4)]       │
├─────────────────────┤
│ Rajesh Kumar        │
│ FRM-0042 · ₹45,200  │
│ Bhairkhanpally      │
├─────────────────────┤
│ Lakshmi Devi        │
│ ...                 │
├─────────────────────┤
│ 🏠  📋  👤  💰  ⚙   │  bottom nav
└─────────────────────┘
```

Profile tabs → horizontal scroll chip bar. Collection workflow → full-screen steps.

---

## Cross-References

- Components: [COMPONENT_LIBRARY.md](./COMPONENT_LIBRARY.md)
- Component trees: [COMPONENT_TREE.md](./COMPONENT_TREE.md)
- Screen specs: [SCREEN_SPECS.md](./SCREEN_SPECS.md)
