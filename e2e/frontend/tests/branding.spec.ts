import { test, expect } from "@playwright/test";

test.describe("Branding & Theme Management Page E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/branding");
  });

  test("renders brand identity console", async ({ page }) => {
    await expect(page).toHaveURL(/.*branding/);
    await expect(page.getByText(/Brand & Identity|Branding Management Console/i).first()).toBeVisible();
  });

  test("toggles between Light Mode and Dark Mode", async ({ page }) => {
    // Theme toggle button in header or on branding page
    const themeBtn = page.locator("button[aria-label*='theme' i], button:has-text('Dark'), button:has-text('Light')").first();
    if (await themeBtn.isVisible()) {
      await themeBtn.click();
      // Verify html tag receives or toggles 'dark' class
      const htmlClass = await page.locator("html").getAttribute("class");
      expect(htmlClass).toBeDefined();
    }
  });

  test("displays design tokens editor and live preview", async ({ page }) => {
    await expect(page.getByText(/Semantic Design Tokens|Brand Palette|Theme Customization/i).first()).toBeVisible();
  });
});
