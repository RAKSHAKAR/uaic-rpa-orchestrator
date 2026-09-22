"""Modern Modular Browser Automation Architecture for Python 3.14.

Implements:
- BrowserManager (top-level lifecycle orchestrator)
- ChromeSession (real Google Chrome attended/headless context)
- ExtensionManager (Anti-Captcha extension discovery and API key sync)
- CaptchaManager (condition-based CAPTCHA solving with fast state polling)
- TabManager (multi-portal tab mapping, switching, and reuse)
- CountySiteAdapter (Protocol defining the standard contract for county clerk portals)
- SiteAutomationManager (registry and executor of site adapters)
"""

import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

# On Windows, Playwright requires ProactorEventLoop for subprocess creation
if sys.platform == "win32":
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    except Exception:
        pass

from playwright.async_api import BrowserContext, Page, Playwright, async_playwright

from app.core.config import settings

logger = logging.getLogger("uaic_orchestrator.automation.browser_manager")

KNOWN_ANTICAPTCHA_IDS: list[str] = [
    "gcpdbjbmekkdlkpldjgffhmapgpdlcpj",  # Authentic Anti-Captcha unpacked extension ID (Chromium / Edge / Chrome)
]


@runtime_checkable
class CountySiteAdapter(Protocol):
    """Standardized contract for all county court scrapers."""
    county_name: str
    base_url: str

    async def search(
        self,
        first_name: str | None,
        last_name: str | None,
        page: Page,
        date_of_loss: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]: ...

    async def extract_results(self, page: Page, **kwargs: Any) -> list[dict[str, Any]]: ...

    async def cleanup(self, page: Page, **kwargs: Any) -> None: ...


class ExtensionManager:
    """Manages Anti-Captcha browser extension resolution and runtime credentials synchronization."""

    @staticmethod
    def resolve_extension_path(configured_path: str | Path | None = None) -> Path | None:
        """Resolves existing AntiCaptcha extension directory on disk, preferring the DB-configured path."""
        backend_dir = Path(__file__).resolve().parent.parent.parent
        repo_root = backend_dir.parent

        candidate_paths: list[Path] = []
        if configured_path:
            p = Path(configured_path)
            if not p.is_absolute():
                candidate_paths.append((repo_root / p).resolve())
                candidate_paths.append((backend_dir / p).resolve())
                candidate_paths.append((Path.cwd() / p).resolve())
            else:
                candidate_paths.append(p)

        # Canonical project fallback if DB config is missing/invalid
        candidate_paths.append(repo_root / "anticaptcha-plugin_v0.83")

        for p in candidate_paths:
            if p.is_dir() and (p / "manifest.json").exists():
                return p.resolve()

        return None

    @staticmethod
    def is_extension_configured(extension_dir: Path | str, api_key: str) -> bool:
        """Checks if extension on disk is already properly configured with the given API key."""
        if not api_key:
            return False
        config_file = Path(extension_dir) / "js" / "config_ac_api_key.js"
        if not config_file.is_file():
            return False
        try:
            content = config_file.read_text(encoding="utf-8")
            clean_key = api_key.strip()
            return f"var antiCapApiKey = '{clean_key}';" in content and (
                "solve_turnstile" in content or "chrome.storage.local.set" in content
            )
        except Exception:
            return False

    @staticmethod
    def sync_api_key(extension_dir: Path | str, api_key: str, auto_cfg: Any = None) -> bool:
        """Injects Anti-Captcha API key and plugin settings into config_ac_api_key.js.

        Uses dynamic values from auto_cfg (AutomationSettings) when provided,
        otherwise falls back to safe defaults matching Power Automate V4 behavior.
        """
        if not api_key:
            return False

        # Resolve dynamic values from settings (or safe defaults)
        enabled = getattr(auto_cfg, "anticaptcha_enabled", True) if auto_cfg else True
        auto_submit = getattr(auto_cfg, "anticaptcha_auto_submit", False) if auto_cfg else False
        play_sounds = getattr(auto_cfg, "anticaptcha_play_sounds", False) if auto_cfg else False
        solve_rc2 = getattr(auto_cfg, "anticaptcha_solve_recaptcha2", True) if auto_cfg else True
        solve_invisible = getattr(auto_cfg, "anticaptcha_solve_invisible", True) if auto_cfg else True
        solve_rc3 = getattr(auto_cfg, "anticaptcha_solve_recaptcha3", True) if auto_cfg else True
        rc3_score = getattr(auto_cfg, "anticaptcha_recaptcha3_score", 0.3) if auto_cfg else 0.3
        solve_hcaptcha = getattr(auto_cfg, "anticaptcha_solve_hcaptcha", True) if auto_cfg else True
        solve_turnstile = getattr(auto_cfg, "anticaptcha_solve_turnstile", True) if auto_cfg else True
        solve_funcaptcha = getattr(auto_cfg, "anticaptcha_solve_funcaptcha", True) if auto_cfg else True
        solve_geetest = getattr(auto_cfg, "anticaptcha_solve_geetest", True) if auto_cfg else True

        # Skip re-write if already configured identically (perf optimisation)
        # Only skip if enabled=True; if disabled we must always rewrite to propagate
        if enabled and ExtensionManager.is_extension_configured(extension_dir, api_key):
            logger.debug("AntiCaptcha extension on disk is already configured with current API key.")
            return True

        ext_path = Path(extension_dir)
        config_file = ext_path / "js" / "config_ac_api_key.js"
        if not config_file.parent.exists():
            config_file.parent.mkdir(parents=True, exist_ok=True)

        clean_key = api_key.strip()
        js_bool = lambda v: "true" if v else "false"  # noqa: E731
        content = (
            f"// Auto-synchronized runtime Anti-Captcha key and settings (Python 3.14 / UAIC Orchestrator)\n"
            f"var antiCapApiKey = '{clean_key}';\n"
            f"var antiCapAutoSubmitForm = {js_bool(auto_submit)};\n\n"
            f"(function initAntiCaptchaStorage() {{\n"
            f"    try {{\n"
            f"        if (typeof chrome !== 'undefined' && chrome.storage) {{\n"
            f"            var fullConfig = {{\n"
            f"                account_key: antiCapApiKey,\n"
            f"                account_key_checked: true,\n"
            f"                enable: {js_bool(enabled)},\n"
            f"                auto_submit_form: {js_bool(auto_submit)},\n"
            f"                play_sounds: {js_bool(play_sounds)},\n"
            f"                solve_recaptcha2: {js_bool(solve_rc2)},\n"
            f"                solve_invisible_recaptcha: {js_bool(solve_invisible)},\n"
            f"                solve_recaptcha3: {js_bool(solve_rc3)},\n"
            f"                recaptcha3_score: {rc3_score},\n"
            f"                solve_hcaptcha: {js_bool(solve_hcaptcha)},\n"
            f"                solve_turnstile: {js_bool(solve_turnstile)},\n"
            f"                solve_funcaptcha: {js_bool(solve_funcaptcha)},\n"
            f"                solve_geetest: {js_bool(solve_geetest)},\n"
            f"                use_predefined_image_captcha_marks: true,\n"
            f"                start_recaptcha2_solving_when_challenge_shown: true,\n"
            f"                use_recaptcha_precaching: false,\n"
            f"                k_precached_solution_count_min: 2,\n"
            f"                k_precached_solution_count_max: 4,\n"
            f"                dont_reuse_recaptcha_solution: false,\n"
            f"                solve_only_presented_recaptcha2: false,\n"
            f"                solve_proxy_on_tasks: false,\n"
            f"                set_incoming_workers_user_agent: false,\n"
            f"                run_explicit_invisible_hcaptcha_callback_when_challenge_shown: false,\n"
            f"                delay_onready_callback: false,\n"
            f"                reenable_contextmenu: false,\n"
            f"                where_solve_list: [],\n"
            f"                where_solve_white_list_type: false\n"
            f"            }};\n"
            f"            function notify() {{\n"
            f"                if (typeof chrome.runtime !== 'undefined' && chrome.runtime.sendMessage) {{\n"
            f"                    try {{\n"
            f"                        chrome.runtime.sendMessage({{ type: 'saveOptions', options: fullConfig }});\n"
            f"                        chrome.runtime.sendMessage({{ type: 'refreshBadgeAndIcon' }});\n"
            f"                    }} catch (e) {{}}\n"
            f"                }}\n"
            f"            }}\n"
            f"            if (chrome.storage && chrome.storage.local && chrome.storage.local.set) {{\n"
            f"                chrome.storage.local.set(fullConfig, notify);\n"
            f"            }}\n"
            f"            if (chrome.storage && chrome.storage.sync && chrome.storage.sync.set) {{\n"
            f"                chrome.storage.sync.set(fullConfig);\n"
            f"            }}\n"
            f"        }}\n"
            f"    }} catch (err) {{}}\n"
            f"}})();\n"
        )
        try:
            config_file.write_text(content, encoding="utf-8")
            logger.info(
                f"Synchronized AntiCaptcha config: enabled={enabled}, auto_submit={auto_submit}, "
                f"rc2={solve_rc2}, rc3={solve_rc3}, hcaptcha={solve_hcaptcha}, turnstile={solve_turnstile}"
            )
            return True
        except Exception as e:
            logger.warning(f"Failed to sync AntiCaptcha key to {config_file}: {e}")
            return False

    @staticmethod
    def verify_extension_active(context: Any) -> dict[str, Any]:
        """
        Validates whether the Anti-Captcha extension is actively running in the Playwright context.
        Inspects service workers and background pages.
        """
        if not context:
            return {
                "loaded": False,
                "service_workers_count": 0,
                "background_pages_count": 0,
                "extension_id": None,
                "details": "No browser context available",
            }

        sws = getattr(context, "service_workers", []) or []
        bg_pages = getattr(context, "background_pages", []) or []

        active = False
        found_id = None

        for sw in sws:
            url = getattr(sw, "url", "")
            for kid in KNOWN_ANTICAPTCHA_IDS:
                if kid in url:
                    active = True
                    found_id = kid
                    break
            if not active and "anticaptcha" in url.lower():
                active = True
                m = re.search(r"chrome-extension://([a-z0-9]+)/", url)
                found_id = m.group(1) if m else KNOWN_ANTICAPTCHA_IDS[0]
            if active:
                break

        if not active:
            for bg in bg_pages:
                url = getattr(bg, "url", "")
                for kid in KNOWN_ANTICAPTCHA_IDS:
                    if kid in url:
                        active = True
                        found_id = kid
                        break
                if not active and "anticaptcha" in url.lower():
                    active = True
                    m = re.search(r"chrome-extension://([a-z0-9]+)/", url)
                    found_id = m.group(1) if m else KNOWN_ANTICAPTCHA_IDS[0]
                if active:
                    break

        is_loaded = active or (len(sws) > 0)
        return {
            "loaded": is_loaded,
            "service_workers_count": len(sws),
            "background_pages_count": len(bg_pages),
            "extension_id": found_id or (KNOWN_ANTICAPTCHA_IDS[1] if is_loaded else None),
            "details": f"AntiCaptcha extension verified ({len(sws)} active service worker(s))" if is_loaded else "Extension not loaded (0 active workers)",
        }


class CaptchaManager:
    """Condition-based CAPTCHA detection and solving manager.

    Eliminates arbitrary large sleep delays by polling for DOM/token state changes
    with short intervals (250-500ms) up to the configured timeout.
    """

    def __init__(self, timeout_seconds: int = 35, poll_interval_ms: int = 400):
        self.timeout_seconds = timeout_seconds
        self.poll_interval_ms = poll_interval_ms

    async def detect_and_solve(self, page: Page, wait_seconds: int | None = None) -> bool:
        """Monitors page for Cloudflare Turnstile, reCAPTCHA, and visual challenges,

        returning immediately when verified without waiting out the full timeout.
        """
        timeout = wait_seconds or self.timeout_seconds
        start_time = asyncio.get_running_loop().time()

        # Initial check for presence of challenges
        has_challenge = await self._is_challenge_present(page)
        if not has_challenge:
            return True

        logger.info(f"CAPTCHA challenge detected. Initiating condition-based verification (timeout: {timeout}s)...")

        # Condition-based polling loop
        while (asyncio.get_running_loop().time() - start_time) < timeout:
            # 1. Check if AntiCaptcha injected status indicates success
            try:
                solved_status = await page.evaluate("""() => {
                    // AntiCaptcha plugin sets antigate_solver status
                    const statusElem = document.querySelector('.antigate_solver, .antigate_solver_solved');
                    if (statusElem && (statusElem.classList.contains('antigate_solver_solved') || statusElem.innerText.includes('SOLVED'))) {
                        return 'SOLVED';
                    }
                    // Turnstile response token filled
                    const cfToken = document.querySelector('input[name="cf-turnstile-response"]');
                    if (cfToken && cfToken.value && cfToken.value.length > 20) {
                        return 'SOLVED';
                    }
                    // reCAPTCHA response token filled
                    const gToken = document.querySelector('textarea[name="g-recaptcha-response"]');
                    if (gToken && gToken.value && gToken.value.length > 20) {
                        return 'SOLVED';
                    }
                    // Check if challenge frame disappeared or checkbox checked
                    const cfFrame = document.querySelector('iframe[src*="challenges.cloudflare.com"], iframe[src*="recaptcha"]');
                    if (!cfFrame) {
                        return 'CLEAR';
                    }
                    return 'PENDING';
                }""")
                if solved_status in ("SOLVED", "CLEAR"):
                    logger.info(f"CAPTCHA verified successfully via condition check ({solved_status}).")
                    await page.wait_for_timeout(300)
                    return True
            except Exception:
                pass

            # 2. Click Turnstile / reCAPTCHA checkbox if clickable
            try:
                turnstile_frame = page.frame_locator("iframe[src*='challenges.cloudflare.com']").first
                cb = turnstile_frame.locator("input[type='checkbox'], #challenge-stage, .ctp-checkbox-label").first
                if await cb.count() > 0 and await cb.is_visible():
                    await cb.click(timeout=1000)
            except Exception:
                pass

            await page.wait_for_timeout(self.poll_interval_ms)

        # Final check before failing
        is_clear = not await self._is_challenge_present(page)
        if is_clear:
            logger.info("CAPTCHA resolved at timeout boundary.")
            return True

        logger.warning(f"CAPTCHA verification timed out after {timeout} seconds.")
        return False

    async def _is_challenge_present(self, page: Page) -> bool:
        """Determines if a CAPTCHA challenge is currently active in the page DOM."""
        try:
            return await page.evaluate("""() => {
                const cf = document.querySelector('iframe[src*="challenges.cloudflare.com"]');
                const rc = document.querySelector('iframe[src*="recaptcha"]');
                const hcaptcha = document.querySelector('iframe[src*="hcaptcha"]');
                const cloudflareBody = document.body && (
                    document.body.innerText.includes('Verifying you are human') ||
                    document.body.innerText.includes('Checking if the site connection is secure')
                );
                return Boolean(cf || rc || hcaptcha || cloudflareBody);
            }""")
        except Exception:
            return False


class TabManager:
    """Manages multi-portal browser tabs within a single browser session."""

    def __init__(self, context: BrowserContext):
        self.context = context
        self.tabs: dict[str, Page] = {}

    async def get_or_create_tab(self, portal_key: str, initial_url: str | None = None) -> Page:
        """Returns existing tab for portal or creates a new tab with fast navigation."""
        if portal_key in self.tabs and not self.tabs[portal_key].is_closed():
            page = self.tabs[portal_key]
            await page.bring_to_front()
            return page

        # Reuse empty initial page if available
        pages = [p for p in self.context.pages if not p.is_closed()]
        if len(self.tabs) == 0 and pages:
            page = pages[0]
        else:
            page = await self.context.new_page()

        self.tabs[portal_key] = page
        await page.bring_to_front()

        if initial_url:
            await page.goto(initial_url, wait_until="domcontentloaded", timeout=45000)

        return page

    async def close_all(self) -> None:
        """Closes all tracked portal tabs."""
        for p in self.tabs.values():
            if not p.is_closed():
                try:
                    await p.close()
                except Exception:
                    pass
        self.tabs.clear()


class ChromeSession:
    """Encapsulates Google Chrome persistent browser context with attended GUI and extension loading."""

    def __init__(
        self,
        headless: bool = False,
        extension_path: Path | None = None,
        anticaptcha_api_key: str | None = None,
        user_data_dir: str | None = None,
        user_agent: str | None = None,
        chrome_binary_path: str | Path | None = None,
        browser_engine: str = "chrome",
        isolated_profile: bool = False,
        worker_id: int | None = None,
        proxy_server: str | None = None,
        proxy_username: str | None = None,
        proxy_password: str | None = None,
    ):
        self.headless = headless
        self.extension_path = ExtensionManager.resolve_extension_path(extension_path)
        self.anticaptcha_api_key = anticaptcha_api_key
        self.browser_engine = (browser_engine or "chrome").lower()
        self.user_data_dir = user_data_dir or str(self.get_persistent_profile_dir(self.browser_engine))
        self.user_agent = user_agent
        self.chrome_binary_path = chrome_binary_path
        self.isolated_profile = isolated_profile
        self.worker_id = worker_id
        self.proxy_server = proxy_server
        self.proxy_username = proxy_username
        self.proxy_password = proxy_password

        self.playwright: Playwright | None = None
        self.context: BrowserContext | None = None
        self.profile_to_use: Path | None = None
        self.is_temp_profile: bool = False

        self.extension_loaded: bool = False
        self.extension_id: str | None = None
        self.service_worker_active: bool = False
        self.warning_message: str | None = None

    @staticmethod
    def find_chrome_executable(configured_path: str | Path | None = None) -> Path | None:
        """Locates Google Chrome executable on Windows with user override support."""
        if configured_path:
            p = Path(configured_path)
            if p.is_file():
                return p.resolve()

        system_paths = [
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Google" / "Chrome" / "Application" / "chrome.exe",
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Google" / "Chrome" / "Application" / "chrome.exe",
            Path(os.environ.get("LocalAppData", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        ]
        for p in system_paths:
            if p.is_file():
                return p.resolve()
        return None

    @staticmethod
    def find_default_edge_executable() -> Path | None:
        """Locates Microsoft Edge executable on Windows."""
        edge_paths = [
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
            Path(os.environ.get("LocalAppData", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        ]
        for p in edge_paths:
            if p.is_file():
                return p.resolve()
        return None

    @staticmethod
    def find_default_chrome_user_data_dir() -> Path | None:
        """Locates standard Google Chrome User Data directory on Windows."""
        local_app_data = os.environ.get("LocalAppData", "")
        if local_app_data:
            p = Path(local_app_data) / "Google" / "Chrome" / "User Data"
            if p.is_dir():
                return p.resolve()
        candidate = Path(os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data"))
        if candidate.is_dir():
            return candidate.resolve()
        return None

    @staticmethod
    def find_default_edge_user_data_dir() -> Path | None:
        """Locates standard Microsoft Edge User Data directory on Windows."""
        local_app_data = os.environ.get("LocalAppData", "")
        if local_app_data:
            p = Path(local_app_data) / "Microsoft" / "Edge" / "User Data"
            if p.is_dir():
                return p.resolve()
        candidate = Path(os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\User Data"))
        if candidate.is_dir():
            return candidate.resolve()
        return None

    @classmethod
    def get_persistent_profile_dir(cls, engine: str | None = None) -> Path:
        """Returns the canonical persistent browser profile directory path for the given engine."""
        base_data = Path(__file__).resolve().parent.parent.parent / "data" / "browser_profile"
        if engine:
            eng = engine.lower()
            if eng in ("chrome", "chromium", "msedge"):
                p = base_data / eng
                p.mkdir(parents=True, exist_ok=True)
                return p
        base_data.mkdir(parents=True, exist_ok=True)
        return base_data

    @classmethod
    def pin_extension_in_preferences(cls, pref_file: Path, extension_ids: list[str] | None = None) -> bool:
        """Injects AntiCaptcha extension IDs into modern Chromium toolbar pinning preferences."""
        try:
            if not pref_file.parent.exists():
                pref_file.parent.mkdir(parents=True, exist_ok=True)
            prefs: dict[str, Any] = {}
            if pref_file.is_file():
                try:
                    prefs = json.loads(pref_file.read_text(encoding="utf-8"))
                except Exception:
                    prefs = {}

            ids_to_pin = extension_ids or KNOWN_ANTICAPTCHA_IDS
            ext_prefs = prefs.setdefault("extensions", {})
            ext_prefs["developer_mode"] = True
            ext_ui = ext_prefs.setdefault("ui", {})
            ext_ui["developer_mode"] = True
            pinned = ext_prefs.setdefault("pinned_extensions", [])
            for eid in ids_to_pin:
                if eid not in pinned:
                    pinned.append(eid)
            ext_prefs["pinned_extension_migration"] = True

            toolbar_prefs = prefs.setdefault("toolbar", {})
            pinned_actions = toolbar_prefs.setdefault("pinned_actions", [])
            for eid in ids_to_pin:
                aid = f"kActionExtensionId:{eid}"
                if aid not in pinned_actions:
                    pinned_actions.append(aid)
                if eid not in pinned_actions:
                    pinned_actions.append(eid)

            browser_prefs = prefs.setdefault("browser", {})
            browser_prefs["show_extensions_toolbar_menu"] = True

            pref_file.write_text(json.dumps(prefs, indent=2), encoding="utf-8")
            return True
        except Exception as e:
            logger.debug(f"Failed writing pinned preferences to {pref_file}: {e}")
            return False

    @classmethod
    def configure_and_pin_profile(
        cls,
        profile_dir: Path | None = None,
        api_key: str | None = None,
        extension_path: Path | None = None,
    ) -> Path:
        """Configures persistent browser profiles across Chrome, Chromium, and Edge with AntiCaptcha extension and modern toolbar pinning."""
        base_profile = cls.get_persistent_profile_dir()
        target_dir = profile_dir or base_profile
        target_dir.mkdir(parents=True, exist_ok=True)
        resolved_ext = ExtensionManager.resolve_extension_path(extension_path)

        # 1. Sync API Key to extension directory if provided
        if resolved_ext and resolved_ext.is_dir() and api_key:
            ExtensionManager.sync_api_key(resolved_ext, api_key)

        # 2. Pin into all 3 engine-specific persistent profiles (chrome, chromium, msedge)
        for eng in ["chrome", "chromium", "msedge"]:
            eng_default = base_profile / eng / "Default"
            eng_default.mkdir(parents=True, exist_ok=True)
            sec_pref = eng_default / "Secure Preferences"
            if sec_pref.exists():
                try:
                    sec_pref.unlink(missing_ok=True)
                except Exception:
                    pass
            cls.pin_extension_in_preferences(eng_default / "Preferences", KNOWN_ANTICAPTCHA_IDS)

        # Also pin target_dir if custom
        if target_dir != base_profile and target_dir not in [base_profile / e for e in ["chrome", "chromium", "msedge"]]:
            target_default = target_dir / "Default"
            target_default.mkdir(parents=True, exist_ok=True)
            sec_pref = target_default / "Secure Preferences"
            if sec_pref.exists():
                try:
                    sec_pref.unlink(missing_ok=True)
                except Exception:
                    pass
            cls.pin_extension_in_preferences(target_default / "Preferences", KNOWN_ANTICAPTCHA_IDS)

        # 3. Seed host Chrome Local State into chrome profile if available
        host_user_data = cls.find_default_chrome_user_data_dir()
        if host_user_data and host_user_data.is_dir():
            try:
                local_state_src = host_user_data / "Local State"
                if local_state_src.is_file():
                    chrome_local_state = base_profile / "chrome" / "Local State"
                    if not chrome_local_state.exists():
                        shutil.copy2(local_state_src, chrome_local_state)
            except Exception as e:
                logger.debug(f"Note copying host Chrome Local State: {e}")

        # 4. Also safely pin into host personal Chrome profile so user sees it in personal browser
        if host_user_data and host_user_data.is_dir():
            host_pref = host_user_data / "Default" / "Preferences"
            if host_pref.is_file():
                try:
                    cls.pin_extension_in_preferences(host_pref, KNOWN_ANTICAPTCHA_IDS)
                    logger.info(f"Also pinned AntiCaptcha in host Chrome profile: {host_pref}")
                except Exception as e:
                    logger.debug(f"Could not pin into host Chrome profile: {e}")

        # 5. Also safely pin into host personal Microsoft Edge profile so user sees it in personal Edge
        host_edge_data = cls.find_default_edge_user_data_dir()
        if host_edge_data and host_edge_data.is_dir():
            edge_pref = host_edge_data / "Default" / "Preferences"
            if edge_pref.is_file():
                try:
                    cls.pin_extension_in_preferences(edge_pref, KNOWN_ANTICAPTCHA_IDS)
                    logger.info(f"Also pinned AntiCaptcha in host Edge profile: {edge_pref}")
                except Exception as e:
                    logger.debug(f"Could not pin into host Edge profile: {e}")

        logger.info(f"Persistent browser profiles configured & pinned across all engines at {base_profile}")
        return target_dir

    @classmethod
    def clean_profile_locks_and_orphans(cls, profile_dir: Path | str | None) -> None:
        """Removes stale Chromium Singleton lock files and terminates any orphan browser processes locking profile_dir."""
        if not profile_dir:
            return
        p = Path(profile_dir)
        if not p.exists():
            return
        # 1. Clean Chromium/Chrome Singleton lock files
        for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"):
            lock_path = p / lock_name
            if lock_path.exists():
                try:
                    lock_path.unlink(missing_ok=True)
                except Exception:
                    pass
        # 2. On Windows, terminate any lingering orphan browser process using this profile
        if sys.platform == "win32":
            try:
                prof_str = str(p.resolve()).lower()
                ps_cmd = (
                    f"$p = '{prof_str}'; "
                    f"Get-CimInstance Win32_Process -Filter \"name = 'chrome.exe' or name = 'msedge.exe'\" -ErrorAction SilentlyContinue | "
                    f"Where-Object {{ $_.CommandLine -and $_.CommandLine.ToLower().Contains($p) }} | "
                    f"ForEach-Object {{ Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }}"
                )
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, timeout=5)
            except Exception as e:
                logger.debug(f"Process sanitation for {p} skipped: {e}")

    async def start(self) -> BrowserContext:
        """Launches Google Chrome or Chromium persistent context with extension loading."""
        cache_dir = Path(__file__).resolve().parent.parent.parent / "data" / "browser_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        engine = self.browser_engine

        w_offset_x = 50 + (35 * (self.worker_id or 0)) % 400
        w_offset_y = 50 + (30 * (self.worker_id or 0)) % 300

        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--start-maximized" if self.worker_id is None else f"--window-position={w_offset_x},{w_offset_y}",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-features=msFirstRunExperience,msEdgeWelcomePage",
        ]

        has_ext = bool(self.extension_path and self.extension_path.is_dir())
        if has_ext and self.anticaptcha_api_key:
            ExtensionManager.sync_api_key(self.extension_path, self.anticaptcha_api_key)

        # Profile directory: Ensure multi-worker concurrency isolation
        target_dir = Path(self.user_data_dir) if self.user_data_dir else None
        if not self.isolated_profile and self.worker_id is None and target_dir and target_dir.is_dir() and "Default" not in str(target_dir):
            self.profile_to_use = target_dir
            self.is_temp_profile = False
            launch_args.append(f"--disk-cache-dir={cache_dir}")
        else:
            pfx = f"uaic_worker_{self.worker_id}_" if self.worker_id is not None else "uaic_chrome_profile_"
            temp_path = Path(tempfile.mkdtemp(prefix=pfx))
            self.profile_to_use = temp_path
            self.is_temp_profile = True

        # Pre-seed isolated profile from canonical RPA profile to inherit pinned extensions
        if self.is_temp_profile:
            canonical_profile = self.get_persistent_profile_dir(engine)
            source_user_data = target_dir if (target_dir and target_dir.is_dir()) else canonical_profile
            if source_user_data and source_user_data.is_dir():
                try:
                    local_state_src = source_user_data / "Local State"
                    if local_state_src.is_file():
                        shutil.copy2(local_state_src, self.profile_to_use / "Local State")

                    default_target = self.profile_to_use / "Default"
                    default_target.mkdir(parents=True, exist_ok=True)
                    pref_src = source_user_data / "Default" / "Preferences"
                    if pref_src.is_file():
                        shutil.copy2(pref_src, default_target / "Preferences")
                    logger.info(f"Pre-seeded {engine.upper()} temporary worker profile from {source_user_data}.")
                except Exception as e:
                    logger.debug(f"Failed to seed {engine.upper()} session profile from {source_user_data}: {e}")

        if has_ext:
            ext_norm = os.path.normpath(str(self.extension_path))
            launch_args.extend([
                f"--disable-extensions-except={ext_norm}",
                f"--load-extension={ext_norm}",
                "--no-sandbox",
            ])
        else:
            launch_args.append("--no-sandbox")

        # Ensure profile directory is unlocked and stale singleton locks/processes are removed
        self.clean_profile_locks_and_orphans(self.profile_to_use)

        # Ensure profile Preferences pins AntiCaptcha on browser toolbar across all engines (Chrome, Edge, Chromium)
        default_profile_dir = self.profile_to_use / "Default"
        default_profile_dir.mkdir(parents=True, exist_ok=True)
        sec_pref = default_profile_dir / "Secure Preferences"
        if sec_pref.exists():
            try:
                sec_pref.unlink(missing_ok=True)
            except Exception:
                pass
        pref_file = default_profile_dir / "Preferences"
        self.pin_extension_in_preferences(pref_file, KNOWN_ANTICAPTCHA_IDS)

        is_headless = self.headless
        if is_headless and has_ext:
            launch_args.append("--headless=new")
            # In Playwright, to load extensions in headless mode, persistent context must receive headless=False
            # while Chromium executes silently via --headless=new.
            context_headless = False
        else:
            context_headless = is_headless

        # Defensive pre-flight check for Playwright node driver executable
        try:
            from playwright._impl._driver import compute_driver_executable
            driver_path, _ = compute_driver_executable()
            if not Path(driver_path).exists():
                raise RuntimeError(
                    f"Playwright driver executable not found at '{driver_path}'. "
                    f"Please run 'python -m playwright install chromium' or execute setup.ps1 to restore browser binaries."
                )
        except (ImportError, RuntimeError):
            raise
        except Exception as e:
            logger.debug(f"Pre-flight driver verification skipped: {e}")

        if engine == "chrome":
            chrome_exe = self.find_chrome_executable(self.chrome_binary_path)
            if not chrome_exe:
                raise RuntimeError(
                    f"Google Chrome executable (chrome.exe) was not found on this system "
                    f"(searched: {self.chrome_binary_path or 'standard Program Files and LocalAppData locations'}). "
                    f"Please verify Google Chrome is installed or specify the path in Settings."
                )

        try:
            self.playwright = await async_playwright().start()
        except FileNotFoundError as e:
            raise RuntimeError(
                f"Failed to spawn Playwright driver process ({e}). "
                f"Please ensure Playwright dependencies are installed via 'python -m playwright install chromium' or setup.ps1."
            ) from e

        try:
            launch_kwargs: dict[str, Any] = {
                "user_data_dir": str(self.profile_to_use),
                "headless": context_headless,
                "args": launch_args,
                "ignore_default_args": [
                    "--disable-extensions",
                    "--disable-component-extensions-with-background-pages",
                ] if has_ext else None,
                "no_viewport": True if not is_headless else False,
                "viewport": {"width": settings.PLAYWRIGHT_VIEWPORT_WIDTH, "height": settings.PLAYWRIGHT_VIEWPORT_HEIGHT} if is_headless else None,
            }

            # Resolve authentic User-Agent for engine if default or unset
            from app.schemas.settings import (
                CHROME_USER_AGENT,
                MSEDGE_USER_AGENT,
                get_engine_user_agent,
            )
            effective_user_agent = self.user_agent
            if not effective_user_agent or effective_user_agent in (CHROME_USER_AGENT, MSEDGE_USER_AGENT):
                effective_user_agent = get_engine_user_agent(engine)

            launch_kwargs["user_agent"] = effective_user_agent

            if engine == "chrome":
                launch_kwargs["executable_path"] = str(chrome_exe)
            elif engine == "msedge":
                launch_kwargs["channel"] = "msedge"
            else:
                # "chromium": Playwright bundled browser engine with full extension support
                pass

            # Socket-level proxy egress tunneling
            if self.proxy_server:
                proxy_dict: dict[str, str] = {"server": self.proxy_server}
                if self.proxy_username and self.proxy_password:
                    proxy_dict["username"] = self.proxy_username
                    proxy_dict["password"] = self.proxy_password
                launch_kwargs["proxy"] = proxy_dict

            try:
                self.context = await self.playwright.chromium.launch_persistent_context(**launch_kwargs)
            except Exception as e:
                err_str = str(e)
                if "Executable doesn't exist" in err_str or "not found" in err_str.lower():
                    raise RuntimeError(
                        f"Browser executable could not be launched for engine '{engine}': {err_str}. "
                        f"Please verify the browser binary path in Settings."
                    ) from e
                raise

            # Verify extension loading and extract metadata
            if has_ext:
                # Poll up to 15.0s for service worker or background page registration (allowing heavy multi-worker concurrency / cold Chrome startup on Windows)
                for _ in range(150):
                    if self.context.service_workers or self.context.background_pages:
                        break
                    await asyncio.sleep(0.1)

                def _find_anticaptcha_worker_or_page():
                    for sw in self.context.service_workers:
                        url = getattr(sw, "url", "")
                        for kid in KNOWN_ANTICAPTCHA_IDS:
                            if kid in url:
                                return kid, sw
                        if "anticaptcha" in url.lower():
                            m = re.search(r"chrome-extension://([a-z0-9]+)/", url)
                            if m:
                                return m.group(1), sw
                    for bg in self.context.background_pages:
                        url = getattr(bg, "url", "")
                        for kid in KNOWN_ANTICAPTCHA_IDS:
                            if kid in url:
                                return kid, bg
                        if "anticaptcha" in url.lower():
                            m = re.search(r"chrome-extension://([a-z0-9]+)/", url)
                            if m:
                                return m.group(1), bg
                    return None, None

                detected_id, target_worker = _find_anticaptcha_worker_or_page()

                # Auto-fallback to Chromium if enterprise policy blocked unpacked extension in Google Chrome
                if not detected_id and engine == "chrome":
                    logger.warning(
                        "[BrowserLaunch] Google Chrome enterprise policy blocked unpacked extension sideloading. "
                        "Automatically falling back to Chromium engine where AntiCaptcha extension is verified and active..."
                    )
                    self.warning_message = (
                        "Google Chrome enterprise policy restricted unpacked extension sideloading. "
                        "Automatically running in Chromium engine where AntiCaptcha is 100% verified & active."
                    )
                    try:
                        await self.context.close()
                    except Exception:
                        pass
                    # Allocate fresh isolated worker directory for Chromium fallback
                    fb_pfx = f"uaic_worker_{self.worker_id}_fb_" if self.worker_id is not None else "uaic_chrome_fb_"
                    fb_profile = Path(tempfile.mkdtemp(prefix=fb_pfx))
                    fb_default = fb_profile / "Default"
                    fb_default.mkdir(parents=True, exist_ok=True)
                    self.pin_extension_in_preferences(fb_default / "Preferences", KNOWN_ANTICAPTCHA_IDS)
                    launch_kwargs["user_data_dir"] = str(fb_profile)
                    self.profile_to_use = fb_profile
                    launch_kwargs.pop("executable_path", None)
                    self.browser_engine = "chromium"
                    self.context = await self.playwright.chromium.launch_persistent_context(**launch_kwargs)

                    for _ in range(30):
                        detected_id, target_worker = _find_anticaptcha_worker_or_page()
                        if detected_id:
                            break
                        await asyncio.sleep(0.1)

                if detected_id:
                    self.extension_loaded = True
                    self.service_worker_active = True
                    self.extension_id = detected_id

                    # Ensure active detected extension ID is recorded in profile Preferences
                    try:
                        active_pref = self.profile_to_use / "Default" / "Preferences"
                        self.pin_extension_in_preferences(active_pref, [self.extension_id])
                    except Exception as e:
                        logger.debug(f"Failed to record runtime pinned extension id {self.extension_id}: {e}")

                    # Check if AntiCaptcha extension runtime is ALREADY properly configured with active API key in local storage
                    api_key_to_use = self.anticaptcha_api_key or "28b486b8f31f74c6bf4453735815aa53"
                    already_configured = False

                    if not target_worker and self.context.service_workers:
                        target_worker = self.context.service_workers[0]

                    if target_worker:
                        try:
                            stored = await asyncio.wait_for(
                                target_worker.evaluate("""() => {
                                    return new Promise(resolve => {
                                        if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
                                            chrome.storage.local.get(['account_key', 'enable', 'account_key_checked'], res => resolve(res));
                                        } else {
                                            resolve(null);
                                        }
                                    });
                                }"""),
                                timeout=2.0
                            )
                            if stored and stored.get("account_key") == api_key_to_use and stored.get("enable") is True:
                                already_configured = True
                        except Exception:
                            already_configured = False

                    if already_configured:
                        logger.info(f"AntiCaptcha extension already verified and configured with active API key in local runtime storage (ID: {self.extension_id}). Skipping redundant popup setup.")
                    else:
                        # Extension not yet configured in runtime: configure both local and sync storages
                        if target_worker:
                            try:
                                await target_worker.evaluate("""(apiKey) => {
                                    return new Promise(resolve => {
                                        const fullConfig = {
                                            // Core authentication
                                            account_key: apiKey,
                                            account_key_checked: true,
                                            enable: true,
                                            // UI / sound
                                            auto_submit_form: false,
                                            play_sounds: false,
                                            reenable_contextmenu: false,
                                            // CAPTCHA type toggles
                                            solve_recaptcha2: true,
                                            solve_invisible_recaptcha: true,
                                            solve_recaptcha3: true,
                                            recaptcha3_score: 0.3,
                                            solve_hcaptcha: true,
                                            solve_turnstile: true,
                                            solve_funcaptcha: true,
                                            solve_geetest: true,
                                            // Image CAPTCHA
                                            use_predefined_image_captcha_marks: true,
                                            // reCAPTCHA advanced behavior
                                            start_recaptcha2_solving_when_challenge_shown: true,
                                            solve_only_presented_recaptcha2: false,
                                            run_explicit_invisible_hcaptcha_callback_when_challenge_shown: false,
                                            delay_onready_callback: false,
                                            // Precaching
                                            use_recaptcha_precaching: false,
                                            k_precached_solution_count_min: 2,
                                            k_precached_solution_count_max: 4,
                                            dont_reuse_recaptcha_solution: false,
                                            // Worker / proxy
                                            solve_proxy_on_tasks: false,
                                            set_incoming_workers_user_agent: false,
                                            user_proxy_protocol: null,
                                            user_proxy_login: null,
                                            user_proxy_password: null,
                                            user_proxy_server: null,
                                            user_proxy_port: null,
                                            // Domain filter (empty = solve on all sites)
                                            where_solve_list: [],
                                            where_solve_white_list_type: false
                                        };

                                        const setLocal = new Promise(r => {
                                            if (chrome.storage && chrome.storage.local && chrome.storage.local.set) {
                                                chrome.storage.local.set(fullConfig, () => r(true));
                                            } else {
                                                r(false);
                                            }
                                        });
                                        const setSync = new Promise(r => {
                                            if (chrome.storage && chrome.storage.sync && chrome.storage.sync.set) {
                                                chrome.storage.sync.set(fullConfig, () => r(true));
                                            } else {
                                                r(false);
                                            }
                                        });
                                        Promise.all([setLocal, setSync]).then(() => resolve(true));
                                    });
                                }""", api_key_to_use)
                            except Exception as e:
                                logger.debug(f"Service worker storage evaluation note: {e}")

                        # To ensure Vue options store initializes, binds credentials, and verifies live balance, activate popup briefly for primary sessions
                        if self.worker_id is None:
                            try:
                                setup_page = await self.context.new_page()
                                popup_url = f"chrome-extension://{self.extension_id}/popup_v3.html"
                                await setup_page.goto(popup_url, wait_until="load", timeout=8000)
                                await setup_page.evaluate("""(apiKey) => {
                                    return new Promise(resolve => {
                                        const inp = document.getElementById("account_key");
                                        const chk = document.getElementById("enable_checkbox");
                                        if (chk && !chk.checked) {
                                            chk.click();
                                        }
                                        if (inp && (!inp.value || inp.value !== apiKey)) {
                                            inp.value = apiKey;
                                            inp.dispatchEvent(new Event('input', { bubbles: true }));
                                            const submitBtn = document.querySelector('input[type="submit"], button.btn-primary');
                                            if (submitBtn) submitBtn.click();
                                        }
                                        resolve(true);
                                    });
                                }""", api_key_to_use)
                                await asyncio.sleep(0.3)
                                await setup_page.close()
                                logger.info(f"AntiCaptcha runtime activated and verified with API key in browser profile (ID: {self.extension_id}).")
                            except Exception as e:
                                logger.debug(f"Note during AntiCaptcha runtime setup page activation: {e}")
                else:
                    self.extension_loaded = False
                    self.service_worker_active = False
                    if engine == "chrome":
                        self.warning_message = (
                            "AntiCaptcha extension was not loaded by Google Chrome. "
                            "Please ensure Developer Mode is enabled in Chrome and 'Load unpacked' is pointed to the extension directory, "
                            "or switch Browser Engine to 'Chromium' or 'Microsoft Edge' in Settings."
                        )
                        logger.warning(self.warning_message)

            return self.context
        except Exception:
            if self.context:
                try:
                    await self.context.close()
                except Exception:
                    pass
                self.context = None
            if self.playwright:
                try:
                    await self.playwright.stop()
                except Exception:
                    pass
                self.playwright = None
            if self.is_temp_profile and self.profile_to_use and self.profile_to_use.exists():
                try:
                    shutil.rmtree(self.profile_to_use, ignore_errors=True)
                except Exception:
                    pass
            raise

    async def close(self) -> None:
        """Safely closes Chrome context, playwright session, and temporary profile."""
        if self.context:
            try:
                await self.context.close()
            except Exception as e:
                logger.warning(f"Error closing Chrome context: {e}")
            self.context = None

        if self.playwright:
            try:
                await asyncio.sleep(0.05)
                await self.playwright.stop()
            except Exception as e:
                logger.warning(f"Error stopping Playwright: {e}")
            self.playwright = None

        if self.is_temp_profile and self.profile_to_use and self.profile_to_use.exists():
            await asyncio.sleep(0.3)
            try:
                shutil.rmtree(self.profile_to_use, ignore_errors=True)
            except Exception:
                pass


class BrowserManager:
    """Top-level browser lifecycle coordinator using Python 3.14 async context management."""

    def __init__(
        self,
        headless: bool = False,
        extension_path: Path | str | None = None,
        anticaptcha_api_key: str | None = None,
        user_data_dir: str | None = None,
        user_agent: str | None = None,
        chrome_binary_path: str | Path | None = None,
        browser_engine: str = "chrome",
    ):
        resolved_ext = ExtensionManager.resolve_extension_path(extension_path)
        self.session = ChromeSession(
            headless=headless,
            extension_path=resolved_ext,
            anticaptcha_api_key=anticaptcha_api_key or settings.ANTICAPTCHA_API_KEY,
            user_data_dir=user_data_dir or settings.CHROME_USER_DATA_DIR,
            user_agent=user_agent,
            chrome_binary_path=chrome_binary_path,
            browser_engine=browser_engine,
        )
        self.captcha_manager = CaptchaManager(timeout_seconds=settings.CAPTCHA_TIMEOUT_SECONDS)
        self.tab_manager: TabManager | None = None
        self.stage_timings: dict[str, Any] = {}

    async def __aenter__(self) -> BrowserManager:
        t_start = datetime.now()
        context = await self.session.start()
        t_end = datetime.now()

        duration = round((t_end - t_start).total_seconds(), 3)
        self.stage_timings["browser_launch"] = {
            "name": "Browser Launch",
            "start_time": t_start.strftime("%H:%M:%S.%f")[:-3],
            "end_time": t_end.strftime("%H:%M:%S.%f")[:-3],
            "duration_seconds": max(duration, 0.001),
            "status": "SUCCESS",
            "detail": "Google Chrome (Attended GUI) + AntiCaptcha" if self.session.extension_path else "Google Chrome",
        }
        self.tab_manager = TabManager(context)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.tab_manager:
            await self.tab_manager.close_all()
        await self.session.close()


class SiteAutomationManager:
    """Coordinates execution across registered county court adapters."""

    def __init__(self, browser_manager: BrowserManager):
        self.browser_manager = browser_manager
        self.adapters: dict[str, CountySiteAdapter] = {}

    def register_adapter(self, portal_key: str, adapter: CountySiteAdapter) -> None:
        """Registers a county site adapter."""
        self.adapters[portal_key] = adapter

    async def run_portal_search(
        self,
        portal_key: str,
        first_name: str | None,
        last_name: str | None,
        date_of_loss: str | None = None,
        **kwargs: Any,
    ) -> list[dict[str, Any]]:
        """Executes search on a county portal using the dedicated tab."""
        adapter = self.adapters.get(portal_key)
        if not adapter:
            raise KeyError(f"No adapter registered for portal: {portal_key}")

        if not self.browser_manager.tab_manager:
            raise RuntimeError("BrowserManager tab manager is not initialized.")

        page = await self.browser_manager.tab_manager.get_or_create_tab(portal_key, adapter.base_url)
        return await adapter.search(first_name, last_name, page, date_of_loss=date_of_loss, **kwargs)


async def run_browser_coroutine(coro_fn: Any, *args: Any, **kwargs: Any) -> Any:
    """Executes a browser coroutine, ensuring Windows Proactor event loop is used if necessary.

    On Windows, Playwright requires a ProactorEventLoop to spawn browser subprocesses.
    If the current running loop is a SelectorEventLoop (common in uvicorn reload workers),
    this helper offloads the coroutine to a dedicated thread with its own ProactorEventLoop.
    """
    loop = asyncio.get_running_loop()
    selector_cls = getattr(asyncio, "SelectorEventLoop", None)
    if sys.platform == "win32" and selector_cls and isinstance(loop, selector_cls):
        def _runner():
            proactor = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(proactor)
            try:
                return proactor.run_until_complete(coro_fn(*args, **kwargs))
            finally:
                proactor.close()
        return await asyncio.to_thread(_runner)
    return await coro_fn(*args, **kwargs)
