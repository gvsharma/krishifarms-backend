import { expect, type Page } from "@playwright/test";
import { validateAccessibility } from "../a11y/axe-scan";
import { validateColorContrast } from "../a11y/contrast-check";
import { validatePerformance } from "../perf/metrics";
import { recordValidationReport } from "../reports/validation-store";
import { validateVisualRegression } from "../visual/screenshot-compare";
import { getValidationContext } from "./context";
import { validateAllButtons } from "./validate-buttons";
import { validateConsoleErrors } from "./validate-console";
import { validateCSS } from "./validate-css";
import { validateDialogs } from "./validate-dialogs";
import { validateAllInputs } from "./validate-inputs";
import { validateLayout } from "./validate-layout";
import { validateNavigation } from "./validate-navigation";
import { validateNetworkRequests } from "./validate-network";
import { validateResponsive } from "./validate-responsive";
import { validateTables } from "./validate-tables";
import { validateTypography } from "./validate-typography";
import type {
  PageValidationReport,
  ValidateEntirePageOptions,
  ValidationCheck,
  ValidationResult,
} from "./types";

type CheckRunner = (page: Page, options: ValidateEntirePageOptions) => Promise<ValidationResult>;

const CHECK_RUNNERS: Record<ValidationCheck, CheckRunner> = {
  console: async (page) => validateConsoleErrors(page),
  network: async (page) => validateNetworkRequests(page),
  layout: async (page) => validateLayout(page),
  inputs: async (page) => validateAllInputs(page),
  buttons: async (page) => validateAllButtons(page),
  typography: async (page) => validateTypography(page),
  tables: async (page) => validateTables(page),
  dialogs: async (page) => validateDialogs(page),
  navigation: async (page) => validateNavigation(page),
  accessibility: async (page, opts) =>
    validateAccessibility(page, opts.a11yFailOn ?? ["critical", "serious", "moderate"]),
  responsive: async (page, opts) =>
    validateResponsive(page, opts.viewports ?? ["desktop"]),
  visual: async (page, opts) => {
    const name = opts.name ?? (new URL(page.url()).pathname.replace(/\//g, "-") || "page");
    return validateVisualRegression(page, name);
  },
  contrast: async (page) => validateColorContrast(page),
  css: async (page) => validateCSS(page),
  performance: async (page, opts) => validatePerformance(page, opts.performance),
};

const DEFAULT_CHECKS: ValidationCheck[] = [
  "console",
  "network",
  "layout",
  "inputs",
  "buttons",
  "typography",
  "tables",
  "dialogs",
  "navigation",
  "accessibility",
  "contrast",
  "css",
  "performance",
];

/**
 * Run the full enterprise validation suite on the current page.
 * New page tests only need: `await validateEntirePage(page);`
 */
export async function validateEntirePage(
  page: Page,
  options: ValidateEntirePageOptions = {},
): Promise<PageValidationReport> {
  getValidationContext(page);

  if (options.waitForNetworkIdle !== false) {
    await page.waitForLoadState("domcontentloaded");
    await page.waitForLoadState("networkidle").catch(() => undefined);
  }

  const skip = new Set(options.skip ?? []);
  const softFail = new Set(options.softFail ?? ["typography", "css", "performance"]);
  const checks: ValidationCheck[] = [...DEFAULT_CHECKS];

  if (options.visualRegression) checks.push("visual");
  if (options.viewports && options.viewports.length > 1) checks.push("responsive");

  const results: ValidationResult[] = [];

  for (const check of checks) {
    if (skip.has(check)) continue;
    const runner = CHECK_RUNNERS[check];
    const result = await runner(page, options);
    results.push(result);

    const isSoft = softFail.has(check);
    const errors = result.issues.filter((i) => i.severity === "error");

    if (!result.passed && errors.length > 0 && !isSoft) {
      const summary = errors.map((i) => `[${i.check}] ${i.message}`).join("\n");
      // Record partial report before failing
      recordValidationReport({
        pageName: options.name ?? page.url(),
        url: page.url(),
        timestamp: new Date().toISOString(),
        results,
        passed: false,
        totalIssues: results.reduce((n, r) => n + r.issues.length, 0),
        errorCount: results.reduce(
          (n, r) => n + r.issues.filter((i) => i.severity === "error").length,
          0,
        ),
        warningCount: results.reduce(
          (n, r) => n + r.issues.filter((i) => i.severity === "warning").length,
          0,
        ),
      });
      expect(errors, `Validation check "${check}" failed:\n${summary}`).toHaveLength(0);
    }
  }

  const errorCount = results.reduce(
    (n, r) => n + r.issues.filter((i) => i.severity === "error").length,
    0,
  );
  const warningCount = results.reduce(
    (n, r) => n + r.issues.filter((i) => i.severity === "warning").length,
    0,
  );

  const report: PageValidationReport = {
    pageName: options.name ?? page.url(),
    url: page.url(),
    timestamp: new Date().toISOString(),
    results,
    passed: results.every((r) => r.passed || softFail.has(r.check)),
    totalIssues: errorCount + warningCount,
    errorCount,
    warningCount,
  };

  recordValidationReport(report);
  return report;
}

export { validateConsoleErrors } from "./validate-console";
export { validateNetworkRequests } from "./validate-network";
export { validateLayout } from "./validate-layout";
export { validateAllInputs } from "./validate-inputs";
export { validateAllButtons } from "./validate-buttons";
export { validateTypography } from "./validate-typography";
export { validateTables } from "./validate-tables";
export { validateDialogs } from "./validate-dialogs";
export { validateNavigation } from "./validate-navigation";
export { validateResponsive } from "./validate-responsive";
export { validateCSS } from "./validate-css";
export type {
  PageValidationReport,
  ValidateEntirePageOptions,
  ValidationCheck,
  ValidationIssue,
  ValidationResult,
} from "./types";
