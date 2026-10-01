import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from app.automation.browser_manager import ChromeSession

async def main():
    s = ChromeSession(headless=False, browser_engine="chrome")
    ctx = await s.start()
    page = await ctx.new_page()
    await page.goto("chrome://extensions")
    await asyncio.sleep(2)

    # Let's inspect the shadow DOM of chrome://extensions
    js_eval = """
    () => {
        const mgr = document.querySelector('extensions-manager');
        if (!mgr) return 'No extensions-manager';
        const shadow1 = mgr.shadowRoot;
        if (!shadow1) return 'No shadow1';
        const itemList = shadow1.querySelector('extensions-item-list');
        if (!itemList) return 'No itemList';
        const shadow2 = itemList.shadowRoot;
        if (!shadow2) return 'No shadow2';
        const items = shadow2.querySelectorAll('extensions-item');
        const res = [];
        items.forEach(it => {
            const sh = it.shadowRoot;
            const nameEl = sh ? sh.querySelector('#name') : null;
            const idEl = sh ? sh.querySelector('#extension-id') : null;
            res.push({
                id: it.id,
                name: nameEl ? nameEl.innerText : 'Unknown',
                extensionId: idEl ? idEl.innerText : 'No ID'
            });
        });
        return {
            itemsCount: items.length,
            extensions: res
        };
    }
    """
    res = await page.evaluate(js_eval)
    print("EXTENSIONS SHADOW DOM EVALUATION RESULT:")
    print(res)

    await page.wait_for_timeout(3000)
    await ctx.close()

if __name__ == '__main__':
    asyncio.run(main())
