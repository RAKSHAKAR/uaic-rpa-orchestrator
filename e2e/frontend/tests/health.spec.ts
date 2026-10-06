import { test, expect } from "@playwright/test";

test.describe("System Health Page E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/health");
  });

  test("renders system posture banner and browser health panel", async ({ page }) => {
    await expect(page).toHaveURL(/.*health/);
    await expect(page.getByText(/Overall System Posture/i).first()).toBeVisible();
    await expect(page.getByText(/RPA Browser & Automation Health Panel/i).first()).toBeVisible();
  });

  test("renders core infrastructure stack modules", async ({ page }) => {
    await expect(page.getByText(/Core Infrastructure Stack/i).first()).toBeVisible();
    await expect(page.getByText(/FastAPI Core Service/i).first()).toBeVisible();
    await expect(page.getByText(/SQLAlchemy Database Engine/i).first()).toBeVisible();
    await expect(page.getByText(/Redis Broker \/ Cache/i).first()).toBeVisible();
    await expect(page.getByText(/Celery Distributed Workers/i).first()).toBeVisible();
    await expect(page.getByText(/AntiCaptcha Extension/i).first()).toBeVisible();
    await expect(page.getByText(/Guidewire Cloud Integration/i).first()).toBeVisible();
    await expect(page.getByText(/Local File Storage/i).first()).toBeVisible();
  });

  test("renders 8 county court clerk portals with live ping latency", async ({ page }) => {
    const courtPortalsSection = page.getByText(/County Court Clerk Portals/i).first();
    await courtPortalsSection.scrollIntoViewIfNeeded();
    await expect(courtPortalsSection).toBeVisible();

    await expect(page.getByText(/Broward County Clerk/i).first()).toBeVisible();
    await expect(page.getByText(/Hillsborough County Clerk/i).first()).toBeVisible();
    await expect(page.getByText(/Miami-Dade County Clerk/i).first()).toBeVisible();
    await expect(page.getByText(/Travis County/i).first()).toBeVisible();
    await expect(page.getByText(/Dallas County/i).first()).toBeVisible();
    await expect(page.getByText(/Harris County JP/i).first()).toBeVisible();
    await expect(page.getByText(/Harris County District Clerk/i).first()).toBeVisible();
    await expect(page.getByText(/Harris County Clerk/i).first()).toBeVisible();
  });
});
