import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.browardclerk.org/Web2", wait_until="domcontentloaded")
        print("Page URL:", page.url)
        print("Page Title:", await page.title())

        # Check all links on the page
        links = await page.eval_on_selector_all("a", """elements => elements.map(el => ({
            id: el.id,
            href: el.getAttribute('href'),
            text: el.innerText.trim(),
            parent_id: el.parentElement ? el.parentElement.id : '',
            parent_class: el.parentElement ? el.parentElement.className : '',
            outerHTML: el.outerHTML.slice(0, 150)
        }))""")
        
        print("\n--- LINKS MATCHING 'CASE SEARCH' OR 'SERVICES' OR 'GLOSSARY' ---")
        for l in links:
            t = l['text'].lower()
            h = (l['href'] or '').lower()
            if 'search' in t or 'search' in h or 'premium' in h or 'glossary' in h or 'services' in h:
                print(f"TEXT: {repr(l['text']):25} | HREF: {repr(l['href']):45} | PARENT_ID: {repr(l['parent_id']):15} | PARENT_CLS: {repr(l['parent_class']):25}")

        # Check if #nameSearch exists right on https://www.browardclerk.org/Web2
        name_search = await page.query_selector("#nameSearch")
        print("\n#nameSearch exists on page?", name_search is not None)
        
        first_name_input = await page.query_selector("#firstName")
        last_name_input = await page.query_selector("#lastName")
        print("#firstName exists?", first_name_input is not None)
        print("#lastName exists?", last_name_input is not None)
        
        search_btn = await page.query_selector("#PersonSearchResults")
        print("#PersonSearchResults exists?", search_btn is not None)

        await browser.close()

asyncio.run(inspect())
