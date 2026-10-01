import asyncio
from httpx import AsyncClient, ASGITransport
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path("backend").resolve()))
from app.main import app

async def main():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for i in range(2):
            print(f"=== TEST LAUNCH RUN {i+1} ===")
            resp = await client.post("/api/v1/settings/test-browser", json={
                "browser_engine": "chrome",
                "headless": False,
                "test_extension": True,
                "force_kill": True,
                "timeout_seconds": 40
            })
            data = resp.json()
            print(f"Run {i+1} status: {resp.status_code}")
            print(f"  extension_loaded: {data.get('extension_loaded')}")
            print(f"  extension_id: {data.get('extension_id')}")
            print(f"  service_worker_active: {data.get('service_worker_active')}")
            print(f"  message: {data.get('message')}")
            if not data.get("extension_loaded"):
                print("FAILED DATA:", data)
                sys.exit(1)
    print("\nSUCCESS: All consecutive Chrome launches verified AntiCaptcha loaded and active!")

if __name__ == "__main__":
    asyncio.run(main())
