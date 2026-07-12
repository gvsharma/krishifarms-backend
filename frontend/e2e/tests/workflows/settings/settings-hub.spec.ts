import { expect, test } from "@playwright/test";
import {
  ensureAuthenticated,
  expectNoPageErrors,
  expectSettingsShell,
  trackPageErrors,
} from "./helpers";

test.describe("Settings — hub", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("/settings loads with nav cards", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/settings");
    await expectSettingsShell(page, "Settings");

    // Card links (avoid sidebar duplicates for Master data / Villages)
    await expect(page.getByRole("link", { name: /Users & roles/i })).toBeVisible();
    await expect(
      page.getByRole("link", { name: /Villages.*Geography master/i }),
    ).toBeVisible();
    await expect(
      page.getByRole("link", { name: /Master data.*Crops, buyers/i }),
    ).toBeVisible();

    expectNoPageErrors(pageErrors);
  });

  test("/settings/master-data lists catalog links", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/settings/master-data");
    await expectSettingsShell(page, "Master data");

    for (const name of [
      /Crop types/i,
      /Crop price rules/i,
      /Buyers/i,
      /Field agents/i,
      /Vehicle types/i,
      /Activity types/i,
      /Expense categories/i,
      /Payment modes/i,
      /Villages/i,
    ]) {
      await expect(page.getByRole("link", { name })).toBeVisible();
    }

    expectNoPageErrors(pageErrors);
  });
});
