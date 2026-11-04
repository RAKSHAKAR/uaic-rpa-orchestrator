import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path("backend").resolve()))

from app.automation.browser_manager import ChromeSession


async def main():
    print("Launching ChromeSession...")
    async with ChromeSession(headless=False, browser_engine="chrome") as session:
        print("Extension loaded:", session.extension_loaded)
        print("Extension ID:", session.extension_id)
        print("SW active:", session.service_worker_active)
        print("Context service workers count:", len(session.context.service_workers))
        for sw in session.context.service_workers:
            print("  SW URL:", sw.url)
        page = await session.context.new_page()
        await page.goto("chrome://extensions")
        await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())

