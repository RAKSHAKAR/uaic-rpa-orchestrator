import asyncio
from pathlib import Path

from playwright.async_api import async_playwright


async def capture():
    docs_dir = Path("docs").resolve()
    docs_dir.mkdir(exist_ok=True)
    dashboard_png = docs_dir / "2026-10-11_uaic_32_errors_fixed_dashboard.png"
    monitor_png = docs_dir / "2026-10-11_uaic_32_errors_fixed_monitor.png"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        print("Navigating to http://localhost:3000/ ...")
        await page.goto("http://localhost:3000/", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path=str(dashboard_png), full_page=True)
        print(f"Captured dashboard screenshot: {dashboard_png}")

        print("Navigating to http://localhost:3000/monitor ...")
        await page.goto("http://localhost:3000/monitor", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path=str(monitor_png), full_page=True)
        print(f"Captured monitor screenshot: {monitor_png}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture())
