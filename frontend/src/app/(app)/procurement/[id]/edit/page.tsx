"use client";

import {
  Alert,
  Box,
  Button,
  Card,
  Checkbox,
  CircularProgress,
  FormControlLabel,
  Grid2 as Grid,
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
import {
  fetchProcurement,
  recordWeighment,
  updateProcurement,
} from "@/features/procurements/api";
import { BagWeightEntry } from "@/features/procurements/bag-weight-entry";
import { bagWeightsValid, resizeBagWeights } from "@/features/procurements/bag-weights";
import { calculateProcurementPreview } from "@/features/procurements/calculate";
import { ProcurementIntakeSummary } from "@/features/procurements/procurement-intake-summary";
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
  const [bagWeights, setBagWeights] = useState<string[]>([]);
  const [perBagDeduction, setPerBagDeduction] = useState("");
  const [isSpotPayment, setIsSpotPayment] = useState(false);
  const [moisturePct, setMoisturePct] = useState("");
  const [ratePerQuintal, setRatePerQuintal] = useState("");
  const [notes, setNotes] = useState("");
  const [hydrated, setHydrated] = useState(false);

  const bags = Number(bagCount) || 0;

  useEffect(() => {
    if (data && !hydrated) {
      const count = data.bag_count ?? 0;
      setBagCount(String(count));
      if (data.bag_entries && data.bag_entries.length > 0) {
        const sorted = [...data.bag_entries].sort((a, b) => a.bag_number - b.bag_number);
        setBagWeights(sorted.map((e) => e.weight_kg));
      } else if (count > 0 && Number(data.gross_weight_kg) > 0) {
        const avg = Number(data.gross_weight_kg) / count;
        setBagWeights(resizeBagWeights([], count, String(avg)));
      } else {
        setBagWeights(resizeBagWeights([], count, data.weight_per_bag_kg ?? "50"));
      }
      setPerBagDeduction(data.per_bag_deduction_kg ?? "2");
      setIsSpotPayment(Boolean(data.is_spot_payment));
      setMoisturePct(data.moisture_pct ?? "");
      setRatePerQuintal(Number(data.rate_per_quintal) > 0 ? data.rate_per_quintal : "");
      setNotes(data.notes ?? "");
      setHydrated(true);
    }
  }, [data, hydrated]);

  useEffect(() => {
    if (!hydrated) return;
    setBagWeights((prev) => resizeBagWeights(prev, bags, prev[0] ?? "50"));
  }, [bags, hydrated]);

  const bagWeightsNumeric = useMemo(
    () => bagWeights.map((w) => Number(w)).filter((n) => Number.isFinite(n) && n > 0),
    [bagWeights],
  );

  const calcPreview = useMemo(
    () =>
      calculateProcurementPreview({
        bagCount: bags,
        bagWeightsKg:
          bagWeightsNumeric.length === bags && bags > 0 ? bagWeightsNumeric : undefined,
        perBagDeductionKg: Number(perBagDeduction) || 2,
        ratePerQuintal: Number(ratePerQuintal) || 0,
        isSpotPayment,
      }),
    [bags, bagWeightsNumeric, perBagDeduction, ratePerQuintal, isSpotPayment],
  );

  const updateMutation = useMutation({
    mutationFn: async () => {
      await recordWeighment(params.id, procurementDate, {
        bag_weights_kg: bagWeights.map((w) => w.trim()),
        bag_count: bags,
        per_bag_deduction_kg: perBagDeduction.trim() || null,
        moisture_pct: moisturePct.trim() || null,
      });
      return updateProcurement(params.id, procurementDate, {
        bag_count: bags,
        per_bag_deduction_kg: perBagDeduction.trim() || null,
        moisture_pct: moisturePct.trim() || null,
        rate_per_quintal: ratePerQuintal.trim() || null,
        is_spot_payment: isSpotPayment,
        notes: notes.trim() || null,
      });
    },
    onSuccess: (updated) => {
      queryClient.invalidateQueries({ queryKey: ["procurement", params.id] });
      queryClient.invalidateQueries({ queryKey: ["procurements"] });
      router.push(`/procurement/${updated.id}?date=${updated.procurement_date}`);
    },
  });

  const canSubmit =
    bagWeightsValid(bagWeights, bags) &&
    Number(ratePerQuintal) > 0 &&
    !updateMutation.isPending;

  const saving = updateMutation.isPending;

  return (
    <MuiPageShell
      title={data ? `Edit ${data.procurement_number}` : "Edit procurement"}
      description="Correct bag weights or rate — the farmer ledger is adjusted automatically."
      actions={
        <Button
          component={Link}
          href={`/procurement/${params.id}?date=${procurementDate}`}
          startIcon={<ArrowBack />}
          variant="outlined"
          disabled={saving}
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
        <Box sx={{ position: "relative" }}>
        <Grid container spacing={2.5} alignItems="flex-start" sx={{ pointerEvents: saving ? "none" : undefined, opacity: saving ? 0.6 : 1 }}>
          <Grid size={{ xs: 12, lg: 7 }}>
            <Card sx={{ p: 3 }}>
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
                    label="Number of bags"
                    type="number"
                    disabled={saving}
                    sx={TOUCH_FIELD_SX}
                    inputProps={{ min: 1 }}
                    value={bagCount}
                    onChange={(e) => setBagCount(e.target.value)}
                  />
                  <TextField
                    fullWidth
                    label="Per-bag deduction (kg)"
                    type="number"
                    disabled={saving}
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
                    disabled={saving}
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
                    disabled={saving}
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
                      disabled={saving}
                      onChange={(e) => setIsSpotPayment(e.target.checked)}
                    />
                  }
                  label="100% payment on spot"
                  sx={{ alignItems: "flex-start", ml: 0 }}
                />

                <TextField
                  label="Notes"
                  multiline
                  minRows={2}
                  disabled={saving}
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

                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={!canSubmit}
                  sx={{ minHeight: 48 }}
                >
                  {saving ? "Saving…" : "Save changes"}
                </Button>
              </Stack>
            </Card>
          </Grid>

          <Grid size={{ xs: 12, lg: 5 }}>
            <Stack spacing={2} sx={{ position: { lg: "sticky" }, top: { lg: 80 } }}>
              <BagWeightEntry
                bagWeights={bagWeights}
                onChange={setBagWeights}
                perBagDeductionKg={perBagDeduction}
                disabled={saving}
              />
              <ProcurementIntakeSummary
                preview={calcPreview}
                bagCount={bags}
                ratePerQuintal={Number(ratePerQuintal) || 0}
                isSpotPayment={isSpotPayment}
                perBagDeductionKg={Number(perBagDeduction) || 2}
              />
            </Stack>
          </Grid>
        </Grid>
        </Box>
      )}
    </MuiPageShell>
  );
}
