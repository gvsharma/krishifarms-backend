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
} from "@mui/material";
import { ArrowBack } from "@mui/icons-material";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { createFarmer } from "@/features/farmers/api";
import { fetchVillages } from "@/features/master-data/api";

export default function NewFarmerPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [fullName, setFullName] = useState("");
  const [fullNameTe, setFullNameTe] = useState("");
  const [phone, setPhone] = useState("");
  const [villageId, setVillageId] = useState("");
  const [notes, setNotes] = useState("");

  const villagesQuery = useQuery({
    queryKey: ["villages-farmer-form"],
    queryFn: () => fetchVillages(1, 100),
  });

  const createMutation = useMutation({
    mutationFn: () =>
      createFarmer({
        full_name: fullName.trim(),
        phone_primary: phone.trim(),
        village_id: villageId,
        full_name_te: fullNameTe.trim() || null,
        notes: notes.trim() || null,
      }),
    onSuccess: (created) => {
      queryClient.invalidateQueries({ queryKey: ["farmers"] });
      router.push(`/farmers/${created.id}`);
    },
  });

  const canSubmit =
    fullName.trim().length >= 2 && phone.trim().length >= 10 && villageId && !createMutation.isPending;

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
      {villagesQuery.isLoading && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {!villagesQuery.isLoading && (
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
            <TextField
              select
              required
              label="Village"
              value={villageId}
              onChange={(e) => setVillageId(e.target.value)}
            >
              {(villagesQuery.data?.items ?? []).map((v) => (
                <MenuItem key={v.id} value={v.id}>
                  {v.name}
                </MenuItem>
              ))}
            </TextField>
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
      )}
    </MuiPageShell>
  );
}
