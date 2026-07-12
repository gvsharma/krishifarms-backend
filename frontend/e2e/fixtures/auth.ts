import fs from "node:fs";
import path from "node:path";
import type { Page } from "@playwright/test";

/** Persisted Playwright storageState (localStorage tokens + cookies). */
export const AUTH_STORAGE_STATE = path.join(__dirname, "../.auth/user.json");

export function e2eCredentials() {
  return {
    email: process.env.E2E_EMAIL || "gvsharma4@gmail.com",
    password: process.env.E2E_PASSWORD || "admin123",
  };
}

/**
 * UI login on `/login`. Supports current "Next" CTA and older "Sign in" label.
 * Tokens land in localStorage (`krishi-access-token`); storageState captures them.
 */
export async function loginViaUi(page: Page): Promise<void> {
  const { email, password } = e2eCredentials();

  await page.goto("/login");
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/^password/i).fill(password);
  await page.getByRole("button", { name: /^(Next|Sign in)$/i }).click();

  await page.waitForURL((url) => !url.pathname.includes("/login"), { timeout: 45_000 });
  await page.waitForFunction(() => Boolean(localStorage.getItem("krishi-access-token")), null, {
    timeout: 15_000,
  });
}

/** Ensure auth dir exists and write storageState for dependent projects. */
export async function saveAuthStorageState(page: Page): Promise<void> {
  fs.mkdirSync(path.dirname(AUTH_STORAGE_STATE), { recursive: true });
  await page.context().storageState({ path: AUTH_STORAGE_STATE });
}
