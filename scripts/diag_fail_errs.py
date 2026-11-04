import asyncio
import os
import sys

sys.path.insert(0, r'C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\backend')
os.chdir(r'C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\backend')
from app.core.database import TaskAsyncSessionLocal
from sqlalchemy import text


async def main():
    async with TaskAsyncSessionLocal() as db:
        r = await db.execute(text("""
            SELECT claim_number, last_error, fl_website_broward, fl_website_hillsborough, fl_website_miami,
                   te_website_travis, te_website_dallas, te_website_harris, te_website_cclerk, te_website_hcdistrict,
                   policy_state, loss_location_state
            FROM claim_records WHERE record_status = 'failed' LIMIT 10
        """))
        for row in r.fetchall():
            print(f'Claim={row[0]} States={row[10]}/{row[11]}')
            print(f'  Targets: br={row[2]} hi={row[3]} mi={row[4]} tr={row[5]} da={row[6]} ha={row[7]} cc={row[8]} hd={row[9]}')
            print(f'  Error: {str(row[1] or "")[:250]}')

asyncio.run(main())
