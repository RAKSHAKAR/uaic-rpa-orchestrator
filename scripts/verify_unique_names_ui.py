"""Visual verification script for Unique Names API Live Tester in Settings UI.
Captures screenshot of Cornelius Bright, Aquaria Mitchell, and Felicia Mcmiller 3-array deduplication in action.
"""

import asyncio
import os
import shutil
from playwright.async_api import async_playwright

SCREENSHOT_PATH = "implementation_plan/Images/settings_unique_names_matrix_verified.png"
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

        # Ensure we are on Tab 1 (APIs & Integrations)
        apis_tab = page.locator("button:has-text('APIs & Integrations')")
        if await apis_tab.count() > 0:
            await apis_tab.first.click()
            await page.wait_for_timeout(1000)

        # Find the Unique Names party deduplication section
        dedup_header = page.locator("text=Unique Names Party Deduplication & Noise Cleaning Engine")
        await dedup_header.scroll_into_view_if_needed()
        await page.wait_for_timeout(1000)

        # Move the slider to 60%
        slider = page.locator("input[type='range']").nth(0)
        if await slider.count() > 0:
            print("Adjusting Party Deduplication Threshold slider to 0.60...")
            await slider.fill("0.6")
            await page.wait_for_timeout(500)

        # Find the Unique Names API Live Tester section
        tester_header = page.locator("text=Unique Names API Live Tester")
        await tester_header.scroll_into_view_if_needed()
        await page.wait_for_timeout(500)

        # Click the "Generate Unique Names" button
        generate_btn = page.locator("button:has-text('Generate Unique Names')")
        if await generate_btn.count() > 0:
            print("Clicking 'Generate Unique Names' button...")
            await generate_btn.first.click()
            # Wait for response to appear in response container
            await page.wait_for_selector("text=total_unique_names", timeout=5000)
            await page.wait_for_timeout(1000)
            print("Response successfully rendered!")

        # Scroll so Unique Names API Live Tester and response are clearly visible
        await tester_header.scroll_into_view_if_needed()
        await page.wait_for_timeout(800)

        # Capture the screenshot
        await page.screenshot(path=SCREENSHOT_PATH, full_page=False)
        print(f"Saved screenshot to {SCREENSHOT_PATH}")

        # Also copy to artifact directory for presentation
        artifact_dest = os.path.join(ARTIFACT_DIR, "settings_unique_names_matrix_verified.png")
        shutil.copy2(SCREENSHOT_PATH, artifact_dest)
        print(f"Copied to {artifact_dest}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
