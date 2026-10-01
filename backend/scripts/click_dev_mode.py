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
                
        context = await p.chromium.launch_persistent_context(
            user_data_dir=os.path.abspath("test_chrome_profile2"),
            executable_path=chrome_path,
            headless=False,
            args=launch_args,
            ignore_default_args=["--disable-extensions", "--disable-component-extensions-with-background-pages"]
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto("chrome://extensions", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        
        # Try to click Developer mode toggle
        try:
            # We need to pierce the shadow DOM of the extensions manager
            await page.evaluate('''() => {
                const manager = document.querySelector('extensions-manager');
                const toolbar = manager.shadowRoot.querySelector('extensions-toolbar');
                const toggle = toolbar.shadowRoot.querySelector('#devMode');
                if (toggle && !toggle.hasAttribute('aria-pressed') || toggle.getAttribute('aria-pressed') === 'false') {
                    toggle.click();
                }
            }''')
            print("Clicked Developer Mode toggle!")
            await asyncio.sleep(2)
            await page.screenshot(path="chrome_extensions_debug_after_click.png")
            print("Screenshot saved to chrome_extensions_debug_after_click.png")
        except Exception as e:
            print(f"Failed to click toggle: {e}")
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
