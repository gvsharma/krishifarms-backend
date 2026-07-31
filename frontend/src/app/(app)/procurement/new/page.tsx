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
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { SearchableSelect } from "@/components/ui/searchable-select";
import { fetchFarmers } from "@/features/farmers/api";
import { fetchCropTypes } from "@/features/master-data/api";
import { formatMasterOptionLabel } from "@/lib/bilingual";
import { useLocale } from "@/i18n/use-translation";
import {
  EMPTY_LOCATION_CASCADE,
  LocationCascade,
  type LocationCascadeValue,
} from "@/features/master-data/location-cascade";
import { createFieldEntry } from "@/features/procurements/api";
import { BagWeightEntry } from "@/features/procurements/bag-weight-entry";
import { bagWeightsValid, resizeBagWeights } from "@/features/procurements/bag-weights";
import { calculateProcurementPreview } from "@/features/procurements/calculate";
import { ProcurementIntakeSummary } from "@/features/procurements/procurement-intake-summary";
import { TOUCH_FIELD_SX } from "@/features/field-services/work-details";

export default function NewProcurementPage() {
  const locale = useLocale();
  const router = useRouter();
  const queryClient = useQueryClient();
  const today = useMemo(() => new Date().toISOString().slice(0, 10), []);

  const [farmerId, setFarmerId] = useState("");
  const [cropTypeId, setCropTypeId] = useState("");
  const [location, setLocation] = useState<LocationCascadeValue>({ ...EMPTY_LOCATION_CASCADE });
  const [hydrateVillageId, setHydrateVillageId] = useState<string | null>(null);
  const [bagCount, setBagCount] = useState("0");
  const [bagWeights, setBagWeights] = useState<string[]>([]);
  const [perBagDeduction, setPerBagDeduction] = useState("2");
  const [isSpotPayment, setIsSpotPayment] = useState(false);
  const [moisturePct, setMoisturePct] = useState("");
  const [ratePerQuintal, setRatePerQuintal] = useState("");
  const [notes, setNotes] = useState("");

  const bags = Number(bagCount) || 0;

  useEffect(() => {
    setBagWeights((prev) => resizeBagWeights(prev, bags, "50"));
  }, [bags]);

  const farmersQuery = useQuery({
    queryKey: ["farmers-wizard"],
    queryFn: () => fetchFarmers({ pageSize: 100 }),
  });
  const cropsQuery = useQuery({
    queryKey: ["crop-types-procurement"],
    queryFn: () => fetchCropTypes(1, 100),
  });

  const selectedCrop = useMemo(
    () => (cropsQuery.data?.items ?? []).find((c) => c.id === cropTypeId),
    [cropsQuery.data, cropTypeId],
  );

  const onCropChange = (id: string) => {
    setCropTypeId(id);
    const crop = (cropsQuery.data?.items ?? []).find((c) => c.id === id);
    if (crop?.default_moisture_pct != null && !moisturePct) {
      setMoisturePct(String(crop.default_moisture_pct));
    }
  };

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

  const createMutation = useMutation({
    mutationFn: () =>
      createFieldEntry({
        farmer_id: farmerId,
        crop_type_id: cropTypeId,
        village_id: location.villageId,
        procurement_date: today,
        bag_count: bags,
        bag_weights_kg: bagWeights.map((w) => w.trim()),
        per_bag_deduction_kg: perBagDeduction.trim() || null,
        moisture_pct: moisturePct.trim() || null,
        rate_per_quintal: ratePerQuintal.trim(),
        is_spot_payment: isSpotPayment,
        auto_confirm: true,
        notify_farmer: true,
        notes: notes.trim() || null,
      }),
    onSuccess: (created) => {
      queryClient.invalidateQueries({ queryKey: ["procurements"] });
      router.push(`/procurement/${created.id}?date=${created.procurement_date}`);
    },
  });

  const loading = farmersQuery.isLoading || cropsQuery.isLoading;
  const saving = createMutation.isPending;
  const canSubmit =
    Boolean(farmerId && cropTypeId && location.villageId) &&
    bagWeightsValid(bagWeights, bags) &&
    Number(ratePerQuintal) > 0 &&
    !createMutation.isPending;

  const farmers = farmersQuery.data?.items ?? [];
  const crops = (cropsQuery.data?.items ?? []).filter((c) => c.is_active);

  return (
    <MuiPageShell
      title="New procurement"
      description="Enter each bag weight and rate — the ticket is recorded as final. Buyer is assigned later."
      actions={
        <Button component={Link} href="/procurement" startIcon={<ArrowBack />} variant="outlined" disabled={saving}>
          Cancel
        </Button>
      }
    >
      {loading && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {!loading && (
        <Box sx={{ position: "relative" }}>
        <Grid container spacing={2.5} alignItems="flex-start" sx={{ pointerEvents: saving ? "none" : undefined, opacity: saving ? 0.6 : 1 }}>
          <Grid size={{ xs: 12, lg: 7 }}>
            <Card sx={{ p: 3 }}>
              <Stack
                spacing={2}
                component="form"
                onSubmit={(e) => {
                  e.preventDefault();
                  if (canSubmit) createMutation.mutate();
                }}
              >
                <Typography variant="subtitle2" color="text.secondary">
                  Farmer, crop, and pricing
                </Typography>

                <SearchableSelect
                  options={farmers}
                  getOptionLabel={(farmer) =>
                    `${formatMasterOptionLabel(locale, farmer.full_name, farmer.full_name_te)} (${farmer.farmer_code})`
                  }
                  isOptionEqualToValue={(a, b) => a.id === b.id}
                  value={farmers.find((f) => f.id === farmerId) ?? null}
                  onChange={(farmer) => {
                    setFarmerId(farmer?.id ?? "");
                    if (farmer?.village_id) setHydrateVillageId(farmer.village_id);
                  }}
                  label="Farmer"
                  required
                  disabled={saving}
                  sx={TOUCH_FIELD_SX}
                />

                <SearchableSelect
                  options={crops}
                  getOptionLabel={(crop) => formatMasterOptionLabel(locale, crop.name, crop.name_te)}
                  isOptionEqualToValue={(a, b) => a.id === b.id}
                  value={crops.find((c) => c.id === cropTypeId) ?? null}
                  onChange={(crop) => onCropChange(crop?.id ?? "")}
                  label="Crop type"
                  required
                  disabled={saving}
                  sx={TOUCH_FIELD_SX}
                />

                <LocationCascade
                  required
                  disabled={saving}
                  value={location}
                  onChange={setLocation}
                  textFieldSx={TOUCH_FIELD_SX}
                  hydrateVillageId={hydrateVillageId}
                />

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
                    helperText="Each bag gets its own weight on the right"
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
                    helperText="Kata weight per bag. Default 2 kg."
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
                    helperText={
                      selectedCrop?.default_moisture_pct != null
                        ? `Crop default: ${selectedCrop.default_moisture_pct}%`
                        : " "
                    }
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
                    helperText="Rate paid to the farmer"
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
                <Typography variant="caption" color="text.secondary" sx={{ mt: -1.5, display: "block" }}>
                  When checked, deducts ₹100 per net quintal from farmer payment (cash discount).
                </Typography>

                <TextField
                  label="Notes"
                  multiline
                  minRows={2}
                  disabled={saving}
                  sx={TOUCH_FIELD_SX}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />

                {createMutation.isError && (
                  <Alert severity="error">
                    {createMutation.error instanceof Error
                      ? createMutation.error.message
                      : "Could not create procurement"}
                  </Alert>
                )}

                <Button
                  type="submit"
                  variant="contained"
                  size="large"
                  disabled={!canSubmit}
                  sx={{ minHeight: 48 }}
                >
                  {saving ? "Saving…" : "Save procurement"}
                </Button>
              </Stack>
            </Card>
          </Grid>

          <Grid size={{ xs: 12, lg: 5 }}>
            <Stack
              spacing={2}
              sx={{
                position: { lg: "sticky" },
                top: { lg: 80 },
              }}
            >
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
