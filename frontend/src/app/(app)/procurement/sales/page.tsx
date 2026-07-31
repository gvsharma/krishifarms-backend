"use client";

import {
  Alert,
  Box,
  Button,
  Card,
  Checkbox,
  Chip,
  CircularProgress,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { ArrowBack, LocalShipping } from "@mui/icons-material";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { SearchableSelect } from "@/components/ui/searchable-select";
import {
  PremiumDialog,
  PremiumDialogActions,
  PremiumDialogContent,
  PremiumDialogTitle,
} from "@/components/ui/premium-dialog";
import { fetchBuyers, type Buyer } from "@/features/master-data/api";
import { assignBuyer, fetchProcurements, formatInr } from "@/features/procurements/api";
import { TOUCH_FIELD_SX } from "@/features/field-services/work-details";

export default function ProcurementSalesPage() {
  const queryClient = useQueryClient();
  const today = useMemo(() => new Date().toISOString().slice(0, 10), []);
  const [selected, setSelected] = useState<Record<string, string>>({});
  const [dialogOpen, setDialogOpen] = useState(false);
  const [buyerId, setBuyerId] = useState("");
  const [saleRate, setSaleRate] = useState("");
  const [saleDate, setSaleDate] = useState(today);

  const procurementsQuery = useQuery({
    queryKey: ["procurements", "confirmed-sales"],
    queryFn: () => fetchProcurements({ status: "confirmed", pageSize: 100 }),
  });
  const buyersQuery = useQuery({
    queryKey: ["buyers-sales"],
    queryFn: () => fetchBuyers(1, 100),
  });

  const rows = procurementsQuery.data?.items ?? [];
  const buyers = (buyersQuery.data?.items ?? []).filter((b) => b.is_active);
  const selectedIds = Object.keys(selected);

  const toggle = (id: string, procurementDate: string) => {
    setSelected((prev) => {
      const next = { ...prev };
      if (next[id]) delete next[id];
      else next[id] = procurementDate;
      return next;
    });
  };

  const assignMutation = useMutation({
    mutationFn: () =>
      assignBuyer({
        items: selectedIds.map((id) => ({ procurement_id: id, procurement_date: selected[id] })),
        buyer_id: buyerId,
        sale_rate_per_quintal: saleRate.trim() || null,
        sale_date: saleDate || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["procurements"] });
      setDialogOpen(false);
      setSelected({});
      setBuyerId("");
      setSaleRate("");
    },
  });

  return (
    <MuiPageShell
      title="Sales · assign buyer"
      description="Group confirmed procurements and assign them to one buyer with a sale rate."
      actions={
        <Button component={Link} href="/procurement" startIcon={<ArrowBack />} variant="outlined">
          Back to board
        </Button>
      }
    >
      {(procurementsQuery.isLoading || buyersQuery.isLoading) && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {!procurementsQuery.isLoading && (
        <Stack spacing={2}>
          <Stack direction="row" spacing={2} alignItems="center">
            <Typography variant="body2" color="text.secondary">
              {selectedIds.length} selected
            </Typography>
            <Button
              variant="contained"
              startIcon={<LocalShipping />}
              disabled={selectedIds.length === 0}
              onClick={() => setDialogOpen(true)}
            >
              Assign buyer
            </Button>
          </Stack>

          <Card>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell padding="checkbox" />
                  <TableCell>Ticket</TableCell>
                  <TableCell>Farmer</TableCell>
                  <TableCell align="right">Net (kg)</TableCell>
                  <TableCell align="right">Farmer net</TableCell>
                  <TableCell>Buyer</TableCell>
                  <TableCell align="right">Sale ₹/qtl</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.id} hover selected={Boolean(selected[row.id])}>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={Boolean(selected[row.id])}
                        onChange={() => toggle(row.id, row.procurement_date)}
                      />
                    </TableCell>
                    <TableCell>{row.procurement_number}</TableCell>
                    <TableCell>{row.farmer_name ?? "—"}</TableCell>
                    <TableCell align="right">{row.net_weight_kg}</TableCell>
                    <TableCell align="right">{formatInr(row.net_amount)}</TableCell>
                    <TableCell>
                      {row.buyer_name ? (
                        <Chip size="small" label={row.buyer_name} color="success" variant="outlined" />
                      ) : (
                        <Chip size="small" label="Unassigned" variant="outlined" />
                      )}
                    </TableCell>
                    <TableCell align="right">
                      {row.sale_rate_per_quintal ? formatInr(row.sale_rate_per_quintal) : "—"}
                    </TableCell>
                  </TableRow>
                ))}
                {rows.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7}>
                      <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                        No confirmed procurements to assign.
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </Card>
        </Stack>
      )}

      <PremiumDialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="xs">
        <PremiumDialogTitle>Assign {selectedIds.length} ticket(s) to buyer</PremiumDialogTitle>
        <PremiumDialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <SearchableSelect
              options={buyers}
              getOptionLabel={(buyer: Buyer) => (buyer.name_te ? `${buyer.name} · ${buyer.name_te}` : buyer.name)}
              isOptionEqualToValue={(a, b) => a.id === b.id}
              value={buyers.find((b) => b.id === buyerId) ?? null}
              onChange={(buyer) => setBuyerId(buyer?.id ?? "")}
              label="Buyer"
              required
              sx={TOUCH_FIELD_SX}
            />
            <TextField
              label="Sale rate / quintal (₹)"
              type="number"
              sx={TOUCH_FIELD_SX}
              inputProps={{ min: 0, step: 0.01 }}
              value={saleRate}
              onChange={(e) => setSaleRate(e.target.value)}
              helperText="Rate the crop is sold to the buyer at (drives margin)"
            />
            <TextField
              label="Dispatch date"
              type="date"
              sx={TOUCH_FIELD_SX}
              InputLabelProps={{ shrink: true }}
              value={saleDate}
              onChange={(e) => setSaleDate(e.target.value)}
            />
            {assignMutation.isError && (
              <Alert severity="error">
                {assignMutation.error instanceof Error
                  ? assignMutation.error.message
                  : "Could not assign buyer"}
              </Alert>
            )}
          </Stack>
        </PremiumDialogContent>
        <PremiumDialogActions>
          <Button variant="outlined" onClick={() => setDialogOpen(false)}>
            Cancel
          </Button>
          <Button
            variant="contained"
            disabled={!buyerId || assignMutation.isPending}
            onClick={() => assignMutation.mutate()}
          >
            {assignMutation.isPending ? "Assigning…" : "Assign buyer"}
          </Button>
        </PremiumDialogActions>
      </PremiumDialog>
    </MuiPageShell>
  );
}
