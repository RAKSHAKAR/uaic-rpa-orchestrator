"""Capture frontend UI screenshots of the 2 demonstration claims."""

import asyncio
import os

from playwright.async_api import async_playwright

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
img_dir = os.path.abspath(os.path.join(backend_dir, "..", "implementation_plan", "Images"))
os.makedirs(img_dir, exist_ok=True)

CLAIMS = [
    {"id": "4d6e8f53-f6dc-409f-8413-a9add23d70ac", "num": "987654321"},
    {"id": "36f64fa5-a1b4-4091-9c95-b1186e1c5623", "num": "123456789"},
]


async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})

        for c in CLAIMS:
            url = f"http://localhost:3000/claims/{c['id']}"
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until="networkidle", timeout=20000)
            await page.wait_for_timeout(2000)

            out_path = os.path.join(img_dir, f"live_demo_claim_{c['num']}.png")
            await page.screenshot(path=out_path, full_page=True)
            print(f"Captured screenshot: {out_path}")

        # Also capture dashboard claims table
        dash_url = "http://localhost:3000/"
        print(f"Navigating to {dash_url}...")
        await page.goto(dash_url, wait_until="networkidle", timeout=20000)
        await page.wait_for_timeout(2000)
        dash_path = os.path.join(img_dir, "live_demo_dashboard_claims.png")
        await page.screenshot(path=dash_path, full_page=True)
        print(f"Captured dashboard screenshot: {dash_path}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(capture())
