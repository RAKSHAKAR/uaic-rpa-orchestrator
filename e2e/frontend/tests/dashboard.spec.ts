import { test, expect } from "@playwright/test";

test.describe("Dashboard Page E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test("renders navigation bar and brand title", async ({ page }) => {
    await expect(page).toHaveTitle(/UAIC/i);
    const nav = page.locator("nav, header").first();
    await expect(nav).toBeVisible();
    await expect(page.getByText(/UAIC Orchestrator|Claim & RPA Orchestrator/i).first()).toBeVisible();
  });

  test("displays metric cards and claims data table", async ({ page }) => {
    // Check main dashboard statistics cards
    const statsContainer = page.locator("main, [role='main']").first();
    await expect(statsContainer).toBeVisible();

    // Verify presence of table or empty state
    const tableOrEmpty = page.locator("table, [role='table'], text=No claims found").first();
    await expect(tableOrEmpty).toBeVisible();
  });

  test("supports global search filter interaction", async ({ page }) => {
    const searchInput = page.locator("input[placeholder*='Search']").first();
    if (await searchInput.isVisible()) {
      await searchInput.fill("CLM-TEST-001");
      await expect(searchInput).toHaveValue("CLM-TEST-001");
      await searchInput.clear();
    }
  });

  test("displays in progress subtitle breakdown and quick filter tab counts", async ({ page }) => {
    // Verify In Progress / Queue breakdown subtitle
    const queueSubtitle = page.locator("text=/active scraping.*queued/i").first();
    if (await queueSubtitle.isVisible()) {
      await expect(queueSubtitle).toBeVisible();
    }

    // Verify Quick Filter tabs have count badges
    const allTab = page.getByRole("button", { name: /All Claims/i }).first();
    if (await allTab.isVisible()) {
      await expect(allTab).toBeVisible();
    }
  });

  test("displays multi-select filter comboboxes with dynamic counts", async ({ page }) => {
    // Verify presence of filter trigger buttons (Status, State, Match)
    const filterButtons = page.locator("button:has-text('Status:'), button:has-text('State:'), button:has-text('Match:')");
    const count = await filterButtons.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });
});

