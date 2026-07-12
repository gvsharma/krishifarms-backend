import { expect, type Page } from "@playwright/test";
import { getValidationContext } from "./context";
import type { ValidationResult } from "./types";

export async function validateNetworkRequests(page: Page): Promise<ValidationResult> {
  const start = Date.now();
  const ctx = getValidationContext(page);
  const issues = ctx.issuesForNetwork();

  if (issues.length > 0) {
    console.error("[validateNetworkRequests]", issues.map((i) => i.message).join("\n"));
  }

  return {
    check: "network",
    passed: issues.length === 0,
    issues,
    durationMs: Date.now() - start,
  };
}

export async function assertNoFailedRequests(page: Page): Promise<void> {
  const result = await validateNetworkRequests(page);
  expect(result.issues, result.issues.map((i) => i.message).join("\n")).toHaveLength(0);
}
