import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import asyncio
from app.services.settings_service import get_system_settings_async

async def main():
    s = await get_system_settings_async()
    print("chrome_user_data_dir:", repr(s.automation.chrome_user_data_dir))
    print("chrome_extension_dir:", repr(s.automation.chrome_extension_dir))
    print("browser_engine:", repr(s.automation.browser_engine))
    print("headless_mode:", repr(s.automation.headless_mode))
    print("user_agent:", repr(s.automation.user_agent))
    print("chrome_binary_path:", repr(s.automation.chrome_binary_path))
    print("anticaptcha_api_key:", repr(s.automation.anticaptcha_api_key[:5] if s.automation.anticaptcha_api_key else None))

if __name__ == "__main__":
    asyncio.run(main())
