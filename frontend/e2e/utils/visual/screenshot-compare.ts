import { expect, type Page } from "@playwright/test";
import path from "node:path";
import type { ValidationIssue, ValidationResult } from "../validation/types";

const BASELINE_DIR = path.join(__dirname, "../../baselines");

export async function validateVisualRegression(
  page: Page,
  name: string,
): Promise<ValidationResult> {
  const start = Date.now();
  const issues: ValidationIssue[] = [];
  const snapshotName = name.replace(/[^a-z0-9-_]/gi, "-").toLowerCase();

  try {
    await expect(page).toHaveScreenshot(`${snapshotName}.png`, {
      fullPage: true,
      maxDiffPixels: 100,
      animations: "disabled",
      caret: "hide",
      timeout: 30_000,
    });
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    issues.push({
      check: "visual",
      severity: "error",
      message: `Visual regression failed for "${name}": ${message.split("\n")[0]}`,
      details: {
        baselineDir: BASELINE_DIR,
        snapshot: `${snapshotName}.png`,
        diffHint: "See test-results/ and playwright-report/ for diff images",
      },
    });
    console.error("[validateVisualRegression]", message);
  }

  return {
    check: "visual",
    passed: issues.length === 0,
    issues,
    durationMs: Date.now() - start,
  };
}
