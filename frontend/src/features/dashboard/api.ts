import { fetchApi } from "@/lib/api/client";

export interface DashboardSummaryCounts {
  users: number;
  villages: number;
  crop_types: number;
  documents: number;
  farmers?: number;
  procurements?: number;
  assets?: number;
  farmer_payments?: number;
  field_services?: number;
  vehicle_trips?: number;
}

export type ReportStatus = "available" | "partial" | "coming_soon";

export interface ReportCatalogItem {
  id: string;
  name: string;
  description: string;
  status: ReportStatus;
  sql_file?: string | null;
  kpi_prefix?: string | null;
  module_paths: string[];
  notes?: string | null;
}

export interface ReportCatalogResponse {
  items: ReportCatalogItem[];
  summary_endpoint: string;
  architecture_doc: string;
}

/** Fallback when `/dashboard/reports` is unavailable — matches backend registry. */
export const FALLBACK_REPORT_CATALOG: ReportCatalogItem[] = [
  {
    id: "vehicle_utilization",
    name: "Vehicle Utilization",
    description: "Trips, distance, fuel efficiency, and fleet utilization rate.",
    status: "partial",
    sql_file: "docs/reporting/sql/04_vehicle_utilization.sql",
    kpi_prefix: "VEH",
    module_paths: ["/vehicles", "/field-services"],
    notes: "Assets + vehicle-trips APIs live; dedicated utilization KPI endpoint missing.",
  },
  {
    id: "diesel_expenses",
    name: "Diesel Expenses",
    description: "Fuel liters/cost from trips and field-service diesel amounts.",
    status: "partial",
    sql_file: "docs/reporting/sql/06_expense.sql",
    kpi_prefix: "EXP",
    module_paths: ["/field-services", "/vehicles", "/expenses"],
    notes: "Diesel captured on trips/field services; expense posting + rollup API missing.",
  },
  {
    id: "procurement_summary",
    name: "Procurement Summary",
    description: "Volume, value, moisture, deductions, and confirmed ticket counts.",
    status: "partial",
    sql_file: "docs/reporting/sql/01_procurement.sql",
    kpi_prefix: "PROC",
    module_paths: ["/procurement"],
    notes: "Procurement CRUD/workflow live; period KPI aggregation endpoint missing.",
  },
  {
    id: "farmer_ledger",
    name: "Farmer Ledger",
    description: "Immutable ledger credits/debits by farmer and period.",
    status: "partial",
    sql_file: "docs/reporting/sql/02_farmer_payments.sql",
    kpi_prefix: "PAY",
    module_paths: ["/farmers", "/payments", "/procurement"],
    notes: "Ledger posts on confirm/pay; farmer-level ledger report endpoint missing.",
  },
  {
    id: "outstanding_payments",
    name: "Outstanding Payments",
    description: "Farmer outstanding balances and unallocated payment amounts.",
    status: "partial",
    sql_file: "docs/reporting/sql/02_farmer_payments.sql",
    kpi_prefix: "PAY",
    module_paths: ["/payments", "/farmers"],
    notes: "Payments list/create + allocate/reverse live; outstanding snapshot report missing.",
  },
  {
    id: "crop_village_procurement",
    name: "Crop / Village Wise Procurement",
    description: "Procurement mix by crop type and village share of value/volume.",
    status: "coming_soon",
    sql_file: "docs/reporting/sql/01_procurement.sql",
    kpi_prefix: "PROC",
    module_paths: ["/procurement", "/settings/villages"],
    notes: "SQL ready (PROC-011/012); no grouped report API yet.",
  },
  {
    id: "vehicle_earnings",
    name: "Vehicle Earnings",
    description: "Revenue per machine hour and trip-related earnings by asset.",
    status: "coming_soon",
    sql_file: "docs/reporting/sql/04_vehicle_utilization.sql",
    kpi_prefix: "VEH",
    module_paths: ["/vehicles", "/field-services"],
    notes: "Needs asset_usage_logs / rental revenue aggregation endpoints.",
  },
  {
    id: "supervisor_productivity",
    name: "Supervisor Productivity",
    description: "Attendance, work orders, and labor cost for farming supervisors.",
    status: "coming_soon",
    sql_file: "docs/reporting/sql/03_worker_productivity.sql",
    kpi_prefix: "WRK",
    module_paths: ["/field-services", "/workers", "/farms"],
    notes: "SQL ready; workers/work-orders report APIs not live.",
  },
];

export function fetchDashboardSummary(): Promise<DashboardSummaryCounts> {
  return fetchApi<DashboardSummaryCounts>("/dashboard/summary", {
    method: "GET",
    clientHeaders: false,
  });
}

export function fetchReportCatalog(): Promise<ReportCatalogResponse> {
  return fetchApi<ReportCatalogResponse>("/dashboard/reports", {
    method: "GET",
    clientHeaders: false,
  });
}
