"use client";

import { Stack, type SxProps, type Theme } from "@mui/material";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useMemo } from "react";
import { SearchableSelect } from "@/components/ui/searchable-select";
import { useAuth } from "@/hooks/use-auth";
import {
  fetchDistricts,
  fetchMandals,
  fetchVillages,
  type District,
  type Mandal,
  type Village,
} from "./api";
import { locationLabels } from "./location-labels";

export type LocationCascadeValue = {
  districtId: string;
  mandalId: string;
  villageId: string;
};

export type LocationCascadeProps = {
  value: LocationCascadeValue;
  onChange: (next: LocationCascadeValue, meta?: { village: Village | null }) => void;
  /** When false, only District → Mandal (settings village create/edit). Default true. */
  showVillage?: boolean;
  required?: boolean;
  disabled?: boolean;
  textFieldSx?: SxProps<Theme>;
  /** Hydrate cascade from a known village id (e.g. farmer default). */
  hydrateVillageId?: string | null;
  /** Hydrate cascade by matching village name (field-service location string). */
  hydrateVillageName?: string | null;
};

const EMPTY: LocationCascadeValue = { districtId: "", mandalId: "", villageId: "" };

/** Large touch targets for field ops + admin forms. */
export const LOCATION_TOUCH_FIELD_SX = {
  "& .MuiInputBase-root": { minHeight: 52 },
  "& .MuiSelect-select": { py: 1.5 },
} as const;

const LISTBOX_SX = {
  "& .MuiAutocomplete-option": { minHeight: 48, py: 1.25 },
} as const;

export function LocationCascade({
  value,
  onChange,
  showVillage = true,
  required = false,
  disabled = false,
  textFieldSx = LOCATION_TOUCH_FIELD_SX,
  hydrateVillageId,
  hydrateVillageName,
}: LocationCascadeProps) {
  const { user } = useAuth();
  const labels = locationLabels(user?.preferred_locale ?? "en");

  const districtsQuery = useQuery({
    queryKey: ["districts", "cascade"],
    queryFn: () => fetchDistricts(1, 200),
    staleTime: 5 * 60_000,
  });

  const mandalsQuery = useQuery({
    queryKey: ["mandals", "cascade", value.districtId],
    queryFn: () => fetchMandals(1, 200, { district_id: value.districtId }),
    enabled: Boolean(value.districtId),
    staleTime: 5 * 60_000,
  });

  const villagesQuery = useQuery({
    queryKey: ["villages", "cascade", value.mandalId],
    queryFn: () => fetchVillages(1, 200, { mandal_id: value.mandalId }),
    enabled: showVillage && Boolean(value.mandalId),
    staleTime: 5 * 60_000,
  });

  const hydrateQuery = useQuery({
    queryKey: ["villages", "hydrate", hydrateVillageId, hydrateVillageName],
    queryFn: () => fetchVillages(1, 200),
    enabled: Boolean(
      (hydrateVillageId || hydrateVillageName) &&
        (!value.districtId || !value.mandalId || (showVillage && !value.villageId)),
    ),
    staleTime: 5 * 60_000,
  });

  useEffect(() => {
    const items = hydrateQuery.data?.items ?? [];
    if (!items.length) return;
    const match = hydrateVillageId
      ? items.find((v) => v.id === hydrateVillageId)
      : hydrateVillageName
        ? items.find((v) => v.name.toLowerCase() === hydrateVillageName.trim().toLowerCase())
        : undefined;
    if (!match?.district_id || !match?.mandal_id) return;
    if (
      value.districtId === match.district_id &&
      value.mandalId === match.mandal_id &&
      (!showVillage || value.villageId === match.id)
    ) {
      return;
    }
    onChange(
      {
        districtId: match.district_id,
        mandalId: match.mandal_id,
        villageId: showVillage ? match.id : "",
      },
      { village: match },
    );
    // eslint-disable-next-line react-hooks/exhaustive-deps -- hydrate once per match
  }, [hydrateQuery.data, hydrateVillageId, hydrateVillageName]);

  const districts = districtsQuery.data?.items ?? [];
  const mandals = mandalsQuery.data?.items ?? [];
  const villages = villagesQuery.data?.items ?? [];
  const hydrateItems = hydrateQuery.data?.items ?? [];

  const selectedDistrict = useMemo(
    () => districts.find((d) => d.id === value.districtId) ?? null,
    [districts, value.districtId],
  );
  const selectedMandal = useMemo(
    () => mandals.find((m) => m.id === value.mandalId) ?? null,
    [mandals, value.mandalId],
  );
  const selectedVillage = useMemo(() => {
    if (!value.villageId) return null;
    return (
      villages.find((v) => v.id === value.villageId) ??
      hydrateItems.find((v) => v.id === value.villageId) ??
      null
    );
  }, [villages, hydrateItems, value.villageId]);

  const villageOptions = useMemo(() => {
    if (selectedVillage && !villages.some((v) => v.id === selectedVillage.id)) {
      return [selectedVillage, ...villages];
    }
    return villages;
  }, [villages, selectedVillage]);

  const setDistrict = (district: District | null) => {
    onChange(
      {
        districtId: district?.id ?? "",
        mandalId: "",
        villageId: "",
      },
      { village: null },
    );
  };

  const setMandal = (mandal: Mandal | null) => {
    onChange(
      {
        districtId: value.districtId,
        mandalId: mandal?.id ?? "",
        villageId: "",
      },
      { village: null },
    );
  };

  const setVillage = (village: Village | null) => {
    onChange(
      {
        districtId: value.districtId,
        mandalId: value.mandalId,
        villageId: village?.id ?? "",
      },
      { village },
    );
  };

  return (
    <Stack spacing={2}>
      <SearchableSelect
        options={districts}
        getOptionLabel={(d) => d.name}
        isOptionEqualToValue={(a, b) => a.id === b.id}
        value={selectedDistrict}
        onChange={setDistrict}
        disabled={disabled}
        loading={districtsQuery.isLoading}
        required={required}
        label={labels.district}
        placeholder={labels.selectDistrict}
        sx={textFieldSx}
        listboxSx={LISTBOX_SX}
      />

      <SearchableSelect
        options={mandals}
        getOptionLabel={(m) => m.name}
        isOptionEqualToValue={(a, b) => a.id === b.id}
        value={selectedMandal}
        onChange={setMandal}
        disabled={disabled || !value.districtId}
        loading={Boolean(value.districtId) && mandalsQuery.isLoading}
        required={required}
        label={labels.mandal}
        placeholder={labels.selectMandal}
        helperText={!value.districtId ? "Select a district first" : undefined}
        sx={textFieldSx}
        listboxSx={LISTBOX_SX}
      />

      {showVillage && (
        <SearchableSelect
          options={villageOptions}
          getOptionLabel={(v) => v.name}
          isOptionEqualToValue={(a, b) => a.id === b.id}
          value={selectedVillage}
          onChange={setVillage}
          disabled={disabled || !value.mandalId}
          loading={Boolean(value.mandalId) && villagesQuery.isLoading}
          required={required}
          label={labels.village}
          placeholder={labels.selectVillage}
          helperText={!value.mandalId ? "Select a mandal first" : undefined}
          sx={textFieldSx}
          listboxSx={LISTBOX_SX}
        />
      )}
    </Stack>
  );
}

export { EMPTY as EMPTY_LOCATION_CASCADE };
