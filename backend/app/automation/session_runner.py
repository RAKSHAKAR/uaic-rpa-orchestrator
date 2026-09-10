"""Single-Session Multi-Tab Browser Automation Runner for Claim Portals."""

import asyncio
import logging
import os
import shutil
import tempfile
from datetime import datetime
from typing import Any

from playwright.async_api import BrowserContext, Page, async_playwright

from app.automation.base import (
    BaseCourtScraper,
    find_chrome_executable,
    resolve_extension_dir,
    sync_anticaptcha_api_key,
)
from app.core.config import settings

logger = logging.getLogger("uaic_orchestrator.automation.session_runner")


def derive_search_counts(claim: Any) -> tuple[int, int]:
    """
    Derives DualSearch and TripleSearch count configuration matching Power Automate V4:
    - Insured == Driver == Claimant: (1, 1) -> 1 search (Insured)
    - Insured == Driver, Claimant !=: (1, 3) -> 2 searches (Insured, Claimant)
    - Insured == Claimant, Driver !=: (2, 1) -> 2 searches (Insured, Driver)
    - Driver == Claimant, Insured !=: (2, 1) -> 2 searches (Insured, Driver)
    - All different: (2, 3) -> 3 searches (Insured, Driver, Claimant)
    """
    ins_first = (getattr(claim, "insured_first_name", "") or "").strip().lower()
    ins_last = (getattr(claim, "insured_last_name", "") or "").strip().lower()
    drv_first = (getattr(claim, "driver_first_name", "") or "").strip().lower()
    drv_last = (getattr(claim, "driver_last_name", "") or "").strip().lower()
    clm_first = (getattr(claim, "claimant_first_name", "") or "").strip().lower()
    clm_last = (getattr(claim, "claimant_last_name", "") or "").strip().lower()

    ins_name = f"{ins_first} {ins_last}".strip()
    drv_name = f"{drv_first} {drv_last}".strip()
    clm_name = f"{clm_first} {clm_last}".strip()

    ins_eq_drv = bool(ins_name and drv_name and ins_name == drv_name)
    ins_eq_clm = bool(ins_name and clm_name and ins_name == clm_name)
    drv_eq_clm = bool(drv_name and clm_name and drv_name == clm_name)

    if ins_eq_drv and ins_eq_clm:
        return 1, 1
    elif ins_eq_drv and not ins_eq_clm:
        return 1, 3
    elif ins_eq_clm and not ins_eq_drv or drv_eq_clm and not ins_eq_drv:
        return 2, 1
    else:
        return 2, 3


def get_search_party_pairs(claim: Any, dual_search: int, triple_search: int) -> list[tuple[str, str | None, str | None]]:
    """Builds ordered list of (party_type, first_name, last_name) based on V4 logic."""
    parties = []

    # 1. Primary: Insured
    if getattr(claim, "insured_last_name", None):
        parties.append(("Insured", claim.insured_first_name, claim.insured_last_name))

    # 2. Dual Search: Driver (if dual_search == 2)
    if dual_search == 2 and getattr(claim, "driver_last_name", None):
        drv_pair = ("Driver", claim.driver_first_name, claim.driver_last_name)
        if drv_pair not in parties:
            parties.append(drv_pair)

    # 3. Triple Search: Claimant (if triple_search == 3)
    if triple_search == 3 and getattr(claim, "claimant_last_name", None):
        clm_pair = ("Claimant", claim.claimant_first_name, claim.claimant_last_name)
        if clm_pair not in parties:
            parties.append(clm_pair)

    # Fallback if no valid parties found
    if not parties:
        for p_label, f_attr, l_attr in [
            ("Claimant", "claimant_first_name", "claimant_last_name"),
            ("Insured", "insured_first_name", "insured_last_name"),
            ("Driver", "driver_first_name", "driver_last_name"),
        ]:
            l_val = getattr(claim, l_attr, None)
            if l_val and str(l_val).strip():
                parties.append((p_label, getattr(claim, f_attr, None), l_val))
                break

    return parties


class SingleSessionBrowserRunner:
    """
    Manages a single Google Chrome browser session across multiple portal tabs for a claim.
    Eliminates closing and reopening Chrome between websites.
    """

    def __init__(
        self,
        headless: bool = False,
        timeout_ms: int = 30000,
        use_chrome: bool = True,
        extension_dir: str | None = None,
        anticaptcha_api_key: str | None = None,
        user_data_dir: str | None = None,
        user_agent: str | None = None,
    ):
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.use_chrome = use_chrome
        self.extension_dir = resolve_extension_dir(extension_dir)
        self.anticaptcha_api_key = anticaptcha_api_key
        self.user_data_dir = user_data_dir
        self.user_agent = user_agent
        self.playwright = None
        self.context: BrowserContext | None = None
        self.tabs: dict[str, Page] = {}
        self.profile_to_use: str | None = None
        self.is_temp_profile: bool = False
        self.stage_timings: dict[str, Any] = {}

    async def __aenter__(self):
        cache_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "browser_cache"))
        os.makedirs(cache_dir, exist_ok=True)

        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--window-position=50,50",
            f"--disk-cache-dir={cache_dir}",
        ]

        ext_dir = self.extension_dir
        has_extension = bool(ext_dir and os.path.exists(ext_dir))
        ext_norm = os.path.normpath(str(ext_dir)) if has_extension else None

        if self.anticaptcha_api_key and has_extension:
            sync_anticaptcha_api_key(ext_norm, self.anticaptcha_api_key)

        if has_extension and ext_norm:
            launch_args.append(f"--disable-extensions-except={ext_norm}")
            launch_args.append(f"--load-extension={ext_norm}")
            launch_args.append("--no-sandbox")

        target_user_dir = (self.user_data_dir or "").strip()
        if "Users\\Default" in target_user_dir:
            target_user_dir = ""

        if target_user_dir and os.path.exists(target_user_dir):
            self.profile_to_use = target_user_dir
        else:
            self.profile_to_use = tempfile.mkdtemp(prefix="uaic_chrome_profile_")
            self.is_temp_profile = True

        executable_path = find_chrome_executable() if self.use_chrome else None
        channel = "chrome" if (self.use_chrome and not executable_path) else None
        is_headless = self.headless
        if is_headless and has_extension:
            launch_args.append("--headless=new")

        t_start = datetime.now()
        self.playwright = await async_playwright().start()

        launch_kwargs = {
            "user_data_dir": self.profile_to_use,
            "headless": is_headless,
            "args": launch_args,
            "ignore_default_args": ["--disable-extensions"] if has_extension else None,
            "no_viewport": True if not is_headless else False,
            "viewport": {"width": settings.PLAYWRIGHT_VIEWPORT_WIDTH, "height": settings.PLAYWRIGHT_VIEWPORT_HEIGHT} if is_headless else None,
        }
        if self.user_agent:
            launch_kwargs["user_agent"] = self.user_agent
        if executable_path:
            launch_kwargs["executable_path"] = executable_path
        elif channel:
            launch_kwargs["channel"] = channel

        self.context = await self.playwright.chromium.launch_persistent_context(**launch_kwargs)

        # Pre-flight verify that AntiCaptcha extension loaded
        actual_engine = "Google Chrome" if (executable_path or channel) else "Chromium"
        if has_extension:
            for _ in range(15):
                if self.context.service_workers or self.context.background_pages:
                    break
                await asyncio.sleep(0.1)

            # Auto-fallback to Chromium if enterprise group policy blocked extension in Google Chrome
            if not (self.context.service_workers or self.context.background_pages) and (executable_path or channel):
                logger.warning(
                    "[SingleSessionRunner] Google Chrome enterprise policy blocked unpacked extension sideloading. "
                    "Automatically falling back to Chromium engine where AntiCaptcha extension is verified and active..."
                )
                try:
                    await self.context.close()
                except Exception:
                    pass
                launch_kwargs["executable_path"] = None
                launch_kwargs["channel"] = None
                self.use_chrome = False
                actual_engine = "Chromium"
                self.context = await self.playwright.chromium.launch_persistent_context(**launch_kwargs)
                for _ in range(15):
                    if self.context.service_workers or self.context.background_pages:
                        break
                    await asyncio.sleep(0.1)

        t_end = datetime.now()
        duration = round((t_end - t_start).total_seconds(), 3)
        ext_verified = bool(self.context.service_workers or self.context.background_pages) if has_extension else False

        self.stage_timings["browser_launch"] = {
            "name": "Browser Launch",
            "start_time": t_start.strftime("%H:%M:%S.%f")[:-3],
            "end_time": t_end.strftime("%H:%M:%S.%f")[:-3],
            "duration_seconds": max(duration, 0.001),
            "status": "SUCCESS",
            "detail": (
                f"{actual_engine} ({'Headless (Background)' if is_headless else 'Attended (Visible GUI)'}) + AntiCaptcha (Active & Verified)"
                if ext_verified
                else f"{actual_engine} ({'Headless (Background)' if is_headless else 'Attended (Visible GUI)'})"
            ),
        }

        if self.anticaptcha_api_key and ext_verified:
            try:
                worker = self.context.service_workers[0] if self.context.service_workers else (self.context.background_pages[0] if self.context.background_pages else None)
                if worker:
                    await worker.evaluate(f"chrome.storage.local.set({{ 'account_key': '{self.anticaptcha_api_key}', 'auto_submit_form': false, 'solve_turnstile': true }})")
                    await worker.evaluate(f"chrome.storage.sync.set({{ 'account_key': '{self.anticaptcha_api_key}', 'auto_submit_form': false, 'solve_turnstile': true }})")
                    logger.info("[SingleSessionRunner] AntiCaptcha extension configured with solve_turnstile=True, auto_submit_form=False.")
            except Exception as e:
                logger.warning(f"Note on AntiCaptcha storage injection: {e}")

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            try:
                await self.context.close()
            except Exception:
                pass
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception:
                pass
        if self.is_temp_profile and self.profile_to_use and os.path.exists(self.profile_to_use):
            try:
                shutil.rmtree(self.profile_to_use, ignore_errors=True)
            except Exception:
                pass

    async def get_or_create_tab(self, portal_key: str, url: str) -> Page:
        """Returns existing tab for portal or creates a new one and navigates to url."""
        if portal_key in self.tabs and not self.tabs[portal_key].is_closed():
            page = self.tabs[portal_key]
            try:
                await page.bring_to_front()
            except Exception:
                pass
            return page

        # Use first page if empty, otherwise open new page
        if not self.tabs and self.context.pages:
            page = self.context.pages[0]
        else:
            page = await self.context.new_page()

        page.set_default_timeout(self.timeout_ms)
        try:
            await page.bring_to_front()
        except Exception:
            pass

        self.tabs[portal_key] = page
        return page

    async def execute_portal_searches(
        self,
        portal_key: str,
        scraper: BaseCourtScraper,
        party_pairs: list[tuple[str, str | None, str | None]],
        date_of_loss: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Executes all party searches for a specific portal on its dedicated tab.
        Accumulates cases and deduplicates by CaseNumber.
        """
        page = await self.get_or_create_tab(portal_key, scraper.base_url)
        all_cases: list[dict[str, Any]] = []
        seen_case_numbers = set()

        for party_label, f_name, l_name in party_pairs:
            if not l_name or not str(l_name).strip():
                continue

            logger.info(f"[{scraper.county_name}] Running search for party '{party_label}': {f_name} {l_name} (DOL={date_of_loss})")
            cases = await scraper.search_on_page(
                page=page,
                first_name=f_name,
                last_name=l_name,
                date_of_loss=date_of_loss,
            )

            for c in cases:
                c_num = c.get("CaseNumber") or c.get("case_number") or ""
                if c_num and c_num not in seen_case_numbers:
                    seen_case_numbers.add(c_num)
                    all_cases.append(c)
                elif not c_num:
                    all_cases.append(c)

        # Merge scraper stage timings
        self.stage_timings.update(scraper.stage_timings)
        return all_cases
