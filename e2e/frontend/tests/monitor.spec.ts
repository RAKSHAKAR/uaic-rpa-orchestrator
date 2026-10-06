import { test, expect } from "@playwright/test";

test.describe("Queue Monitor Page E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/monitor");
  });

  test("renders queue orchestrator status and controls", async ({ page }) => {
    await expect(page).toHaveURL(/.*monitor/);
    await expect(page.getByText(/Queue Monitor|Orchestrator Execution Monitor/i).first()).toBeVisible();
  });

  test("displays queue statistics cards", async ({ page }) => {
    // Check metric cards: Active, Queued, Completed, Failed
    const main = page.locator("main, [role='main']").first();
    await expect(main).toBeVisible();
    await expect(page.getByText(/Active|Queued|Completed|Failed/i).first()).toBeVisible();
  });

  test("displays queue table with claim processing rows", async ({ page }) => {
    const tableOrEmpty = page.locator("table, [role='table'], text=No active queue items, text=Queue is empty").first();
    await expect(tableOrEmpty).toBeVisible();
  });
});
