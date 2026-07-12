"use client";

import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Grid2 as Grid,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
import { fetchFarmers } from "@/features/farmers/api";
import { fetchActivityTypes, fetchVehicleTypes } from "@/features/master-data/api";
import {
  filterVehiclesForCategory,
  sortFleetVehicles,
} from "@/constants/fleet-inventory";
import {
  CATEGORY_FIELDS,
  CLEANING_STATUS_OPTIONS,
  FACILITY_STATUS_OPTIONS,
  STATUS_OPTIONS,
  type ServiceCategory,
} from "./constants";
import type { FieldServiceCreatePayload, FieldServiceRecord, FieldServiceUpdatePayload } from "./api";
import { emptyToNull, toMoneyString, toOptionalDecimal, toOptionalInt } from "./utils";

export interface FieldServiceFormValues {
  service_date: string;
  farmer_id: string;
  activity_type_id: string;
  vehicle_type_id: string;
  location: string;
  hours: string;
  diesel_amount: string;
  amount_given: string;
  advance_amount: string;
  total_amount: string;
  pending_amount: string;
  bag_count: string;
  quantity: string;
  quantity_unit: string;
  rate_per_unit: string;
  cleaning_status: string;
  facility_status: string;
  status: string;
  comments: string;
}

export const EMPTY_FORM: FieldServiceFormValues = {
  service_date: new Date().toISOString().slice(0, 10),
  farmer_id: "",
  activity_type_id: "",
  vehicle_type_id: "",
  location: "",
  hours: "",
  diesel_amount: "0.00",
  amount_given: "0.00",
  advance_amount: "0.00",
  total_amount: "0.00",
  pending_amount: "0.00",
  bag_count: "",
  quantity: "",
  quantity_unit: "",
  rate_per_unit: "",
  cleaning_status: "",
  facility_status: "",
  status: "open",
  comments: "",
};

export function recordToFormValues(record: FieldServiceRecord): FieldServiceFormValues {
  return {
    service_date: record.service_date,
    farmer_id: record.farmer_id ?? "",
    activity_type_id: record.activity_type_id ?? "",
    vehicle_type_id: record.vehicle_type_id ?? "",
    location: record.location ?? "",
    hours: record.hours ?? "",
    diesel_amount: record.diesel_amount,
    amount_given: record.amount_given,
    advance_amount: record.advance_amount,
    total_amount: record.total_amount,
    pending_amount: record.pending_amount,
    bag_count: record.bag_count != null ? String(record.bag_count) : "",
    quantity: record.quantity ?? "",
    quantity_unit: record.quantity_unit ?? "",
    rate_per_unit: record.rate_per_unit ?? "",
    cleaning_status: record.cleaning_status ?? "",
    facility_status: record.facility_status ?? "",
    status: record.status,
    comments: record.comments ?? "",
  };
}

export function formValuesToCreatePayload(
  category: ServiceCategory,
  values: FieldServiceFormValues,
): FieldServiceCreatePayload {
  const fields = new Set(CATEGORY_FIELDS[category]);
  return {
    service_category: category,
    service_date: values.service_date,
    status: values.status,
    comments: emptyToNull(values.comments),
    ...(fields.has("farmer_id") && { farmer_id: values.farmer_id || null }),
    ...(fields.has("activity_type_id") && { activity_type_id: values.activity_type_id || null }),
    ...(fields.has("vehicle_type_id") && { vehicle_type_id: values.vehicle_type_id || null }),
    ...(fields.has("location") && { location: emptyToNull(values.location) }),
    ...(fields.has("hours") && { hours: toOptionalDecimal(values.hours) }),
    ...(fields.has("diesel_amount") && { diesel_amount: toMoneyString(values.diesel_amount) }),
    ...(fields.has("amount_given") && { amount_given: toMoneyString(values.amount_given) }),
    ...(fields.has("advance_amount") && { advance_amount: toMoneyString(values.advance_amount) }),
    ...(fields.has("total_amount") && { total_amount: toMoneyString(values.total_amount) }),
    ...(fields.has("pending_amount") && { pending_amount: toMoneyString(values.pending_amount) }),
    ...(fields.has("bag_count") && { bag_count: toOptionalInt(values.bag_count) }),
    ...(fields.has("quantity") && { quantity: toOptionalDecimal(values.quantity) }),
    ...(fields.has("quantity_unit") && { quantity_unit: emptyToNull(values.quantity_unit) }),
    ...(fields.has("rate_per_unit") && { rate_per_unit: toOptionalDecimal(values.rate_per_unit) }),
    ...(fields.has("cleaning_status") && { cleaning_status: values.cleaning_status || null }),
    ...(fields.has("facility_status") && { facility_status: values.facility_status || null }),
  };
}

export function formValuesToUpdatePayload(
  category: ServiceCategory,
  values: FieldServiceFormValues,
): FieldServiceUpdatePayload {
  const { service_category: _omit, ...rest } = formValuesToCreatePayload(category, values);
  return rest;
}

interface FieldServiceFormProps {
  category: ServiceCategory;
  values: FieldServiceFormValues;
  onChange: (values: FieldServiceFormValues) => void;
  onSubmit: () => void;
  submitLabel: string;
  isSubmitting?: boolean;
  error?: string | null;
  disabled?: boolean;
}

export function FieldServiceForm({
  category,
  values,
  onChange,
  onSubmit,
  submitLabel,
  isSubmitting = false,
  error = null,
  disabled = false,
}: FieldServiceFormProps) {
  const fields = useMemo(() => new Set(CATEGORY_FIELDS[category]), [category]);

  const farmersQuery = useQuery({
    queryKey: ["farmers-field-service-form"],
    queryFn: () => fetchFarmers({ pageSize: 100 }),
    enabled: fields.has("farmer_id"),
  });

  const activityTypesQuery = useQuery({
    queryKey: ["activity-types-field-service"],
    queryFn: () => fetchActivityTypes(1, 100),
    enabled: fields.has("activity_type_id"),
  });

  const vehicleTypesQuery = useQuery({
    queryKey: ["vehicle-types-field-service"],
    queryFn: () => fetchVehicleTypes(1, 100),
    enabled: fields.has("vehicle_type_id"),
  });

  const activityOptions = useMemo(
    () =>
      (activityTypesQuery.data?.items ?? []).filter(
        (a) => a.is_active && (a.service_category === category || a.service_category == null),
      ),
    [activityTypesQuery.data, category],
  );

  const vehicleOptions = useMemo(
    () =>
      sortFleetVehicles(
        filterVehiclesForCategory(category, vehicleTypesQuery.data?.items ?? []),
      ),
    [vehicleTypesQuery.data, category],
  );

  const loading =
    (fields.has("farmer_id") && farmersQuery.isLoading) ||
    (fields.has("activity_type_id") && activityTypesQuery.isLoading) ||
    (fields.has("vehicle_type_id") && vehicleTypesQuery.isLoading);

  const set = (patch: Partial<FieldServiceFormValues>) => onChange({ ...values, ...patch });

  if (loading) {
    return (
      <Box sx={{ display: "flex", justifyContent: "center", py: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Stack
      spacing={2}
      component="form"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
    >
      <Grid container spacing={2}>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            required
            fullWidth
            type="date"
            label="Service date"
            slotProps={{ inputLabel: { shrink: true } }}
            value={values.service_date}
            onChange={(e) => set({ service_date: e.target.value })}
            disabled={disabled}
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6 }}>
          <TextField
            select
            fullWidth
            label="Status"
            value={values.status}
            onChange={(e) => set({ status: e.target.value })}
            disabled={disabled}
          >
            {STATUS_OPTIONS.map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>
                {opt.label}
              </MenuItem>
            ))}
          </TextField>
        </Grid>

        {fields.has("farmer_id") && (
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              select
              fullWidth
              label="Farmer"
              value={values.farmer_id}
              onChange={(e) => set({ farmer_id: e.target.value })}
              disabled={disabled}
            >
              <MenuItem value="">None</MenuItem>
              {(farmersQuery.data?.items ?? []).map((farmer) => (
                <MenuItem key={farmer.id} value={farmer.id}>
                  {farmer.full_name} ({farmer.farmer_code})
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        )}

        {fields.has("activity_type_id") && (
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              select
              fullWidth
              label="Activity / equipment type"
              value={values.activity_type_id}
              onChange={(e) => set({ activity_type_id: e.target.value })}
              disabled={disabled}
            >
              <MenuItem value="">None</MenuItem>
              {activityOptions.map((activity) => (
                <MenuItem key={activity.id} value={activity.id}>
                  {activity.name}
                  {activity.name_te ? ` · ${activity.name_te}` : ""}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        )}

        {fields.has("vehicle_type_id") && (
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              select
              fullWidth
              label="Vehicle / equipment type"
              value={values.vehicle_type_id}
              onChange={(e) => set({ vehicle_type_id: e.target.value })}
              disabled={disabled}
            >
              <MenuItem value="">None</MenuItem>
              {vehicleOptions.map((vehicle) => (
                <MenuItem key={vehicle.id} value={vehicle.id}>
                  {vehicle.name}
                  {vehicle.name_te ? ` · ${vehicle.name_te}` : ""}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        )}

        {fields.has("location") && (
          <Grid size={{ xs: 12 }}>
            <TextField
              fullWidth
              label="Location"
              value={values.location}
              onChange={(e) => set({ location: e.target.value })}
              disabled={disabled}
            />
          </Grid>
        )}

        {fields.has("hours") && (
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              type="number"
              slotProps={{ htmlInput: { min: 0, step: 0.5 } }}
              label="Hours"
              value={values.hours}
              onChange={(e) => set({ hours: e.target.value })}
              disabled={disabled}
            />
          </Grid>
        )}

        {fields.has("bag_count") && (
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              type="number"
              slotProps={{ htmlInput: { min: 0, step: 1 } }}
              label="Bag count"
              value={values.bag_count}
              onChange={(e) => set({ bag_count: e.target.value })}
              disabled={disabled}
            />
          </Grid>
        )}

        {fields.has("quantity") && (
          <Grid size={{ xs: 12, sm: 4 }}>
            <TextField
              fullWidth
              type="number"
              slotProps={{ htmlInput: { min: 0, step: 0.01 } }}
              label="Quantity"
              value={values.quantity}
              onChange={(e) => set({ quantity: e.target.value })}
              disabled={disabled}
            />
          </Grid>
        )}

        {fields.has("quantity_unit") && (
          <Grid size={{ xs: 12, sm: 4 }}>
            <TextField
              fullWidth
              label="Quantity unit"
              placeholder="kg, quintal, bags…"
              value={values.quantity_unit}
              onChange={(e) => set({ quantity_unit: e.target.value })}
              disabled={disabled}
            />
          </Grid>
        )}

        {fields.has("rate_per_unit") && (
          <Grid size={{ xs: 12, sm: 4 }}>
            <TextField
              fullWidth
              type="number"
              slotProps={{ htmlInput: { min: 0, step: 0.01 } }}
              label="Rate per unit (₹)"
              value={values.rate_per_unit}
              onChange={(e) => set({ rate_per_unit: e.target.value })}
              disabled={disabled}
            />
          </Grid>
        )}

        {fields.has("diesel_amount") && (
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <TextField
              fullWidth
              type="number"
              slotProps={{ htmlInput: { min: 0, step: 0.01 } }}
              label="Diesel amount (₹)"
              value={values.diesel_amount}
              onChange={(e) => set({ diesel_amount: e.target.value })}
              disabled={disabled}
            />
          </Grid>
        )}

        {fields.has("amount_given") && (
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <TextField
              fullWidth
              type="number"
              slotProps={{ htmlInput: { min: 0, step: 0.01 } }}
              label="Amount given (₹)"
              value={values.amount_given}
              onChange={(e) => set({ amount_given: e.target.value })}
              disabled={disabled}
            />
          </Grid>
        )}

        {fields.has("advance_amount") && (
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <TextField
              fullWidth
              type="number"
              slotProps={{ htmlInput: { min: 0, step: 0.01 } }}
              label="Advance (₹)"
              value={values.advance_amount}
              onChange={(e) => set({ advance_amount: e.target.value })}
              disabled={disabled}
            />
          </Grid>
        )}

        {fields.has("total_amount") && (
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <TextField
              fullWidth
              type="number"
              slotProps={{ htmlInput: { min: 0, step: 0.01 } }}
              label="Total (₹)"
              value={values.total_amount}
              onChange={(e) => set({ total_amount: e.target.value })}
              disabled={disabled}
            />
          </Grid>
        )}

        {fields.has("pending_amount") && (
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <TextField
              fullWidth
              type="number"
              slotProps={{ htmlInput: { min: 0, step: 0.01 } }}
              label="Pending (₹)"
              value={values.pending_amount}
              onChange={(e) => set({ pending_amount: e.target.value })}
              disabled={disabled}
            />
          </Grid>
        )}

        {fields.has("cleaning_status") && (
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              select
              fullWidth
              label="Cleaning status"
              value={values.cleaning_status}
              onChange={(e) => set({ cleaning_status: e.target.value })}
              disabled={disabled}
            >
              <MenuItem value="">None</MenuItem>
              {CLEANING_STATUS_OPTIONS.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        )}

        {fields.has("facility_status") && (
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              select
              fullWidth
              label="Facility status"
              value={values.facility_status}
              onChange={(e) => set({ facility_status: e.target.value })}
              disabled={disabled}
            >
              <MenuItem value="">None</MenuItem>
              {FACILITY_STATUS_OPTIONS.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>
                  {opt.label}
                </MenuItem>
              ))}
            </TextField>
          </Grid>
        )}

        <Grid size={{ xs: 12 }}>
          <TextField
            fullWidth
            label="Comments"
            multiline
            minRows={2}
            value={values.comments}
            onChange={(e) => set({ comments: e.target.value })}
            disabled={disabled}
          />
        </Grid>
      </Grid>

      {error && <Alert severity="error">{error}</Alert>}

      {!disabled && (
        <Button type="submit" variant="contained" disabled={isSubmitting || !values.service_date}>
          {isSubmitting ? "Saving…" : submitLabel}
        </Button>
      )}
    </Stack>
  );
}
