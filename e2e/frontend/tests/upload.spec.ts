import { test, expect } from "@playwright/test";

test.describe("Upload & Ingestion Page E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/upload");
  });

  test("renders file upload dropzone", async ({ page }) => {
    await expect(page).toHaveURL(/.*upload/);
    await expect(page.getByText(/Upload & Ingest|Import Claims Dataset|Drag and drop/i).first()).toBeVisible();
  });

  test("displays template download link or button", async ({ page }) => {
    const templateLink = page.getByText(/Download Template|Sample Excel|Download Sample/i).first();
    await expect(templateLink).toBeVisible();
  });
});
