"""Script to refactor _async_orchestrate_scrapers in scraper_tasks.py into 3 decoupled phases."""
from pathlib import Path

FILE_PATH = Path("backend/app/tasks/scraper_tasks.py")
content = FILE_PATH.read_text(encoding="utf-8")

start_marker = "async def _async_orchestrate_scrapers("
end_marker = "@celery_app.task(name=\"app.tasks.scraper_tasks.orchestrate_court_scrapers_task\", bind=True)"

start_idx = content.index(start_marker)
end_idx = content.index(end_marker)

new_func = '''async def _async_orchestrate_scrapers(
    claim_id: str,
    single_bot_key: str | None = None,
    retry_failed_only: bool = False,
):
    """Async helper to execute active county scrapers for a claim in a single Chrome session."""
    # ── PHASE 1: DB Read & Mark In-Progress (Short-lived session < 10ms) ──────────
    async with TaskAsyncSessionLocal() as session:
        claim_q = select(ClaimRecord).where(ClaimRecord.id == claim_id)
        res = await session.execute(claim_q)
        claim = res.scalar_one_or_none()
        if not claim:
            logger.error(f"Claim {claim_id} not found for scraping")
            return

        # Guard against duplicate/redundant execution on already completed claims
        terminal_statuses = (
            RecordStatusEnum.COMPLETED,
            RecordStatusEnum.MATCH_FOUND,
            RecordStatusEnum.NO_MATCH_FOUND,
            RecordStatusEnum.MANUAL_REVIEW,
        )
        if not single_bot_key and not retry_failed_only and claim.record_status in terminal_statuses:
            logger.info(
                f"Claim {claim.claim_number} is already in terminal state '{claim.record_status.value}'. "
                f"Skipping redundant scraper orchestration task."
            )
            return

        claim.record_status = RecordStatusEnum.SCRAPING_IN_PROGRESS
        await session.commit()

        # Load dynamic settings from Redis/Database
        runtime_settings = await get_system_settings_async()
        auto_cfg = runtime_settings.automation
        portals_cfg = runtime_settings.portals
        queue_cfg = runtime_settings.queue
        proxy_cfg = runtime_settings.proxy

        # Copy needed primitive fields from claim before releasing session
        claim_number = claim.claim_number
        dol = claim.dol
        policy_state = claim.policy_state
        loss_location_state = claim.loss_location_state
        retry_count = claim.retry_count or 0
        timings = dict(claim.action_timings or {})
        portal_timings = timings.setdefault("portals", {})
        stages = timings.setdefault("stages", {})

        # Scraper kwargs
        scraper_kw = {
            "headless": auto_cfg.headless_mode,
            "max_attempts": auto_cfg.max_captcha_attempts,
            "timeout_ms": auto_cfg.page_timeout_seconds * 1000,
            "captcha_wait_seconds": auto_cfg.captcha_wait_seconds,
            "reload_backoff_seconds": auto_cfg.reload_backoff_seconds,
            "use_chrome": auto_cfg.use_chrome_browser,
            "browser_engine": getattr(auto_cfg, "browser_engine", "chrome"),
            "chrome_binary_path": getattr(auto_cfg, "chrome_binary_path", None),
            "extension_dir": auto_cfg.chrome_extension_dir,
            "user_data_dir": auto_cfg.chrome_user_data_dir,
            "anticaptcha_api_key": auto_cfg.anticaptcha_api_key,
            "user_agent": auto_cfg.user_agent,
            "typing_speed_mode": getattr(auto_cfg, "typing_speed_mode", "turbo"),
            "typing_delay_ms": getattr(auto_cfg, "typing_delay_ms", 0),
            "action_pacing_ms": getattr(auto_cfg, "action_pacing_ms", 100),
            "stealth_clicks": getattr(auto_cfg, "stealth_clicks", False),
        }

        # Canonical V4 Portal Sequencing Order:
        # Florida: 1. Broward -> 2. Hillsborough -> 3. Miami-Dade
        # Texas:   4. Travis  -> 5. Dallas       -> 6. Harris JP -> 7. Harris CClerk -> 8. Harris District
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
            if not scrapers_to_run:
                from app.services.excel_parser import resolve_county_bot_targets
                resolved_targets = resolve_county_bot_targets(claim.policy_state, claim.loss_location_state)
                bot_map = {item[0]: item for item in all_bot_list}
                scrapers_to_run = [
                    bot_map[k.replace("fl_", "").replace("te_", "")]
                    for k, v in resolved_targets.items()
                    if v == "Yes" and k.replace("fl_", "").replace("te_", "") in bot_map
                ]

        if not scrapers_to_run:
            claim.record_status = RecordStatusEnum.FAILED
            claim.last_error = "No enabled county portal is available for this claim. Check Settings > Portals."
            await session.commit()
            from app.tasks.queue_runner import is_auto_queue_enabled, remove_active_queue_item_id
            remove_active_queue_item_id(claim_id)
            if is_auto_queue_enabled():
                celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")
            return

        # Check if ALL scrapers_to_run are currently in cooldown
        all_in_cooldown = True
        min_remaining = 0
        for name, *_ in scrapers_to_run:
            in_cooldown, remaining, _ = is_portal_in_cooldown(name)
            if not in_cooldown:
                all_in_cooldown = False
                break
            if min_remaining == 0 or remaining < min_remaining:
                min_remaining = remaining

        if scrapers_to_run and all_in_cooldown:
            logger.warning(f"Claim {claim_number}: All required portals are in cooldown (min {min_remaining}s). Backing off.")
            claim.record_status = RecordStatusEnum.FAILED
            claim.last_error = f"All required portals are in cooldown. Next retry in ~{min_remaining}s."
            if claim.retry_count > 0:
                claim.retry_count -= 1
            await session.commit()
            try:
                from app.tasks.queue_runner import is_auto_queue_enabled, remove_active_queue_item_id
                remove_active_queue_item_id(claim_id)
                if is_auto_queue_enabled():
                    celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")
            except Exception:
                pass
            return

        # Deduplicate Unique Names from the 3 Columns
        unique_name_items = generate_unique_names_for_claim(claim, fuzzy_threshold=0.60)
        party_pairs = [
            (p["party_type"], p.get("first_name"), p.get("last_name"))
            for p in unique_name_items
        ]
        if not any(str(last_name or "").strip() for _, _, last_name in party_pairs):
            claim.record_status = RecordStatusEnum.FAILED
            claim.last_error = "No searchable party surname was provided for court discovery."
            await session.commit()
            logger.error("Claim %s has no searchable party surname", claim_number)
            from app.tasks.queue_runner import is_auto_queue_enabled, remove_active_queue_item_id
            remove_active_queue_item_id(claim_id)
            if is_auto_queue_enabled():
                celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")
            return

        targets_preview = "\\n".join([f"  -> Target {p['search_order']}: [{p['party_type']}] '{p['full_name']}'" for p in unique_name_items])
        logger.info(
            f"Claim {claim_number}: [UNIQUE_NAMES_EXTRACTION] Extracted {len(unique_name_items)} unique search target(s):\\n"
            f"{targets_preview}\\n"
            f"  Source Columns: Insured='{claim.insured_first_name} {claim.insured_last_name}', "
            f"Driver='{claim.driver_first_name} {claim.driver_last_name}', "
            f"Claimant='{claim.claimant_first_name} {claim.claimant_last_name}'"
        )

        named_targets_summary = ", ".join([f"Target {p['search_order']}: [{p['party_type']}] '{p['full_name']}'" for p in unique_name_items])
        append_portal_execution_log(
            claim_id, "orchestrator",
            f"[PIPELINE START - FIRST ACTION] Extracted {len(unique_name_items)} unique search target(s): {named_targets_summary}. "
            f"Columns: Insured='{claim.insured_first_name} {claim.insured_last_name}', "
            f"Driver='{claim.driver_first_name} {claim.driver_last_name}', "
            f"Claimant='{claim.claimant_first_name} {claim.claimant_last_name}'"
        )

        try:
            await log_audit_event_async(
                session=session,
                action="UNIQUE_NAMES_EXTRACTED",
                entity_type="CLAIM",
                description=f"Extracted {len(unique_name_items)} unique search target(s) for claim '{claim_number}'.",
                entity_id=claim_id,
                claim_number=claim_number,
                user_id="celery_worker",
                user_email="orchestrator@system.local",
                status="SUCCESS",
                details={
                    "claim_number": claim_number,
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

        # Pre-mark active portals IN_PROGRESS (checking cooldowns)
        portal_status_map: dict[str, BotStatusEnum] = {}
        for name, scraper, status_attr, json_attr in scrapers_to_run:
            in_cooldown, remaining_seconds, *_ = is_portal_in_cooldown(name)
            if in_cooldown:
                logger.warning(
                    f"Claim {claim_number}: Portal '{name}' is in security cooldown "
                    f"({remaining_seconds:.1f}s remaining). Setting status BLOCKED."
                )
                setattr(claim, status_attr, BotStatusEnum.BLOCKED)
                portal_status_map[name] = BotStatusEnum.BLOCKED
                portal_timings.setdefault(name, {
                    "portal_name": scraper.county_name,
                    "url": scraper.base_url,
                    "start_time": datetime.now().isoformat(),
                    "cases_found": 0,
                    "status": "BLOCKED",
                    "error": f"Portal in security cooldown ({int(remaining_seconds)}s remaining)",
                })
                continue

            setattr(claim, status_attr, BotStatusEnum.IN_PROGRESS)
            portal_status_map[name] = BotStatusEnum.IN_PROGRESS
            portal_timings.setdefault(name, {
                "portal_name": scraper.county_name,
                "url": scraper.base_url,
                "start_time": datetime.now().isoformat(),
                "cases_found": 0,
                "status": "IN_PROGRESS",
            })
        claim.modified_by = "worker:scrapers"
        await session.commit()

        try:
            await log_audit_event_async(
                session=session,
                action="SCRAPING_STARTED",
                entity_type="CLAIM",
                description=f"Automated browser scraping initiated across {len(scrapers_to_run)} portal(s) for {len(unique_name_items)} unique party target(s) for claim '{claim_number}'.",
                entity_id=claim_id,
                claim_number=claim_number,
                user_id="celery_worker",
                user_email="orchestrator@system.local",
                status="SUCCESS",
                details={
                    "portals": [s[0] for s in scrapers_to_run],
                    "unique_name_count": len(unique_name_items),
                },
            )
            await session.commit()
        except Exception as e_audit_start:
            logger.warning(f"Could not log audit event for scraping start: {e_audit_start}")

    # ── PHASE 2: BROWSER AUTOMATION (Zero active DB sessions held) ──────────────
    proxy_server = None
    proxy_username = None
    proxy_password = None
    if proxy_cfg.enabled and proxy_cfg.host:
        proxy_server = f"http://{proxy_cfg.host}:{proxy_cfg.port}"
        proxy_username = proxy_cfg.username or None
        proxy_password = proxy_cfg.password or None

    max_concurrency = max(1, getattr(auto_cfg, "max_concurrent_claims", 1) or 1)
    slot_acquired = await _acquire_browser_slot(max_concurrency, claim_number)
    if not slot_acquired:
        async with TaskAsyncSessionLocal() as session:
            claim = await session.get(ClaimRecord, claim_id)
            if claim:
                claim.record_status = RecordStatusEnum.FAILED
                claim.last_error = (
                    f"Fleet concurrency limit reached (max={max_concurrency}). "
                    "Claim timed out waiting for an available browser slot."
                )
                await session.commit()
        try:
            from app.tasks.queue_runner import (
                is_auto_queue_enabled,
                remove_active_queue_item_id,
            )
            remove_active_queue_item_id(claim_id)
            if is_auto_queue_enabled():
                celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")
        except Exception:
            pass
        return

    # Pre-Flight: Ensure AntiCaptcha is verified, configured, and pinned
    try:
        from app.automation.browser_manager import ChromeSession, ExtensionManager
        ext_path = ExtensionManager.resolve_extension_path(auto_cfg.chrome_extension_dir)
        engine_key = (auto_cfg.browser_engine or "chrome").lower()
        persistent_dir = ChromeSession.get_persistent_profile_dir(engine_key)
        ChromeSession.configure_and_pin_profile(
            profile_dir=persistent_dir,
            api_key=auto_cfg.anticaptcha_api_key,
            extension_path=ext_path,
            auto_cfg=auto_cfg,
        )
        logger.info(
            f"[ScraperTasks] Pre-flight: AntiCaptcha extension automatically configured & pinned "
            f"for claim {claim_number}"
        )
    except Exception as e_pre_ext:
        logger.warning(f"[ScraperTasks] Note during automated pre-flight extension pinning: {e_pre_ext}")

    portal_results: dict[str, list[dict]] = {name: [] for name, *_ in scrapers_to_run}
    portal_stages: dict[str, dict] = {name: {} for name, *_ in scrapers_to_run}
    portal_active_duration: dict[str, float] = {name: 0.0 for name, *_ in scrapers_to_run}
    portal_start_iso: dict[str, str] = {name: datetime.now().isoformat() for name, *_ in scrapers_to_run}
    overall_scraping_start_t = time.perf_counter()
    database_save_seconds = 0.0
    database_save_started_at = None
    database_save_finished_at = None
    total_scraped_cases = []

    try:
        rpa_mode_label = "ATTENDED (VISIBLE GUI)" if not auto_cfg.headless_mode else "UNATTENDED (HEADLESS BACKGROUND)"
        engine_label = getattr(auto_cfg, "browser_engine", "chrome").upper()
        portals_list_str = ", ".join([s[0] for s in scrapers_to_run])
        logger.info(
            f"\\n=======================================================\\n"
            f" CLAIM {claim_number} - RPA AUTOMATION LAUNCHING\\n"
            f" MODE:    {rpa_mode_label}\\n"
            f" ENGINE:  {engine_label}\\n"
            f" PORTALS ({len(scrapers_to_run)}): {portals_list_str}\\n"
            f"======================================================="
        )

        browser_runner_kwargs = {
            "headless": auto_cfg.headless_mode,
            "timeout_ms": auto_cfg.page_timeout_seconds * 1000,
            "use_chrome": auto_cfg.use_chrome_browser,
            "extension_dir": auto_cfg.chrome_extension_dir,
            "anticaptcha_api_key": auto_cfg.anticaptcha_api_key,
            "anticaptcha_settings": auto_cfg,
            "user_data_dir": auto_cfg.chrome_user_data_dir,
            "user_agent": auto_cfg.user_agent,
            "proxy_server": proxy_server,
            "proxy_username": proxy_username,
            "proxy_password": proxy_password,
            "typing_speed_mode": getattr(auto_cfg, "typing_speed_mode", "turbo"),
            "typing_delay_ms": getattr(auto_cfg, "typing_delay_ms", 0),
            "action_pacing_ms": getattr(auto_cfg, "action_pacing_ms", 100),
            "stealth_clicks": getattr(auto_cfg, "stealth_clicks", False),
            "browser_engine": getattr(auto_cfg, "browser_engine", "chrome"),
            "chrome_binary_path": getattr(auto_cfg, "chrome_binary_path", None),
            "worker_id": str(claim_id),
            "isolated_profile": (max_concurrency > 1),
        }

        browser_session_runner = SingleSessionBrowserRunner(**browser_runner_kwargs)
        async with browser_session_runner as browser_session:
            stages.update(browser_session.stage_timings)

            # Step 1: Pre-open tabs for active portals
            for name, scraper, status_attr, json_attr in scrapers_to_run:
                if portal_status_map.get(name) in (BotStatusEnum.BLOCKED, BotStatusEnum.FAILED):
                    continue
                in_cooldown, _, *_ = is_portal_in_cooldown(name)
                if not in_cooldown:
                    await browser_session.get_or_create_tab(portal_key=name, url=scraper.base_url)

            # Step 2: Iterate unique party names across pre-opened portal tabs
            for name_idx, party_item in enumerate(unique_name_items, start=1):
                f_name = party_item.get("first_name")
                l_name = party_item.get("last_name")
                party_label = party_item.get("party_type", "Party")
                party_full = party_item.get("full_name") or f"{f_name or ''} {l_name or ''}".strip()

                if not l_name or not str(l_name).strip():
                    continue

                search_dol = dol

                logger.info(
                    f"\\n═══════════════════════════════════════════════════════\\n"
                    f" CLAIM {claim_number} - UNIQUE NAME {name_idx}/{len(unique_name_items)}\\n"
                    f" TARGET: [{party_label}] '{party_full}' (DOL: {search_dol or 'None'})\\n"
                    f" PORTALS ({len(scrapers_to_run)}): {portals_list_str}\\n"
                    f"═══════════════════════════════════════════════════════"
                )
                append_portal_execution_log(
                    claim_id, "orchestrator",
                    f"Searching Unique Name {name_idx}/{len(unique_name_items)} [{party_label}] '{party_full}' across active portal tabs"
                )

                for portal_idx, (name, scraper, status_attr, json_attr) in enumerate(scrapers_to_run, start=1):
                    if portal_status_map.get(name) == BotStatusEnum.BLOCKED:
                        logger.info(f"Claim {claim_number}: Skipping portal '{name}' (portal BLOCKED / in cooldown)")
                        continue
                    if portal_status_map.get(name) == BotStatusEnum.FAILED:
                        logger.info(f"Claim {claim_number}: Skipping portal '{name}' (portal already marked FAILED)")
                        continue

                    in_cooldown, remaining_seconds, *_ = is_portal_in_cooldown(name)
                    if in_cooldown:
                        logger.warning(
                            f"Claim {claim_number}: Portal '{name}' entered cooldown "
                            f"({remaining_seconds:.1f}s remaining). Marking BLOCKED."
                        )
                        portal_status_map[name] = BotStatusEnum.BLOCKED
                        portal_timings[name]["status"] = "BLOCKED"
                        portal_timings[name]["error"] = f"Cooldown active ({int(remaining_seconds)}s)"
                        continue

                    logger.info(
                        f"Claim {claim_number}: [{scraper.county_name}] Searching Unique Name {name_idx}/{len(unique_name_items)} "
                        f"[{party_label}: {party_full}] (Portal {portal_idx}/{len(scrapers_to_run)})"
                    )
                    append_portal_execution_log(
                        claim_id, name,
                        f"Searching Unique Name {name_idx}/{len(unique_name_items)} [{party_label}] '{party_full}' (DOL: {search_dol or 'None'})"
                    )

                    tab = await browser_session.get_or_create_tab(portal_key=name, url=scraper.base_url)
                    try:
                        await tab.bring_to_front()
                    except Exception:
                        pass

                    t_portal_iter_start = time.perf_counter()
                    try:
                        cases = await scraper.search_on_page(
                            page=tab,
                            first_name=f_name,
                            last_name=l_name,
                            date_of_loss=search_dol,
                        )
                        append_portal_execution_log(
                            claim_id, name,
                            f"Completed search for Unique Name {name_idx} [{party_label}] '{party_full}'. Returned {len(cases)} case(s)"
                        )

                        for c in cases:
                            try:
                                clean_case = canonical_portal_case(name, c)
                                portal_results[name].append(clean_case)
                            except ValueError as val_err:
                                logger.warning(
                                    f"Claim {claim_number}: Discarding invalid case row from {name}: {c}. Reason: {val_err}"
                                )

                        if len(cases) > 0 and getattr(runtime_settings.storage, "capture_error_screenshots", True):
                            try:
                                ss_meta = await scraper.capture_discovery_screenshot(
                                    page=tab,
                                    claim_id=claim_id,
                                    portal_key=name,
                                    cases_count=len(cases),
                                    party_name=party_full,
                                )
                                if ss_meta:
                                    screenshot_record = ErrorScreenshot(
                                        claim_id=claim_id,
                                        portal_key=name,
                                        portal_name=scraper.county_name,
                                        page_url=ss_meta.get("page_url"),
                                        page_title=ss_meta.get("page_title"),
                                        exception_message=ss_meta.get("exception_message"),
                                        attempt_number=1,
                                        storage_provider=ss_meta.get("storage_provider", "local"),
                                        file_path=ss_meta.get("file_path", ""),
                                    )
                                    async with TaskAsyncSessionLocal() as sc_session:
                                        sc_session.add(screenshot_record)
                                        await sc_session.commit()
                            except Exception as ss_ex:
                                logger.debug(f"Discovery screenshot recording notice for {name}: {ss_ex}")

                        if hasattr(scraper, "stage_timings") and scraper.stage_timings:
                            browser_session.stage_timings.update(scraper.stage_timings)
                            stages.update(scraper.stage_timings)
                            portal_stages[name].update(scraper.stage_timings)
                            scraper.stage_timings = {}

                        try:
                            if hasattr(scraper, "return_to_search_state"):
                                res_rst = scraper.return_to_search_state(tab)
                                if inspect.isawaitable(res_rst):
                                    await res_rst
                        except Exception as e_reset:
                            logger.warning(f"Claim {claim_number}: [{scraper.county_name}] return_to_search_state notice: {e_reset}")

                    except SecurityBlockException as sbe:
                        logger.warning(
                            f"Claim {claim_number}: Security block detected on {name} "
                            f"during Unique Name {name_idx} [{party_label}: {party_full}]: {sbe.message}"
                        )
                        portal_status_map[name] = BotStatusEnum.BLOCKED
                        portal_timings[name]["status"] = "BLOCKED"
                        portal_timings[name]["error"] = sbe.message
                        set_portal_cooldown(name, sbe.cooldown_seconds, sbe.message)
                        append_portal_execution_log(claim_id, name, f"Security block detected on Unique Name {name_idx}: {sbe.message}", level="ERROR")

                        tab = browser_session.tabs.get(name)
                        if tab and not tab.is_closed():
                            try:
                                ss_meta = await scraper.capture_screenshot_on_error(
                                    page=tab,
                                    claim_id=claim_id,
                                    portal_key=name,
                                    attempt=1,
                                    error=sbe,
                                )
                                if ss_meta:
                                    screenshot_record = ErrorScreenshot(
                                        claim_id=claim_id,
                                        portal_key=ss_meta["portal_key"],
                                        portal_name=ss_meta["portal_name"],
                                        page_url=ss_meta.get("page_url"),
                                        page_title=ss_meta.get("page_title"),
                                        exception_message=f"SECURITY_BLOCK: {sbe.message}",
                                        attempt_number=1,
                                        storage_provider=ss_meta.get("storage_provider", "local"),
                                        file_path=ss_meta["file_path"],
                                    )
                                    async with TaskAsyncSessionLocal() as err_session:
                                        err_session.add(screenshot_record)
                                        await err_session.commit()
                            except Exception as ss_ex:
                                logger.warning(f"Could not capture security block screenshot for {name}: {ss_ex}")

                    except Exception as e:
                        logger.error(
                            f"Claim {claim_number}: Scraper error for {name} "
                            f"on Unique Name {name_idx} [{party_label}: {party_full}]: {e}"
                        )
                        portal_status_map[name] = BotStatusEnum.FAILED
                        portal_timings[name]["status"] = "FAILED"
                        portal_timings[name]["error"] = str(e)
                        append_portal_execution_log(claim_id, name, f"Error during search for Unique Name {name_idx}: {e}", level="ERROR")

                        try:
                            import traceback
                            record_audit_event_background(
                                action="PORTAL_SCRAPING_EXCEPTION",
                                entity_type="CLAIM",
                                description=f"{scraper.county_name} scraper failure on Unique Name {name_idx} '{party_label}': {e}",
                                entity_id=claim_id,
                                claim_number=claim_number,
                                user_id="celery_worker",
                                user_email="worker:scrapers",
                                status="FAILURE",
                                details={
                                    "portal_key": name,
                                    "portal_name": scraper.county_name,
                                    "unique_name_index": name_idx,
                                    "party": party_label,
                                    "party_name": party_full,
                                    "error": str(e),
                                    "exception_type": type(e).__name__,
                                    "traceback": traceback.format_exc(),
                                },
                            )
                        except Exception as e_aud_p:
                            logger.warning(f"Could not log audit exception for portal {name}: {e_aud_p}")

                        tab = browser_session.tabs.get(name)
                        if tab and not tab.is_closed():
                            try:
                                ss_meta = await scraper.capture_screenshot_on_error(
                                    page=tab,
                                    claim_id=claim_id,
                                    portal_key=name,
                                    attempt=1,
                                    error=e,
                                )
                                if ss_meta:
                                    screenshot_record = ErrorScreenshot(
                                        claim_id=claim_id,
                                        portal_key=ss_meta["portal_key"],
                                        portal_name=ss_meta["portal_name"],
                                        page_url=ss_meta.get("page_url"),
                                        page_title=ss_meta.get("page_title"),
                                        exception_message=ss_meta.get("exception_message"),
                                        attempt_number=ss_meta.get("attempt_number", 1),
                                        storage_provider=ss_meta.get("storage_provider", "local"),
                                        file_path=ss_meta["file_path"],
                                    )
                                    async with TaskAsyncSessionLocal() as err_session:
                                        err_session.add(screenshot_record)
                                        await err_session.commit()
                            except Exception as ss_ex:
                                logger.warning(f"Could not capture error screenshot for {name}: {ss_ex}")
                    finally:
                        portal_active_duration[name] += time.perf_counter() - t_portal_iter_start

            logger.info(
                f"Claim {claim_number}: Completed searches across all {len(unique_name_items)} unique party targets. "
                "Closing browser session."
            )
            append_portal_execution_log(
                claim_id, "orchestrator",
                f"Completed searches across all {len(unique_name_items)} unique party targets. Browser session closing."
            )

        # ── PHASE 3: DB PERSISTENCE OF RESULTS (Short-lived session < 15ms) ──────
        async with TaskAsyncSessionLocal() as session:
            claim = await session.get(ClaimRecord, claim_id)
            if not claim:
                logger.error(f"Claim {claim_id} was removed concurrently.")
                return

            for name, scraper, status_attr, json_attr in scrapers_to_run:
                cases = portal_results[name]
                duration = round(portal_active_duration[name], 2)
                current_portal_status = portal_status_map.get(name, BotStatusEnum.IN_PROGRESS)
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
                append_portal_execution_log(
                    claim_id, name,
                    f"Completed portal scraping with status {final_status_str}. Total cases found: {len(cases)}. Duration: {duration}s"
                )

                if current_portal_status not in (BotStatusEnum.FAILED, BotStatusEnum.BLOCKED):
                    portal_timings[name].pop("error", None)
                    save_started = time.perf_counter()
                    if database_save_started_at is None:
                        database_save_started_at = datetime.now()
                    await session.execute(
                        delete(ScrapedCourtCase).where(
                            ScrapedCourtCase.claim_id == claim.id,
                            ScrapedCourtCase.county_name == scraper.county_name,
                        )
                    )
                    for case in cases:
                        scraped_case = ScrapedCourtCase(
                            claim_id=claim.id,
                            county_name=scraper.county_name,
                            county_website=scraper.base_url,
                            case_number=case["CaseNumber"],
                            case_style=case["CaseStyle"],
                            filing_date=case["FilingDate"],
                            case_status=case["CaseStatus"],
                            case_type=case.get("CaseType"),
                            raw_payload=case,
                        )
                        session.add(scraped_case)
                        total_scraped_cases.append(scraped_case)
                    setattr(claim, json_attr, cases)
                    setattr(claim, status_attr, BotStatusEnum.COMPLETED if cases else BotStatusEnum.NO_MATCH_FOUND)
                else:
                    setattr(claim, status_attr, current_portal_status)

                scraper_stages = dict(portal_stages.get(name, {}))
                if hasattr(scraper, "stage_timings") and scraper.stage_timings:
                    scraper_stages.update(scraper.stage_timings)
                portal_timings[name]["stages"] = scraper_stages
                if scraper_stages:
                    stages.update(scraper_stages)

                if current_portal_status not in (BotStatusEnum.FAILED, BotStatusEnum.BLOCKED):
                    database_save_seconds += time.perf_counter() - save_started
                    database_save_finished_at = datetime.now()

            stages["database_save"] = {
                "name": "Database Save",
                "start_time": database_save_started_at.strftime("%H:%M:%S.%f")[:-3] if database_save_started_at else None,
                "end_time": database_save_finished_at.strftime("%H:%M:%S.%f")[:-3] if database_save_finished_at else None,
                "duration_seconds": round(database_save_seconds, 3),
                "status": "SUCCESS" if database_save_started_at else "SKIPPED",
                "cases_saved": len(total_scraped_cases),
            }

            timings["portals"] = copy.deepcopy(portal_timings)
            timings["total_scraping_seconds"] = round(time.perf_counter() - overall_scraping_start_t, 2)
            claim.total_duration_seconds = timings["total_scraping_seconds"]
            claim.action_timings = copy.deepcopy(timings)
            flag_modified(claim, "action_timings")

            active_scrapers = scrapers_to_run if scrapers_to_run else all_bot_list
            has_failed_portals = any(
                getattr(claim, s[2]) in (BotStatusEnum.FAILED, BotStatusEnum.BLOCKED) for s in active_scrapers
            )
            claim.record_status = RecordStatusEnum.FAILED if has_failed_portals else RecordStatusEnum.SCRAPING_COMPLETED
            if not has_failed_portals:
                claim.last_error = None
            claim.modified_by = "worker:scrapers"
            try:
                await log_audit_event_async(
                    session=session,
                    action="SCRAPING_COMPLETED" if not has_failed_portals else "SCRAPING_FAILED",
                    entity_type="CLAIM",
                    description=f"Court scraper automation completed with {len(total_scraped_cases)} cases found across {len(scrapers_to_run)} portals.",
                    entity_id=claim.id,
                    claim_number=claim.claim_number,
                    user_id="celery_worker",
                    user_email="worker:scrapers",
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
                try:
                    from app.tasks.queue_runner import (
                        is_auto_queue_enabled,
                        remove_active_queue_item_id,
                    )
                    remove_active_queue_item_id(claim.id)
                    if is_auto_queue_enabled():
                        celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")
                        if queue_cfg.auto_retry_failed_scrapes and (claim.retry_count or 0) < queue_cfg.max_task_retries:
                            retry_delay = max(1, getattr(queue_cfg, "task_retry_delay_seconds", 30))
                            logger.info(
                                f"Claim {claim.claim_number}: Scheduled auto-retry advance task in {retry_delay}s "
                                f"(attempt {claim.retry_count or 0}/{queue_cfg.max_task_retries})"
                            )
                            celery_app.send_task(
                                "app.tasks.queue_runner.advance_auto_queue_task",
                                queue="default",
                                countdown=retry_delay,
                            )
                except Exception as auto_q_exc:
                    logger.warning(f"Could not advance auto-queue after browser failure: {auto_q_exc}")
            else:
                celery_app.send_task(
                    "app.tasks.fuzzy_tasks.evaluate_fuzzy_matches_task",
                    args=[claim.id],
                    queue="matcher",
                )
    except Exception as session_exc:
        logger.error(f"Browser automation session failure for Claim {claim_number}: {session_exc}", exc_info=True)
        try:
            async with TaskAsyncSessionLocal() as session:
                claim = await session.get(ClaimRecord, claim_id)
                if claim:
                    cases_q = select(func.count(ScrapedCourtCase.id)).where(ScrapedCourtCase.claim_id == claim.id)
                    cases_count_res = await session.execute(cases_q)
                    extracted_cases_count = cases_count_res.scalar() or 0

                    for name, scraper, status_attr, json_attr in scrapers_to_run:
                        if portal_status_map.get(name) == BotStatusEnum.IN_PROGRESS:
                            setattr(claim, status_attr, BotStatusEnum.FAILED)

                    claim.modified_by = "worker:scrapers"
                    try:
                        active_elapsed = round(time.perf_counter() - overall_scraping_start_t, 2)
                        timings["total_scraping_seconds"] = active_elapsed
                        claim.total_duration_seconds = active_elapsed
                        claim.action_timings = copy.deepcopy(timings)
                        flag_modified(claim, "action_timings")
                    except Exception:
                        pass

                    if extracted_cases_count > 0:
                        logger.warning(
                            f"Claim {claim.claim_number} encountered browser session error ({session_exc}), "
                            f"but {extracted_cases_count} court cases were already extracted. "
                            f"Preserving extracted data and advancing to fuzzy matching."
                        )
                        claim.last_error = f"Partial session warning: {session_exc!s}"
                        if claim.record_status not in (RecordStatusEnum.MATCH_FOUND, RecordStatusEnum.NO_MATCH_FOUND, RecordStatusEnum.COMPLETED):
                            claim.record_status = RecordStatusEnum.SCRAPING_COMPLETED

                        celery_app.send_task(
                            "app.tasks.fuzzy_tasks.evaluate_fuzzy_matches_task",
                            args=[claim.id],
                            queue="matcher",
                        )
                    else:
                        claim.record_status = RecordStatusEnum.FAILED
                        claim.last_error = f"Browser session failure: {session_exc!s}"
                    try:
                        import traceback
                        await log_audit_event_async(
                            session=session,
                            action="SCRAPING_SESSION_FAILED",
                            entity_type="CLAIM",
                            description=f"Browser automation session failure for Claim {claim.claim_number}: {session_exc}",
                            entity_id=claim.id,
                            claim_number=claim.claim_number,
                            user_id="celery_worker",
                            user_email="worker:scrapers",
                            status="FAILED",
                            details={
                                "error": str(session_exc),
                                "exception_type": type(session_exc).__name__,
                                "traceback": traceback.format_exc(),
                            },
                        )
                    except Exception as e_aud:
                        logger.warning(f"Could not log audit event for scraper session failure: {e_aud}")
                    await session.commit()
        except Exception as e_rec:
            logger.error(f"Error persisting session failure for claim {claim_number}: {e_rec}")

        try:
            from app.tasks.queue_runner import (
                is_auto_queue_enabled,
                remove_active_queue_item_id,
            )
            remove_active_queue_item_id(claim_id)
            if is_auto_queue_enabled():
                celery_app.send_task("app.tasks.queue_runner.advance_auto_queue_task", queue="default")
                if queue_cfg.auto_retry_failed_scrapes and (retry_count or 0) < queue_cfg.max_task_retries:
                    retry_delay = max(1, getattr(queue_cfg, "task_retry_delay_seconds", 30))
                    logger.info(
                        f"Claim {claim_number}: Scheduled auto-retry advance task in {retry_delay}s "
                        f"following session failure (attempt {retry_count or 0}/{queue_cfg.max_task_retries})"
                    )
                    celery_app.send_task(
                        "app.tasks.queue_runner.advance_auto_queue_task",
                        queue="default",
                        countdown=retry_delay,
                    )
        except Exception as auto_q_exc:
            logger.warning(f"Could not advance auto-queue after browser failure: {auto_q_exc}")
    finally:
        await _release_browser_slot(claim_number)
'''

patched_content = content[:start_idx] + new_func + "\n\n" + content[end_idx:]
FILE_PATH.write_text(patched_content, encoding="utf-8")
print("Successfully patched scraper_tasks.py")
