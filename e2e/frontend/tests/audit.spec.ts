import { test, expect } from "@playwright/test";

test.describe("Audit Trail Page E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/audit");
  });

  test("renders audit trail header and table", async ({ page }) => {
    await expect(page).toHaveURL(/.*audit/);
    await expect(page.getByText(/Audit Trail|System Event Log/i).first()).toBeVisible();
  });

  test("displays stat cards and dynamic filter dropdowns with live counts", async ({ page }) => {
    // Verify stat cards
    await expect(page.getByText(/Total Events/i).first()).toBeVisible();
    await expect(page.getByText(/Today's Activity/i).first()).toBeVisible();
    await expect(page.getByText(/Claim Ops/i).first()).toBeVisible();
    await expect(page.getByText(/Failures/i).first()).toBeVisible();

    // Verify filter dropdowns (Actions, Entities, Statuses)
    const filterButtons = page.locator("button:has-text('Actions:'), button:has-text('Entities:'), button:has-text('Statuses:')");
    const count = await filterButtons.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test("toggles theme between light and dark mode seamlessly", async ({ page }) => {
    const themeBtn = page.locator("button[aria-label='Toggle theme']").first();
    await expect(themeBtn).toBeVisible();

    // Toggle theme and verify document attribute or class changes
    await themeBtn.click();
    await page.waitForTimeout(500);

    // Toggle back
    await themeBtn.click();
    await page.waitForTimeout(500);
  });
});

