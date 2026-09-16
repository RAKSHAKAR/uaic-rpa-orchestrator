"""Script to enrich sample claim with realistic provenance and 4-tab diagnostic logs."""

import asyncio
from pathlib import Path

from app.core.database import TaskAsyncSessionLocal
from app.models.claim import ClaimRecord
from app.services.audit_service import log_audit_event_async


async def enrich():
    async with TaskAsyncSessionLocal() as session:
        claim = await session.get(ClaimRecord, "0127b8ee-9911-42ed-9ed6-bc6261cb02de")
        if not claim:
            print("Claim 0127b8ee-9911-42ed-9ed6-bc6261cb02de not found")
            return

        claim.created_by = "claims_adjuster:sarah.connor@uaic.com"
        claim.modified_by = "worker:scrapers"
        claim.action_timings = {
            "stages": {
                "broward": {
                    "name": "Broward County Portal",
                    "status": "FAILED",
                    "start_time": "10:14:02.100",
                    "end_time": "10:14:15.340",
                    "duration_seconds": 13.24,
                    "detail": "Timeout waiting for reCAPTCHA v2 token injection",
                    "error": "TimeoutError: 30000ms exceeded while waiting for selector .g-recaptcha-response",
                },
                "hillsborough": {
                    "name": "Hillsborough County Portal",
                    "status": "SUCCESS",
                    "start_time": "10:14:16.000",
                    "end_time": "10:14:24.210",
                    "duration_seconds": 8.21,
                    "cases_found": 3,
                    "detail": "Scraped 3 court cases cleanly",
                },
                "miami": {
                    "name": "Miami-Dade County Portal",
                    "status": "SUCCESS",
                    "start_time": "10:14:25.000",
                    "end_time": "10:14:32.450",
                    "duration_seconds": 7.45,
                    "cases_found": 1,
                    "detail": "Scraped 1 court case cleanly",
                },
            }
        }

        await log_audit_event_async(
            session=session,
            action="CLAIM_CREATED",
            entity_type="CLAIM",
            description="Ingested claim 086965175 via policy feed",
            entity_id=claim.id,
            claim_number=claim.claim_number,
            user_id="sarah.connor",
            user_email="sarah.connor@uaic.com",
            status="SUCCESS",
            details={"policy_number": "POL-99281", "source": "PolicyCenter API"},
        )

        await log_audit_event_async(
            session=session,
            action="PORTAL_SCRAPING_FAILED",
            entity_type="CLAIM",
            description="Broward portal encountered reCAPTCHA token timeout",
            entity_id=claim.id,
            claim_number=claim.claim_number,
            user_id="worker:scrapers",
            user_email="scrapers@worker.local",
            status="FAILED",
            details={
                "portal_key": "broward",
                "portal_name": "Broward County Portal",
                "exception_type": "PlaywrightTimeoutError",
                "error_message": "Timeout 30000ms exceeded while waiting for element .g-recaptcha-response",
                "traceback": "Traceback (most recent call last):\n  File 'broward.py', line 114, in search_parties\n    await page.wait_for_selector('.g-recaptcha-response', timeout=30000)\nPlaywrightTimeoutError: Timeout 30000ms exceeded.",
            },
        )

        # Create execution log file for portal console terminal
        log_dir = Path("logs") / claim.id / "broward"
        log_dir.mkdir(parents=True, exist_ok=True)
        with open(log_dir / "execution.log", "w", encoding="utf-8") as f:
            f.write(
                "[BROWARD BOT] Initializing Chromium session (PID 49281)\n"
                "[BROWARD BOT] Navigating to https://www.browardclerk.org/\n"
                "[BROWARD BOT] Waiting for party search form input fields...\n"
                "[BROWARD BOT] Injected party: James Rodriguez\n"
                "[BROWARD BOT] reCAPTCHA challenge detected (SiteKey: 6Ld...)\n"
                "[BROWARD BOT] AntiCaptcha solver active (Task #891238)\n"
                "[BROWARD BOT] [ERROR] Timeout waiting for token callback.\n"
            )

        await session.commit()
        print("Enriched claim 0127b8ee-9911-42ed-9ed6-bc6261cb02de successfully")


if __name__ == "__main__":
    asyncio.run(enrich())
