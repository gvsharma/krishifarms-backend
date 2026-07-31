"use client";

import { ArrowBack } from "@mui/icons-material";
import {
  Alert,
  Button,
  Box,
  Card,
  CircularProgress,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import Link from "next/link";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useMemo, useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { createFieldService } from "@/features/field-services/api";
import { SERVICE_CATEGORIES, type ServiceCategory } from "@/features/field-services/constants";
import {
  EMPTY_FORM,
  FieldServiceForm,
  formValuesToCreatePayload,
  type FieldServiceFormValues,
} from "@/features/field-services/field-service-form";
import { categoryForVehicleSlug } from "@/features/field-services/url-prefill";

const VALID_CATEGORIES = new Set(SERVICE_CATEGORIES.map((c) => c.value));

function parseCategory(value: string | null): ServiceCategory | "" {
  if (!value || !VALID_CATEGORIES.has(value as ServiceCategory)) return "";
  return value as ServiceCategory;
}

function NewFieldServicePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();

  const farmerIdParam = searchParams.get("farmer_id");
  const vehicleParam = searchParams.get("vehicle");
  const categoryParam = searchParams.get("category");

  const initialCategory = useMemo(() => {
    const fromQuery = parseCategory(categoryParam);
    if (fromQuery) return fromQuery;
    if (vehicleParam) return categoryForVehicleSlug(vehicleParam);
    return "";
  }, [categoryParam, vehicleParam]);

  const [category, setCategory] = useState<ServiceCategory | "">(initialCategory);
  const [values, setValues] = useState<FieldServiceFormValues>(() => ({
    ...EMPTY_FORM,
    farmer_id: farmerIdParam ?? "",
  }));

  const createMutation = useMutation({
    mutationFn: () => {
      if (!category) throw new Error("Select a service category");
      return createFieldService(formValuesToCreatePayload(category, values));
    },
    onSuccess: (created) => {
      queryClient.invalidateQueries({ queryKey: ["field-services"] });
      router.push(`/field-services/${created.id}`);
    },
  });

  const handleCategoryChange = (next: ServiceCategory | "") => {
    setCategory(next);
    setValues({
      ...EMPTY_FORM,
      service_date: values.service_date,
      farmer_id: farmerIdParam ?? values.farmer_id,
    });
  };

  return (
    <MuiPageShell
      title="New field service"
      description="Record operational work — choose a category, then fill the fields relevant to that service."
      actions={
        <Button component={Link} href="/field-services" startIcon={<ArrowBack />} variant="outlined">
          Cancel
        </Button>
      }
    >
      <Card sx={{ p: { xs: 2, sm: 3 }, maxWidth: 800 }}>
        <Stack spacing={3}>
          <Box>
            <Typography variant="subtitle1" fontWeight={600} gutterBottom>
              Service details
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Choose a category first. The fields below update for that work type.
            </Typography>
            <TextField
              select
              required
              fullWidth
              label="Service category"
              value={category}
              onChange={(e) => handleCategoryChange(e.target.value as ServiceCategory | "")}
            >
              <MenuItem value="" disabled>
                Select category…
              </MenuItem>
              {SERVICE_CATEGORIES.map((c) => (
                <MenuItem key={c.value} value={c.value}>
                  {c.label}
                </MenuItem>
              ))}
            </TextField>
          </Box>

          {!category && (
            <Alert severity="info">
              Pick a category to show the operational form (hours, bags, amounts, equipment, etc.).
            </Alert>
          )}

          {category && (
            <Box>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                {SERVICE_CATEGORIES.find((c) => c.value === category)?.label ?? "Details"}
              </Typography>
              <FieldServiceForm
                category={category}
                values={values}
                onChange={setValues}
                onSubmit={() => createMutation.mutate()}
                submitLabel="Create service record"
                isSubmitting={createMutation.isPending}
                initialVehicleCode={vehicleParam}
                error={
                  createMutation.isError
                    ? createMutation.error instanceof Error
                      ? createMutation.error.message
                      : "Failed to create record"
                    : null
                }
              />
            </Box>
          )}
        </Stack>
      </Card>
    </MuiPageShell>
  );
}

export default function NewFieldServicePage() {
  return (
    <Suspense
      fallback={
        <MuiPageShell title="New field service" description="Loading…">
          <Stack alignItems="center" sx={{ py: 6 }}>
            <CircularProgress />
          </Stack>
        </MuiPageShell>
      }
    >
      <NewFieldServicePageContent />
    </Suspense>
  );
}
