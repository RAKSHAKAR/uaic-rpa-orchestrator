import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    ext_dir = os.path.abspath("../anticaptcha-plugin_v0.83")
    profile_dir = os.path.abspath("test_load_unpacked_profile4")
    
    async with async_playwright() as p:
        chrome_path = None
        for p_path in [
            r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        ]:
            if os.path.exists(p_path):
                chrome_path = p_path
                break
                
        context = await p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            executable_path=chrome_path,
            headless=False,
            args=["--test-type", "--disable-extensions"]
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("chrome://extensions", wait_until="networkidle")
        
        # Click Developer mode toggle
        try:
            await page.locator('#devMode').click(timeout=3000)
            print("Clicked Developer mode toggle using Playwright locator.")
            await asyncio.sleep(1)
        except Exception as e:
            print(f"Could not click dev mode toggle: {e}")
            
        # Click Load unpacked and handle file chooser
        try:
            async with page.expect_file_chooser(timeout=5000) as fc_info:
                await page.locator('#loadUnpacked').click(timeout=3000)
            
            file_chooser = await fc_info.value
            print("File chooser intercepted!")
            await file_chooser.set_files(ext_dir)
            print(f"Loaded extension from {ext_dir}")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Error handling file chooser: {e}")
            
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
