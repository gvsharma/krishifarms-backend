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
  Category,
  ChevronRight,
  DirectionsCar,
  Groups,
  LocalAtm,
  Payments,
  Store,
  WorkOutline,
} from "@mui/icons-material";
import Link from "next/link";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { useTranslations } from "@/i18n/use-translations";

const MASTER_LINK_KEYS = [
  { href: "/settings/master-data/crops", key: "cropTypes", icon: Agriculture },
  { href: "/settings/master-data/crop-prices", key: "cropPrices", icon: LocalAtm },
  { href: "/settings/master-data/buyers", key: "buyers", icon: Store },
  { href: "/settings/master-data/agents", key: "agents", icon: Groups },
  { href: "/settings/master-data/vehicle-types", key: "vehicleTypes", icon: DirectionsCar },
  { href: "/settings/master-data/activity-types", key: "activityTypes", icon: WorkOutline },
  { href: "/settings/master-data/expense-categories", key: "expenseCategories", icon: Category },
  { href: "/settings/master-data/payment-modes", key: "paymentModes", icon: Payments },
  { href: "/settings/villages", key: "villages", icon: Agriculture },
] as const;

export default function SettingsMasterDataPage() {
  const { t } = useTranslations();

  return (
    <MuiPageShell
      title={t("settings.masterDataHub.title")}
      description={t("settings.masterDataHub.description")}
    >
      <Grid container spacing={2}>
        {MASTER_LINK_KEYS.map((link) => {
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
                            {t(`catalog.${link.key}`)}
                          </Typography>
                          <ChevronRight fontSize="small" color="action" />
                        </Stack>
                        <Typography variant="body2" color="text.secondary">
                          {t(`catalog.${link.key}Desc`)}
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
