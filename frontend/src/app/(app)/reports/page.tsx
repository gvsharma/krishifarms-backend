"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Box, CircularProgress, Typography } from "@mui/material";
import { ROUTES } from "@/constants/routes";
import { tAnalytics } from "@/features/analytics/messages";
import { useLocale } from "@/i18n/use-translation";

/** Legacy reports registry → Analytics Hub. */
export default function ReportsRedirectPage() {
  const router = useRouter();
  const locale = useLocale();

  useEffect(() => {
    router.replace(ROUTES.analytics);
  }, [router]);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 2, py: 10 }}>
      <CircularProgress size={28} />
      <Typography color="text.secondary">{tAnalytics(locale, "reportsRedirect")}</Typography>
    </Box>
  );
}
