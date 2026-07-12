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
import { useState } from "react";
import { CommentThread } from "@/components/comments/CommentThread";
import { MuiPageShell } from "@/components/shell/mui-page-shell";
import { fetchFieldService, updateFieldService } from "@/features/field-services/api";
import { CATEGORY_FIELDS, categoryLabel, type ServiceCategory } from "@/features/field-services/constants";
import {
  FieldServiceForm,
  formValuesToUpdatePayload,
  recordToFormValues,
  type FieldServiceFormValues,
} from "@/features/field-services/field-service-form";
import {
  CULTIVATION_STAGE_OPTIONS,
  GOODS_TYPE_OPTIONS,
  LOCALITY_OPTIONS,
  SPRAY_TYPE_OPTIONS,
  TROLLEY_MATERIAL_OPTIONS,
  TROLLEY_PURPOSE_OPTIONS,
  parseWorkDetailsFromComments,
} from "@/features/field-services/work-details";
import { formatInr } from "@/features/procurements/api";

function labelFor(options: readonly { value: string; label: string }[], value?: string) {
  if (!value) return "—";
  return options.find((o) => o.value === value)?.label ?? value;
}

export default function FieldServiceDetailPage() {
  const params = useParams<{ id: string }>();
  const recordId = params.id;
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [formValues, setFormValues] = useState<FieldServiceFormValues | null>(null);

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
  const { details: workDetails, freeComments } = parseWorkDetailsFromComments(data?.comments);

  return (
    <MuiPageShell
      title={data?.record_number ?? "Field service"}
      description={
        data
          ? `${categoryLabel(data.service_category)} · ${data.service_date}`
          : "Loading…"
      }
      actions={
        <Stack direction="row" spacing={1}>
          {!editing && data && (
            <Button startIcon={<Edit />} variant="contained" onClick={startEdit}>
              Edit
            </Button>
          )}
          <Button component={Link} href="/field-services" startIcon={<ArrowBack />} variant="outlined">
            Back to list
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
          {error instanceof Error ? error.message : "Could not load field service"}
        </Alert>
      )}

      {data && editing && formValues && category && (
        <Card sx={{ p: 3, maxWidth: 720 }}>
          <FieldServiceForm
            category={category}
            values={formValues}
            onChange={setFormValues}
            onSubmit={() => updateMutation.mutate()}
            submitLabel="Save changes"
            isSubmitting={updateMutation.isPending}
            error={
              updateMutation.isError
                ? updateMutation.error instanceof Error
                  ? updateMutation.error.message
                  : "Failed to update record"
                : null
            }
          />
          <Button sx={{ mt: 2 }} variant="text" onClick={cancelEdit}>
            Cancel edit
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
                <DetailField label="Service date" value={data.service_date} />
              </Grid>

              {visibleFields.has("farmer_id") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label="Farmer"
                    value={
                      data.farmer_name
                        ? `${data.farmer_name}${data.farmer_phone ? ` · ${data.farmer_phone}` : ""}`
                        : "—"
                    }
                  />
                </Grid>
              )}

              {visibleFields.has("activity_type_id") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField label="Activity type" value={data.activity_type_name ?? "—"} />
                </Grid>
              )}

              {visibleFields.has("vehicle_type_id") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField label="Vehicle / equipment" value={data.vehicle_type_name ?? "—"} />
                </Grid>
              )}

              {visibleFields.has("location") && (
                <Grid size={{ xs: 12, sm: 6 }}>
                  <DetailField label="Location" value={data.location ?? "—"} />
                </Grid>
              )}

              {visibleFields.has("hours") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField label="Hours" value={data.hours ?? "—"} />
                </Grid>
              )}

              {visibleFields.has("bag_count") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField label="Bag count" value={data.bag_count != null ? String(data.bag_count) : "—"} />
                </Grid>
              )}

              {visibleFields.has("quantity") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label="Quantity"
                    value={
                      data.quantity
                        ? `${data.quantity}${data.quantity_unit ? ` ${data.quantity_unit}` : ""}`
                        : "—"
                    }
                  />
                </Grid>
              )}

              {visibleFields.has("rate_per_unit") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField
                    label="Rate per unit"
                    value={data.rate_per_unit ? formatInr(data.rate_per_unit) : "—"}
                  />
                </Grid>
              )}

              {visibleFields.has("diesel_amount") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField label="Diesel cost" value={formatInr(data.diesel_amount)} />
                </Grid>
              )}

              {visibleFields.has("amount_given") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField label="Amount given" value={formatInr(data.amount_given)} />
                </Grid>
              )}

              {visibleFields.has("advance_amount") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField label="Advance" value={formatInr(data.advance_amount)} />
                </Grid>
              )}

              {visibleFields.has("total_amount") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField label="Total" value={formatInr(data.total_amount)} />
                </Grid>
              )}

              {visibleFields.has("pending_amount") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField label="Pending" value={formatInr(data.pending_amount)} />
                </Grid>
              )}

              {visibleFields.has("cleaning_status") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField label="Cleaning status" value={data.cleaning_status ?? "—"} />
                </Grid>
              )}

              {visibleFields.has("facility_status") && (
                <Grid size={{ xs: 6, sm: 4 }}>
                  <DetailField label="Facility status" value={data.facility_status ?? "—"} />
                </Grid>
              )}

              {workDetails?.profile === "tractor" && (
                <>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Crop" value={workDetails.crop_name || workDetails.crop_code || "—"} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Area (acres)" value={workDetails.area_acres || "—"} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField
                      label="Cultivation stage"
                      value={labelFor(CULTIVATION_STAGE_OPTIONS, workDetails.cultivation_stage)}
                    />
                  </Grid>
                </>
              )}

              {workDetails?.profile === "trolley" && (
                <>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Trips" value={workDetails.trips || "—"} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Purpose" value={labelFor(TROLLEY_PURPOSE_OPTIONS, workDetails.purpose)} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Material" value={labelFor(TROLLEY_MATERIAL_OPTIONS, workDetails.material)} />
                  </Grid>
                </>
              )}

              {workDetails?.profile === "bolero" && (
                <>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Trips" value={workDetails.trips || "—"} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Local / Non-local" value={labelFor(LOCALITY_OPTIONS, workDetails.locality)} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Distance (km)" value={workDetails.distance_km || "—"} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Weight (kg)" value={workDetails.weight_kg || "—"} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Goods type" value={labelFor(GOODS_TYPE_OPTIONS, workDetails.goods_type)} />
                  </Grid>
                </>
              )}

              {workDetails?.profile === "dcm" && (
                <>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Trips" value={workDetails.trips || "—"} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Distance (km)" value={workDetails.distance_km || "—"} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Tonnes" value={workDetails.tonnes || "—"} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 6 }}>
                    <DetailField label="Loading point" value={workDetails.loading_point || "—"} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 6 }}>
                    <DetailField label="Unloading point" value={workDetails.unloading_point || "—"} />
                  </Grid>
                </>
              )}

              {workDetails?.profile === "pump" && (
                <>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Crop" value={workDetails.crop_name || workDetails.crop_code || "—"} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Area (acres)" value={workDetails.area_acres || "—"} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Litres applied" value={workDetails.litres || "—"} />
                  </Grid>
                </>
              )}

              {workDetails?.profile === "drone" && (
                <>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Crop" value={workDetails.crop_name || workDetails.crop_code || "—"} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField label="Area (acres)" value={workDetails.area_acres || "—"} />
                  </Grid>
                  <Grid size={{ xs: 6, sm: 4 }}>
                    <DetailField
                      label="Spray type"
                      value={labelFor(SPRAY_TYPE_OPTIONS, workDetails.spray_type)}
                    />
                  </Grid>
                </>
              )}

              {freeComments && (
                <Grid size={{ xs: 12 }}>
                  <DetailField label="Comments" value={freeComments} />
                </Grid>
              )}
            </Grid>
          </Card>

          <Card sx={{ p: 2 }}>
            <CommentThread entityType="field_service" entityId={data.id} />
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
