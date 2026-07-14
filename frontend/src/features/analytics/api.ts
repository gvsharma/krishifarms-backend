import { fetchApi, getAccessToken } from "@/lib/api/client";
import { getApiBaseUrl } from "@/lib/api/config";
import type { AnalyticsCatalog, AnalyticsFilterState, ModuleSummary } from "./types";

function toQuery(filters: AnalyticsFilterState): string {
  const search = new URLSearchParams();
  if (filters.preset) search.set("preset", filters.preset);
  if (filters.date_from) search.set("date_from", filters.date_from);
  if (filters.date_to) search.set("date_to", filters.date_to);
  if (filters.village_id) search.set("village_id", filters.village_id);
  if (filters.crop_type_id) search.set("crop_type_id", filters.crop_type_id);
  if (filters.farmer_id) search.set("farmer_id", filters.farmer_id);
  if (filters.buyer_id) search.set("buyer_id", filters.buyer_id);
  if (filters.asset_id) search.set("asset_id", filters.asset_id);
  if (filters.season) search.set("season", filters.season);
  const qs = search.toString();
  return qs ? `?${qs}` : "";
}

export function fetchAnalyticsCatalog(): Promise<AnalyticsCatalog> {
  return fetchApi<AnalyticsCatalog>("/analytics/catalog", { method: "GET", clientHeaders: false });
}

export function fetchAnalyticsSummary(
  module: string,
  filters: AnalyticsFilterState,
): Promise<ModuleSummary> {
  return fetchApi<ModuleSummary>(`/analytics/${module}/summary${toQuery(filters)}`, {
    method: "GET",
    clientHeaders: false,
  });
}

export async function exportAnalyticsCsv(
  module: string,
  filters: AnalyticsFilterState,
): Promise<{ blob: Blob; filename: string }> {
  const token = getAccessToken();
  const res = await fetch(`${getApiBaseUrl()}/analytics/export`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      module,
      format: "csv",
      preset: filters.preset ?? undefined,
      date_from: filters.date_from ?? undefined,
      date_to: filters.date_to ?? undefined,
      village_id: filters.village_id ?? undefined,
      crop_type_id: filters.crop_type_id ?? undefined,
      farmer_id: filters.farmer_id ?? undefined,
      buyer_id: filters.buyer_id ?? undefined,
      asset_id: filters.asset_id ?? undefined,
      season: filters.season ?? undefined,
    }),
  });
  if (!res.ok) {
    throw new Error(`Export failed (${res.status})`);
  }
  const disposition = res.headers.get("Content-Disposition") || "";
  const match = /filename="([^"]+)"/.exec(disposition);
  const filename = match?.[1] ?? `analytics_${module}.csv`;
  const blob = await res.blob();
  return { blob, filename };
}
