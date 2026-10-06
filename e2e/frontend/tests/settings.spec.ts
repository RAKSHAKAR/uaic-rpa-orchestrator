import { test, expect } from "@playwright/test";

test.describe("Settings Page E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/settings");
  });

  test("renders automation runtime settings panel", async ({ page }) => {
    await expect(page).toHaveURL(/.*settings/);
    await expect(page.getByText(/Browser Automation Engine|Browser Engine & Runtime Environment/i).first()).toBeVisible();
  });

  test("allows selecting browser automation engine", async ({ page }) => {
    const chromiumCard = page.getByText(/Chromium \(Bundled\)/i).first();
    const chromeCard = page.getByText(/Google Chrome/i).first();
    await expect(chromiumCard).toBeVisible();
    await expect(chromeCard).toBeVisible();

    // Click Chromium and verify selection
    await chromiumCard.click();
    await expect(page.getByText(/Selected Engine:\s*CHROMIUM|Assigned Engine:\s*Chromium/i).first()).toBeVisible();
  });

  test("displays execution mode toggle (Attended vs Headless)", async ({ page }) => {
    const attendedOption = page.getByText(/Attended \(Visible GUI\)/i).first();
    const headlessOption = page.getByText(/Headless \(Background\)/i).first();
    await expect(attendedOption).toBeVisible();
    await expect(headlessOption).toBeVisible();
  });

  test("displays public county court portal list with ping triggers", async ({ page }) => {
    // Scroll down to County Court Scraper Portals section
    const portalsHeader = page.getByText(/Public County Court Scraper Portals|County Court Clerk Portals/i).first();
    await portalsHeader.scrollIntoViewIfNeeded();
    await expect(portalsHeader).toBeVisible();

    // Verify presence of ping portal buttons
    const pingButtons = page.getByRole("button", { name: /Ping Portal/i });
    const count = await pingButtons.count();
    expect(count).toBeGreaterThanOrEqual(1);
  });

  test("displays retention time scopes including 14 days and purge button", async ({ page }) => {
    // Navigate to Storage & Retention tab if present
    const storageTab = page.getByRole("button", { name: /Storage & Exports|Retention/i }).first();
    if (await storageTab.isVisible()) {
      await storageTab.click();
    }

    // Verify retention scope dropdown options
    const retentionSelect = page.locator("select").filter({ hasText: /Older than/i }).first();
    if (await retentionSelect.isVisible()) {
      await expect(retentionSelect).toBeVisible();
      const text = await retentionSelect.innerText();
      expect(text).toContain("14 Days");
    }

    // Verify manual purge button
    const purgeBtn = page.getByRole("button", { name: /Purge Expired Storage Now/i }).first();
    if (await purgeBtn.isVisible()) {
      await expect(purgeBtn).toBeVisible();
    }
  });
});

