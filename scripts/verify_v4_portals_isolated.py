"""Read-only live probe of eight V4 portal bots using an isolated browser profile.

No application database or settings service is used. The temporary profile is
removed after the run; screenshots and a JSON report are retained as evidence.
"""

import argparse
import asyncio
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.automation.florida import (
    BrowardScraper,
    HillsboroughScraper,
    MiamiDadeScraper,
)
from app.automation.texas import (
    DallasScraper,
    HarrisCountyClerkScraper,
    HarrisDistrictClerkScraper,
    HarrisJPScraper,
    TravisScraper,
)

SCRAPERS = {
    "broward": BrowardScraper,
    "dallas": DallasScraper,
    "travis": TravisScraper,
    "harris_jp": HarrisJPScraper,
    "miami": MiamiDadeScraper,
    "harris_cclerk": HarrisCountyClerkScraper,
    "hillsborough": HillsboroughScraper,
    "harris_district": HarrisDistrictClerkScraper,
}


async def probe_one(
    context, name: str, first: str, last: str, date_of_loss: str,
    timeout_seconds: int, navigation_timeout_seconds: int,
) -> dict:
    navigation_timeout_ms = navigation_timeout_seconds * 1000
    scraper = SCRAPERS[name](
        headless=True,
        timeout_ms=navigation_timeout_ms,
        captcha_wait_seconds=5,
        max_attempts=1,
        reload_backoff_seconds=0,
    )
    page = await context.new_page()
    page.set_default_timeout(navigation_timeout_ms)
    page.set_default_navigation_timeout(navigation_timeout_ms)
    result = {
        "portal": name,
        "configured_url": scraper.base_url,
        "navigation": "not_attempted",
        "search": "not_attempted",
        "case_count": None,
        "first_case_fields": [],
        "final_url": None,
        "page_title": None,
        "captcha_visible": None,
        "error": None,
    }
    try:
        try:
            response = await page.goto(
                scraper.base_url, wait_until="domcontentloaded", timeout=navigation_timeout_ms
            )
            result["navigation"] = "loaded"
            result["http_status"] = response.status if response else None
        except Exception as error:  # noqa: BLE001 - report any live portal failure
            result["navigation"] = "failed"
            result["error"] = f"navigation: {type(error).__name__}: {str(error)[:450]}"

        if result["navigation"] == "loaded":
            try:
                async with asyncio.timeout(timeout_seconds):
                    cases = await scraper.search_by_party_name(
                        first, last, page, date_of_loss=date_of_loss
                    )
                result["search"] = "returned"
                result["case_count"] = len(cases)
                if cases:
                    result["first_case_fields"] = sorted(cases[0].keys())
                    expected_fields = {"CaseNumber", "CaseStyle", "FilingDate", "CaseStatus"}
                    if name not in {"harris_jp", "harris_cclerk"}:
                        expected_fields.add("CaseType")
                    result["all_case_fields_exact"] = all(set(case) == expected_fields for case in cases)
                    result["unique_case_numbers"] = len({case.get("CaseNumber") for case in cases}) == len(cases)
                    result["pagination_status"] = "not independently observed by this probe"
            except TimeoutError:
                result["search"] = "timed_out"
                result["error"] = f"search exceeded {timeout_seconds}s probe budget"
            except Exception as error:  # noqa: BLE001 - report any live scraper failure
                result["search"] = "failed"
                result["error"] = f"search: {type(error).__name__}: {str(error)[:450]}"
    finally:
        try:
            final_url = urlsplit(page.url)
            result["final_url"] = urlunsplit((final_url.scheme, final_url.netloc, final_url.path, "", ""))
            result["page_title"] = await page.title()
            result["captcha_visible"] = await page.evaluate("""() => Boolean(
                document.querySelector('iframe[src*="recaptcha"], iframe[src*="hcaptcha"], '
                    + 'iframe[src*="challenges.cloudflare.com"], .cf-turnstile, .g-recaptcha')
            )""")
        except Exception as error:  # noqa: BLE001 - metadata must not hide the probe result
            result["metadata_error"] = f"{type(error).__name__}: {str(error)[:200]}"
        image_time = datetime.now(timezone.utc)
        screenshot = ROOT / "implementation_plan" / "Images" / (
            f"IMP-2026-1001-002_{name}_live_probe_{image_time:%Y%m%dT%H%M%S%fZ}.png"
        )
        try:
            screenshot.parent.mkdir(parents=True, exist_ok=True)
            await page.screenshot(path=str(screenshot), full_page=True, timeout=10_000)
            result["screenshot"] = str(screenshot.relative_to(ROOT))
        except Exception as error:  # noqa: BLE001 - retain screenshot failure in report
            result["screenshot_error"] = f"{type(error).__name__}: {str(error)[:200]}"
        await page.close()
    return result


async def main(
    portals: list[str], first: str, last: str, date_of_loss: str,
    timeout_seconds: int, navigation_timeout_seconds: int,
) -> list[dict]:
    data_dir = (ROOT / "backend" / "data").resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    profile = Path(tempfile.mkdtemp(prefix="v4_live_probe_", dir=data_dir)).resolve()
    if not profile.is_relative_to(data_dir):
        raise RuntimeError("Probe profile resolved outside backend data directory")
    findings = []
    try:
        async with async_playwright() as playwright:
            context = await playwright.chromium.launch_persistent_context(
                user_data_dir=str(profile),
                headless=True,
                ignore_https_errors=False,
                viewport={"width": 1440, "height": 900},
            )
            try:
                for portal in portals:
                    finding = await probe_one(
                        context, portal, first, last, date_of_loss,
                        timeout_seconds, navigation_timeout_seconds,
                    )
                    findings.append(finding)
                    print(json.dumps(finding, ensure_ascii=False), flush=True)
            finally:
                await context.close()
    finally:
        if profile.is_relative_to(data_dir) and profile.exists():
            shutil.rmtree(profile)

    run_time = datetime.now(timezone.utc)
    scope = "all8" if len(portals) == len(SCRAPERS) else "_".join(portals)
    report = ROOT / "implementation_plan" / (
        f"2026-10-01_uaic_live_portal_probe_{scope}_{run_time:%Y%m%dT%H%M%SZ}.json"
    )
    report.write_text(
        json.dumps(
            {"implementation_id": "IMP-2026-1001-002", "timestamp_utc": run_time.isoformat(),
             "synthetic_search": {
                 "first": first, "last": last, "date_of_loss": date_of_loss
             }, "findings": findings},
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Probe report: {report.relative_to(ROOT)}", flush=True)
    return findings


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--portals", nargs="+", choices=list(SCRAPERS), default=list(SCRAPERS))
    parser.add_argument("--first", default="Audit")
    parser.add_argument("--last", default="Zyxqtest")
    parser.add_argument("--date-of-loss", default="01/01/2020")
    parser.add_argument("--timeout-seconds", type=int, default=40)
    parser.add_argument("--navigation-timeout-seconds", type=int, default=45)
    args = parser.parse_args()
    asyncio.run(main(
        args.portals, args.first, args.last, args.date_of_loss,
        args.timeout_seconds, args.navigation_timeout_seconds,
    ))
