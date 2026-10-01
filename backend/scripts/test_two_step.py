import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    ext_dir = os.path.abspath("../anticaptcha-plugin_v0.83")
    profile_dir = os.path.abspath("test_two_step_profile")
    
    chrome_path = None
    for p_path in [
        r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    ]:
        if os.path.exists(p_path):
            chrome_path = p_path
            break

    # Step 1: Launch, enable dev mode via UI, close
    print("Step 1: Enabling Developer Mode via UI...")
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            executable_path=chrome_path,
            headless=False,
            args=["--test-type", "--disable-extensions"]
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("chrome://extensions", wait_until="networkidle")
        
        await page.evaluate('''() => {
            const extManager = document.querySelector('extensions-manager');
            const toolbar = extManager.shadowRoot.querySelector('extensions-toolbar');
            const toggle = toolbar.shadowRoot.querySelector('#devMode');
            if (toggle && !toggle.checked) {
                toggle.click();
            }
        }''')
        await asyncio.sleep(2)
        await context.close()

    # Step 2: Relaunch with --load-extension
    print("Step 2: Relaunching with --load-extension...")
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            executable_path=chrome_path,
            headless=False,
            args=["--test-type", f"--disable-extensions-except={ext_dir}", f"--load-extension={ext_dir}"]
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("chrome://extensions", wait_until="networkidle")
        
        ext_found = await page.evaluate('''() => {
            const extManager = document.querySelector('extensions-manager');
            const list = extManager.shadowRoot.querySelector('extensions-item-list');
            return list && list.shadowRoot.querySelectorAll('extensions-item').length > 0;
        }''')
        print(f"Extension successfully loaded: {ext_found}")
        await asyncio.sleep(1)
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
