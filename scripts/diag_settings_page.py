import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        page.on("console", lambda msg: print(f"CONSOLE [{msg.type}]: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))
        page.on("requestfailed", lambda req: print(f"REQ FAILED: {req.url} - {req.failure}"))

        print("Navigating to http://localhost:3000/settings...")
        await page.goto("http://localhost:3000/settings", wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
