import { expect, test } from "@playwright/test";
import {
  ensureAuthenticated,
  expectDialogLabelsNotOverlapping,
  expectNoPageErrors,
  expectSettingsShell,
  expectTableOrAlert,
  dialogField,
  openCatalogAddDialog,
  trackPageErrors,
} from "./helpers";

test.describe("Settings — Villages", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("list loads with table or Alert", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/settings/villages");
    await expectSettingsShell(page, "Villages");
    await expectTableOrAlert(page);

    expectNoPageErrors(pageErrors);
  });

  test("Add village dialog fields not overlapping", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/settings/villages");
    await expectSettingsShell(page, "Villages");

    const dialog = await openCatalogAddDialog(page);
    await expect(dialog.getByRole("heading", { name: /Add Village/i })).toBeVisible();

    await expectDialogLabelsNotOverlapping(dialog, [
      "Name",
      "District",
      "Mandal",
      "State",
      "Pincode",
    ]);

    await dialog.getByRole("button", { name: /Cancel/i }).click();
    expectNoPageErrors(pageErrors);
  });

  test("Add village validation blocks empty required fields", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/settings/villages");
    await expectSettingsShell(page, "Villages");

    const dialog = await openCatalogAddDialog(page);
    const saveBtn = dialog.getByRole("button", { name: /^Save$/i });
    await expect(saveBtn).toBeDisabled();

    await dialog.getByRole("button", { name: /Cancel/i }).click();
    expectNoPageErrors(pageErrors);
  });

  test("Add village cancel closes dialog without saving", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/settings/villages");
    await expectSettingsShell(page, "Villages");

    const dialog = await openCatalogAddDialog(page);
    await dialogField(dialog, "Name").fill("E2E Test Village");
    await dialog.getByRole("button", { name: /Cancel/i }).click();
    await expect(dialog).toHaveCount(0);

    expectNoPageErrors(pageErrors);
  });
});
