import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto('https://www2.miamidadeclerk.gov/ocs', wait_until='domcontentloaded')
        await asyncio.sleep(2)
        party_link = page.locator("span.subitem-color[role='button']:has-text('Party Name'), span:has-text('Party Name')")
        if await party_link.count() > 0:
            await party_link.first.click()
            await asyncio.sleep(1)
        
        await page.locator('input#partyLastName').fill('User')
        await page.locator('input#partyFirstName').fill('Test')
        await page.locator('input#filingDateFrom').fill('2024-10-01')
        await page.locator('input#filingDateTo').fill('2026-10-01')
        
        # Check Formik / React state on the inputs
        state = await page.evaluate('''() => {
            const last = document.getElementById('partyLastName');
            const fiberKey = Object.keys(last).find(k => k.startsWith('__reactFiber$') || k.startsWith('__reactProps$'));
            const props = last[fiberKey]?.memoizedProps || last[fiberKey];
            return {
                domVal: last.value,
                reactValue: props?.value,
                propsKeys: Object.keys(props || {})
            };
        }''')
        print('React input state:', state, flush=True)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
