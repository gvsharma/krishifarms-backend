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
import {
  EMPTY_LOCATION_CASCADE,
  LocationCascade,
  type LocationCascadeValue,
} from "@/features/master-data/location-cascade";

export default function NewFarmerPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [fullName, setFullName] = useState("");
  const [fullNameTe, setFullNameTe] = useState("");
  const [phone, setPhone] = useState("");
  const [location, setLocation] = useState<LocationCascadeValue>({ ...EMPTY_LOCATION_CASCADE });
  const [notes, setNotes] = useState("");

  const createMutation = useMutation({
    mutationFn: () =>
      createFarmer({
        full_name: fullName.trim(),
        phone_primary: phone.trim(),
        village_id: location.villageId,
        full_name_te: fullNameTe.trim() || null,
        notes: notes.trim() || null,
      }),
    onSuccess: (created) => {
      queryClient.invalidateQueries({ queryKey: ["farmers"] });
      router.push(`/farmers/${created.id}`);
    },
  });

  const canSubmit =
    fullName.trim().length >= 2 &&
    phone.trim().length >= 10 &&
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
          />
          <TextField
            label="Full name (Telugu)"
            value={fullNameTe}
            onChange={(e) => setFullNameTe(e.target.value)}
          />
          <TextField
            required
            label="Primary phone"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            helperText="10–20 digits"
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
