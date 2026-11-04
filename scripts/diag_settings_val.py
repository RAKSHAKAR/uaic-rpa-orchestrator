import asyncio
import sys

sys.path.insert(0, "backend")

from app.core.database import TaskAsyncSessionLocal
from app.models.guidewire import AutomationSetting
from app.schemas.settings import SystemSettings
from sqlalchemy import select


async def check():
    async with TaskAsyncSessionLocal() as session:
        res = await session.execute(
            select(AutomationSetting).filter(AutomationSetting.key == "system_settings_v4")
        )
        row = res.scalar_one_or_none()
        if row:
            doc = row.value.get("settings", row.value)
            try:
                SystemSettings.model_validate(doc)
                print("Validation succeeded!")
            except Exception:
                import traceback
                traceback.print_exc()

asyncio.run(check())

