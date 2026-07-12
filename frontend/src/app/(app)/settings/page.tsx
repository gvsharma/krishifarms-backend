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
import { useTranslations } from "@/i18n/use-translations";
import { ROUTES } from "@/constants/routes";
import { MuiPageShell } from "@/components/shell/mui-page-shell";

const SETTINGS_LINKS = [
  { href: ROUTES.settingsUsers, cardKey: "usersRoles" as const, icon: People },
  { href: ROUTES.settingsVillages, cardKey: "villages" as const, icon: LocationCity },
  { href: ROUTES.settingsMasterData, cardKey: "masterData" as const, icon: Dataset },
] as const;

export default function SettingsPage() {
  const { t } = useTranslations();

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
                            {t(`settings.cards.${link.cardKey}.title`)}
                          </Typography>
                          <ChevronRight fontSize="small" color="action" />
                        </Stack>
                        <Typography variant="body2" color="text.secondary">
                          {t(`settings.cards.${link.cardKey}.description`)}
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
