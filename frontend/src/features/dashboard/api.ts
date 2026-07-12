import { fetchApi } from "@/lib/api/client";

export interface DashboardSummaryCounts {
  users: number;
  villages: number;
  crop_types: number;
  documents: number;
}

export function fetchDashboardSummary(): Promise<DashboardSummaryCounts> {
  return fetchApi<DashboardSummaryCounts>("/dashboard/summary", {
    method: "GET",
    clientHeaders: false,
  });
}
