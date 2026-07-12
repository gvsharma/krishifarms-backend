"use client";

import { Add } from "@mui/icons-material";
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
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useCallback, useMemo, useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { fetchFieldServices } from "@/features/field-services/api";
import { SERVICE_CATEGORIES } from "@/features/field-services/constants";
import { useTranslations } from "@/i18n/use-translations";

export default function FieldServicesPage() {
  const { t } = useTranslations();
  const [category, setCategory] = useState("");

  const categoryLabel = useCallback(
    (value: string) => {
      const key = `operations.fieldServices.categories.${value}`;
      const label = t(key);
      return label === key ? value.replace(/_/g, " ") : label;
    },
    [t],
  );

  const categories = useMemo(
    () => [
      { value: "", label: t("operations.fieldServices.allCategories") },
      ...SERVICE_CATEGORIES.map((c) => ({
        value: c.value,
        label: t(`operations.fieldServices.categories.${c.value}`),
      })),
    ],
    [t],
  );

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["field-services", category],
    queryFn: () =>
      fetchFieldServices({
        service_category: category || undefined,
        page_size: 50,
      }),
  });

  const recordCountLabel =
    data?.total === 1
      ? t("format.recordCount", { count: data.total })
      : t("format.recordCountPlural", { count: data?.total ?? 0 });

  return (
    <MuiPageShell
      title={t("operations.fieldServices.title")}
      description={t("operations.fieldServices.description")}
      actions={
        <Button component={Link} href="/field-services/new" variant="contained" startIcon={<Add />}>
          {t("operations.fieldServices.newService")}
        </Button>
      }
    >
      <Card sx={{ mb: 2, p: 2 }}>
        <TextField
          select
          size="small"
          label={t("operations.fieldServices.category")}
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          sx={{ minWidth: 220 }}
        >
          {categories.map((c) => (
            <MenuItem key={c.value || "all"} value={c.value}>
              {c.label}
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
            {error instanceof Error ? error.message : t("operations.fieldServices.loadError")}
          </Alert>
        )}

        {!isLoading && data && (
          <>
            <Box sx={{ px: 2, py: 1.5 }}>
              <Typography variant="body2" color="text.secondary">
                {recordCountLabel}
              </Typography>
            </Box>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>{t("operations.fieldServices.table.number")}</TableCell>
                    <TableCell>{t("operations.fieldServices.table.category")}</TableCell>
                    <TableCell>{t("operations.fieldServices.table.date")}</TableCell>
                    <TableCell>{t("operations.fieldServices.table.farmer")}</TableCell>
                    <TableCell align="right">{t("operations.fieldServices.table.totalInr")}</TableCell>
                    <TableCell align="right">{t("operations.fieldServices.table.pendingInr")}</TableCell>
                    <TableCell>{t("operations.fieldServices.table.status")}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data.items.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7}>
                        <Typography variant="body2" color="text.secondary" sx={{ py: 3, textAlign: "center" }}>
                          {t("operations.fieldServices.empty")}{" "}
                          <Typography
                            component={Link}
                            href="/field-services/new"
                            variant="body2"
                            color="primary"
                            sx={{ textDecoration: "underline" }}
                          >
                            {t("operations.fieldServices.emptyAction")}
                          </Typography>
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    data.items.map((row) => (
                      <TableRow
                        key={row.id}
                        hover
                        component={Link}
                        href={`/field-services/${row.id}`}
                        sx={{ cursor: "pointer", textDecoration: "none" }}
                      >
                        <TableCell>{row.record_number}</TableCell>
                        <TableCell sx={{ textTransform: "capitalize" }}>
                          {categoryLabel(row.service_category)}
                        </TableCell>
                        <TableCell>{row.service_date}</TableCell>
                        <TableCell>
                          {row.farmer_name ?? t("common.dash")}
                          {row.farmer_phone ? (
                            <Typography variant="caption" display="block" color="text.secondary">
                              {row.farmer_phone}
                            </Typography>
                          ) : null}
                        </TableCell>
                        <TableCell align="right">{row.total_amount}</TableCell>
                        <TableCell align="right">{row.pending_amount}</TableCell>
                        <TableCell>
                          <Chip label={row.status} size="small" variant="outlined" />
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </>
        )}
      </Card>
    </MuiPageShell>
  );
}
