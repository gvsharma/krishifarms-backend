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
import { ArrowBack } from "@mui/icons-material";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { fetchFarmers } from "@/features/farmers/api";
import { fetchVillages } from "@/features/master-data/api";
import { createProcurement, fetchCropTypes } from "@/features/procurements/api";
import { useTranslations } from "@/i18n/use-translations";

export default function NewProcurementPage() {
  const { t } = useTranslations();
  const router = useRouter();
  const queryClient = useQueryClient();
  const today = useMemo(() => new Date().toISOString().slice(0, 10), []);

  const [farmerId, setFarmerId] = useState("");
  const [cropTypeId, setCropTypeId] = useState("");
  const [villageId, setVillageId] = useState("");
  const [bagCount, setBagCount] = useState("0");
  const [notes, setNotes] = useState("");

  const farmersQuery = useQuery({ queryKey: ["farmers-wizard"], queryFn: () => fetchFarmers({ pageSize: 100 }) });
  const cropsQuery = useQuery({ queryKey: ["crop-types"], queryFn: fetchCropTypes });
  const villagesQuery = useQuery({ queryKey: ["villages-wizard"], queryFn: () => fetchVillages(1, 100) });

  const createMutation = useMutation({
    mutationFn: () =>
      createProcurement({
        farmer_id: farmerId,
        crop_type_id: cropTypeId,
        village_id: villageId,
        procurement_date: today,
        bag_count: Number(bagCount) || 0,
        notes: notes.trim() || null,
      }),
    onSuccess: (created) => {
      queryClient.invalidateQueries({ queryKey: ["procurements"] });
      router.push(`/procurement/${created.id}?date=${created.procurement_date}`);
    },
  });

  const loading = farmersQuery.isLoading || cropsQuery.isLoading || villagesQuery.isLoading;
  const canSubmit = farmerId && cropTypeId && villageId && !createMutation.isPending;

  return (
    <MuiPageShell
      title={t("operations.procurement.new.title")}
      description={t("operations.procurement.new.description")}
      actions={
        <Button component={Link} href="/procurement" startIcon={<ArrowBack />} variant="outlined">
          {t("common.cancel")}
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
          <Stack spacing={2} component="form" onSubmit={(e) => { e.preventDefault(); if (canSubmit) createMutation.mutate(); }}>
            <Typography variant="subtitle2" color="text.secondary">
              {t("operations.procurement.new.step1")}
            </Typography>

            <TextField
              select
              required
              label={t("common.farmer")}
              value={farmerId}
              onChange={(e) => {
                setFarmerId(e.target.value);
                const farmer = farmersQuery.data?.items.find((f) => f.id === e.target.value);
                if (farmer?.village_id) setVillageId(farmer.village_id);
              }}
            >
              {farmersQuery.data?.items.map((farmer) => (
                <MenuItem key={farmer.id} value={farmer.id}>
                  {farmer.full_name} ({farmer.farmer_code})
                </MenuItem>
              ))}
            </TextField>

            <TextField
              select
              required
              label={t("operations.procurement.new.cropType")}
              value={cropTypeId}
              onChange={(e) => setCropTypeId(e.target.value)}
            >
              {cropsQuery.data?.items.filter((c) => c.is_active).map((crop) => (
                <MenuItem key={crop.id} value={crop.id}>
                  {crop.name}
                </MenuItem>
              ))}
            </TextField>

            <TextField
              select
              required
              label={t("common.village")}
              value={villageId}
              onChange={(e) => setVillageId(e.target.value)}
            >
              {villagesQuery.data?.items.map((village) => (
                <MenuItem key={village.id} value={village.id}>
                  {village.name}
                </MenuItem>
              ))}
            </TextField>

            <TextField
              label={t("operations.procurement.new.bagCount")}
              type="number"
              inputProps={{ min: 0 }}
              value={bagCount}
              onChange={(e) => setBagCount(e.target.value)}
            />

            <TextField
              label={t("common.notes")}
              multiline
              minRows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />

            {createMutation.isError && (
              <Alert severity="error">
                {createMutation.error instanceof Error
                  ? createMutation.error.message
                  : t("operations.procurement.new.createError")}
              </Alert>
            )}

            <Button type="submit" variant="contained" disabled={!canSubmit}>
              {createMutation.isPending ? t("common.saving") : t("operations.procurement.new.saveDraft")}
            </Button>
          </Stack>
        </Card>
      )}
    </MuiPageShell>
  );
}
