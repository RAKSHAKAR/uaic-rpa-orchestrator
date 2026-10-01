import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        await page.set_content("<div><h1>Search Results</h1><p>Party Name:</p></div>")
        try:
            loc = page.locator(":has-text('Search Results'), :has-text('Party Name:'), #tblResults")
            print("New selector count:", await loc.count())
        except Exception as e:
            print("CRASHED WITH ERROR:", type(e), e)
        await b.close()

if __name__ == "__main__":
    asyncio.run(run())
