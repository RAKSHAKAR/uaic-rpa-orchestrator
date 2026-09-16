"""Test interactive execution of Fuzzy Match API Tester in browser and capture screenshot."""

import asyncio
import os
import shutil
from playwright.async_api import async_playwright


async def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    images_dir = os.path.join(repo_root, "implementation_plan", "Images")
    brain_dir = r"C:\Users\priyer\.gemini\antigravity-ide\brain\30bd64a9-ed61-44b7-89db-e138423f4fb8"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("Navigating to http://localhost:3000/settings...")
        await page.goto("http://localhost:3000/settings", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(1500)

        # Scroll down to Fuzzy Match API Tester
        await page.evaluate("window.scrollTo(0, 2300)")
        await page.wait_for_timeout(500)

        # Click Evaluate Fuzzy Match button
        eval_btn = page.locator("button:has-text('Evaluate Fuzzy Match')")
        if await eval_btn.is_visible():
            print("Clicking 'Evaluate Fuzzy Match'...")
            await eval_btn.click()
            await page.wait_for_timeout(1500)

        # Capture evaluated state screenshot
        active_img_path = os.path.join(images_dir, "settings_fuzzy_tester_evaluated_result.png")
        await page.screenshot(path=active_img_path, full_page=False)
        print(f"Captured active evaluated state: {active_img_path}")
        if os.path.exists(brain_dir):
            shutil.copy(active_img_path, os.path.join(brain_dir, "settings_fuzzy_tester_evaluated_result.png"))

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
