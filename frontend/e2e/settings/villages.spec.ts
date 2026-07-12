import { expect, test } from "@playwright/test";
import {
  ensureAuthenticated,
  expectDialogLabelsNotOverlapping,
  expectNoPageErrors,
  expectSettingsShell,
  expectTableOrAlert,
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
      "Mandal",
      "District",
      "State",
      "Pincode",
    ]);

    await dialog.getByRole("button", { name: /Cancel/i }).click();
    expectNoPageErrors(pageErrors);
  });
});
