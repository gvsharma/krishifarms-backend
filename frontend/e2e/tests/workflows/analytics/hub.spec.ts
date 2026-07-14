import { expect, test } from "@playwright/test";
import { ensureAuthenticated, expectNoPageErrors, trackPageErrors } from "../../../utils/common";

test.describe("workflows — analytics hub", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("hub loads modules; executive KPIs; preset; CSV export; scaffold availability", async ({
    page,
  }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/analytics");
    await expect(page.getByRole("heading", { name: /Analytics Hub/i })).toBeVisible();
    await expect(page.getByTestId("analytics-hub-grid")).toBeVisible({ timeout: 15000 });
    await expect(page.getByTestId("analytics-module-card-executive")).toBeVisible();

    await page.getByTestId("analytics-module-card-executive").click();
    await expect(page.getByTestId("analytics-shell-executive")).toBeVisible({ timeout: 20000 });
    await expect(page.getByTestId("kpi-revenue")).toBeVisible({ timeout: 20000 });
    await expect(page.getByTestId("analytics-export")).toBeVisible();

    const preset = page.getByTestId("analytics-preset");
    await preset.click();
    await page.getByRole("option", { name: /7 days|7 రోజులు/i }).click();

    await page.goto("/analytics/inventory");
    await expect(page.getByTestId("scaffold-availability")).toBeVisible({ timeout: 20000 });
    await expect(page.getByTestId("data-availability-chip").first()).toBeVisible();

    expectNoPageErrors(pageErrors);
  });
});
