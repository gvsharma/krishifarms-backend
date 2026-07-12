import { test as base, type Page } from "@playwright/test";
import { DashboardPage, LoginPage } from "../pages";
import { testData, type TestData } from "../test-data";
import { ensureAuthenticated } from "../utils/auth-helpers";
import { trackPageErrors } from "../utils/page-errors";
import { viewportPreset, type ViewportPreset } from "../utils/viewports";

export type E2EFixtures = {
  /** Pre-authenticated page (storageState or UI fallback). */
  authedPage: Page;
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
  testData: TestData;
  /** Uncaught JS error collector — assert empty at end of test. */
  pageErrors: string[];
  /** Apply a named viewport preset for responsive tests. */
  viewportPreset: (name: ViewportPreset) => Promise<void>;
};

export const test = base.extend<E2EFixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },

  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },

  testData: async ({}, use) => {
    await use(testData);
  },

  pageErrors: async ({ page }, use) => {
    const errors = trackPageErrors(page);
    await use(errors);
  },

  authedPage: async ({ page }, use) => {
    await ensureAuthenticated(page);
    await use(page);
  },

  viewportPreset: async ({ page }, use) => {
    await use(async (name: ViewportPreset) => {
      const size = viewportPreset(name);
      await page.setViewportSize(size);
    });
  },
});

export { expect } from "@playwright/test";
