# Component Tree — KrishiFarms CRM

React component hierarchy using tree notation: `Page → Layout → Sections → Components`.

Naming convention: `Krishi` prefix for design-system components; feature components live under `features/<module>/components/`.

---

## 1. App Root

```text
RootLayout (app/layout.tsx)
├── Providers (client)
│   ├── QueryClientProvider (TanStack Query)
│   ├── ThemeProvider (next-themes)
│   └── NextIntlClientProvider
└── children
    └── AuthGate
        ├── LoginPage
        └── AppShell (app/(app)/layout.tsx)
            ├── KrishiTopNav
            ├── KrishiSidebar | KrishiBottomNav (responsive)
            ├── KrishiBreadcrumbs
            └── {children} — feature page
```

---

## 2. ExecutiveDashboardPage

Route: `/dashboard/executive`

```text
ExecutiveDashboardPage
└── KrishiPageLayout
    ├── DashboardHeaderSection
    │   ├── PageTitle ("Executive Dashboard")
    │   └── DashboardFilterBar
    │       ├── DateRangePicker
    │       ├── VillageMultiSelect
    │       └── CropTypeSelect
    ├── HeroKpiSection
    │   └── NetCashKpiCard (PNL-010)
    │       ├── KpiLabel
    │       ├── KpiValue (tabular ₹)
    │       ├── KpiDeltaChip
    │       └── SparklineChart
    ├── KpiGridSection (responsive CSS grid)
    │   ├── KpiCard (PROC-001 volume)
    │   ├── KpiCard (PROC-002 value)
    │   ├── KpiCard (PAY-001 disbursed)
    │   └── KpiCard (PAY-005 outstanding)
    ├── ChartsRowSection
    │   ├── CashFlowLineChart
    │   └── CropMixDonutChart
    ├── AttentionPanelSection
    │   └── AttentionListTile × n
    │       ├── StatusIcon
    │       ├── Message
    │       └── CtaLinkButton
    └── RecentActivitySection
        └── ActivityTimeline (compact)
```

**Data:** `useExecutiveDashboard(dateRange, filters)` — TanStack Query hook aggregating reporting API / stub.

---

## 3. FarmerListPage

Route: `/farmers`

```text
FarmerListPage
└── KrishiPageLayout
    ├── ListPageHeader
    │   ├── PageTitle
    │   └── PrimaryButton ("Add farmer")
    ├── SavedViewToolbar
    │   ├── SavedViewDropdown
    │   ├── KrishiSearchBar (module scope)
    │   └── SaveViewButton
    ├── SmartFilterBar
    │   ├── VillageFilterChip
    │   ├── CropFilterChip
    │   ├── OutstandingFilterChip
    │   ├── StatusFilterChip
    │   └── ClearFiltersButton
    ├── FarmerDataTable | FarmerListSkeleton
    │   ├── SelectAllCheckbox
    │   ├── FarmerTableRow × n
    │   │   ├── RowCheckbox
    │   │   ├── FarmerAvatarCell
    │   │   ├── FarmerNameCell (bilingual)
    │   │   ├── VillageCell
    │   │   ├── OutstandingCell (₹)
    │   │   ├── LastProcurementCell
    │   │   ├── StatusBadge
    │   │   └── RowActionsMenu
    │   └── TablePaginationBar
    └── BulkActionBar (visible if selection > 0)
        ├── SelectionCount
        ├── ExportCsvButton
        └── SecondaryBulkActions
```

---

## 4. FarmerProfilePage

Route: `/farmers/:id/:tab`

```text
FarmerProfilePage
└── KrishiPageLayout (fullWidth header)
    ├── ProfileHeaderSection
    │   ├── BackLinkBreadcrumb
    │   ├── ProfileActionsBar
    │   │   ├── RecordPaymentButton
    │   │   └── OverflowMenu
    │   ├── FarmerIdentityRow
    │   │   ├── FarmerAvatar (large)
    │   │   ├── FarmerNameBlock (en + te)
    │   │   └── FarmerMetaChips (village, phone, status)
    │   └── MetricsStrip
    │       ├── MetricTile (outstanding)
    │       ├── MetricTile (total proc volume)
    │       ├── MetricTile (ytd paid)
    │       └── MetricTile (last visit)
    ├── ProfileTabBar (scrollable)
    │   └── Tab × 7
    └── ProfileTabPanel (active tab content)
        ├── OverviewTab → OverviewTabContent
        ├── ProcurementsTab → ProcurementsTabContent
        ├── LedgerTab → LedgerTabContent
        ├── LandCropsTab → LandCropsTabContent
        ├── DocumentsTab → DocumentsTabContent
        ├── ActivityTab → ActivityTabContent
        └── BankingTab → BankingTabContent
```

### 4.1 OverviewTabContent

```text
OverviewTabContent
└── TwoColumnLayout (single on mobile)
    ├── LeftColumn
    │   ├── ContactInfoCard
    │   ├── RecentProcurementsCard
    │   │   └── MiniProcurementTable
    │   └── LandSummaryCard
    └── RightColumn
        └── QuickActionsCard
            ├── StartCollectionButton
            ├── UploadDocumentButton
            └── ViewOutstandingButton
```

### 4.2 LedgerTabContent

```text
LedgerTabContent
└── Column
    ├── LedgerSummaryBar (opening/closing balance)
    ├── LedgerFilterBar (date range, entry type)
    └── LedgerDataTable
        └── LedgerRow
            ├── EntryDateCell
            ├── EntryTypeBadge
            ├── ReferenceLink (PR-/FP-)
            ├── DebitCell | CreditCell
            ├── BalanceCell
            └── ReversalIndicator (if reversal_of_id)
```

### 4.3 DocumentsTabContent

```text
DocumentsTabContent
└── Column
    ├── DocumentUploadDropzone
    ├── DocumentFilterChips (type, OCR status)
    └── DocumentGrid
        └── DocumentCard
            ├── ThumbnailPreview
            ├── DocumentTypeBadge
            ├── OcrStatusChip
            └── LinkCountBadge
```

---

## 5. CollectionWorkflowPage

Route: `/operations/collection-entry/:sessionId?`

```text
CollectionWorkflowPage
└── FullHeightSlideLayout
    ├── WorkflowHeader
    │   ├── PageTitle ("Collection Entry")
    │   └── SaveDraftButton
    ├── CollectionTimelineRail (horizontal)
    │   └── TimelineStep × 4
    │       ├── StepIndicator (complete|current|pending)
    │       └── StepLabel
    ├── WorkflowStepContent (indexed panel)
    │   ├── EntryStepPanel
    │   │   ├── FarmerSearchSelect
    │   │   ├── VillageSelect (auto from farmer)
    │   │   └── CropTypeSelect
    │   ├── QualityStepPanel
    │   │   ├── MoistureInput
    │   │   └── DeductionLinesEditor
    │   ├── WeightStepPanel
    │   │   ├── WeighmentForm
    │   │   ├── LiveCalculationPanel
    │   │   └── AttachmentUploader
    │   └── ApprovalStepPanel
    │       ├── ReadOnlySummaryCard
    │       ├── LinkedDocumentsList
    │       └── ConfirmProcurementButton
    └── WorkflowFooter
        ├── BackStepButton
        └── NextStepButton | ConfirmButton
```

---

## 6. ProcurementBoardPage

Route: `/procurements/board`

```text
ProcurementBoardPage
└── KrishiPageLayout
    ├── BoardHeader
    │   ├── ViewToggle (Board | Table | Map)
    │   ├── FilterBar
    │   └── NewCollectionButton
    └── ViewPanel (conditional render)
        ├── KanbanView
        │   └── KanbanBoard
        │       └── KanbanColumn × 5
        │           ├── ColumnHeader (status + count)
        │           └── ProcurementKanbanCard × n
        │               ├── ProcurementIdBadge
        │               ├── FarmerNameLink
        │               ├── CropWeightSummary
        │               ├── AmountLabel
        │               └── CardMenu
        ├── ProcurementTableView
        │   └── ProcurementDataTable
        └── DispatchMapView
            ├── TripMap
            └── ActiveDispatchList
```

**Slide-over on card click:**

```text
ProcurementDetailSheet (shadcn Sheet)
├── SheetHeader (PR-id, status)
├── AmountBreakdownSection
├── DeductionListSection
├── LinkedDocumentsSection
├── LinkedTripSection (if dispatched)
└── SheetFooter (Confirm | Cancel | Dispatch)
```

---

## 7. PaymentsDashboardPage

Route: `/finance/payments`

```text
PaymentsDashboardPage
└── KrishiPageLayout
    ├── PaymentsKpiGrid
    ├── SegmentedControl (Unallocated | Outstanding | Completed | Reversed)
    ├── PrimaryActionBar (+ Record payment)
    ├── SettlementQueueList
    │   └── PaymentQueueTile × n
    └── ChartsRow
        ├── PaymentModeDonut
        └── OutstandingFarmersBarChart
```

**Allocation slide-over:**

```text
PaymentAllocationSheet
├── PaymentSummaryHeader
├── OutstandingProcurementsChecklist
├── AllocationAmountInputs
├── RunningTotalFooter
└── SubmitAllocationButton
```

---

## 8. FleetOverviewPage

Route: `/fleet/overview`

```text
FleetOverviewPage
└── KrishiPageLayout
    ├── FleetKpiGrid (VEH-001..004)
    ├── AssetCardList
    │   └── AssetCard × n
    │       ├── AssetCategoryIcon
    │       ├── UtilizationSparkline
    │       └── MaintenanceDueBadge
    └── RecentTripsTable
```

---

## 9. CommandPalette

Global overlay — not a route (`CommandDialog` from shadcn/cmdk).

```text
CommandPalette
└── CommandDialog
    ├── CommandInput (search)
    ├── CommandList
    │   ├── CommandGroup ("RECENT" | "ACTIONS" | …)
    │   └── CommandItem × n
    │       ├── ResultIcon
    │       ├── PrimaryLabel
    │       ├── SecondaryMeta
    │       └── ShortcutHint
    └── PaletteFooterHints
```

---

## 10. DocumentsLibraryPage (P1)

Route: `/documents`

```text
DocumentsLibraryPage
└── KrishiPageLayout
    ├── UploadActionBar
    ├── DocumentSmartFilters
    ├── DocumentDataTable | DocumentGridToggle
    └── DocumentPreviewSheet
        ├── PreviewPane (image/pdf)
        ├── MetadataForm
        ├── TagsEditor
        ├── EntityLinksList
        └── OcrResultPanel (P5)
```

---

## 11. Settings Pages (P1)

```text
SettingsLayout
└── flex row
    ├── SettingsNavList
    └── SettingsContentArea
        ├── UsersListPage
        ├── VillagesMasterPage
        ├── CropTypesMasterPage
        ├── ExpenseCategoriesPage
        └── AuditLogPage
```

---

## Composition Rules

1. **KrishiPageLayout** — standard padding, max-width, scroll; never duplicate in feature pages.
2. **Sections** — semantic `<section>` groupings; one Query hook per section where possible.
3. **Sheets** — use `KrishiSlideOver` (shadcn `Sheet`) wrapper with consistent 480 px width.
4. **Loading** — swap section content with matching skeleton, not full-page spinner.
5. **Error** — `KrishiInlineError` at section level with retry callback.

---

## Cross-References

- Architecture: [FRONTEND_ARCHITECTURE.md](./FRONTEND_ARCHITECTURE.md)
- Components: [COMPONENT_LIBRARY.md](./COMPONENT_LIBRARY.md)
- Wireframes: [WIREFRAMES.md](./WIREFRAMES.md)
