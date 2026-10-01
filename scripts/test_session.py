import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from app.automation.browser_manager import ChromeSession

async def main():
    print("Testing ChromeSession launch in Attended GUI mode...")
    session = ChromeSession(
        headless=False,
        browser_engine="chrome",
        user_data_dir=None,
        load_extension=True,
    )
    try:
        ctx = await asyncio.wait_for(session.start(), timeout=25.0)
        print("SUCCESS: Context created!")
        print("Service workers count:", len(ctx.service_workers))
        for sw in ctx.service_workers:
            print("  SW URL:", getattr(sw, "url", ""))
        print("Background pages count:", len(ctx.background_pages))
        for bg in ctx.background_pages:
            print("  BG URL:", getattr(bg, "url", ""))
        print("Session extension_loaded:", session.extension_loaded)
        print("Session extension_id:", session.extension_id)
        await asyncio.sleep(1)
        await session.close()
        print("SUCCESS: Session closed cleanly!")
    except Exception as e:
        print("ERROR launching browser:", type(e), e)
        if session:
            await session.close()

if __name__ == "__main__":
    asyncio.run(main())
