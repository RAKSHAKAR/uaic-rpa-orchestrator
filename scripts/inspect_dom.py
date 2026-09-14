import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto('http://localhost:3000/settings', wait_until='networkidle')
        await page.wait_for_timeout(2000)
        btn = page.locator("button:has-text('Email')").first
        await btn.click()
        await page.wait_for_timeout(1000)
        
        elements = await page.locator("text=JANE SMITH").all()
        print(f"Found {len(elements)} elements with JANE SMITH")
        for i, el in enumerate(elements):
            box = await el.bounding_box()
            tag = await el.evaluate("e => e.tagName")
            text = await el.text_content()
            parent = await el.evaluate("e => e.parentElement.className")
            print(f"El {i}: tag={tag}, box={box}, parent_class={parent[:60]}")
            
        # Check delivery history box
        hist = page.locator("#delivery-history-section")
        count = await hist.count()
        print("Count of #delivery-history-section:", count)
        if count > 0:
            box = await hist.first.bounding_box()
            print("History section box:", box)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(inspect())
