"use client";

import {
  Alert,
  Box,
  Button,
  Card,
  CircularProgress,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { Add, ArrowBack } from "@mui/icons-material";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { SearchableSelect } from "@/components/ui/searchable-select";
import {
  Button as PremiumButton,
  Field,
  Input,
  PREMIUM_SCOPE,
  Scope,
} from "@/components/ui/premium";
import {
  PremiumDialog,
  PremiumDialogActions,
  PremiumDialogContent,
  PremiumDialogTitle,
} from "@/components/ui/premium-dialog";
import { SoftAlert } from "@/components/ui/soft-alert";
import { fetchFarmers } from "@/features/farmers/api";
import { createBuyer, fetchBuyers, fetchCropTypes, type Buyer } from "@/features/master-data/api";
import {
  EMPTY_LOCATION_CASCADE,
  LocationCascade,
  type LocationCascadeValue,
} from "@/features/master-data/location-cascade";
import { createProcurement } from "@/features/procurements/api";
import {
  PAYMENT_TERM_OPTIONS,
  mergeProcurementExtrasIntoNotes,
  type PaymentTermValue,
} from "@/features/procurements/draft-extras";
import { TOUCH_FIELD_SX } from "@/features/field-services/work-details";

export default function NewProcurementPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const today = useMemo(() => new Date().toISOString().slice(0, 10), []);

  const [farmerId, setFarmerId] = useState("");
  const [cropTypeId, setCropTypeId] = useState("");
  const [location, setLocation] = useState<LocationCascadeValue>({ ...EMPTY_LOCATION_CASCADE });
  const [hydrateVillageId, setHydrateVillageId] = useState<string | null>(null);
  const [bagCount, setBagCount] = useState("0");
  const [perBagDeduction, setPerBagDeduction] = useState("2");
  const [buyerId, setBuyerId] = useState("");
  const [paymentTerms, setPaymentTerms] = useState<PaymentTermValue | "">("one_week");
  const [paymentTermsCustom, setPaymentTermsCustom] = useState("");
  const [moisturePct, setMoisturePct] = useState("");
  const [ratePerQuintal, setRatePerQuintal] = useState("");
  const [notes, setNotes] = useState("");
  const [buyerDialogOpen, setBuyerDialogOpen] = useState(false);
  const [newBuyerName, setNewBuyerName] = useState("");
  const [newBuyerPhone, setNewBuyerPhone] = useState("");

  const farmersQuery = useQuery({
    queryKey: ["farmers-wizard"],
    queryFn: () => fetchFarmers({ pageSize: 100 }),
  });
  const cropsQuery = useQuery({
    queryKey: ["crop-types-procurement"],
    queryFn: () => fetchCropTypes(1, 100),
  });
  const buyersQuery = useQuery({
    queryKey: ["buyers-wizard"],
    queryFn: () => fetchBuyers(1, 100),
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

  const createBuyerMut = useMutation({
    mutationFn: () =>
      createBuyer({
        name: newBuyerName.trim(),
        phone: newBuyerPhone.trim() || null,
        is_active: true,
      }),
    onSuccess: (buyer: Buyer) => {
      queryClient.setQueryData(
        ["buyers-wizard"],
        (prev: { items: Buyer[]; total: number; page: number; page_size: number } | undefined) =>
          prev
            ? { ...prev, items: [buyer, ...prev.items], total: prev.total + 1 }
            : { items: [buyer], total: 1, page: 1, page_size: 100 },
      );
      queryClient.invalidateQueries({ queryKey: ["buyers"] });
      setBuyerId(buyer.id);
      setBuyerDialogOpen(false);
      setNewBuyerName("");
      setNewBuyerPhone("");
    },
  });

  const createMutation = useMutation({
    mutationFn: () => {
      // First-class buyer/terms on API (migration 026); planned moisture/rate stay in [kf:proc] notes.
      const mergedNotes = mergeProcurementExtrasIntoNotes(notes, {
        moisture_pct: moisturePct,
        rate_per_quintal: ratePerQuintal,
      });
      return createProcurement({
        farmer_id: farmerId,
        crop_type_id: cropTypeId,
        village_id: location.villageId,
        procurement_date: today,
        bag_count: Number(bagCount) || 0,
        per_bag_deduction_kg: perBagDeduction.trim() || null,
        buyer_id: buyerId || null,
        payment_terms: paymentTerms || null,
        payment_terms_custom:
          paymentTerms === "custom" ? paymentTermsCustom.trim() || null : null,
        notes: mergedNotes,
      });
    },
    onSuccess: (created) => {
      queryClient.invalidateQueries({ queryKey: ["procurements"] });
      router.push(`/procurement/${created.id}?date=${created.procurement_date}`);
    },
  });

  const loading = farmersQuery.isLoading || cropsQuery.isLoading || buyersQuery.isLoading;
  const canSubmit =
    Boolean(farmerId && cropTypeId && location.villageId) &&
    !createMutation.isPending &&
    (paymentTerms !== "custom" || paymentTermsCustom.trim().length > 0);

  const farmers = farmersQuery.data?.items ?? [];
  const crops = (cropsQuery.data?.items ?? []).filter((c) => c.is_active);
  const buyers = (buyersQuery.data?.items ?? []).filter((b) => b.is_active);

  return (
    <MuiPageShell
      title="New procurement"
      description="Create a draft ticket — then submit → weigh → price → confirm on the detail page."
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
              Capture basics — workflow continues on the ticket detail
            </Typography>

            <SearchableSelect
              options={farmers}
              getOptionLabel={(farmer) => `${farmer.full_name} (${farmer.farmer_code})`}
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
              getOptionLabel={(crop) => crop.name}
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

            <Stack direction="row" spacing={1} alignItems="flex-start">
              <Box sx={{ flex: 1 }}>
                <SearchableSelect
                  options={buyers}
                  getOptionLabel={(buyer) =>
                    buyer.name_te ? `${buyer.name} · ${buyer.name_te}` : buyer.name
                  }
                  isOptionEqualToValue={(a, b) => a.id === b.id}
                  value={buyers.find((b) => b.id === buyerId) ?? null}
                  onChange={(buyer) => setBuyerId(buyer?.id ?? "")}
                  label="Buyer"
                  placeholder="Search buyer…"
                  sx={TOUCH_FIELD_SX}
                />
              </Box>
              <Button
                variant="outlined"
                startIcon={<Add />}
                sx={{ minHeight: 52, mt: 0, whiteSpace: "nowrap" }}
                onClick={() => {
                  createBuyerMut.reset();
                  setBuyerDialogOpen(true);
                }}
              >
                Add
              </Button>
            </Stack>

            <TextField
              select
              label="Payment terms"
              sx={TOUCH_FIELD_SX}
              value={paymentTerms}
              onChange={(e) => setPaymentTerms(e.target.value as PaymentTermValue | "")}
            >
              {PAYMENT_TERM_OPTIONS.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </TextField>

            {paymentTerms === "custom" && (
              <TextField
                label="Custom payment terms"
                sx={TOUCH_FIELD_SX}
                value={paymentTermsCustom}
                onChange={(e) => setPaymentTermsCustom(e.target.value)}
                placeholder="e.g. 15 days after delivery"
              />
            )}

            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField
                fullWidth
                label="Moisture % (planned)"
                type="number"
                sx={TOUCH_FIELD_SX}
                inputProps={{ min: 0, max: 100, step: 0.1 }}
                value={moisturePct}
                onChange={(e) => setMoisturePct(e.target.value)}
                helperText={
                  selectedCrop?.default_moisture_pct != null
                    ? `Crop default: ${selectedCrop.default_moisture_pct}%`
                    : "Prefills weighment step"
                }
              />
              <TextField
                fullWidth
                label="Rate / quintal (₹)"
                type="number"
                sx={TOUCH_FIELD_SX}
                inputProps={{ min: 0, step: 0.01 }}
                value={ratePerQuintal}
                onChange={(e) => setRatePerQuintal(e.target.value)}
                helperText="Optional — apply-price uses crop price rules"
              />
            </Stack>

            <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
              <TextField
                fullWidth
                label="Bag count"
                type="number"
                sx={TOUCH_FIELD_SX}
                inputProps={{ min: 0 }}
                value={bagCount}
                onChange={(e) => setBagCount(e.target.value)}
              />
              <TextField
                fullWidth
                label="Per-bag deduction (kg)"
                type="number"
                sx={TOUCH_FIELD_SX}
                inputProps={{ min: 0, step: 0.001 }}
                value={perBagDeduction}
                onChange={(e) => setPerBagDeduction(e.target.value)}
                helperText="Kata weight deducted per bag at weighment. Default 2 kg."
              />
            </Stack>

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
              {createMutation.isPending ? "Saving…" : "Save draft"}
            </Button>
          </Stack>
        </Card>
      )}

      <PremiumDialog
        open={buyerDialogOpen}
        onClose={() => setBuyerDialogOpen(false)}
        maxWidth="xs"
      >
        <PremiumDialogTitle>Add buyer</PremiumDialogTitle>
        <PremiumDialogContent>
          <Scope className="flex flex-col gap-4 bg-transparent">
            <Field label="Name" required>
              <Input
                autoFocus
                value={newBuyerName}
                onChange={(e) => setNewBuyerName(e.target.value)}
              />
            </Field>
            <Field label="Phone">
              <Input
                value={newBuyerPhone}
                onChange={(e) => setNewBuyerPhone(e.target.value)}
              />
            </Field>
            {createBuyerMut.isError && (
              <SoftAlert severity="error">
                {createBuyerMut.error instanceof Error
                  ? createBuyerMut.error.message
                  : "Could not create buyer"}
              </SoftAlert>
            )}
          </Scope>
        </PremiumDialogContent>
        <PremiumDialogActions className={PREMIUM_SCOPE}>
          <PremiumButton variant="secondary" size="sm" onClick={() => setBuyerDialogOpen(false)}>
            Cancel
          </PremiumButton>
          <PremiumButton
            variant="primary"
            size="sm"
            disabled={newBuyerName.trim().length < 2 || createBuyerMut.isPending}
            onClick={() => createBuyerMut.mutate()}
          >
            {createBuyerMut.isPending ? "Saving…" : "Save buyer"}
          </PremiumButton>
        </PremiumDialogActions>
      </PremiumDialog>
    </MuiPageShell>
  );
}
