"use client";

import {
  Card,
  CardActionArea,
  CardContent,
  Grid2 as Grid,
  Stack,
  Typography,
} from "@mui/material";
import { ChevronRight, Dataset, Language, LocationCity, People } from "@mui/icons-material";
import Link from "next/link";
import { ROUTES } from "@/constants/routes";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { useTranslation } from "@/i18n/use-translation";
import type { MessageKey } from "@/i18n/messages";

const SETTINGS_LINKS = [
  {
    href: ROUTES.settingsPreferences,
    titleKey: "settings.preferences",
    descriptionKey: "settings.preferencesDesc",
    icon: Language,
    allRoles: true,
  },
  {
    href: ROUTES.settingsUsers,
    titleKey: "settings.usersRoles",
    descriptionKey: "settings.usersRolesDesc",
    icon: People,
  },
  {
    href: ROUTES.settingsVillages,
    titleKey: "settings.villages",
    descriptionKey: "settings.villagesDesc",
    icon: LocationCity,
  },
  {
    href: ROUTES.settingsMasterData,
    titleKey: "settings.masterData",
    descriptionKey: "settings.masterDataDesc",
    icon: Dataset,
  },
] as const;

export default function SettingsPage() {
  const { t } = useTranslation();

  return (
    <MuiPageShell title={t("settings.title")} description={t("settings.description")}>
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
                            {t(link.titleKey as MessageKey)}
                          </Typography>
                          <ChevronRight fontSize="small" color="action" />
                        </Stack>
                        <Typography variant="body2" color="text.secondary">
                          {t(link.descriptionKey as MessageKey)}
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
