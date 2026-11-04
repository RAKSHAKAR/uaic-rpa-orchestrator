import asyncio
import os
import sys

sys.path.insert(0, r'C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\backend')
os.chdir(r'C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\backend')
from app.core.database import TaskAsyncSessionLocal
from sqlalchemy import text


async def main():
    async with TaskAsyncSessionLocal() as db:
        # Get unique error messages in failed claims
        r = await db.execute(text("""
            SELECT last_error, COUNT(*) as cnt FROM claim_records
            WHERE record_status='failed' AND last_error IS NOT NULL
            GROUP BY last_error ORDER BY cnt DESC LIMIT 10
        """))
        print('=== UNIQUE ERROR PATTERNS ===')
        for row in r.fetchall():
            print(f'  [{row[1]}x] {str(row[0])[:250]}')
        
        # Check if ANY claim has fl/te website targets set to non-null
        r2 = await db.execute(text("""
            SELECT
                SUM(CASE WHEN fl_website_broward='Yes' THEN 1 ELSE 0 END) as br_yes,
                SUM(CASE WHEN fl_website_broward='No' THEN 1 ELSE 0 END) as br_no,
                SUM(CASE WHEN fl_website_broward IS NULL THEN 1 ELSE 0 END) as br_null,
                SUM(CASE WHEN te_website_travis='Yes' THEN 1 ELSE 0 END) as tr_yes,
                COUNT(*) as total
            FROM claim_records WHERE record_status='failed'
        """))
        row = r2.fetchone()
        print(f'Broward target: Yes={row[0]} No={row[1]} Null={row[2]}  Travis target: Yes={row[3]} Total={row[4]}')

asyncio.run(main())
