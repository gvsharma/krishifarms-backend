import { expect, test } from "@playwright/test";

test.describe("dashboard smoke", () => {
  test("loads shell after auth without page errors", async ({ page }) => {
    const pageErrors: string[] = [];
    page.on("pageerror", (err) => {
      pageErrors.push(err.message);
    });

    await page.goto("/dashboard");

    await expect(page.getByRole("heading", { name: /^Home$/i })).toBeVisible();
    await expect(page.getByText(/Farm operations overview/i).first()).toBeVisible();

    expect(pageErrors, `Uncaught page errors:\n${pageErrors.join("\n")}`).toEqual([]);
  });
});
