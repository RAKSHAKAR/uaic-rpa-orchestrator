"""Interactive and CLI Test Harness to Run and Validate Any of the 8 Court Portal Bots.

Usage:
    # Interactive mode (prompts for bot selection and party name):
    python scripts/test_court_bot.py

    # Test single bot in visible Google Chrome (Attended Mode):
    python scripts/test_court_bot.py --bot broward --party "DOE, JOHN"
    python scripts/test_court_bot.py --bot hillsborough --party "SMITH, ROBERT" --dol "01/15/2023"
    python scripts/test_court_bot.py --bot dallas --party "JOHNSON, MICHAEL"
    python scripts/test_court_bot.py --bot harris_jp --party "WILLIAMS, DAVID"

    # Test all 8 bots sequentially:
    python scripts/test_court_bot.py --bot all --party "DOE, JOHN"
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.automation.florida import BrowardScraper, HillsboroughScraper, MiamiDadeScraper
from app.automation.texas import (
    DallasScraper,
    HarrisCountyClerkScraper,
    HarrisDistrictClerkScraper,
    HarrisJPScraper,
    TravisScraper,
)
from app.core.config import settings
import functools
print = functools.partial(print, flush=True)

# Registry of all 8 court portal bots with their metadata and canonical V4 configuration
BOT_REGISTRY = {
    "broward": {
        "num": 1,
        "name": "Broward County Clerk",
        "state": "FL",
        "cls": BrowardScraper,
        "default_url": "https://www.browardclerk.org/Web2",
        "has_case_type": True,
        "source_file": "backend/app/automation/florida/broward.py",
        "db_key": "fl_jsonbody_broward",
        "status_col": "fl_botstatus_broward",
    },
    "dallas": {
        "num": 2,
        "name": "Dallas County Odyssey",
        "state": "TX",
        "cls": DallasScraper,
        "default_url": "https://courtsportal.dallascounty.org/DALLASPROD/Home/Dashboard/29",
        "has_case_type": True,
        "source_file": "backend/app/automation/texas/dallas.py",
        "db_key": "te_jsonbody_dallas",
        "status_col": "te_botstatus_dallas",
    },
    "travis": {
        "num": 3,
        "name": "Travis County Odyssey",
        "state": "TX",
        "cls": TravisScraper,
        "default_url": "https://odysseyweb.traviscountytx.gov/Portal/Home/Dashboard/29",
        "has_case_type": True,
        "source_file": "backend/app/automation/texas/travis.py",
        "db_key": "te_jsonbody_travis",
        "status_col": "te_botstatus_travis",
    },
    "harris_jp": {
        "num": 4,
        "name": "Harris County JP",
        "state": "TX",
        "cls": HarrisJPScraper,
        "default_url": "https://jpodysseyportal.harriscountytx.gov/OdysseyPortalJP/Home/Dashboard/29",
        "has_case_type": False,  # STRICT V4 RULE: NO CaseType
        "source_file": "backend/app/automation/texas/harris_jp.py",
        "db_key": "te_jsonbody_harris",
        "status_col": "te_botstatus_harris",
    },
    "miami": {
        "num": 5,
        "name": "Miami-Dade County Clerk",
        "state": "FL",
        "cls": MiamiDadeScraper,
        "default_url": "https://www2.miamidadeclerk.gov/ocs",
        "has_case_type": True,
        "source_file": "backend/app/automation/florida/miami.py",
        "db_key": "fl_jsonbody_miami",
        "status_col": "fl_botstatus_miami",
    },
    "harris_cclerk": {
        "num": 6,
        "name": "Harris County Clerk",
        "state": "TX",
        "cls": HarrisCountyClerkScraper,
        "default_url": "https://www.cclerk.hctx.net/Applications/WebSearch/",
        "has_case_type": False,  # STRICT V4 RULE: NO CaseType
        "source_file": "backend/app/automation/texas/harris_cclerk.py",
        "db_key": "te_jsonbody_cclerk",
        "status_col": "te_botstatus_cclerk",
    },
    "hillsborough": {
        "num": 7,
        "name": "Hillsborough County Clerk",
        "state": "FL",
        "cls": HillsboroughScraper,
        "default_url": "https://hover.hillsclerk.com/html/case/caseSearch.html#nav-Party-tab",
        "has_case_type": True,
        "source_file": "backend/app/automation/florida/hillsborough.py",
        "db_key": "fl_jsonbody_hillsborough",
        "status_col": "fl_botstatus_hillsborough",
    },
    "harris_district": {
        "num": 8,
        "name": "Harris District Clerk",
        "state": "TX",
        "cls": HarrisDistrictClerkScraper,
        "default_url": "https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx",
        "has_case_type": True,
        "source_file": "backend/app/automation/texas/harris_district.py",
        "db_key": "te_jsonbody_hcdistrict",
        "status_col": "te_botstatus_hcdistrict",
    },
}


def parse_party_name(party_str: str) -> tuple[str, str]:
    """Parses 'Last, First' or 'First Last' into (first_name, last_name)."""
    cleaned = (party_str or "").strip()
    if not cleaned:
        return ("JOHN", "DOE")
    if "," in cleaned:
        parts = [p.strip() for p in cleaned.split(",", 1)]
        return (parts[1] if len(parts) > 1 else "", parts[0])
    parts = cleaned.split()
    if len(parts) == 1:
        return ("", parts[0])
    return (" ".join(parts[:-1]), parts[-1])


async def run_single_bot_test(
    bot_key: str,
    first_name: str,
    last_name: str,
    date_of_loss: str | None = None,
    headless: bool = False,
    timeout_ms: int = 35000,
) -> dict:
    meta = BOT_REGISTRY[bot_key]
    scraper_cls = meta["cls"]
    county_name = meta["name"]
    expected_case_type = meta["has_case_type"]

    print("\n" + "=" * 80)
    print(f"  LAUNCHING BOT TEST: [{meta['num']}/8] {county_name} ({meta['state']})")
    print(f"  Source File : {meta['source_file']}")
    print(f"  Search Party: '{first_name} {last_name}' | DOL: '{date_of_loss or 'None'}'")
    print(f"  Browser Mode: {'Headless (Background)' if headless else 'Attended (Visible Google Chrome GUI)'}")
    print(f"  Target URL  : {meta['default_url']}")
    print(f"  Schema Rule : {'CaseType INCLUDED (5 fields)' if expected_case_type else 'CaseType STRICTLY OMITTED (4 fields)'}")
    print("=" * 80)

    # Initialize scraper
    scraper = scraper_cls(
        base_url=meta["default_url"],
        headless=headless,
        timeout_ms=timeout_ms,
        use_chrome=True,
    )

    t_start = datetime.now()
    results = []
    error = None

    try:
        results = await scraper.run_search(
            first_name=first_name,
            last_name=last_name,
            date_of_loss=date_of_loss,
        )
    except Exception as exc:
        error = str(exc)
        print(f"\n  [ERROR] Execution encountered exception: {exc}")

    t_duration = round((datetime.now() - t_start).total_seconds(), 2)

    # Telemetry and stage breakdown
    print(f"\n  [COMPLETED] Execution finished in {t_duration}s. Records Extracted: {len(results)}")
    if scraper.stage_timings:
        print("\n  --- Pipeline Stage Telemetry ---")
        for stage_key, s_data in scraper.stage_timings.items():
            s_name = s_data.get("name", stage_key)
            s_dur = s_data.get("duration_seconds", 0)
            s_status = s_data.get("status", "SUCCESS")
            print(f"    - {s_name:<24} : {s_dur:>6.2f}s [{s_status}]")

    # Schema Parity Validation
    schema_ok = True
    if results:
        print("\n  --- Extracted Cases Sample ---")
        for idx, case in enumerate(results[:3], 1):
            c_num = case.get("CaseNumber") or case.get("case_number") or "N/A"
            c_style = case.get("CaseStyle") or case.get("case_style") or "N/A"
            c_date = case.get("FilingDate") or case.get("filing_date") or "N/A"
            c_status = case.get("CaseStatus") or case.get("case_status") or "N/A"
            c_type = case.get("CaseType") or case.get("case_type")

            print(f"    [{idx}] Case #{c_num:<20} | Date: {c_date:<10} | Status: {c_status:<10}")
            print(f"        Style: {c_style}")
            if c_type:
                print(f"        Type : {c_type}")

            # Check schema invariant
            if not expected_case_type and ("CaseType" in case or "case_type" in case):
                schema_ok = False
                print(f"    [!] SCHEMA VIOLATION: {county_name} must NOT output CaseType!")
            elif expected_case_type and ("CaseType" not in case and "case_type" not in case):
                schema_ok = False
                print(f"    [!] SCHEMA WARNING: {county_name} expected CaseType in output payload.")

    print(f"\n  Schema Parity Check: {'PASS (Exact Power Automate V4 Contract)' if schema_ok else 'FAILED'}")
    return {
        "bot_key": bot_key,
        "county_name": county_name,
        "results_count": len(results),
        "duration_seconds": t_duration,
        "schema_ok": schema_ok,
        "error": error,
    }


async def main():
    parser = argparse.ArgumentParser(description="Test any of the 8 court portal bots one by one.")
    parser.add_argument(
        "--bot",
        choices=list(BOT_REGISTRY.keys()) + ["all"],
        help="Bot key to test (e.g. broward, dallas, harris_jp, or all)",
    )
    parser.add_argument("--party", default=None, help="Party name (e.g. 'DOE, JOHN' or 'JOHN DOE')")
    parser.add_argument("--dol", default=None, help="Date of Loss (e.g. '01/15/2023')")
    parser.add_argument("--headless", action="store_true", default=False, help="Run in headless mode (default: False/Attended GUI)")
    args = parser.parse_args()

    selected_bot = args.bot

    # If not provided via CLI, prompt interactively
    if not selected_bot:
        print("\n" + "=" * 80)
        print("  UAIC COURT PORTAL RPA BOT SELECTION MENU")
        print("=" * 80)
        for k, v in BOT_REGISTRY.items():
            print(f"  [{v['num']}] {v['name']:<30} ({v['state']}) -> key: '{k}'")
        print("  [9] Run All 8 Bots Sequentially (Full V4 Fleet)")
        print("=" * 80)

        choice = input("\nSelect bot to test [1-9] (default 1): ").strip() or "1"
        num_map = {str(v["num"]): k for k, v in BOT_REGISTRY.items()}
        num_map["9"] = "all"
        selected_bot = num_map.get(choice, "broward")

    party_input = args.party
    if not party_input and not sys.stdin.isatty():
        party_input = "DOE, JOHN"
    elif not party_input:
        user_party = input("Enter Party Name to search [Last, First or First Last] (default: 'DOE, JOHN'): ").strip()
        party_input = user_party or "DOE, JOHN"

    f_name, l_name = parse_party_name(party_input)

    bots_to_run = list(BOT_REGISTRY.keys()) if selected_bot == "all" else [selected_bot]

    summary_reports = []
    for b_key in bots_to_run:
        report = await run_single_bot_test(
            bot_key=b_key,
            first_name=f_name,
            last_name=l_name,
            date_of_loss=args.dol,
            headless=args.headless,
        )
        summary_reports.append(report)

    # Print summary
    print("\n" + "#" * 80)
    print("  TEST HARNESS EXECUTION SUMMARY REPORT")
    print("#" * 80)
    print(f"  {'#':<4} {'County Court Portal':<32} {'Records':<10} {'Time':<8} {'Schema':<10} {'Status'}")
    print("  " + "-" * 76)
    for idx, r in enumerate(summary_reports, 1):
        status = "FAIL" if r["error"] else ("OK (Extracted)" if r["results_count"] > 0 else "OK (0 Found)")
        schema_lbl = "PASS" if r["schema_ok"] else "FAIL"
        print(f"  [{idx}] {r['county_name']:<32} {r['results_count']:<10} {r['duration_seconds']:>5.2f}s  {schema_lbl:<10} {status}")
    print("#" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
