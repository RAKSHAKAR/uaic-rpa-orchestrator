import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        page.on("console", lambda msg: print(f"[CONSOLE {msg.type}] {msg.text}"))
        page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))
        page.on("response", lambda resp: print(f"[HTTP {resp.status}] {resp.url}") if resp.status >= 400 else None)

        print("Navigating...")
        response = await page.goto("http://localhost:3000/settings")
        print(f"HTTP Status: {response.status}")
        await page.wait_for_timeout(3000)

        # Check title and body text snippet
        title = await page.title()
        print(f"Page Title: {title}")
        body_text = await page.inner_text("body")
        print("Body preview (first 400 chars):")
        print(body_text[:400])

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
