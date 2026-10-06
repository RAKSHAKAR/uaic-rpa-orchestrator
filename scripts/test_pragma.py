import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL)

@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    print(f"Connected: {type(dbapi_connection)}")
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA busy_timeout=60000;")
    cursor.close()

async def test():
    async with engine.connect() as conn:
        res1 = await conn.execute(text("PRAGMA journal_mode;"))
        res2 = await conn.execute(text("PRAGMA busy_timeout;"))
        print("Journal mode:", res1.scalar())
        print("Busy timeout:", res2.scalar())

asyncio.run(test())
