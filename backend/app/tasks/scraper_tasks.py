"""Distributed Celery Tasks for County Court Scraping (Single-Session Multi-Tab Runner)."""

import asyncio
import logging
import time
from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm.exc import StaleDataError

from app.automation.base import (
    SecurityBlockException,
    append_portal_execution_log,
)
from app.automation.florida import (
    BrowardScraper,
    HillsboroughScraper,
    MiamiDadeScraper,
)
from app.automation.session_runner import SingleSessionBrowserRunner
from app.automation.texas import (
    DallasScraper,
    HarrisCountyClerkScraper,
    HarrisDistrictClerkScraper,
    HarrisJPScraper,
    TravisScraper,
)
from app.core.celery_app import celery_app
from app.core.database import TaskAsyncSessionLocal
from app.models.claim import BotStatusEnum, ClaimRecord, RecordStatusEnum
from app.models.court_case import ScrapedCourtCase
from app.models.error_screenshot import ErrorScreenshot
from app.services.audit_service import log_audit_event_async
from app.services.cooldown_service import (
    set_portal_cooldown,
)
from app.services.fuzzy_engine import (
    generate_unique_names_for_claim,
)
from app.services.settings_service import get_system_settings_async

logger = logging.getLogger("uaic_orchestrator.tasks.scrapers")


def normalize_court_date(val: str | None) -> str | None:
    """Normalize court filing date to standard MM/dd/yyyy format."""
    if val is None:
        return None
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ["null", "none", "nan", "n/a", "-", "--"]:
        return ""
    import re
    # 1. First try regex extraction for ISO dates YYYY-MM-DD
    iso_match = re.search(r"(\d{4})[/-](\d{1,2})[/-](\d{1,2})", val_str)
    if iso_match:
        y, m, d = iso_match.groups()
        return f"{int(m):02d}/{int(d):02d}/{y}"
    # 2. Try regex extraction for US dates MM/DD/YYYY or DD/MM/YYYY or MM/DD/YY
    us_match = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", val_str)
    if us_match:
        m, d, y = us_match.groups()
        m_int, d_int = int(m), int(d)
        if m_int > 12 and d_int <= 12:
            # DD/MM/YYYY detected (e.g. 15/01/2025)
            m_int, d_int = d_int, m_int
        if len(y) == 2:
            y = f"20{y}" if int(y) < 50 else f"19{y}"
        return f"{m_int:02d}/{d_int:02d}/{y}"
    # Strip time part if present (e.g. '2023-05-12 00:00:00' or '2023-05-12T00:00:00')
    cleaned = val_str.split("T")[0].split()[0] if (" " in val_str or "T" in val_str) else val_str
    for fmt in ["%m/%d/%Y", "%Y-%m-%d", "%Y/%m/%d", "%m-%d-%Y", "%d/%m/%Y", "%m/%d/%y"]:
        try:
            dt = datetime.strptime(cleaned, fmt)
            return dt.strftime("%m/%d/%Y")
        except ValueError:
            pass
    return val_str


@celery_app.task(name="app.tasks.scraper_tasks.health_ping_task")
def health_ping_task(message: str = "PING") -> str:
    """Dummy task used to verify worker connectivity during E2E diagnostic tests."""
    return f"PONG: {message}"


async def _async_orchestrate_scrapers(
    claim_id: str,
    single_bot_key: str | None = None,
    retry_failed_only: bool = False,
):
    """Async helper to execute active county scrapers for a claim in a single Chrome session."""
    async with TaskAsyncSessionLocal() as session:
        claim_q = select(ClaimRecord).where(ClaimRecord.id == claim_id)
        res = await session.execute(claim_q)
        claim = res.scalar_one_or_none()
        if not claim:
            logger.error(f"Claim {claim_id} not found for scraping")
            return

        claim.record_status = RecordStatusEnum.SCRAPING_IN_PROGRESS
        await session.commit()

        # Load dynamic settings from Redis/Database
        runtime_settings = await get_system_settings_async()
        auto_cfg = runtime_settings.automation
        portals_cfg = runtime_settings.portals

        # Scraper kwargs
        scraper_kw = {
            "headless": auto_cfg.headless_mode,
            "max_attempts": auto_cfg.max_captcha_attempts,
            "timeout_ms": auto_cfg.page_timeout_seconds * 1000,
            "captcha_wait_seconds": auto_cfg.captcha_wait_seconds,
            "reload_backoff_seconds": auto_cfg.reload_backoff_seconds,
            "use_chrome": auto_cfg.use_chrome_browser,
            "extension_dir": auto_cfg.chrome_extension_dir,
            "user_data_dir": auto_cfg.chrome_user_data_dir,
            "anticaptcha_api_key": auto_cfg.anticaptcha_api_key,
            "user_agent": auto_cfg.user_agent,
            "typing_speed_mode": getattr(auto_cfg, "typing_speed_mode", "turbo"),
            "typing_delay_ms": getattr(auto_cfg, "typing_delay_ms", 0),
            "action_pacing_ms": getattr(auto_cfg, "action_pacing_ms", 100),
            "stealth_clicks": getattr(auto_cfg, "stealth_clicks", False),
        }

        # Map active county scrapers based on routing flags and portal toggles
        scrapers_to_run = []
        if claim.fl_website_broward == "Yes" and portals_cfg.broward_enabled:
            scrapers_to_run.append(("broward", BrowardScraper(base_url=portals_cfg.broward_url, **scraper_kw), "fl_botstatus_broward", "fl_jsonbody_broward"))
        if claim.fl_website_hillsborough == "Yes" and portals_cfg.hillsborough_enabled:
            scrapers_to_run.append(("hillsborough", HillsboroughScraper(base_url=portals_cfg.hillsborough_url, **scraper_kw), "fl_botstatus_hillsborough", "fl_jsonbody_hillsborough"))
        if claim.fl_website_miami == "Yes" and portals_cfg.miami_enabled:
            scrapers_to_run.append(("miami", MiamiDadeScraper(base_url=portals_cfg.miami_url, username=portals_cfg.miami_username, password=portals_cfg.miami_password, requires_login=portals_cfg.miami_requires_login, **scraper_kw), "fl_botstatus_miami", "fl_jsonbody_miami"))
        if claim.te_website_travis == "Yes" and portals_cfg.travis_enabled:
            scrapers_to_run.append(("travis", TravisScraper(base_url=portals_cfg.travis_url, **scraper_kw), "te_botstatus_travis", "te_jsonbody_travis"))
        if claim.te_website_dallas == "Yes" and portals_cfg.dallas_enabled:
            scrapers_to_run.append(("dallas", DallasScraper(base_url=portals_cfg.dallas_url, **scraper_kw), "te_botstatus_dallas", "te_jsonbody_dallas"))
        if claim.te_website_harris == "Yes" and portals_cfg.harris_jp_enabled:
            scrapers_to_run.append(("harris_jp", HarrisJPScraper(base_url=portals_cfg.harris_jp_url, **scraper_kw), "te_botstatus_harris", "te_jsonbody_harris"))
        if claim.te_website_cclerk == "Yes" and portals_cfg.harris_cclerk_enabled:
            scrapers_to_run.append(("harris_cclerk", HarrisCountyClerkScraper(base_url=portals_cfg.harris_cclerk_url, **scraper_kw), "te_botstatus_cclerk", "te_jsonbody_cclerk"))
        if claim.te_website_hcdistrict == "Yes" and portals_cfg.harris_district_enabled:
            scrapers_to_run.append(("harris_district", HarrisDistrictClerkScraper(base_url=portals_cfg.harris_district_url, **scraper_kw), "te_botstatus_hcdistrict", "te_jsonbody_hcdistrict"))

        all_bot_list = [
            bot for bot in [
                ("broward", BrowardScraper(base_url=portals_cfg.broward_url, **scraper_kw), "fl_botstatus_broward", "fl_jsonbody_broward") if portals_cfg.broward_enabled else None,
                ("hillsborough", HillsboroughScraper(base_url=portals_cfg.hillsborough_url, **scraper_kw), "fl_botstatus_hillsborough", "fl_jsonbody_hillsborough") if portals_cfg.hillsborough_enabled else None,
                ("miami", MiamiDadeScraper(base_url=portals_cfg.miami_url, username=portals_cfg.miami_username, password=portals_cfg.miami_password, requires_login=portals_cfg.miami_requires_login, **scraper_kw), "fl_botstatus_miami", "fl_jsonbody_miami") if portals_cfg.miami_enabled else None,
                ("travis", TravisScraper(base_url=portals_cfg.travis_url, **scraper_kw), "te_botstatus_travis", "te_jsonbody_travis") if portals_cfg.travis_enabled else None,
                ("dallas", DallasScraper(base_url=portals_cfg.dallas_url, **scraper_kw), "te_botstatus_dallas", "te_jsonbody_dallas") if portals_cfg.dallas_enabled else None,
                ("harris_jp", HarrisJPScraper(base_url=portals_cfg.harris_jp_url, **scraper_kw), "te_botstatus_harris", "te_jsonbody_harris") if portals_cfg.harris_jp_enabled else None,
                ("harris_cclerk", HarrisCountyClerkScraper(base_url=portals_cfg.harris_cclerk_url, **scraper_kw), "te_botstatus_cclerk", "te_jsonbody_cclerk") if portals_cfg.harris_cclerk_enabled else None,
                ("harris_district", HarrisDistrictClerkScraper(base_url=portals_cfg.harris_district_url, **scraper_kw), "te_botstatus_hcdistrict", "te_jsonbody_hcdistrict") if portals_cfg.harris_district_enabled else None,
            ] if bot is not None
        ]

        if single_bot_key == "all":
            scrapers_to_run = all_bot_list
        elif single_bot_key:
            matched = [s for s in scrapers_to_run if s[0] == single_bot_key]
            if matched:
                scrapers_to_run = matched
            else:
                bot_map = {item[0]: item for item in all_bot_list}
                if single_bot_key in bot_map:
                    scrapers_to_run = [bot_map[single_bot_key]]
                else:
                    logger.warning(f"Bot {single_bot_key} is either disabled in settings or unmapped. Scrapers to run empty.")
                    scrapers_to_run = []
        elif retry_failed_only:
            candidate_list = scrapers_to_run if scrapers_to_run else all_bot_list
            failed_scrapers = [
                s for s in candidate_list
                if getattr(claim, s[2]) in (BotStatusEnum.FAILED, BotStatusEnum.BLOCKED, BotStatusEnum.IN_PROGRESS)
            ]
            scrapers_to_run = failed_scrapers
            logger.info(
                f"Claim {claim.claim_number}: Retrying failed/blocked portals only. "
                f"Portals to run: {[s[0] for s in scrapers_to_run]}"
            )
            if not scrapers_to_run:
                logger.info(f"Claim {claim.claim_number}: No failed/blocked portals found to retry.")
                has_any_failed = any(
                    getattr(claim, s[2]) in (BotStatusEnum.FAILED, BotStatusEnum.BLOCKED) for s in all_bot_list
                )
                claim.record_status = RecordStatusEnum.FAILED if has_any_failed else RecordStatusEnum.SCRAPING_COMPLETED
                await session.commit()
                return

        # Check if ALL scrapers_to_run are currently in cooldown
        all_in_cooldown = True
        min_remaining = 0
        for name, *_ in scrapers_to_run:
            from app.services.cooldown_service import is_portal_in_cooldown
            in_cooldown, remaining, _ = is_portal_in_cooldown(name)
            if not in_cooldown:
                all_in_cooldown = False
                break
            if min_remaining == 0 or remaining < min_remaining:
                min_remaining = remaining
                
        if scrapers_to_run and all_in_cooldown:
            logger.warning(f"Claim {claim.claim_number}: All required portals are in cooldown (min {min_remaining}s). Backing off.")
            claim.record_status = RecordStatusEnum.FAILED
            claim.last_error = f"All required portals are in cooldown. Next retry in ~{min_remaining}s."
            
            # Decrement retry_count so this doesn't burn a true failure retry
            if claim.retry_count > 0:
                claim.retry_count -= 1
                
            await session.commit()
            
            try:
                from app.tasks.queue_runner import (
                    is_auto_queue_enabled,
                    remove_active_queue_item_id,
                )
                remove_active_queue_item_id(claim.id)
                if is_auto_queue_enabled():
                    celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")
            except Exception:
                pass
            return

        # ── FIRST ACTION: Extract & Deduplicate Unique Names from the 3 Columns ──
        unique_name_items = generate_unique_names_for_claim(claim, fuzzy_threshold=0.60)
        party_pairs = [
            (p["party_type"], p.get("first_name"), p.get("last_name"))
            for p in unique_name_items
        ]

        targets_preview = "\n".join([f"  -> Target {p['search_order']}: [{p['party_type']}] '{p['full_name']}'" for p in unique_name_items])
        logger.info(
            f"Claim {claim.claim_number}: [UNIQUE_NAMES_EXTRACTION] Extracted {len(unique_name_items)} unique search target(s):\n"
            f"{targets_preview}\n"
            f"  Source Columns: Insured='{claim.insured_first_name} {claim.insured_last_name}', "
            f"Driver='{claim.driver_first_name} {claim.driver_last_name}', "
            f"Claimant='{claim.claimant_first_name} {claim.claimant_last_name}'"
        )

        named_targets_summary = ", ".join([f"Target {p['search_order']}: [{p['party_type']}] '{p['full_name']}'" for p in unique_name_items])
        append_portal_execution_log(
            claim.id, "orchestrator",
            f"[PIPELINE START - FIRST ACTION] Extracted {len(unique_name_items)} unique search target(s): {named_targets_summary}. "
            f"Columns: Insured='{claim.insured_first_name} {claim.insured_last_name}', "
            f"Driver='{claim.driver_first_name} {claim.driver_last_name}', "
            f"Claimant='{claim.claimant_first_name} {claim.claimant_last_name}'"
        )

        try:
            await log_audit_event_async(
                session=session,
                claim_id=claim.id,
                claim_number=claim.claim_number,
                action="UNIQUE_NAMES_EXTRACTED",
                details={
                    "claim_number": claim.claim_number,
                    "unique_count": len(unique_name_items),
                    "unique_targets": [
                        {"search_order": p["search_order"], "party_type": p["party_type"], "full_name": p["full_name"]}
                        for p in unique_name_items
                    ],
                    "source_insured": f"{claim.insured_first_name} {claim.insured_last_name}".strip(),
                    "source_driver": f"{claim.driver_first_name} {claim.driver_last_name}".strip(),
                    "source_claimant": f"{claim.claimant_first_name} {claim.claimant_last_name}".strip(),
                    "fuzzy_threshold": 0.60,
                },
            )
            await session.commit()
        except Exception as e_audit_names:
            logger.warning(f"Could not log audit event for unique names: {e_audit_names}")

        total_scraped_cases = []
        timings = dict(claim.action_timings or {})
        portal_timings = timings.setdefault("portals", {})
        stages = timings.setdefault("stages", {})

        # Extract Proxy Configuration
        proxy_cfg = runtime_settings.proxy
        proxy_server = None
        proxy_username = None
        proxy_password = None
        if proxy_cfg.enabled and proxy_cfg.host:
            proxy_server = f"http://{proxy_cfg.host}:{proxy_cfg.port}"
            proxy_username = proxy_cfg.username or None
            proxy_password = proxy_cfg.password or None

        # Launch single Chrome browser session across all enabled portals for this claim
        try:
            browser_session_runner = SingleSessionBrowserRunner(
                headless=auto_cfg.headless_mode,
                timeout_ms=auto_cfg.page_timeout_seconds * 1000,
                use_chrome=auto_cfg.use_chrome_browser,
                extension_dir=auto_cfg.chrome_extension_dir,
                anticaptcha_api_key=auto_cfg.anticaptcha_api_key,
                user_data_dir=auto_cfg.chrome_user_data_dir,
                user_agent=auto_cfg.user_agent,
                proxy_server=proxy_server,
                proxy_username=proxy_username,
                proxy_password=proxy_password,
                typing_speed_mode=getattr(auto_cfg, "typing_speed_mode", "turbo"),
                typing_delay_ms=getattr(auto_cfg, "typing_delay_ms", 0),
                action_pacing_ms=getattr(auto_cfg, "action_pacing_ms", 100),
                stealth_clicks=getattr(auto_cfg, "stealth_clicks", False),
            )

            async with browser_session_runner as browser_session:
                stages.update(browser_session.stage_timings)

                # ── Name-First Orchestration (per spec §3) ──────────────────────────
                # Step 1: Pre-open all portal tabs and mark IN_PROGRESS (checking cooldowns)
                for name, scraper, status_attr, json_attr in scrapers_to_run:
                    in_cooldown, remaining_seconds, *_ = is_portal_in_cooldown(name)
                    if in_cooldown:
                        logger.warning(
                            f"Claim {claim.claim_number}: Portal '{name}' is in security cooldown "
                            f"({remaining_seconds:.1f}s remaining). Setting status BLOCKED."
                        )
                        setattr(claim, status_attr, BotStatusEnum.BLOCKED)
                        portal_timings.setdefault(name, {
                            "portal_name": scraper.county_name,
                            "url": scraper.base_url,
                            "start_time": datetime.now().isoformat(),
                            "cases_found": 0,
                            "status": "BLOCKED",
                            "error": f"Portal in security cooldown ({int(remaining_seconds)}s remaining)",
                        })
                        continue

                    await browser_session.get_or_create_tab(portal_key=name, url=scraper.base_url)
                    append_portal_execution_log(claim.id, name, f"Initialized portal tab for {scraper.county_name} ({scraper.base_url})")
                    setattr(claim, status_attr, BotStatusEnum.IN_PROGRESS)
                    portal_timings.setdefault(name, {
                        "portal_name": scraper.county_name,
                        "url": scraper.base_url,
                        "start_time": datetime.now().isoformat(),
                        "cases_found": 0,
                        "status": "IN_PROGRESS",
                    })
                await session.commit()

                try:
                    await log_audit_event_async(
                        session=session,
                        action="SCRAPING_STARTED",
                        entity_type="CLAIM",
                        description=f"Automated browser scraping initiated across {len(scrapers_to_run)} portal tabs for claim '{claim.claim_number}'.",
                        entity_id=claim.id,
                        claim_number=claim.claim_number,
                        user_id="celery_worker",
                        user_email="orchestrator@system.local",
                        status="SUCCESS",
                        details={
                            "portals": [s[0] for s in scrapers_to_run],
                            "party_pairs_count": len(party_pairs),
                        },
                    )
                    await session.commit()
                except Exception as e_audit_start:
                    logger.warning(f"Could not log audit event for scraping start: {e_audit_start}")

                # Accumulate results per portal across all names
                portal_results: dict[str, list[dict]] = {name: [] for name, *_ in scrapers_to_run}
                portal_seen: dict[str, set] = {name: set() for name, *_ in scrapers_to_run}
                portal_start_t: dict[str, float] = {}
                portal_start_iso: dict[str, str] = {}
                for name, *_ in scrapers_to_run:
                    portal_start_t[name] = time.perf_counter()
                    portal_start_iso[name] = datetime.now().isoformat()

                # Pre-purge previous cases for target counties in this run to ensure clean incremental accumulation
                for name, scraper, *_ in scrapers_to_run:
                    await session.execute(
                        delete(ScrapedCourtCase).where(
                            ScrapedCourtCase.claim_id == claim.id,
                            ScrapedCourtCase.county_name == scraper.county_name,
                        )
                    )
                await session.commit()

                # Step 2: For each unique name → search all portals sequentially (Name A across Tab 1, Tab 2, ... -> Store)
                for party_label, f_name, l_name in party_pairs:
                    if not l_name or not str(l_name).strip():
                        continue
                    logger.info(
                        f"Claim {claim.claim_number}: ── Searching party '{party_label}: {f_name} {l_name}' "
                        f"across {len(scrapers_to_run)} portal(s) ──"
                    )
                    for name, scraper, status_attr, json_attr in scrapers_to_run:
                        if getattr(claim, status_attr) == BotStatusEnum.BLOCKED:
                            logger.info(
                                f"Claim {claim.claim_number}: Skipping portal '{name}' "
                                f"(currently BLOCKED / in cooldown)"
                            )
                            continue

                        in_cooldown, remaining_seconds, *_ = is_portal_in_cooldown(name)
                        if in_cooldown:
                            logger.warning(
                                f"Claim {claim.claim_number}: Portal '{name}' entered cooldown "
                                f"({remaining_seconds:.1f}s remaining). Marking BLOCKED."
                            )
                            setattr(claim, status_attr, BotStatusEnum.BLOCKED)
                            portal_timings[name]["status"] = "BLOCKED"
                            portal_timings[name]["error"] = f"Cooldown active ({int(remaining_seconds)}s)"
                            continue

                        # Enforce 10-year lookback
                        search_dol = claim.dol
                        if search_dol:
                            try:
                                dt = datetime.strptime(search_dol, "%m/%d/%Y")
                                ten_years_ago = datetime.now() - timedelta(days=365*10)
                                if dt < ten_years_ago:
                                    search_dol = ten_years_ago.strftime("%m/%d/%Y")
                                    logger.info(f"Claim {claim.claim_number}: Capped DOL {claim.dol} to {search_dol} (10-year lookback)")
                            except Exception:
                                pass

                        logger.info(
                            f"Claim {claim.claim_number}: [{party_label}: {f_name} {l_name}] → {scraper.county_name}"
                        )
                        append_portal_execution_log(claim.id, name, f"Searching party [{party_label}] '{f_name} {l_name}' (DOL: {search_dol or 'None'})")
                        try:
                            tab = await browser_session.get_or_create_tab(portal_key=name, url=scraper.base_url)

                            cases = await scraper.search_on_page(
                                page=tab,
                                first_name=f_name,
                                last_name=l_name,
                                date_of_loss=search_dol,
                            )
                            append_portal_execution_log(claim.id, name, f"Party search [{party_label}] returned {len(cases)} case(s)")
                            # Incremental store: save freshly extracted cases for this party/tab immediately
                            for c in cases:
                                c_num = c.get("CaseNumber") or c.get("case_number") or ""
                                if c_num and c_num not in portal_seen[name]:
                                    portal_seen[name].add(c_num)
                                    portal_results[name].append(c)
                                    raw_f_date = (
                                        c.get("FilingDate")
                                        or c.get("filing_date")
                                        or c.get("Filing Date")
                                        or c.get("SuitFiledDate")
                                        or c.get("suit_filed_date")
                                        or c.get("filed_date")
                                        or c.get("DateFiled")
                                        or c.get("date_filed")
                                        or c.get("Filed")
                                        or c.get("filed")
                                    )
                                    f_date = normalize_court_date(raw_f_date) or (claim.dol if claim and claim.dol else "")
                                    c["FilingDate"] = f_date or ""
                                    c["PartyNameSearched"] = f"{f_name} {l_name}".strip() if (f_name or l_name) else party_label
                                    scraped_case = ScrapedCourtCase(
                                        claim_id=claim.id,
                                        county_name=scraper.county_name,
                                        county_website=scraper.base_url,
                                        case_number=c_num,
                                        case_style=c.get("CaseStyle") or c.get("case_style") or "",
                                        filing_date=f_date,
                                        case_status=c.get("CaseStatus") or c.get("case_status"),
                                        case_type=c.get("CaseType") or c.get("case_type"),
                                        raw_payload=c,
                                    )
                                    session.add(scraped_case)
                                    total_scraped_cases.append(scraped_case)
                                elif not c_num:
                                    portal_results[name].append(c)
                            await session.commit()

                            # Merge per-name stage timings into aggregate
                            if hasattr(scraper, "stage_timings") and scraper.stage_timings:
                                browser_session.stage_timings.update(scraper.stage_timings)
                                stages.update(scraper.stage_timings)
                                # Reset scraper timings so next name gets fresh telemetry
                                scraper.stage_timings = {}

                        except SecurityBlockException as sbe:
                            logger.warning(
                                f"Claim {claim.claim_number}: Security block detected on {name} "
                                f"during '{party_label}: {f_name} {l_name}': {sbe.message}"
                            )
                            setattr(claim, status_attr, BotStatusEnum.BLOCKED)
                            claim.last_error = f"{name} blocked by security check: {sbe.message}"
                            portal_timings[name]["status"] = "BLOCKED"
                            portal_timings[name]["error"] = sbe.message
                            set_portal_cooldown(name, sbe.cooldown_seconds, sbe.message)
                            append_portal_execution_log(claim.id, name, f"Security block detected: {sbe.message}", level="ERROR")

                            # Auto-capture error screenshot for security block
                            tab = browser_session.tabs.get(name)
                            if tab and not tab.is_closed():
                                try:
                                    ss_meta = await scraper.capture_screenshot_on_error(
                                        page=tab,
                                        claim_id=claim.id,
                                        portal_key=name,
                                        attempt=1,
                                        error=sbe,
                                    )
                                    if ss_meta:
                                        screenshot_record = ErrorScreenshot(
                                            claim_id=claim.id,
                                            portal_key=ss_meta["portal_key"],
                                            portal_name=ss_meta["portal_name"],
                                            page_url=ss_meta.get("page_url"),
                                            page_title=ss_meta.get("page_title"),
                                            exception_message=f"SECURITY_BLOCK: {sbe.message}",
                                            attempt_number=1,
                                            storage_provider=ss_meta.get("storage_provider", "local"),
                                            file_path=ss_meta["file_path"],
                                        )
                                        session.add(screenshot_record)
                                except Exception as ss_ex:
                                    logger.warning(f"Could not capture security block screenshot for {name}: {ss_ex}")

                        except Exception as e:
                            logger.error(
                                f"Claim {claim.claim_number}: Scraper error for {name} "
                                f"on party '{party_label}: {f_name} {l_name}': {e}"
                            )
                            # Mark portal FAILED but continue processing other portals for this name
                            setattr(claim, status_attr, BotStatusEnum.FAILED)
                            claim.last_error = f"{name} scraping failure on '{party_label}': {e!s}"
                            portal_timings[name]["status"] = "FAILED"
                            portal_timings[name]["error"] = str(e)
                            append_portal_execution_log(claim.id, name, f"Error during party search: {e}", level="ERROR")

                            # Auto-capture error screenshot
                            tab = browser_session.tabs.get(name)
                            if tab and not tab.is_closed():
                                try:
                                    ss_meta = await scraper.capture_screenshot_on_error(
                                        page=tab,
                                        claim_id=claim.id,
                                        portal_key=name,
                                        attempt=1,
                                        error=e,
                                    )
                                    if ss_meta:
                                        screenshot_record = ErrorScreenshot(
                                            claim_id=claim.id,
                                            portal_key=ss_meta["portal_key"],
                                            portal_name=ss_meta["portal_name"],
                                            page_url=ss_meta.get("page_url"),
                                            page_title=ss_meta.get("page_title"),
                                            exception_message=ss_meta.get("exception_message"),
                                            attempt_number=ss_meta.get("attempt_number", 1),
                                            storage_provider=ss_meta.get("storage_provider", "local"),
                                            file_path=ss_meta["file_path"],
                                        )
                                        session.add(screenshot_record)
                                except Exception as ss_ex:
                                    logger.warning(f"Could not capture error screenshot for {name}: {ss_ex}")
                    await session.commit()

                # Step 3: All names processed — persist results per portal
                for name, scraper, status_attr, json_attr in scrapers_to_run:
                    cases = portal_results[name]
                    duration = round(time.perf_counter() - portal_start_t[name], 2)

                    current_portal_status = getattr(claim, status_attr)
                    if current_portal_status in (BotStatusEnum.FAILED, BotStatusEnum.BLOCKED):
                        final_status_str = current_portal_status.value if hasattr(current_portal_status, "value") else str(current_portal_status)
                    else:
                        final_status_str = "COMPLETED" if cases else "NO_MATCH_FOUND"

                    portal_timings[name].update({
                        "end_time": datetime.now().isoformat(),
                        "duration_seconds": duration,
                        "cases_found": len(cases),
                        "status": final_status_str,
                    })
                    append_portal_execution_log(claim.id, name, f"Completed portal scraping with status {final_status_str}. Total cases found: {len(cases)}. Duration: {duration}s")

                    setattr(claim, json_attr, cases)
                    t_db_start = datetime.now()

                    if cases:
                        if getattr(claim, status_attr) not in (BotStatusEnum.FAILED, BotStatusEnum.BLOCKED):
                            setattr(claim, status_attr, BotStatusEnum.COMPLETED)
                    else:
                        if getattr(claim, status_attr) not in (BotStatusEnum.FAILED, BotStatusEnum.BLOCKED):
                            setattr(claim, status_attr, BotStatusEnum.NO_MATCH_FOUND)

                    await session.commit()
                    t_db_end = datetime.now()

                    scraper_stages = dict(scraper.stage_timings) if hasattr(scraper, "stage_timings") and scraper.stage_timings else {}
                    portal_timings[name]["stages"] = scraper_stages
                    if scraper_stages:
                        stages.update(scraper_stages)

                    stages["database_save"] = {
                        "name": "Database Save",
                        "start_time": t_db_start.strftime("%H:%M:%S.%f")[:-3],
                        "end_time": t_db_end.strftime("%H:%M:%S.%f")[:-3],
                        "duration_seconds": max(round((t_db_end - t_db_start).total_seconds(), 3), 0.001),
                        "status": "SUCCESS",
                        "cases_saved": len(cases),
                    }

                    timings["portals"] = portal_timings
                    timings["total_scraping_seconds"] = round(
                        sum(p.get("duration_seconds", 0.0) for p in portal_timings.values()), 2
                    )
                    claim.total_duration_seconds = timings["total_scraping_seconds"]
                    claim.action_timings = timings
                    await session.commit()

            # Determine overall claim status across all configured scrapers
            has_failed_portals = any(
                getattr(claim, s[2]) in (BotStatusEnum.FAILED, BotStatusEnum.BLOCKED) for s in all_bot_list
            )
            claim.record_status = RecordStatusEnum.FAILED if has_failed_portals else RecordStatusEnum.SCRAPING_COMPLETED
            try:
                await log_audit_event_async(
                    session=session,
                    action="SCRAPING_COMPLETED" if not has_failed_portals else "SCRAPING_FAILED",
                    entity_type="CLAIM",
                    description=f"Court scraper automation completed with {len(total_scraped_cases)} cases found across {len(scrapers_to_run)} portals.",
                    entity_id=claim.id,
                    claim_number=claim.claim_number,
                    user_id="celery_worker",
                    user_email="orchestrator@system.local",
                    status="SUCCESS" if not has_failed_portals else "FAILED",
                    details={
                        "portals_executed": [s[0] for s in scrapers_to_run],
                        "cases_scraped_count": len(total_scraped_cases),
                        "total_scraping_seconds": timings.get("total_scraping_seconds", 0.0),
                    },
                )
            except Exception as e_audit:
                logger.warning(f"Could not log audit event for scraping completion: {e_audit}")
            await session.commit()
            logger.info(
                f"Scraping completed for Claim {claim.claim_number} (status={claim.record_status}). "
                f"Total cases scraped this session: {len(total_scraped_cases)}"
            )

            if has_failed_portals:
                # Do not proceed to fuzzy match if we failed. Just release lock and let queue_runner retry it later.
                try:
                    from app.tasks.queue_runner import (
                        is_auto_queue_enabled,
                        remove_active_queue_item_id,
                    )
                    remove_active_queue_item_id(claim.id)
                    if is_auto_queue_enabled():
                        celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")
                except Exception as auto_q_exc:
                    logger.warning(f"Could not advance auto-queue after browser failure: {auto_q_exc}")
            else:
                # Dispatch RapidFuzz evaluation task
                celery_app.send_task(
                    "app.tasks.fuzzy_tasks.evaluate_fuzzy_matches_task",
                    args=[claim.id],
                    queue="matcher",
                )
        except Exception as session_exc:
            logger.error(f"Browser automation session failure for Claim {claim.claim_number}: {session_exc}", exc_info=True)
            claim.record_status = RecordStatusEnum.FAILED
            claim.last_error = f"Browser session failure: {session_exc!s}"
            for name, scraper, status_attr, json_attr in scrapers_to_run:
                if getattr(claim, status_attr) == BotStatusEnum.IN_PROGRESS:
                    setattr(claim, status_attr, BotStatusEnum.FAILED)
            try:
                await log_audit_event_async(
                    session=session,
                    action="SCRAPING_SESSION_FAILED",
                    entity_type="CLAIM",
                    description=f"Browser automation session failure for Claim {claim.claim_number}: {session_exc}",
                    entity_id=claim.id,
                    claim_number=claim.claim_number,
                    user_id="celery_worker",
                    user_email="orchestrator@system.local",
                    status="FAILED",
                    details={"error": str(session_exc)},
                )
            except Exception as e_aud:
                logger.warning(f"Could not log audit event for scraper session failure: {e_aud}")
            await session.commit()

            # If auto-queue is active, release lock for this specific claim and advance queue
            try:
                from app.tasks.queue_runner import (
                    is_auto_queue_enabled,
                    remove_active_queue_item_id,
                )
                remove_active_queue_item_id(claim.id)
                if is_auto_queue_enabled():
                    celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")
            except Exception as auto_q_exc:
                logger.warning(f"Could not advance auto-queue after browser failure: {auto_q_exc}")


@celery_app.task(name="app.tasks.scraper_tasks.orchestrate_court_scrapers_task", bind=True, max_retries=3)
def orchestrate_court_scrapers_task(
    self,
    claim_id: str,
    single_bot_key: str | None = None,
    retry_failed_only: bool = False,
):
    """Celery task entrypoint for county court scraping orchestration."""
    logger.info(f"Orchestrating scrapers for Claim {claim_id} (single_bot={single_bot_key}, retry_failed_only={retry_failed_only})")
    try:
        asyncio.run(_async_orchestrate_scrapers(claim_id, single_bot_key, retry_failed_only))
    except StaleDataError:
        logger.warning(f"Claim {claim_id} was deleted or purged concurrently; aborting task.")
        return
    except Exception as exc:
        logger.error(f"Error in orchestrate_court_scrapers_task: {exc}")
        raise self.retry(exc=exc, countdown=30)

