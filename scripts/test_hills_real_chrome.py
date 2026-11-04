import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.automation.browser_manager import ChromeSession


async def main():
    s = ChromeSession(
        browser_engine="chrome",
        headless=False,
    )
    try:
        ctx = await s.start()
        p = await ctx.new_page()
        print("Testing Hillsborough in real Chrome...")
        resp = await p.goto("https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab", wait_until="domcontentloaded", timeout=45000)
        print(f"Status: {resp.status if resp else None}")
        print(f"Title: {await p.title()}")
        await asyncio.sleep(4)
        print(f"URL: {p.url}")
        body = await p.inner_text("body")
        print(f"Body preview: {body[:300]!r}")
    finally:
        await s.close()

if __name__ == "__main__":
    asyncio.run(main())
