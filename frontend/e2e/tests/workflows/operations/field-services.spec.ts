import { expect, test } from "@playwright/test";
import {
  ensureAuthenticated,
  expectLabeledFieldsNotOverlapping,
  expectListContent,
  expectNoPageErrors,
  expectShellTitle,
  trackPageErrors,
} from "./helpers";
import { contentAlerts } from "../../../utils/shell";

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

  test("detail page: view record, enter edit, cancel without save", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/field-services");
    await expectShellTitle(page, /^Field services$/i);

    const outcome = await expectListContent(page, /No records yet/i);
    if (outcome !== "table") {
      test.info().annotations.push({
        type: "note",
        description: "No field service rows — skipped detail check",
      });
      expectNoPageErrors(pageErrors);
      return;
    }

    const firstRow = page.getByRole("row").nth(1);
    await firstRow.click();

    const editBtn = page.getByRole("button", { name: /^Edit$/i });
    if ((await editBtn.count()) === 0) {
      await expect(
        page.getByRole("button", { name: /Back to list/i }).or(contentAlerts(page)),
      ).toBeVisible();
      expectNoPageErrors(pageErrors);
      return;
    }

    await editBtn.click();
    await expect(page.getByRole("button", { name: /Save changes/i })).toBeVisible();

    const cancelBtn = page.getByRole("button", { name: /Cancel/i });
    if ((await cancelBtn.count()) > 0) {
      await cancelBtn.first().click();
    }

    expectNoPageErrors(pageErrors);
  });
});
