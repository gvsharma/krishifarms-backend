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
  Groups,
  LocalShipping,
  Store,
} from "@mui/icons-material";
import Link from "next/link";
import { MuiPageShell } from "@/components/shell/mui-page-shell";

const MASTER_LINKS = [
  {
    href: "/settings/master-data/crops",
    title: "Crop types",
    description: "Paddy, corn, and seasonal crop catalog",
    icon: Agriculture,
    status: "W2",
  },
  {
    href: "/settings/master-data/buyers",
    title: "Buyers",
    description: "Mill and trader contacts for procurement",
    icon: Store,
    status: "W2",
  },
  {
    href: "/settings/master-data/agents",
    title: "Field agents",
    description: "Collection and village agent roster",
    icon: Groups,
    status: "W2",
  },
  {
    href: "/settings/villages",
    title: "Villages",
    description: "Geography master — live CRUD stub",
    icon: LocalShipping,
    status: "W1",
  },
] as const;

export default function SettingsMasterDataPage() {
  return (
    <MuiPageShell
      title="Master data"
      description="Links to crops, buyers, agents, and related admin catalogs."
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
                        <Typography variant="caption" color="primary">
                          Phase {link.status}
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
