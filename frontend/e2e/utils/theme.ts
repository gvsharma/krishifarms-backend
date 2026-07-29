import { expect, type Page } from "@playwright/test";

/**
 * Force dark theme via next-themes (storage + html class) and MUI `.dark` selector.
 * Call before navigating, or reload after if the page is already open.
 */
export async function enableDarkTheme(page: Page): Promise<void> {
  await page.addInitScript(() => {
    try {
      localStorage.setItem("theme", "dark");
    } catch {
      /* ignore quota / private mode */
    }
    document.documentElement?.classList.add("dark");
  });
}

/** Toggle or confirm dark mode using the shell theme control (page must be authenticated). */
export async function ensureDarkThemeViaToggle(page: Page): Promise<void> {
  const alreadyDark = await page.evaluate(() => document.documentElement.classList.contains("dark"));
  if (alreadyDark) return;

  const toggle = page.getByRole("button", { name: /Toggle theme/i });
  if ((await toggle.count()) === 0) {
    await page.evaluate(() => {
      localStorage.setItem("theme", "dark");
      document.documentElement?.classList.add("dark");
    });
    await page.reload({ waitUntil: "domcontentloaded" });
    return;
  }

  await toggle.click();
  await expect
    .poll(async () => page.evaluate(() => document.documentElement.classList.contains("dark")))
    .toBe(true);
}
