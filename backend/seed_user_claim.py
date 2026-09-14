"""Seed the exact claim ID 0304eac4-37bb-4d69-91e8-15c6b5f94941 requested by the user."""

import asyncio
import uuid
from datetime import datetime, UTC
from sqlalchemy import select
from app.core.database import Base, TaskAsyncSessionLocal, engine
from app.models.claim import ClaimRecord, FuzzyMatchStatusEnum, RecordStatusEnum
from app.models.court_case import ScrapedCourtCase
from app.models.match_result import MatchPair, MatchReviewStatusEnum, PartyTypeEnum

TARGET_CLAIM_ID = "0304eac4-37bb-4d69-91e8-15c6b5f94941"

async def seed_user_claim():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TaskAsyncSessionLocal() as session:
        # Check if already exists
        existing = await session.get(ClaimRecord, TARGET_CLAIM_ID)
        if existing:
            print(f"Claim {TARGET_CLAIM_ID} already exists: {existing.claim_number}")
            return

        claim = ClaimRecord(
            id=TARGET_CLAIM_ID,
            primary_key="PK-904128",
            claim_number="CLM-2026-904128",
            exposure_number="1",
            insured_first_name="Carlos",
            insured_last_name="Rodriguez",
            claimant_first_name="Elena",
            claimant_last_name="Vargas",
            driver_first_name="Carlos",
            driver_last_name="Rodriguez",
            dol="11/20/2025",
            policy_state="Florida",
            loss_location_state="Florida",
            record_status=RecordStatusEnum.MATCH_FOUND,
            fuzzy_match_status=FuzzyMatchStatusEnum.COMPLETED,
            fl_website_miami="Yes",
            fl_botstatus_miami="COMPLETED",
            fl_jsonbody_miami=[{"CaseNumber": "2026-004821-CA-01", "CaseStyle": "ELENA VARGAS VS CARLOS RODRIGUEZ"}],
            fl_website_broward="Yes",
            fl_botstatus_broward="COMPLETED",
            fl_jsonbody_broward=[],
            fl_website_hillsborough="Yes",
            fl_botstatus_hillsborough="COMPLETED",
            fl_jsonbody_hillsborough=[],
            te_website_travis="No",
            te_botstatus_travis="NOT_TRIGGERED",
            te_website_dallas="No",
            te_botstatus_dallas="NOT_TRIGGERED",
            te_website_harris="No",
            te_botstatus_harris="NOT_TRIGGERED",
            te_website_cclerk="No",
            te_botstatus_cclerk="NOT_TRIGGERED",
            te_website_hcdistrict="No",
            te_botstatus_hcdistrict="NOT_TRIGGERED",
            activity_id="GW-ACT-98234-FL",
            total_duration_seconds=18.45,
            action_timings={
                "total_execution_seconds": 18.45,
                "total_scraping_seconds": 18.45,
                "portals": {
                    "miami_dade": {
                        "portal_name": "Miami-Dade County (FL)",
                        "url": "https://www2.miamidadeclerk.gov/ocs",
                        "status": "COMPLETED",
                        "duration_seconds": 12.35,
                        "cases_found": 1,
                        "stages": {
                            "browser_launch": {"name": "Browser Launch", "duration_seconds": 2.72, "status": "SUCCESS", "detail": "Attended Google Chrome with AntiCaptcha Extension"},
                            "website_navigation": {"name": "Website Navigation", "duration_seconds": 2.29, "status": "SUCCESS", "url": "https://www2.miamidadeclerk.gov/ocs"},
                            "data_filling": {"name": "Data Entry", "duration_seconds": 1.33, "status": "SUCCESS", "detail": "Entered Party Name: ELENA VARGAS, DOL: 11/20/2025"},
                            "captcha": {"name": "CAPTCHA Defense", "duration_seconds": 5.2, "status": "SOLVED", "detail": "AntiCaptcha Extension Token Injection"},
                            "submit": {"name": "Search Submit", "duration_seconds": 0.55, "status": "SUCCESS", "detail": "Search button clicked"},
                            "result_retrieval": {"name": "Result Retrieval", "duration_seconds": 2.62, "status": "SUCCESS", "cases_count": 1},
                            "database_save": {"name": "Database Commit", "duration_seconds": 0.33, "status": "SUCCESS", "records_written": 1},
                            "fuzzy_matching": {"name": "RapidFuzz Matcher Engine", "duration_seconds": 0.05, "status": "COMPLETED", "detail": "High-confidence token sort match confirmed (Score: 94%)"},
                            "guidewire_trigger": {"name": "Guidewire 2-Way API Sync", "duration_seconds": 3.40, "status": "SUCCESS", "detail": "Activity GW-ACT-98234-FL created in ClaimCenter"},
                        }
                    },
                    "broward": {
                        "portal_name": "Broward County (FL)",
                        "url": "https://www.browardclerk.org/Web2",
                        "status": "COMPLETED",
                        "duration_seconds": 3.1,
                        "cases_found": 0,
                    },
                    "hillsborough": {
                        "portal_name": "Hillsborough County (FL)",
                        "url": "https://hover.hillsclerk.com",
                        "status": "COMPLETED",
                        "duration_seconds": 2.15,
                        "cases_found": 0,
                    }
                },
                "stages": {
                    "browser_launch": {"name": "Browser Launch", "duration_seconds": 2.72, "status": "SUCCESS", "start_time": "14:20:01.104", "end_time": "14:20:03.824", "detail": "Attended Google Chrome with AntiCaptcha Extension"},
                    "website_navigation": {"name": "Website Navigation", "duration_seconds": 2.29, "status": "SUCCESS", "start_time": "14:20:03.825", "end_time": "14:20:06.120", "url": "https://www2.miamidadeclerk.gov/ocs"},
                    "data_filling": {"name": "Data Entry", "duration_seconds": 1.33, "status": "SUCCESS", "start_time": "14:20:06.121", "end_time": "14:20:07.450", "detail": "Entered Party Name: ELENA VARGAS, DOL: 11/20/2025"},
                    "captcha": {"name": "CAPTCHA Defense", "duration_seconds": 5.2, "status": "SOLVED", "start_time": "14:20:07.451", "end_time": "14:20:12.650", "detail": "AntiCaptcha Extension Token Injection"},
                    "submit": {"name": "Search Submit", "duration_seconds": 0.55, "status": "SUCCESS", "start_time": "14:20:12.651", "end_time": "14:20:13.200", "detail": "Search button clicked"},
                    "result_retrieval": {"name": "Result Retrieval", "duration_seconds": 2.62, "status": "SUCCESS", "start_time": "14:20:13.201", "end_time": "14:20:15.820", "cases_count": 1},
                    "database_save": {"name": "Database Commit", "duration_seconds": 0.33, "status": "SUCCESS", "start_time": "14:20:15.821", "end_time": "14:20:16.150", "records_written": 1},
                    "fuzzy_matching": {"name": "RapidFuzz Matcher Engine", "duration_seconds": 0.05, "status": "COMPLETED", "start_time": "14:20:16.151", "end_time": "14:20:16.200", "detail": "High-confidence token sort match confirmed (Score: 94%)"},
                    "guidewire_trigger": {"name": "Guidewire 2-Way API Sync", "duration_seconds": 3.40, "status": "SUCCESS", "start_time": "14:20:16.201", "end_time": "14:20:19.600", "detail": "Activity GW-ACT-98234-FL created in ClaimCenter"},
                }
            }
        )
        session.add(claim)
        await session.flush()

        case_id = str(uuid.uuid4())
        court_case = ScrapedCourtCase(
            id=case_id,
            claim_id=claim.id,
            case_number="2026-004821-CA-01",
            case_style="ELENA VARGAS VS CARLOS RODRIGUEZ",
            county_name="Miami-Dade County",
            county_website="https://www2.miamidadeclerk.gov/ocs",
            filing_date="2025-11-22",
            case_status="OPEN",
            case_type="CIVIL",
            raw_payload={"CaseNumber": "2026-004821-CA-01", "CaseStyle": "ELENA VARGAS VS CARLOS RODRIGUEZ", "County": "Miami-Dade"},
        )
        session.add(court_case)

        match_pair = MatchPair(
            id=str(uuid.uuid4()),
            claim_id=claim.id,
            court_case_id=case_id,
            party_type=PartyTypeEnum.CLAIMANT,
            party_name="Elena Vargas",
            case_style="ELENA VARGAS VS CARLOS RODRIGUEZ",
            similarity_score=94.0,
            threshold_applied=60.0,
            is_match=True,
            review_status=MatchReviewStatusEnum.AUTO_MATCHED,
            review_notes="High-confidence token sort match against Claimant Name and DOL correlation.",
        )
        session.add(match_pair)

        await session.commit()
        print(f"Successfully seeded target claim: {TARGET_CLAIM_ID}")

if __name__ == "__main__":
    asyncio.run(seed_user_claim())
