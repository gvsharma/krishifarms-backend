import { expect, test } from "@playwright/test";
import { expectNoPageErrors, trackPageErrors } from "../../utils/common";

test.describe("smoke — session expiry auto-logout", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test("invalid access + refresh tokens redirect to login", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/login");
    await page.evaluate(() => {
      localStorage.setItem("krishi-access-token", "invalid-access-token");
      localStorage.setItem("krishi-refresh-token", "invalid-refresh-token");
      sessionStorage.removeItem("krishi-signed-out");
    });

    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/, { timeout: 20_000 });

    const tokens = await page.evaluate(() => ({
      access: localStorage.getItem("krishi-access-token"),
      refresh: localStorage.getItem("krishi-refresh-token"),
      signedOut: sessionStorage.getItem("krishi-signed-out"),
    }));
    expect(tokens.access).toBeNull();
    expect(tokens.refresh).toBeNull();
    expect(tokens.signedOut).toBe("1");

    expectNoPageErrors(pageErrors);
  });

  test("missing access token redirects to login without crash", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/login");
    await page.evaluate(() => {
      localStorage.removeItem("krishi-access-token");
      localStorage.removeItem("krishi-refresh-token");
    });

    await page.goto("/farmers");
    await expect(page).toHaveURL(/\/login/, { timeout: 15_000 });
    expectNoPageErrors(pageErrors);
  });

  test("invalid access token alone (no refresh) redirects to login", async ({ page }) => {
    const pageErrors = trackPageErrors(page);

    await page.goto("/login");
    await page.evaluate(() => {
      localStorage.setItem("krishi-access-token", "expired-only");
      localStorage.removeItem("krishi-refresh-token");
      sessionStorage.removeItem("krishi-signed-out");
    });

    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/login/, { timeout: 20_000 });

    const access = await page.evaluate(() => localStorage.getItem("krishi-access-token"));
    expect(access).toBeNull();
    expectNoPageErrors(pageErrors);
  });
});
