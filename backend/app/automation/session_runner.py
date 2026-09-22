"""Single-Session Multi-Tab Browser Automation Runner for Claim Portals."""

import asyncio
import logging
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from playwright.async_api import BrowserContext, Page, async_playwright

from app.automation.base import (
    BaseCourtScraper,
    find_chrome_executable,
)
from app.automation.browser_manager import ExtensionManager
from app.core.config import settings

logger = logging.getLogger("uaic_orchestrator.automation.session_runner")


# ── Backward-compatibility shim ───────────────────────────────────────────────
# Tests and legacy code may import resolve_extension_dir from this module.
# Delegate to ExtensionManager which now owns the canonical implementation.
def resolve_extension_dir(ext_dir: str | None = None) -> str | None:
    """Compatibility shim: use ExtensionManager.resolve_extension_path instead."""
    result = ExtensionManager.resolve_extension_path(ext_dir)
    return str(result) if result else None


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
        anticaptcha_settings: Any = None,
        user_data_dir: str | None = None,
        user_agent: str | None = None,
        proxy_server: str | None = None,
        proxy_username: str | None = None,
        proxy_password: str | None = None,
        typing_speed_mode: str = "turbo",
        typing_delay_ms: int = 0,
        action_pacing_ms: int = 100,
        stealth_clicks: bool = False,
        browser_engine: str | None = None,
        **kwargs: Any,
    ):
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.use_chrome = use_chrome
        self.browser_engine = (browser_engine or "chrome").lower()
        # Use ExtensionManager for robust absolute-path resolution (works in any CWD/Celery context)
        resolved_ext = ExtensionManager.resolve_extension_path(extension_dir)
        self.extension_dir = str(resolved_ext) if resolved_ext else None
        self.anticaptcha_api_key = anticaptcha_api_key
        self.anticaptcha_settings = anticaptcha_settings  # AutomationSettings for plugin toggles
        self.user_data_dir = user_data_dir
        self.user_agent = user_agent
        self.proxy_server = proxy_server
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.typing_speed_mode = typing_speed_mode
        self.typing_delay_ms = typing_delay_ms
        self.action_pacing_ms = action_pacing_ms
        self.stealth_clicks = stealth_clicks
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
            "--disable-gpu",
            "--disable-dev-shm-usage",
        ]

        ext_dir = self.extension_dir
        has_extension = bool(ext_dir and os.path.isdir(ext_dir) and os.path.isfile(os.path.join(ext_dir, "manifest.json")))
        ext_norm = os.path.normpath(os.path.abspath(str(ext_dir))) if has_extension else None

        if has_extension:
            logger.info(f"AntiCaptcha extension resolved at: {ext_norm}")
        else:
            logger.warning(
                f"AntiCaptcha extension NOT found at configured path: {ext_dir!r}. "
                "CAPTCHAs will not be solved automatically. Check Settings > Extension tab."
            )

        if self.anticaptcha_api_key and has_extension and ext_norm:
            # Always sync on launch — use ExtensionManager with dynamic plugin settings from DB
            ExtensionManager.sync_api_key(Path(ext_norm), self.anticaptcha_api_key, self.anticaptcha_settings)

        if has_extension and ext_norm:
            launch_args.append(f"--disable-extensions-except={ext_norm}")
            launch_args.append(f"--load-extension={ext_norm}")
            launch_args.append("--no-sandbox")

        target_user_dir = (self.user_data_dir or "").strip()
        if "Users\\Default" in target_user_dir:
            target_user_dir = ""

        persistent_default = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "browser_profile"))
        # Prefer engine-specific sub-profile (chrome/) — this is where setup-extension writes
        # the correctly-pinned Preferences file. Fall back to the root browser_profile/ dir.
        persistent_chrome = os.path.join(persistent_default, "chrome")

        # For parallel multi-worker concurrency, always provision an isolated profile directory
        # pre-seeded from persistent_default (or target_user_dir) to eliminate Chromium's SingletonLock
        # while preserving 100% of extension credentials, toolbar pinning, and preferences.
        self.profile_to_use = tempfile.mkdtemp(prefix="uaic_worker_profile_")
        self.is_temp_profile = True

        # Priority order: explicit user_data_dir → chrome/ sub-profile → root browser_profile/
        if target_user_dir and os.path.exists(target_user_dir):
            source_profile = target_user_dir
        elif os.path.isdir(persistent_chrome) and os.path.isfile(os.path.join(persistent_chrome, "Default", "Preferences")):
            source_profile = persistent_chrome
            logger.info(f"[SingleSessionRunner] Pre-seeding worker profile from chrome sub-profile: {source_profile}")
        elif os.path.exists(persistent_default) and os.path.isdir(persistent_default):
            source_profile = persistent_default
        else:
            source_profile = None

        if source_profile:
            try:
                src_default = os.path.join(source_profile, "Default")
                dest_default = os.path.join(self.profile_to_use, "Default")
                if os.path.isdir(src_default):
                    os.makedirs(dest_default, exist_ok=True)
                    for fname in ("Preferences", "Secure Preferences"):
                        s = os.path.join(src_default, fname)
                        if os.path.isfile(s):
                            shutil.copy2(s, os.path.join(dest_default, fname))
                src_ls = os.path.join(source_profile, "Local State")
                if os.path.isfile(src_ls):
                    shutil.copy2(src_ls, os.path.join(self.profile_to_use, "Local State"))
            except Exception as e:
                logger.debug(f"Note pre-seeding worker profile from {source_profile}: {e}")

        # Browser Engine resolution
        executable_path = None
        channel = None
        if self.browser_engine == "chrome":
            executable_path = find_chrome_executable()
            if not executable_path:
                channel = "chrome"
        elif self.browser_engine in ("edge", "msedge"):
            channel = "msedge"
        elif self.browser_engine == "chromium":
            executable_path = None
            channel = None
        elif self.use_chrome:
            executable_path = find_chrome_executable()
            channel = "chrome" if not executable_path else None
        is_headless = self.headless
        if is_headless and has_extension:
            launch_args.append("--headless=new")
            # In Playwright, to load extensions in headless mode, persistent context must receive headless=False
            # while Chromium executes silently via --headless=new.
            context_headless = False
        else:
            context_headless = is_headless

        t_start = datetime.now()
        self.playwright = await async_playwright().start()

        launch_kwargs = {
            "user_data_dir": self.profile_to_use,
            "headless": context_headless,
            "args": launch_args,
            "ignore_default_args": [
                "--disable-extensions",
                "--disable-component-extensions-with-background-pages",
            ] if has_extension else None,
            "no_viewport": True if not is_headless else False,
            "viewport": {"width": settings.PLAYWRIGHT_VIEWPORT_WIDTH, "height": settings.PLAYWRIGHT_VIEWPORT_HEIGHT} if is_headless else None,
        }
        if self.user_agent:
            launch_kwargs["user_agent"] = self.user_agent
        if executable_path:
            launch_kwargs["executable_path"] = executable_path
        elif channel:
            launch_kwargs["channel"] = channel

        if self.proxy_server:
            proxy_dict = {"server": self.proxy_server}
            if self.proxy_username and self.proxy_password:
                proxy_dict["username"] = self.proxy_username
                proxy_dict["password"] = self.proxy_password
            launch_kwargs["proxy"] = proxy_dict

        self.context = await self.playwright.chromium.launch_persistent_context(**launch_kwargs)

        # Pre-flight verify that AntiCaptcha extension loaded
        actual_engine = "Google Chrome" if (executable_path or channel) else "Chromium"
        if has_extension:
            for _ in range(50):  # Wait up to 5 seconds for Manifest V3 Service Worker
                if self.context.service_workers or self.context.background_pages:
                    break
                await asyncio.sleep(0.1)

            # Auto-fallback to Chromium if enterprise group policy blocked extension in Google Chrome
            if not (self.context.service_workers or self.context.background_pages) and (executable_path or channel):
                logger.warning(
                    "[SingleSessionRunner] Google Chrome enterprise policy blocked unpacked extension sideloading "
                    "(or took too long to load). Automatically falling back to Chromium engine..."
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
            api_key_to_use = self.anticaptcha_api_key
            worker = (
                self.context.service_workers[0] if self.context.service_workers
                else (self.context.background_pages[0] if self.context.background_pages else None)
            )

            # Detect the actual loaded extension ID from service worker URL
            import re as _re
            detected_ext_id = None
            for sw in self.context.service_workers:
                url = getattr(sw, "url", "")
                m = _re.search(r"chrome-extension://([a-z0-9]+)/", url)
                if m:
                    detected_ext_id = m.group(1)
                    break
            if not detected_ext_id:
                for bg in self.context.background_pages:
                    url = getattr(bg, "url", "")
                    m = _re.search(r"chrome-extension://([a-z0-9]+)/", url)
                    if m:
                        detected_ext_id = m.group(1)
                        break

            # Pin the actual runtime extension ID to the temp profile Preferences
            if detected_ext_id:
                try:
                    from pathlib import Path as _Path

                    from app.automation.browser_manager import ChromeSession as _CS
                    active_pref = _Path(self.profile_to_use) / "Default" / "Preferences"
                    _CS.pin_extension_in_preferences(active_pref, [detected_ext_id])
                except Exception as _pin_err:
                    logger.debug(f"[SingleSessionRunner] Could not pin ext ID {detected_ext_id}: {_pin_err}")

            if worker:
                try:
                    # Check if extension is already fully configured with the correct API key
                    already_configured = False
                    try:
                        stored = await asyncio.wait_for(
                            worker.evaluate("""() => {
                                return new Promise(resolve => {
                                    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
                                        chrome.storage.local.get(['account_key', 'enable', 'account_key_checked'], res => resolve(res));
                                    } else { resolve(null); }
                                });
                            }"""),
                            timeout=2.0,
                        )
                        if (
                            stored
                            and stored.get("account_key") == api_key_to_use
                            and stored.get("enable") is True
                            and stored.get("account_key_checked") is True
                        ):
                            already_configured = True
                    except Exception:
                        already_configured = False

                    if already_configured:
                        logger.info(
                            "[SingleSessionRunner] AntiCaptcha already fully configured with active API key. Skipping re-injection."
                        )
                    else:
                        # ── Full config injection — ALL keys from anticaptcha-plugin_v0.83 options ─
                        full_config = {
                            # Core authentication
                            "account_key": api_key_to_use,
                            "account_key_checked": True,
                            "enable": True,
                            # UI / sound
                            "auto_submit_form": False,
                            "play_sounds": False,
                            "reenable_contextmenu": False,
                            # CAPTCHA type toggles
                            "solve_recaptcha2": True,
                            "solve_invisible_recaptcha": True,
                            "solve_recaptcha3": True,
                            "recaptcha3_score": 0.3,
                            "solve_hcaptcha": True,
                            "solve_turnstile": True,
                            "solve_funcaptcha": True,
                            "solve_geetest": True,
                            # Image CAPTCHA
                            "use_predefined_image_captcha_marks": True,
                            # reCAPTCHA advanced behavior
                            "start_recaptcha2_solving_when_challenge_shown": True,
                            "solve_only_presented_recaptcha2": False,
                            "run_explicit_invisible_hcaptcha_callback_when_challenge_shown": False,
                            "delay_onready_callback": False,
                            # Precaching
                            "use_recaptcha_precaching": False,
                            "k_precached_solution_count_min": 2,
                            "k_precached_solution_count_max": 4,
                            "dont_reuse_recaptcha_solution": False,
                            # Worker / proxy
                            "solve_proxy_on_tasks": False,
                            "set_incoming_workers_user_agent": False,
                            "user_proxy_protocol": None,
                            "user_proxy_login": None,
                            "user_proxy_password": None,
                            "user_proxy_server": None,
                            "user_proxy_port": None,
                            # Domain filter (empty = solve on all sites)
                            "where_solve_list": [],
                            "where_solve_white_list_type": False,
                        }


                        # Inject into chrome.storage.local (primary runtime storage)
                        await asyncio.wait_for(
                            worker.evaluate(
                                """(cfg) => {
                                    return new Promise(resolve => {
                                        const setLocal = new Promise(r => {
                                            if (chrome.storage && chrome.storage.local && chrome.storage.local.set) {
                                                chrome.storage.local.set(cfg, () => r(true));
                                            } else { r(false); }
                                        });
                                        const setSync = new Promise(r => {
                                            if (chrome.storage && chrome.storage.sync && chrome.storage.sync.set) {
                                                chrome.storage.sync.set(cfg, () => r(true));
                                            } else { r(false); }
                                        });
                                        Promise.all([setLocal, setSync]).then(() => resolve(true));
                                    });
                                }""",
                                full_config,
                            ),
                            timeout=5.0,
                        )
                        logger.info(
                            f"[SingleSessionRunner] AntiCaptcha fully configured: 20-key config injected "
                            f"into chrome.storage.local + chrome.storage.sync (ext ID: {detected_ext_id or 'unknown'})."
                        )

                        # ── Popup activation: initialize Vue options store (same as ChromeSession) ──
                        if detected_ext_id:
                            try:
                                setup_page = await self.context.new_page()
                                popup_url = f"chrome-extension://{detected_ext_id}/popup_v3.html"
                                await setup_page.goto(popup_url, wait_until="load", timeout=8000)
                                await setup_page.evaluate(
                                    """(apiKey) => {
                                        return new Promise(resolve => {
                                            const inp = document.getElementById("account_key");
                                            const chk = document.getElementById("enable_checkbox");
                                            if (chk && !chk.checked) { chk.click(); }
                                            if (inp && (!inp.value || inp.value !== apiKey)) {
                                                inp.value = apiKey;
                                                inp.dispatchEvent(new Event('input', { bubbles: true }));
                                                const submitBtn = document.querySelector('input[type="submit"], button.btn-primary');
                                                if (submitBtn) submitBtn.click();
                                            }
                                            resolve(true);
                                        });
                                    }""",
                                    api_key_to_use,
                                )
                                await asyncio.sleep(0.4)
                                await setup_page.close()
                                logger.info(
                                    f"[SingleSessionRunner] AntiCaptcha popup activated and Vue store initialized "
                                    f"(ext ID: {detected_ext_id})."
                                )
                            except Exception as _popup_err:
                                logger.debug(f"[SingleSessionRunner] Popup init note (non-critical): {_popup_err}")
                except Exception as e:
                    logger.warning(f"[SingleSessionRunner] AntiCaptcha CDP injection note: {e}")



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
