import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.automation.browser_manager import ChromeSession
from app.services.settings_service import get_system_settings_async


async def check():
    s = await get_system_settings_async()
    print("settings.chrome_user_data_dir:", s.chrome_user_data_dir)
    print("settings.browser_engine:", s.browser_engine)
    print("settings.use_chrome_browser:", s.use_chrome_browser)
    prof = ChromeSession.get_persistent_profile_dir(s.browser_engine)
    print("get_persistent_profile_dir:", prof)
    if s.chrome_user_data_dir:
        print("s.chrome_user_data_dir exists:", os.path.exists(s.chrome_user_data_dir))
    if prof:
        print("prof exists:", prof.exists())
        default_pref = prof / "Default" / "Preferences"
        print("default_pref exists:", default_pref.exists())
        root_pref = prof / "Preferences"
        print("root_pref exists:", root_pref.exists())

if __name__ == "__main__":
    asyncio.run(check())
