"use client";

import { Autocomplete, TextField, type SxProps, type Theme } from "@mui/material";

export type SearchableSelectProps<T> = {
  options: T[];
  value: T | null;
  onChange: (value: T | null) => void;
  getOptionLabel: (option: T) => string;
  isOptionEqualToValue?: (a: T, b: T) => boolean;
  label: string;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  loading?: boolean;
  helperText?: string;
  sx?: SxProps<Theme>;
  /** Larger listbox option rows for touch. */
  listboxSx?: SxProps<Theme>;
  /** When true, allow clearing the selection. Default true. */
  clearable?: boolean;
  /** When true, raise popper z-index so lists work inside MUI Dialog. Default true. */
  inDialog?: boolean;
};

/**
 * Touch-friendly searchable dropdown (MUI Autocomplete wrapper).
 * Prefer this over ad-hoc Autocomplete copies for master-data FKs.
 */
export function SearchableSelect<T>({
  options,
  value,
  onChange,
  getOptionLabel,
  isOptionEqualToValue,
  label,
  placeholder,
  required = false,
  disabled = false,
  loading = false,
  helperText,
  sx,
  listboxSx,
  clearable = true,
  inDialog = true,
}: SearchableSelectProps<T>) {
  return (
    <Autocomplete
      options={options}
      value={value}
      onChange={(_e, next) => onChange(next)}
      getOptionLabel={getOptionLabel}
      isOptionEqualToValue={isOptionEqualToValue}
      disabled={disabled || loading}
      disableClearable={!clearable}
      slotProps={{
        popper: inDialog
          ? {
              sx: { zIndex: (theme) => theme.zIndex.modal + 2 },
            }
          : undefined,
        ...(listboxSx
          ? {
              listbox: { sx: listboxSx },
            }
          : {}),
      }}
      renderInput={(params) => (
        <TextField
          {...params}
          required={required}
          label={label}
          placeholder={placeholder}
          helperText={helperText}
          sx={sx}
        />
      )}
    />
  );
}
