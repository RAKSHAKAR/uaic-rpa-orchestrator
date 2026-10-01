import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("Navigating to OCS...")
            await page.goto("https://www2.miamidadeclerk.gov/ocs", wait_until="domcontentloaded", timeout=25000)
            await asyncio.sleep(2)
            
            # Click Party Name tab
            party_link = page.locator("span.subitem-color[role='button']:has-text('Party Name'), span:has-text('Party Name')")
            if await party_link.count() > 0:
                await party_link.first.click()
                await asyncio.sleep(1)
                
            # Inspect the form element in detail
            form_details = await page.evaluate('''() => {
                const form = document.querySelector('form');
                if (!form) return 'No form';
                
                // Get all attributes of the form
                const attrs = {};
                for (let i = 0; i < form.attributes.length; i++) {
                    attrs[form.attributes[i].name] = form.attributes[i].value;
                }
                
                // Check if React Formik or Hook Form is attached
                const btn = document.querySelector('button.button-green');
                const btnAttrs = {};
                if (btn) {
                    for (let i = 0; i < btn.attributes.length; i++) {
                        btnAttrs[btn.attributes[i].name] = btn.attributes[i].value;
                    }
                }
                
                return {
                    formAttrs: attrs,
                    btnAttrs: btnAttrs,
                    formAction: form.action,
                    formMethod: form.method
                };
            }''')
            print("Form details:", form_details)
            
            # Let's inspect React Fiber on the form and button
            fiber_details = await page.evaluate('''() => {
                const btn = document.querySelector('button.button-green');
                if (!btn) return 'No button';
                
                const propKey = Object.keys(btn).find(k => k.startsWith('__reactProps'));
                const fiberKey = Object.keys(btn).find(k => k.startsWith('__reactFiber'));
                
                const props = propKey ? btn[propKey] : null;
                const form = document.querySelector('form');
                const formPropKey = form ? Object.keys(form).find(k => k.startsWith('__reactProps')) : null;
                const formProps = formPropKey ? form[formPropKey] : null;
                
                return {
                    btnPropKeys: props ? Object.keys(props) : null,
                    btnOnClick: props && props.onClick ? props.onClick.toString().substring(0, 300) : null,
                    formPropKeys: formProps ? Object.keys(formProps) : null,
                    formOnSubmit: formProps && formProps.onSubmit ? formProps.onSubmit.toString().substring(0, 500) : null,
                };
            }''')
            print("Fiber details:", fiber_details)
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
