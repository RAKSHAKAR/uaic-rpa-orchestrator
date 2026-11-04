import asyncio
import os
import sys

sys.path.insert(0, r'C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\backend')
os.chdir(r'C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\backend')
from app.services.settings_service import get_system_settings_async


async def main():
    s = await get_system_settings_async()
    a = s.automation
    p = s.portals
    print('=== AUTOMATION SETTINGS ===')
    print(f'  browser_engine: {getattr(a, "browser_engine", "NOT SET")}')
    print(f'  headless_mode: {a.headless_mode}')
    print(f'  use_chrome_browser: {a.use_chrome_browser}')
    print(f'  max_captcha_attempts: {a.max_captcha_attempts}')
    print(f'  page_timeout_seconds: {a.page_timeout_seconds}')
    print(f'  anticaptcha_api_key: {"SET" if a.anticaptcha_api_key else "NOT SET"}')
    print()
    print('=== PORTAL ENABLED STATUS ===')
    print(f'  broward: {p.broward_enabled}')
    print(f'  hillsborough: {p.hillsborough_enabled}')
    print(f'  miami: {p.miami_enabled}')
    print(f'  travis: {p.travis_enabled}')
    print(f'  dallas: {p.dallas_enabled}')
    print(f'  harris_jp: {p.harris_jp_enabled}')
    print(f'  harris_cclerk: {p.harris_cclerk_enabled}')
    print(f'  harris_district: {p.harris_district_enabled}')
    print()
    q = s.queue
    print('=== QUEUE SETTINGS ===')
    print(f'  max_concurrent_claims: {q.max_concurrent_claims}')
    print(f'  max_task_retries: {q.max_task_retries}')
    print(f'  auto_retry_failed_scrapes: {q.auto_retry_failed_scrapes}')

asyncio.run(main())
