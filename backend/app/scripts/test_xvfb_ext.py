import asyncio

from app.automation.browser_manager import ChromeSession


async def test():
    session = ChromeSession(headless=False, browser_engine="chromium")
    await session.start()
    print("SUCCESS: Extension loaded =", session.extension_loaded)
    print("Worker active =", session.extension_worker_active)
    await session.stop()

if __name__ == "__main__":
    asyncio.run(test())
