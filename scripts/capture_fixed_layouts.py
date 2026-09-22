"""Capture screenshots of the 5 routes demonstrating fixed shell layout and scrolling main container."""
import asyncio
from playwright.async_api import async_playwright

PAGES = [
    ("monitor", "http://localhost:3000/monitor", "monitor_fixed_layout.png"),
    ("health", "http://localhost:3000/health", "health_fixed_layout.png"),
    ("exceptions", "http://localhost:3000/exceptions", "exceptions_fixed_layout.png"),
    ("audit", "http://localhost:3000/audit", "audit_fixed_layout.png"),
]

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        for name, url, filename in PAGES:
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_timeout(1000)
            # Scroll main container
            await page.evaluate("const m = document.querySelector('main'); if(m) m.scrollTop = 300;")
            await page.wait_for_timeout(500)
            save_path = f"implementation_plan/Images/{filename}"
            await page.screenshot(path=save_path)
            print(f"Saved: {save_path}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
