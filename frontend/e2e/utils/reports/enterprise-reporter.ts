import type {
  FullConfig,
  FullResult,
  Reporter,
  Suite,
  TestCase,
  TestResult,
} from "@playwright/test/reporter";
import fs from "node:fs";
import path from "node:path";
import {
  clearValidationReports,
  readValidationReports,
  summarizeReports,
} from "./validation-store";

/**
 * Custom enterprise reporter — augments Playwright HTML report with
 * structured validation summaries (a11y, visual, console/network).
 */
class EnterpriseReporter implements Reporter {
  private outputDir = "playwright-report";

  onBegin(config: FullConfig, _suite: Suite): void {
    const reporter = config.reporter.find((r) => Array.isArray(r) && r[0] === "html");
    if (reporter && Array.isArray(reporter[1])) {
      this.outputDir = (reporter[1] as { outputFolder?: string }).outputFolder ?? this.outputDir;
    }
    clearValidationReports();
  }

  onTestEnd(_test: TestCase, result: TestResult): void {
    if (result.status !== "passed") return;
  }

  onEnd(result: FullResult): void {
    const reports = readValidationReports();
    const summary = summarizeReports(reports);
    console.log("\n" + summary);

    const payload = {
      generatedAt: new Date().toISOString(),
      status: result.status,
      totalTests: result.status === "passed" ? reports.length : undefined,
      reports,
      accessibility: {
        totalViolations: reports.reduce(
          (n, r) =>
            n +
            (r.results.find((x) => x.check === "accessibility")?.issues.length ?? 0),
          0,
        ),
      },
      visual: {
        failures: reports.flatMap((r) =>
          (r.results.find((x) => x.check === "visual")?.issues ?? []).map((i) => ({
            page: r.pageName,
            message: i.message,
            details: i.details,
          })),
        ),
      },
      consoleAndNetwork: reports.flatMap((r) =>
        r.results
          .filter((x) => x.check === "console" || x.check === "network")
          .flatMap((x) => x.issues.map((i) => ({ page: r.pageName, check: x.check, message: i.message }))),
      ),
    };

    const outDir = path.join(process.cwd(), this.outputDir);
    fs.mkdirSync(outDir, { recursive: true });
    fs.writeFileSync(
      path.join(outDir, "enterprise-validation.json"),
      JSON.stringify(payload, null, 2),
      "utf-8",
    );
  }
}

export default EnterpriseReporter;
