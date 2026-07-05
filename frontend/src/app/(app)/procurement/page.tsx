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
import { useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import {
  fetchProcurements,
  formatInr,
  STATUS_LABELS,
  type ProcurementStatus,
} from "@/features/procurements/api";

export default function ProcurementPage() {
  const [status, setStatus] = useState<ProcurementStatus | "">("");

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["procurements", status],
    queryFn: () => fetchProcurements({ status: status || undefined }),
  });

  return (
    <MuiPageShell
      title="Procurement"
      description="Intake tickets from draft through confirmation."
      actions={
        <Button component={Link} href="/procurement/new" variant="contained" startIcon={<Add />}>
          New procurement
        </Button>
      }
    >
      <Card sx={{ mb: 2, p: 2 }}>
        <TextField
          select
          size="small"
          label="Status filter"
          value={status}
          onChange={(e) => setStatus(e.target.value as ProcurementStatus | "")}
          sx={{ minWidth: 220 }}
        >
          <MenuItem value="">All statuses</MenuItem>
          {(Object.keys(STATUS_LABELS) as ProcurementStatus[]).map((key) => (
            <MenuItem key={key} value={key}>
              {STATUS_LABELS[key]}
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
            {error instanceof Error ? error.message : "Could not load procurements"}
          </Alert>
        )}

        {!isLoading && data && (
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Ticket</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Farmer</TableCell>
                  <TableCell>Crop</TableCell>
                  <TableCell>Net (kg)</TableCell>
                  <TableCell>Amount</TableCell>
                  <TableCell>Status</TableCell>
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
                    <TableCell>{row.farmer_name ?? "—"}</TableCell>
                    <TableCell>{row.crop_type_name ?? "—"}</TableCell>
                    <TableCell>{row.net_weight_kg}</TableCell>
                    <TableCell>{formatInr(row.net_amount)}</TableCell>
                    <TableCell>
                      <Chip label={STATUS_LABELS[row.status]} size="small" />
                    </TableCell>
                  </TableRow>
                ))}
                {data.items.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography variant="body2" color="text.secondary" sx={{ py: 3 }}>
                        No procurements yet — create a draft to get started
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
