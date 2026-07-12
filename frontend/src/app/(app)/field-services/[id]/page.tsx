"use client";

import { ArrowBack, Edit } from "@mui/icons-material";
import {
  Alert,
  Box,
  Button,
  Card,
  Chip,
  CircularProgress,
  Grid2 as Grid,
  Stack,
  Typography,
} from "@mui/material";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import { useCallback, useState } from "react";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { fetchFieldService, updateFieldService } from "@/features/field-services/api";
import { CATEGORY_FIELDS, type ServiceCategory } from "@/features/field-services/constants";
import {
  FieldServiceForm,
  formValuesToUpdatePayload,
  recordToFormValues,
  type FieldServiceFormValues,
} from "@/features/field-services/field-service-form";
import { formatInr } from "@/features/procurements/api";
import { useTranslations } from "@/i18n/use-translations";

export default function FieldServiceDetailPage() {
  const { t } = useTranslations();
  const params = useParams<{ id: string }>();
  const recordId = params.id;
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [formValues, setFormValues] = useState<FieldServiceFormValues | null>(null);

  const categoryLabel = useCallback(
    (value: string) => {
      const key = `operations.fieldServices.categories.${value}`;
      const label = t(key);
      return label === key ? value.replace(/_/g, " ") : label;
    },
    [t],
  );

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["field-service", recordId],
    queryFn: () => fetchFieldService(recordId),
    enabled: Boolean(recordId),
  });

  const updateMutation = useMutation({
    mutationFn: () => {
      if (!data || !formValues) throw new Error("Missing form data");
      return updateFieldService(
        data.id,
        formValuesToUpdatePayload(data.service_category as ServiceCategory, formValues),
      );
    },
    onSuccess: (updated) => {
      queryClient.setQueryData(["field-service", recordId], updated);
      queryClient.invalidateQueries({ queryKey: ["field-services"] });
      setEditing(false);
      setFormValues(null);
    },
  });

  const startEdit = () => {
    if (!data) return;
    setFormValues(recordToFormValues(data));
    setEditing(true);
  };

  const cancelEdit = () => {
    setEditing(false);
    setFormValues(null);
    updateMutation.reset();
  };

  const category = data?.service_category as ServiceCategory | undefined;
  const visibleFields = category ? new Set(CATEGORY_FIELDS[category]) : new Set<string>();

  return (
    <MuiPageShell
      title={data?.record_number ?? t("operations.fieldServices.detail.title")}
      description={
        data
          ? `${categoryLabel(data.service_category)} · ${data.service_date}`
          : t("common.loading")
      }
      actions={
        <Stack direction="row" spacing={1}>
          {!editing && data && (
            <Button startIcon={<Edit />} variant="contained" onClick={startEdit}>
              {t("common.edit")}
            </Button>
          )}
          <Button component={Link} href="/field-services" startIcon={<ArrowBack />} variant="outlined">
            {t("operations.fieldServices.detail.backToList")}
          </Button>
        </Stack>
      }
    >
      {isLoading && (
        <Box sx={{ display: "flex", justifyContent: "center", py: 6 }}>
          <CircularProgress />
        </Box>
      )}

      {isError && (
        <Alert severity="warning">
          {error instanceof Error ? error.message : t("operations.fieldServices.detail.loadError")}
        </Alert>
      )}

      {data && editing && formValues && category && (
        <Card sx={{ p: 3, maxWidth: 720 }}>
          <FieldServiceForm
            category={category}
            values={formValues}
            onChange={setFormValues}
            onSubmit={() => updateMutation.mutate()}
            submitLabel={t("operations.fieldServices.detail.saveChanges")}
            isSubmitting={updateMutation.isPending}
            error={
              updateMutation.isError
                ? updateMutation.error instanceof Error
                  ? updateMutation.error.message
                  : t("operations.fieldServices.detail.updateError")
                : null
            }
          />
          <Button sx={{ mt: 2 }} variant="text" onClick={cancelEdit}>
            {t("operations.fieldServices.detail.cancelEdit")}
          </Button>
        </Card>
      )}

      {data && !editing && (
        <Stack spacing={2}>
          <Card sx={{ p: 2 }}>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 2 }}>
              <Chip label={data.status} color="primary" size="small" />
              <Chip label={categoryLabel(data.service_category)} size="small" variant="outlined" />
            </Stack>

            <Grid container spacing={2}>
              <Grid size={{ xs: 6, sm: 4 }}>
                <DetailField label={t("operations.fieldServices.detail.serviceDate")} value={data.service_date} />
              </Grid>

              {visibleFields.has("farmer_id") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label={t("common.farmer")}
                    value={
                      data.farmer_name
                        ? `${data.farmer_name}${data.farmer_phone ? ` · ${data.farmer_phone}` : ""}`
                        : t("common.dash")
                    }
                  />
                </Grid>
              )}

              {visibleFields.has("activity_type_id") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label={t("operations.fieldServices.detail.activityType")}
                    value={data.activity_type_name ?? t("common.dash")}
                  />
                </Grid>
              )}

              {visibleFields.has("vehicle_type_id") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label={t("operations.fieldServices.detail.vehicleEquipment")}
                    value={data.vehicle_type_name ?? t("common.dash")}
                  />
                </Grid>
              )}

              {visibleFields.has("location") && (
                <Grid size={{ xs: 12, sm: 6 }}>
                  <DetailField
                    label={t("operations.fieldServices.detail.location")}
                    value={data.location ?? t("common.dash")}
                  />
                </Grid>
              )}

              {visibleFields.has("hours") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label={t("operations.fieldServices.detail.hours")}
                    value={data.hours ?? t("common.dash")}
                  />
                </Grid>
              )}

              {visibleFields.has("bag_count") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label={t("operations.fieldServices.detail.bagCount")}
                    value={data.bag_count != null ? String(data.bag_count) : t("common.dash")}
                  />
                </Grid>
              )}

              {visibleFields.has("quantity") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label={t("operations.fieldServices.detail.quantity")}
                    value={
                      data.quantity
                        ? `${data.quantity}${data.quantity_unit ? ` ${data.quantity_unit}` : ""}`
                        : t("common.dash")
                    }
                  />
                </Grid>
              )}

              {visibleFields.has("rate_per_unit") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label={t("operations.fieldServices.detail.ratePerUnit")}
                    value={data.rate_per_unit ? formatInr(data.rate_per_unit) : t("common.dash")}
                  />
                </Grid>
              )}

              {visibleFields.has("diesel_amount") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label={t("operations.fieldServices.detail.diesel")}
                    value={formatInr(data.diesel_amount)}
                  />
                </Grid>
              )}

              {visibleFields.has("amount_given") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label={t("operations.fieldServices.detail.amountGiven")}
                    value={formatInr(data.amount_given)}
                  />
                </Grid>
              )}

              {visibleFields.has("advance_amount") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label={t("operations.fieldServices.detail.advance")}
                    value={formatInr(data.advance_amount)}
                  />
                </Grid>
              )}

              {visibleFields.has("total_amount") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label={t("operations.fieldServices.detail.total")}
                    value={formatInr(data.total_amount)}
                  />
                </Grid>
              )}

              {visibleFields.has("pending_amount") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label={t("operations.fieldServices.detail.pending")}
                    value={formatInr(data.pending_amount)}
                  />
                </Grid>
              )}

              {visibleFields.has("cleaning_status") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label={t("operations.fieldServices.detail.cleaningStatus")}
                    value={data.cleaning_status ?? t("common.dash")}
                  />
                </Grid>
              )}

              {visibleFields.has("facility_status") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label={t("operations.fieldServices.detail.facilityStatus")}
                    value={data.facility_status ?? t("common.dash")}
                  />
                </Grid>
              )}

              {data.comments && (
                <Grid size={{ xs: 12 }}>
                  <DetailField label={t("common.comments")} value={data.comments} />
                </Grid>
              )}
            </Grid>
          </Card>
        </Stack>
      )}
    </MuiPageShell>
  );
}

function DetailField({ label, value }: { label: string; value: string }) {
  return (
    <Box>
      <Typography variant="caption" color="text.secondary">
        {label}
      </Typography>
      <Typography variant="body2" fontWeight={500}>
        {value}
      </Typography>
    </Box>
  );
}
