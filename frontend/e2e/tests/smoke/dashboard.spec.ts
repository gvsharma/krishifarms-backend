import { test, expect } from "@playwright/test";
import { ensureAuthenticated, expectNoPageErrors, trackPageErrors } from "../../utils/common";
import { expectPageVisualHealth } from "../../utils/visual";

test.describe("smoke — dashboard", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("loads shell after auth without page errors", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/dashboard");

    await expectPageVisualHealth(page, /^Home$/i);
    await expect(page.getByText(/Farm operations overview/i).first()).toBeVisible();

    expectNoPageErrors(pageErrors);
  });
});
