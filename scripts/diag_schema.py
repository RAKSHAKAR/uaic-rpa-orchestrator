import asyncio
import os
import sys

sys.path.insert(0, r'C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\backend')
os.chdir(r'C:\Users\priyer\.gemini\antigravity-ide\scratch\Bot_UAIC\backend')
from app.core.database import TaskAsyncSessionLocal
from sqlalchemy import text


async def main():
    async with TaskAsyncSessionLocal() as db:
        r = await db.execute(text('SELECT * FROM claim_records LIMIT 2'))
        cols = r.keys()
        print('COLUMNS:', list(cols))
        rows = r.fetchall()
        for row in rows:
            d = dict(zip(cols, row))
            print()
            for k,v in d.items():
                if v not in (None, ''):
                    print(f'  {k}: {str(v)[:100]}')

asyncio.run(main())
