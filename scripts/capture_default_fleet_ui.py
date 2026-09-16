"""Capture screenshot of Settings Tab 3 verifying default Fleet = 1."""

import asyncio
import os
import shutil
from playwright.async_api import async_playwright

SCREENSHOT_PATH = "implementation_plan/Images/settings_default_fleet_1.png"
ARTIFACT_DIR = r"C:\Users\priyer\.gemini\antigravity-ide\brain\30bd64a9-ed61-44b7-89db-e138423f4fb8"


async def main():
    os.makedirs("implementation_plan/Images", exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("Navigating to http://localhost:3000/settings...")
        await page.goto("http://localhost:3000/settings", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Click Tab 3: Browser Automation & Fleet
        auto_tab = page.locator("button:has-text('Browser Automation & Fleet')")
        if await auto_tab.count() > 0:
            await auto_tab.first.click()
            await page.wait_for_timeout(1000)

        # Verify Fleet section is visible
        fleet_header = page.locator("text=Concurrent Scraper Worker Fleet")
        await fleet_header.scroll_into_view_if_needed()
        await page.wait_for_timeout(1000)

        # Screenshot the full viewport
        await page.screenshot(path=SCREENSHOT_PATH, full_page=False)
        print(f"Saved screenshot to {SCREENSHOT_PATH}")

        # Copy to artifact dir
        artifact_dest = os.path.join(ARTIFACT_DIR, "settings_default_fleet_1.png")
        shutil.copy2(SCREENSHOT_PATH, artifact_dest)
        print(f"Copied to {artifact_dest}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
