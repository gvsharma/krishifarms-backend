"use client";

import { Box, Stack, Table, TableBody, TableCell, TableHead, TableRow, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { ResponsiveTable } from "@/components/ui/responsive-table";
import { fetchAnalyticsSummary } from "../api";
import { BarCompare } from "../charts/BarCompare";
import { HeatmapSimple } from "../charts/HeatmapSimple";
import { LineTrend } from "../charts/LineTrend";
import { AnalyticsShell } from "../components/AnalyticsShell";
import { useAnalyticsFiltersStore } from "../filters-store";

function RankingTable({
  title,
  table,
}: {
  title: string;
  table?: {
    columns: { key: string; label: string }[];
    rows: { cells: Record<string, string | number | null> }[];
  };
}) {
  if (!table) return null;
  return (
    <Box sx={{ border: "1px solid", borderColor: "divider", borderRadius: 2, overflow: "hidden" }}>
      <Typography variant="subtitle2" sx={{ px: 2, py: 1.5 }}>
        {title}
      </Typography>
      <ResponsiveTable>
        <Table size="small">
          <TableHead>
            <TableRow>
              {table.columns.map((c) => (
                <TableCell key={c.key}>{c.label}</TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {table.rows.map((row, idx) => (
              <TableRow key={idx}>
                {table.columns.map((c) => (
                  <TableCell key={c.key}>{row.cells[c.key] ?? "—"}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </ResponsiveTable>
    </Box>
  );
}

export function ExecutiveModule() {
  const filters = useAnalyticsFiltersStore((s) => s.filters);
  const { data, isLoading, error } = useQuery({
    queryKey: ["analytics", "executive", filters],
    queryFn: () => fetchAnalyticsSummary("executive", filters),
  });

  const villages = data?.tables_preview?.find((t) => t.id === "top_villages");
  const farmers = data?.tables_preview?.find((t) => t.id === "top_farmers");
  const crops = data?.tables_preview?.find((t) => t.id === "top_crops");
  const heatCells =
    villages?.rows.map((r) => ({
      label: String(r.cells.name ?? ""),
      value: Number(r.cells.amount ?? 0),
    })) ?? [];

  return (
    <AnalyticsShell
      module="executive"
      title="Executive"
      summary={data}
      loading={isLoading}
      error={error instanceof Error ? error.message : null}
    >
      <Stack spacing={2}>
        <LineTrend title="Sales & profit trend" points={data?.series_preview ?? []} seriesKey="profit" />
        <Box
          sx={{
            display: "grid",
            gap: 2,
            gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" },
          }}
        >
          <HeatmapSimple title="Village value heat (table)" cells={heatCells} />
          <RankingTable title="Profit by village" table={villages} />
        </Box>
        <Box
          sx={{
            display: "grid",
            gap: 2,
            gridTemplateColumns: { xs: "1fr", lg: "1fr 1fr" },
          }}
        >
          <RankingTable title="Profit by farmer" table={farmers} />
          <RankingTable title="Profit by crop" table={crops} />
        </Box>
      </Stack>
    </AnalyticsShell>
  );
}
