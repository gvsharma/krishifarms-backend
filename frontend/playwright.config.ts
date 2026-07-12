import { defineConfig, devices } from "@playwright/test";
import path from "node:path";

/**
 * E2E against deployed CRM by default.
 * Local: PLAYWRIGHT_BASE_URL=http://localhost:3000 npm run test:e2e
 */
const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "https://krishifarms-backend.vercel.app";

export const AUTH_STORAGE_STATE = path.join(__dirname, "e2e/.auth/user.json");

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [["list"], ["html", { open: "never", outputFolder: "playwright-report" }]],
  timeout: 60_000,
  expect: { timeout: 15_000 },
  use: {
    baseURL,
    trace: "on-first-retry",
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
      name: "chromium",
      dependencies: ["setup"],
      testMatch: /.*\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        storageState: AUTH_STORAGE_STATE,
      },
    },
  ],
  outputDir: "test-results",
});
