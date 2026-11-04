import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.automation.browser_manager import ChromeSession


async def main():
    s = ChromeSession(browser_engine="chromium", headless=True)
    try:
        ctx = await s.start()
        p = await ctx.new_page()
        print("Visiting https://hover.hillsclerk.com/ first...")
        resp = await p.goto("https://hover.hillsclerk.com/", wait_until="networkidle", timeout=45000)
        print(f"Base status: {resp.status if resp else None}")
        print(f"Title: {await p.title()}")
        await asyncio.sleep(2)
        
        # Check buttons on page
        links = await p.locator("a").evaluate_all("els => els.map(e => ({text: e.innerText, href: e.href}))")
        for l in links[:10]:
            print(f"Link: {l}")
    finally:
        await s.close()

if __name__ == "__main__":
    asyncio.run(main())
