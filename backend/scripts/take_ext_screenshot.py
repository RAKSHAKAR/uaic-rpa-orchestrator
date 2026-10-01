import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    profile_dir = os.path.abspath("test_dev_mode_profile2")
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            args=["--test-type"]
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("chrome://extensions", wait_until="networkidle")
        await asyncio.sleep(2)
        await page.screenshot(path="extensions_managed.png")
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
