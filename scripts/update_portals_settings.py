import asyncio
import json
import sys
from pathlib import Path

backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.settings_service import get_system_settings_async, save_system_settings_async
from app.schemas.settings import SettingsUpdateRequest

async def main():
    current = await get_system_settings_async()
    portals_dict = current.portals.model_dump()
    print("Previous Dallas enabled:", portals_dict.get("dallas_enabled"))
    print("Previous Travis enabled:", portals_dict.get("travis_enabled"))
    
    portals_dict["dallas_enabled"] = False
    portals_dict["travis_enabled"] = False
    
    update_dict = current.model_dump()
    update_dict["portals"] = portals_dict
    payload = SettingsUpdateRequest.model_validate(update_dict)
    
    updated = await save_system_settings_async(payload)
    print("Updated Dallas enabled:", updated.portals.dallas_enabled)
    print("Updated Travis enabled:", updated.portals.travis_enabled)
    print("Settings updated and synchronized successfully!")

if __name__ == "__main__":
    asyncio.run(main())
