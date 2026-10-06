import asyncio
import json
import sys
from pathlib import Path

backend_dir = str(Path(__file__).resolve().parent.parent / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import AsyncSessionLocal
from sqlalchemy import text

async def main():
    async with AsyncSessionLocal() as s:
        r = await s.execute(text("SELECT value FROM automation_settings WHERE key = 'system_settings_v4'"))
        raw = r.scalar_one_or_none()
        if raw:
            data = json.loads(raw)
            print("Portals in DB:")
            print(json.dumps(data.get("settings", {}).get("portals", {}), indent=2))

if __name__ == "__main__":
    asyncio.run(main())
