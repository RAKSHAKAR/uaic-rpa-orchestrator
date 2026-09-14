import asyncio
import sys
import os
import json

# Setup environment
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app.tasks.scraper_tasks import _async_orchestrate_scrapers
from app.core.database import AsyncSessionLocal
from app.models.claim import ClaimRecord

async def run():
    print("Connecting to DB...")
    async with AsyncSessionLocal() as db:
        claim = ClaimRecord(
            claim_number='TEST-E2E-123',
            insured_first_name='John',
            insured_last_name='Fletcher',
            policy_state='TX',
            te_website_travis='Yes'
        )
        db.add(claim)
        await db.commit()
        await db.refresh(claim)
        
        print(f"Created claim: {claim.id}, {claim.claim_number}")
        print("Running scraper orchestrator...")
        
        await _async_orchestrate_scrapers(claim.id)
        
        await db.refresh(claim)
        print("Done running scraper!")
        print(json.dumps(claim.action_timings, indent=2))

if __name__ == "__main__":
    asyncio.run(run())
