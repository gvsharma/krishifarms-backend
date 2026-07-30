"use client";

import {
  Box,
  Card,
  Chip,
  CircularProgress,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { ROUTES } from "@/constants/routes";
import {
  STATUS_COLORS,
  STATUS_LABELS,
  fetchProcurements,
  formatInr,
  type ProcurementListItem,
} from "@/features/procurements/api";

export default function MyProcurementsPage() {
  const query = useQuery({
    queryKey: ["my-procurements"],
    queryFn: () => fetchProcurements({ pageSize: 50 }),
  });

  const items = query.data?.items ?? [];

  return (
    <MuiPageShell
      title="My procurements"
      description="Your crop deliveries and payment summary"
    >
      {query.isLoading ? (
        <Box display="flex" justifyContent="center" py={6}>
          <CircularProgress />
        </Box>
      ) : items.length === 0 ? (
        <Card sx={{ p: 3 }}>
          <Typography color="text.secondary">
            No procurements recorded for your account yet.
          </Typography>
        </Card>
      ) : (
        <Card>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Ticket</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Crop</TableCell>
                <TableCell align="right">Net weight</TableCell>
                <TableCell align="right">Net amount</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((row: ProcurementListItem) => (
                <TableRow key={`${row.id}-${row.procurement_date}`} hover>
                  <TableCell>
                    <Link
                      href={`${ROUTES.procurement}/${row.id}?date=${row.procurement_date}`}
                      style={{ textDecoration: "none", color: "inherit", fontWeight: 600 }}
                    >
                      {row.procurement_number}
                    </Link>
                  </TableCell>
                  <TableCell>{row.procurement_date}</TableCell>
                  <TableCell>{row.crop_type_name ?? "—"}</TableCell>
                  <TableCell align="right">{row.net_weight_kg} kg</TableCell>
                  <TableCell align="right">{formatInr(row.net_amount)}</TableCell>
                  <TableCell>
                    <Chip
                      size="small"
                      label={STATUS_LABELS[row.status]}
                      color={STATUS_COLORS[row.status]}
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      )}
      <Stack direction="row" spacing={1} mt={2}>
        <Typography variant="caption" color="text.secondary">
          Tap a ticket for full weight, rate, and deduction breakdown.
        </Typography>
      </Stack>
    </MuiPageShell>
  );
}
