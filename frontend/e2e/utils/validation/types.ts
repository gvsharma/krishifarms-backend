import type { ViewportPreset } from "../viewports";

export type ValidationCheck =
  | "console"
  | "network"
  | "layout"
  | "inputs"
  | "buttons"
  | "typography"
  | "tables"
  | "dialogs"
  | "navigation"
  | "accessibility"
  | "responsive"
  | "visual"
  | "contrast"
  | "css"
  | "performance";

export type ValidationSeverity = "error" | "warning" | "info";

export interface ValidationIssue {
  check: ValidationCheck;
  severity: ValidationSeverity;
  message: string;
  selector?: string;
  details?: Record<string, unknown>;
}

export interface ValidationResult {
  check: ValidationCheck;
  passed: boolean;
  issues: ValidationIssue[];
  durationMs: number;
}

export interface ValidateEntirePageOptions {
  /** Human-readable page name for reports and visual baselines. */
  name?: string;
  /** Checks to skip entirely. */
  skip?: ValidationCheck[];
  /** Checks that collect issues but do not fail the test. */
  softFail?: ValidationCheck[];
  /** Viewport presets for responsive validation (default: desktop only). */
  viewports?: ViewportPreset[];
  /** Run visual regression with baseline compare. */
  visualRegression?: boolean;
  /** Axe impact levels that fail the test. */
  a11yFailOn?: Array<"critical" | "serious" | "moderate" | "minor">;
  /** Max allowed performance metrics. */
  performance?: {
    maxLoadMs?: number;
    maxCls?: number;
    maxSlowApiMs?: number;
  };
  /** Wait for network idle before validating. */
  waitForNetworkIdle?: boolean;
}

export interface PageValidationReport {
  pageName: string;
  url: string;
  timestamp: string;
  results: ValidationResult[];
  passed: boolean;
  totalIssues: number;
  errorCount: number;
  warningCount: number;
}
