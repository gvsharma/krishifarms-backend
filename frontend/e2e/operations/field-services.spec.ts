import { expect, test } from "@playwright/test";
import {
  ensureAuthenticated,
  expectLabeledFieldsNotOverlapping,
  expectListContent,
  expectNoPageErrors,
  expectShellTitle,
  trackPageErrors,
} from "./helpers";

test.describe("operations — field services", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("list loads with category filter / table / empty / alert and no pageerror", async ({
    page,
  }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/field-services");
    await expectShellTitle(page, /^Field services$/i);
    await expect(page.getByLabel(/^Category$/i)).toBeVisible();
    await expect(page.getByRole("link", { name: /New service/i })).toBeVisible();

    await expectListContent(page, /No records yet/i);
    expectNoPageErrors(pageErrors);
  });

  test("new form: category select + fields visible without overlap", async ({
    page,
  }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/field-services/new");
    await expectShellTitle(page, /^New field service$/i);

    const category = page.getByLabel(/Service category/i);
    await expect(category).toBeVisible();

    await category.click();
    await page.getByRole("option", { name: /^Tractor work$/i }).click();

    await expect(page.getByLabel("Service date")).toBeVisible({ timeout: 10_000 });

    await expectLabeledFieldsNotOverlapping(page, [
      "Service date",
      "Status",
      "Hours",
      "Total (₹)",
      "Pending (₹)",
      "Comments",
    ]);

    await expect(
      page.getByRole("button", { name: /Create service record/i }),
    ).toBeVisible();

    expectNoPageErrors(pageErrors);
  });
});
