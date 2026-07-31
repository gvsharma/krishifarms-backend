"use client";

import { Box, Typography } from "@mui/material";
import { LineChart } from "@mui/x-charts/LineChart";
import type { SeriesPoint } from "../types";

export function LineTrend({
  title,
  points,
  seriesKey,
  seriesKeys,
}: {
  title: string;
  points: SeriesPoint[];
  seriesKey?: string;
  /** When set, render one line per series name (overrides seriesKey). */
  seriesKeys?: string[];
}) {
  const keys =
    seriesKeys ??
    (seriesKey ? [seriesKey] : [...new Set(points.map((p) => p.series ?? "primary"))]);
  const filtered = points.filter((p) => keys.includes(p.series ?? "primary"));
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
  const xLabels = [...new Set(filtered.map((p) => p.x))];
  const palette = ["#2E7D32", "#1565C0", "#EF6C00", "#6A1B9A"];
  const series = keys.map((key, idx) => ({
    data: xLabels.map((x) => {
      const pt = filtered.find((p) => p.x === x && (p.series ?? "primary") === key);
      return pt ? Number(pt.y) : null;
    }),
    label: key.replace(/_/g, " "),
    color: palette[idx % palette.length],
    connectNulls: true,
  }));
  return (
    <Box sx={{ p: 1, border: "1px solid", borderColor: "divider", borderRadius: 2, bgcolor: "background.paper" }}>
      <Typography variant="subtitle2" sx={{ px: 1, pt: 1 }}>
        {title}
      </Typography>
      <LineChart
        height={260}
        series={series}
        xAxis={[{ data: xLabels, scaleType: "point" }]}
        margin={{ left: 60, right: 20, top: 20, bottom: 40 }}
      />
    </Box>
  );
}
