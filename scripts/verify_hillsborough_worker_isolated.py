"""Bounded live portal worker probe with isolated storage and mock Guidewire.

This executes the application's actual scraper, matcher, and Guidewire task helpers.
It never reads or writes the running application's database, Redis DB, browser
profile, AntiCaptcha extension, notifications, or external Guidewire endpoint.
The retained report contains counts, statuses, and field names only.
"""

import argparse
import asyncio
import json
import logging
import os
import re
import sys
import tempfile
import time
import uuid
from contextlib import nullcontext
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
DATA = BACKEND / "data"
REPORTS = ROOT / "implementation_plan"
REDIS_DB = 11
MAX_SECONDS = 240
EXPECTED_FIELDS = {"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus", "CaseType"}
PORTAL_PROBES = {
    "hillsborough": {
        "dol": "01/01/2024",
        "state": "FL",
        "target_flag": "fl_website_hillsborough",
        "bot_status": "fl_botstatus_hillsborough",
        "json_field": "fl_jsonbody_hillsborough",
        "url": "https://hover.hillsclerk.com/",
    },
    "harris_district": {
        "dol": "01/01/2020",
        "state": "TX",
        "target_flag": "te_website_hcdistrict",
        "bot_status": "te_botstatus_hcdistrict",
        "json_field": "te_jsonbody_hcdistrict",
        "url": "https://www.hcdistrictclerk.com/eDocs/Public/Search.aspx",
    },
}


async def run_probe(temp_dir: Path, portal: str) -> dict:
    # Configure process isolation BEFORE importing any app module.
    db_file = temp_dir / "worker.db"
    profile = temp_dir / "browser_profile"
    profile.mkdir()
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_file.as_posix()}"
    for key in ("REDIS_URL", "CELERY_BROKER_URL", "CELERY_RESULT_BACKEND"):
        os.environ[key] = f"redis://127.0.0.1:6379/{REDIS_DB}"
    os.environ["DEBUG"] = "false"
    os.environ.pop("SEMAPHORE_BYPASS", None)
    sys.path.insert(0, str(BACKEND))

    import app.models  # noqa: F401 - register complete metadata
    import redis
    from app.automation.browser_manager import ChromeSession, ExtensionManager
    from app.automation.florida.hillsborough import HillsboroughScraper
    from app.automation.texas.harris_district import HarrisDistrictClerkScraper
    from app.core.database import Base, TaskAsyncSessionLocal, task_engine
    from app.models.claim import ClaimRecord
    from app.models.court_case import ScrapedCourtCase
    from app.models.guidewire import GuidewireActivity
    from app.schemas.settings import SystemSettings
    from app.tasks import fuzzy_tasks, scraper_tasks
    from sqlalchemy import func, select

    broker = redis.Redis.from_url(os.environ["CELERY_BROKER_URL"], socket_timeout=2)
    broker.ping()

    async with task_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    probe = PORTAL_PROBES[portal]
    scraper_class = HillsboroughScraper if portal == "hillsborough" else HarrisDistrictClerkScraper
    claim_id = str(uuid.uuid4())
    claim_fields = {probe["target_flag"]: "Yes"}
    async with TaskAsyncSessionLocal() as session:
        session.add(ClaimRecord(
            id=claim_id,
            claim_number=f"ISO-{portal.upper()}-{uuid.uuid4().hex[:12]}",
            exposure_number="001",
            dol=probe["dol"],
            policy_state=probe["state"],
            loss_location_state=probe["state"],
            insured_first_name="John",
            insured_last_name="Smith",
            claimant_first_name="John",
            claimant_last_name="Smith",
            driver_first_name="John",
            driver_last_name="Smith",
            **claim_fields,
        ))
        await session.commit()

    runtime = SystemSettings()
    runtime.automation.headless_mode = True
    runtime.automation.browser_engine = "chromium"
    runtime.automation.use_chrome_browser = False
    runtime.automation.chrome_binary_path = None
    runtime.automation.chrome_extension_dir = ""
    runtime.automation.chrome_user_data_dir = str(profile)
    runtime.automation.anticaptcha_api_key = ""
    runtime.automation.anticaptcha_enabled = False
    runtime.automation.max_captcha_attempts = 1
    runtime.automation.captcha_wait_seconds = 5
    runtime.automation.page_timeout_seconds = 90
    runtime.automation.action_pacing_ms = 100
    setattr(runtime.portals, f"{portal}_url", probe["url"])
    runtime.matcher.scorer_algorithm = "partial_ratio"
    runtime.integration.guidewire_mock_mode = True
    runtime.integration.notification_dispatch_mode = "guidewire_activity"
    runtime.integration.auto_push_on_match = True

    async def isolated_settings():
        return runtime

    def isolated_profile(_cls, _engine=None):
        return profile

    original_search = scraper_class.search_on_page

    async def observed_search(self, *args, **kwargs):
        raw_cases = await original_search(self, *args, **kwargs)
        result["scraper_returned_row_count"] = len(raw_cases)
        result["scraper_missing_number_count"] = sum(
            not bool(str(row.get("CaseNumber") or "").strip()) for row in raw_cases
        )
        result["scraper_missing_style_count"] = sum(
            not bool(str(row.get("CaseStyle") or "").strip()) for row in raw_cases
        )
        result["scraper_missing_date_count"] = sum(
            not bool(str(row.get("FilingDate") or "").strip()) for row in raw_cases
        )
        result["scraper_field_sets"] = sorted({
            ",".join(sorted(row)) for row in raw_cases
        })
        result["invalid_row_shapes"] = [
            {
                "index": index,
                "number_mask": re.sub(r"[A-Za-z]", "A", re.sub(r"\d", "9", str(row.get("CaseNumber") or ""))),
                "field_lengths": {field: len(str(row.get(field) or "").strip()) for field in EXPECTED_FIELDS},
            }
            for index, row in enumerate(raw_cases)
            if not row.get("CaseNumber") or not row.get("CaseStyle") or not row.get("FilingDate")
        ]
        page = kwargs.get("page")
        if page and result["invalid_row_shapes"]:
            result["last_page_dom_shape"] = await page.evaluate("""() => {
                const rows = [...document.querySelectorAll('#partyResultsTable tbody tr, table.dataTable tbody tr')];
                const row = rows.at(-1);
                const cells = row ? [...row.querySelectorAll('td')] : [];
                return {
                    row_count: rows.length,
                    last_row_cell_count: cells.length,
                    last_row_cell_text_lengths: cells.map(cell => (cell.innerText || '').trim().length),
                    last_row_cell_colspans: cells.map(cell => cell.getAttribute('colspan')),
                    last_row_cell_child_tags: cells.map(cell => [...cell.children].map(child => child.tagName)),
                    last_row_number_has_link: Boolean(cells[2]?.querySelector('a')),
                    last_row_classes: row ? [...row.classList] : [],
                };
            }""")
        return raw_cases

    result = {
        "implementation_id": "IMP-2026-1001-002",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "portal": portal,
        "synthetic_claim": f"John Smith, {probe['dol']}",
        "browser": "headless Chromium, isolated profile, no extension",
        "storage": "temporary SQLite, Redis DB 11",
        "guidewire": "mock only",
        "runtime_settings": {
            "scorer_algorithm": runtime.matcher.scorer_algorithm,
            "page_timeout_seconds": runtime.automation.page_timeout_seconds,
            "captcha_wait_seconds": runtime.automation.captcha_wait_seconds,
            "max_captcha_attempts": runtime.automation.max_captcha_attempts,
            "action_pacing_ms": runtime.automation.action_pacing_ms,
        },
        "scrape": "not_attempted",
        "fuzzy": "not_attempted",
        "mock_guidewire": "not_attempted",
    }

    try:
        # These patches affect this process only. The real scraper, persistence,
        # matching, and Guidewire payload builders remain in use.
        with (
            patch.object(ExtensionManager, "resolve_extension_path", return_value=None),
            patch.object(ChromeSession, "get_persistent_profile_dir", classmethod(isolated_profile)),
            patch.object(ChromeSession, "configure_and_pin_profile", return_value=profile),
            patch.object(scraper_tasks, "get_system_settings_async", isolated_settings),
            patch.object(fuzzy_tasks, "get_system_settings_async", isolated_settings),
            patch.object(scraper_class, "search_on_page", observed_search),
            patch.object(HillsboroughScraper, "return_to_search_state", new_callable=AsyncMock)
            if portal == "hillsborough" else nullcontext(),
            patch.object(scraper_tasks.celery_app, "send_task", MagicMock()) as queued,
            patch.object(fuzzy_tasks.NotificationService, "emit_event", AsyncMock()),
        ):
            started = time.monotonic()
            await asyncio.wait_for(
                scraper_tasks._async_orchestrate_scrapers(claim_id, single_bot_key=portal),
                timeout=MAX_SECONDS,
            )
            result["scrape_duration_seconds"] = round(time.monotonic() - started, 2)

            async with TaskAsyncSessionLocal() as session:
                claim = await session.get(ClaimRecord, claim_id)
                cases = (await session.execute(select(ScrapedCourtCase).where(
                    ScrapedCourtCase.claim_id == claim_id
                ))).scalars().all()
                json_rows = getattr(claim, probe["json_field"]) or []
                result.update({
                    "scrape": str(getattr(claim, probe["bot_status"]).value),
                    "claim_status_after_scrape": str(claim.record_status.value),
                    "claim_json_row_count": len(json_rows),
                    "court_case_row_count": len(cases),
                    "exact_json_fields": all(set(row) == EXPECTED_FIELDS for row in json_rows),
                    "first_json_fields": sorted(json_rows[0]) if json_rows else [],
                    "distinct_case_number_count": len({row["CaseNumber"] for row in json_rows}),
                    "all_rows_have_number_style_date": all(
                        bool(c.case_number and c.case_style and c.filing_date) for c in cases
                    ),
                    "fuzzy_task_queued": any(
                        call.args and call.args[0] == "app.tasks.fuzzy_tasks.evaluate_fuzzy_matches_task"
                        for call in queued.call_args_list
                    ),
                })

            if not cases or result["scrape"] != "COMPLETED":
                return result
            if len(json_rows) != len(cases) or not result["exact_json_fields"]:
                return result

            # The V4 matcher is run with its configured 2010 cutoff, status,
            # and type lists. Its outcome determines whether a Guidewire push
            # should occur; no synthetic match is injected.
            await fuzzy_tasks._async_evaluate_fuzzy_matches(claim_id)
            async with TaskAsyncSessionLocal() as session:
                claim = await session.get(ClaimRecord, claim_id)
                items = (claim.final_matched_json or {}).get("CaseItems", [])
                result.update({
                    "fuzzy": str(claim.fuzzy_match_status.value),
                    "claim_status_after_fuzzy": str(claim.record_status.value),
                    "matched_case_item_count": len(items),
                    "matched_case_item_fields": sorted(items[0]) if items else [],
                })

            if not items:
                return result

            await fuzzy_tasks._async_notify_guidewire(claim_id)
            async with TaskAsyncSessionLocal() as session:
                claim = await session.get(ClaimRecord, claim_id)
                activity = (await session.execute(select(GuidewireActivity).where(
                    GuidewireActivity.claim_id == claim_id
                ))).scalar_one_or_none()
                db_count = (await session.execute(select(func.count()).select_from(ScrapedCourtCase).where(
                    ScrapedCourtCase.claim_id == claim_id
                ))).scalar_one()
                payload_items = (activity.request_payload or {}).get("CaseItems", []) if activity else []
                result.update({
                    "mock_guidewire": activity.status if activity else "no_activity",
                    "claim_status_after_mock_guidewire": str(claim.record_status.value),
                    "mock_payload_case_item_count": len(payload_items),
                    "mock_payload_case_item_fields": sorted(payload_items[0]) if payload_items else [],
                    "court_case_rows_final": db_count,
                })
            return result
    finally:
        await task_engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--portal", choices=tuple(PORTAL_PROBES), default="hillsborough")
    portal = parser.parse_args().portal
    DATA.mkdir(parents=True, exist_ok=True)
    logging.disable(logging.INFO)
    # TemporaryDirectory never points outside backend/data; all DB and browser
    # files are removed when the isolated process finishes.
    with tempfile.TemporaryDirectory(prefix=f"uaic_{portal}_worker_e2e_", dir=DATA) as directory:
        temp_dir = Path(directory).resolve()
        if temp_dir.parent != DATA.resolve():
            raise RuntimeError("Isolated probe directory escaped backend/data")
        try:
            result = asyncio.run(run_probe(temp_dir, portal))
        except Exception as exc:  # noqa: BLE001 - report failure without case PII
            result = {
                "implementation_id": "IMP-2026-1001-002",
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "portal": portal,
                "status": "probe_exception",
                "exception_type": type(exc).__name__,
            }
            if hasattr(exc, "errors"):
                result["validation_fields"] = [
                    {"field": ".".join(map(str, item.get("loc", ()))), "type": item.get("type")}
                    for item in exc.errors()
                ]

    REPORTS.mkdir(parents=True, exist_ok=True)
    report = REPORTS / (
        f"2026-10-01_uaic_{portal}_worker_e2e_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"
    )
    report.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(report.relative_to(ROOT)), "result": result}, indent=2))
    return 0 if result.get("mock_guidewire") == "SUCCESS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
