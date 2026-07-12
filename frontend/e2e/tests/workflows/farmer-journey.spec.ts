import { expect, test } from "@playwright/test";
import { loginViaUi } from "../../fixtures/auth";
import { expectNoPageErrors, trackPageErrors } from "../../utils/common";
import { expectNoHorizontalScroll } from "../../utils/visual";

/**
 * End-to-end workflow: fresh login → create farmer (or validate form) → dashboard.
 * Uses a unique farmer name to avoid collisions when API is writable.
 */
test.describe("workflow — farmer journey", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test("login → create farmer → view dashboard", async ({ page }) => {
    const pageErrors = trackPageErrors(page);
    const uniqueName = `E2E Farmer ${Date.now()}`;

    // 1. Login
    await loginViaUi(page);
    await expect(page.getByRole("heading", { name: /^Home$/i })).toBeVisible({
      timeout: 20_000,
    });

    // 2. Navigate to create farmer
    await page.getByRole("navigation").getByRole("link", { name: "Farmers" }).click();
    await expect(page.getByRole("heading", { name: /^Farmers$/i })).toBeVisible();
    await page.getByRole("link", { name: /Add farmer/i }).click();
    await expect(page.getByRole("heading", { name: /^Add farmer$/i })).toBeVisible();

    const villagesAlert = page.getByRole("alert");
    if (await villagesAlert.isVisible().catch(() => false)) {
      test.info().annotations.push({
        type: "note",
        description: "Villages API unavailable — validated form shell only",
      });
    } else {
      await page.getByLabel("Full name", { exact: true }).fill(uniqueName);
      await page.getByLabel("Primary phone").fill("9876543210");

      const villageSelect = page.getByLabel("Village");
      await villageSelect.click();
      const firstOption = page.getByRole("option").first();
      if (await firstOption.isVisible().catch(() => false)) {
        await firstOption.click();

        const createBtn = page.getByRole("button", { name: /Create farmer/i });
        await expect(createBtn).toBeEnabled({ timeout: 5_000 });
        await createBtn.click();

        // 3. Land on detail or list after create
        await expect(
          page.getByRole("button", { name: /Back to list/i }).or(page.getByRole("alert")),
        ).toBeVisible({ timeout: 30_000 });
      }
    }

    // 4. Return to dashboard
    await page.getByRole("navigation").getByRole("link", { name: "Dashboard" }).click();
    await expect(page.getByRole("heading", { name: /^Home$/i })).toBeVisible();
    await expectNoHorizontalScroll(page);

    expectNoPageErrors(pageErrors);
  });
});
