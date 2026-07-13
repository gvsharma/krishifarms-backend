import { defineConfig, devices } from "@playwright/test";
import path from "node:path";

/**
 * Enterprise E2E framework for KrishiFarms CRM.
 * Local: PLAYWRIGHT_BASE_URL=http://localhost:3000 npm run test:e2e
 */
const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "https://krishifarms-backend.vercel.app";

export const AUTH_STORAGE_STATE = path.join(__dirname, "e2e/.auth/user.json");

const testMatch = [
  /tests\/.*\.spec\.ts/,
  /smoke\/.*\.spec\.ts/,
  /settings\/.*\.spec\.ts/,
  /operations\/.*\.spec\.ts/,
  /finance\/.*\.spec\.ts/,
];

export default defineConfig({
  testDir: "./e2e",
  testMatch,
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: [
    ["list"],
    ["html", { open: "never", outputFolder: "playwright-report" }],
    [path.join(__dirname, "e2e/utils/reports/enterprise-reporter.ts")],
  ],
  timeout: 90_000,
  expect: {
    timeout: 15_000,
    toHaveScreenshot: {
      maxDiffPixels: 100,
      animations: "disabled",
    },
  },
  snapshotPathTemplate: "{testDir}/baselines/{projectName}/{testFilePath}/{arg}{ext}",
  use: {
    baseURL,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    actionTimeout: 15_000,
    navigationTimeout: 45_000,
  },
  projects: [
    {
      name: "setup",
      testMatch: /auth\.setup\.ts/,
    },
    {
      // Unauthenticated session-expiry specs — must not depend on auth.setup.
      name: "smoke-session",
      testMatch: /tests\/smoke\/session-expiry\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        storageState: { cookies: [], origins: [] },
      },
    },
    {
      name: "smoke-chromium",
      dependencies: ["setup"],
      testMatch: /tests\/smoke\/(?!session-expiry).*\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        storageState: AUTH_STORAGE_STATE,
      },
    },
    {
      name: "regression",
      dependencies: ["setup"],
      testMatch: /tests\/regression\/.*\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        storageState: AUTH_STORAGE_STATE,
      },
    },
    {
      name: "visual",
      dependencies: ["setup"],
      testMatch: /tests\/visual\/.*\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        storageState: AUTH_STORAGE_STATE,
      },
    },
    {
      name: "responsive",
      dependencies: ["setup"],
      testMatch: /tests\/responsive\/.*\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        storageState: AUTH_STORAGE_STATE,
      },
    },
    {
      name: "mobile-chrome",
      dependencies: ["setup"],
      testMatch: /tests\/responsive\/.*\.spec\.ts/,
      use: {
        ...devices["Pixel 5"],
        storageState: AUTH_STORAGE_STATE,
      },
    },
    {
      name: "workflow",
      dependencies: ["setup"],
      testMatch: /tests\/workflows\/.*\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        storageState: AUTH_STORAGE_STATE,
      },
    },
    {
      name: "chromium",
      dependencies: ["setup"],
      testIgnore: [/auth\.setup\.ts/],
      use: {
        ...devices["Desktop Chrome"],
        storageState: AUTH_STORAGE_STATE,
      },
    },
    {
      name: "firefox",
      dependencies: ["setup"],
      testIgnore: [/auth\.setup\.ts/],
      use: {
        ...devices["Desktop Firefox"],
        storageState: AUTH_STORAGE_STATE,
      },
    },
    {
      name: "webkit",
      dependencies: ["setup"],
      testIgnore: [/auth\.setup\.ts/],
      use: {
        ...devices["Desktop Safari"],
        storageState: AUTH_STORAGE_STATE,
      },
    },
  ],
  outputDir: "test-results",
});
