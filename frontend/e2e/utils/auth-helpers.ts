import fs from "node:fs";
import type { Page } from "@playwright/test";
import { AUTH_STORAGE_STATE, loginViaUi } from "../fixtures/auth";

/**
 * Prefer storageState from setup (`e2e/.auth/user.json`).
 * Fall back to UI login if the file is missing or the session expired.
 */
export async function ensureAuthenticated(page: Page): Promise<void> {
  if (!fs.existsSync(AUTH_STORAGE_STATE)) {
    await loginViaUi(page);
    return;
  }

  await page.goto("/dashboard");
  if (page.url().includes("/login")) {
    await loginViaUi(page);
  }
}
