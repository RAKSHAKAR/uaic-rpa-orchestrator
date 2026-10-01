import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.automation.session_runner import SingleSessionBrowserRunner  # noqa: E402
from app.services.settings_service import get_system_settings_async  # noqa: E402


async def main():
    settings = await get_system_settings_async()
    auto_cfg = settings.automation

    print("Testing SingleSessionBrowserRunner in Attended Mode (Visible GUI)...")
    runner = SingleSessionBrowserRunner(
        headless=False,
        use_chrome=True,
        extension_dir=auto_cfg.chrome_extension_dir,
        anticaptcha_api_key=auto_cfg.anticaptcha_api_key,
        anticaptcha_settings=auto_cfg,
        user_data_dir=auto_cfg.chrome_user_data_dir,
        browser_engine="chrome",
    )

    async with runner:
        print("SingleSessionBrowserRunner launched in Attended Mode!")
        print(f"Profile used: {runner.profile_to_use}")
        print(f"Is temp profile: {runner.is_temp_profile}")
        print("Stage timings:")
        for k, v in runner.stage_timings.items():
            print(f"  {k}: {v}")

    print("Attended Runner closed successfully and master profile preserved!")

if __name__ == "__main__":
    asyncio.run(main())
