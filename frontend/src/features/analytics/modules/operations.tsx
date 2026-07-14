"use client";

import { Stack } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { fetchAnalyticsSummary } from "../api";
import { LineTrend } from "../charts/LineTrend";
import { AnalyticsShell } from "../components/AnalyticsShell";
import { useAnalyticsFiltersStore } from "../filters-store";

export function OperationsModule() {
  const filters = useAnalyticsFiltersStore((s) => s.filters);
  const opsFilters = { ...filters, preset: filters.preset ?? "today" };
  const { data, isLoading, error } = useQuery({
    queryKey: ["analytics", "operations", opsFilters],
    queryFn: () => fetchAnalyticsSummary("operations", opsFilters),
  });

  return (
    <AnalyticsShell
      module="operations"
      title="Operations Command"
      summary={data}
      loading={isLoading}
      error={error instanceof Error ? error.message : null}
    >
      <Stack spacing={2}>
        <LineTrend title="Day revenue pulse" points={data?.series_preview ?? []} />
      </Stack>
    </AnalyticsShell>
  );
}
