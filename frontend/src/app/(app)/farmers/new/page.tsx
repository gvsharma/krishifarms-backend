"use client";

import {
  Alert,
  Button,
  Card,
  Stack,
  TextField,
} from "@mui/material";
import { ArrowBack } from "@mui/icons-material";
import Link from "next/link";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { createFarmer } from "@/features/farmers/api";
import { useAutoTeluguName } from "@/hooks/use-auto-telugu-name";
import {
  EMPTY_LOCATION_CASCADE,
  LocationCascade,
  type LocationCascadeValue,
} from "@/features/master-data/location-cascade";
import { TOUCH_FIELD_SX } from "@/lib/ui/touch-targets";
import {
  isValidIndianMobile,
  normalizeIndianMobile,
  phoneInputSlotProps,
  PHONE_REQUIRED_ERROR,
  sanitizePhoneInput,
} from "@/lib/validation/phone";

export default function NewFarmerPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [fullName, setFullName] = useState("");
  const [fullNameTe, setFullNameTe] = useState("");
  const [phone, setPhone] = useState("");
  const [location, setLocation] = useState<LocationCascadeValue>({ ...EMPTY_LOCATION_CASCADE });
  const [notes, setNotes] = useState("");

  const { onTeluguChange: onFarmerTeluguChange } = useAutoTeluguName(
    fullName,
    fullNameTe,
    setFullNameTe,
  );

  const phoneValid = isValidIndianMobile(phone);

  const createMutation = useMutation({
    mutationFn: () => {
      const normalized = normalizeIndianMobile(phone);
      if (!normalized) throw new Error(PHONE_REQUIRED_ERROR);
      return createFarmer({
        full_name: fullName.trim(),
        phone_primary: normalized,
        village_id: location.villageId,
        full_name_te: fullNameTe.trim() || null,
        notes: notes.trim() || null,
      });
    },
    onSuccess: (created) => {
      queryClient.invalidateQueries({ queryKey: ["farmers"] });
      router.push(`/farmers/${created.id}`);
    },
  });

  const canSubmit =
    fullName.trim().length >= 2 &&
    phoneValid &&
    location.villageId &&
    !createMutation.isPending;

  return (
    <MuiPageShell
      title="Add farmer"
      description="Register a farmer for procurement and ledger tracking."
      actions={
        <Button component={Link} href="/farmers" startIcon={<ArrowBack />} variant="outlined">
          Cancel
        </Button>
      }
    >
      <Card sx={{ p: 3, maxWidth: 560 }}>
        <Stack
          spacing={2}
          component="form"
          onSubmit={(e) => {
            e.preventDefault();
            if (canSubmit) createMutation.mutate();
          }}
        >
          <TextField
            required
            label="Full name"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            disabled={createMutation.isPending}
          />
          <TextField
            label="Full name (Telugu)"
            value={fullNameTe}
            onChange={(e) => onFarmerTeluguChange(e.target.value)}
            disabled={createMutation.isPending}
            slotProps={{
              input: { sx: { fontFamily: "var(--font-noto-telugu), sans-serif" } },
            }}
          />
          <TextField
            required
            label="Primary phone"
            value={phone}
            onChange={(e) => setPhone(sanitizePhoneInput(e.target.value))}
            error={phone.length > 0 && !phoneValid}
            helperText={phone.length > 0 && !phoneValid ? PHONE_REQUIRED_ERROR : "10 digits, numbers only"}
            slotProps={phoneInputSlotProps}
            sx={TOUCH_FIELD_SX}
          />

          <LocationCascade required value={location} onChange={setLocation} />

          <TextField
            label="Notes"
            multiline
            minRows={2}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
          />
          {createMutation.isError && (
            <Alert severity="error">
              {createMutation.error instanceof Error
                ? createMutation.error.message
                : "Failed to create farmer"}
            </Alert>
          )}
          <Button type="submit" variant="contained" disabled={!canSubmit}>
            {createMutation.isPending ? "Saving…" : "Create farmer"}
          </Button>
        </Stack>
      </Card>
    </MuiPageShell>
  );
}
