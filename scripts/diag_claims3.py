import asyncio
import os
import sys

sys.path.insert(0, r'C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\backend')
os.chdir(r'C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\backend')
from app.core.database import TaskAsyncSessionLocal
from sqlalchemy import text


async def main():
    async with TaskAsyncSessionLocal() as db:
        # Sample failed claims with error messages
        r = await db.execute(text("""
            SELECT claim_number, record_status, last_error, policy_state, loss_location_state,
                   fl_website_broward, fl_website_hillsborough, fl_website_miami,
                   te_website_travis, te_website_dallas, te_website_harris, te_website_cclerk, te_website_hcdistrict,
                   fl_botstatus_broward, te_botstatus_travis
            FROM claim_records
            WHERE record_status = 'failed'
            LIMIT 6
        """))
        rows = r.fetchall()
        print('=== FAILED CLAIMS DETAIL ===')
        for row in rows:
            print(f'Claim={row[0]} PolicyState={row[3]} LossState={row[4]}')
            print(f'  Targets: broward={row[5]} hills={row[6]} miami={row[7]} travis={row[8]} dallas={row[9]} harris={row[10]} cclerk={row[11]} hcdistrict={row[12]}')
            print(f'  BotStatus: broward={row[13]} travis={row[14]}')
            print(f'  Error: {str(row[2] or "")[:200]}')
            print()
        
        # Check overall bot status summary
        r2 = await db.execute(text("""
            SELECT fl_botstatus_broward, COUNT(*) FROM claim_records GROUP BY fl_botstatus_broward
        """))
        print('=== BROWARD BOT STATUS ===')
        for row in r2.fetchall():
            print(f'  {row[0]}: {row[1]}')
        
        r3 = await db.execute(text("""
            SELECT te_botstatus_travis, COUNT(*) FROM claim_records GROUP BY te_botstatus_travis
        """))
        print('=== TRAVIS BOT STATUS ===')
        for row in r3.fetchall():
            print(f'  {row[0]}: {row[1]}')

asyncio.run(main())
