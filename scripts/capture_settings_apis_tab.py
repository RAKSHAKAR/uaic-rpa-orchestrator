"""Capture visual evidence of the separated Unique Names and Fuzzy Match API Testers in Settings."""

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
        await page.wait_for_timeout(2000)

        # 1. Capture top view (APIs tab selected + Guidewire Integration card)
        top_img_path = os.path.join(images_dir, "settings_apis_tab_top_guidewire.png")
        await page.screenshot(path=top_img_path, full_page=False)
        print(f"Captured top view: {top_img_path}")
        if os.path.exists(brain_dir):
            shutil.copy(top_img_path, os.path.join(brain_dir, "settings_apis_tab_top_guidewire.png"))

        # 2. Scroll to Unique Names Engine & API Tester
        await page.evaluate("window.scrollTo(0, 1050)")
        await page.wait_for_timeout(1000)
        unique_img_path = os.path.join(images_dir, "settings_apis_tab_unique_names_engine.png")
        await page.screenshot(path=unique_img_path, full_page=False)
        print(f"Captured Unique Names Engine view: {unique_img_path}")
        if os.path.exists(brain_dir):
            shutil.copy(unique_img_path, os.path.join(brain_dir, "settings_apis_tab_unique_names_engine.png"))

        # 3. Scroll to RapidFuzz Case Matching & Guidewire Filter Engine + Fuzzy Match API Tester
        await page.evaluate("window.scrollTo(0, 2200)")
        await page.wait_for_timeout(1000)
        fuzzy_img_path = os.path.join(images_dir, "settings_apis_tab_fuzzy_match_engine.png")
        await page.screenshot(path=fuzzy_img_path, full_page=False)
        print(f"Captured Fuzzy Match Engine view: {fuzzy_img_path}")
        if os.path.exists(brain_dir):
            shutil.copy(fuzzy_img_path, os.path.join(brain_dir, "settings_apis_tab_fuzzy_match_engine.png"))

        # 4. Full page screenshot for complete review
        full_img_path = os.path.join(images_dir, "settings_apis_tab_full_page.png")
        await page.screenshot(path=full_img_path, full_page=True)
        print(f"Captured full page view: {full_img_path}")
        if os.path.exists(brain_dir):
            shutil.copy(full_img_path, os.path.join(brain_dir, "settings_apis_tab_full_page.png"))

        await browser.close()
        print("Visual verification screenshots captured successfully!")


if __name__ == "__main__":
    asyncio.run(main())
