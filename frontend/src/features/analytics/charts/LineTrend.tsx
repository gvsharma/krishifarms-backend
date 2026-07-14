"use client";

import { Box, Typography } from "@mui/material";
import { LineChart } from "@mui/x-charts/LineChart";
import type { SeriesPoint } from "../types";

export function LineTrend({
  title,
  points,
  seriesKey,
}: {
  title: string;
  points: SeriesPoint[];
  seriesKey?: string;
}) {
  const filtered = seriesKey ? points.filter((p) => (p.series ?? "primary") === seriesKey) : points;
  if (!filtered.length) {
    return (
      <Box sx={{ p: 2, border: "1px dashed", borderColor: "divider", borderRadius: 2 }}>
        <Typography variant="subtitle2">{title}</Typography>
        <Typography variant="body2" color="text.secondary">
          No series data
        </Typography>
      </Box>
    );
  }
  return (
    <Box sx={{ p: 1, border: "1px solid", borderColor: "divider", borderRadius: 2, bgcolor: "background.paper" }}>
      <Typography variant="subtitle2" sx={{ px: 1, pt: 1 }}>
        {title}
      </Typography>
      <LineChart
        height={260}
        series={[
          {
            data: filtered.map((p) => Number(p.y)),
            label: seriesKey ?? "trend",
            color: "#2E7D32",
          },
        ]}
        xAxis={[{ data: filtered.map((p) => p.x), scaleType: "point" }]}
        margin={{ left: 60, right: 20, top: 20, bottom: 40 }}
      />
    </Box>
  );
}
