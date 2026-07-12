"use client";

import {
  Alert,
  Autocomplete,
  Button,
  Grid2 as Grid,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";
import { fetchFarmers } from "@/features/farmers/api";
import { fetchActivityTypes, fetchCropTypes, fetchVehicleTypes, fetchVillages } from "@/features/master-data/api";
import {
  EMPTY_LOCATION_CASCADE,
  LocationCascade,
  type LocationCascadeValue,
} from "@/features/master-data/location-cascade";
import {
  filterVehiclesForCategory,
  resolveVehicleWorkProfile,
  sortFleetVehicles,
  type VehicleWorkProfile,
} from "@/constants/fleet-inventory";
import {
  CATEGORY_FIELDS,
  CLEANING_STATUS_OPTIONS,
  FACILITY_STATUS_OPTIONS,
  STATUS_OPTIONS,
  type ServiceCategory,
} from "./constants";
import type { FieldServiceCreatePayload, FieldServiceRecord, FieldServiceUpdatePayload } from "./api";
import { emptyToNull, isValidMoneyInput, toMoneyString, toOptionalDecimal, toOptionalInt } from "./utils";
import {
  CULTIVATION_STAGE_OPTIONS,
  GOODS_TYPE_OPTIONS,
  LOCALITY_OPTIONS,
  SPRAY_TYPE_OPTIONS,
  TOUCH_FIELD_SX,
  TROLLEY_MATERIAL_OPTIONS,
  TROLLEY_PURPOSE_OPTIONS,
  mergeWorkDetailsIntoComments,
  parseWorkDetailsFromComments,
  type VehicleWorkDetails,
} from "./work-details";
import { SearchableSelect } from "@/components/ui/searchable-select";

export interface FieldServiceFormValues {
  service_date: string;
  farmer_id: string;
  activity_type_id: string;
  vehicle_type_id: string;
  /** Set when vehicle dropdown changes — used to serialize work details. */
  vehicle_type_code: string;
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
  // Vehicle-specific (persisted into comments marker)
  work_crop_code: string;
  work_crop_name: string;
  work_area_acres: string;
  work_cultivation_stage: string;
  work_trips: string;
  work_purpose: string;
  work_material: string;
  work_locality: string;
  work_distance_km: string;
  work_weight_kg: string;
  work_goods_type: string;
  work_tonnes: string;
  work_loading_point: string;
  work_unloading_point: string;
  work_litres: string;
  work_spray_type: string;
}

export const EMPTY_FORM: FieldServiceFormValues = {
  service_date: new Date().toISOString().slice(0, 10),
  farmer_id: "",
  activity_type_id: "",
  vehicle_type_id: "",
  vehicle_type_code: "",
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
  work_crop_code: "",
  work_crop_name: "",
  work_area_acres: "",
  work_cultivation_stage: "",
  work_trips: "1",
  work_purpose: "",
  work_material: "",
  work_locality: "local",
  work_distance_km: "",
  work_weight_kg: "",
  work_goods_type: "",
  work_tonnes: "",
  work_loading_point: "",
  work_unloading_point: "",
  work_litres: "",
  work_spray_type: "",
};

function workDetailsFromForm(
  profile: VehicleWorkProfile,
  values: FieldServiceFormValues,
): VehicleWorkDetails | null {
  if (!profile) return null;
  if (profile === "tractor") {
    return {
      profile,
      crop_code: values.work_crop_code || undefined,
      crop_name: values.work_crop_name || undefined,
      area_acres: values.work_area_acres || undefined,
      cultivation_stage: values.work_cultivation_stage || undefined,
    };
  }
  if (profile === "trolley") {
    return {
      profile,
      trips: values.work_trips || undefined,
      purpose: values.work_purpose || undefined,
      material: values.work_material || undefined,
    };
  }
  if (profile === "bolero") {
    return {
      profile,
      trips: values.work_trips || undefined,
      locality: values.work_locality || undefined,
      distance_km: values.work_distance_km || undefined,
      weight_kg: values.work_weight_kg || undefined,
      goods_type: values.work_goods_type || undefined,
    };
  }
  if (profile === "pump") {
    return {
      profile,
      crop_code: values.work_crop_code || undefined,
      crop_name: values.work_crop_name || undefined,
      area_acres: values.work_area_acres || undefined,
      litres: values.work_litres || undefined,
    };
  }
  if (profile === "drone") {
    return {
      profile,
      crop_code: values.work_crop_code || undefined,
      crop_name: values.work_crop_name || undefined,
      area_acres: values.work_area_acres || undefined,
      spray_type: values.work_spray_type || undefined,
    };
  }
  return {
    profile,
    trips: values.work_trips || undefined,
    distance_km: values.work_distance_km || undefined,
    tonnes: values.work_tonnes || undefined,
    loading_point: values.work_loading_point || undefined,
    unloading_point: values.work_unloading_point || undefined,
  };
}

function applyWorkDetailsToForm(
  base: FieldServiceFormValues,
  details: VehicleWorkDetails | null,
): FieldServiceFormValues {
  if (!details) return base;
  return {
    ...base,
    work_crop_code: details.crop_code ?? "",
    work_crop_name: details.crop_name ?? "",
    work_area_acres: details.area_acres ?? "",
    work_cultivation_stage: details.cultivation_stage ?? "",
    work_trips: details.trips ?? base.work_trips,
    work_purpose: details.purpose ?? "",
    work_material: details.material ?? "",
    work_locality: details.locality ?? base.work_locality,
    work_distance_km: details.distance_km ?? "",
    work_weight_kg: details.weight_kg ?? "",
    work_goods_type: details.goods_type ?? "",
    work_tonnes: details.tonnes ?? "",
    work_loading_point: details.loading_point ?? "",
    work_unloading_point: details.unloading_point ?? "",
    work_litres: details.litres ?? "",
    work_spray_type: details.spray_type ?? "",
  };
}

export function recordToFormValues(record: FieldServiceRecord): FieldServiceFormValues {
  const { details, freeComments } = parseWorkDetailsFromComments(record.comments);
  const base: FieldServiceFormValues = {
    ...EMPTY_FORM,
    service_date: record.service_date,
    farmer_id: record.farmer_id ?? "",
    activity_type_id: record.activity_type_id ?? "",
    vehicle_type_id: record.vehicle_type_id ?? "",
    vehicle_type_code: "",
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
    comments: freeComments,
  };
  return applyWorkDetailsToForm(base, details);
}

function buildComments(category: ServiceCategory, values: FieldServiceFormValues): string | null {
  const fields = new Set(CATEGORY_FIELDS[category]);
  const profile = fields.has("vehicle_type_id")
    ? resolveVehicleWorkProfile(values.vehicle_type_code)
    : null;
  const details = workDetailsFromForm(profile, values);
  return mergeWorkDetailsIntoComments(values.comments, details);
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
    comments: buildComments(category, values),
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
  const [locationCascade, setLocationCascade] = useState<LocationCascadeValue>({
    ...EMPTY_LOCATION_CASCADE,
  });

  const farmersQuery = useQuery({
    queryKey: ["farmers-field-service-form"],
    queryFn: () => fetchFarmers({ pageSize: 100 }),
    enabled: fields.has("farmer_id"),
    retry: false,
  });

  const activityTypesQuery = useQuery({
    queryKey: ["activity-types-field-service"],
    queryFn: () => fetchActivityTypes(1, 100),
    enabled: fields.has("activity_type_id"),
    retry: false,
  });

  const vehicleTypesQuery = useQuery({
    queryKey: ["vehicle-types-field-service"],
    queryFn: () => fetchVehicleTypes(1, 100),
    enabled: fields.has("vehicle_type_id"),
    retry: false,
  });

  const villagesQuery = useQuery({
    queryKey: ["villages-field-service"],
    queryFn: () => fetchVillages(1, 200),
    enabled: fields.has("location") || fields.has("vehicle_type_id"),
    retry: false,
  });

  const cropsQuery = useQuery({
    queryKey: ["crop-types-field-service"],
    queryFn: () => fetchCropTypes(1, 100),
    enabled: fields.has("vehicle_type_id"),
    retry: false,
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

  const dieselInvalid = fields.has("diesel_amount") && !isValidMoneyInput(values.diesel_amount);
  const moneyFieldsInvalid =
    dieselInvalid ||
    (fields.has("amount_given") && !isValidMoneyInput(values.amount_given)) ||
    (fields.has("advance_amount") && !isValidMoneyInput(values.advance_amount)) ||
    (fields.has("total_amount") && !isValidMoneyInput(values.total_amount)) ||
    (fields.has("pending_amount") && !isValidMoneyInput(values.pending_amount));

  const selectedVehicle = useMemo(
    () => vehicleOptions.find((v) => v.id === values.vehicle_type_id),
    [vehicleOptions, values.vehicle_type_id],
  );

  useEffect(() => {
    if (!selectedVehicle) return;
    if (values.vehicle_type_code === selectedVehicle.code) return;
    onChange({ ...values, vehicle_type_code: selectedVehicle.code });
    // Only sync code when vehicle options load for an existing id.
    // eslint-disable-next-line react-hooks/exhaustive-deps -- avoid loops on values
  }, [selectedVehicle?.code, values.vehicle_type_id]);

  const workProfile = useMemo(
    () =>
      fields.has("vehicle_type_id")
        ? resolveVehicleWorkProfile(values.vehicle_type_code || selectedVehicle?.code)
        : null,
    [fields, values.vehicle_type_code, selectedVehicle?.code],
  );

  const cropOptions = useMemo(
    () => (cropsQuery.data?.items ?? []).filter((c) => c.is_active),
    [cropsQuery.data],
  );

  const villageOptions = useMemo(() => villagesQuery.data?.items ?? [], [villagesQuery.data]);

  const set = (patch: Partial<FieldServiceFormValues>) => onChange({ ...values, ...patch });

  const onVehicleChange = (vehicleTypeId: string) => {
    const next = vehicleOptions.find((v) => v.id === vehicleTypeId);
    const profile = resolveVehicleWorkProfile(next?.code);
    set({
      vehicle_type_id: vehicleTypeId,
      vehicle_type_code: next?.code ?? "",
      work_trips:
        profile === "trolley" || profile === "bolero" || profile === "dcm" ? "1" : values.work_trips,
      work_locality: profile === "bolero" ? values.work_locality || "local" : values.work_locality,
    });
  };

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
            sx={TOUCH_FIELD_SX}
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
            sx={TOUCH_FIELD_SX}
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
            <Autocomplete
              options={farmersQuery.data?.items ?? []}
              getOptionLabel={(farmer) => `${farmer.full_name} (${farmer.farmer_code})`}
              value={(farmersQuery.data?.items ?? []).find((f) => f.id === values.farmer_id) ?? null}
              onChange={(_e, farmer) => set({ farmer_id: farmer?.id ?? "" })}
              disabled={disabled || farmersQuery.isLoading}
              renderInput={(params) => (
                <TextField {...params} label="Farmer" sx={TOUCH_FIELD_SX} placeholder="Search farmer…" />
              )}
            />
          </Grid>
        )}

        {fields.has("activity_type_id") && (
          <Grid size={{ xs: 12, sm: 6 }}>
            <SearchableSelect
              options={activityOptions}
              getOptionLabel={(activity) =>
                activity.name_te ? `${activity.name} · ${activity.name_te}` : activity.name
              }
              isOptionEqualToValue={(a, b) => a.id === b.id}
              value={activityOptions.find((a) => a.id === values.activity_type_id) ?? null}
              onChange={(activity) => set({ activity_type_id: activity?.id ?? "" })}
              label="Activity / equipment type"
              placeholder="Search activity…"
              disabled={disabled}
              loading={activityTypesQuery.isLoading}
              sx={TOUCH_FIELD_SX}
              clearable
            />
          </Grid>
        )}

        {fields.has("vehicle_type_id") && (
          <Grid size={{ xs: 12, sm: 6 }}>
            <Autocomplete
              options={vehicleOptions}
              getOptionLabel={(vehicle) =>
                vehicle.name_te ? `${vehicle.name} · ${vehicle.name_te}` : vehicle.name
              }
              value={vehicleOptions.find((v) => v.id === values.vehicle_type_id) ?? null}
              onChange={(_e, vehicle) => onVehicleChange(vehicle?.id ?? "")}
              disabled={disabled || vehicleTypesQuery.isLoading}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Vehicle / equipment type"
                  sx={TOUCH_FIELD_SX}
                  placeholder="Search vehicle…"
                />
              )}
            />
          </Grid>
        )}

        {workProfile && (
          <Grid size={{ xs: 12 }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 0.5 }}>
              {workProfile === "tractor" && "Work details (tractor / implement / harvester)"}
              {workProfile === "trolley" && "Trolley trip details"}
              {workProfile === "bolero" && "Bolero trip details"}
              {workProfile === "dcm" && "DCM trip details"}
              {workProfile === "pump" && "Fertilizer pump details"}
              {workProfile === "drone" && "Drone spray details"}
            </Typography>
          </Grid>
        )}

        {workProfile === "tractor" && (
          <>
            <Grid size={{ xs: 12, sm: 4 }}>
              <Autocomplete
                options={cropOptions}
                getOptionLabel={(crop) => crop.name}
                value={cropOptions.find((c) => c.code === values.work_crop_code) ?? null}
                onChange={(_e, crop) =>
                  set({
                    work_crop_code: crop?.code ?? "",
                    work_crop_name: crop?.name ?? "",
                  })
                }
                disabled={disabled || cropsQuery.isLoading}
                renderInput={(params) => (
                  <TextField {...params} label="Crop" sx={TOUCH_FIELD_SX} placeholder="Select crop…" />
                )}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                type="number"
                label="Area (acres)"
                sx={TOUCH_FIELD_SX}
                slotProps={{ htmlInput: { min: 0, step: 0.25 } }}
                value={values.work_area_acres}
                onChange={(e) => set({ work_area_acres: e.target.value })}
                disabled={disabled}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                select
                fullWidth
                label="Cultivation stage"
                sx={TOUCH_FIELD_SX}
                value={values.work_cultivation_stage}
                onChange={(e) => set({ work_cultivation_stage: e.target.value })}
                disabled={disabled}
              >
                <MenuItem value="">Select…</MenuItem>
                {CULTIVATION_STAGE_OPTIONS.map((opt) => (
                  <MenuItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
          </>
        )}

        {workProfile === "trolley" && (
          <>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                type="number"
                label="Trips"
                sx={TOUCH_FIELD_SX}
                slotProps={{ htmlInput: { min: 1, step: 1 } }}
                value={values.work_trips}
                onChange={(e) => set({ work_trips: e.target.value })}
                disabled={disabled}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                select
                fullWidth
                label="Purpose"
                sx={TOUCH_FIELD_SX}
                value={values.work_purpose}
                onChange={(e) => set({ work_purpose: e.target.value })}
                disabled={disabled}
              >
                <MenuItem value="">Select…</MenuItem>
                {TROLLEY_PURPOSE_OPTIONS.map((opt) => (
                  <MenuItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                select
                fullWidth
                label="Material"
                sx={TOUCH_FIELD_SX}
                value={values.work_material}
                onChange={(e) => set({ work_material: e.target.value })}
                disabled={disabled}
              >
                <MenuItem value="">Select…</MenuItem>
                {TROLLEY_MATERIAL_OPTIONS.map((opt) => (
                  <MenuItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
          </>
        )}

        {workProfile === "bolero" && (
          <>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                type="number"
                label="Trips"
                sx={TOUCH_FIELD_SX}
                slotProps={{ htmlInput: { min: 1, step: 1 } }}
                value={values.work_trips}
                onChange={(e) => set({ work_trips: e.target.value })}
                disabled={disabled}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                select
                fullWidth
                label="Local / Non-local"
                sx={TOUCH_FIELD_SX}
                value={values.work_locality}
                onChange={(e) => set({ work_locality: e.target.value })}
                disabled={disabled}
              >
                {LOCALITY_OPTIONS.map((opt) => (
                  <MenuItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                type="number"
                label="Distance (km)"
                sx={TOUCH_FIELD_SX}
                slotProps={{ htmlInput: { min: 0, step: 0.1 } }}
                value={values.work_distance_km}
                onChange={(e) => set({ work_distance_km: e.target.value })}
                disabled={disabled}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                fullWidth
                type="number"
                label="Weight (kg)"
                sx={TOUCH_FIELD_SX}
                slotProps={{ htmlInput: { min: 0, step: 1 } }}
                value={values.work_weight_kg}
                onChange={(e) => set({ work_weight_kg: e.target.value })}
                disabled={disabled}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                select
                fullWidth
                label="Goods type"
                sx={TOUCH_FIELD_SX}
                value={values.work_goods_type}
                onChange={(e) => set({ work_goods_type: e.target.value })}
                disabled={disabled}
              >
                <MenuItem value="">Select…</MenuItem>
                {GOODS_TYPE_OPTIONS.map((opt) => (
                  <MenuItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
          </>
        )}

        {workProfile === "dcm" && (
          <>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                type="number"
                label="Trips"
                sx={TOUCH_FIELD_SX}
                slotProps={{ htmlInput: { min: 1, step: 1 } }}
                value={values.work_trips}
                onChange={(e) => set({ work_trips: e.target.value })}
                disabled={disabled}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                type="number"
                label="Distance (km)"
                sx={TOUCH_FIELD_SX}
                slotProps={{ htmlInput: { min: 0, step: 0.1 } }}
                value={values.work_distance_km}
                onChange={(e) => set({ work_distance_km: e.target.value })}
                disabled={disabled}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                type="number"
                label="Tonnes"
                sx={TOUCH_FIELD_SX}
                slotProps={{ htmlInput: { min: 0, step: 0.1 } }}
                value={values.work_tonnes}
                onChange={(e) => set({ work_tonnes: e.target.value })}
                disabled={disabled}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <SearchableSelect
                options={villageOptions}
                getOptionLabel={(v) => v.name}
                isOptionEqualToValue={(a, b) => a.id === b.id}
                value={villageOptions.find((v) => v.name === values.work_loading_point) ?? null}
                onChange={(village) => set({ work_loading_point: village?.name ?? "" })}
                disabled={disabled}
                loading={villagesQuery.isLoading}
                label="Loading point"
                placeholder="Search village…"
                sx={TOUCH_FIELD_SX}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 6 }}>
              <SearchableSelect
                options={villageOptions}
                getOptionLabel={(v) => v.name}
                isOptionEqualToValue={(a, b) => a.id === b.id}
                value={villageOptions.find((v) => v.name === values.work_unloading_point) ?? null}
                onChange={(village) => set({ work_unloading_point: village?.name ?? "" })}
                disabled={disabled}
                loading={villagesQuery.isLoading}
                label="Unloading point"
                placeholder="Search village…"
                sx={TOUCH_FIELD_SX}
              />
            </Grid>
          </>
        )}

        {workProfile === "pump" && (
          <>
            <Grid size={{ xs: 12, sm: 4 }}>
              <Autocomplete
                options={cropOptions}
                getOptionLabel={(crop) => crop.name}
                value={cropOptions.find((c) => c.code === values.work_crop_code) ?? null}
                onChange={(_e, crop) =>
                  set({
                    work_crop_code: crop?.code ?? "",
                    work_crop_name: crop?.name ?? "",
                  })
                }
                disabled={disabled || cropsQuery.isLoading}
                renderInput={(params) => (
                  <TextField {...params} label="Crop" sx={TOUCH_FIELD_SX} placeholder="Select crop…" />
                )}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                type="number"
                label="Area (acres)"
                sx={TOUCH_FIELD_SX}
                slotProps={{ htmlInput: { min: 0, step: 0.25 } }}
                value={values.work_area_acres}
                onChange={(e) => set({ work_area_acres: e.target.value })}
                disabled={disabled}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                type="number"
                label="Litres applied"
                sx={TOUCH_FIELD_SX}
                slotProps={{ htmlInput: { min: 0, step: 0.5 } }}
                value={values.work_litres}
                onChange={(e) => set({ work_litres: e.target.value })}
                disabled={disabled}
              />
            </Grid>
          </>
        )}

        {workProfile === "drone" && (
          <>
            <Grid size={{ xs: 12, sm: 4 }}>
              <Autocomplete
                options={cropOptions}
                getOptionLabel={(crop) => crop.name}
                value={cropOptions.find((c) => c.code === values.work_crop_code) ?? null}
                onChange={(_e, crop) =>
                  set({
                    work_crop_code: crop?.code ?? "",
                    work_crop_name: crop?.name ?? "",
                  })
                }
                disabled={disabled || cropsQuery.isLoading}
                renderInput={(params) => (
                  <TextField {...params} label="Crop" sx={TOUCH_FIELD_SX} placeholder="Select crop…" />
                )}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                fullWidth
                type="number"
                label="Area (acres)"
                sx={TOUCH_FIELD_SX}
                slotProps={{ htmlInput: { min: 0, step: 0.25 } }}
                value={values.work_area_acres}
                onChange={(e) => set({ work_area_acres: e.target.value })}
                disabled={disabled}
              />
            </Grid>
            <Grid size={{ xs: 12, sm: 4 }}>
              <TextField
                select
                fullWidth
                label="Spray type"
                sx={TOUCH_FIELD_SX}
                value={values.work_spray_type}
                onChange={(e) => set({ work_spray_type: e.target.value })}
                disabled={disabled}
              >
                <MenuItem value="">Select…</MenuItem>
                {SPRAY_TYPE_OPTIONS.map((opt) => (
                  <MenuItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
          </>
        )}

        {fields.has("location") && (
          <Grid size={{ xs: 12 }}>
            <LocationCascade
              required={false}
              disabled={disabled}
              value={locationCascade}
              textFieldSx={TOUCH_FIELD_SX}
              hydrateVillageName={values.location || null}
              onChange={(next, meta) => {
                setLocationCascade(next);
                set({ location: meta?.village?.name ?? "" });
              }}
            />
          </Grid>
        )}

        {fields.has("hours") && (
          <Grid size={{ xs: 12, sm: 6 }}>
            <TextField
              fullWidth
              type="number"
              sx={TOUCH_FIELD_SX}
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
              sx={TOUCH_FIELD_SX}
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
              sx={TOUCH_FIELD_SX}
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
              select
              fullWidth
              label="Quantity unit"
              sx={TOUCH_FIELD_SX}
              value={values.quantity_unit}
              onChange={(e) => set({ quantity_unit: e.target.value })}
              disabled={disabled}
            >
              <MenuItem value="">Select…</MenuItem>
              <MenuItem value="kg">kg</MenuItem>
              <MenuItem value="quintal">Quintal</MenuItem>
              <MenuItem value="bags">Bags</MenuItem>
              <MenuItem value="acres">Acres</MenuItem>
            </TextField>
          </Grid>
        )}

        {fields.has("rate_per_unit") && (
          <Grid size={{ xs: 12, sm: 4 }}>
            <TextField
              fullWidth
              type="number"
              sx={TOUCH_FIELD_SX}
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
              sx={TOUCH_FIELD_SX}
              slotProps={{ htmlInput: { min: 0, step: 0.01 } }}
              label="Diesel cost (₹)"
              value={values.diesel_amount}
              onChange={(e) => set({ diesel_amount: e.target.value })}
              disabled={disabled}
              error={dieselInvalid}
              helperText={
                dieselInvalid
                  ? "Enter a non-negative amount (₹)"
                  : "Fuel cost for this service — shown on detail as Diesel cost"
              }
            />
          </Grid>
        )}

        {fields.has("amount_given") && (
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <TextField
              fullWidth
              type="number"
              sx={TOUCH_FIELD_SX}
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
              sx={TOUCH_FIELD_SX}
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
              sx={TOUCH_FIELD_SX}
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
              sx={TOUCH_FIELD_SX}
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
              sx={TOUCH_FIELD_SX}
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
              sx={TOUCH_FIELD_SX}
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
            sx={TOUCH_FIELD_SX}
            value={values.comments}
            onChange={(e) => set({ comments: e.target.value })}
            disabled={disabled}
          />
        </Grid>
      </Grid>

      {error && <Alert severity="error">{error}</Alert>}

      {!disabled && (
        <Button
          type="submit"
          variant="contained"
          size="large"
          disabled={isSubmitting || !values.service_date || moneyFieldsInvalid}
          sx={{ minHeight: 48 }}
        >
          {isSubmitting ? "Saving…" : submitLabel}
        </Button>
      )}
    </Stack>
  );
}
