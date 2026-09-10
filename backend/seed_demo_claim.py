"""Seed a realistic representative claim record with full stage execution timings."""

import asyncio
import uuid

from app.core.database import Base, TaskAsyncSessionLocal, engine
from app.models.claim import ClaimRecord, FuzzyMatchStatusEnum, RecordStatusEnum
from app.models.court_case import ScrapedCourtCase


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    claim_id = str(uuid.uuid4())
    async with TaskAsyncSessionLocal() as session:
        # Create claim
        claim = ClaimRecord(
            id=claim_id,
            claim_number="CLM-2026-889102",
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
            loss_location_city="Miami",
            loss_location_county="Miami-Dade",
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
                "portals": {
                    "miami_dade": {
                        "portal_name": "Miami-Dade County (FL)",
                        "duration_seconds": 12.35,
                        "cases_found": 1,
                        "status": "COMPLETED",
                    },
                    "broward": {
                        "portal_name": "Broward County (FL)",
                        "duration_seconds": 3.10,
                        "cases_found": 0,
                        "status": "COMPLETED",
                    },
                    "hillsborough": {
                        "portal_name": "Hillsborough County (FL)",
                        "duration_seconds": 2.15,
                        "cases_found": 0,
                        "status": "COMPLETED",
                    }
                },
                "stages": {
                    "browser_launch": {
                        "name": "Browser Launch",
                        "start_time": "14:20:01.104",
                        "end_time": "14:20:03.824",
                        "duration_seconds": 2.72,
                        "status": "SUCCESS",
                        "detail": "Attended Google Chrome with AntiCaptcha Extension",
                    },
                    "website_navigation": {
                        "name": "Website Navigation",
                        "start_time": "14:20:03.825",
                        "end_time": "14:20:06.120",
                        "duration_seconds": 2.29,
                        "status": "SUCCESS",
                        "url": "https://www2.miamidadeclerk.gov/ocs",
                    },
                    "data_filling": {
                        "name": "Data Filling",
                        "start_time": "14:20:06.121",
                        "end_time": "14:20:07.450",
                        "duration_seconds": 1.33,
                        "status": "SUCCESS",
                        "detail": "Entered Party Name: Rodriguez, Carlos",
                    },
                    "captcha": {
                        "name": "CAPTCHA Handling",
                        "start_time": "14:20:07.451",
                        "end_time": "14:20:12.650",
                        "duration_seconds": 5.20,
                        "status": "SOLVED",
                        "solver": "AntiCaptcha Extension Plugin v0.83",
                        "retry_count": 1,
                    },
                    "submit": {
                        "name": "Search Submit",
                        "start_time": "14:20:12.651",
                        "end_time": "14:20:13.200",
                        "duration_seconds": 0.55,
                        "status": "SUCCESS",
                    },
                    "result_retrieval": {
                        "name": "Result Retrieval",
                        "start_time": "14:20:13.201",
                        "end_time": "14:20:15.820",
                        "duration_seconds": 2.62,
                        "status": "SUCCESS",
                        "result_category": "Data Found",
                        "cases_count": 1,
                    },
                    "database_save": {
                        "name": "Database Save",
                        "start_time": "14:20:15.821",
                        "end_time": "14:20:16.150",
                        "duration_seconds": 0.33,
                        "status": "SUCCESS",
                        "cases_saved": 1,
                    },
                    "guidewire_trigger": {
                        "name": "Guidewire Dispatch",
                        "start_time": "14:20:16.151",
                        "end_time": "14:20:19.554",
                        "duration_seconds": 3.40,
                        "status": "SUCCESS",
                        "detail": "Activity created: GW-ACT-98234-FL",
                    }
                }
            }
        )
        session.add(claim)

        # Scraped case
        sc = ScrapedCourtCase(
            id=str(uuid.uuid4()),
            claim_id=claim_id,
            county_name="Miami-Dade County",
            county_website="https://www2.miamidadeclerk.gov/ocs",
            case_number="2026-004821-CA-01",
            case_style="ELENA VARGAS VS CARLOS RODRIGUEZ",
            case_status="OPEN",
            filing_date="11/22/2025",
            raw_payload={"CaseNumber": "2026-004821-CA-01"}
        )
        session.add(sc)
        await session.commit()

    print(f"SEEDED_CLAIM_ID={claim_id}")

if __name__ == "__main__":
    asyncio.run(seed())
