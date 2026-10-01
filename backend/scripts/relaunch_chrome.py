import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        ext_dir = os.path.abspath("../anticaptcha-plugin_v0.83")
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
                
        # Launch second time using the same profile that now has Developer Mode enabled!
        context2 = await p.chromium.launch_persistent_context(
            user_data_dir=os.path.abspath("test_chrome_profile2"),
            executable_path=chrome_path,
            headless=False,
            args=launch_args,
            ignore_default_args=["--disable-extensions", "--disable-component-extensions-with-background-pages"]
        )
        
        page2 = context2.pages[0] if context2.pages else await context2.new_page()
        await page2.goto("chrome://extensions", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        await page2.screenshot(path="chrome_extensions_debug_relaunch.png")
        print("Screenshot of second launch saved to chrome_extensions_debug_relaunch.png")
        await context2.close()

if __name__ == "__main__":
    asyncio.run(main())
