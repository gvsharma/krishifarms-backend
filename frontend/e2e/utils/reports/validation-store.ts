import fs from "node:fs";
import path from "node:path";
import type { PageValidationReport } from "../validation/types";

const REPORT_FILE = path.join(process.cwd(), "test-results", "validation-reports.jsonl");

function ensureDir(): void {
  fs.mkdirSync(path.dirname(REPORT_FILE), { recursive: true });
}

export function recordValidationReport(report: PageValidationReport): void {
  ensureDir();
  fs.appendFileSync(REPORT_FILE, `${JSON.stringify(report)}\n`, "utf-8");
}

export function readValidationReports(): PageValidationReport[] {
  if (!fs.existsSync(REPORT_FILE)) return [];
  const lines = fs.readFileSync(REPORT_FILE, "utf-8").trim().split("\n").filter(Boolean);
  return lines.map((line) => JSON.parse(line) as PageValidationReport);
}

export function clearValidationReports(): void {
  ensureDir();
  fs.writeFileSync(REPORT_FILE, "", "utf-8");
}

export function summarizeReports(reports: PageValidationReport[]): string {
  if (reports.length === 0) return "No validation reports recorded.";

  const lines: string[] = ["=== Enterprise Validation Summary ==="];
  for (const report of reports) {
    lines.push(`\n📄 ${report.pageName} (${report.url})`);
    lines.push(`   Errors: ${report.errorCount} | Warnings: ${report.warningCount} | Passed: ${report.passed}`);
    for (const result of report.results) {
      if (result.issues.length === 0) continue;
      lines.push(`   [${result.check}] ${result.issues.length} issue(s) (${result.durationMs}ms)`);
      for (const issue of result.issues.slice(0, 3)) {
        lines.push(`     - ${issue.message}`);
      }
      if (result.issues.length > 3) {
        lines.push(`     ... +${result.issues.length - 3} more`);
      }
    }
  }
  return lines.join("\n");
}
