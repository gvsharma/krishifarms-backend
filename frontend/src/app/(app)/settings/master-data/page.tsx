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

const MASTER_LINKS = [
  {
    href: "/settings/master-data/crops",
    title: "Crop types",
    description: "Paddy, corn, maize, cotton, grams, oilseeds, and more",
    icon: Agriculture,
  },
  {
    href: "/settings/master-data/crop-prices",
    title: "Crop price rules",
    description: "Effective rates per quintal for procurement pricing",
    icon: LocalAtm,
  },
  {
    href: "/settings/master-data/buyers",
    title: "Buyers",
    description: "Mill and trader contacts for procurement",
    icon: Store,
  },
  {
    href: "/settings/master-data/agents",
    title: "Field agents",
    description: "Collection and village agent roster",
    icon: Groups,
  },
  {
    href: "/settings/master-data/vehicle-types",
    title: "Vehicle types",
    description: "Tractor–Drone catalog plus John Deere, Bolero, DCM inventory",
    icon: DirectionsCar,
  },
  {
    href: "/settings/master-data/activity-types",
    title: "Activity types",
    description: "Tractor, transport, fertiliser, seeds, and vehicle ops service catalog",
    icon: WorkOutline,
  },
  {
    href: "/settings/master-data/expense-categories",
    title: "Expense categories",
    description: "Fuel, labour, repairs, and other expense buckets",
    icon: Category,
  },
  {
    href: "/settings/master-data/payment-modes",
    title: "Payment modes",
    description: "Cash, UPI, bank transfer settlement modes",
    icon: Payments,
  },
  {
    href: "/settings/villages",
    title: "Villages",
    description: "Geography master for farmers and trips",
    icon: Agriculture,
  },
] as const;

export default function SettingsMasterDataPage() {
  return (
    <MuiPageShell
      title="Master data"
      description="Admin catalogs shared by the CRM web app and Android field app."
    >
      <Grid container spacing={2}>
        {MASTER_LINKS.map((link) => {
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
