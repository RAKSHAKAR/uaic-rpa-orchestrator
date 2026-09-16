"""Capture visual evidence of the reorganized Settings page tabs."""

import asyncio
import os
import shutil
from playwright.async_api import async_playwright

ARTIFACTS_DIR = r"C:\Users\priyer\.gemini\antigravity-ide\brain\30bd64a9-ed61-44b7-89db-e138423f4fb8"

async def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    images_dir = os.path.join(repo_root, "implementation_plan", "Images")
    os.makedirs(images_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        print("Navigating to http://localhost:3000/settings...")
        await page.goto("http://localhost:3000/settings", wait_until="domcontentloaded", timeout=45000)
        
        print("Waiting for settings to finish loading...")
        await page.wait_for_selector("button:has-text('APIs & Matching Engine')", timeout=45000)
        await page.wait_for_timeout(1500)

        # 1. Capture Tab 1: APIs & Matching (Top)
        top_img = os.path.join(images_dir, "settings_tab_1_apis_and_matching.png")
        await page.screenshot(path=top_img, full_page=False)
        print(f"Captured: {top_img}")

        # 2. Capture Tab 1 scrolled down to RapidFuzz & Fuzzy Match Tester
        await page.evaluate("window.scrollBy(0, 1100)")
        await page.wait_for_timeout(1000)
        bottom_img = os.path.join(images_dir, "settings_tab_1_rapidfuzz_and_fuzzy_tester.png")
        await page.screenshot(path=bottom_img, full_page=False)
        print(f"Captured: {bottom_img}")

        # Scroll to top
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(500)

        # 3. Click Tab 3: Browser Automation & Fleet
        print("Clicking Browser Automation & Fleet tab...")
        auto_btn = page.locator("button:has-text('Browser Automation & Fleet')")
        await auto_btn.click()
        await page.wait_for_selector("text=Browser Automation & RPA Execution Fleet", timeout=15000)
        await page.wait_for_timeout(1000)
        auto_img = os.path.join(images_dir, "settings_tab_3_browser_automation.png")
        await page.screenshot(path=auto_img, full_page=False)
        print(f"Captured: {auto_img}")

        # 4. Click Tab 4: CAPTCHA Solver & Extension
        print("Clicking CAPTCHA Solver & Extension tab...")
        ext_btn = page.locator("button:has-text('CAPTCHA Solver & Extension')")
        await ext_btn.click()
        await page.wait_for_selector("text=CAPTCHA Challenge Detection", timeout=15000)
        await page.wait_for_timeout(1000)
        ext_img = os.path.join(images_dir, "settings_tab_4_captcha_extension.png")
        await page.screenshot(path=ext_img, full_page=False)
        print(f"Captured: {ext_img}")

        # 5. Click Tab 5: Proxy Network
        print("Clicking Proxy Network tab...")
        proxy_btn = page.locator("button:has-text('Proxy Network')")
        await proxy_btn.click()
        await page.wait_for_selector("text=Proxy Pool Settings", timeout=15000)
        await page.wait_for_timeout(1000)
        proxy_img = os.path.join(images_dir, "settings_tab_5_proxy_network.png")
        await page.screenshot(path=proxy_img, full_page=False)
        print(f"Captured: {proxy_img}")

        await browser.close()
        
        # Copy to artifacts directory
        for fname in [
            "settings_tab_1_apis_and_matching.png",
            "settings_tab_1_rapidfuzz_and_fuzzy_tester.png",
            "settings_tab_3_browser_automation.png",
            "settings_tab_4_captcha_extension.png",
            "settings_tab_5_proxy_network.png",
        ]:
            src = os.path.join(images_dir, fname)
            dst = os.path.join(ARTIFACTS_DIR, fname)
            if os.path.exists(src):
                shutil.copyfile(src, dst)
        print("All screenshots captured and copied to artifacts directory successfully!")

if __name__ == "__main__":
    asyncio.run(main())
