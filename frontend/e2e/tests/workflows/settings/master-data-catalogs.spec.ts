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

type CatalogSmoke = {
  path: string;
  title: string;
  addHeading: RegExp;
  /** Labels that must be visible and non-overlapping in the Add dialog. */
  labels: string[];
};

const CATALOGS: CatalogSmoke[] = [
  {
    path: "/settings/master-data/crops",
    title: "Crop types",
    addHeading: /Add Crop type/i,
    labels: ["Name", "Code", "Default moisture %"],
  },
  {
    path: "/settings/master-data/crop-prices",
    title: "Crop price rules",
    addHeading: /Add Crop price rule/i,
    labels: ["Crop type", "Effective from", "Rate / quintal (₹)"],
  },
  {
    path: "/settings/master-data/buyers",
    title: "Buyers",
    addHeading: /Add Buyer/i,
    labels: [
      "Name",
      "Name (Telugu)",
      "Phone",
      "GSTIN",
      "Contact person",
      "Address",
      "Notes",
    ],
  },
  {
    path: "/settings/master-data/agents",
    title: "Field agents",
    addHeading: /Add Field agent/i,
    labels: ["Name", "Name (Telugu)", "Phone", "Commission %", "Notes"],
  },
  {
    path: "/settings/master-data/vehicle-types",
    title: "Vehicle types",
    addHeading: /Add Vehicle type/i,
    labels: ["Name", "Code", "Name (Telugu)", "Capacity (qtl)", "Fuel type", "Notes"],
  },
  {
    path: "/settings/master-data/activity-types",
    title: "Activity types",
    addHeading: /Add Activity type/i,
    labels: ["Name", "Code", "Name (Telugu)", "Default rate type"],
  },
  {
    path: "/settings/master-data/expense-categories",
    title: "Expense categories",
    addHeading: /Add Expense categor/i,
    labels: ["Name", "Type"],
  },
  {
    path: "/settings/master-data/payment-modes",
    title: "Payment modes",
    addHeading: /Add Payment mode/i,
    labels: ["Name", "Code", "Name (Telugu)"],
  },
];

test.describe("Settings — master-data catalogs", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  for (const catalog of CATALOGS) {
    test(`${catalog.title} list loads`, async ({ page }) => {
      const pageErrors = trackPageErrors(page);

      await page.goto(catalog.path);
      await expectSettingsShell(page, catalog.title);
      await expectTableOrAlert(page);

      expectNoPageErrors(pageErrors);
    });

    test(`${catalog.title} Add dialog labels visible and not overlapping`, async ({
      page,
    }) => {
      const pageErrors = trackPageErrors(page);

      await page.goto(catalog.path);
      await expectSettingsShell(page, catalog.title);

      const dialog = await openCatalogAddDialog(page);
      await expect(dialog.getByRole("heading", { name: catalog.addHeading })).toBeVisible();

      await expectDialogLabelsNotOverlapping(dialog, catalog.labels);

      // Active switch present on most catalogs
      const active = dialog.getByLabel("Active", { exact: true });
      if ((await active.count()) > 0) {
        await expect(active.first()).toBeVisible();
      }

      await dialog.getByRole("button", { name: /Cancel/i }).click();
      expectNoPageErrors(pageErrors);
    });
  }

  test("Buyers Edit dialog fields not overlapping when a row exists", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/settings/master-data/buyers");
    await expectSettingsShell(page, "Buyers");

    const outcome = await expectTableOrAlert(page);
    if (outcome === "alert") {
      test.info().annotations.push({
        type: "note",
        description: "Buyers list API error — skipped Edit dialog check",
      });
      expectNoPageErrors(pageErrors);
      return;
    }

    const editBtn = page.getByRole("button", { name: /^Edit$/i }).first();
    if ((await editBtn.count()) === 0) {
      test.info().annotations.push({
        type: "note",
        description: "No buyer rows to edit",
      });
      expectNoPageErrors(pageErrors);
      return;
    }

    await editBtn.click();
    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();
    await expect(dialog.getByRole("heading", { name: /Edit Buyer/i })).toBeVisible();

    await expectDialogLabelsNotOverlapping(dialog, [
      "Name",
      "Name (Telugu)",
      "Phone",
      "GSTIN",
      "Contact person",
      "Address",
      "Notes",
    ]);

    await dialog.getByRole("button", { name: /Cancel/i }).click();
    expectNoPageErrors(pageErrors);
  });
});
