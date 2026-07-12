"use client";

import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Grid2 as Grid,
  Stack,
  Typography,
} from "@mui/material";
import {
  Agriculture,
  ChevronRight,
  DirectionsCar,
  Groups,
  LocalAtm,
  People,
  Summarize,
  TrendingUp,
} from "@mui/icons-material";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { ROUTES } from "@/constants/routes";
import {
  FALLBACK_REPORT_CATALOG,
  fetchDashboardSummary,
  fetchReportCatalog,
  type ReportCatalogItem,
  type ReportStatus,
} from "@/features/dashboard/api";

const STATUS_LABEL: Record<ReportStatus, string> = {
  available: "Available",
  partial: "Browse data",
  coming_soon: "Coming soon",
};

const STATUS_COLOR: Record<ReportStatus, "success" | "warning" | "default"> = {
  available: "success",
  partial: "warning",
  coming_soon: "default",
};

const MODULE_LABELS: Record<string, string> = {
  [ROUTES.vehicles]: "Vehicles",
  [ROUTES.services]: "Field services",
  [ROUTES.expenses]: "Expenses",
  [ROUTES.procurement]: "Procurement",
  [ROUTES.farmers]: "Farmers",
  [ROUTES.payments]: "Payments",
  [ROUTES.settingsVillages]: "Villages",
  [ROUTES.workers]: "Workers",
  [ROUTES.farms]: "Farms",
};

function SummaryStat({ label, value }: { label: string; value: number | string }) {
  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Typography variant="caption" color="text.secondary" textTransform="uppercase">
          {label}
        </Typography>
        <Typography variant="h4" fontWeight={700} sx={{ mt: 0.5 }}>
          {value}
        </Typography>
      </CardContent>
    </Card>
  );
}

function reportIcon(id: string) {
  switch (id) {
    case "vehicle_utilization":
    case "vehicle_earnings":
    case "diesel_expenses":
      return DirectionsCar;
    case "procurement_summary":
    case "crop_village_procurement":
      return Agriculture;
    case "farmer_ledger":
    case "outstanding_payments":
      return LocalAtm;
    case "supervisor_productivity":
      return Groups;
    default:
      return Summarize;
  }
}

function ReportCard({ report }: { report: ReportCatalogItem }) {
  const Icon = reportIcon(report.id);
  const paths = report.module_paths ?? [];

  return (
    <Card sx={{ height: "100%" }}>
      <CardContent>
        <Stack spacing={1.5}>
          <Stack direction="row" spacing={1.5} alignItems="flex-start">
            <Icon color="primary" />
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Stack
                direction="row"
                alignItems="center"
                justifyContent="space-between"
                gap={1}
                flexWrap="wrap"
              >
                <Typography variant="subtitle1" fontWeight={600}>
                  {report.name}
                </Typography>
                <Chip
                  size="small"
                  label={STATUS_LABEL[report.status] ?? report.status}
                  color={STATUS_COLOR[report.status] ?? "default"}
                  variant={report.status === "coming_soon" ? "outlined" : "filled"}
                />
              </Stack>
              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                {report.description}
              </Typography>
            </Box>
          </Stack>

          {report.notes && (
            <Typography variant="caption" color="text.secondary">
              {report.notes}
            </Typography>
          )}

          {paths.length > 0 && (
            <Stack direction="row" flexWrap="wrap" gap={1}>
              {paths.map((href) => (
                <Button
                  key={href}
                  component={Link}
                  href={href}
                  size="small"
                  endIcon={<ChevronRight fontSize="small" />}
                  sx={{ textTransform: "none" }}
                >
                  {MODULE_LABELS[href] ?? href}
                </Button>
              ))}
            </Stack>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}

export default function ReportsPage() {
  const summaryQuery = useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: fetchDashboardSummary,
    staleTime: 60_000,
    retry: 1,
  });

  const catalogQuery = useQuery({
    queryKey: ["dashboard", "reports"],
    queryFn: fetchReportCatalog,
    staleTime: 300_000,
    retry: 1,
  });

  const reports = catalogQuery.data?.items ?? FALLBACK_REPORT_CATALOG;
  const summary = summaryQuery.data;

  return (
    <MuiPageShell
      title="Reports"
      description="Executive report registry for Bhairkhanpally ops. Live KPI strip from /dashboard/summary; analytic report APIs still roll out against docs/reporting SQL."
    >
      <Stack spacing={3}>
        <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
          <Chip icon={<TrendingUp />} label="KPI strip live" color="success" size="small" />
          <Chip label="Full reports: SQL ready, APIs pending" size="small" variant="outlined" />
          <Button component={Link} href={ROUTES.dashboard} size="small" sx={{ textTransform: "none" }}>
            Open home dashboard
          </Button>
        </Stack>

        {summaryQuery.isLoading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 2 }}>
            <CircularProgress size={28} />
          </Box>
        )}

        {summaryQuery.isError && (
          <Alert severity="info">
            Dashboard counts unavailable
            {summaryQuery.error instanceof Error ? `: ${summaryQuery.error.message}` : ""}.
          </Alert>
        )}

        {summary && (
          <>
            <Typography variant="subtitle1" fontWeight={600}>
              Operational snapshot
            </Typography>
            <Grid container spacing={2}>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat label="Farmers" value={summary.farmers ?? 0} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat label="Procurements" value={summary.procurements ?? 0} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat label="Payments" value={summary.farmer_payments ?? 0} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat label="Assets" value={summary.assets ?? 0} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat label="Field services" value={summary.field_services ?? 0} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat label="Trips" value={summary.vehicle_trips ?? 0} />
              </Grid>
            </Grid>
            <Grid container spacing={2}>
              <Grid size={{ xs: 6, sm: 3 }}>
                <SummaryStat label="Users" value={summary.users} />
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <SummaryStat label="Villages" value={summary.villages} />
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <SummaryStat label="Crop types" value={summary.crop_types} />
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <SummaryStat label="Documents" value={summary.documents} />
              </Grid>
            </Grid>
          </>
        )}

        <Stack spacing={1}>
          <Stack direction="row" alignItems="center" justifyContent="space-between" flexWrap="wrap" gap={1}>
            <Typography variant="subtitle1" fontWeight={600}>
              Report catalog
            </Typography>
            {catalogQuery.isFetching && <CircularProgress size={18} />}
          </Stack>
          {catalogQuery.isError && (
            <Alert severity="warning">
              Report registry API unavailable — showing local ERP catalog.{" "}
              {catalogQuery.error instanceof Error ? catalogQuery.error.message : null}
            </Alert>
          )}
          <Typography variant="body2" color="text.secondary">
            Browse-data reports link to modules where records already live. Coming-soon items need
            dedicated `/dashboard/*` or `/reports/*` KPI endpoints over the SQL in{" "}
            <Box component="span" sx={{ fontFamily: "monospace", fontSize: "0.85em" }}>
              docs/reporting/sql/
            </Box>
            .
          </Typography>
        </Stack>

        <Grid container spacing={2}>
          {reports.map((report) => (
            <Grid key={report.id} size={{ xs: 12, md: 6 }}>
              <ReportCard report={report} />
            </Grid>
          ))}
        </Grid>

        <Card variant="outlined">
          <CardContent>
            <Stack direction="row" spacing={1.5} alignItems="flex-start">
              <People color="action" />
              <Box>
                <Typography variant="subtitle2" fontWeight={600}>
                  API gaps (checklist)
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  Still needed for runnable reports: period filters (`date_from`/`date_to`),
                  procurement/village/crop aggregates, farmer outstanding snapshots, diesel expense
                  rollups, vehicle earnings from usage logs, and supervisor productivity from
                  workers/work-orders. Registry + summary counts ship now via{" "}
                  <Box component="span" sx={{ fontFamily: "monospace", fontSize: "0.85em" }}>
                    GET /dashboard/reports
                  </Box>{" "}
                  and{" "}
                  <Box component="span" sx={{ fontFamily: "monospace", fontSize: "0.85em" }}>
                    GET /dashboard/summary
                  </Box>
                  .
                </Typography>
              </Box>
            </Stack>
          </CardContent>
        </Card>
      </Stack>
    </MuiPageShell>
  );
}
