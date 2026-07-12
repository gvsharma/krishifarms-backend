import type { AriaAttributes } from "react";

/** Shared invalid-state detection for premium controls. */
export function isInvalid(
  error: boolean | undefined,
  ariaInvalid: AriaAttributes["aria-invalid"],
): boolean {
  return Boolean(error) || ariaInvalid === true || ariaInvalid === "true";
}
