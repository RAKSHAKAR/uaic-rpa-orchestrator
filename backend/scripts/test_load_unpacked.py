import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    ext_dir = os.path.abspath("../anticaptcha-plugin_v0.83")
    profile_dir = os.path.abspath("test_load_unpacked_profile2")
    
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
        
        # Take initial screenshot
        await page.screenshot(path="extensions_initial.png")
        print("extensions_initial.png saved.")
        
        # Enable developer mode
        await page.evaluate('''() => {
            const extManager = document.querySelector('extensions-manager');
            if (!extManager) return;
            const toolbar = extManager.shadowRoot.querySelector('extensions-toolbar');
            if (!toolbar) return;
            const toggle = toolbar.shadowRoot.querySelector('#devMode');
            if (toggle && (!toggle.hasAttribute('aria-pressed') || toggle.getAttribute('aria-pressed') === 'false')) {
                toggle.click();
            }
        }''')
        await asyncio.sleep(1)
        
        # Take screenshot after toggling
        await page.screenshot(path="extensions_after_toggle.png")
        print("extensions_after_toggle.png saved.")
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
