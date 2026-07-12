"use client";

import {
  Alert,
  Box,
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
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { fetchFieldServices } from "@/features/field-services/api";

const CATEGORIES = [
  { value: "", label: "All categories" },
  { value: "field_service", label: "Field services" },
  { value: "tractor_work", label: "Tractor work" },
  { value: "transport", label: "Transport" },
  { value: "fertiliser", label: "Fertiliser" },
  { value: "seeds", label: "Seeds" },
  { value: "agri_finance", label: "Agri-finance" },
  { value: "vehicle_ops", label: "Vehicle ops" },
  { value: "godown", label: "Godown" },
] as const;

function formatCategory(value: string) {
  return value.replace(/_/g, " ");
}

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
                          No records yet. Create via API or Android app (Phase 2 forms).
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ) : (
                    data.items.map((row) => (
                      <TableRow key={row.id} hover>
                        <TableCell>{row.record_number}</TableCell>
                        <TableCell sx={{ textTransform: "capitalize" }}>
                          {formatCategory(row.service_category)}
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
