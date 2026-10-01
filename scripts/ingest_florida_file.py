import asyncio
import os
import sys
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.database import AsyncSessionLocal
from app.models.claim import IngestionBatch, ClaimRecord
from app.tasks.ingest_tasks import _async_parse_and_ingest
from sqlalchemy import select

async def main():
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Testing files", "sample_claims - Florida.xlsx"))
    print(f"Reading: {file_path}")
    if not os.path.exists(file_path):
        print("File does not exist!")
        return

    batch_id = str(uuid.uuid4())
    async with AsyncSessionLocal() as session:
        # First remove any old records with duplicate strategy OVERWRITE
        batch = IngestionBatch(
            id=batch_id,
            filename="sample_claims - Florida.xlsx",
            status="PROCESSING",
            total_records=0,
            processed_records=0,
            failed_records=0,
            duplicate_records=0,
            invalid_records=0,
        )
        session.add(batch)
        await session.commit()

    print(f"Created IngestionBatch {batch_id}. Parsing and ingesting...")
    await _async_parse_and_ingest(
        batch_id=batch_id,
        file_path=file_path,
        duplicate_strategy="OVERWRITE",
    )

    async with AsyncSessionLocal() as session:
        res = await session.execute(select(ClaimRecord).where(ClaimRecord.batch_id == batch_id))
        claims = res.scalars().all()
        print(f"Successfully ingested {len(claims)} Florida claims:")
        for c in claims:
            print(f"  Claim #{c.claim_number} | {c.insured_first_name} {c.insured_last_name} vs {c.claimant_first_name} {c.claimant_last_name} | Status: {c.record_status}")

if __name__ == "__main__":
    asyncio.run(main())
