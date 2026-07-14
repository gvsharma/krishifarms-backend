"use client";

import { Box, Typography } from "@mui/material";

/** Simple CSS heatmap (Phase 1) — no map layers. */
export function HeatmapSimple({
  title,
  cells,
}: {
  title: string;
  cells: { label: string; value: number }[];
}) {
  const max = Math.max(...cells.map((c) => c.value), 1);
  if (!cells.length) {
    return (
      <Box sx={{ p: 2, border: "1px dashed", borderColor: "divider", borderRadius: 2 }}>
        <Typography variant="subtitle2">{title}</Typography>
        <Typography variant="body2" color="text.secondary">
          No ranking heat data
        </Typography>
      </Box>
    );
  }
  return (
    <Box sx={{ p: 2, border: "1px solid", borderColor: "divider", borderRadius: 2, bgcolor: "background.paper" }}>
      <Typography variant="subtitle2" gutterBottom>
        {title}
      </Typography>
      <Box sx={{ display: "grid", gap: 0.75, gridTemplateColumns: "repeat(auto-fill, minmax(120px, 1fr))" }}>
        {cells.map((c) => {
          const intensity = c.value / max;
          return (
            <Box
              key={c.label}
              sx={{
                p: 1,
                borderRadius: 1,
                bgcolor: `rgba(46, 125, 50, ${0.12 + intensity * 0.55})`,
                color: "text.primary",
              }}
            >
              <Typography variant="caption" display="block" noWrap>
                {c.label}
              </Typography>
              <Typography variant="body2" fontWeight={600}>
                {c.value.toLocaleString("en-IN")}
              </Typography>
            </Box>
          );
        })}
      </Box>
    </Box>
  );
}
