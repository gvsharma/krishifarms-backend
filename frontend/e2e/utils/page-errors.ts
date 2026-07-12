import { expect, type Page } from "@playwright/test";
import { getValidationContext } from "./validation/context";

/** Collect uncaught page exceptions for the duration of a test (backward compatible). */
export function trackPageErrors(page: Page): string[] {
  const ctx = getValidationContext(page);
  return ctx.consoleErrors;
}

export function expectNoPageErrors(pageErrors: string[]): void {
  expect(pageErrors, `Uncaught page errors:\n${pageErrors.join("\n")}`).toEqual([]);
}

export { validateConsoleErrors, assertNoConsoleErrors } from "./validation/validate-console";
