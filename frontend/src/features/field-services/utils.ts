/** Normalize user input to API decimal string (NUMERIC 14,2). */
export function toMoneyString(value: string, fallback = "0.00"): string {
  const trimmed = value.trim();
  if (!trimmed) return fallback;
  const num = Number(trimmed);
  if (Number.isNaN(num) || num < 0) return fallback;
  return num.toFixed(2);
}

/** True when value is empty, or a finite number >= 0. */
export function isValidMoneyInput(value: string): boolean {
  const trimmed = value.trim();
  if (!trimmed) return true;
  const num = Number(trimmed);
  return Number.isFinite(num) && num >= 0;
}

/** Optional decimal — empty string becomes null for API. */
export function toOptionalDecimal(value: string): string | null {
  const trimmed = value.trim();
  if (!trimmed) return null;
  const num = Number(trimmed);
  if (Number.isNaN(num) || num < 0) return null;
  return num.toFixed(2);
}

export function toOptionalInt(value: string): number | null {
  const trimmed = value.trim();
  if (!trimmed) return null;
  const num = Number.parseInt(trimmed, 10);
  if (Number.isNaN(num) || num < 0) return null;
  return num;
}

export function emptyToNull(value: string): string | null {
  const trimmed = value.trim();
  return trimmed || null;
}
