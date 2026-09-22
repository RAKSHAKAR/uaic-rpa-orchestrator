"""Capture screenshots of the updated Action ID & Profile Target card across viewports."""
import asyncio
from playwright.async_api import async_playwright

VIEWPORTS = [
    ("desktop", 1440, 900),
    ("tablet", 1024, 768),
    ("mobile", 390, 844),
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for name, width, height in VIEWPORTS:
            context = await browser.new_context(viewport={"width": width, "height": height})
            page = await context.new_page()

            print(f"Loading /settings at {width}x{height} ({name})...")
            await page.goto("http://localhost:3000/settings", wait_until="networkidle", timeout=30000)
            # Wait for loading spinner to detach
            try:
                await page.wait_for_selector("text=Loading dynamic system settings...", state="hidden", timeout=15000)
            except Exception:
                pass
            await page.wait_for_timeout(1000)

            # Click Tab 4 (CAPTCHA Solver & Extension)
            tab_button = page.locator("button:has-text('CAPTCHA Solver & Extension'), button:has-text('CAPTCHA Solver')").first
            await tab_button.wait_for(state="visible", timeout=15000)
            await tab_button.click()
            await page.wait_for_timeout(1000)

            # Locate the exact One-Time Extension Toolbar Pinning card container
            pinning_card = page.locator("text=One-Time Extension Toolbar Pinning").locator("xpath=ancestor::div[contains(@class, 'rounded-2xl')][1]")
            await pinning_card.wait_for(state="visible", timeout=15000)
            await pinning_card.scroll_into_view_if_needed()
            await page.wait_for_timeout(600)

            save_path = f"implementation_plan/Images/action_id_aligned_{name}.png"
            await pinning_card.screenshot(path=save_path)

            print(f"Saved screenshot: {save_path}")
            await context.close()

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
