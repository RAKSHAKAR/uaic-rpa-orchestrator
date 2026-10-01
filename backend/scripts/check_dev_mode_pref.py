import asyncio
from playwright.async_api import async_playwright
import os
import json

async def main():
    profile_dir = os.path.abspath("test_dev_mode_profile")
    
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            args=["--test-type"]
        )
        page = context.pages[0] if context.pages else await context.new_page()
        
        # 1. Open extensions page
        await page.goto("chrome://extensions", wait_until="domcontentloaded")
        await asyncio.sleep(1)
        
        # 2. Toggle Developer Mode ON
        await page.evaluate('''() => {
            const extManager = document.querySelector('extensions-manager');
            const toolbar = extManager.shadowRoot.querySelector('extensions-toolbar');
            const toggle = toolbar.shadowRoot.querySelector('#devMode');
            if (toggle && !toggle.hasAttribute('aria-pressed') || toggle.getAttribute('aria-pressed') === 'false') {
                toggle.click();
            }
        }''')
        await asyncio.sleep(2)
        
        await context.close()
        
    # 3. Read Preferences file
    pref_path = os.path.join(profile_dir, "Default", "Preferences")
    if os.path.exists(pref_path):
        with open(pref_path, "r", encoding="utf-8") as f:
            prefs = json.load(f)
            print("EXTENSIONS PREF:", json.dumps(prefs.get("extensions", {}), indent=2))
            print("PROFILE PREF:", json.dumps(prefs.get("profile", {}), indent=2))

if __name__ == "__main__":
    asyncio.run(main())
