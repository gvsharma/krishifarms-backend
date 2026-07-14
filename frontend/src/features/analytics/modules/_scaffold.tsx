"use client";

import { Alert, List, ListItem, ListItemText, Typography } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { fetchAnalyticsSummary } from "../api";
import { AnalyticsShell } from "../components/AnalyticsShell";
import { useAnalyticsFiltersStore } from "../filters-store";

const TITLES: Record<string, string> = {
  farming: "Farming",
  vehicle: "Vehicle",
  village: "Village",
  farmer: "Farmer",
  buyer: "Buyer",
  employee: "Employee",
  service: "Service",
  "crop-intelligence": "Crop Intelligence",
  inventory: "Inventory",
  "ai-prediction": "AI Prediction",
  alerts: "Alerts",
};

export function ScaffoldModule({ moduleId }: { moduleId: string }) {
  const filters = useAnalyticsFiltersStore((s) => s.filters);
  const { data, isLoading, error } = useQuery({
    queryKey: ["analytics", moduleId, filters],
    queryFn: () => fetchAnalyticsSummary(moduleId, filters),
  });

  return (
    <AnalyticsShell
      module={moduleId}
      title={TITLES[moduleId] ?? moduleId}
      summary={data}
      loading={isLoading}
      error={error instanceof Error ? error.message : null}
    >
      <Alert severity="info" data-testid="scaffold-availability">
        This module is scaffolded for Phase 1. No fabricated KPIs — see data availability below.
      </Alert>
      <Typography variant="subtitle2" sx={{ mt: 2 }}>
        Missing sources
      </Typography>
      <List dense>
        {(data?.data_availability ?? []).map((d) => (
          <ListItem key={d.source}>
            <ListItemText primary={d.source} secondary={d.notes ?? d.status} />
          </ListItem>
        ))}
      </List>
    </AnalyticsShell>
  );
}
