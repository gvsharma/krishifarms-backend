# Screen Specifications — KrishiFarms CRM

Per-screen specs: purpose, persona, layout, components, data sources, interactions, states, mobile.

**API phase legend:** P1 live · P2 OpenAPI · P3+ later phases

---

## Implementation Phase Roadmap

| Priority | Screens | Phase | Rationale |
|----------|---------|-------|-----------|
| **P0** | Login, App shell, Settings (users, villages, crops), Documents library, Audit log | P1 | Backend live; establishes shell |
| **P1** | Executive dashboard shell, Activity feed | P1 stub | CEO landing; grow into KPIs |
| **P2** | Farmer list/profile, Collection workflow, Procurement board/table, Payments dashboard | P2 | Core procurement revenue path |
| **P3** | Expenses, Collections, Vendor payments, Expense dashboard | P3 | Finance completion |
| **P4** | Farms, Workforce, Attendance, Work orders | P4 | Operations |
| **P5** | Fleet, Rentals, Global search, OCR review, Dispatch map | P5 | Fleet + AR + AI |

---

## 1. Login Screen

| Attribute | Detail |
|-----------|--------|
| **Route** | `/login` |
| **Persona** | All |
| **Purpose** | Authenticate org user |

**Layout:** Centered card on `surface` background; org logo; email/password; login button; language toggle.

**Components:** `LoginForm`, `PasswordField`, `LanguageToggle`, `LoginButton`.

**Data sources:** `POST /auth/login` (P1) · `POST /auth/refresh` (P1)

**Interactions:** Submit → store tokens → redirect to role home. Show validation errors inline.

**States:** Loading button · Invalid credentials error banner · Network error retry.

**Mobile:** Full-width card, 16 px margin.

---

## 2. Executive Dashboard

| Attribute | Detail |
|-----------|--------|
| **Route** | `/dashboard/executive` |
| **Persona** | Super Admin, CEO view |
| **Purpose** | Org-wide cash, procurement, payment health |

**Layout:** Hero net cash KPI · 4-up metric grid · 2 charts · attention panel · activity feed.

**Components:** See [COMPONENT_TREE.md § ExecutiveDashboardPage](./COMPONENT_TREE.md#2-executivedashboardpage).

**Data sources**

| Component | KPI | API | Phase |
|--------|-----|-----|-------|
| Net cash | PNL-010 | Reporting SQL / future `/dashboard/profitability` | P3+ |
| Proc volume/value | PROC-001/002 | `/dashboard/procurement` | P2+ |
| Disbursed | PAY-001 | `/dashboard/payments` | P2+ |
| Outstanding | PAY-005 | `/dashboard/payments` | P2+ |
| Activity | — | `GET /activity-feed` (P1) | P1 |
| Summary stub | — | `GET /dashboard/summary` (P1 partial) | P1 |

**Interactions:** Date/village filters persist in URL. Attention rows deep-link. KPI cards click → filtered module view.

**States:** P1 — partial data + "Phase 2 KPIs" info banner. Skeleton on load. Section-level error retry.

**Mobile:** Single column KPI stack; charts scroll horizontal.

---

## 3. Procurement Dashboard

| Attribute | Detail |
|-----------|--------|
| **Route** | `/dashboard/procurement` |
| **Persona** | Procurement Manager, Super Admin |
| **Purpose** | Intake volume, quality, deductions |

**KPIs:** PROC-001 through PROC-012.

**Data sources:** Reporting endpoints (P2+); drill-down to `/procurements/board` with filters.

**Interactions:** Crop mix slice → board filtered by crop. Village bar → farmer list filtered.

---

## 4. Payments Dashboard

| Attribute | Detail |
|-----------|--------|
| **Route** | `/dashboard/payments` |
| **Persona** | Accountant |
| **Purpose** | Disbursement, outstanding, allocation coverage |

**KPIs:** PAY-001 through PAY-012.

**Data sources:** P2+ reporting; links to `/finance/payments` and farmer ledger tabs.

---

## 5. Profitability Dashboard

| Attribute | Detail |
|-----------|--------|
| **Route** | `/dashboard/profitability` |
| **Persona** | Super Admin, Accountant |
| **Purpose** | Cash in/out, net position (PNL-*) |

**Data sources:** P3+ (`collections`, `expenses`, procurements COGS).

**Note:** PNL-011 gross margin requires future `crop_sales` — show "Coming soon" card.

---

## 6. Farm Operations Dashboard

| Attribute | Detail |
|-----------|--------|
| **Route** | `/dashboard/farm-operations` |
| **Persona** | Farm Manager |
| **Purpose** | Farms, labor, per-acre costs |

**KPIs:** FARM-001 through FARM-012. **Phase:** P4.

---

## 7. Farmer List

| Attribute | Detail |
|-----------|--------|
| **Route** | `/farmers` |
| **Persona** | Procurement Manager, Field Officer, Accountant |
| **Purpose** | Find and manage farmers |

**Layout:** Saved views + smart filters + data table + bulk bar.

**Data sources:** `GET /farmers?village_id&status&q&sort&page` (P2)

**Interactions:** Row click → profile. `N` new farmer slide-over. Export CSV. Bulk export selection.

**Empty:** "No farmers in Bhairkhanpally yet" + onboarding CTA.

**Loading:** Table skeleton 10 rows.

**Error:** Inline banner + retry.

**Mobile:** Card list; filters in bottom sheet.

**Default saved views:** Accountant → Outstanding > 0; Field Officer → My village active.

---

## 8. Farmer Profile 360

| Attribute | Detail |
|-----------|--------|
| **Route** | `/farmers/:id/:tab` |
| **Persona** | All operational roles (tab subset varies) |
| **Purpose** | Single farmer operational hub |

**Tabs & data sources**

| Tab | API endpoints | Phase |
|-----|---------------|-------|
| Overview | `GET /farmers/{id}`, recent procurements | P2 |
| Procurements | `GET /procurements?farmer_id=` | P2 |
| Ledger | `GET /farmers/{id}/ledger` | P2 |
| Land & Crops | `GET .../land-parcels`, `.../crop-history` | P2 |
| Documents | `GET /documents?entity_type=farmer&entity_id=` | P1 |
| Activity | Audit + feed aggregation | P1/P2 |
| Banking | `GET/POST .../bank-accounts` | P2 |

**Interactions:** Record payment → allocation drawer. Start collection → workflow with farmer pre-filled. Documents upload + link.

**States:** 404 farmer not found page. Tab-level skeleton. Ledger empty: "No ledger entries yet."

**Mobile:** Horizontal scrolling tabs; metrics strip 2×2.

**Role visibility:** Field Officer — no banking edit if policy restricted; Accountant — full ledger/banking.

---

## 9. Farmer Onboarding Queue

| Attribute | Detail |
|-----------|--------|
| **Route** | `/farmers/onboarding` |
| **Persona** | Field Officer |
| **Purpose** | Duplicate review, incomplete profiles |

**Data sources:** `GET /farmers?status=draft` or client-side queue (P2).

**Phase:** P2.

---

## 10. Collection Entry Workflow

| Attribute | Detail |
|-----------|--------|
| **Route** | `/operations/collection-entry/:sessionId?` |
| **Persona** | Field Officer (primary), Procurement Manager |
| **Purpose** | Record procurement via timeline |

**Data sources**

| Step | API | Phase |
|------|-----|-------|
| Create draft | `POST /procurements` | P2 |
| Update | `PATCH /procurements/{id}?procurement_date=` | P2 |
| Deductions | `POST .../deductions` | P2 |
| Confirm | `POST .../confirm` | P2 |
| Documents | presign + register + link | P1 |

**Interactions:** Timeline navigation; save draft anytime; confirm requires permission; attach crop_bill.

**States:** Session restored from `sessionId` local storage. Conflict 409 if already confirmed.

**Mobile:** Full-screen steps; large touch targets for weight inputs.

---

## 11. Procurement Board / Table / Map

| Attribute | Detail |
|-----------|--------|
| **Route** | `/procurements/board`, `/table`, `/map` |
| **Persona** | Procurement Manager |
| **Purpose** | Pipeline visibility + dispatch |

**Data sources:** `GET /procurements?status&village_id&crop_type_id&date_from&date_to` (P2)

**Kanban columns:** Draft · Confirmed · Dispatched · Delivered · Closed (latter three operational metadata until API extends).

**Map:** `GET /vehicle-trips` linked dispatches (P5).

**Interactions:** Drag card between columns (where permitted). Card → detail drawer. Filter sync URL.

**Empty columns:** Column-level empty hint, not blank.

---

## 12. Payments & Settlement

| Attribute | Detail |
|-----------|--------|
| **Route** | `/finance/payments`, `/finance/payments/:id?date=` |
| **Persona** | Accountant |
| **Purpose** | Disburse and allocate farmer payments |

**Data sources**

| Action | API | Phase |
|--------|-----|-------|
| List | `GET /farmer-payments` | P2 |
| Create | `POST /farmer-payments` + `Idempotency-Key` | P2 |
| Allocate | `POST .../allocate` | P2 |
| Reverse | `POST .../reverse` | P2 |
| Outstanding | `GET /farmers/{id}/outstanding` | P2 |

**Layout:** KPI row + segmented queue + charts (see wireframe).

**Interactions:** Allocation drawer with running total. Reverse requires reason + confirm dialog.

**States:** Unallocated tab default. Payment detail shows allocation progress bar.

---

## 13. Outstanding & Ledger (Finance module)

| Attribute | Detail |
|-----------|--------|
| **Route** | `/finance/outstanding` |
| **Persona** | Accountant |
| **Purpose** | Cross-farmer outstanding snapshot |

**KPIs:** PAY-005, PAY-006.

**Data sources:** Farmer outstanding snapshots (P2 reporting).

**Interactions:** Row → farmer profile ledger tab.

---

## 14. Collections

| Attribute | Detail |
|-----------|--------|
| **Route** | `/finance/collections` |
| **Persona** | Accountant |
| **Purpose** | Record rental/other cash in |

**Data sources:** `GET/POST /collections` (P3)

**Interactions:** Link UPI screenshot document on create.

---

## 15. Expenses

| Attribute | Detail |
|-----------|--------|
| **Route** | `/finance/expenses` |
| **Persona** | Accountant, Farm Manager |
| **Purpose** | Operating expense tracking |

**Data sources:** `GET/POST /expenses`, `GET /expense-categories` (categories P1)

**KPIs:** EXP-* on expense dashboard `/dashboard/expenses` (P3).

---

## 16. Vendor Payments

| Attribute | Detail |
|-----------|--------|
| **Route** | `/finance/vendor-payments` |
| **Persona** | Accountant |
| **Purpose** | Non-farmer outbound payments |

**Data sources:** `GET/POST /payments` (P3)

---

## 17. Rental Collections (AR)

| Attribute | Detail |
|-----------|--------|
| **Route** | `/rentals/pending-collections` |
| **Persona** | Accountant, Farm Manager |
| **Purpose** | AR on rental agreements |

**Data sources:** `GET /rental-agreements/pending-collections` (P5)

**KPIs:** RENT-003, RENT-012.

---

## 18. Fleet Overview & Vehicle Trips

| Attribute | Detail |
|-----------|--------|
| **Route** | `/fleet/overview`, `/fleet/trips` |
| **Persona** | Farm Manager, Field Officer |
| **Purpose** | Trip logging, utilization |

**Data sources:** `GET/POST /vehicle-trips?trip_date`, `GET /assets` (P5)

**KPIs:** VEH-001 through VEH-012.

**Interactions:** New trip slide-over; link trip to procurement dispatch.

**Mobile:** Simplified trip form for field logging.

---

## 19. Assets & Maintenance

| Attribute | Detail |
|-----------|--------|
| **Route** | `/fleet/assets`, `/fleet/assets/:id` |
| **Persona** | Farm Manager |
| **Purpose** | Asset registry, maintenance records |

**Data sources:** `GET/POST /assets`, `.../maintenance-records`, `.../usage-logs` (P5)

---

## 20. Workforce — Workers, Work Orders, Attendance

| Routes | `/workforce/workers`, `/work-orders`, `/attendance` |
| **Persona** | Farm Manager, Supervisor |
| **Phase** | P4 |

**Data sources:** `/workers`, `/work-orders`, `/attendance` per API_CONTRACT.

**KPIs:** WRK-* on `/dashboard/workforce`.

**Interactions:** Complete work order with photo documents. Attendance calendar view.

---

## 21. Rentals — Agreements & Customers

| Routes | `/rentals/agreements`, `/rentals/customers` |
| **Phase** | P5 |

**KPIs:** RENT-* on `/dashboard/rentals`.

---

## 22. Farms — List, Activities, Leases

| Routes | `/farms`, `/farms/:id` |
| **Phase** | P4 |

**Data sources:** `/farms`, `/farms/{id}/activities`

---

## 23. Documents Library

| Attribute | Detail |
|-----------|--------|
| **Route** | `/documents` |
| **Persona** | All (with `documents:read`) |
| **Purpose** | Org document hub |

**Data sources (P1):** `GET /documents`, presign upload, register, link, download-url

**Interactions:** Upload queue, filter by type/OCR/tags, preview drawer, link to entity.

**States:** Empty upload zone. OCR pending chip. Archive soft-delete.

---

## 24. OCR Review

| Attribute | Detail |
|-----------|--------|
| **Route** | `/documents/ocr-review` |
| **Phase** | P5 |
| **Purpose** | Verify OCR extractions for weighment slips |

**Data sources:** `GET .../ocr/result`, `POST .../ocr/verify`

---

## 25. Reports & Export Center

| Attribute | Detail |
|-----------|--------|
| **Route** | `/reports`, `/reports/exports` |
| **Phase** | P2+ |
| **Purpose** | Saved reports, scheduled CSV exports |

---

## 26. Settings — Organization

| Route | `/settings/organization` |
| **Phase** | P1 (read-only org from JWT context) |

---

## 27. Settings — Users & Roles

| Route | `/settings/users`, `/settings/roles` |
| **Data sources:** `GET/POST/PATCH /users`, `/roles` (P1) |
| **Persona** | Super Admin only |

---

## 28. Settings — Master Data

| Routes | `/settings/villages`, `/settings/crop-types`, `/settings/expense-categories` |
| **Data sources (P1):** `/villages`, `/crop-types`, `/expense-categories` |
| **Persona** | Super Admin, Manager (read/create per RBAC) |

**Note:** Seed includes Bhairkhanpally village, Paddy/Corn crop types.

---

## 29. Settings — Audit Log & Activity

| Routes | `/settings/audit`, `/activity` |
| **Data sources (P1):** `GET /audit-logs`, `GET /activity-feed` |
| **Persona** | Super Admin, Manager (read) |

**Layout:** Filterable table + detail drawer with JSON diff.

---

## 30. Global Search Overlay

| Attribute | Detail |
|-----------|--------|
| **Trigger** | ⌘K, `/` |
| **Phase** | P1 navigation only → P5 full `GET /search` |
| **Persona** | All |

See [NAVIGATION_AND_FLOWS.md § Global Search](./NAVIGATION_AND_FLOWS.md#9-global-search-behavior).

---

## 31. Forbidden / Not Found

| Routes | `/forbidden`, `/not-found` |
| **Purpose** | RBAC denial, invalid deep links |

---

## Cross-Screen Patterns

| Pattern | Application |
|---------|-------------|
| Slide-over detail | Procurement, payment, document |
| Timeline | Collection workflow, activity tabs |
| Saved views | All list screens |
| Idempotency | Payment/procurement POST |
| Partition date in URL | Procurement, farmer payment, trip detail |
| Bilingual display | All farmer-facing names, villages, crops |

---

## Cross-References

- Wireframes: [WIREFRAMES.md](./WIREFRAMES.md)
- IA: [INFORMATION_ARCHITECTURE.md](./INFORMATION_ARCHITECTURE.md)
- API: [API_CONTRACT.md](../api/API_CONTRACT.md)
- KPIs: [kpi_definitions.md](../reporting/kpi_definitions.md)
