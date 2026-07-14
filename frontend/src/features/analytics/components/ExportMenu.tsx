"use client";

import { Button, Menu, MenuItem } from "@mui/material";
import { FileDownload } from "@mui/icons-material";
import { useState } from "react";
import { exportAnalyticsCsv } from "../api";
import type { AnalyticsFilterState } from "../types";
import { tAnalytics, type AnalyticsLocale } from "../messages";

export function ExportMenu({
  module,
  filters,
  locale = "en",
}: {
  module: string;
  filters: AnalyticsFilterState;
  locale?: AnalyticsLocale;
}) {
  const [anchor, setAnchor] = useState<null | HTMLElement>(null);
  const [busy, setBusy] = useState(false);

  async function onCsv() {
    setBusy(true);
    try {
      const { blob, filename } = await exportAnalyticsCsv(module, filters);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
    } finally {
      setBusy(false);
      setAnchor(null);
    }
  }

  return (
    <>
      <Button
        data-testid="analytics-export"
        variant="outlined"
        startIcon={<FileDownload />}
        onClick={(e) => setAnchor(e.currentTarget)}
        disabled={busy}
      >
        {tAnalytics(locale, "exportCsv")}
      </Button>
      <Menu open={Boolean(anchor)} anchorEl={anchor} onClose={() => setAnchor(null)}>
        <MenuItem onClick={onCsv}>{tAnalytics(locale, "exportCsv")}</MenuItem>
        <MenuItem disabled>Excel (Phase 2)</MenuItem>
        <MenuItem disabled>PDF (Phase 2)</MenuItem>
      </Menu>
    </>
  );
}
