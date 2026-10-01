import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        ext_dir = os.path.abspath("../anticaptcha-plugin_v0.83")
        print(f"Extension dir: {ext_dir}")
        launch_args = [
            "--start-maximized",
            f"--disable-extensions-except={ext_dir}",
            f"--load-extension={ext_dir}",
            "--enable-developer-mode",
            "--disable-extension-content-verification",
            "--disable-extensions-file-access-check",
            "--allow-outdated-plugins",
            "--disable-infobars",
            "--test-type",
            "--disable-blink-features=AutomationControlled",
        ]
        
        chrome_path = None
        for p_path in [
            r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        ]:
            if os.path.exists(p_path):
                chrome_path = p_path
                break
                
        print(f"Chrome path: {chrome_path}")
        
        context = await p.chromium.launch_persistent_context(
            user_data_dir=os.path.abspath("test_chrome_profile"),
            executable_path=chrome_path,
            headless=False,
            args=launch_args,
            ignore_default_args=["--disable-extensions", "--disable-component-extensions-with-background-pages"]
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        print("Navigating to chrome://extensions...")
        await page.goto("chrome://extensions", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        screenshot_path = os.path.abspath("chrome_extensions_debug.png")
        await page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
