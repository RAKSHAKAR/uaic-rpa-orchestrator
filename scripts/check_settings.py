import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.services.settings_service import get_system_settings_async


async def check():
    s = await get_system_settings_async()
    print("browser_engine:", s.automation.browser_engine)
    print("use_chrome_browser:", s.automation.use_chrome_browser)
    print("headless_mode:", s.automation.headless_mode)
    print("anticaptcha_api_key:", (s.automation.anticaptcha_api_key[:6] + "...") if s.automation.anticaptcha_api_key else "None")
    print("chrome_binary_path:", s.automation.chrome_binary_path)

if __name__ == "__main__":
    asyncio.run(check())
