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
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
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
import { calculateProcurementPreview } from "@/features/procurements/calculate";
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
  const [weightPerBag, setWeightPerBag] = useState("50");
  const [perBagDeduction, setPerBagDeduction] = useState("2");
  const [isSpotPayment, setIsSpotPayment] = useState(false);
  const [moisturePct, setMoisturePct] = useState("");
  const [ratePerQuintal, setRatePerQuintal] = useState("");
  const [notes, setNotes] = useState("");

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

  const createMutation = useMutation({
    mutationFn: () =>
      createFieldEntry({
        farmer_id: farmerId,
        crop_type_id: cropTypeId,
        village_id: location.villageId,
        procurement_date: today,
        bag_count: Number(bagCount) || 0,
        weight_per_bag_kg: weightPerBag.trim(),
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
  const canSubmit =
    Boolean(farmerId && cropTypeId && location.villageId) &&
    Number(bagCount) > 0 &&
    Number(weightPerBag) > 0 &&
    Number(ratePerQuintal) > 0 &&
    !createMutation.isPending;

  const farmers = farmersQuery.data?.items ?? [];
  const crops = (cropsQuery.data?.items ?? []).filter((c) => c.is_active);

  return (
    <MuiPageShell
      title="New procurement"
      description="Enter the crop intake — the ticket is recorded as final. Buyer is assigned separately later."
      actions={
        <Button component={Link} href="/procurement" startIcon={<ArrowBack />} variant="outlined">
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
        <Card sx={{ p: 3, maxWidth: 560 }}>
          <Stack
            spacing={2}
            component="form"
            onSubmit={(e) => {
              e.preventDefault();
              if (canSubmit) createMutation.mutate();
            }}
          >
            <Typography variant="subtitle2" color="text.secondary">
              Record the farmer&apos;s crop intake and rate
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
              sx={TOUCH_FIELD_SX}
            />

            <LocationCascade
              required
              value={location}
              onChange={setLocation}
              textFieldSx={TOUCH_FIELD_SX}
              hydrateVillageId={hydrateVillageId}
            />

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
                helperText="Kata weight per bag. Default 2 kg."
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
                  onChange={(e) => setIsSpotPayment(e.target.checked)}
                />
              }
              label="100% payment on spot"
              sx={{ alignItems: "flex-start", ml: 0 }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: -1.5, display: "block" }}>
              When checked, deducts ₹100 per net quintal from farmer payment (cash discount).
            </Typography>

            {calcPreview && Number(ratePerQuintal) > 0 && (
              <Card variant="outlined" sx={{ p: 2, bgcolor: "action.hover" }}>
                <Typography variant="subtitle2" gutterBottom>
                  Live calculation preview
                </Typography>
                <Stack spacing={0.5}>
                  <Typography variant="body2">
                    Gross weight: {calcPreview.grossWeightKg} kg · Kata: −{calcPreview.bagWeightDeductionKg} kg
                  </Typography>
                  <Typography variant="body2">
                    Net weight: {calcPreview.netWeightKg} kg ({calcPreview.netQuintals} qtl)
                  </Typography>
                  <Typography variant="body2">
                    Gross amount: ₹{calcPreview.grossAmount.toLocaleString("en-IN")}
                    {calcPreview.spotDeductionAmount > 0 &&
                      ` · Spot: −₹${calcPreview.spotDeductionAmount.toLocaleString("en-IN")}`}
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

            {createMutation.isError && (
              <Alert severity="error">
                {createMutation.error instanceof Error
                  ? createMutation.error.message
                  : "Could not create procurement"}
              </Alert>
            )}

            <Button type="submit" variant="contained" size="large" disabled={!canSubmit} sx={{ minHeight: 48 }}>
              {createMutation.isPending ? "Saving…" : "Save procurement"}
            </Button>
          </Stack>
        </Card>
      )}
    </MuiPageShell>
  );
}
