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
import { useTranslations } from "@/i18n/use-translations";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { ROUTES } from "@/constants/routes";
import { useAuth } from "@/hooks/use-auth";
import type { AppRole } from "@/features/auth/types";

const ADMIN_LINK_KEYS = [
  {
    href: ROUTES.settingsUsers,
    titleKey: "usersRoles",
    icon: People,
  },
  {
    href: ROUTES.settingsMasterData,
    titleKey: "masterDataHub",
    icon: Dataset,
  },
  {
    href: "/settings/master-data/crops",
    titleKey: "cropTypes",
    icon: Agriculture,
  },
  {
    href: "/settings/master-data/vehicle-types",
    titleKey: "vehicleTypes",
    icon: DirectionsCar,
  },
  {
    href: "/settings/master-data/activity-types",
    titleKey: "activityTypes",
    icon: WorkOutline,
  },
  {
    href: "/settings/master-data/buyers",
    titleKey: "buyers",
    icon: LocalAtm,
  },
  {
    href: "/settings/master-data/agents",
    titleKey: "fieldAgents",
    icon: Groups,
  },
  {
    href: ROUTES.settingsVillages,
    titleKey: "villages",
    icon: Agriculture,
  },
] as const;

export function DashboardHome() {
  const { t } = useTranslations();
  const { user, role, canAccessAdmin, isError, error, isLoading } = useAuth();

  const roleLabel =
    role && (["OWNER", "MANAGER", "SUPERVISOR", "AGENT", "DRIVER", "WORKER", "ACCOUNTANT"] as const).includes(
      role as AppRole,
    )
      ? t(`roles.${role as AppRole}`)
      : role;

  return (
    <MuiPageShell
      title={t("dashboard.title")}
      description={canAccessAdmin ? t("dashboard.descriptionAdmin") : t("dashboard.descriptionUser")}
    >
      <Stack spacing={3}>
        {isError && (
          <Alert severity="warning">
            {error instanceof Error ? error.message : t("dashboard.sessionError")}
          </Alert>
        )}

        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight={600}>
              {t("dashboard.welcome", {
                commaName: user?.name ? t("dashboard.welcomeCommaName", { name: user.name }) : "",
              })}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {isLoading
                ? t("dashboard.loadingSession")
                : role
                  ? t("dashboard.signedInAs", { role: roleLabel ?? role })
                  : t("dashboard.sessionUnavailable")}{" "}
              {t("dashboard.sidebarHint")}
            </Typography>
          </CardContent>
        </Card>

        {canAccessAdmin && (
          <>
            <Typography variant="subtitle1" fontWeight={600}>
              {t("dashboard.administration")}
            </Typography>
            <Grid container spacing={2}>
              {ADMIN_LINK_KEYS.map((link) => {
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
                                  {t(`dashboard.adminLinks.${link.titleKey}.title`)}
                                </Typography>
                                <ChevronRight fontSize="small" color="action" />
                              </Stack>
                              <Typography variant="body2" color="text.secondary">
                                {t(`dashboard.adminLinks.${link.titleKey}.description`)}
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
