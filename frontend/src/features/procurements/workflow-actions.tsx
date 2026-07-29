"use client";

import {
  Alert,
  Button,
  Card,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { PermissionGuard } from "@/components/auth/permission-guard";
import {
  PremiumDialog,
  PremiumDialogActions,
  PremiumDialogContent,
  PremiumDialogTitle,
} from "@/components/ui/premium-dialog";
import { Button as PremiumButton, PREMIUM_SCOPE } from "@/components/ui/premium";
import { useAuth } from "@/hooks/use-auth";
import {
  applyPrice,
  cancelProcurement,
  confirmProcurement,
  recordWeighment,
  reverseProcurement,
  submitProcurement,
  type ProcurementDetail,
  type ProcurementStatus,
  CANCELLABLE_STATUSES,
} from "@/features/procurements/api";
import { TOUCH_FIELD_SX } from "@/features/field-services/work-details";

type Props = {
  procurement: ProcurementDetail;
  procurementDate: string;
  /** Planned moisture from [kf:proc] notes — prefill weighment. */
  plannedMoisturePct?: string | null;
};

export function ProcurementWorkflowActions({
  procurement,
  procurementDate,
  plannedMoisturePct,
}: Props) {
  const queryClient = useQueryClient();
  const { roles } = useAuth();
  const isOwner = roles.includes("OWNER");
  const status = procurement.status;
  const [weighOpen, setWeighOpen] = useState(false);
  const [cancelOpen, setCancelOpen] = useState(false);
  const [reverseOpen, setReverseOpen] = useState(false);
  const [gross, setGross] = useState("");
  const [tare, setTare] = useState("0");
  const [moisture, setMoisture] = useState(plannedMoisturePct ?? "");
  const [bagCount, setBagCount] = useState(String(procurement.bag_count || ""));
  const [perBag, setPerBag] = useState(procurement.per_bag_deduction_kg ?? "2");
  const [cancelReason, setCancelReason] = useState("");
  const [reverseReason, setReverseReason] = useState("");

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["procurement", procurement.id, procurementDate] });
    queryClient.invalidateQueries({ queryKey: ["procurements"] });
  };

  const submitMut = useMutation({
    mutationFn: () => submitProcurement(procurement.id, procurementDate),
    onSuccess: invalidate,
  });
  const weighMut = useMutation({
    mutationFn: () =>
      recordWeighment(procurement.id, procurementDate, {
        gross_weight_kg: gross,
        tare_weight_kg: tare || "0",
        moisture_pct: moisture.trim() || null,
        bag_count: bagCount.trim() ? Number(bagCount) : null,
        per_bag_deduction_kg: perBag.trim() || null,
      }),
    onSuccess: () => {
      setWeighOpen(false);
      invalidate();
    },
  });
  const priceMut = useMutation({
    mutationFn: () => applyPrice(procurement.id, procurementDate),
    onSuccess: invalidate,
  });
  const confirmMut = useMutation({
    mutationFn: () => confirmProcurement(procurement.id, procurementDate),
    onSuccess: invalidate,
  });
  const cancelMut = useMutation({
    mutationFn: () => cancelProcurement(procurement.id, procurementDate, cancelReason.trim()),
    onSuccess: () => {
      setCancelOpen(false);
      setCancelReason("");
      invalidate();
    },
  });
  const reverseMut = useMutation({
    mutationFn: () => reverseProcurement(procurement.id, procurementDate, reverseReason.trim()),
    onSuccess: () => {
      setReverseOpen(false);
      setReverseReason("");
      invalidate();
    },
  });

  const actionError =
    submitMut.error ??
    weighMut.error ??
    priceMut.error ??
    confirmMut.error ??
    cancelMut.error ??
    reverseMut.error;

  const openWeigh = () => {
    setGross("");
    setTare("0");
    setMoisture(plannedMoisturePct ?? procurement.moisture_pct ?? "");
    setBagCount(String(procurement.bag_count || ""));
    setPerBag(procurement.per_bag_deduction_kg ?? "2");
    weighMut.reset();
    setWeighOpen(true);
  };

  const bagWeightDeduction = (Number(bagCount) || 0) * (Number(perBag) || 0);
  const netWeightPreview =
    (Number(gross) || 0) - (Number(tare) || 0) - bagWeightDeduction;

  const isTerminal = (["confirmed", "paid_partial", "paid_full", "cancelled", "reversed"] as ProcurementStatus[]).includes(
    status,
  );

  if (isTerminal && status !== "confirmed") {
    return null;
  }

  return (
    <Card sx={{ p: 2 }}>
      <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1.5 }}>
        Workflow
      </Typography>

      <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} flexWrap="wrap" useFlexGap>
        {status === "draft" && (
          <PermissionGuard permission="procurements:update">
            <Button
              variant="contained"
              size="large"
              sx={{ minHeight: 48 }}
              disabled={submitMut.isPending}
              onClick={() => submitMut.mutate()}
            >
              {submitMut.isPending ? "Submitting…" : "Submit for weighment"}
            </Button>
          </PermissionGuard>
        )}

        {status === "pending_weighment" && (
          <PermissionGuard permission="procurements:update">
            <Button variant="contained" size="large" sx={{ minHeight: 48 }} onClick={openWeigh}>
              Record weighment
            </Button>
          </PermissionGuard>
        )}

        {status === "weighed" && (
          <PermissionGuard permission="procurements:update">
            <Button
              variant="contained"
              size="large"
              sx={{ minHeight: 48 }}
              disabled={priceMut.isPending}
              onClick={() => priceMut.mutate()}
            >
              {priceMut.isPending ? "Applying…" : "Apply price"}
            </Button>
          </PermissionGuard>
        )}

        {status === "priced" && (
          <PermissionGuard permission="procurements:confirm">
            <Button
              variant="contained"
              color="success"
              size="large"
              sx={{ minHeight: 48 }}
              disabled={confirmMut.isPending}
              onClick={() => confirmMut.mutate()}
            >
              {confirmMut.isPending ? "Confirming…" : "Confirm (post ledger)"}
            </Button>
          </PermissionGuard>
        )}

        {status === "confirmed" && isOwner && (
          <PermissionGuard permission="procurements:confirm">
            <Button
              variant="outlined"
              color="error"
              size="large"
              sx={{ minHeight: 48 }}
              onClick={() => {
                reverseMut.reset();
                setReverseOpen(true);
              }}
            >
              Reverse
            </Button>
          </PermissionGuard>
        )}

        {CANCELLABLE_STATUSES.includes(status) && (
          <PermissionGuard permission="procurements:cancel">
            <Button
              variant="outlined"
              color="error"
              size="large"
              sx={{ minHeight: 48 }}
              onClick={() => {
                cancelMut.reset();
                setCancelOpen(true);
              }}
            >
              Cancel ticket
            </Button>
          </PermissionGuard>
        )}
      </Stack>

      {actionError && (
        <Alert severity="error" sx={{ mt: 1.5 }}>
          {actionError instanceof Error ? actionError.message : "Action failed"}
        </Alert>
      )}

      <PremiumDialog open={weighOpen} onClose={() => setWeighOpen(false)} maxWidth="sm">
        <PremiumDialogTitle>Record weighment</PremiumDialogTitle>
        <PremiumDialogContent>
          <Stack spacing={2} sx={{ pt: 1 }}>
            <TextField
              required
              label="Gross weight (kg)"
              type="number"
              sx={TOUCH_FIELD_SX}
              inputProps={{ min: 0.01, step: 0.01 }}
              value={gross}
              onChange={(e) => setGross(e.target.value)}
              autoFocus
            />
            <TextField
              label="Tare weight (kg)"
              type="number"
              sx={TOUCH_FIELD_SX}
              inputProps={{ min: 0, step: 0.01 }}
              value={tare}
              onChange={(e) => setTare(e.target.value)}
            />
            <TextField
              label="Moisture %"
              type="number"
              sx={TOUCH_FIELD_SX}
              inputProps={{ min: 0, max: 100, step: 0.1 }}
              value={moisture}
              onChange={(e) => setMoisture(e.target.value)}
              helperText={
                plannedMoisturePct
                  ? `Planned at create: ${plannedMoisturePct}%`
                  : "Optional — stored on ticket"
              }
            />
            <TextField
              label="Bag count"
              type="number"
              sx={TOUCH_FIELD_SX}
              inputProps={{ min: 0, step: 1 }}
              value={bagCount}
              onChange={(e) => setBagCount(e.target.value)}
            />
            <TextField
              label="Per-bag deduction (kg)"
              type="number"
              sx={TOUCH_FIELD_SX}
              inputProps={{ min: 0, step: 0.001 }}
              value={perBag}
              onChange={(e) => setPerBag(e.target.value)}
              helperText="Standard weight deducted per bag (kata). Default 2 kg."
            />
            <Alert severity="info" icon={false}>
              <Typography variant="body2">
                Bag weight deduction: <strong>{bagWeightDeduction.toFixed(3)} kg</strong>{" "}
                ({bagCount || 0} bags × {perBag || 0} kg)
              </Typography>
              <Typography variant="body2">
                Net payable weight:{" "}
                <strong>
                  {netWeightPreview > 0 ? netWeightPreview.toFixed(3) : "0.000"} kg
                </strong>{" "}
                (gross − tare − bag deduction)
              </Typography>
            </Alert>
            {weighMut.isError && (
              <Alert severity="error">
                {weighMut.error instanceof Error ? weighMut.error.message : "Weighment failed"}
              </Alert>
            )}
          </Stack>
        </PremiumDialogContent>
        <PremiumDialogActions className={PREMIUM_SCOPE}>
          <PremiumButton variant="secondary" size="sm" onClick={() => setWeighOpen(false)}>
            Cancel
          </PremiumButton>
          <PremiumButton
            variant="primary"
            size="sm"
            disabled={!gross || Number(gross) <= 0 || weighMut.isPending}
            onClick={() => weighMut.mutate()}
          >
            {weighMut.isPending ? "Saving…" : "Save weighment"}
          </PremiumButton>
        </PremiumDialogActions>
      </PremiumDialog>

      <PremiumDialog open={cancelOpen} onClose={() => setCancelOpen(false)} maxWidth="xs">
        <PremiumDialogTitle>Cancel procurement?</PremiumDialogTitle>
        <PremiumDialogContent>
          <TextField
            fullWidth
            required
            multiline
            minRows={2}
            label="Reason"
            sx={{ ...TOUCH_FIELD_SX, mt: 1 }}
            value={cancelReason}
            onChange={(e) => setCancelReason(e.target.value)}
            helperText="Minimum 3 characters"
          />
          {cancelMut.isError && (
            <Alert severity="error" sx={{ mt: 1.5 }}>
              {cancelMut.error instanceof Error ? cancelMut.error.message : "Cancel failed"}
            </Alert>
          )}
        </PremiumDialogContent>
        <PremiumDialogActions className={PREMIUM_SCOPE}>
          <PremiumButton variant="secondary" size="sm" onClick={() => setCancelOpen(false)}>
            Keep ticket
          </PremiumButton>
          <PremiumButton
            variant="danger"
            size="sm"
            disabled={cancelReason.trim().length < 3 || cancelMut.isPending}
            onClick={() => cancelMut.mutate()}
          >
            {cancelMut.isPending ? "Cancelling…" : "Cancel ticket"}
          </PremiumButton>
        </PremiumDialogActions>
      </PremiumDialog>

      <PremiumDialog open={reverseOpen} onClose={() => setReverseOpen(false)} maxWidth="xs">
        <PremiumDialogTitle>Reverse confirmation?</PremiumDialogTitle>
        <PremiumDialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
            Reverses the ledger debit. OWNER + confirm permission required.
          </Typography>
          <TextField
            fullWidth
            required
            multiline
            minRows={2}
            label="Reason"
            sx={TOUCH_FIELD_SX}
            value={reverseReason}
            onChange={(e) => setReverseReason(e.target.value)}
          />
          {reverseMut.isError && (
            <Alert severity="error" sx={{ mt: 1.5 }}>
              {reverseMut.error instanceof Error ? reverseMut.error.message : "Reverse failed"}
            </Alert>
          )}
        </PremiumDialogContent>
        <PremiumDialogActions className={PREMIUM_SCOPE}>
          <PremiumButton variant="secondary" size="sm" onClick={() => setReverseOpen(false)}>
            Keep confirmed
          </PremiumButton>
          <PremiumButton
            variant="danger"
            size="sm"
            disabled={reverseReason.trim().length < 3 || reverseMut.isPending}
            onClick={() => reverseMut.mutate()}
          >
            {reverseMut.isPending ? "Reversing…" : "Reverse"}
          </PremiumButton>
        </PremiumDialogActions>
      </PremiumDialog>
    </Card>
  );
}
