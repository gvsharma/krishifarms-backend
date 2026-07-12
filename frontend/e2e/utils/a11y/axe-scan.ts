import AxeBuilder from "@axe-core/playwright";
import type { Page } from "@playwright/test";
import type { ValidationIssue, ValidationResult } from "../validation/types";

const DEFAULT_FAIL_ON: Array<"critical" | "serious" | "moderate"> = ["critical", "serious", "moderate"];

export async function validateAccessibility(
  page: Page,
  failOn: Array<"critical" | "serious" | "moderate" | "minor"> = DEFAULT_FAIL_ON,
): Promise<ValidationResult> {
  const start = Date.now();
  const issues: ValidationIssue[] = [];

  try {
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();

    for (const violation of results.violations) {
      const impact = (violation.impact || "minor") as ValidationIssue["severity"];
      const severity =
        violation.impact === "critical" || violation.impact === "serious"
          ? "error"
          : violation.impact === "moderate"
            ? "warning"
            : "info";

      if (!failOn.includes(violation.impact as "critical" | "serious" | "moderate" | "minor")) {
        continue;
      }

      for (const node of violation.nodes) {
        issues.push({
          check: "accessibility",
          severity,
          message: `[${violation.impact}] ${violation.id}: ${violation.help} — ${node.failureSummary || violation.description}`,
          selector: node.target.join(", "),
          details: { impact, rule: violation.id },
        });
      }
    }

    if (issues.length > 0) {
      console.warn(
        "[validateAccessibility]",
        `Found ${results.violations.length} axe violations (${issues.length} nodes)`,
      );
    }
  } catch (err) {
    issues.push({
      check: "accessibility",
      severity: "error",
      message: `Axe scan failed: ${err instanceof Error ? err.message : String(err)}`,
    });
  }

  return {
    check: "accessibility",
    passed: issues.filter((i) => i.severity === "error").length === 0,
    issues,
    durationMs: Date.now() - start,
  };
}
