"use client";

import { Alert, AlertTitle, Box, Collapse } from "@mui/material";
import { CloudOff } from "@mui/icons-material";
import { useApiHealth } from "@/hooks/use-api-health";
import { useTranslation } from "@/i18n/use-translation";

type ApiHealthBannerProps = {
  /** Sticky offset below fixed AppBar (px). Omit on full-width pages like login. */
  stickyTop?: number;
};

export function ApiHealthBanner({ stickyTop }: ApiHealthBannerProps) {
  const { t } = useTranslation();
  const { isFetched, isError } = useApiHealth();
  const show = isFetched && isError;

  return (
    <Collapse in={show}>
      <Box
        sx={
          stickyTop != null
            ? {
                position: "sticky",
                top: stickyTop,
                zIndex: (theme) => theme.zIndex.appBar - 1,
              }
            : undefined
        }
      >
        <Alert
          severity="warning"
          icon={<CloudOff fontSize="inherit" />}
          sx={{
            borderRadius: 0,
            "& .MuiAlert-message": { width: "100%" },
          }}
        >
          <AlertTitle sx={{ mb: 0.25 }}>{t("common.apiSleepingTitle")}</AlertTitle>
          {t("common.apiSleepingDescription")}
        </Alert>
      </Box>
    </Collapse>
  );
}
