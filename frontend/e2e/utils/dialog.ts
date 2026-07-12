import { expect, type Locator, type Page } from "@playwright/test";
import { heavyOverlap } from "./overlap";
import { dialogFieldRoles } from "./selectors";

/**
 * Resolve a MUI dialog field by accessible name.
 * Prefer role locators: getByLabel(exact) misses required asterisk / floating-label quirks.
 */
export function dialogField(dialog: Locator, label: string): Locator {
  const exact = { name: label, exact: true as const };
  let locator = dialog.getByLabel(label, { exact: true });
  for (const role of dialogFieldRoles()) {
    locator = locator.or(dialog.getByRole(role, exact));
  }
  return locator.first();
}

/**
 * Assert labeled controls inside a dialog are visible and do not heavily overlap.
 */
export async function expectDialogLabelsNotOverlapping(
  dialog: Locator,
  labels: string[],
): Promise<void> {
  const boxes: { label: string; box: NonNullable<Awaited<ReturnType<Locator["boundingBox"]>>> }[] =
    [];

  for (const label of labels) {
    const control = dialogField(dialog, label);
    await expect(control, `Field "${label}" should be visible`).toBeVisible({ timeout: 15_000 });
    await expect(
      dialog.getByText(label, { exact: true }).first(),
      `Label text "${label}" should be visible`,
    ).toBeVisible();
    const box = await control.boundingBox();
    expect(box, `Field "${label}" should have a layout box`).not.toBeNull();
    if (box) {
      expect(box.height, `Field "${label}" should have non-collapsed height`).toBeGreaterThan(8);
      boxes.push({ label, box });
    }
  }

  for (let i = 0; i < boxes.length; i++) {
    for (let j = i + 1; j < boxes.length; j++) {
      expect(
        heavyOverlap(boxes[i].box, boxes[j].box),
        `Fields "${boxes[i].label}" and "${boxes[j].label}" heavily overlap`,
      ).toBe(false);
    }
  }
}

/** Assert labeled form controls on the page are visible and not heavily stacked. */
export async function expectLabeledFieldsNotOverlapping(
  page: Page,
  labels: string[],
): Promise<void> {
  const boxes: NonNullable<Awaited<ReturnType<Locator["boundingBox"]>>>[] = [];

  for (const label of labels) {
    const field = page.getByLabel(label, { exact: true }).first();
    await expect(field, `Field "${label}" should be visible`).toBeVisible({ timeout: 15_000 });
    const box = await field.boundingBox();
    expect(box, `Field "${label}" should have a layout box`).not.toBeNull();
    if (box) boxes.push(box);
  }

  for (let i = 0; i < boxes.length; i++) {
    for (let j = i + 1; j < boxes.length; j++) {
      expect(
        heavyOverlap(boxes[i], boxes[j], 0.4),
        `Fields "${labels[i]}" and "${labels[j]}" overlap too much`,
      ).toBe(false);
    }
  }
}

/** Open Add dialog on a CatalogAdminPage and assert key fields. */
export async function openCatalogAddDialog(page: Page): Promise<Locator> {
  await page.getByRole("button", { name: /^Add$/i }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();
  return dialog;
}

/** Open a create dialog/button if present and assert labeled fields do not heavily overlap. */
export async function assertCreateDialogFieldsNotOverlapping(
  page: Page,
  openButtonName: RegExp,
): Promise<boolean> {
  const openBtn = page.getByRole("button", { name: openButtonName });
  if ((await openBtn.count()) === 0) {
    return false;
  }

  await openBtn.first().click();
  const dialog = page.getByRole("dialog");
  await expect(dialog).toBeVisible();

  const fields = dialog.locator(
    'input:not([type="hidden"]), textarea, [role="combobox"], .MuiInputBase-root',
  );
  const count = await fields.count();
  if (count < 2) {
    await expect(dialog.locator("label, .MuiFormLabel-root").first()).toBeVisible();
    return true;
  }

  const boxes: NonNullable<Awaited<ReturnType<Locator["boundingBox"]>>>[] = [];
  for (let i = 0; i < Math.min(count, 8); i++) {
    const field = fields.nth(i);
    if (!(await field.isVisible())) continue;
    const box = await field.boundingBox();
    if (box && box.width > 0 && box.height > 0) {
      boxes.push(box);
    }
  }

  for (let i = 0; i < boxes.length; i++) {
    for (let j = i + 1; j < boxes.length; j++) {
      expect(
        heavyOverlap(boxes[i], boxes[j], 0.4),
        `Form fields ${i} and ${j} overlap too much`,
      ).toBe(false);
    }
  }

  return true;
}
