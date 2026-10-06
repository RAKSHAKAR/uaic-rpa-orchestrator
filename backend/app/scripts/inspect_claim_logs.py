import asyncio

import httpx
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.claim import ClaimRecord


async def main():
    async with AsyncSessionLocal() as session:
        claim = (await session.execute(select(ClaimRecord).where(ClaimRecord.claim_number == '100285987'))).scalars().first()
        if not claim:
            print('Claim not found')
            return
        print(f"Claim ID: {claim.id}, Retries: {claim.retry_count}")
        with httpx.Client(base_url='http://localhost:8000/api/v1', timeout=30.0) as client:
            r = client.get(f'/claims/{claim.id}/logs')
            if r.status_code == 200:
                data = r.json()
                pel = data.get('portal_execution_logs', [])
                print(f"Total portal execution logs: {len(pel)}")
                for p in pel:
                    print(f"[{p.get('timestamp')}] [{p.get('portal')}] {p.get('message')}")

if __name__ == '__main__':
    asyncio.run(main())
