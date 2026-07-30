"use client";

import {
  Alert,
  Box,
  Button,
  Card,
  Checkbox,
  CircularProgress,
  FormControlLabel,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { ArrowBack } from "@mui/icons-material";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { fetchProcurement, updateProcurement } from "@/features/procurements/api";
import { calculateProcurementPreview } from "@/features/procurements/calculate";
import { TOUCH_FIELD_SX } from "@/features/field-services/work-details";

export default function EditProcurementPage() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const procurementDate = searchParams.get("date") ?? new Date().toISOString().slice(0, 10);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["procurement", params.id, procurementDate],
    queryFn: () => fetchProcurement(params.id, procurementDate),
    enabled: Boolean(params.id),
  });

  const [bagCount, setBagCount] = useState("");
  const [weightPerBag, setWeightPerBag] = useState("");
  const [perBagDeduction, setPerBagDeduction] = useState("");
  const [isSpotPayment, setIsSpotPayment] = useState(false);
  const [moisturePct, setMoisturePct] = useState("");
  const [ratePerQuintal, setRatePerQuintal] = useState("");
  const [notes, setNotes] = useState("");
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    if (data && !hydrated) {
      setBagCount(String(data.bag_count ?? ""));
      const perBagFromGross =
        data.bag_count > 0 && Number(data.gross_weight_kg) > 0
          ? String(Number(data.gross_weight_kg) / data.bag_count)
          : "";
      setWeightPerBag(data.weight_per_bag_kg ?? perBagFromGross);
      setPerBagDeduction(data.per_bag_deduction_kg ?? "2");
      setIsSpotPayment(Boolean(data.is_spot_payment));
      setMoisturePct(data.moisture_pct ?? "");
      setRatePerQuintal(Number(data.rate_per_quintal) > 0 ? data.rate_per_quintal : "");
      setNotes(data.notes ?? "");
      setHydrated(true);
    }
  }, [data, hydrated]);

  const calcPreview = useMemo(
    () =>
      calculateProcurementPreview({
        bagCount: Number(bagCount) || 0,
        weightPerBagKg: Number(weightPerBag) || 0,
        perBagDeductionKg: Number(perBagDeduction) || 2,
        ratePerQuintal: Number(ratePerQuintal) || 0,
        isSpotPayment,
      }),
    [bagCount, weightPerBag, perBagDeduction, ratePerQuintal, isSpotPayment],
  );

  const updateMutation = useMutation({
    mutationFn: () =>
      updateProcurement(params.id, procurementDate, {
        bag_count: Number(bagCount) || 0,
        weight_per_bag_kg: weightPerBag.trim() || null,
        per_bag_deduction_kg: perBagDeduction.trim() || null,
        moisture_pct: moisturePct.trim() || null,
        rate_per_quintal: ratePerQuintal.trim() || null,
        is_spot_payment: isSpotPayment,
        notes: notes.trim() || null,
      }),
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ["procurement", params.id] });
      queryClient.invalidateQueries({ queryKey: ["procurements"] });
      router.push(`/procurement/${updated.id}?date=${updated.procurement_date}`);
    },
  });

  const canSubmit =
    Number(bagCount) > 0 &&
    Number(weightPerBag) > 0 &&
    Number(ratePerQuintal) > 0 &&
    !updateMutation.isPending;

  return (
    <MuiPageShell
      title={data ? `Edit ${data.procurement_number}` : "Edit procurement"}
      description="Correct the intake or rate — the farmer ledger is adjusted automatically."
      actions={
        <Button
          component={Link}
          href={`/procurement/${params.id}?date=${procurementDate}`}
          startIcon={<ArrowBack />}
          variant="outlined"
        >
          Cancel
        </Button>
      }
    >
      {isLoading && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {isError && (
        <Alert severity="warning">
          {error instanceof Error ? error.message : "Could not load procurement"}
        </Alert>
      )}

      {data && (
        <Card sx={{ p: 3, maxWidth: 560 }}>
          <Stack
            spacing={2}
            component="form"
            onSubmit={(e) => {
              e.preventDefault();
              if (canSubmit) updateMutation.mutate();
            }}
          >
            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField
                fullWidth
                required
                label="Bag count"
                type="number"
                sx={TOUCH_FIELD_SX}
                inputProps={{ min: 1 }}
                value={bagCount}
                onChange={(e) => setBagCount(e.target.value)}
              />
              <TextField
                fullWidth
                required
                label="Weight per bag (kg)"
                type="number"
                sx={TOUCH_FIELD_SX}
                inputProps={{ min: 0, step: 0.001 }}
                value={weightPerBag}
                onChange={(e) => setWeightPerBag(e.target.value)}
                helperText="Gross = bags × kg/bag"
              />
              <TextField
                fullWidth
                label="Per-bag deduction (kg)"
                type="number"
                sx={TOUCH_FIELD_SX}
                inputProps={{ min: 0, step: 0.001 }}
                value={perBagDeduction}
                onChange={(e) => setPerBagDeduction(e.target.value)}
              />
            </Stack>

            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField
                fullWidth
                label="Moisture %"
                type="number"
                sx={TOUCH_FIELD_SX}
                inputProps={{ min: 0, max: 100, step: 0.1 }}
                value={moisturePct}
                onChange={(e) => setMoisturePct(e.target.value)}
              />
              <TextField
                fullWidth
                required
                label="Rate / quintal (₹)"
                type="number"
                sx={TOUCH_FIELD_SX}
                inputProps={{ min: 0, step: 0.01 }}
                value={ratePerQuintal}
                onChange={(e) => setRatePerQuintal(e.target.value)}
              />
            </Stack>

            <FormControlLabel
              control={
                <Checkbox
                  checked={isSpotPayment}
                  onChange={(e) => setIsSpotPayment(e.target.checked)}
                />
              }
              label="100% payment on spot"
              sx={{ alignItems: "flex-start", ml: 0 }}
            />

            {calcPreview && Number(ratePerQuintal) > 0 && (
              <Card variant="outlined" sx={{ p: 2, bgcolor: "action.hover" }}>
                <Typography variant="subtitle2" gutterBottom>
                  Live calculation preview
                </Typography>
                <Stack spacing={0.5}>
                  <Typography variant="body2">
                    Net weight: {calcPreview.netWeightKg} kg ({calcPreview.netQuintals} qtl)
                  </Typography>
                  <Typography variant="body2" fontWeight={600}>
                    Farmer net: ₹{calcPreview.netAmount.toLocaleString("en-IN")}
                  </Typography>
                </Stack>
              </Card>
            )}

            <TextField
              label="Notes"
              multiline
              minRows={2}
              sx={TOUCH_FIELD_SX}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />

            {updateMutation.isError && (
              <Alert severity="error">
                {updateMutation.error instanceof Error
                  ? updateMutation.error.message
                  : "Could not update procurement"}
              </Alert>
            )}

            <Button type="submit" variant="contained" size="large" disabled={!canSubmit} sx={{ minHeight: 48 }}>
              {updateMutation.isPending ? "Saving…" : "Save changes"}
            </Button>
          </Stack>
        </Card>
      )}
    </MuiPageShell>
  );
}
