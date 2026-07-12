"use client";

import { ArrowBack } from "@mui/icons-material";
import {
  Alert,
  Button,
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

const VALID_CATEGORIES = new Set(SERVICE_CATEGORIES.map((c) => c.value));

function parseCategory(value: string | null): ServiceCategory | "" {
  if (!value || !VALID_CATEGORIES.has(value as ServiceCategory)) return "";
  return value as ServiceCategory;
}

function NewFieldServicePageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const queryClient = useQueryClient();

  const initialCategory = useMemo(
    () => parseCategory(searchParams.get("category")),
    [searchParams],
  );

  const [category, setCategory] = useState<ServiceCategory | "">(initialCategory);
  const [values, setValues] = useState<FieldServiceFormValues>(EMPTY_FORM);

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
    setValues({ ...EMPTY_FORM, service_date: values.service_date });
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
      <Card sx={{ p: 3, maxWidth: 720 }}>
        <Stack spacing={3}>
          <TextField
            select
            required
            label="Service category"
            value={category}
            onChange={(e) => handleCategoryChange(e.target.value as ServiceCategory | "")}
            helperText="Fields below change based on category"
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

          {!category && (
            <Typography variant="body2" color="text.secondary">
              Pick a category to show the operational form (hours, bags, amounts, equipment, etc.).
            </Typography>
          )}

          {category && (
            <FieldServiceForm
              category={category}
              values={values}
              onChange={setValues}
              onSubmit={() => createMutation.mutate()}
              submitLabel="Create service record"
              isSubmitting={createMutation.isPending}
              error={
                createMutation.isError
                  ? createMutation.error instanceof Error
                    ? createMutation.error.message
                    : "Failed to create record"
                  : null
              }
            />
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
