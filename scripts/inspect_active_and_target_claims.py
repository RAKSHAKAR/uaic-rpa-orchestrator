import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("backend"))
from app.core.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.claim import ClaimRecord, RecordStatusEnum

async def inspect():
    async with AsyncSessionLocal() as db:
        # 1. Check SCRAPING_IN_PROGRESS claims
        res = await db.execute(select(ClaimRecord).where(ClaimRecord.record_status == RecordStatusEnum.SCRAPING_IN_PROGRESS))
        active_claims = res.scalars().all()
        print(f"=== 1. Active SCRAPING_IN_PROGRESS count: {len(active_claims)} ===")
        for c in active_claims[:10]:
            print(f"Claim #{c.claim_number} ({c.id}): created_at={c.created_at}, updated_at={c.updated_at}, duration={c.total_duration_seconds}")

        # 2. Check claim 870f33f1-d4e5-49b5-9afd-13521bcf60f9
        res = await db.execute(select(ClaimRecord).where(ClaimRecord.id == "870f33f1-d4e5-49b5-9afd-13521bcf60f9"))
        claim_870 = res.scalar_one_or_none()
        print("\n=== 2. Claim 870f33f1-d4e5-49b5-9afd-13521bcf60f9 ===")
        if claim_870:
            print(f"ClaimNumber: {claim_870.claim_number}, Status: {claim_870.record_status}, FuzzyStatus: {claim_870.fuzzy_match_status}")
            print(f"Insured: {claim_870.insured_first_name} {claim_870.insured_last_name}, Claimant: {claim_870.claimant_first_name} {claim_870.claimant_last_name}")
            print(f"Cases extracted: {len(claim_870.scraped_cases) if claim_870.scraped_cases else 0}, Total duration: {claim_870.total_duration_seconds}")
            print(f"Bot statuses: FL_broward={claim_870.fl_botstatus_broward}, FL_hillsborough={claim_870.fl_botstatus_hillsborough}, FL_miami={claim_870.fl_botstatus_miami}")
            print(f"TE_cclerk={claim_870.te_botstatus_cclerk}, TE_dallas={claim_870.te_botstatus_dallas}, TE_harris={claim_870.te_botstatus_harris}, TE_hcdistrict={claim_870.te_botstatus_hcdistrict}, TE_travis={claim_870.te_botstatus_travis}")
            print(f"Guidewire activity ID: {claim_870.activity_id}")
            print(f"Scraped cases count: {len(claim_870.scraped_cases) if claim_870.scraped_cases else 0}")
            print(f"Final matched JSON: {claim_870.final_matched_json}")
            print(f"Action timings: {claim_870.action_timings}")
        else:
            print("Claim 870 not found by ID, checking by claim number if needed.")

        # 3. Check claim 28eab91e-8491-4923-8709-397ed895feb9
        res = await db.execute(select(ClaimRecord).where(ClaimRecord.id == "28eab91e-8491-4923-8709-397ed895feb9"))
        claim_28e = res.scalar_one_or_none()
        print("\n=== 3. Claim 28eab91e-8491-4923-8709-397ed895feb9 ===")
        if claim_28e:
            print(f"ClaimNumber: {claim_28e.claim_number}, Status: {claim_28e.record_status}, FuzzyStatus: {claim_28e.fuzzy_match_status}")
            print(f"PolicyState: {claim_28e.policy_state}, LossState: {claim_28e.loss_location_state}")
            print(f"Cases extracted: {len(claim_28e.scraped_cases) if claim_28e.scraped_cases else 0}, Total duration: {claim_28e.total_duration_seconds}")
            print(f"Bot statuses: FL_broward={claim_28e.fl_botstatus_broward}, FL_hillsborough={claim_28e.fl_botstatus_hillsborough}, FL_miami={claim_28e.fl_botstatus_miami}")
            print(f"TE_cclerk={claim_28e.te_botstatus_cclerk}, TE_dallas={claim_28e.te_botstatus_dallas}, TE_harris={claim_28e.te_botstatus_harris}, TE_hcdistrict={claim_28e.te_botstatus_hcdistrict}, TE_travis={claim_28e.te_botstatus_travis}")
            print(f"JSON lengths: cclerk={len(claim_28e.te_jsonbody_cclerk or '')}, dallas={len(claim_28e.te_jsonbody_dallas or '')}, harris={len(claim_28e.te_jsonbody_harris or '')}, hcdistrict={len(claim_28e.te_jsonbody_hcdistrict or '')}, travis={len(claim_28e.te_jsonbody_travis or '')}")
            # check individual case counts from JSON
            import json
            for key, name in [
                ("te_jsonbody_cclerk", "Harris Clerk"),
                ("te_jsonbody_dallas", "Dallas"),
                ("te_jsonbody_harris", "Harris JP"),
                ("te_jsonbody_hcdistrict", "Harris District"),
                ("te_jsonbody_travis", "Travis")
            ]:
                val = getattr(claim_28e, key, None)
                try:
                    parsed = json.loads(val) if val else []
                    print(f"  {name} ({key}): {len(parsed)} cases in JSON body")
                except Exception as e:
                    print(f"  {name} ({key}): error parsing JSON: {e}")
        else:
            print("Claim 28e not found by ID.")

if __name__ == "__main__":
    asyncio.run(inspect())
