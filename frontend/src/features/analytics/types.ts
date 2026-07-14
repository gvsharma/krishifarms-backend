export type AnalyticsModuleStatus = "live" | "scaffold";
export type KpiStatus = "live" | "unavailable" | "coming_soon" | "estimate";

export interface DrillLink {
  href: string;
  label?: string | null;
}

export interface KpiCard {
  id: string;
  label: string;
  label_te?: string | null;
  value: string | number | null;
  unit?: string | null;
  format: string;
  delta_pct?: number | null;
  status: KpiStatus;
  note?: string | null;
  drill?: DrillLink | null;
}

export interface SeriesPoint {
  x: string;
  y: string | number;
  series?: string | null;
}

export interface TableColumn {
  key: string;
  label: string;
  format: string;
}

export interface TableRow {
  cells: Record<string, string | number | null>;
}

export interface TablePage {
  id: string;
  title: string;
  columns: TableColumn[];
  rows: TableRow[];
  total: number;
}

export interface DataAvailabilityItem {
  source: string;
  status: string;
  notes?: string | null;
}

export interface AnalyticsFilterState {
  date_from?: string | null;
  date_to?: string | null;
  village_id?: string | null;
  crop_type_id?: string | null;
  farmer_id?: string | null;
  buyer_id?: string | null;
  asset_id?: string | null;
  season?: string | null;
  preset?: string | null;
}

export interface ModuleSummary {
  module: string;
  status: AnalyticsModuleStatus;
  filters: AnalyticsFilterState;
  kpis: KpiCard[];
  series_preview: SeriesPoint[];
  tables_preview: TablePage[];
  data_availability: DataAvailabilityItem[];
  health_score?: number | null;
  health_score_method?: string | null;
  cache_hit: boolean;
  latency_ms?: number | null;
}

export interface ModuleCatalogItem {
  id: string;
  name: string;
  name_te?: string | null;
  description: string;
  status: AnalyticsModuleStatus;
  href: string;
  group: string;
  missing_sources: string[];
}

export interface AnalyticsCatalog {
  modules: ModuleCatalogItem[];
  live_count: number;
  scaffold_count: number;
  data_plane: string;
  permission: string;
}

export const LIVE_MODULE_IDS = ["executive", "operations", "procurement", "finance"] as const;
export type LiveModuleId = (typeof LIVE_MODULE_IDS)[number];

export const ALL_MODULE_IDS = [
  ...LIVE_MODULE_IDS,
  "farming",
  "vehicle",
  "village",
  "farmer",
  "buyer",
  "employee",
  "service",
  "crop-intelligence",
  "inventory",
  "ai-prediction",
  "alerts",
] as const;
