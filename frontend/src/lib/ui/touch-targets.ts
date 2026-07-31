/** Touch-friendly MUI TextField defaults for forms on mobile. */
export const TOUCH_FIELD_SX = {
  "& .MuiInputBase-root": { minHeight: 52 },
  "& .MuiSelect-select": { py: 1.5 },
} as const;

export const TOUCH_BUTTON_SX = {
  minHeight: 44,
  minWidth: 44,
} as const;
