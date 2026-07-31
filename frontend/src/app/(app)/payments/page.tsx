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
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { PermissionGuard } from "@/components/auth/permission-guard";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import {
  PremiumDialog,
  PremiumDialogActions,
  PremiumDialogContent,
  PremiumDialogTitle,
} from "@/components/ui/premium-dialog";
import { Button as PremiumButton, PREMIUM_SCOPE } from "@/components/ui/premium";
import { SearchableSelect } from "@/components/ui/searchable-select";
import { ResponsiveTable } from "@/components/ui/responsive-table";
import { fetchFarmers, type FarmerListItem } from "@/features/farmers/api";
import {
  createFarmerPayment,
  fetchFarmerPayments,
  PAYMENT_STATUS_COLORS,
  PAYMENT_STATUS_LABELS,
  PAYMENT_TYPE_LABELS,
  type FarmerPaymentType,
} from "@/features/farmer-payments/api";
import { PaymentSettlementActions } from "@/features/farmer-payments/settlement-actions";
import { fetchPaymentModes, type PaymentMode } from "@/features/master-data/api";
import { formatInr } from "@/features/procurements/api";
import { formatMasterOptionLabel } from "@/lib/bilingual";
import { useLocale } from "@/i18n/use-translation";

const TYPE_OPTIONS: FarmerPaymentType[] = ["advance", "final", "adjustment"];

export default function PaymentsPage() {
  const locale = useLocale();
  const queryClient = useQueryClient();
  const [typeFilter, setTypeFilter] = useState<string>("");
  const [createOpen, setCreateOpen] = useState(false);
  const [farmerId, setFarmerId] = useState("");
  const [paymentType, setPaymentType] = useState<FarmerPaymentType>("advance");
  const [paymentDate, setPaymentDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [amount, setAmount] = useState("");
  const [paymentModeId, setPaymentModeId] = useState("");
  const [referenceNo, setReferenceNo] = useState("");
  const [notes, setNotes] = useState("");

  const listQuery = useQuery({
    queryKey: ["farmer-payments", typeFilter],
    queryFn: () =>
      fetchFarmerPayments({
        pageSize: 50,
        payment_type: (typeFilter as FarmerPaymentType) || undefined,
      }),
  });

  const farmersQuery = useQuery({
    queryKey: ["farmers-wizard"],
    queryFn: () => fetchFarmers({ pageSize: 100 }),
  });

  const modesQuery = useQuery({
    queryKey: ["payment-modes"],
    queryFn: () => fetchPaymentModes(1, 100),
    enabled: createOpen,
  });

  const farmers = farmersQuery.data?.items ?? [];
  const modes = useMemo(
    () => (modesQuery.data?.items ?? []).filter((m: PaymentMode) => m.is_active),
    [modesQuery.data],
  );

  const createMut = useMutation({
    mutationFn: () =>
      createFarmerPayment({
        farmer_id: farmerId,
        payment_type: paymentType,
        payment_date: paymentDate,
        amount: amount.trim(),
        payment_mode_id: paymentModeId,
        reference_no: referenceNo.trim() || null,
        notes: notes.trim() || null,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["farmer-payments"] });
      setCreateOpen(false);
      setFarmerId("");
      setAmount("");
      setPaymentModeId("");
      setReferenceNo("");
      setNotes("");
      setPaymentType("advance");
      setPaymentDate(new Date().toISOString().slice(0, 10));
    },
  });

  const farmerById = useMemo(() => {
    const map = new Map<string, FarmerListItem>();
    for (const f of farmers) map.set(f.id, f);
    return map;
  }, [farmers]);

  const canSubmit =
    Boolean(farmerId && paymentModeId && amount.trim() && Number(amount) > 0) &&
    !createMut.isPending;

  return (
    <MuiPageShell
      title="Payments"
      description="Farmer payments, allocation, and settlement queue."
      actions={
        <PermissionGuard permission="farmer_payments:create">
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateOpen(true)}
            sx={{ minHeight: 44 }}
          >
            Record payment
          </Button>
        </PermissionGuard>
      }
    >
      <Card sx={{ mb: 2, p: 2 }}>
        <TextField
          select
          size="small"
          label="Payment type"
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          sx={{ minWidth: 200 }}
        >
          <MenuItem value="">All types</MenuItem>
          {TYPE_OPTIONS.map((t) => (
            <MenuItem key={t} value={t}>
              {PAYMENT_TYPE_LABELS[t]}
            </MenuItem>
          ))}
        </TextField>
      </Card>

      <Card sx={{ overflow: "hidden" }}>
        {listQuery.isLoading && (
          <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
            <CircularProgress />
          </Box>
        )}

        {listQuery.isError && (
          <Alert severity="warning" sx={{ m: 2 }}>
            {listQuery.error instanceof Error
              ? listQuery.error.message
              : "Could not load farmer payments"}
          </Alert>
        )}

        {!listQuery.isLoading && listQuery.data && listQuery.data.items.length === 0 && (
          <Box sx={{ p: 4, textAlign: "center" }}>
            <Typography color="text.secondary">No farmer payments yet.</Typography>
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
              Record an advance or final payment, then allocate it to confirmed procurements.
            </Typography>
          </Box>
        )}

        {!listQuery.isLoading && listQuery.data && listQuery.data.items.length > 0 && (
          <ResponsiveTable>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Number</TableCell>
                  <TableCell>Date</TableCell>
                  <TableCell>Type</TableCell>
                  <TableCell>Farmer</TableCell>
                  <TableCell align="right">Amount</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Ref</TableCell>
                  <TableCell align="right">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {listQuery.data.items.map((row) => (
                  <TableRow key={row.id} hover>
                    <TableCell>
                      <Typography variant="body2" fontWeight={600}>
                        {row.payment_number}
                      </Typography>
                    </TableCell>
                    <TableCell>{row.payment_date}</TableCell>
                    <TableCell>
                      {PAYMENT_TYPE_LABELS[row.payment_type] ?? row.payment_type}
                    </TableCell>
                    <TableCell>
                      {farmerById.get(row.farmer_id)?.full_name ??
                        row.farmer_id.slice(0, 8)}
                    </TableCell>
                    <TableCell align="right">{formatInr(row.amount)}</TableCell>
                    <TableCell>
                      <Chip
                        label={PAYMENT_STATUS_LABELS[row.status] ?? row.status}
                        size="small"
                        color={PAYMENT_STATUS_COLORS[row.status] ?? "default"}
                        variant={row.status === "completed" ? "filled" : "outlined"}
                      />
                    </TableCell>
                    <TableCell>{row.reference_no ?? "—"}</TableCell>
                    <TableCell align="right">
                      <PaymentSettlementActions
                        payment={row}
                        farmerName={farmerById.get(row.farmer_id)?.full_name}
                        dense
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </ResponsiveTable>
        )}
      </Card>

      <PremiumDialog open={createOpen} onClose={() => !createMut.isPending && setCreateOpen(false)} maxWidth="sm" fullWidth>
        <PremiumDialogTitle>Record farmer payment</PremiumDialogTitle>
        <PremiumDialogContent className={PREMIUM_SCOPE}>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <SearchableSelect
              options={farmers}
              value={farmers.find((f) => f.id === farmerId) ?? null}
              onChange={(f) => setFarmerId(f?.id ?? "")}
              getOptionLabel={(f) => `${f.full_name} (${f.farmer_code})`}
              isOptionEqualToValue={(a, b) => a.id === b.id}
              label="Farmer"
              required
              loading={farmersQuery.isLoading}
            />
            <TextField
              select
              label="Payment type"
              value={paymentType}
              onChange={(e) => setPaymentType(e.target.value as FarmerPaymentType)}
              required
              fullWidth
            >
              {TYPE_OPTIONS.map((t) => (
                <MenuItem key={t} value={t}>
                  {PAYMENT_TYPE_LABELS[t]}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              type="date"
              label="Payment date"
              value={paymentDate}
              onChange={(e) => setPaymentDate(e.target.value)}
              InputLabelProps={{ shrink: true }}
              required
              fullWidth
            />
            <TextField
              label="Amount (₹)"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
              fullWidth
              inputMode="decimal"
            />
            <SearchableSelect
              options={modes}
              value={modes.find((m) => m.id === paymentModeId) ?? null}
              onChange={(m) => setPaymentModeId(m?.id ?? "")}
              getOptionLabel={(m) => formatMasterOptionLabel(locale, m.name, m.name_te)}
              isOptionEqualToValue={(a, b) => a.id === b.id}
              label="Payment mode"
              required
              loading={modesQuery.isLoading}
            />
            <TextField
              label="Reference no"
              value={referenceNo}
              onChange={(e) => setReferenceNo(e.target.value)}
              fullWidth
            />
            <TextField
              label="Notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              fullWidth
              multiline
              minRows={2}
            />
            {createMut.isError && (
              <Alert severity="error">
                {createMut.error instanceof Error
                  ? createMut.error.message
                  : "Could not create payment"}
              </Alert>
            )}
          </Stack>
        </PremiumDialogContent>
        <PremiumDialogActions>
          <PremiumButton
            variant="secondary"
            size="sm"
            onClick={() => setCreateOpen(false)}
            disabled={createMut.isPending}
          >
            Cancel
          </PremiumButton>
          <PremiumButton
            size="sm"
            onClick={() => createMut.mutate()}
            disabled={!canSubmit}
          >
            {createMut.isPending ? "Saving…" : "Save payment"}
          </PremiumButton>
        </PremiumDialogActions>
      </PremiumDialog>
    </MuiPageShell>
  );
}
