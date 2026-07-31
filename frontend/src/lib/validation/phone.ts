/** Indian mobile: exactly 10 digits, numbers only. */

export const PHONE_DIGITS_LEN = 10;

export const PHONE_REQUIRED_ERROR = "Phone must be exactly 10 digits (numbers only)";

export function digitsOnlyPhone(raw: string): string {
  return raw.replace(/\D/g, "");
}

/** Strip non-digits; accept leading 91; return 10 digits or null. */
export function normalizeIndianMobile(raw: string): string | null {
  let digits = digitsOnlyPhone(raw);
  if (digits.length > PHONE_DIGITS_LEN && digits.startsWith("91")) {
    digits = digits.slice(-PHONE_DIGITS_LEN);
  }
  return digits.length === PHONE_DIGITS_LEN ? digits : null;
}

export function isValidIndianMobile(raw: string): boolean {
  return normalizeIndianMobile(raw) !== null;
}

/** Restrict typing to digits and cap at 10 for controlled inputs. */
export function sanitizePhoneInput(raw: string): string {
  return digitsOnlyPhone(raw).slice(0, PHONE_DIGITS_LEN);
}

export const phoneInputSlotProps = {
  htmlInput: {
    inputMode: "numeric" as const,
    pattern: "[0-9]*",
    maxLength: PHONE_DIGITS_LEN,
  },
};
