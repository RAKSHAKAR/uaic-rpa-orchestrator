import asyncio
import shutil
import tempfile
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    repo_root = Path('.').resolve()
    ext_dir = (repo_root / 'anticaptcha-plugin_v0.83').resolve()
    meta = ext_dir / '_metadata'
    if meta.exists():
        shutil.rmtree(meta)

    async with async_playwright() as p:
        # Bundled
        ctx1 = await p.chromium.launch_persistent_context(
            user_data_dir=tempfile.mkdtemp(prefix="cmp_chrom_"),
            headless=False,
            ignore_default_args=['--disable-extensions', '--disable-component-extensions-with-background-pages'],
            args=[
                f'--disable-extensions-except={str(ext_dir)}',
                f'--load-extension={str(ext_dir)}',
                '--no-sandbox'
            ]
        )
        print('=== Bundled Chromium ===')
        print('SWs:', [sw.url for sw in ctx1.service_workers])
        print('BGs:', [bg.url for bg in ctx1.background_pages])
        await ctx1.close()

        if meta.exists():
            shutil.rmtree(meta)

        # Google Chrome
        ctx2 = await p.chromium.launch_persistent_context(
            user_data_dir=tempfile.mkdtemp(prefix="cmp_gc_"),
            executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',
            headless=False,
            ignore_default_args=['--disable-extensions', '--disable-component-extensions-with-background-pages'],
            args=[
                f'--disable-extensions-except={str(ext_dir)}',
                f'--load-extension={str(ext_dir)}',
                '--no-sandbox'
            ]
        )
        print('=== Google Chrome ===')
        print('SWs:', [sw.url for sw in ctx2.service_workers])
        print('BGs:', [bg.url for bg in ctx2.background_pages])
        page = await ctx2.new_page()
        await page.goto("chrome://extensions")
        await asyncio.sleep(2)
        js = """() => {
            const mgr = document.querySelector('extensions-manager');
            if (!mgr) return 'No mgr';
            const list = mgr.shadowRoot.querySelector('extensions-item-list');
            if (!list) return 'No list';
            const items = list.shadowRoot.querySelectorAll('extensions-item');
            return Array.from(items).map(i => ({ id: i.id, name: i.shadowRoot.querySelector('#name')?.innerText }));
        }"""
        exts = await page.evaluate(js)
        print('Google Chrome Installed Extensions in DOM:', exts)
        await page.screenshot(path='implementation_plan/Images/compare_gc_exts.png')
        await ctx2.close()

if __name__ == '__main__':
    asyncio.run(main())
