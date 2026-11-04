"""Single-Session Multi-Tab Browser Automation Runner for Claim Portals."""

import asyncio
import logging
import os
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

from playwright.async_api import BrowserContext, Page, async_playwright

from app.automation.base import (
    BaseCourtScraper,
)
from app.automation.browser_manager import KNOWN_ANTICAPTCHA_IDS as _IMPORTED_ANTICAPTCHA_IDS
from app.automation.browser_manager import ExtensionManager
from app.core.config import settings

logger = logging.getLogger("uaic_orchestrator.automation.session_runner")

# Module-level constant with safe fallback ensuring KNOWN_ANTICAPTCHA_IDS is always defined
KNOWN_ANTICAPTCHA_IDS: list[str] = (
    list(_IMPORTED_ANTICAPTCHA_IDS)
    if _IMPORTED_ANTICAPTCHA_IDS
    else ["gcpdbjbmekkdlkpldjgffhmapgpdlcpj"]
)


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


def get_search_party_pairs(
    claim: Any, dual_search: int, triple_search: int
) -> list[tuple[str, str | None, str | None]]:
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


def _normalize_worker_offset(wid: Any) -> int:
    """Safely converts worker ID (int, str, UUID, None) to an integer offset."""
    if wid is None:
        return 0
    if isinstance(wid, int):
        return wid
    try:
        return int(wid)
    except ValueError, TypeError:
        return abs(hash(str(wid))) % 10


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
        chrome_binary_path: str | None = None,
        **kwargs: Any,
    ):
        self.headless = headless
        self.timeout_ms = timeout_ms
        self.use_chrome = use_chrome
        self.browser_engine = (browser_engine or "chrome").lower()
        self.chrome_binary_path = chrome_binary_path or kwargs.get("chrome_binary_path")
        # Use ExtensionManager for robust absolute-path resolution (works in any CWD/Celery context)
        resolved_ext = ExtensionManager.resolve_extension_path(extension_dir)
        self.extension_dir = str(resolved_ext) if resolved_ext else None
        self.anticaptcha_settings = anticaptcha_settings  # AutomationSettings for plugin toggles
        self.anticaptcha_api_key = anticaptcha_api_key or getattr(
            anticaptcha_settings, "anticaptcha_api_key", None
        )
        self.user_data_dir = user_data_dir
        self.user_agent = user_agent
        self.proxy_server = proxy_server
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password
        self.typing_speed_mode = typing_speed_mode
        self.typing_delay_ms = typing_delay_ms
        self.action_pacing_ms = action_pacing_ms
        self.stealth_clicks = stealth_clicks
        self.worker_id = kwargs.get("worker_id")
        self.isolated_profile = kwargs.get("isolated_profile", False)
        self.playwright = None
        self.context: BrowserContext | None = None
        self.tabs: dict[str, Page] = {}
        self.profile_to_use: str | None = None
        self.is_temp_profile: bool = False
        self.stage_timings: dict[str, Any] = {}

    async def __aenter__(self):
        cache_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "browser_cache"
            )
        )
        os.makedirs(cache_dir, exist_ok=True)

        is_headless = self.headless
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-dev-shm-usage",
            "--disable-infobars",
        ]

        if is_headless:
            launch_args.append("--disable-gpu")
            launch_args.append("--window-size=1920,1080")
        else:
            # Visible Attended Mode: ensure window is explicitly placed, sized, maximized and visible
            w_offset = _normalize_worker_offset(self.worker_id)
            pos_x = 50 + (35 * w_offset) % 400
            pos_y = 50 + (30 * w_offset) % 300
            launch_args.extend(
                [
                    "--start-maximized",
                    "--window-position=50,50"
                    if self.worker_id is None
                    else f"--window-position={pos_x},{pos_y}",
                    "--window-size=1280,900",
                ]
            )

        from app.automation.base import resolve_extension_dir

        ext_resolved = resolve_extension_dir(self.extension_dir)
        ext_dir = ext_resolved or self.extension_dir
        has_extension = bool(
            ext_dir
            and os.path.isdir(ext_dir)
            and os.path.isfile(os.path.join(ext_dir, "manifest.json"))
        )
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
            if (
                self.anticaptcha_settings is not None
                or not ExtensionManager.is_extension_configured(ext_norm, self.anticaptcha_api_key)
            ):
                ExtensionManager.sync_api_key(
                    Path(ext_norm), self.anticaptcha_api_key, self.anticaptcha_settings
                )

        if has_extension and ext_norm:
            launch_args.extend(
                [
                    f"--disable-extensions-except={ext_norm}",
                    f"--load-extension={ext_norm}",
                    "--enable-developer-mode",
                    "--disable-extension-content-verification",
                    "--disable-extensions-file-access-check",
                    "--allow-outdated-plugins",
                ]
            )
            if sys.platform != "win32":
                launch_args.append("--no-sandbox")

        target_user_dir = (self.user_data_dir or "").strip()
        if target_user_dir and not os.path.isdir(target_user_dir):
            raise ValueError(
                "Configured Chrome User Data Directory does not exist or is not a directory"
            )

        persistent_default = os.path.abspath(
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "data",
                "browser_profile",
            )
        )
        engine_key = (self.browser_engine or "chrome").lower()
        if engine_key in ("edge", "msedge"):
            engine_key = "msedge"
        elif engine_key not in ("chrome", "chromium"):
            engine_key = "chrome"
        persistent_engine = os.path.join(persistent_default, engine_key)
        os.makedirs(persistent_engine, exist_ok=True)

        # Priority order: explicit user_data_dir -> engine persistent profile (e.g. backend/data/browser_profile/chrome)
        canonical_profile = target_user_dir or persistent_engine

        # Clean stale Singleton locks or orphan processes holding the master profile if using master profile
        from app.automation.browser_manager import ChromeSession

        if not self.isolated_profile:
            ChromeSession.clean_profile_locks_and_orphans(canonical_profile, force_kill=True)

        # Always check, configure, and pin AntiCaptcha to browser toolbar across profiles before starting automation
        try:
            ChromeSession.configure_and_pin_profile(
                profile_dir=Path(canonical_profile),
                api_key=self.anticaptcha_api_key,
                extension_path=Path(ext_norm) if ext_norm else None,
                auto_cfg=self.anticaptcha_settings,
            )
            logger.info(
                f"[SingleSessionRunner] Pre-flight: AntiCaptcha extension automatically verified, "
                f"configured, and pinned to toolbar at {canonical_profile}"
            )
        except Exception as e_pin:
            logger.warning(
                f"[SingleSessionRunner] Note auto-configuring/pinning extension profile: {e_pin}"
            )

        # For standard workflow runs (concurrency=1 / not isolated_profile), use the verified persistent master profile directly.
        # This preserves the automated AntiCaptcha setup, toolbar pinning, credentials, and cookies.
        if not self.isolated_profile and not ChromeSession.is_profile_locked(canonical_profile):
            self.profile_to_use = str(canonical_profile)
            self.is_temp_profile = False
            launch_args.append(f"--disk-cache-dir={cache_dir}")
            logger.info(
                f"[SingleSessionRunner] Using verified persistent master profile at: {self.profile_to_use}"
            )
        else:
            # For parallel multi-worker concurrency or if master profile is actively locked,
            # provision an isolated profile pre-seeded with complete extension state from canonical_profile
            import re

            clean_wid = (
                re.sub(r"[^a-zA-Z0-9_]", "_", str(self.worker_id)[:8]) if self.worker_id else "0"
            )
            self.profile_to_use = tempfile.mkdtemp(prefix=f"uaic_worker_{clean_wid}_")
            self.is_temp_profile = True
            logger.info(
                f"[SingleSessionRunner] Provisioning isolated worker profile pre-seeded from: {canonical_profile}"
            )
            if os.path.isdir(canonical_profile):
                try:
                    src_default = os.path.join(canonical_profile, "Default")
                    dest_default = os.path.join(self.profile_to_use, "Default")
                    os.makedirs(dest_default, exist_ok=True)
                    src_ls = os.path.join(canonical_profile, "Local State")
                    if os.path.isfile(src_ls):
                        shutil.copy2(src_ls, os.path.join(self.profile_to_use, "Local State"))
                    pref_src = os.path.join(src_default, "Preferences")
                    if os.path.isfile(pref_src):
                        shutil.copy2(pref_src, os.path.join(dest_default, "Preferences"))
                    # Note: Secure Preferences is explicitly omitted to prevent HMAC corruption across profile directories
                    for ext_sub in [
                        "Local Extension Settings",
                        "Sync Extension Settings",
                        "Extension State",
                        "Extension Rules",
                        "Extension Scripts",
                        "Extensions",
                    ]:
                        sub_src = os.path.join(src_default, ext_sub)
                        sub_dest = os.path.join(dest_default, ext_sub)
                        if os.path.isdir(sub_src):
                            shutil.copytree(sub_src, sub_dest, dirs_exist_ok=True)
                except Exception as e_seed:
                    logger.debug(f"[SingleSessionRunner] Pre-seeding worker profile note: {e_seed}")

        # Always pin AntiCaptcha into modern Chromium toolbar preferences in the active profile
        dest_default_dir = os.path.join(self.profile_to_use, "Default")
        os.makedirs(dest_default_dir, exist_ok=True)
        pref_file_path = Path(dest_default_dir) / "Preferences"
        try:
            from app.automation.browser_manager import ChromeSession

            ChromeSession.pin_extension_in_preferences(pref_file_path, KNOWN_ANTICAPTCHA_IDS)
            logger.info(
                f"[SingleSessionRunner] Pinned AntiCaptcha extension in profile preferences: {pref_file_path}"
            )
        except Exception as e_pin:
            logger.debug(
                f"[SingleSessionRunner] Note pinning extension in profile preferences: {e_pin}"
            )

        # Sanitize any stale Secure Preferences from active profile to prevent Chrome HMAC mismatch
        for p_dir in [Path(self.profile_to_use), Path(dest_default_dir)]:
            sec_p = p_dir / "Secure Preferences"
            if sec_p.is_file():
                try:
                    sec_p.unlink(missing_ok=True)
                except Exception:
                    pass

        # Browser Engine resolution
        from app.automation.base import resolve_browser_launch_target

        executable_path, channel = resolve_browser_launch_target(
            browser_engine=self.browser_engine,
            chrome_binary_path=self.chrome_binary_path,
            use_chrome=self.use_chrome,
            has_extension=has_extension,
        )
        is_headless = self.headless
        # Auto-detect headless requirement on Linux / Docker without X11 ($DISPLAY)
        if sys.platform != "win32":
            if "DISPLAY" not in os.environ:
                if not is_headless:
                    logger.warning(
                        "[SingleSessionRunner] Non-Windows environment without $DISPLAY detected; "
                        "forcing headless mode for container execution. To enable Attended GUI in Docker, ensure Xvfb is running."
                    )
                    is_headless = True
            elif not is_headless:
                logger.info(
                    f"[SingleSessionRunner] Attended GUI execution active on display {os.environ.get('DISPLAY')}. "
                    "Operator can observe and interact via noVNC at http://localhost:6080/vnc.html or VNC port 5900."
                )

        if is_headless and has_extension:
            launch_args.append("--headless=new")
            # In Playwright, to load extensions in headless mode, persistent context can receive headless=False
            # while Chromium executes silently via --headless=new.
            # However, on Linux without an X11 server, headless=False fails with missing DISPLAY.
            if sys.platform != "win32" and "DISPLAY" not in os.environ:
                context_headless = True
            else:
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
            ]
            if has_extension
            else None,
            "no_viewport": True if not is_headless else False,
            "viewport": {
                "width": settings.PLAYWRIGHT_VIEWPORT_WIDTH,
                "height": settings.PLAYWRIGHT_VIEWPORT_HEIGHT,
            }
            if is_headless
            else None,
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

        if not is_headless and self.context and self.context.pages:
            try:
                first_page = self.context.pages[0]
                await first_page.bring_to_front()
                await first_page.evaluate("window.focus()")
            except Exception:
                pass

        # Pre-flight verify that AntiCaptcha extension loaded
        if self.browser_engine == "chrome":
            actual_engine = "Google Chrome"
        elif self.browser_engine in ("edge", "msedge"):
            actual_engine = "Microsoft Edge"
        else:
            actual_engine = "Chromium"

        ext_verified = False
        detected_ext_id = None

        if has_extension:
            api_key_to_use = self.anticaptcha_api_key
            config_payload = (
                ExtensionManager.runtime_config(api_key_to_use, self.anticaptcha_settings)
                if api_key_to_use and self.anticaptcha_settings is not None
                else None
            )

            def _scan_for_extension():
                import re as _re

                _known_ids = KNOWN_ANTICAPTCHA_IDS or ["gcpdbjbmekkdlkpldjgffhmapgpdlcpj"]

                sw_list = getattr(self.context, "service_workers", []) if self.context else []
                for sw in sw_list:
                    url = getattr(sw, "url", "")
                    for kid in _known_ids:
                        if kid in url:
                            return kid
                    m = _re.search(r"chrome-extension://([a-z0-9]+)/", url)
                    if m:
                        return m.group(1)

                bg_list = getattr(self.context, "background_pages", []) if self.context else []
                for bg in bg_list:
                    url = getattr(bg, "url", "")
                    for kid in _known_ids:
                        if kid in url:
                            return kid
                    m = _re.search(r"chrome-extension://([a-z0-9]+)/", url)
                    if m:
                        return m.group(1)

                try:
                    res = ExtensionManager.verify_extension_active(self.context)
                    if res.get("loaded") and res.get("extension_id"):
                        return res["extension_id"]
                except Exception:
                    pass

                return None

            # Wait for service worker loading (extend to 25x0.2s = 5.0s to accommodate Chrome process startup)
            for attempt_i in range(25):
                detected_ext_id = _scan_for_extension()
                if detected_ext_id:
                    break
                await asyncio.sleep(0.2)

            # If not detected via dormant service worker list, probe chrome://extensions to wake it up
            if not detected_ext_id and self.context:
                try:
                    probe_page = await self.context.new_page()
                    try:
                        await probe_page.goto(
                            "chrome://extensions", wait_until="domcontentloaded", timeout=5000
                        )
                        exts_info = await probe_page.evaluate("""() => {
                            const dp = window.chrome?.developerPrivate;
                            if (!dp) return [];
                            return new Promise(resolve => {
                                dp.getExtensionsInfo({ includeDisabled: true }, (items) => {
                                    resolve(items.map(x => ({ id: x.id, name: x.name, state: x.state })));
                                });
                            });
                        }""")
                        for item in exts_info:
                            if (
                                item.get("id") in KNOWN_ANTICAPTCHA_IDS
                                or "anticaptcha" in item.get("name", "").lower()
                            ):
                                if item.get("state") == "ENABLED":
                                    detected_ext_id = item.get("id")
                                    break
                    finally:
                        await probe_page.close()
                except Exception as probe_err:
                    logger.debug(
                        f"[SingleSessionRunner] Probe for extension on chrome://extensions note: {probe_err}"
                    )

            if not detected_ext_id:
                logger.warning(
                    f"[{actual_engine}] AntiCaptcha extension service worker was not detected after launch. "
                    "Verify Developer Mode is enabled and unpacked extension is present."
                )

            # Verify Configuration if Extension is active
            if detected_ext_id and config_payload:
                ext_verified = True
                logger.info(
                    f"[{actual_engine}] AntiCaptcha verified and active via synchronized runtime config (ID: {detected_ext_id})."
                )
            elif detected_ext_id and not api_key_to_use:
                logger.warning(
                    f"[{actual_engine}] AntiCaptcha loaded but no API key is configured; automatic solving is unavailable."
                )
            elif detected_ext_id:
                ext_verified = True
                logger.info(
                    f"[{actual_engine}] AntiCaptcha loaded with existing extension preferences preserved."
                )
            else:
                logger.warning(
                    f"[SingleSessionRunner] AntiCaptcha extension not detected in {actual_engine}."
                )

        t_end = datetime.now()
        duration = round((t_end - t_start).total_seconds(), 3)

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

        return self

    async def close(self) -> None:
        """Gracefully closes all tabs, the browser context, stops Playwright, and sanitizes lingering processes."""
        # 1. Gracefully close all portal tabs
        for portal_key, page in list(self.tabs.items()):
            try:
                if page and not page.is_closed():
                    await page.close()
            except Exception:
                pass
        self.tabs.clear()

        # 2. Close any remaining open pages in the persistent context
        if self.context:
            try:
                for p in list(getattr(self.context, "pages", [])):
                    try:
                        if not p.is_closed():
                            await p.close()
                    except Exception:
                        pass
            except Exception:
                pass

        # 3. Close persistent browser context
        if self.context:
            try:
                await self.context.close()
            except Exception as e_ctx:
                logger.debug(f"[SingleSessionRunner] Context close notice: {e_ctx}")
            finally:
                self.context = None

        # 4. Stop Playwright driver
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e_pw:
                logger.debug(f"[SingleSessionRunner] Playwright stop notice: {e_pw}")
            finally:
                self.playwright = None

        # 5. Terminate lingering orphan browser processes holding this profile (Windows & Linux)
        if self.profile_to_use:
            try:
                from app.automation.browser_manager import ChromeSession

                ChromeSession.clean_profile_locks_and_orphans(self.profile_to_use, force_kill=True)
            except Exception as e_proc:
                logger.debug(f"[SingleSessionRunner] Process cleanup notice: {e_proc}")

        # 6. Clean temporary isolated profile directory if created
        if self.is_temp_profile and self.profile_to_use and os.path.exists(self.profile_to_use):
            try:
                shutil.rmtree(self.profile_to_use, ignore_errors=True)
            except Exception:
                pass

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def get_or_create_tab(self, portal_key: str, url: str) -> Page:
        """Returns existing tab for portal or creates a new one and navigates to url."""
        if portal_key in self.tabs and not self.tabs[portal_key].is_closed():
            page = self.tabs[portal_key]
            try:
                await page.bring_to_front()
                await page.evaluate("window.focus()")
            except Exception:
                pass
            return page

        # Use first page if empty and unnavigated, otherwise open new page
        pages = [p for p in (self.context.pages if self.context else []) if not p.is_closed()]
        if not self.tabs and pages:
            page = pages[0]
        else:
            page = await self.context.new_page()

        page.set_default_timeout(self.timeout_ms)
        page.set_default_navigation_timeout(self.timeout_ms)
        self.tabs[portal_key] = page

        try:
            await page.bring_to_front()
            await page.evaluate("window.focus()")
        except Exception:
            pass

        # Actively navigate to portal URL if provided
        if url and url != "about:blank":
            try:
                logger.info(f"[SingleSessionRunner] Navigating tab '{portal_key}' to {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout_ms)
            except Exception as e_nav:
                logger.warning(
                    f"[SingleSessionRunner] Initial navigation for tab '{portal_key}' to {url} encountered: {e_nav}"
                )

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
        Accumulates every extracted row in V4 search order.
        """
        target_url = scraper.base_url
        page = await self.get_or_create_tab(portal_key, target_url)
        all_cases: list[dict[str, Any]] = []

        for party_label, f_name, l_name in party_pairs:
            if not l_name or not str(l_name).strip():
                continue

            logger.info(
                f"[{scraper.county_name}] Running search for party '{party_label}': {f_name} {l_name} (DOL={date_of_loss})"
            )
            cases = await scraper.search_on_page(
                page=page,
                first_name=f_name,
                last_name=l_name,
                date_of_loss=date_of_loss,
            )

            all_cases.extend(cases)

        # Merge scraper stage timings
        self.stage_timings.update(scraper.stage_timings)
        return all_cases
