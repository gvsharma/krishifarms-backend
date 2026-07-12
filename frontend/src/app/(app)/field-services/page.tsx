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
import { useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { fetchFieldServices } from "@/features/field-services/api";
import { SERVICE_CATEGORIES, categoryLabel } from "@/features/field-services/constants";

const CATEGORIES = [{ value: "", label: "All categories" }, ...SERVICE_CATEGORIES] as const;

export default function FieldServicesPage() {
  const [category, setCategory] = useState("");

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["field-services", category],
    queryFn: () =>
      fetchFieldServices({
        service_category: category || undefined,
        page_size: 50,
      }),
  });

  return (
    <MuiPageShell
      title="Field services"
      description="Operational services — tractor work, transport, fertiliser, seeds, agri-finance, vehicle and godown ops."
      actions={
        <Button component={Link} href="/field-services/new" variant="contained" startIcon={<Add />}>
          New service
        </Button>
      }
    >
      <Card sx={{ mb: 2, p: 2 }}>
        <TextField
          select
          size="small"
          label="Category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          sx={{ minWidth: 220 }}
        >
          {CATEGORIES.map((c) => (
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
            {error instanceof Error ? error.message : "Could not load field services"}
          </Alert>
        )}

        {!isLoading && data && (
          <>
            <Box sx={{ px: 2, py: 1.5 }}>
              <Typography variant="body2" color="text.secondary">
                {data.total} record{data.total === 1 ? "" : "s"}
              </Typography>
            </Box>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Number</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Farmer</TableCell>
                    <TableCell align="right">Total (₹)</TableCell>
                    <TableCell align="right">Pending (₹)</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {data.items.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7}>
                        <Typography variant="body2" color="text.secondary" sx={{ py: 3, textAlign: "center" }}>
                          No records yet.{" "}
                          <Typography
                            component={Link}
                            href="/field-services/new"
                            variant="body2"
                            color="primary"
                            sx={{ textDecoration: "underline" }}
                          >
                            Create your first service record
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
                          {row.farmer_name ?? "—"}
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
