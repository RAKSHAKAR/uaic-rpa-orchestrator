import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            print("Navigating to Broward...")
            await page.goto("https://www.browardclerk.org/Web2", wait_until="domcontentloaded", timeout=30000)
            print("Successfully navigated!")
            content = await page.content()
            print(f"Content length: {len(content)}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
