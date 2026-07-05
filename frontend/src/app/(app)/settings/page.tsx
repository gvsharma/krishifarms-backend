"use client";

import {
  Card,
  CardActionArea,
  CardContent,
  Grid2 as Grid,
  Stack,
  Typography,
} from "@mui/material";
import { ChevronRight, Dataset, LocationCity, People } from "@mui/icons-material";
import Link from "next/link";
import { ROUTES } from "@/constants/routes";
import { MuiPageShell } from "@/components/shell/mui-page-shell";

const SETTINGS_LINKS = [
  {
    href: ROUTES.settingsUsers,
    title: "Users & roles",
    description: "Members, RBAC roles, and access control",
    icon: People,
  },
  {
    href: ROUTES.settingsVillages,
    title: "Villages",
    description: "Geography master for farmers and trips",
    icon: LocationCity,
  },
  {
    href: ROUTES.settingsMasterData,
    title: "Master data",
    description: "Crops, buyers, agents, and catalogs",
    icon: Dataset,
  },
] as const;

export default function SettingsPage() {
  return (
    <MuiPageShell
      title="Settings"
      description="Organization, users, roles, master data, and locale preferences."
    >
      <Grid container spacing={2}>
        {SETTINGS_LINKS.map((link) => {
          const Icon = link.icon;
          return (
            <Grid key={link.href} size={{ xs: 12, sm: 6, md: 4 }}>
              <Card>
                <CardActionArea component={Link} href={link.href}>
                  <CardContent>
                    <Stack direction="row" spacing={2} alignItems="flex-start">
                      <Icon color="primary" />
                      <Stack spacing={0.5} sx={{ flex: 1 }}>
                        <Stack direction="row" alignItems="center" justifyContent="space-between">
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
    </MuiPageShell>
  );
}
