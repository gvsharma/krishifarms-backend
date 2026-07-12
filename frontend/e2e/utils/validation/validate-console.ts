import { expect, type Page } from "@playwright/test";
import { getValidationContext } from "./context";
import type { ValidationResult } from "./types";

export async function validateConsoleErrors(page: Page): Promise<ValidationResult> {
  const start = Date.now();
  const ctx = getValidationContext(page);
  const issues = ctx.issuesForConsole();

  if (issues.length > 0) {
    console.error("[validateConsoleErrors]", issues.map((i) => i.message).join("\n"));
  }

  return {
    check: "console",
    passed: issues.length === 0,
    issues,
    durationMs: Date.now() - start,
  };
}

export async function assertNoConsoleErrors(page: Page): Promise<void> {
  const result = await validateConsoleErrors(page);
  expect(result.issues, result.issues.map((i) => i.message).join("\n")).toHaveLength(0);
}
