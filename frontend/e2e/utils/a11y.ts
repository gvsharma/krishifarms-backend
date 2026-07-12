import { expect, type Page } from "@playwright/test";

/**
 * Assert the page has a single logical main landmark (MUI shell or role=main).
 */
export async function expectMainLandmark(page: Page): Promise<void> {
  const main = page.getByRole("main");
  await expect(main).toBeVisible({ timeout: 15_000 });
  expect(await main.count()).toBeGreaterThanOrEqual(1);
}

/**
 * Tab through focusable elements and collect focus targets.
 * Returns ordered list of accessible names / tag names for the focused element.
 */
export async function collectTabOrder(page: Page, maxTabs = 12): Promise<string[]> {
  const order: string[] = [];

  for (let i = 0; i < maxTabs; i++) {
    await page.keyboard.press("Tab");
    const descriptor = await page.evaluate(() => {
      const el = document.activeElement;
      if (!el || el === document.body) return null;
      const name =
        el.getAttribute("aria-label") ||
        (el as HTMLElement).innerText?.trim().slice(0, 40) ||
        el.getAttribute("placeholder") ||
        el.getAttribute("name") ||
        el.tagName.toLowerCase();
      return name;
    });
    if (descriptor) order.push(descriptor);
  }

  return order;
}

/**
 * Assert key interactive controls expose accessible names.
 */
export async function expectNamedControls(
  page: Page,
  roles: Array<"button" | "link" | "textbox" | "combobox">,
  minCount = 1,
): Promise<void> {
  for (const role of roles) {
    const controls = page.getByRole(role);
    const count = await controls.count();
    expect(count, `Expected at least ${minCount} ${role} controls`).toBeGreaterThanOrEqual(
      minCount,
    );

    const named = await controls.evaluateAll((els) =>
      els.filter((el) => {
        const name =
          el.getAttribute("aria-label") ||
          el.textContent?.trim() ||
          el.getAttribute("placeholder") ||
          el.getAttribute("name");
        return Boolean(name);
      }).length,
    );

    expect(named, `${role} controls should have accessible names`).toBeGreaterThanOrEqual(
      Math.min(minCount, count),
    );
  }
}
