import { expect, test } from "@playwright/test";
import {
  ensureAuthenticated,
  expectListContent,
  expectNoPageErrors,
  expectShellTitle,
  trackPageErrors,
} from "./helpers";

test.describe("operations — farmers", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("list loads with search / table / empty / alert and no pageerror", async ({
    page,
  }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/farmers");
    await expectShellTitle(page, /^Farmers$/i);
    await expect(
      page.getByText(/Farmer registry with village assignments/i),
    ).toBeVisible();

    await expect(page.getByPlaceholder(/Search name, phone, or code/i)).toBeVisible();
    await expect(page.getByRole("button", { name: /^Search$/i })).toBeVisible();

    await expectListContent(page, /No farmers found/i);
    expectNoPageErrors(pageErrors);
  });

  test("create form fields visible at /farmers/new", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/farmers/new");
    await expectShellTitle(page, /^Add farmer$/i);

    const fullName = page.getByLabel("Full name", { exact: true });
    const alert = page.getByRole("alert");

    await expect(fullName.or(alert).first()).toBeVisible({ timeout: 20_000 });

    if (await fullName.isVisible().catch(() => false)) {
      await expect(page.getByLabel("Full name (Telugu)")).toBeVisible();
      await expect(page.getByLabel("Primary phone")).toBeVisible();
      await expect(page.getByLabel("Village")).toBeVisible();
      await expect(page.getByLabel("Notes")).toBeVisible();
      await expect(page.getByRole("button", { name: /Create farmer/i })).toBeVisible();
    }

    expectNoPageErrors(pageErrors);
  });
});
