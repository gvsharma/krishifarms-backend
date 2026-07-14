"use client";

import {
  Alert,
  Box,
  Button,
  Chip,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import type { ReactNode } from "react";
import { useAnalyticsFiltersStore } from "../filters-store";
import { tAnalytics, type AnalyticsLocale } from "../messages";
import { ExportMenu } from "./ExportMenu";
import { KpiGrid } from "./KpiGrid";
import type { ModuleSummary } from "../types";

const PRESETS = [
  { value: "today", labelKey: "today" as const },
  { value: "7d", labelKey: "d7" as const },
  { value: "30d", labelKey: "d30" as const },
  { value: "season", labelKey: "season" as const },
  { value: "custom", labelKey: "custom" as const },
];

export function AnalyticsShell({
  module,
  title,
  summary,
  locale = "en",
  children,
  loading,
  error,
}: {
  module: string;
  title: string;
  summary?: ModuleSummary | null;
  locale?: AnalyticsLocale;
  children?: ReactNode;
  loading?: boolean;
  error?: string | null;
}) {
  const filters = useAnalyticsFiltersStore((s) => s.filters);
  const setPreset = useAnalyticsFiltersStore((s) => s.setPreset);
  const setFilters = useAnalyticsFiltersStore((s) => s.setFilters);
  const saveView = useAnalyticsFiltersStore((s) => s.saveView);
  const loadView = useAnalyticsFiltersStore((s) => s.loadView);
  const savedViews = useAnalyticsFiltersStore((s) => s.savedViews);

  return (
    <Box data-testid={`analytics-shell-${module}`}>
      <Stack
        direction={{ xs: "column", md: "row" }}
        spacing={1.5}
        alignItems={{ md: "center" }}
        justifyContent="space-between"
        sx={{
          position: "sticky",
          top: 0,
          zIndex: 2,
          py: 1.5,
          mb: 2,
          bgcolor: "background.default",
          borderBottom: "1px solid",
          borderColor: "divider",
        }}
      >
        <Box>
          <Typography variant="h5" fontWeight={700}>
            {title}
          </Typography>
          {summary?.health_score != null ? (
            <Typography variant="body2" color="text.secondary">
              {tAnalytics(locale, "healthScore")}: {summary.health_score}
              {summary.health_score_method ? ` (${summary.health_score_method})` : ""}
              {summary.cache_hit ? ` · ${tAnalytics(locale, "cacheHit")}` : ""}
            </Typography>
          ) : null}
        </Box>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          <TextField
            select
            size="small"
            label={tAnalytics(locale, "preset")}
            value={filters.preset ?? "30d"}
            onChange={(e) => setPreset(e.target.value)}
            sx={{ minWidth: 140 }}
            data-testid="analytics-preset"
          >
            {PRESETS.map((p) => (
              <MenuItem key={p.value} value={p.value}>
                {tAnalytics(locale, p.labelKey)}
              </MenuItem>
            ))}
          </TextField>
          {filters.preset === "custom" ? (
            <>
              <TextField
                size="small"
                type="date"
                label="From"
                InputLabelProps={{ shrink: true }}
                value={filters.date_from ?? ""}
                onChange={(e) => setFilters({ date_from: e.target.value || null, preset: "custom" })}
              />
              <TextField
                size="small"
                type="date"
                label="To"
                InputLabelProps={{ shrink: true }}
                value={filters.date_to ?? ""}
                onChange={(e) => setFilters({ date_to: e.target.value || null, preset: "custom" })}
              />
            </>
          ) : null}
          <Button
            size="small"
            variant="text"
            onClick={() => {
              const name = window.prompt("View name");
              if (name) saveView(name.trim());
            }}
          >
            {tAnalytics(locale, "saveView")}
          </Button>
          {Object.keys(savedViews).length > 0 ? (
            <TextField
              select
              size="small"
              label={tAnalytics(locale, "savedViews")}
              value=""
              onChange={(e) => loadView(e.target.value)}
              sx={{ minWidth: 140 }}
            >
              {Object.keys(savedViews).map((name) => (
                <MenuItem key={name} value={name}>
                  {name}
                </MenuItem>
              ))}
            </TextField>
          ) : null}
          <ExportMenu module={module} filters={filters} locale={locale} />
        </Stack>
      </Stack>

      {loading ? (
        <Typography color="text.secondary">Loading…</Typography>
      ) : null}
      {error ? (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {error}
        </Alert>
      ) : null}

      {summary ? (
        <Stack spacing={3}>
          <KpiGrid kpis={summary.kpis} />
          {children}
          {summary.data_availability.length > 0 ? (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                {tAnalytics(locale, "dataAvailability")}
              </Typography>
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                {summary.data_availability.map((d) => (
                  <Chip
                    key={`${d.source}-${d.status}`}
                    size="small"
                    label={`${d.source}: ${d.status}${d.notes ? ` — ${d.notes}` : ""}`}
                    color={d.status === "available" ? "success" : d.status === "partial" ? "warning" : "default"}
                    data-testid="data-availability-chip"
                  />
                ))}
              </Stack>
            </Box>
          ) : null}
        </Stack>
      ) : null}
    </Box>
  );
}
