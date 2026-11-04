import asyncio
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.claim import ClaimRecord


async def main():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    columns = [
        "fl_jsonbody_broward",
        "fl_jsonbody_hillsborough",
        "fl_jsonbody_miami",
        "te_jsonbody_dallas",
        "te_jsonbody_travis",
        "te_jsonbody_harris",
        "te_jsonbody_hcdistrict",
        "te_jsonbody_cclerk"
    ]
    
    async with async_session() as session:
        for col in columns:
            print(f"\n=== {col} ===")
            # Select first claim where this column is not null
            query = select(getattr(ClaimRecord, col)).where(getattr(ClaimRecord, col).isnot(None)).limit(1)
            result = await session.execute(query)
            case_data = result.scalar_one_or_none()
            if case_data:
                # Assuming case_data is a list of cases or a dict
                print(json.dumps(case_data, indent=2))
            else:
                print("No data found in DB.")

if __name__ == "__main__":
    asyncio.run(main())
