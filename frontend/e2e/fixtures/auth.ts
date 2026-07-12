import fs from "node:fs";
import path from "node:path";
import type { Page } from "@playwright/test";
import { LoginPage } from "../pages/login.page";

/** Persisted Playwright storageState (localStorage tokens + cookies). */
export const AUTH_STORAGE_STATE = path.join(__dirname, "../.auth/user.json");

export function e2eCredentials() {
  return {
    email: process.env.E2E_EMAIL || "owner@krishifarms.local",
    password: process.env.E2E_PASSWORD || "ChangeMe123!",
  };
}

/**
 * UI login on `/login`. Supports current "Next" CTA and older "Sign in" label.
 * Tokens land in localStorage (`krishi-access-token`); storageState captures them.
 */
export async function loginViaUi(page: Page): Promise<void> {
  const { email, password } = e2eCredentials();
  const loginPage = new LoginPage(page);
  await loginPage.login(email, password);
}

/** Ensure auth dir exists and write storageState for dependent projects. */
export async function saveAuthStorageState(page: Page): Promise<void> {
  fs.mkdirSync(path.dirname(AUTH_STORAGE_STATE), { recursive: true });
  await page.context().storageState({ path: AUTH_STORAGE_STATE });
}
