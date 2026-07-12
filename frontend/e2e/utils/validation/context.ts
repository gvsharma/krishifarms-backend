import type { Page, Request, Response } from "@playwright/test";
import type { ValidationIssue } from "./types";

/** Per-test collectors for console and network validation. */
export class ValidationContext {
  readonly consoleErrors: string[] = [];
  readonly consoleWarnings: string[] = [];
  readonly unhandledRejections: string[] = [];
  readonly failedRequests: Array<{
    url: string;
    method: string;
    status?: number;
    failure?: string;
  }> = [];
  readonly slowRequests: Array<{ url: string; durationMs: number }> = [];

  private disposed = false;

  constructor(private readonly page: Page) {
    page.on("pageerror", (err) => {
      this.consoleErrors.push(err.message);
    });
    page.on("console", (msg) => {
      const text = msg.text();
      if (msg.type() === "error") {
        this.consoleErrors.push(text);
      } else if (msg.type() === "warning") {
        this.consoleWarnings.push(text);
      }
    });
    page.on("requestfailed", (request) => {
      const failure = request.failure()?.errorText ?? "";
      const url = request.url();
      // Next.js RSC prefetch / navigation aborts are expected
      if (failure.includes("ERR_ABORTED")) return;
      if (url.includes("_rsc=")) return;
      this.failedRequests.push({
        url,
        method: request.method(),
        failure,
      });
    });
    page.on("response", (response) => {
      this.trackResponse(response);
    });
  }

  private trackResponse(response: Response): void {
    const request = response.request();
    const timing = request.timing();
    const durationMs = timing.responseEnd > 0 ? timing.responseEnd : 0;
    if (durationMs > 3000) {
      this.slowRequests.push({ url: request.url(), durationMs });
    }
    const status = response.status();
    const url = response.url();
    if (status >= 400 && !this.isIgnorableFailedRequest(url, status)) {
      this.failedRequests.push({
        url,
        method: request.method(),
        status,
      });
    }
  }

  private isIgnorableFailedRequest(url: string, status: number): boolean {
    if (url.includes("favicon.ico")) return true;
    if (status === 401 && url.includes("/auth/")) return true;
    return false;
  }

  issuesForConsole(): ValidationIssue[] {
    const issues: ValidationIssue[] = [];
    for (const msg of this.consoleErrors) {
      issues.push({
        check: "console",
        severity: "error",
        message: `Console/page error: ${msg}`,
      });
    }
    for (const msg of this.unhandledRejections) {
      issues.push({
        check: "console",
        severity: "error",
        message: `Unhandled rejection: ${msg}`,
      });
    }
    return issues;
  }

  issuesForNetwork(): ValidationIssue[] {
    return this.failedRequests.map((req) => ({
      check: "network",
      severity: "error",
      message: `Failed request: ${req.method} ${req.url} (${req.status ?? req.failure ?? "unknown"})`,
      details: req as Record<string, unknown>,
    }));
  }

  dispose(): void {
    this.disposed = true;
  }

  get isDisposed(): boolean {
    return this.disposed;
  }
}

const contextMap = new WeakMap<Page, ValidationContext>();

export function getValidationContext(page: Page): ValidationContext {
  let ctx = contextMap.get(page);
  if (!ctx) {
    ctx = new ValidationContext(page);
    contextMap.set(page, ctx);
  }
  return ctx;
}
