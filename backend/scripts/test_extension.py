import asyncio
import logging
from pathlib import Path
from app.automation.session_runner import SingleSessionBrowserRunner

logging.basicConfig(level=logging.INFO)

async def main():
    runner = SingleSessionBrowserRunner(
        headless=False,
        use_chrome=True,
    )
    async with runner as session:
        print("Extension loaded:", session.extension_loaded)
        print("Extension ID:", session.extension_id)
        print("Service worker active:", session.service_worker_active)

if __name__ == "__main__":
    asyncio.run(main())
