import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.automation.browser_manager import ChromeSession


async def main():
    s = ChromeSession(browser_engine="chromium", headless=True)
    try:
        ctx = await s.start()
        
        # Test 1: Hillsborough
        p1 = await ctx.new_page()
        print("Navigating to Hillsborough direct URL...")
        try:
            resp1 = await p1.goto("https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab", wait_until="domcontentloaded", timeout=45000)
            status1 = resp1.status if resp1 else "None"
            title1 = await p1.title()
            print(f"Hillsborough direct: status={status1}, title='{title1}', url='{p1.url}'")
            body1 = await p1.inner_text("body")
            print(f"Hillsborough direct body preview: {body1[:200]!r}")
        except Exception as e:
            print(f"Hillsborough direct error: {e}")

        # Test 1b: Hillsborough base URL
        print("\nNavigating to Hillsborough base URL...")
        try:
            resp1b = await p1.goto("https://hover.hillsclerk.com/", wait_until="domcontentloaded", timeout=45000)
            status1b = resp1b.status if resp1b else "None"
            title1b = await p1.title()
            print(f"Hillsborough base: status={status1b}, title='{title1b}', url='{p1.url}'")
        except Exception as e:
            print(f"Hillsborough base error: {e}")

        # Test 2: Travis
        p2 = await ctx.new_page()
        print("\nNavigating to Travis County URL...")
        try:
            resp2 = await p2.goto("https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29", wait_until="domcontentloaded", timeout=45000)
            status2 = resp2.status if resp2 else "None"
            title2 = await p2.title()
            print(f"Travis direct: status={status2}, title='{title2}', url='{p2.url}'")
            body2 = await p2.inner_text("body")
            print(f"Travis direct body preview: {body2[:200]!r}")
        except Exception as e:
            print(f"Travis direct error: {e}")

        # Test 2b: Travis base URL
        print("\nNavigating to Travis base URL...")
        try:
            resp2b = await p2.goto("https://odysseyweb.traviscountytx.gov/Portal/", wait_until="domcontentloaded", timeout=45000)
            status2b = resp2b.status if resp2b else "None"
            title2b = await p2.title()
            print(f"Travis base: status={status2b}, title='{title2b}', url='{p2.url}'")
        except Exception as e:
            print(f"Travis base error: {e}")

    finally:
        await s.close()

if __name__ == "__main__":
    asyncio.run(main())
