import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    profile_dir = os.path.abspath("test_load_unpacked_profile3")
    
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
        
        # Check initial state
        initial_state = await page.evaluate('''() => {
            const extManager = document.querySelector('extensions-manager');
            const toolbar = extManager.shadowRoot.querySelector('extensions-toolbar');
            const toggle = toolbar.shadowRoot.querySelector('#devMode');
            return toggle ? toggle.getAttribute('aria-pressed') : 'not found';
        }''')
        print(f"Initial devMode aria-pressed: {initial_state}")
        
        # Enable developer mode
        await page.evaluate('''() => {
            const extManager = document.querySelector('extensions-manager');
            const toolbar = extManager.shadowRoot.querySelector('extensions-toolbar');
            const toggle = toolbar.shadowRoot.querySelector('#devMode');
            if (toggle && toggle.getAttribute('aria-pressed') !== 'true') {
                toggle.click();
            }
        }''')
        await asyncio.sleep(1)
        
        # Check new state
        new_state = await page.evaluate('''() => {
            const extManager = document.querySelector('extensions-manager');
            const toolbar = extManager.shadowRoot.querySelector('extensions-toolbar');
            const toggle = toolbar.shadowRoot.querySelector('#devMode');
            return toggle ? toggle.getAttribute('aria-pressed') : 'not found';
        }''')
        print(f"New devMode aria-pressed: {new_state}")
        
        # Try to find Load unpacked button
        load_btn_visible = await page.evaluate('''() => {
            const extManager = document.querySelector('extensions-manager');
            const toolbar = extManager.shadowRoot.querySelector('extensions-toolbar');
            const loadBtn = toolbar.shadowRoot.querySelector('#loadUnpacked');
            return loadBtn && window.getComputedStyle(loadBtn).display !== 'none';
        }''')
        print(f"Load unpacked button visible: {load_btn_visible}")
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
