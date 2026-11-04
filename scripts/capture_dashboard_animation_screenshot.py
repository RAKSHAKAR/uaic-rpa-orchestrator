import asyncio
import os
from playwright.async_api import async_playwright

async def capture():
    os.makedirs("docs/images", exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # 1. Light Mode
        context = await browser.new_context(viewport={"width": 1440, "height": 1050})
        page = await context.new_page()
        try:
            await page.goto("http://localhost:3000/", wait_until="networkidle", timeout=15000)
        except Exception:
            await page.goto("http://localhost:3000/", timeout=15000)
        
        # Wait 1.5 seconds for all count-up and sweep animations to complete
        await asyncio.sleep(1.5)
        await page.screenshot(path="docs/images/dashboard_animated_light.png", full_page=False)
        print("Captured docs/images/dashboard_animated_light.png")

        # 2. Dark Mode
        await page.evaluate("() => { document.documentElement.classList.add('dark'); document.documentElement.setAttribute('data-theme', 'dark'); }")
        await asyncio.sleep(0.5)
        await page.screenshot(path="docs/images/dashboard_animated_dark.png", full_page=False)
        print("Captured docs/images/dashboard_animated_dark.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture())
