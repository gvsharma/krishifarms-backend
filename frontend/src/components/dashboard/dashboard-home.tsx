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
import { useTranslation } from "@/i18n/use-translation";
import type { MessageKey } from "@/i18n/messages";

const ADMIN_LINKS = [
  {
    href: ROUTES.settingsUsers,
    titleKey: "dashboard.admin.usersRoles",
    descriptionKey: "dashboard.admin.usersRolesDesc",
    icon: People,
  },
  {
    href: ROUTES.settingsMasterData,
    titleKey: "dashboard.admin.masterData",
    descriptionKey: "dashboard.admin.masterDataDesc",
    icon: Dataset,
  },
  {
    href: "/settings/master-data/crops",
    titleKey: "dashboard.admin.crops",
    descriptionKey: "dashboard.admin.cropsDesc",
    icon: Agriculture,
  },
  {
    href: "/settings/master-data/vehicle-types",
    titleKey: "dashboard.admin.vehicleTypes",
    descriptionKey: "dashboard.admin.vehicleTypesDesc",
    icon: DirectionsCar,
  },
  {
    href: "/settings/master-data/activity-types",
    titleKey: "dashboard.admin.activityTypes",
    descriptionKey: "dashboard.admin.activityTypesDesc",
    icon: WorkOutline,
  },
  {
    href: "/settings/master-data/buyers",
    titleKey: "dashboard.admin.buyers",
    descriptionKey: "dashboard.admin.buyersDesc",
    icon: LocalAtm,
  },
  {
    href: "/settings/master-data/agents",
    titleKey: "dashboard.admin.agents",
    descriptionKey: "dashboard.admin.agentsDesc",
    icon: Groups,
  },
  {
    href: ROUTES.settingsVillages,
    titleKey: "dashboard.admin.villages",
    descriptionKey: "dashboard.admin.villagesDesc",
    icon: Agriculture,
  },
] as const;

const ROLE_HINT_KEYS: Record<string, MessageKey> = {
  OWNER: "dashboard.role.OWNER",
  MANAGER: "dashboard.role.MANAGER",
  SUPERVISOR: "dashboard.role.SUPERVISOR",
  DRIVER: "dashboard.role.DRIVER",
  AGENT: "dashboard.role.AGENT",
  WORKER: "dashboard.role.WORKER",
  ACCOUNTANT: "dashboard.role.ACCOUNTANT",
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
  const { t } = useTranslation();
  const { user, role, canAccessAdmin, isError, error, isLoading } = useAuth();
  const summaryQuery = useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: fetchDashboardSummary,
    staleTime: 60_000,
    retry: 1,
  });

  const roleHint = role ? t(ROLE_HINT_KEYS[role] ?? "dashboard.sidebarHint") : t("dashboard.sidebarHint");

  return (
    <MuiPageShell
      title={t("dashboard.home")}
      description={
        canAccessAdmin ? t("dashboard.descriptionAdmin") : t("dashboard.description")
      }
    >
      <Stack spacing={3}>
        {isError && (
          <Alert severity="warning">
            {error instanceof Error ? error.message : t("common.signInAgain")}
          </Alert>
        )}

        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight={600}>
              {t("dashboard.welcome", { suffix: user?.name ? `, ${user.name}` : "" })}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {isLoading
                ? t("dashboard.loadingSession")
                : role
                  ? t("dashboard.signedInAs", { role })
                  : t("common.sessionUnavailable")}{" "}
              — {roleHint}
            </Typography>
          </CardContent>
        </Card>

        {summaryQuery.isError && (
          <Alert severity="info">
            {t("dashboard.countsUnavailable")}
            {summaryQuery.error instanceof Error ? `: ${summaryQuery.error.message}` : ""}.
          </Alert>
        )}

        {summaryQuery.data && (
          <>
            <Grid container spacing={2}>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat label={t("dashboard.stat.farmers")} value={summaryQuery.data.farmers ?? 0} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat
                  label={t("dashboard.stat.procurements")}
                  value={summaryQuery.data.procurements ?? 0}
                />
              </Grid>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat
                  label={t("dashboard.stat.payments")}
                  value={summaryQuery.data.farmer_payments ?? 0}
                />
              </Grid>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat label={t("dashboard.stat.assets")} value={summaryQuery.data.assets ?? 0} />
              </Grid>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat
                  label={t("dashboard.stat.fieldServices")}
                  value={summaryQuery.data.field_services ?? 0}
                />
              </Grid>
              <Grid size={{ xs: 6, sm: 4, md: 2 }}>
                <SummaryStat label={t("dashboard.stat.trips")} value={summaryQuery.data.vehicle_trips ?? 0} />
              </Grid>
            </Grid>
            <Grid container spacing={2}>
              <Grid size={{ xs: 6, sm: 3 }}>
                <SummaryStat label={t("dashboard.stat.users")} value={summaryQuery.data.users} />
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <SummaryStat label={t("dashboard.stat.villages")} value={summaryQuery.data.villages} />
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <SummaryStat
                  label={t("dashboard.stat.cropTypes")}
                  value={summaryQuery.data.crop_types}
                />
              </Grid>
              <Grid size={{ xs: 6, sm: 3 }}>
                <SummaryStat
                  label={t("dashboard.stat.documents")}
                  value={summaryQuery.data.documents}
                />
              </Grid>
            </Grid>
          </>
        )}

        {canAccessAdmin && (
          <>
            <Typography variant="subtitle1" fontWeight={600}>
              {t("dashboard.administration")}
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
                                  {t(link.titleKey)}
                                </Typography>
                                <ChevronRight fontSize="small" color="action" />
                              </Stack>
                              <Typography variant="body2" color="text.secondary">
                                {t(link.descriptionKey)}
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
