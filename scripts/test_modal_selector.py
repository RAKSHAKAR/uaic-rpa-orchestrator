import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        await page.set_content("""
        <div class="modal show" role="dialog" style="display: block;">
            <div class="modal-dialog">
                <div class="modal-content">
                    <button type="button" class="close" data-dismiss="modal">&times;</button>
                    <div class="modal-body">
                        <label class="text-primary">YOUR SEARCH CRITERIA:</label>
                        <p>Last Name: User</p>
                        <button id="messageClose" class="btn btn-primary">Close</button>
                    </div>
                </div>
            </div>
        </div>
        """)
        try:
            sel = "div.modal:has-text('YOUR SEARCH CRITERIA' i), .modal-title:has-text('YOUR SEARCH CRITERIA' i), div:has-text('YOUR SEARCH CRITERIA' i), [role='dialog']:has-text('YOUR SEARCH CRITERIA' i)"
            loc = page.locator(sel)
            print("Count with 'i':", await loc.count())
        except Exception as e:
            print("ERROR with 'i':", type(e), e)
            
        try:
            sel_no_i = "div.modal:has-text('YOUR SEARCH CRITERIA'), .modal-title:has-text('YOUR SEARCH CRITERIA'), div:has-text('YOUR SEARCH CRITERIA'), [role='dialog']:has-text('YOUR SEARCH CRITERIA')"
            loc2 = page.locator(sel_no_i)
            print("Count without 'i':", await loc2.count())
        except Exception as e:
            print("ERROR without 'i':", type(e), e)
            
        await b.close()

if __name__ == "__main__":
    asyncio.run(run())
