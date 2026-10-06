import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("backend"))

from app.tasks.fuzzy_tasks import _async_evaluate_fuzzy_matches
from app.core.database import AsyncSessionLocal
from app.models.claim import ClaimRecord

async def main():
    claim_id = "870f33f1-d4e5-49b5-9afd-13521bcf60f9"
    print(f"Triggering RapidFuzz evaluation for Claim {claim_id}...")
    await _async_evaluate_fuzzy_matches(claim_id)
    
    async with AsyncSessionLocal() as session:
        claim = await session.get(ClaimRecord, claim_id)
        if claim:
            print(f"Claim #{claim.claim_number} evaluation finished:")
            print(f"  Record Status: {claim.record_status}")
            print(f"  Fuzzy Match Status: {claim.fuzzy_match_status}")
            print(f"  Total Duration: {claim.total_duration_seconds}")
            print(f"  Guidewire Activity ID: {claim.activity_id}")
            print(f"  Final Matched JSON: {claim.final_matched_json}")

if __name__ == "__main__":
    asyncio.run(main())
