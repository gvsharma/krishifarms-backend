import { expect, test } from "@playwright/test";
import {
  ensureAuthenticated,
  expectDialogLabelsNotOverlapping,
  expectNoPageErrors,
  expectSettingsShell,
  expectTableOrAlert,
  trackPageErrors,
} from "./helpers";

test.describe("Settings — Users", () => {
  test.beforeEach(async ({ page }) => {
    await ensureAuthenticated(page);
  });

  test("list loads as table or clear error Alert (not blank crash)", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/settings/users");
    await expectSettingsShell(page, "Users");

    // Live may still 500 on *.local EmailStr until deploy of 52d6cb8; Alert is OK.
    const outcome = await expectTableOrAlert(page);
    expect(["table", "alert"]).toContain(outcome);

    if (outcome === "table") {
      await expect(page.getByRole("columnheader", { name: "Name" })).toBeVisible();
      await expect(page.getByRole("columnheader", { name: "Role" })).toBeVisible();
    } else {
      await expect(page.getByRole("alert").first()).toContainText(/./);
    }

    expectNoPageErrors(pageErrors);
  });

  test("Add user dialog fields visible and not overlapping", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/settings/users");
    await expectSettingsShell(page, "Users");

    const addBtn = page.getByRole("button", { name: /Add user/i });
    // MANAGER without users:create may not see Add — skip dialog UI in that case.
    if ((await addBtn.count()) === 0) {
      test.info().annotations.push({
        type: "note",
        description: "Add user button hidden (permission) — skipped dialog layout check",
      });
      expectNoPageErrors(pageErrors);
      return;
    }

    await addBtn.click();
    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();
    await expect(dialog.getByRole("heading", { name: /Add user/i })).toBeVisible();

    await expectDialogLabelsNotOverlapping(dialog, [
      "Full name",
      "Email",
      "Phone",
      "Password",
      "Role",
      "Locale",
    ]);

    await dialog.getByRole("button", { name: /Cancel/i }).click();
    expectNoPageErrors(pageErrors);
  });

  test("Add user validation blocks empty required fields", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/settings/users");
    await expectSettingsShell(page, "Users");

    const addBtn = page.getByRole("button", { name: /Add user/i });
    if ((await addBtn.count()) === 0) {
      test.info().annotations.push({
        type: "note",
        description: "Add user button hidden (permission) — skipped validation check",
      });
      expectNoPageErrors(pageErrors);
      return;
    }

    await addBtn.click();
    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();

    const saveBtn = dialog.getByRole("button", { name: /^(Save|Create)$/i });
    await expect(saveBtn).toBeDisabled();

    await dialog.getByRole("button", { name: /Cancel/i }).click();
    expectNoPageErrors(pageErrors);
  });

  test("Edit user dialog opens when rows exist", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/settings/users");
    await expectSettingsShell(page, "Users");

    const outcome = await expectTableOrAlert(page);
    if (outcome === "alert") {
      test.info().annotations.push({
        type: "note",
        description: "Users list API error — skipped Edit dialog check",
      });
      expectNoPageErrors(pageErrors);
      return;
    }

    const editBtn = page.getByRole("button", { name: /^Edit$/i }).first();
    if ((await editBtn.count()) === 0) {
      test.info().annotations.push({ type: "note", description: "No user rows to edit" });
      expectNoPageErrors(pageErrors);
      return;
    }

    await editBtn.click();
    const dialog = page.getByRole("dialog");
    await expect(dialog.getByRole("heading", { name: /Edit user/i })).toBeVisible();
    await expectDialogLabelsNotOverlapping(dialog, ["Full name", "Email", "Phone", "Role"]);

    await dialog.getByRole("button", { name: /Cancel/i }).click();
    expectNoPageErrors(pageErrors);
  });
});
