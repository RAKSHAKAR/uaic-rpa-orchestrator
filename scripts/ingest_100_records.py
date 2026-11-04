"""Execute supported ingestion of UAIC_100_RECORD_CROSS_STATE_TEST_DATA.xlsx into backend/orchestrator.db."""

import asyncio
from datetime import datetime
import hashlib
import os
import sys

# Ensure backend path
sys.path.insert(0, os.path.abspath("backend"))

from sqlalchemy import func, select
from app.compat import utc_now
from app.core.database import TaskAsyncSessionLocal
from app.models.claim import ClaimRecord, IngestionBatch, RecordStatusEnum
from app.tasks.ingest_tasks import _async_parse_and_ingest

FILE_PATH = "UAIC_100_RECORD_CROSS_STATE_TEST_DATA.xlsx"
BATCH_ID = "BATCH-2026-1103-XSTATE-001"


async def main():
    abs_path = os.path.abspath(FILE_PATH)
    assert os.path.exists(abs_path), f"File not found: {abs_path}"

    with open(abs_path, "rb") as f:
        file_bytes = f.read()
        sha256 = hashlib.sha256(file_bytes).hexdigest()

    upload_timestamp = datetime.now().isoformat()

    # Step 1: Create IngestionBatch record in database
    async with TaskAsyncSessionLocal() as session:
        # Check if batch exists already
        existing_batch = await session.get(IngestionBatch, BATCH_ID)
        if not existing_batch:
            batch = IngestionBatch(
                id=BATCH_ID,
                filename=os.path.basename(FILE_PATH),
                status="PROCESSING",
                total_records=100,
                processed_records=0,
                failed_records=0,
                duplicate_records=0,
                invalid_records=0,
                created_at=utc_now(),
            )
            session.add(batch)
            await session.commit()
            print(f"Created IngestionBatch record: {BATCH_ID}")
        else:
            print(f"IngestionBatch record already exists: {BATCH_ID}")

    # Step 2: Run application ingestion workflow
    print(
        f"Executing _async_parse_and_ingest for {FILE_PATH} into orchestrator.db..."
    )
    await _async_parse_and_ingest(
        batch_id=BATCH_ID, file_path=abs_path, duplicate_strategy="OVERWRITE"
    )

    # Step 3: Verify results in database
    async with TaskAsyncSessionLocal() as session:
        batch_res = await session.execute(
            select(IngestionBatch).where(IngestionBatch.id == BATCH_ID)
        )
        batch = batch_res.scalar_one_or_none()

        claims_count_res = await session.execute(
            select(func.count(ClaimRecord.id)).where(
                ClaimRecord.batch_id == BATCH_ID
            )
        )
        total_claims_in_batch = claims_count_res.scalar_one()

        new_status_count_res = await session.execute(
            select(func.count(ClaimRecord.id))
            .where(ClaimRecord.batch_id == BATCH_ID)
            .where(ClaimRecord.record_status == RecordStatusEnum.NEW)
        )
        new_status_count = new_status_count_res.scalar_one()

        # Check cross-state target counts
        xstate_targets_res = await session.execute(
            select(func.count(ClaimRecord.id))
            .where(ClaimRecord.batch_id == BATCH_ID)
            .where(ClaimRecord.fl_website_broward == "Yes")
            .where(ClaimRecord.fl_website_hillsborough == "Yes")
            .where(ClaimRecord.fl_website_miami == "Yes")
            .where(ClaimRecord.te_website_travis == "Yes")
            .where(ClaimRecord.te_website_dallas == "Yes")
            .where(ClaimRecord.te_website_harris == "Yes")
            .where(ClaimRecord.te_website_cclerk == "Yes")
            .where(ClaimRecord.te_website_hcdistrict == "Yes")
        )
        all_8_targeted_count = xstate_targets_res.scalar_one()

    print("\n" + "=" * 65)
    print("UAIC APPLICATION INGESTION VERIFICATION REPORT")
    print("=" * 65)
    print(f"Source File:                    {os.path.basename(FILE_PATH)}")
    print(f"File SHA-256 Checksum:          {sha256}")
    print(f"Upload Timestamp:               {upload_timestamp}")
    print(f"Batch Identifier:               {BATCH_ID}")
    print(f"Batch Status:                   {batch.status if batch else 'N/A'}")
    print("-" * 65)
    print(f"Total Rows Ingested:            {batch.total_records}")
    print(f"Processed / Created Records:    {batch.processed_records}")
    print(f"Duplicate Rows Handled:         {batch.duplicate_records}")
    print(f"Invalid Rows Rejected:          {batch.invalid_records}")
    print(f"Total Claims in Database:       {total_claims_in_batch}")
    print(f"Claims with Status = NEW:       {new_status_count}")
    print(f"Claims with All 8 Bots Targeted:{all_8_targeted_count}")
    print("=" * 65)

    assert (
        total_claims_in_batch == 100
    ), f"Expected 100 claims, got {total_claims_in_batch}"
    assert (
        all_8_targeted_count == 100
    ), f"Expected 100 cross-state claims, got {all_8_targeted_count}"
    print("Ingestion verification SUCCESS: 100% compliant with Cross-State 8-Bot Orchestration.\n")


if __name__ == "__main__":
    asyncio.run(main())

