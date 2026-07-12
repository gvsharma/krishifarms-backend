import { test as setup } from "@playwright/test";
import { loginViaUi, saveAuthStorageState } from "./fixtures/auth";

setup("authenticate", async ({ page }) => {
  await loginViaUi(page);
  await saveAuthStorageState(page);
});
