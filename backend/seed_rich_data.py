"""Seed rich realistic data for all target claims, court cases, and fuzzy match exceptions."""

import asyncio
import uuid
from datetime import UTC, datetime
from app.core.database import Base, TaskAsyncSessionLocal, engine
from app.models.claim import ClaimRecord, FuzzyMatchStatusEnum, RecordStatusEnum
from app.models.court_case import ScrapedCourtCase
from app.models.match_result import MatchPair, MatchReviewStatusEnum, PartyTypeEnum

CLAIMS_TO_SEED = [
    {
        "id": "32b240c2-8a7a-43a7-aa50-5f7358645f1c",
        "primary_key": "PK-100307844",
        "claim_number": "100307844",
        "exposure_number": "1",
        "insured_first_name": "PATRICIA",
        "insured_last_name": "BROWN",
        "claimant_first_name": "Richard",
        "claimant_last_name": "Jackson",
        "driver_first_name": "PATRICIA",
        "driver_last_name": "BROWN",
        "dol": "08/22/2023",
        "policy_state": "Texas",
        "loss_location_state": "Texas",
        "loss_location_city": "Houston",
        "loss_location_county": "Harris",
        "record_status": RecordStatusEnum.MATCH_FOUND,
        "fuzzy_match_status": FuzzyMatchStatusEnum.COMPLETED,
        "fl_website_broward": "No",
        "fl_botstatus_broward": "NOT_TRIGGERED",
        "fl_jsonbody_broward": [],
        "fl_website_hillsborough": "No",
        "fl_botstatus_hillsborough": "NOT_TRIGGERED",
        "fl_jsonbody_hillsborough": [],
        "fl_website_miami": "No",
        "fl_botstatus_miami": "NOT_TRIGGERED",
        "fl_jsonbody_miami": [],
        "te_website_travis": "Yes",
        "te_botstatus_travis": "COMPLETED",
        "te_jsonbody_travis": [{"CaseNumber": "D-1-GN-23-004128", "CaseStyle": "RICHARD JACKSON VS PATRICIA BROWN"}],
        "te_website_dallas": "Yes",
        "te_botstatus_dallas": "COMPLETED",
        "te_jsonbody_dallas": [],
        "te_website_harris": "Yes",
        "te_botstatus_harris": "COMPLETED",
        "te_jsonbody_harris": [{"CaseNumber": "2023-77291", "CaseStyle": "RICHARD JACKSON V. PATRICIA BROWN"}],
        "te_website_cclerk": "Yes",
        "te_botstatus_cclerk": "COMPLETED",
        "te_jsonbody_cclerk": [],
        "te_website_hcdistrict": "Yes",
        "te_botstatus_hcdistrict": "COMPLETED",
        "te_jsonbody_hcdistrict": [],
        "activity_id": "GW-ACT-77291-TX",
        "total_duration_seconds": 16.82,
        "action_timings": {
            "total_execution_seconds": 16.82,
            "total_scraping_seconds": 16.82,
            "portals": {
                "harris": {
                    "portal_name": "Harris County JP (TX)",
                    "url": "https://jpwebsite.harriscountytx.gov",
                    "status": "COMPLETED",
                    "duration_seconds": 11.2,
                    "cases_found": 2,
                    "stages": {
                        "browser_launch": {"name": "Browser Launch", "duration_seconds": 2.1, "status": "SUCCESS", "detail": "Google Chrome (Attended GUI) + AntiCaptcha"},
                        "website_navigation": {"name": "Website Navigation", "duration_seconds": 1.9, "status": "SUCCESS", "url": "https://jpwebsite.harriscountytx.gov"},
                        "data_filling": {"name": "Data Entry", "duration_seconds": 1.1, "status": "SUCCESS", "detail": "Party Name: RICHARD JACKSON"},
                        "captcha": {"name": "CAPTCHA Defense", "duration_seconds": 4.5, "status": "SOLVED", "detail": "AntiCaptcha Extension Token Injection"},
                        "submit": {"name": "Search Submit", "duration_seconds": 0.4, "status": "SUCCESS"},
                        "result_retrieval": {"name": "Result Retrieval", "duration_seconds": 1.2, "status": "SUCCESS", "cases_count": 2},
                    }
                },
                "travis": {
                    "portal_name": "Travis County (TX)",
                    "url": "https://odyssey.traviscountytx.gov",
                    "status": "COMPLETED",
                    "duration_seconds": 9.4,
                    "cases_found": 1,
                }
            },
            "stages": {
                "browser_launch": {"name": "Browser Launch", "duration_seconds": 2.1, "status": "SUCCESS", "detail": "Google Chrome (Attended GUI) + AntiCaptcha"},
                "website_navigation": {"name": "Website Navigation", "duration_seconds": 1.9, "status": "SUCCESS"},
                "data_filling": {"name": "Data Entry", "duration_seconds": 1.1, "status": "SUCCESS"},
                "captcha": {"name": "CAPTCHA Defense", "duration_seconds": 4.5, "status": "SOLVED"},
                "submit": {"name": "Search Submit", "duration_seconds": 0.4, "status": "SUCCESS"},
                "result_retrieval": {"name": "Result Retrieval", "duration_seconds": 1.2, "status": "SUCCESS"},
                "database_save": {"name": "Database Commit", "duration_seconds": 0.25, "status": "SUCCESS"},
                "fuzzy_matching": {"name": "RapidFuzz Matcher Engine", "duration_seconds": 0.04, "status": "COMPLETED"},
                "guidewire_trigger": {"name": "Guidewire 2-Way API Sync", "duration_seconds": 2.8, "status": "SUCCESS"},
            }
        },
        "cases": [
            {
                "case_number": "2023-77291",
                "case_style": "RICHARD JACKSON V. PATRICIA BROWN",
                "county_name": "Harris County JP",
                "county_website": "https://jpwebsite.harriscountytx.gov",
                "filing_date": "2023-09-14",
                "case_status": "OPEN",
                "case_type": "CIVIL INJURY/DAMAGES",
                "match": {
                    "party_type": PartyTypeEnum.CLAIMANT,
                    "party_name": "Richard Jackson",
                    "similarity_score": 96.0,
                    "review_status": MatchReviewStatusEnum.AUTO_MATCHED,
                    "is_match": True,
                }
            },
            {
                "case_number": "D-1-GN-23-004128",
                "case_style": "RICHARD JACKSON VS PATRICIA BROWN ET AL",
                "county_name": "Travis County",
                "county_website": "https://odyssey.traviscountytx.gov",
                "filing_date": "2023-10-02",
                "case_status": "OPEN",
                "case_type": "MOTOR VEHICLE ACCIDENT",
                "match": {
                    "party_type": PartyTypeEnum.INSURED,
                    "party_name": "PATRICIA BROWN",
                    "similarity_score": 88.0,
                    "review_status": MatchReviewStatusEnum.AUTO_MATCHED,
                    "is_match": True,
                }
            },
            {
                "case_number": "CC-23-09941-C",
                "case_style": "JACKSON RICHARD V. BROWN TRUCKING LLC",
                "county_name": "Dallas County",
                "county_website": "https://courtsportal.dallascounty.org",
                "filing_date": "2023-11-18",
                "case_status": "PENDING",
                "case_type": "CIVIL CONTRACT / TORT",
                "match": {
                    "party_type": PartyTypeEnum.CLAIMANT,
                    "party_name": "Richard Jackson",
                    "similarity_score": 78.5,
                    "review_status": MatchReviewStatusEnum.PENDING_REVIEW,
                    "is_match": False,
                }
            },
            {
                "case_number": "2023-08812-JP",
                "case_style": "STATE FARM AS SUBROGEE OF JACKSON VS BROWN",
                "county_name": "Harris County JP",
                "county_website": "https://jpwebsite.harriscountytx.gov",
                "filing_date": "2024-01-05",
                "case_status": "CLOSED",
                "case_type": "SUBROGATION",
                "match": {
                    "party_type": PartyTypeEnum.INSURED,
                    "party_name": "PATRICIA BROWN",
                    "similarity_score": 71.0,
                    "review_status": MatchReviewStatusEnum.PENDING_REVIEW,
                    "is_match": False,
                }
            }
        ]
    },
    {
        "id": "0304eac4-37bb-4d69-91e8-15c6b5f94941",
        "primary_key": "PK-904128",
        "claim_number": "CLM-2026-904128",
        "exposure_number": "1",
        "insured_first_name": "Carlos",
        "insured_last_name": "Rodriguez",
        "claimant_first_name": "Elena",
        "claimant_last_name": "Vargas",
        "driver_first_name": "Carlos",
        "driver_last_name": "Rodriguez",
        "dol": "11/20/2025",
        "policy_state": "Florida",
        "loss_location_state": "Florida",
        "loss_location_city": "Miami",
        "loss_location_county": "Miami-Dade",
        "record_status": RecordStatusEnum.MATCH_FOUND,
        "fuzzy_match_status": FuzzyMatchStatusEnum.COMPLETED,
        "fl_website_miami": "Yes",
        "fl_botstatus_miami": "COMPLETED",
        "fl_jsonbody_miami": [{"CaseNumber": "2026-004821-CA-01", "CaseStyle": "ELENA VARGAS VS CARLOS RODRIGUEZ"}],
        "fl_website_broward": "Yes",
        "fl_botstatus_broward": "COMPLETED",
        "fl_jsonbody_broward": [{"CaseNumber": "CACE-25-019482", "CaseStyle": "VARGAS, ELENA VS RODRIGUEZ, CARLOS"}],
        "fl_website_hillsborough": "Yes",
        "fl_botstatus_hillsborough": "COMPLETED",
        "fl_jsonbody_hillsborough": [],
        "te_website_travis": "No",
        "te_botstatus_travis": "NOT_TRIGGERED",
        "te_website_dallas": "No",
        "te_botstatus_dallas": "NOT_TRIGGERED",
        "te_website_harris": "No",
        "te_botstatus_harris": "NOT_TRIGGERED",
        "te_website_cclerk": "No",
        "te_botstatus_cclerk": "NOT_TRIGGERED",
        "te_website_hcdistrict": "No",
        "te_botstatus_hcdistrict": "NOT_TRIGGERED",
        "activity_id": "GW-ACT-98234-FL",
        "total_duration_seconds": 18.45,
        "action_timings": {
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
                    "duration_seconds": 4.1,
                    "cases_found": 1,
                }
            },
            "stages": {
                "browser_launch": {"name": "Browser Launch", "duration_seconds": 2.72, "status": "SUCCESS", "detail": "Attended Google Chrome with AntiCaptcha Extension"},
                "website_navigation": {"name": "Website Navigation", "duration_seconds": 2.29, "status": "SUCCESS"},
                "data_filling": {"name": "Data Entry", "duration_seconds": 1.33, "status": "SUCCESS"},
                "captcha": {"name": "CAPTCHA Defense", "duration_seconds": 5.2, "status": "SOLVED"},
                "submit": {"name": "Search Submit", "duration_seconds": 0.55, "status": "SUCCESS"},
                "result_retrieval": {"name": "Result Retrieval", "duration_seconds": 2.62, "status": "SUCCESS"},
                "database_save": {"name": "Database Commit", "duration_seconds": 0.33, "status": "SUCCESS"},
                "fuzzy_matching": {"name": "RapidFuzz Matcher Engine", "duration_seconds": 0.05, "status": "COMPLETED"},
                "guidewire_trigger": {"name": "Guidewire 2-Way API Sync", "duration_seconds": 3.40, "status": "SUCCESS"},
            }
        },
        "cases": [
            {
                "case_number": "2026-004821-CA-01",
                "case_style": "ELENA VARGAS VS CARLOS RODRIGUEZ",
                "county_name": "Miami-Dade County",
                "county_website": "https://www2.miamidadeclerk.gov/ocs",
                "filing_date": "2025-11-22",
                "case_status": "OPEN",
                "case_type": "CIRCUIT CIVIL",
                "match": {
                    "party_type": PartyTypeEnum.CLAIMANT,
                    "party_name": "Elena Vargas",
                    "similarity_score": 94.0,
                    "review_status": MatchReviewStatusEnum.AUTO_MATCHED,
                    "is_match": True,
                }
            },
            {
                "case_number": "CACE-25-019482",
                "case_style": "VARGAS, ELENA VS RODRIGUEZ, CARLOS",
                "county_name": "Broward County",
                "county_website": "https://www.browardclerk.org/Web2",
                "filing_date": "2025-12-01",
                "case_status": "PENDING",
                "case_type": "CIVIL ACTION CENTRAL",
                "match": {
                    "party_type": PartyTypeEnum.CLAIMANT,
                    "party_name": "Elena Vargas",
                    "similarity_score": 86.0,
                    "review_status": MatchReviewStatusEnum.PENDING_REVIEW,
                    "is_match": False,
                }
            },
            {
                "case_number": "25-CA-008129",
                "case_style": "PROGRESSIVE SELECT INS CO ASO CARLOS RODRIGUEZ VS VARGAS",
                "county_name": "Hillsborough County",
                "county_website": "https://hover.hillsclerk.com",
                "filing_date": "2026-01-10",
                "case_status": "OPEN",
                "case_type": "GENERAL CIVIL",
                "match": {
                    "party_type": PartyTypeEnum.INSURED,
                    "party_name": "Carlos Rodriguez",
                    "similarity_score": 75.0,
                    "review_status": MatchReviewStatusEnum.PENDING_REVIEW,
                    "is_match": False,
                }
            }
        ]
    },
    {
        "id": "0af1e931-85c7-4203-9d22-969e4e3c5b6a",
        "primary_key": "PK-100298095",
        "claim_number": "100298095",
        "exposure_number": "1",
        "insured_first_name": "MICHAEL",
        "insured_last_name": "JOHNSON",
        "claimant_first_name": "David",
        "claimant_last_name": "Miller",
        "driver_first_name": "MICHAEL",
        "driver_last_name": "JOHNSON",
        "dol": "05/14/2024",
        "policy_state": "Florida",
        "loss_location_state": "Florida",
        "loss_location_city": "Fort Lauderdale",
        "loss_location_county": "Broward",
        "record_status": RecordStatusEnum.MANUAL_REVIEW,
        "fuzzy_match_status": FuzzyMatchStatusEnum.PENDING_REVIEW,
        "fl_website_broward": "Yes",
        "fl_botstatus_broward": "COMPLETED",
        "fl_jsonbody_broward": [{"CaseNumber": "COCE-24-009182", "CaseStyle": "DAVID MILLER V MICHAEL JOHNSON"}],
        "fl_website_hillsborough": "Yes",
        "fl_botstatus_hillsborough": "COMPLETED",
        "fl_jsonbody_hillsborough": [],
        "fl_website_miami": "Yes",
        "fl_botstatus_miami": "COMPLETED",
        "fl_jsonbody_miami": [],
        "te_website_travis": "No",
        "te_botstatus_travis": "NOT_TRIGGERED",
        "te_website_dallas": "No",
        "te_botstatus_dallas": "NOT_TRIGGERED",
        "te_website_harris": "No",
        "te_botstatus_harris": "NOT_TRIGGERED",
        "te_website_cclerk": "No",
        "te_botstatus_cclerk": "NOT_TRIGGERED",
        "te_website_hcdistrict": "No",
        "te_botstatus_hcdistrict": "NOT_TRIGGERED",
        "activity_id": None,
        "total_duration_seconds": 15.2,
        "cases": [
            {
                "case_number": "COCE-24-009182",
                "case_style": "DAVID MILLER V MICHAEL JOHNSON",
                "county_name": "Broward County",
                "county_website": "https://www.browardclerk.org/Web2",
                "filing_date": "2024-06-12",
                "case_status": "OPEN",
                "case_type": "CIVIL DIVISION - COUNTY",
                "match": {
                    "party_type": PartyTypeEnum.CLAIMANT,
                    "party_name": "David Miller",
                    "similarity_score": 79.0,
                    "review_status": MatchReviewStatusEnum.PENDING_REVIEW,
                    "is_match": False,
                }
            }
        ]
    }
]

async def seed_rich_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TaskAsyncSessionLocal() as session:
        for cdata in CLAIMS_TO_SEED:
            cid = cdata["id"]
            cases_data = cdata.get("cases", [])
            claim_fields = {k: v for k, v in cdata.items() if k != "cases"}

            existing = await session.get(ClaimRecord, cid)
            if existing:
                for k, v in claim_fields.items():
                    setattr(existing, k, v)
                claim = existing
            else:
                claim = ClaimRecord(**claim_fields)
                session.add(claim)

            await session.flush()

            # Seed cases
            for case_info in cases_data:
                match_info = case_info.get("match")
                case_fields = {k: v for k, v in case_info.items() if k != "match"}
                
                case_id = str(uuid.uuid4())
                court_case = ScrapedCourtCase(
                    id=case_id,
                    claim_id=claim.id,
                    raw_payload={"CaseNumber": case_fields["case_number"], "CaseStyle": case_fields["case_style"], "County": case_fields["county_name"]},
                    **case_fields
                )
                session.add(court_case)
                await session.flush()

                if match_info:
                    match_pair = MatchPair(
                        id=str(uuid.uuid4()),
                        claim_id=claim.id,
                        court_case_id=case_id,
                        threshold_applied=60.0,
                        case_style=case_fields["case_style"],
                        review_notes="Automated extraction and RapidFuzz match evaluation.",
                        **match_info
                    )
                    session.add(match_pair)

        await session.commit()
        print(f"Successfully seeded {len(CLAIMS_TO_SEED)} rich claims with cases and match pairs!")

if __name__ == "__main__":
    asyncio.run(seed_rich_data())
