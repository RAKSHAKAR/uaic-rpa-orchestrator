import asyncio
import os
import sys

sys.path.insert(0, 'backend')
os.chdir('backend')

from app.core.database import TaskAsyncSessionLocal
from sqlalchemy import text


async def main():
    async with TaskAsyncSessionLocal() as db:
        result = await db.execute(text("SELECT record_status, COUNT(*) as cnt FROM claim_records GROUP BY record_status ORDER BY cnt DESC"))
        rows = result.fetchall()
        for r in rows:
            print(f'Status: {str(r[0]):35s} Count: {r[1]}')
        result2 = await db.execute(text("SELECT claim_number, record_status, last_error, policy_state, loss_location_state FROM claim_records WHERE record_status IN ('failed','error') LIMIT 5"))
        rows2 = result2.fetchall()
        print('---FAILED SAMPLES---')
        for r in rows2:
            print(f'  Claim={r[0]} Status={r[1]} States={r[3]}/{r[4]} Err={str(r[2] or '')[:150]}')
asyncio.run(main())
