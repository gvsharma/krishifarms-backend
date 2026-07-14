"use client";

import { Box, Typography } from "@mui/material";
import { PieChart } from "@mui/x-charts/PieChart";

export function DonutShare({
  title,
  slices,
}: {
  title: string;
  slices: { id: string; label: string; value: number }[];
}) {
  if (!slices.length) {
    return (
      <Box sx={{ p: 2, border: "1px dashed", borderColor: "divider", borderRadius: 2 }}>
        <Typography variant="subtitle2">{title}</Typography>
        <Typography variant="body2" color="text.secondary">
          No share data
        </Typography>
      </Box>
    );
  }
  return (
    <Box sx={{ p: 1, border: "1px solid", borderColor: "divider", borderRadius: 2, bgcolor: "background.paper" }}>
      <Typography variant="subtitle2" sx={{ px: 1, pt: 1 }}>
        {title}
      </Typography>
      <PieChart
        height={260}
        series={[
          {
            data: slices.map((s) => ({ id: s.id, value: s.value, label: s.label })),
            innerRadius: 50,
            paddingAngle: 2,
            cornerRadius: 4,
          },
        ]}
      />
    </Box>
  );
}
