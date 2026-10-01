import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    profile_dir = os.path.abspath("test_dev_mode_profile3")
    chrome_path = os.path.expandvars(r"%TEMP%\\chrome_bypass.exe")
    
    if not os.path.exists(chrome_path):
        print(f"Not found: {chrome_path}")
        return
        
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            executable_path=chrome_path,
            headless=False,
            args=["--test-type"]
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("chrome://extensions", wait_until="networkidle")
        await asyncio.sleep(2)
        await page.screenshot(path="extensions_bypass.png")
        await context.close()
        print("Screenshot saved.")

if __name__ == "__main__":
    asyncio.run(main())
