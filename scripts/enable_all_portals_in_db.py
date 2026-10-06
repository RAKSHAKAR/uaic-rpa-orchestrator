import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("backend"))

from app.services.settings_service import get_system_settings_async, save_system_settings_async

async def main():
    settings = await get_system_settings_async()
    print("Previous portal settings:")
    print(f"  travis_enabled: {settings.portals.travis_enabled}")
    print(f"  dallas_enabled: {settings.portals.dallas_enabled}")
    
    settings.portals.travis_enabled = True
    settings.portals.dallas_enabled = True
    settings.portals.broward_enabled = True
    settings.portals.hillsborough_enabled = True
    settings.portals.miami_enabled = True
    settings.portals.harris_jp_enabled = True
    settings.portals.harris_cclerk_enabled = True
    settings.portals.harris_district_enabled = True
    
    saved = await save_system_settings_async(settings)
    print("\nUpdated portal settings:")
    print(f"  travis_enabled: {saved.portals.travis_enabled}")
    print(f"  dallas_enabled: {saved.portals.dallas_enabled}")
    print("All 8 portals successfully enabled in database!")

if __name__ == "__main__":
    asyncio.run(main())
