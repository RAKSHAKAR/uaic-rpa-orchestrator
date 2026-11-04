import asyncio
import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.automation.browser_manager import ChromeSession


async def main():
    engine = sys.argv[1] if len(sys.argv) > 1 else "chrome"
    print(f"Testing browser engine: {engine} (headless=False)...")
    session = ChromeSession(
        browser_engine=engine,
        headless=False,
        anticaptcha_api_key="28b486b8f31f74c6bf4453735815aa53",
        force_kill=True
    )
    try:
        ctx = await session.start()
        print(f"[{engine}] Context launched successfully!")
        print(f"[{engine}] extension_loaded: {session.extension_loaded}")
        print(f"[{engine}] extension_id: {session.extension_id}")
        print(f"[{engine}] service_worker_active: {session.service_worker_active}")
        print(f"[{engine}] service workers: {[getattr(sw, 'url', '') for sw in ctx.service_workers]}")
        print(f"[{engine}] background pages: {[getattr(bg, 'url', '') for bg in ctx.background_pages]}")
        
        page = await ctx.new_page()
        await page.goto("chrome://extensions", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        data = await page.evaluate("""() => {
            const manager = document.querySelector('extensions-manager');
            const list = manager ? manager.shadowRoot.querySelector('extensions-item-list') : null;
            if (!list) return 'no extensions-item-list';
            const items = list.shadowRoot.querySelectorAll('extensions-item');
            return Array.from(items).map(i => ({
                id: i.id,
                name: i.shadowRoot.querySelector('#name') ? i.shadowRoot.querySelector('#name').innerText : 'no name'
            }));
        }""")
        print(f"[{engine}] Extensions on chrome://extensions: {data}")
        await asyncio.sleep(1)
    finally:
        await session.close()
        print(f"[{engine}] Session closed.")

if __name__ == "__main__":
    asyncio.run(main())
