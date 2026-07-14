"use client";

import { Box, Stack, Table, TableBody, TableCell, TableHead, TableRow, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { fetchAnalyticsSummary } from "../api";
import { BarCompare } from "../charts/BarCompare";
import { DonutShare } from "../charts/DonutShare";
import { LineTrend } from "../charts/LineTrend";
import { AnalyticsShell } from "../components/AnalyticsShell";
import { useAnalyticsFiltersStore } from "../filters-store";

export function ProcurementModule() {
  const filters = useAnalyticsFiltersStore((s) => s.filters);
  const { data, isLoading, error } = useQuery({
    queryKey: ["analytics", "procurement", filters],
    queryFn: () => fetchAnalyticsSummary("procurement", filters),
  });

  const crops = data?.tables_preview?.find((t) => t.id === "top_crops");
  const villages = data?.tables_preview?.find((t) => t.id === "top_villages");

  return (
    <AnalyticsShell
      module="procurement"
      title="Procurement Analytics"
      summary={data}
      loading={isLoading}
      error={error instanceof Error ? error.message : null}
    >
      <Stack spacing={2}>
        <LineTrend title="Confirmed value by day" points={data?.series_preview ?? []} />
        <Box sx={{ display: "grid", gap: 2, gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" } }}>
          <BarCompare
            title="Top crops (₹)"
            labels={(crops?.rows ?? []).map((r) => String(r.cells.name ?? ""))}
            values={(crops?.rows ?? []).map((r) => Number(r.cells.amount ?? 0))}
          />
          <DonutShare
            title="Crop share"
            slices={(crops?.rows ?? []).map((r, i) => ({
              id: String(i),
              label: String(r.cells.name ?? ""),
              value: Number(r.cells.amount ?? 0),
            }))}
          />
        </Box>
        {villages ? (
          <Box sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2, overflow: "hidden" }}>
            <Typography variant="subtitle2" sx={{ px: 2, py: 1.5 }}>
              {villages.title}
            </Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  {villages.columns.map((c) => (
                    <TableCell key={c.key}>{c.label}</TableCell>
                  ))}
                </TableRow>
              </TableHead>
              <TableBody>
                {villages.rows.map((row, idx) => (
                  <TableRow key={idx}>
                    {villages.columns.map((c) => (
                      <TableCell key={c.key}>{row.cells[c.key] ?? "—"}</TableCell>
                    ))}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Box>
        ) : null}
      </Stack>
    </AnalyticsShell>
  );
}
