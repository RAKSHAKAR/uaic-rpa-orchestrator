import asyncio
import io
import traceback
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.claim import ClaimRecord

async def main():
    try:
        async with AsyncSessionLocal() as db:
            query = select(ClaimRecord).where(ClaimRecord.id == "0304eac4-37bb-4d69-91e8-15c6b5f94941").options(
                selectinload(ClaimRecord.scraped_cases),
                selectinload(ClaimRecord.match_pairs),
            )
            res = await db.execute(query)
            claim = res.scalar_one_or_none()
            if not claim:
                print("Claim not found!")
                return
            print(f"Loaded claim: {claim.claim_number}")

            case_rows = []
            if claim.scraped_cases:
                for c in claim.scraped_cases:
                    case_rows.append({
                        "Claim Number": claim.claim_number,
                        "Case Number": c.case_number,
                        "Case Style": c.case_style,
                        "County": c.county_name,
                        "Website URL": c.county_website,
                        "Filing Date": c.filing_date or "",
                        "Case Status": c.case_status or "",
                        "Case Type": c.case_type or "",
                        "Scraped At": c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else "",
                    })
            else:
                case_rows.append({
                    "Claim Number": claim.claim_number,
                    "Case Number": "NO_CASES_FOUND",
                    "Case Style": "",
                    "County": "",
                    "Website URL": "",
                    "Filing Date": "",
                    "Case Status": "",
                    "Case Type": "",
                    "Scraped At": "",
                })

            df_cases = pd.DataFrame(case_rows)

            out = io.BytesIO()
            with pd.ExcelWriter(out, engine="openpyxl") as writer:
                insured = f"{claim.insured_first_name or ''} {claim.insured_last_name or ''}".strip()
                claimant = f"{claim.claimant_first_name or ''} {claim.claimant_last_name or ''}".strip()
                driver = f"{claim.driver_first_name or ''} {claim.driver_last_name or ''}".strip()

                overview_data = [
                    {"Field": "Claim Number", "Value": claim.claim_number},
                    {"Field": "Primary Key", "Value": claim.primary_key or ""},
                    {"Field": "Exposure Number", "Value": claim.exposure_number or "1"},
                    {"Field": "Date of Loss (DOL)", "Value": claim.dol or ""},
                    {"Field": "Policy State", "Value": claim.policy_state or ""},
                    {"Field": "Loss Location", "Value": f"{claim.loss_location_city or ''}, {claim.loss_location_county or ''}, {claim.loss_location_state or ''}".strip(", ")},
                    {"Field": "Insured Party", "Value": insured or "N/A"},
                    {"Field": "Claimant Party", "Value": claimant or "N/A"},
                    {"Field": "Driver (Insured Vehicle)", "Value": driver or "N/A"},
                    {"Field": "Record Status", "Value": claim.record_status.value if hasattr(claim.record_status, "value") else str(claim.record_status)},
                    {"Field": "Fuzzy Match Status", "Value": claim.fuzzy_match_status.value if hasattr(claim.fuzzy_match_status, "value") else str(claim.fuzzy_match_status)},
                    {"Field": "Total Duration (seconds)", "Value": str(claim.total_duration_seconds or "")},
                    {"Field": "Guidewire Activity ID", "Value": claim.activity_id or "None"},
                    {"Field": "Total Cases Scraped", "Value": len(claim.scraped_cases)},
                    {"Field": "Created At", "Value": claim.created_at.strftime("%Y-%m-%d %H:%M:%S") if claim.created_at else ""},
                ]
                pd.DataFrame(overview_data).to_excel(writer, index=False, sheet_name="Claim Overview")
                df_cases.to_excel(writer, index=False, sheet_name="Scraped Court Cases")

                match_rows = []
                for m in claim.match_pairs:
                    match_rows.append({
                        "Case Number": m.scraped_case_number,
                        "Case Style": m.scraped_case_style or "",
                        "County": m.county_name or "",
                        "Match Score": m.match_score,
                        "Party Matched": m.party_matched or "",
                        "Status": m.status.value if hasattr(m.status, "value") else str(m.status),
                        "Rationale": m.rationale or "",
                    })
                pd.DataFrame(match_rows or [{"Note": "No match records evaluated yet"}]).to_excel(writer, index=False, sheet_name="Fuzzy Matches")

                stages_data = []
                timings = claim.action_timings or {}
                stages = timings.get("stages", {})
                for sk, sval in stages.items():
                    if isinstance(sval, dict):
                        stages_data.append({
                            "Stage Key": sk,
                            "Stage Name": sval.get("name", sk),
                            "Start Time": sval.get("start_time", ""),
                            "End Time": sval.get("end_time", ""),
                            "Duration (s)": sval.get("duration_seconds", ""),
                            "Status": sval.get("status", ""),
                            "Detail": sval.get("detail") or sval.get("url") or sval.get("party") or "",
                        })
                pd.DataFrame(stages_data or [{"Note": "No stage telemetry recorded"}]).to_excel(writer, index=False, sheet_name="Stage Telemetry")

            excel_bytes = out.getvalue()
            print(f"SUCCESS! Excel generated, size: {len(excel_bytes)} bytes")
            with open("scratch_test_0304eac4.xlsx", "wb") as f:
                f.write(excel_bytes)
            print("Saved scratch_test_0304eac4.xlsx")
    except Exception as e:
        print("EXCEPTION CAUGHT:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
