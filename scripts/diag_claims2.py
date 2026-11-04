import asyncio
import os
import sys

sys.path.insert(0, r'C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\backend')
os.chdir(r'C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\backend')
from app.core.database import TaskAsyncSessionLocal
from sqlalchemy import text


async def main():
    async with TaskAsyncSessionLocal() as db:
        result = await db.execute(text('SELECT record_status, COUNT(*) as cnt FROM claim_records GROUP BY record_status ORDER BY cnt DESC'))
        rows = result.fetchall()
        print('=== CLAIM STATUS DISTRIBUTION ===')
        for r in rows:
            print(f'  {str(r[0]):35s} {r[1]}')
        result2 = await db.execute(text("SELECT claim_number, record_status, last_error, policy_state, loss_location_state, fl_website_broward, te_website_travis FROM claim_records WHERE record_status IN ('failed','error','scraping_in_progress') LIMIT 8"))
        rows2 = result2.fetchall()
        print('=== FAILED/IN-PROGRESS SAMPLES ===')
        for r in rows2:
            print(f'  Claim={r[0]} Status={r[1]} States={r[3]}/{r[4]} fl_broward={r[5]} te_travis={r[6]}')
            if r[2]:
                print(f'    Error: {str(r[2])[:180]}')
asyncio.run(main())
