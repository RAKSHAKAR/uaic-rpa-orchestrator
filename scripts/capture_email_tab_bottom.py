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
        await page.goto("http://localhost:3000/settings", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_selector("button:has-text('Email & Notifications')", timeout=30000)
        await page.wait_for_timeout(1000)

        # Click Email & Notifications tab
        print("Clicking Email & Notifications tab...")
        email_btn = page.locator("button:has-text('Email & Notifications')")
        await email_btn.click()
        await page.wait_for_selector("text=Outbound Notification Delivery History", timeout=15000)
        await page.wait_for_timeout(1500)

        # Scroll to bottom of delivery history
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(1000)

        out_img = os.path.join(images_dir, "settings_email_tab_bottom_fixed.png")
        await page.screenshot(path=out_img, full_page=False)
        print(f"Captured: {out_img}")

        await browser.close()

        # Copy to brain artifacts
        dst = os.path.join(ARTIFACTS_DIR, "settings_email_tab_bottom_fixed.png")
        shutil.copyfile(out_img, dst)
        print("Copied to brain artifacts successfully!")

if __name__ == "__main__":
    asyncio.run(main())
