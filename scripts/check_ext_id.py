import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.automation.browser_manager import ChromeSession


async def main():
    s = ChromeSession(browser_engine="chromium", headless=True)
    try:
        ctx = await s.start()
        # Find service workers
        sws = ctx.service_workers
        print(f"Service workers count: {len(sws)}")
        for sw in sws:
            print(f"Worker URL: {sw.url}")
            
        # Inspect extension pages or targets
        ext_ids = set()
        for sw in sws:
            if "chrome-extension://" in sw.url:
                eid = sw.url.split("chrome-extension://")[1].split("/")[0]
                ext_ids.add(eid)
        print(f"Detected Extension IDs: {ext_ids}")
    finally:
        await s.close()

if __name__ == "__main__":
    asyncio.run(main())
