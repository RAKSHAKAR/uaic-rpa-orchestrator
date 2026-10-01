import asyncio
from playwright.async_api import async_playwright
import os
import shutil

async def main():
    profile_dir = os.path.abspath("test_chrome_profile3")
    if os.path.exists(profile_dir):
        shutil.rmtree(profile_dir)
        
    async with async_playwright() as p:
        ext_dir = os.path.abspath("../anticaptcha-plugin_v0.83")
        launch_args = [
            "--start-maximized",
            f"--disable-extensions-except={ext_dir}",
            f"--load-extension={ext_dir}",
            "--disable-extension-content-verification",
            "--disable-extensions-file-access-check",
            "--allow-outdated-plugins",
            "--disable-infobars",
        ]
        
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
            args=launch_args,
            ignore_default_args=[
                "--disable-extensions", 
                "--disable-component-extensions-with-background-pages",
                "--enable-automation"
            ]
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("chrome://extensions", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        await page.screenshot(path="chrome_extensions_no_automation.png")
        print("Screenshot saved to chrome_extensions_no_automation.png")
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
