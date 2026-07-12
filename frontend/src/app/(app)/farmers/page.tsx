"use client";

import {
  Alert,
  Box,
  Button,
  Card,
  Chip,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { Add, Search } from "@mui/icons-material";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { fetchFarmers } from "@/features/farmers/api";
import { useTranslations } from "@/i18n/use-translations";

export default function FarmersPage() {
  const { t } = useTranslations();
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["farmers", query],
    queryFn: () => fetchFarmers({ q: query || undefined }),
  });

  return (
    <MuiPageShell
      title={t("operations.farmers.title")}
      description={t("operations.farmers.description")}
      actions={
        <Button component={Link} href="/farmers/new" variant="contained" startIcon={<Add />}>
          {t("operations.farmers.addFarmer")}
        </Button>
      }
    >
      <Card sx={{ mb: 2, p: 2 }}>
        <Box sx={{ display: "flex", gap: 1, alignItems: "center" }}>
          <TextField
            size="small"
            placeholder={t("operations.farmers.searchPlaceholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && setQuery(search.trim())}
            sx={{ flex: 1, maxWidth: 420 }}
          />
          <Button variant="outlined" startIcon={<Search />} onClick={() => setQuery(search.trim())}>
            {t("common.search")}
          </Button>
        </Box>
      </Card>

      <Card sx={{ overflow: "hidden" }}>
        {isLoading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
            <CircularProgress />
          </Box>
        )}

        {isError && (
          <Alert severity="warning" sx={{ m: 2 }}>
            {error instanceof Error ? error.message : t("operations.farmers.loadError")}
          </Alert>
        )}

        {!isLoading && data && (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>{t("operations.farmers.table.code")}</TableCell>
                  <TableCell>{t("operations.farmers.table.name")}</TableCell>
                  <TableCell>{t("operations.farmers.table.phone")}</TableCell>
                  <TableCell>{t("operations.farmers.table.village")}</TableCell>
                  <TableCell>{t("operations.farmers.table.status")}</TableCell>
                  <TableCell>{t("operations.farmers.table.tags")}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.items.map((farmer) => (
                  <TableRow key={farmer.id} hover component={Link} href={`/farmers/${farmer.id}`} sx={{ cursor: "pointer", textDecoration: "none" }}>
                    <TableCell>{farmer.farmer_code}</TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight={600}>
                        {farmer.full_name}
                      </Typography>
                      {farmer.full_name_te && (
                        <Typography variant="caption" color="text.secondary">
                          {farmer.full_name_te}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>{farmer.phone_primary}</TableCell>
                    <TableCell>{farmer.village_name ?? t("common.dash")}</TableCell>
                    <TableCell>{farmer.status}</TableCell>
                    <TableCell>
                      {farmer.tags.map((tag) => (
                        <Chip key={tag} label={tag} size="small" sx={{ mr: 0.5 }} />
                      ))}
                    </TableCell>
                  </TableRow>
                ))}
                {data.items.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6} align="center">
                      <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                        {t("operations.farmers.empty")}
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
