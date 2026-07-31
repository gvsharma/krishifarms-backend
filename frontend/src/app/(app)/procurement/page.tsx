"use client";

import {
  Alert,
  Box,
  Button,
  Card,
  Chip,
  CircularProgress,
  MenuItem,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { Add } from "@mui/icons-material";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "next/navigation";
import { useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { ResponsiveTable } from "@/components/ui/responsive-table";
import {
  fetchProcurements,
  formatInr,
  STATUS_COLORS,
  STATUS_LABELS,
  type ProcurementStatus,
} from "@/features/procurements/api";

export default function ProcurementPage() {
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<ProcurementStatus | "">("");
  const dateFrom = searchParams.get("date_from") ?? undefined;
  const dateTo = searchParams.get("date_to") ?? undefined;
  const villageId = searchParams.get("village_id") ?? undefined;
  const cropTypeId = searchParams.get("crop_type_id") ?? undefined;
  const farmerId = searchParams.get("farmer_id") ?? undefined;

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["procurements", status, dateFrom, dateTo, villageId, cropTypeId, farmerId],
    queryFn: () =>
      fetchProcurements({
        status: status || undefined,
        date_from: dateFrom,
        date_to: dateTo,
        village_id: villageId,
        crop_type_id: cropTypeId,
        farmer_id: farmerId,
      }),
  });

  return (
    <MuiPageShell
      title="Procurement"
      description="Intake tickets from draft through confirmation."
      actions={
        <Stack direction="row" spacing={1}>
          <Button component={Link} href="/procurement/sales" variant="outlined">
            Sales
          </Button>
          <Button component={Link} href="/procurement/new" variant="contained" startIcon={<Add />}>
            New procurement
          </Button>
        </Stack>
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
          <ResponsiveTable>
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
                      <Chip
                        label={STATUS_LABELS[row.status]}
                        color={STATUS_COLORS[row.status]}
                        size="small"
                      />
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
          </ResponsiveTable>
        )}
      </Card>
    </MuiPageShell>
  );
}
