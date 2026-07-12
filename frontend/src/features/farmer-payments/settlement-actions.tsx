"use client";

import {
  Alert,
  Box,
  Button,
  Checkbox,
  Chip,
  CircularProgress,
  Divider,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography,
} from "@mui/material";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { PermissionGuard } from "@/components/auth/permission-guard";
import {
  PremiumDialog,
  PremiumDialogActions,
  PremiumDialogContent,
  PremiumDialogTitle,
} from "@/components/ui/premium-dialog";
import { Button as PremiumButton, PREMIUM_SCOPE } from "@/components/ui/premium";
import { TOUCH_FIELD_SX } from "@/features/field-services/work-details";
import {
  allocateFarmerPayment,
  allocatedTotal,
  fetchFarmerPayment,
  PAYMENT_STATUS_COLORS,
  PAYMENT_STATUS_LABELS,
  PAYMENT_TYPE_LABELS,
  reverseFarmerPayment,
  unallocatedRemainder,
  type FarmerPayment,
} from "@/features/farmer-payments/api";
import {
  fetchProcurement,
  fetchProcurements,
  formatInr,
  STATUS_COLORS,
  STATUS_LABELS,
  type ProcurementListItem,
  type ProcurementStatus,
} from "@/features/procurements/api";

const PAYABLE_STATUSES: ProcurementStatus[] = ["confirmed", "paid_partial"];

/** Distinct settlement result colors (partial vs full vs back to confirmed). */
const SETTLEMENT_STATUS_COLORS: Record<
  string,
  "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning"
> = {
  confirmed: "info",
  paid_partial: "warning",
  paid_full: "success",
};

export type ProcurementStatusResult = {
  id: string;
  procurement_number: string;
  status: ProcurementStatus;
};

type Props = {
  payment: FarmerPayment;
  farmerName?: string;
  /** Compact row action buttons (Allocate / Reverse / Details). */
  dense?: boolean;
};

async function loadProcurementStatuses(
  allocations: { procurement_id: string | null; procurement_date: string | null }[],
): Promise<ProcurementStatusResult[]> {
  const unique = new Map<string, { id: string; date: string }>();
  for (const a of allocations) {
    if (!a.procurement_id || !a.procurement_date) continue;
    unique.set(`${a.procurement_id}:${a.procurement_date}`, {
      id: a.procurement_id,
      date: a.procurement_date,
    });
  }
  const results: ProcurementStatusResult[] = [];
  await Promise.all(
    [...unique.values()].map(async ({ id, date }) => {
      try {
        const p = await fetchProcurement(id, date);
        results.push({
          id: p.id,
          procurement_number: p.procurement_number,
          status: p.status,
        });
      } catch {
        /* skip missing */
      }
    }),
  );
  return results.sort((a, b) =>
    a.procurement_number.localeCompare(b.procurement_number),
  );
}

function StatusResultAlert({
  title,
  results,
}: {
  title: string;
  results: ProcurementStatusResult[];
}) {
  if (results.length === 0) return null;
  return (
    <Alert severity="success" sx={{ mt: 1 }}>
      <Typography variant="body2" fontWeight={600} gutterBottom>
        {title}
      </Typography>
      <Stack direction="row" flexWrap="wrap" gap={1}>
        {results.map((r) => (
          <Chip
            key={r.id}
            size="small"
            label={`${r.procurement_number}: ${STATUS_LABELS[r.status] ?? r.status}`}
            color={SETTLEMENT_STATUS_COLORS[r.status] ?? STATUS_COLORS[r.status] ?? "default"}
          />
        ))}
      </Stack>
    </Alert>
  );
}

export function PaymentSettlementActions({ payment, farmerName, dense }: Props) {
  const queryClient = useQueryClient();
  const [detailOpen, setDetailOpen] = useState(false);
  const [allocateOpen, setAllocateOpen] = useState(false);
  const [reverseOpen, setReverseOpen] = useState(false);
  const [reverseReason, setReverseReason] = useState("");
  const [selected, setSelected] = useState<Record<string, boolean>>({});
  const [amounts, setAmounts] = useState<Record<string, string>>({});
  const [statusResults, setStatusResults] = useState<ProcurementStatusResult[]>([]);
  const [resultTitle, setResultTitle] = useState("");

  const isCompleted = payment.status === "completed";

  const detailQuery = useQuery({
    queryKey: ["farmer-payment", payment.id, payment.payment_date],
    queryFn: () => fetchFarmerPayment(payment.id, payment.payment_date),
    enabled: detailOpen || allocateOpen || reverseOpen,
  });

  const live = detailQuery.data ?? payment;
  const remainder = unallocatedRemainder(live);
  /** Prefer detail remainder when known; else list amount (unallocated until detail loads). */
  const listRemainderHint =
    payment.allocations?.length > 0
      ? unallocatedRemainder(payment)
      : Number(payment.amount);
  const canAllocate =
    isCompleted && (detailQuery.data ? remainder > 0 : listRemainderHint > 0);
  const canReverse = isCompleted;

  const allocationLabelsQuery = useQuery({
    queryKey: [
      "farmer-payment-alloc-labels",
      payment.id,
      payment.payment_date,
      live.allocations.map((a) => a.id).join(","),
    ],
    queryFn: () => loadProcurementStatuses(live.allocations),
    enabled: detailOpen && live.allocations.length > 0,
  });

  const allocationLabelById = useMemo(() => {
    const map = new Map<string, ProcurementStatusResult>();
    for (const r of allocationLabelsQuery.data ?? []) map.set(r.id, r);
    return map;
  }, [allocationLabelsQuery.data]);

  const payableQuery = useQuery({
    queryKey: ["procurements-payable", live.farmer_id],
    queryFn: () =>
      fetchProcurements({ pageSize: 100, farmer_id: live.farmer_id }),
    enabled: allocateOpen,
  });

  const payable = useMemo(() => {
    const items = payableQuery.data?.items ?? [];
    return items.filter((p) => PAYABLE_STATUSES.includes(p.status));
  }, [payableQuery.data]);

  useEffect(() => {
    if (!allocateOpen) return;
    const nextSelected: Record<string, boolean> = {};
    const nextAmounts: Record<string, string> = {};
    for (const p of payable) {
      nextSelected[p.id] = false;
      nextAmounts[p.id] = "";
    }
    setSelected(nextSelected);
    setAmounts(nextAmounts);
    setStatusResults([]);
    setResultTitle("");
  }, [allocateOpen, payable]);

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["farmer-payments"] });
    queryClient.invalidateQueries({ queryKey: ["farmer-payment", payment.id] });
    queryClient.invalidateQueries({ queryKey: ["procurements"] });
    queryClient.invalidateQueries({ queryKey: ["procurements-payable", live.farmer_id] });
  };

  const allocateMut = useMutation({
    mutationFn: async () => {
      const allocations = payable
        .filter((p) => selected[p.id] && Number(amounts[p.id] || 0) > 0)
        .map((p) => ({
          procurement_id: p.id,
          procurement_date: p.procurement_date,
          allocated_amount: Number(amounts[p.id]).toFixed(2),
        }));
      if (allocations.length === 0) {
        throw new Error("Select at least one procurement and enter an amount");
      }
      const sum = allocations.reduce((s, a) => s + Number(a.allocated_amount), 0);
      if (sum > remainder + 0.001) {
        throw new Error(
          `Allocation total ${formatInr(sum)} exceeds unallocated ${formatInr(remainder)}`,
        );
      }
      return allocateFarmerPayment(payment.id, payment.payment_date, { allocations });
    },
    onSuccess: async (updated) => {
      const results = await loadProcurementStatuses(updated.allocations);
      setStatusResults(results);
      setResultTitle("Procurement settlement status after allocate");
      invalidate();
    },
  });

  const reverseMut = useMutation({
    mutationFn: async () => {
      const priorPayment = await fetchFarmerPayment(payment.id, payment.payment_date);
      const priorAllocations = [...priorPayment.allocations];
      const updated = await reverseFarmerPayment(
        payment.id,
        payment.payment_date,
        reverseReason.trim(),
      );
      return { updated, priorAllocations };
    },
    onSuccess: async ({ priorAllocations }) => {
      const results = await loadProcurementStatuses(priorAllocations);
      setStatusResults(results);
      setResultTitle("Procurement status after reverse (may return to confirmed)");
      setReverseOpen(false);
      setReverseReason("");
      setDetailOpen(true);
      invalidate();
    },
  });

  const selectedSum = useMemo(() => {
    return payable
      .filter((p) => selected[p.id])
      .reduce((s, p) => s + (Number(amounts[p.id]) || 0), 0);
  }, [payable, selected, amounts]);

  const canSubmitAllocate =
    !detailQuery.isLoading &&
    remainder > 0 &&
    selectedSum > 0 &&
    selectedSum <= remainder + 0.001 &&
    !allocateMut.isPending;

  const btnSx = dense
    ? { minHeight: 40, minWidth: 88, px: 1.5 }
    : { minHeight: 44, minWidth: 100 };

  const openAllocate = () => {
    setStatusResults([]);
    setResultTitle("");
    allocateMut.reset();
    setAllocateOpen(true);
  };

  const openReverse = () => {
    setReverseReason("");
    reverseMut.reset();
    setReverseOpen(true);
  };

  const toggleRow = (p: ProcurementListItem, checked: boolean) => {
    setSelected((prev) => ({ ...prev, [p.id]: checked }));
    if (checked && !amounts[p.id]) {
      const suggest = Math.min(remainder, Number(p.net_amount) || 0);
      setAmounts((prev) => ({
        ...prev,
        [p.id]: suggest > 0 ? suggest.toFixed(2) : "",
      }));
    }
  };

  return (
    <>
      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
        <Button
          size="small"
          variant="outlined"
          onClick={() => {
            setStatusResults([]);
            setDetailOpen(true);
          }}
          sx={btnSx}
        >
          Details
        </Button>
        <PermissionGuard permission="farmer_payments:create">
          {canAllocate && (
            <Button
              size="small"
              variant="contained"
              color="primary"
              onClick={openAllocate}
              sx={btnSx}
            >
              Allocate
            </Button>
          )}
        </PermissionGuard>
        <PermissionGuard permission="farmer_payments:reverse">
          {canReverse && (
            <Button
              size="small"
              variant="outlined"
              color="error"
              onClick={openReverse}
              sx={btnSx}
            >
              Reverse
            </Button>
          )}
        </PermissionGuard>
      </Stack>

      {/* Detail */}
      <PremiumDialog
        open={detailOpen}
        onClose={() => setDetailOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <PremiumDialogTitle>
          {live.payment_number}
          <Typography component="span" variant="body2" color="text.secondary" sx={{ ml: 1 }}>
            {PAYMENT_TYPE_LABELS[live.payment_type] ?? live.payment_type}
          </Typography>
        </PremiumDialogTitle>
        <PremiumDialogContent className={PREMIUM_SCOPE}>
          {detailQuery.isLoading && (
            <Box sx={{ display: "flex", justifyContent: "center", py: 3 }}>
              <CircularProgress size={28} />
            </Box>
          )}
          {!detailQuery.isLoading && (
            <Stack spacing={1.5}>
              <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
                <Chip
                  label={PAYMENT_STATUS_LABELS[live.status] ?? live.status}
                  color={PAYMENT_STATUS_COLORS[live.status] ?? "default"}
                  size="small"
                />
                <Typography variant="body2">{live.payment_date}</Typography>
                <Typography variant="body2" fontWeight={600}>
                  {formatInr(live.amount)}
                </Typography>
              </Stack>
              <Typography variant="body2" color="text.secondary">
                Farmer: {farmerName ?? live.farmer_id.slice(0, 8)}
              </Typography>
              {live.reference_no && (
                <Typography variant="body2">Ref: {live.reference_no}</Typography>
              )}
              {live.notes && (
                <Typography variant="body2" color="text.secondary">
                  {live.notes}
                </Typography>
              )}
              <Divider />
              <Typography variant="subtitle2">
                Allocations ({formatInr(allocatedTotal(live))} of {formatInr(live.amount)})
              </Typography>
              {live.allocations.length === 0 ? (
                <Typography variant="body2" color="text.secondary">
                  Not allocated to any procurement yet.
                </Typography>
              ) : (
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Procurement</TableCell>
                      <TableCell>Date</TableCell>
                      <TableCell align="right">Amount</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {live.allocations.map((a) => {
                      const label = a.procurement_id
                        ? allocationLabelById.get(a.procurement_id)
                        : undefined;
                      return (
                        <TableRow key={a.id}>
                          <TableCell>
                            <Stack spacing={0.5}>
                              <Typography variant="body2" fontWeight={600}>
                                {label?.procurement_number ??
                                  (a.procurement_id
                                    ? a.procurement_id.slice(0, 8)
                                    : "—")}
                              </Typography>
                              {label && (
                                <Chip
                                  size="small"
                                  label={STATUS_LABELS[label.status] ?? label.status}
                                  color={
                                    SETTLEMENT_STATUS_COLORS[label.status] ??
                                    STATUS_COLORS[label.status] ??
                                    "default"
                                  }
                                  sx={{ alignSelf: "flex-start" }}
                                />
                              )}
                            </Stack>
                          </TableCell>
                          <TableCell>{a.procurement_date ?? "—"}</TableCell>
                          <TableCell align="right">
                            {formatInr(a.allocated_amount)}
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              )}
              {isCompleted && remainder > 0 && (
                <Alert severity="info">
                  Unallocated remainder: {formatInr(remainder)}
                </Alert>
              )}
              <StatusResultAlert title={resultTitle} results={statusResults} />
              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ pt: 1 }}>
                <PermissionGuard permission="farmer_payments:create">
                  {canAllocate && (
                    <Button
                      variant="contained"
                      onClick={openAllocate}
                      sx={{ minHeight: 44 }}
                    >
                      Allocate to procurements
                    </Button>
                  )}
                </PermissionGuard>
                <PermissionGuard permission="farmer_payments:reverse">
                  {canReverse && (
                    <Button
                      variant="outlined"
                      color="error"
                      onClick={openReverse}
                      sx={{ minHeight: 44 }}
                    >
                      Reverse payment
                    </Button>
                  )}
                </PermissionGuard>
              </Stack>
            </Stack>
          )}
        </PremiumDialogContent>
        <PremiumDialogActions>
          <PremiumButton variant="secondary" size="sm" onClick={() => setDetailOpen(false)}>
            Close
          </PremiumButton>
        </PremiumDialogActions>
      </PremiumDialog>

      {/* Allocate */}
      <PremiumDialog
        open={allocateOpen}
        onClose={() => !allocateMut.isPending && setAllocateOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <PremiumDialogTitle>Allocate {live.payment_number}</PremiumDialogTitle>
        <PremiumDialogContent className={PREMIUM_SCOPE}>
          <Stack spacing={2} sx={{ pt: 0.5 }}>
            <Alert severity="warning">
              Allocating links this payment to confirmed procurements and updates their
              status to <strong>partially paid</strong> or <strong>paid in full</strong>.
              This cannot be undone except by reversing the payment.
            </Alert>
            {detailQuery.isLoading && (
              <Box sx={{ display: "flex", justifyContent: "center", py: 2 }}>
                <CircularProgress size={28} />
              </Box>
            )}

            {!detailQuery.isLoading && (
              <Typography variant="body2">
                Unallocated: <strong>{formatInr(remainder)}</strong>
                {live.allocations.length > 0
                  ? ` · Already allocated ${formatInr(allocatedTotal(live))}`
                  : null}
              </Typography>
            )}

            {!detailQuery.isLoading && remainder <= 0 && (
              <Alert severity="info">This payment is fully allocated.</Alert>
            )}

            {payableQuery.isLoading && (
              <Box sx={{ display: "flex", justifyContent: "center", py: 3 }}>
                <CircularProgress size={28} />
              </Box>
            )}

            {payableQuery.isError && (
              <Alert severity="error">
                {payableQuery.error instanceof Error
                  ? payableQuery.error.message
                  : "Could not load procurements"}
              </Alert>
            )}

            {!payableQuery.isLoading && !detailQuery.isLoading && remainder > 0 && payable.length === 0 && (
              <Alert severity="info">
                No confirmed / partially paid procurements for this farmer.
              </Alert>
            )}

            {remainder > 0 && payable.length > 0 && (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell padding="checkbox" />
                    <TableCell>Ticket</TableCell>
                    <TableCell>Date</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell align="right">Net</TableCell>
                    <TableCell align="right" sx={{ minWidth: 140 }}>
                      Allocate ₹
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {payable.map((p) => (
                    <TableRow key={p.id} hover selected={Boolean(selected[p.id])}>
                      <TableCell padding="checkbox">
                        <Checkbox
                          checked={Boolean(selected[p.id])}
                          onChange={(_, c) => toggleRow(p, c)}
                          sx={{ "& .MuiSvgIcon-root": { fontSize: 28 } }}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight={600}>
                          {p.procurement_number}
                        </Typography>
                      </TableCell>
                      <TableCell>{p.procurement_date}</TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={STATUS_LABELS[p.status] ?? p.status}
                          color={
                            SETTLEMENT_STATUS_COLORS[p.status] ??
                            STATUS_COLORS[p.status] ??
                            "default"
                          }
                        />
                      </TableCell>
                      <TableCell align="right">{formatInr(p.net_amount)}</TableCell>
                      <TableCell align="right">
                        <TextField
                          size="small"
                          value={amounts[p.id] ?? ""}
                          disabled={!selected[p.id]}
                          onChange={(e) =>
                            setAmounts((prev) => ({ ...prev, [p.id]: e.target.value }))
                          }
                          inputMode="decimal"
                          placeholder="0.00"
                          sx={{ ...TOUCH_FIELD_SX, maxWidth: 140 }}
                        />
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}

            {selectedSum > 0 && (
              <Typography variant="body2">
                Selected total: <strong>{formatInr(selectedSum)}</strong>
                {selectedSum > remainder + 0.001 && (
                  <Typography component="span" color="error.main" sx={{ ml: 1 }}>
                    exceeds unallocated remainder
                  </Typography>
                )}
              </Typography>
            )}

            {allocateMut.isError && (
              <Alert severity="error">
                {allocateMut.error instanceof Error
                  ? allocateMut.error.message
                  : "Allocate failed"}
              </Alert>
            )}

            <StatusResultAlert title={resultTitle} results={statusResults} />
          </Stack>
        </PremiumDialogContent>
        <PremiumDialogActions>
          <PremiumButton
            variant="secondary"
            size="sm"
            onClick={() => setAllocateOpen(false)}
            disabled={allocateMut.isPending}
          >
            {statusResults.length > 0 ? "Close" : "Cancel"}
          </PremiumButton>
          {statusResults.length === 0 && (
            <PremiumButton
              size="sm"
              onClick={() => allocateMut.mutate()}
              disabled={!canSubmitAllocate}
            >
              {allocateMut.isPending ? "Allocating…" : "Confirm allocate"}
            </PremiumButton>
          )}
        </PremiumDialogActions>
      </PremiumDialog>

      {/* Reverse */}
      <PremiumDialog
        open={reverseOpen}
        onClose={() => !reverseMut.isPending && setReverseOpen(false)}
        maxWidth="xs"
        fullWidth
      >
        <PremiumDialogTitle>Reverse {live.payment_number}</PremiumDialogTitle>
        <PremiumDialogContent className={PREMIUM_SCOPE}>
          <Stack spacing={2} sx={{ pt: 0.5 }}>
            <Alert severity="error">
              Reversing posts a ledger debit, clears all allocations, and recalculates
              linked procurements (often back to <strong>confirmed</strong> or{" "}
              <strong>partially paid</strong>). This cannot be undone.
            </Alert>
            {live.allocations.length > 0 && (
              <Typography variant="body2" color="text.secondary">
                {live.allocations.length} allocation
                {live.allocations.length === 1 ? "" : "s"} will be cleared (
                {formatInr(allocatedTotal(live))}).
              </Typography>
            )}
            <TextField
              label="Reason"
              value={reverseReason}
              onChange={(e) => setReverseReason(e.target.value)}
              required
              fullWidth
              multiline
              minRows={2}
              helperText="At least 3 characters"
              sx={TOUCH_FIELD_SX}
            />
            {reverseMut.isError && (
              <Alert severity="error">
                {reverseMut.error instanceof Error
                  ? reverseMut.error.message
                  : "Reverse failed"}
              </Alert>
            )}
          </Stack>
        </PremiumDialogContent>
        <PremiumDialogActions>
          <PremiumButton
            variant="secondary"
            size="sm"
            onClick={() => setReverseOpen(false)}
            disabled={reverseMut.isPending}
          >
            Cancel
          </PremiumButton>
          <PremiumButton
            size="sm"
            onClick={() => reverseMut.mutate()}
            disabled={reverseReason.trim().length < 3 || reverseMut.isPending}
          >
            {reverseMut.isPending ? "Reversing…" : "Confirm reverse"}
          </PremiumButton>
        </PremiumDialogActions>
      </PremiumDialog>
    </>
  );
}
