"use client";

import { Box, Card, CardActionArea, CardContent, Chip, Stack, Typography } from "@mui/material";
import Link from "next/link";
import type { KpiCard } from "../types";

function formatValue(kpi: KpiCard): string {
  if (kpi.value === null || kpi.value === undefined) return "—";
  if (kpi.format === "money") {
    const n = Number(kpi.value);
    if (Number.isFinite(n)) {
      return new Intl.NumberFormat("en-IN", {
        style: "currency",
        currency: "INR",
        maximumFractionDigits: 0,
      }).format(n);
    }
  }
  return String(kpi.value);
}

const STATUS_COLOR: Record<string, "success" | "warning" | "default" | "info"> = {
  live: "success",
  estimate: "info",
  unavailable: "default",
  coming_soon: "warning",
};

export function KpiGrid({ kpis }: { kpis: KpiCard[] }) {
  return (
    <Box
      sx={{
        display: "grid",
        gap: 1.5,
        gridTemplateColumns: {
          xs: "1fr",
          sm: "repeat(2, 1fr)",
          md: "repeat(3, 1fr)",
          lg: "repeat(4, 1fr)",
        },
      }}
    >
      {kpis.map((kpi) => {
        const body = (
          <CardContent sx={{ py: 1.75, "&:last-child": { pb: 1.75 } }}>
            <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={1}>
              <Typography variant="caption" color="text.secondary" textTransform="uppercase" letterSpacing={0.06}>
                {kpi.label}
              </Typography>
              <Chip size="small" label={kpi.status.replace("_", " ")} color={STATUS_COLOR[kpi.status] ?? "default"} />
            </Stack>
            <Typography variant="h5" fontWeight={700} sx={{ mt: 0.75, color: "text.primary" }}>
              {formatValue(kpi)}
              {kpi.unit && kpi.format !== "money" && kpi.value != null ? (
                <Typography component="span" variant="body2" color="text.secondary" sx={{ ml: 0.5 }}>
                  {kpi.unit}
                </Typography>
              ) : null}
            </Typography>
            {kpi.note ? (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: "block" }}>
                {kpi.note}
              </Typography>
            ) : null}
          </CardContent>
        );

        if (kpi.drill?.href && kpi.status !== "unavailable" && kpi.status !== "coming_soon") {
          return (
            <Card
              key={kpi.id}
              data-testid={`kpi-${kpi.id}`}
              sx={{ border: "1px solid", borderColor: "divider", bgcolor: "background.paper" }}
            >
              <CardActionArea component={Link} href={kpi.drill.href}>
                {body}
              </CardActionArea>
            </Card>
          );
        }

        return (
          <Card
            key={kpi.id}
            data-testid={`kpi-${kpi.id}`}
            sx={{ border: "1px solid", borderColor: "divider", bgcolor: "background.paper" }}
          >
            {body}
          </Card>
        );
      })}
    </Box>
  );
}
