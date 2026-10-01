import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("Fetching Miami OCS JS bundle...")
            await page.goto("https://www2.miamidadeclerk.gov/ocs", wait_until="domcontentloaded", timeout=25000)
            await asyncio.sleep(2)
            
            # Inspect the form and button event listeners
            listeners = await page.evaluate('''() => {
                const btn = document.querySelector('button.button-green');
                const form = document.querySelector('form');
                return {
                    btn_html: btn ? btn.outerHTML : null,
                    btn_type: btn ? btn.type : null,
                    form_html: form ? form.outerHTML.substring(0, 300) : null,
                    has_form: !!form
                };
            }''')
            print("Listeners/Form info:", listeners)
            
            # Click Party Name tab
            party_link = page.locator("span.subitem-color[role='button']:has-text('Party Name'), span:has-text('Party Name')")
            if await party_link.count() > 0:
                await party_link.first.click()
                await asyncio.sleep(1)
                
            # Inspect Formik / React props on the form
            react_info = await page.evaluate('''() => {
                const form = document.querySelector('form');
                if (!form) return 'no form';
                const keys = Object.keys(form);
                const reactKey = keys.find(k => k.startsWith('__reactFiber') || k.startsWith('__reactInternalInstance') || k.startsWith('__reactProps'));
                const btn = document.querySelector('button.button-green');
                const btnKeys = btn ? Object.keys(btn) : [];
                const btnReactKey = btnKeys.find(k => k.startsWith('__reactFiber') || k.startsWith('__reactProps'));
                
                return {
                    form_react: reactKey,
                    btn_react: btnReactKey,
                    btn_onclick: typeof btn?.onclick,
                    form_onsubmit: typeof form?.onsubmit
                };
            }''')
            print("React info:", react_info)
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
