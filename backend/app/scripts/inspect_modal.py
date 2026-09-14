import asyncio

from playwright.async_api import async_playwright


async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1600, "height": 1000})
        await page.goto("http://localhost:3000/settings", wait_until="load")
        
        email_btn = page.locator("button:has-text('Email & Notifications')").first
        await email_btn.wait_for(state="visible", timeout=20000)
        await email_btn.click()
        await page.wait_for_timeout(1000)
        
        await page.locator("table tbody tr").first.wait_for(state="visible", timeout=10000)
        btns = page.locator("button:has-text('View Receipt')")
        await btns.nth(1).click()
        await page.wait_for_timeout(500)
        
        modal_overlay = page.locator("div.fixed.inset-0").first
        box = await modal_overlay.bounding_box()
        print("Modal overlay bounding box:", box)
        
        info = await page.evaluate('''() => {
            const el = document.querySelector('div.fixed.inset-0');
            let curr = el ? el.parentElement : null;
            const chain = [];
            while (curr && curr !== document.body) {
                const style = window.getComputedStyle(curr);
                chain.push({
                    tag: curr.tagName,
                    id: curr.id,
                    className: curr.className,
                    transform: style.transform,
                    filter: style.filter,
                    contain: style.contain,
                    perspective: style.perspective,
                    backdropFilter: style.backdropFilter,
                    position: style.position,
                });
                curr = curr.parentElement;
            }
            return { chain };
        }''')
        for item in info['chain']:
            if item['transform'] != 'none' or item['filter'] != 'none' or item['contain'] != 'none' or item['backdropFilter'] != 'none':
                print('CONTAINING BLOCK PARENT:', item)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect())
