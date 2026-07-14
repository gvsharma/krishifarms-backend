"use client";

import {
  Alert,
  Box,
  Card,
  CardActionArea,
  CardContent,
  Chip,
  CircularProgress,
  Stack,
  Typography,
} from "@mui/material";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { ROUTES } from "@/constants/routes";
import { fetchAnalyticsCatalog } from "@/features/analytics/api";
import { tAnalytics } from "@/features/analytics/messages";

export default function AnalyticsHubPage() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["analytics", "catalog"],
    queryFn: fetchAnalyticsCatalog,
  });

  return (
    <MuiPageShell
      title={tAnalytics("en", "hubTitle")}
      description={tAnalytics("en", "hubDescription")}
    >
      <Alert severity="info" sx={{ mb: 2 }}>
        {tAnalytics("en", "reportsRedirect")} Legacy{" "}
        <Link href={ROUTES.reports}>/reports</Link> redirects here.
      </Alert>

      {isLoading ? (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      ) : null}

      {isError ? (
        <Alert severity="warning">
          {error instanceof Error ? error.message : "Could not load analytics catalog"}
        </Alert>
      ) : null}

      {data ? (
        <Stack spacing={3}>
          <Typography variant="body2" color="text.secondary">
            {data.live_count} live · {data.scaffold_count} scaffold · {data.data_plane}
          </Typography>
          <Box
            data-testid="analytics-hub-grid"
            sx={{
              display: "grid",
              gap: 1.5,
              gridTemplateColumns: {
                xs: "1fr",
                sm: "repeat(2, 1fr)",
                md: "repeat(3, 1fr)",
              },
            }}
          >
            {data.modules.map((mod) => (
              <Card
                key={mod.id}
                sx={{ border: "1px solid", borderColor: "divider" }}
                data-testid={`analytics-module-card-${mod.id}`}
              >
                <CardActionArea component={Link} href={mod.href}>
                  <CardContent>
                    <Stack direction="row" justifyContent="space-between" alignItems="center">
                      <Typography variant="h6">{mod.name}</Typography>
                      <Chip
                        size="small"
                        label={mod.status === "live" ? tAnalytics("en", "live") : tAnalytics("en", "scaffold")}
                        color={mod.status === "live" ? "success" : "default"}
                      />
                    </Stack>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                      {mod.description}
                    </Typography>
                  </CardContent>
                </CardActionArea>
              </Card>
            ))}
          </Box>
        </Stack>
      ) : null}
    </MuiPageShell>
  );
}
