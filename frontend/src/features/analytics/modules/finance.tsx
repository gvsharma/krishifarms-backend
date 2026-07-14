"use client";

import { Box, Stack } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { fetchAnalyticsSummary } from "../api";
import { BarCompare } from "../charts/BarCompare";
import { LineTrend } from "../charts/LineTrend";
import { AnalyticsShell } from "../components/AnalyticsShell";
import { useAnalyticsFiltersStore } from "../filters-store";

export function FinanceModule() {
  const filters = useAnalyticsFiltersStore((s) => s.filters);
  const { data, isLoading, error } = useQuery({
    queryKey: ["analytics", "finance", filters],
    queryFn: () => fetchAnalyticsSummary("finance", filters),
  });

  const categories = data?.tables_preview?.[0];
  const expensePoints = (data?.series_preview ?? []).filter((p) => p.series === "expenses");
  const revenuePoints = (data?.series_preview ?? []).filter((p) => p.series === "procurement_revenue");

  return (
    <AnalyticsShell
      module="finance"
      title="Finance Dashboard"
      summary={data}
      loading={isLoading}
      error={error instanceof Error ? error.message : null}
    >
      <Stack spacing={2}>
        <Box sx={{ display: "grid", gap: 2, gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" } }}>
          <LineTrend title="Expenses by day" points={expensePoints} seriesKey="expenses" />
          <LineTrend title="Procurement revenue by day" points={revenuePoints} seriesKey="procurement_revenue" />
        </Box>
        <BarCompare
          title="Expenses by category"
          labels={(categories?.rows ?? []).map((r) => String(r.cells.name ?? ""))}
          values={(categories?.rows ?? []).map((r) => Number(r.cells.amount ?? 0))}
        />
      </Stack>
    </AnalyticsShell>
  );
}
