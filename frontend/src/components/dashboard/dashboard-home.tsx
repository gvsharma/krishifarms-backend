"use client";

import {
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
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { ROUTES } from "@/constants/routes";
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
    description: "Geography master (read/create/edit)",
    icon: Agriculture,
  },
] as const;

export function DashboardHome() {
  const { user, role, canAccessAdmin } = useAuth();

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
        <Card>
          <CardContent>
            <Typography variant="h6" fontWeight={600}>
              Welcome{user?.name ? `, ${user.name}` : ""}
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
              {role ? `Signed in as ${role}` : "Loading session…"} — use the sidebar for farmers,
              procurement, and field services.
            </Typography>
          </CardContent>
        </Card>

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
