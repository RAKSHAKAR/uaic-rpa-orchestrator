"""Capture visual evidence of the new Execution Speed & Keystroke Dynamics card in Settings Tab 3."""

import asyncio
import os
import shutil
from playwright.async_api import async_playwright


async def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    images_dir = os.path.join(repo_root, "implementation_plan", "Images")
    brain_dir = r"C:\Users\priyer\.gemini\antigravity-ide\brain\30bd64a9-ed61-44b7-89db-e138423f4fb8"
    os.makedirs(images_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("Navigating to http://localhost:3000/settings...")
        await page.goto("http://localhost:3000/settings", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(1000)

        # Click on Tab 3: Browser Automation
        tab_btn = page.locator("button:has-text('Browser Automation')").first
        if not await tab_btn.is_visible():
            tab_btn = page.locator("button:has-text('Automation')").first

        print("Clicking Tab 3: Browser Automation...")
        await tab_btn.click()
        await page.wait_for_timeout(1500)

        # 1. Capture top view (Concurrency Fleet + Execution Speed & Keystroke Dynamics Card)
        speed_img_path = os.path.join(images_dir, "settings_tab_3_execution_speed_controls.png")
        await page.screenshot(path=speed_img_path, full_page=False)
        print(f"Captured Tab 3 Speed Controls view: {speed_img_path}")
        if os.path.exists(brain_dir):
            shutil.copy(speed_img_path, os.path.join(brain_dir, "settings_tab_3_execution_speed_controls.png"))

        # 3. Scroll to full view of Execution Speed card and Anti-Captcha notice
        await page.evaluate("window.scrollBy(0, 350)")
        await page.wait_for_timeout(500)
        full_card_img_path = os.path.join(images_dir, "settings_tab_3_speed_card_detailed.png")
        await page.screenshot(path=full_card_img_path, full_page=False)
        print(f"Captured detailed Speed Card view: {full_card_img_path}")
        if os.path.exists(brain_dir):
            shutil.copy(full_card_img_path, os.path.join(brain_dir, "settings_tab_3_speed_card_detailed.png"))

        await browser.close()
        print("Visual verification screenshots captured successfully!")


if __name__ == "__main__":
    asyncio.run(main())
