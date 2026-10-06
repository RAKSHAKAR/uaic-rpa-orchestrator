import asyncio

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.claim import ClaimRecord

claim_numbers = ['100290914', '100309189', '100301036', '100288773', '100285987']

async def inspect():
    async with AsyncSessionLocal() as session:
        for cn in claim_numbers:
            stmt = select(ClaimRecord).where(ClaimRecord.claim_number == cn)
            claim = (await session.execute(stmt)).scalars().first()
            if not claim:
                continue
            print(f"=== CLAIM #{claim.claim_number} ({claim.insured_first_name} {claim.insured_last_name} vs {claim.claimant_first_name} {claim.claimant_last_name}) ===")
            print(f"Status: {claim.record_status}, Total Duration: {claim.total_duration_seconds}s, Retries: {claim.retry_count}")
            print(f"Created: {claim.created_at}, Updated: {claim.updated_at}")
            print(f"Last Error: {claim.last_error}")
            portals = claim.action_timings.get('portals', {}) if claim.action_timings else {}
            for p_key, p_data in portals.items():
                print(f"  Portal {p_key}: status={p_data.get('status')}, cases={p_data.get('cases_found')}, duration={p_data.get('duration_seconds')}s, error={p_data.get('error')}")
            stages = (claim.action_timings or {}).get("stages", {})
            for s_key, s_data in stages.items():
                print(f"    Stage {s_key}: duration={s_data.get('duration_seconds')}s, status={s_data.get('status')}")
            print("-----------------------------------------")

if __name__ == '__main__':
    asyncio.run(inspect())
