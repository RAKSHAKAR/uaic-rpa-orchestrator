import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.automation.browser_manager import ChromeSession, ExtensionManager
from app.services.settings_service import get_system_settings_async


async def main():
    sys_settings = await get_system_settings_async()
    auto = sys_settings.automation
    ext_path = ExtensionManager.resolve_extension_path(auto.chrome_extension_dir)

    session = ChromeSession(
        headless=False,
        extension_path=ext_path,
        anticaptcha_api_key=auto.anticaptcha_api_key,
        auto_cfg=auto,
        browser_engine=auto.browser_engine,
        chrome_binary_path=auto.chrome_binary_path,
        load_extension=True,
    )
    try:
        context = await session.start()
        page = await context.new_page()
        await page.goto("https://www.browardclerk.org/Web2", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(3000)

        info = await page.evaluate("""() => {
            const col = document.querySelector('#personSearchForm .col-md-8');
            if (!col) return [];
            return Array.from(col.children).map(c => {
                const r = c.getBoundingClientRect();
                return {
                    tag: c.tagName,
                    id: c.id,
                    className: c.className,
                    width: r.width,
                    height: r.height,
                    top: r.top,
                    left: r.left,
                    text: c.innerText ? c.innerText.substring(0, 50).replace(/\\n/g, ' ') : '',
                    html_snippet: c.outerHTML.substring(0, 150)
                };
            });
        }""")
        print("Children of col-md-8:")
        for c in info:
            print(" ", c)

    finally:
        await session.close()

if __name__ == "__main__":
    asyncio.run(main())
