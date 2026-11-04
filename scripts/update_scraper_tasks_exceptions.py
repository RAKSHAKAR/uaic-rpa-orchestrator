"""Update scraper_tasks.py with CaptchaResolutionError handling and operational state tracking."""

from pathlib import Path

scraper_tasks_path = Path("backend/app/tasks/scraper_tasks.py")
text = scraper_tasks_path.read_text(encoding="utf-8")

# 1. Update imports
old_imports = """from app.automation.base import (
    SecurityBlockException,
    append_portal_execution_log,
)"""

new_imports = """from app.automation.base import (
    CaptchaResolutionError,
    SecurityBlockException,
    append_portal_execution_log,
)
from app.services.error_classifier import ErrorCategory, ErrorCode, classify_exception"""

if old_imports in text:
    text = text.replace(old_imports, new_imports, 1)
    print("SUCCESS: Updated imports in scraper_tasks.py")
else:
    print("WARNING: old_imports not found.")

# Update cooldown_service imports
old_cd_import = """from app.services.cooldown_service import (
    is_portal_in_cooldown,
    set_portal_cooldown,
)"""

new_cd_import = """from app.services.cooldown_service import (
    PortalOperationalState,
    check_portal_ready_for_redispatch,
    is_portal_in_cooldown,
    set_portal_cooldown,
    set_portal_operational_state,
)"""

if old_cd_import in text:
    text = text.replace(old_cd_import, new_cd_import, 1)
    print("SUCCESS: Updated cooldown_service imports in scraper_tasks.py")
else:
    print("WARNING: old_cd_import not found.")

# 2. Update SecurityBlockException block to record operational state
old_sbe_block = """                        set_portal_cooldown(name, sbe.cooldown_seconds, sbe.message)

                        append_portal_execution_log(
                            claim_id,
                            name,
                            f"Security block detected on Unique Name {name_idx}: {sbe.message}",
                            level="ERROR",
                        )"""

new_sbe_block = """                        set_portal_cooldown(name, sbe.cooldown_seconds, sbe.message)

                        op_state = (
                            PortalOperationalState.RATE_LIMITED
                            if "rate limit" in sbe.message.lower() or "429" in sbe.message
                            else PortalOperationalState.WAF_BLOCKED
                        )
                        err_code = (
                            ErrorCode.WAF_RATE_LIMIT.value
                            if op_state == PortalOperationalState.RATE_LIMITED
                            else (
                                ErrorCode.WAF_PERIMETERX.value
                                if "perimeterx" in sbe.message.lower()
                                else ErrorCode.WAF_GENERIC_BLOCK.value
                            )
                        )
                        set_portal_operational_state(
                            portal_key=name,
                            state=op_state,
                            error_code=err_code,
                            error_category=ErrorCategory.WAF_SECURITY.value,
                            blocking_reason=sbe.message,
                            claim_id=claim_id,
                            cooldown_seconds=sbe.cooldown_seconds,
                        )

                        append_portal_execution_log(
                            claim_id,
                            name,
                            f"Security block detected on Unique Name {name_idx}: {sbe.message}",
                            level="ERROR",
                        )"""

if old_sbe_block in text:
    text = text.replace(old_sbe_block, new_sbe_block, 1)
    print("SUCCESS: Updated SecurityBlockException handler in scraper_tasks.py")
else:
    print("WARNING: old_sbe_block not found.")

# 3. Add explicit CaptchaResolutionError handler right before `except Exception as e:`
old_generic_exc = """                    except Exception as e:
                        logger.error(
                            f"Claim {claim_number}: Scraper error for {name} "
                            f"on Unique Name {name_idx} [{party_label}: {party_full}]: {e}"
                        )"""

new_captcha_and_generic_exc = """                    except CaptchaResolutionError as cre:
                        logger.error(
                            f"Claim {claim_number}: [{scraper.county_name}] CAPTCHA verification failed "
                            f"on Unique Name {name_idx} [{party_label}: {party_full}]: {cre}"
                        )

                        portal_status_map[name] = BotStatusEnum.FAILED
                        portal_timings[name]["status"] = "FAILED"
                        portal_timings[name]["error"] = str(cre)
                        portal_timings[name]["error_code"] = ErrorCode.CAPTCHA_MAX_ATTEMPTS.value
                        portal_timings[name]["requires_human_intervention"] = True

                        set_portal_operational_state(
                            portal_key=name,
                            state=PortalOperationalState.AWAITING_HUMAN,
                            error_code=ErrorCode.CAPTCHA_MAX_ATTEMPTS.value,
                            error_category=ErrorCategory.CAPTCHA.value,
                            blocking_reason=str(cre),
                            claim_id=claim_id,
                            human_intervention=True,
                        )

                        append_portal_execution_log(
                            claim_id,
                            name,
                            f"CAPTCHA verification failed on attempt {name_idx}: {cre}",
                            level="ERROR",
                        )

                        tab = browser_session.tabs.get(name)
                        if tab and not tab.is_closed():
                            try:
                                ss_meta = await scraper.capture_screenshot_on_error(
                                    page=tab,
                                    claim_id=claim_id,
                                    portal_key=name,
                                    attempt=getattr(scraper, "max_attempts", 2),
                                    error=cre,
                                )
                                if ss_meta:
                                    screenshot_record = ErrorScreenshot(
                                        claim_id=claim_id,
                                        portal_key=ss_meta["portal_key"],
                                        portal_name=ss_meta["portal_name"],
                                        page_url=ss_meta.get("page_url"),
                                        page_title=ss_meta.get("page_title"),
                                        exception_message=f"CAPTCHA_RESOLUTION_ERROR: {cre}",
                                        attempt_number=getattr(scraper, "max_attempts", 2),
                                        storage_provider=ss_meta.get("storage_provider", "local"),
                                        file_path=ss_meta["file_path"],
                                    )
                                    async with TaskAsyncSessionLocal() as err_session:
                                        err_session.add(screenshot_record)
                                        await err_session.commit()
                            except Exception as ss_ex:
                                logger.warning(
                                    f"Could not capture CAPTCHA error screenshot for {name}: {ss_ex}"
                                )

                    except Exception as e:
                        logger.error(
                            f"Claim {claim_number}: Scraper error for {name} "
                            f"on Unique Name {name_idx} [{party_label}: {party_full}]: {e}"
                        )"""

if old_generic_exc in text:
    text = text.replace(old_generic_exc, new_captcha_and_generic_exc, 1)
    print("SUCCESS: Added CaptchaResolutionError handler in scraper_tasks.py")
else:
    print("WARNING: old_generic_exc not found.")

scraper_tasks_path.write_text(text, encoding="utf-8")
print("Done updating scraper_tasks.py")

