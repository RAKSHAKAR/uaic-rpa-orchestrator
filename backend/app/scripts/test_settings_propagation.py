"""Test dynamic settings persistence and propagation across Redis and Database."""

import asyncio

import httpx

from app.services.settings_service import get_system_settings_async


async def main():
    print("Testing dynamic settings propagation...")
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000/api/v1", timeout=15.0) as client:
        # 1. Fetch current settings
        res = await client.get("/settings")
        assert res.status_code == 200, f"GET /settings failed: {res.status_code} {res.text}"
        settings_data = res.json()
        print(f"1. Successfully fetched settings. Automation engine: {settings_data['automation']['browser_engine']}")

        # 2. Modify a setting and persist
        orig_delay = settings_data["automation"]["typing_delay_ms"]
        test_delay = 42 if orig_delay != 42 else 55
        settings_data["automation"]["typing_delay_ms"] = test_delay

        post_res = await client.post("/settings", json=settings_data)
        assert post_res.status_code == 200, f"POST /settings failed: {post_res.status_code} {post_res.text}"
        updated_data = post_res.json()
        assert updated_data["automation"]["typing_delay_ms"] == test_delay, f"Expected {test_delay}, got {updated_data['automation']['typing_delay_ms']}"
        print(f"2. Updated typing_delay_ms to {test_delay}. Confirmed in API response.")

        # 3. Verify downstream async service reads the exact same value from DB/Redis
        sys_settings = await get_system_settings_async()
        assert sys_settings.automation.typing_delay_ms == test_delay, f"Service mismatch: {sys_settings.automation.typing_delay_ms}"
        print(f"3. Verified get_system_settings_async() returns updated typing_delay_ms={sys_settings.automation.typing_delay_ms}.")

        # 4. Revert to original
        settings_data["automation"]["typing_delay_ms"] = orig_delay
        revert_res = await client.post("/settings", json=settings_data)
        assert revert_res.status_code == 200
        print(f"4. Successfully reverted typing_delay_ms to original ({orig_delay}).")
        print("ALL SETTINGS PROPAGATION CHECKS PASSED!")

if __name__ == "__main__":
    asyncio.run(main())
