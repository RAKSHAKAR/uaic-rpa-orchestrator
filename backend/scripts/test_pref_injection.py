import asyncio
import os
import json
from playwright.async_api import async_playwright

async def main():
    profile_dir = os.path.abspath("test_pref_profile2")
    os.makedirs(profile_dir, exist_ok=True)
    os.makedirs(os.path.join(profile_dir, "Default"), exist_ok=True)
    
    prefs = {
        "extensions": {
            "ui": {
                "developer_mode": True
            }
        }
    }
    with open(os.path.join(profile_dir, "Default", "Preferences"), "w") as f:
        json.dump(prefs, f)
        
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
        
        state = await page.evaluate('''() => {
            const extManager = document.querySelector('extensions-manager');
            const toolbar = extManager.shadowRoot.querySelector('extensions-toolbar');
            const toggle = toolbar.shadowRoot.querySelector('#devMode');
            return toggle ? toggle.checked : 'not found';
        }''')
        print(f"DevMode checked property after Preferences injection: {state}")
        
        await context.close()

if __name__ == "__main__":
    asyncio.run(main())
