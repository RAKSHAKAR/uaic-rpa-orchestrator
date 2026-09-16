import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.settings_service import get_system_settings_async, save_system_settings_async


async def main():
    s = await get_system_settings_async()
    s.automation.max_concurrent_claims = 1
    s.queue.max_concurrent_claims = 1
    await save_system_settings_async(s)
    s2 = await get_system_settings_async()
    print(f"Confirmed Automation Fleet: {s2.automation.max_concurrent_claims}")
    print(f"Confirmed Queue Fleet: {s2.queue.max_concurrent_claims}")

if __name__ == "__main__":
    asyncio.run(main())
