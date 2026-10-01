import asyncio
import os
import sys

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Navigating to OCS...")
        await page.goto("https://www2.miamidadeclerk.gov/ocs", wait_until="domcontentloaded", timeout=20000)
        
        selectors = [
            "a[href*='/usermanagementservices/?hs=OCSB']",
            "a.header__nav-link[title*='Register or log in']",
            "a:has-text('Register/Login')",
            "#lnkLogin",
            "a:has-text('Welcome')",
            "a[href*='usermanagement']",
            "button:has-text('Register/Login')"
        ]
        for sel in selectors:
            cnt = await page.locator(sel).count()
            print(f"Selector {sel!r}: count={cnt}")
            if cnt > 0:
                print(f"  First visible: {await page.locator(sel).first.is_visible()}, href: {await page.locator(sel).first.get_attribute('href')}")
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
