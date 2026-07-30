"use client";

import {
  Alert,
  Card,
  CardActionArea,
  CardContent,
  Grid2 as Grid,
  Stack,
  Typography,
} from "@mui/material";
import {
  Agriculture,
  ChevronRight,
  Dataset,
  DirectionsCar,
  Groups,
  LocalAtm,
  People,
  WorkOutline,
} from "@mui/icons-material";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { ROUTES } from "@/constants/routes";
import { fetchDashboardSummary } from "@/features/dashboard/api";
import { useAuth } from "@/hooks/use-auth";

const ADMIN_LINKS = [
  {
    href: ROUTES.settingsUsers,
    title: "Users & roles",
    description: "Add and edit organization members",
    icon: People,
  },
  {
    href: ROUTES.settingsMasterData,
    title: "Master data hub",
    description: "All catalogs in one place",
    icon: Dataset,
  },
  {
    href: "/settings/master-data/crops",
    title: "Crop types",
    description: "Paddy, corn, seasonal crops",
    icon: Agriculture,
  },
  {
    href: "/settings/master-data/vehicle-types",
    title: "Vehicle types",
    description: "Fleet categories for trips",
    icon: DirectionsCar,
  },
  {
    href: "/settings/master-data/activity-types",
    title: "Activity types",
    description: "Field service and work types",
    icon: WorkOutline,
  },
  {
    href: "/settings/master-data/buyers",
    title: "Buyers",
    description: "Mills and traders",
    icon: LocalAtm,
  },
  {
    href: "/settings/master-data/agents",
    title: "Field agents",
    description: "Collection agent roster",
    icon: Groups,
  },
  {
    href: ROUTES.settingsVillages,
    title: "Villages",
    description: "Geography master (District → Mandal cascade)",
    icon: Agriculture,
  },
] as const;

const ROLE_HINTS: Record<string, string> = {
  OWNER: "Admin overview — users, masters, and ops counts.",
  MANAGER: "Operations overview — farmers, procurement, and field services.",
  SUPERVISOR: "Farming supervisor — field services and farmer intake.",
  DRIVER: "Vehicle supervisor — transport and diesel-related ops.",
  AGENT: "Field agent — farmers and procurement drafts.",
  WORKER: "Field ops — use the sidebar for assigned work.",
  HAMALI: "View your daily bags and tips — open My work from the sidebar.",
  FARMER: "Farmer portal — read-only procurement and field updates.",
  ACCOUNTANT: "Finance focus — expenses and collections (when live).",
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

export function DashboardHome() {
  const { user, role, canAccessAdmin, isError, error, isLoading } = useAuth();
  const summaryQuery = useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: fetchDashboardSummary,
    staleTime: 60_000,
    retry: 1,
  });

  return (
    <MuiPageShell
      title="Home"
      description={
        canAccessAdmin
          ? "Farm operations overview and administration shortcuts."
          : "Farm operations overview for Bhairkhanpally."
      }
    >
      <Stack spacing={3}>
        {isError && (
          <Alert severity="warning">
            {error instanceof Error
              ? error.message
              : "Could not load your session. Sign in again if pages look empty."}
          </Alert>
        )}

        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight={600}>
              Welcome{user?.name ? `, ${user.name}` : ""}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {isLoading
                ? "Loading session…"
                : role
                  ? `Signed in as ${role}`
                  : "Session unavailable"}{" "}
              — {role ? ROLE_HINTS[role] ?? "use the sidebar for farmers, procurement, and field services." : "use the sidebar for farmers, procurement, and field services."}
            </Typography>
          </CardContent>
        </Card>

        {summaryQuery.isError && (
          <Alert severity="info">
            Dashboard counts unavailable
            {summaryQuery.error instanceof Error ? `: ${summaryQuery.error.message}` : ""}.
          </Alert>
        )}

        {summaryQuery.data && (
          <>
            <Grid container spacing={2}>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat label="Farmers" value={summaryQuery.data.farmers ?? 0} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat label="Procurements" value={summaryQuery.data.procurements ?? 0} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat label="Payments" value={summaryQuery.data.farmer_payments ?? 0} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat label="Assets" value={summaryQuery.data.assets ?? 0} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat label="Field services" value={summaryQuery.data.field_services ?? 0} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat label="Trips" value={summaryQuery.data.vehicle_trips ?? 0} />
              </Grid>
            </Grid>
            <Grid container spacing={2}>
              <Grid size={{ xs: 6, sm: 3 }}>
                <SummaryStat label="Users" value={summaryQuery.data.users} />
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <SummaryStat label="Villages" value={summaryQuery.data.villages} />
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <SummaryStat label="Crop types" value={summaryQuery.data.crop_types} />
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <SummaryStat label="Documents" value={summaryQuery.data.documents} />
              </Grid>
            </Grid>
          </>
        )}

        {canAccessAdmin && (
          <>
            <Typography variant="subtitle1" fontWeight={600}>
              Administration
            </Typography>
            <Grid container spacing={2}>
              {ADMIN_LINKS.map((link) => {
                const Icon = link.icon;
                return (
                  <Grid key={link.href} size={{ xs: 12, sm: 6, md: 4 }}>
                    <Card>
                      <CardActionArea component={Link} href={link.href}>
                        <CardContent>
                          <Stack direction="row" spacing={2} alignItems="flex-start">
                            <Icon color="primary" />
                            <Stack spacing={0.5} sx={{ flex: 1 }}>
                              <Stack
                                direction="row"
                                alignItems="center"
                                justifyContent="space-between"
                              >
                                <Typography variant="subtitle1" fontWeight={600}>
                                  {link.title}
                                </Typography>
                                <ChevronRight fontSize="small" color="action" />
                              </Stack>
                              <Typography variant="body2" color="text.secondary">
                                {link.description}
                              </Typography>
                            </Stack>
                          </Stack>
                        </CardContent>
                      </CardActionArea>
                    </Card>
                  </Grid>
                );
              })}
            </Grid>
          </>
        )}
      </Stack>
    </MuiPageShell>
  );
}
