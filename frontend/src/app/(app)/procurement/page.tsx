"use client";

import {
  Alert,
  Box,
  Button,
  Card,
  Chip,
  CircularProgress,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { Add } from "@mui/icons-material";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useCallback, useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import {
  fetchProcurements,
  formatInr,
  type ProcurementStatus,
} from "@/features/procurements/api";
import { useTranslations } from "@/i18n/use-translations";

const PROCUREMENT_STATUSES: ProcurementStatus[] = [
  "draft",
  "pending_weighment",
  "weighed",
  "priced",
  "confirmed",
  "paid_partial",
  "paid_full",
  "cancelled",
  "reversed",
];

export default function ProcurementPage() {
  const { t } = useTranslations();
  const [status, setStatus] = useState<ProcurementStatus | "">("");

  const statusLabel = useCallback(
    (key: ProcurementStatus) => t(`operations.procurement.status.${key}`),
    [t],
  );

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["procurements", status],
    queryFn: () => fetchProcurements({ status: status || undefined }),
  });

  return (
    <MuiPageShell
      title={t("operations.procurement.title")}
      description={t("operations.procurement.description")}
      actions={
        <Button component={Link} href="/procurement/new" variant="contained" startIcon={<Add />}>
          {t("operations.procurement.newProcurement")}
        </Button>
      }
    >
      <Card sx={{ mb: 2, p: 2 }}>
        <TextField
          select
          size="small"
          label={t("operations.procurement.statusFilter")}
          value={status}
          onChange={(e) => setStatus(e.target.value as ProcurementStatus | "")}
          sx={{ minWidth: 220 }}
        >
          <MenuItem value="">{t("operations.procurement.allStatuses")}</MenuItem>
          {PROCUREMENT_STATUSES.map((key) => (
            <MenuItem key={key} value={key}>
              {statusLabel(key)}
            </MenuItem>
          ))}
        </TextField>
      </Card>

      <Card sx={{ overflow: "hidden" }}>
        {isLoading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
            <CircularProgress />
          </Box>
        )}

        {isError && (
          <Alert severity="warning" sx={{ m: 2 }}>
            {error instanceof Error ? error.message : t("operations.procurement.loadError")}
          </Alert>
        )}

        {!isLoading && data && (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>{t("operations.procurement.table.ticket")}</TableCell>
                  <TableCell>{t("operations.procurement.table.date")}</TableCell>
                  <TableCell>{t("operations.procurement.table.farmer")}</TableCell>
                  <TableCell>{t("operations.procurement.table.crop")}</TableCell>
                  <TableCell>{t("operations.procurement.table.netKg")}</TableCell>
                  <TableCell>{t("operations.procurement.table.amount")}</TableCell>
                  <TableCell>{t("operations.procurement.table.status")}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.items.map((row) => (
                  <TableRow
                    key={row.id}
                    hover
                    component={Link}
                    href={`/procurement/${row.id}?date=${row.procurement_date}`}
                    sx={{ cursor: "pointer", textDecoration: "none" }}
                  >
                    <TableCell>{row.procurement_number}</TableCell>
                    <TableCell>{row.procurement_date}</TableCell>
                    <TableCell>{row.farmer_name ?? t("common.dash")}</TableCell>
                    <TableCell>{row.crop_type_name ?? t("common.dash")}</TableCell>
                    <TableCell>{row.net_weight_kg}</TableCell>
                    <TableCell>{formatInr(row.net_amount)}</TableCell>
                    <TableCell>
                      <Chip label={statusLabel(row.status)} size="small" />
                    </TableCell>
                  </TableRow>
                ))}
                {data.items.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                        {t("operations.procurement.empty")}
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Card>
    </MuiPageShell>
  );
}
