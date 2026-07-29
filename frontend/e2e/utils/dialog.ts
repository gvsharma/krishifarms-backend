import { expect, type Locator, type Page } from "@playwright/test";
import { heavyOverlap } from "./overlap";
import { dialogFieldRoles } from "./selectors";

const MIN_DIALOG_TEXT_CONTRAST = 4.5;

/**
 * Resolve a MUI / premium dialog field by accessible name.
 * Prefer role locators: getByLabel(exact) misses required asterisk / floating-label quirks.
 * Short labels like "Name" also match via /^Name$/ so we don't grab unrelated text nodes.
 */
export function dialogField(dialog: Locator, label: string): Locator {
  const exact = { name: label, exact: true as const };
  const nameRe = new RegExp(`^${label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}$`, "i");
  let locator = dialog.getByRole("textbox", { name: nameRe });
  for (const role of dialogFieldRoles()) {
    locator = locator.or(dialog.getByRole(role, exact));
  }
  locator = locator.or(dialog.getByLabel(label, { exact: true }));
  locator = locator.or(dialog.getByLabel(new RegExp(`^${label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}`, "i")));
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
    const muiLabel = dialog.locator(".MuiInputLabel-root").filter({ hasText: label });
    const plainLabel = dialog.getByText(label, { exact: true });
    await expect(
      muiLabel.or(plainLabel).first(),
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

/** Resolve a labeled control on the page (MUI TextField / premium Field quirks). */
export function pageField(page: Page, label: string): Locator {
  const exact = { name: label, exact: true as const };
  let locator = page.getByLabel(label, { exact: true });
  for (const role of dialogFieldRoles()) {
    locator = locator.or(page.getByRole(role, exact));
  }
  return locator.first();
}

/** Assert labeled form controls on the page are visible and not heavily stacked. */
export async function expectLabeledFieldsNotOverlapping(
  page: Page,
  labels: string[],
): Promise<void> {
  const boxes: NonNullable<Awaited<ReturnType<Locator["boundingBox"]>>>[] = [];

  for (const label of labels) {
    const field = pageField(page, label);
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
  await expect(dialog.getByRole("heading").first()).toBeVisible();
  await expect(dialog.getByRole("textbox").first()).toBeVisible({ timeout: 15_000 });
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

/**
 * Assert dialog title / labels / filled inputs have WCAG AA contrast against their
 * effective background (catches white-on-light premium dialog regressions in dark mode).
 */
export async function expectDialogTextContrast(
  dialog: Locator,
  minRatio = MIN_DIALOG_TEXT_CONTRAST,
): Promise<void> {
  const failures = await dialog.evaluate(
    (root, minAA) => {
      function parseColor(color: string): [number, number, number] | null {
        const canvas = document.createElement("canvas");
        canvas.width = canvas.height = 1;
        const ctx = canvas.getContext("2d");
        if (!ctx) return null;
        ctx.fillStyle = color;
        ctx.fillRect(0, 0, 1, 1);
        const data = ctx.getImageData(0, 0, 1, 1).data;
        return [data[0], data[1], data[2]];
      }

      function relativeLuminance(rgb: [number, number, number]): number {
        const [r, g, b] = rgb.map((c) => {
          const s = c / 255;
          return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
        });
        return 0.2126 * r + 0.7152 * g + 0.0722 * b;
      }

      function contrastRatio(fg: string, bg: string): number {
        const fgRgb = parseColor(fg);
        const bgRgb = parseColor(bg);
        if (!fgRgb || !bgRgb) return 0;
        const l1 = relativeLuminance(fgRgb);
        const l2 = relativeLuminance(bgRgb);
        const lighter = Math.max(l1, l2);
        const darker = Math.min(l1, l2);
        return (lighter + 0.05) / (darker + 0.05);
      }

      function getEffectiveBackground(el: Element): string {
        let current: Element | null = el;
        while (current && current !== root.parentElement) {
          const bg = window.getComputedStyle(current).backgroundColor;
          if (bg && bg !== "rgba(0, 0, 0, 0)" && bg !== "transparent") return bg;
          current = current.parentElement;
        }
        return window.getComputedStyle(root).backgroundColor || "rgb(255, 255, 255)";
      }

      const targets = [
        ...root.querySelectorAll(
          "h1, h2, h3, h4, h5, h6, .MuiDialogTitle-root, .MuiInputLabel-root, .MuiFormLabel-root, .MuiInputBase-input, .MuiFormHelperText-root, .MuiFormControlLabel-label, label",
        ),
      ];

      const bad: Array<{ text: string; fg: string; bg: string; ratio: number }> = [];
      for (const el of targets) {
        const style = window.getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        if (rect.width === 0 || rect.height === 0) continue;
        if (style.visibility === "hidden" || style.opacity === "0") continue;

        const fg = style.color;
        const bg = getEffectiveBackground(el);
        const ratio = contrastRatio(fg, bg);
        if (ratio < minAA) {
          const text =
            (el as HTMLInputElement).value ||
            el.textContent?.trim() ||
            el.getAttribute("aria-label") ||
            el.tagName;
          bad.push({
            text: String(text).slice(0, 48),
            fg,
            bg,
            ratio: Math.round(ratio * 100) / 100,
          });
        }
      }
      return bad;
    },
    minRatio,
  );

  expect(
    failures,
    failures.length
      ? `Dialog text contrast failures:\n${failures
          .map((f) => `  "${f.text}" ${f.ratio}:1 (fg=${f.fg}, bg=${f.bg})`)
          .join("\n")}`
      : "Dialog text contrast OK",
  ).toEqual([]);
}

