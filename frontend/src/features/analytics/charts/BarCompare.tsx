"use client";

import { Box, Typography } from "@mui/material";
import { BarChart } from "@mui/x-charts/BarChart";

export function BarCompare({
  title,
  labels,
  values,
}: {
  title: string;
  labels: string[];
  values: number[];
}) {
  if (!labels.length) {
    return (
      <Box sx={{ p: 2, border: "1px dashed", borderColor: "divider", borderRadius: 2 }}>
        <Typography variant="subtitle2">{title}</Typography>
        <Typography variant="body2" color="text.secondary">
          No comparison data
        </Typography>
      </Box>
    );
  }
  return (
    <Box sx={{ p: 1, border: "1px solid", borderColor: "divider", borderRadius: 2, bgcolor: "background.paper" }}>
      <Typography variant="subtitle2" sx={{ px: 1, pt: 1 }}>
        {title}
      </Typography>
      <BarChart
        height={260}
        series={[{ data: values, label: title, color: "#558B2F" }]}
        xAxis={[{ data: labels, scaleType: "band" }]}
        margin={{ left: 60, right: 20, top: 20, bottom: 40 }}
      />
    </Box>
  );
}
