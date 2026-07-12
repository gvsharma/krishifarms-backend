import { expect, test } from "../../fixtures";

test.describe("smoke — dashboard (POM)", () => {
  test("loads via DashboardPage fixture", async ({ dashboardPage, pageErrors }) => {
    await dashboardPage.goto();
    await dashboardPage.expectLoaded();
    expect(pageErrors).toEqual([]);
  });

  test("authedPage fixture reaches dashboard", async ({ authedPage, pageErrors }) => {
    await authedPage.goto("/dashboard");
    await expect(authedPage.getByRole("heading", { name: /^Home$/i })).toBeVisible();
    expect(pageErrors).toEqual([]);
  });
});
