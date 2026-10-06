"""Reproduce and verify system settings save behavior."""

import asyncio
import importlib
import sys
import traceback
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Dynamic import to support standalone execution outside backend and prevent static path resolution errors
settings_module = importlib.import_module("app.services.settings_service")
get_system_settings_async = settings_module.get_system_settings_async
save_system_settings_async = settings_module.save_system_settings_async


async def test_save() -> None:
    """Load and re-save system settings to test database lock resilience."""
    try:
        current = await get_system_settings_async()
        print(f"Loaded settings version: {current.version}")
        saved = await save_system_settings_async(current)
        print(f"Saved successfully! New version: {saved.version}")
    except Exception:  # noqa: BLE001
        print("ERROR saving settings:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_save())
