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
    "gcpdbjbmekkdlkpldjgffhmapgpdlcpj",  # Authentic Anti-Captcha extension ID (Web Store / Unpacked Developer Mode)
    "fignfifoniblkonapihmkfakmlgkbkcf",  # Local workspace Anti-Captcha extension ID
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
            norm_str = str(configured_path).replace("\\", "/").strip()
            clean_str = norm_str.strip("/")
            p = Path(norm_str)
            if not p.is_absolute():
                candidate_paths.append((repo_root / clean_str).resolve())
                candidate_paths.append((backend_dir / clean_str).resolve())
                candidate_paths.append((Path.cwd() / clean_str).resolve())
                candidate_paths.append(Path(f"/app/{clean_str.lstrip('./')}"))
            else:
                candidate_paths.append(p)

        # Canonical project fallback if DB config is missing/invalid
        candidate_paths.extend([
            backend_dir / "anticaptcha-plugin_v0.83",
            repo_root / "anticaptcha-plugin_v0.83",
            Path.cwd() / "anticaptcha-plugin_v0.83",
            Path("/app/anticaptcha-plugin_v0.83"),
        ])

        for p in candidate_paths:
            try:
                if p.is_dir() and (p / "manifest.json").exists():
                    # Chromium explicitly rejects unpacked extensions if any folder starting with '_' exists except '_locales'
                    try:
                        for child in p.iterdir():
                            if child.is_dir() and child.name.startswith("_") and child.name != "_locales":
                                import shutil
                                shutil.rmtree(child, ignore_errors=True)
                    except Exception as e:
                        logger.debug(f"Failed to clean reserved underscore dirs in extension: {e}")
                    return p.resolve()
            except Exception:
                continue

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
    def runtime_config(api_key: str, auto_cfg: Any = None) -> dict[str, Any]:
        """Build the complete AntiCaptcha storage payload from current settings."""
        return {
            "account_key": api_key.strip(),
            "account_key_checked": True,
            "enable": bool(getattr(auto_cfg, "anticaptcha_enabled", True)),
            "auto_submit_form": bool(getattr(auto_cfg, "anticaptcha_auto_submit", False)),
            "play_sounds": bool(getattr(auto_cfg, "anticaptcha_play_sounds", False)),
            "solve_recaptcha2": bool(getattr(auto_cfg, "anticaptcha_solve_recaptcha2", True)),
            "solve_invisible_recaptcha": bool(getattr(auto_cfg, "anticaptcha_solve_invisible", True)),
            "solve_recaptcha3": bool(getattr(auto_cfg, "anticaptcha_solve_recaptcha3", True)),
            "recaptcha3_score": float(getattr(auto_cfg, "anticaptcha_recaptcha3_score", 0.3)),
            "solve_hcaptcha": bool(getattr(auto_cfg, "anticaptcha_solve_hcaptcha", True)),
            "solve_turnstile": bool(getattr(auto_cfg, "anticaptcha_solve_turnstile", True)),
            "solve_funcaptcha": bool(getattr(auto_cfg, "anticaptcha_solve_funcaptcha", True)),
            "solve_geetest": bool(getattr(auto_cfg, "anticaptcha_solve_geetest", True)),
            "use_predefined_image_captcha_marks": True,
            "start_recaptcha2_solving_when_challenge_shown": True,
            "solve_only_presented_recaptcha2": False,
            "run_explicit_invisible_hcaptcha_callback_when_challenge_shown": False,
            "delay_onready_callback": False,
            "use_recaptcha_precaching": False,
            "k_precached_solution_count_min": 2,
            "k_precached_solution_count_max": 4,
            "dont_reuse_recaptcha_solution": False,
            "solve_proxy_on_tasks": False,
            "set_incoming_workers_user_agent": False,
            "reenable_contextmenu": False,
            "where_solve_list": [],
            "where_solve_white_list_type": False,
        }

    @staticmethod
    def sync_api_key(extension_dir: Path | str, api_key: str, auto_cfg: Any = None) -> bool:
        """Injects Anti-Captcha API key and plugin settings into config_ac_api_key.js.

        Uses dynamic values from auto_cfg (AutomationSettings) when provided,
        otherwise falls back to safe defaults matching Power Automate V4 behavior.
        """
        if not api_key:
            return False

        config = ExtensionManager.runtime_config(api_key, auto_cfg)
        enabled = config["enable"]
        auto_submit = config["auto_submit_form"]
        play_sounds = config["play_sounds"]
        solve_rc2 = config["solve_recaptcha2"]
        solve_invisible = config["solve_invisible_recaptcha"]
        solve_rc3 = config["solve_recaptcha3"]
        rc3_score = config["recaptcha3_score"]
        solve_hcaptcha = config["solve_hcaptcha"]
        solve_turnstile = config["solve_turnstile"]
        solve_funcaptcha = config["solve_funcaptcha"]
        solve_geetest = config["solve_geetest"]

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
                m = re.search(r"chrome-extension://([a-z0-9]+)/", url)
                if m:
                    active = True
                    found_id = m.group(1)
                    break
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
                    m = re.search(r"chrome-extension://([a-z0-9]+)/", url)
                    if m:
                        active = True
                        found_id = m.group(1)
                        break
                if active:
                    break

        return {
            "loaded": active,
            "service_workers_count": len(sws),
            "background_pages_count": len(bg_pages),
            "extension_id": found_id,
            "details": f"AntiCaptcha extension verified ({found_id})" if active else "Extension not loaded (0 active AntiCaptcha workers)",
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
        timeout = self.timeout_seconds if wait_seconds is None else wait_seconds
        if timeout <= 0:
            return False
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        try:
            return await asyncio.wait_for(
                self._detect_and_solve_until(page, deadline, timeout),
                timeout=timeout,
            )
        except TimeoutError:
            logger.warning("CAPTCHA verification timed out after %s seconds.", timeout)
            return False

    async def _detect_and_solve_until(self, page: Page, deadline: float, timeout: float) -> bool:
        if not await self._is_challenge_present(page):
            return True

        logger.info("CAPTCHA challenge detected. Initiating condition-based verification (timeout: %ss)...", timeout)

        while asyncio.get_running_loop().time() < deadline:
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

            remaining = deadline - asyncio.get_running_loop().time()
            if remaining > 0:
                await asyncio.sleep(min(self.poll_interval_ms / 1000, remaining))

        logger.warning("CAPTCHA verification timed out after %s seconds.", timeout)
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

    def __init__(self, context: BrowserContext, timeout_ms: int | None = None):
        self.context = context
        self.timeout_ms = timeout_ms if timeout_ms is not None else settings.PLAYWRIGHT_TIMEOUT_MS
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
        page.set_default_timeout(self.timeout_ms)
        page.set_default_navigation_timeout(self.timeout_ms)
        await page.bring_to_front()

        if initial_url:
            await page.goto(initial_url, wait_until="domcontentloaded", timeout=self.timeout_ms)

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
        force_kill: bool = False,
        load_extension: bool = True,
        auto_cfg: Any = None,
    ):
        self.headless = headless
        self.force_kill = force_kill
        self.load_extension = load_extension
        self.extension_path = ExtensionManager.resolve_extension_path(extension_path) if load_extension else None
        self.anticaptcha_api_key = anticaptcha_api_key
        self.auto_cfg = auto_cfg
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
        """Locates Google Chrome executable on Windows and Linux with user override support."""
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
            Path("/usr/bin/google-chrome"),
            Path("/usr/bin/google-chrome-stable"),
            Path("/opt/google/chrome/chrome"),
        ]
        for p in system_paths:
            if p.is_file():
                return p.resolve()

        for cmd in ("google-chrome", "google-chrome-stable"):
            found = shutil.which(cmd)
            if found and Path(found).is_file():
                return Path(found).resolve()

        return None

    @staticmethod
    def find_chromium_executable(configured_path: str | Path | None = None) -> Path | None:
        """Locates Playwright bundled Chromium or system Chromium across Linux/Docker and Windows."""
        if configured_path:
            p = Path(configured_path)
            if p.is_file():
                return p.resolve()

        # 1. Check Playwright bundled binary paths on Linux / Docker
        linux_playwright_patterns = [
            Path("/ms-playwright"),
            Path.home() / ".cache" / "ms-playwright",
        ]
        for base_dir in linux_playwright_patterns:
            if base_dir.is_dir():
                for chrome_candidate in sorted(base_dir.glob("chromium-*/chrome-linux*/chrome"), reverse=True):
                    if chrome_candidate.is_file() and os.access(chrome_candidate, os.X_OK):
                        return chrome_candidate.resolve()

        # 2. Check Playwright bundled binary paths on Windows
        local_app_data = os.environ.get("LocalAppData", "")
        if local_app_data:
            pw_win_dir = Path(local_app_data) / "ms-playwright"
            if pw_win_dir.is_dir():
                for chrome_candidate in sorted(pw_win_dir.glob("chromium-*\\chrome-win*\\chrome.exe"), reverse=True):
                    if chrome_candidate.is_file():
                        return chrome_candidate.resolve()

        # 3. Check system PATH
        for cmd in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable"):
            found = shutil.which(cmd)
            if found and Path(found).is_file():
                return Path(found).resolve()

        # 4. Try discovery via playwright driver
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as pw:
                exe = pw.chromium.executable_path
                if exe and Path(exe).is_file():
                    return Path(exe).resolve()
        except Exception:
            pass

        return None

    @staticmethod
    def find_default_edge_executable() -> Path | None:
        """Locates Microsoft Edge executable on Windows and Linux."""
        edge_paths = [
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
            Path(os.environ.get("LocalAppData", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
            Path("/usr/bin/microsoft-edge"),
            Path("/usr/bin/microsoft-edge-stable"),
            Path("/opt/microsoft/msedge/msedge"),
        ]
        for p in edge_paths:
            if p.is_file():
                return p.resolve()

        for cmd in ("microsoft-edge", "microsoft-edge-stable", "msedge"):
            found = shutil.which(cmd)
            if found and Path(found).is_file():
                return Path(found).resolve()

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
            ui_prefs = ext_prefs.setdefault("ui", {})
            ui_prefs["developer_mode"] = True

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

            # Also ensure Secure Preferences does not contain a stale tracked_preferences_reset
            sec_pref_file = pref_file.parent / "Secure Preferences"
            if sec_pref_file.is_file():
                try:
                    sec_prefs = json.loads(sec_pref_file.read_text(encoding="utf-8"))
                    changed = False
                    if "prefs.tracked_preferences_reset" in sec_prefs:
                        sec_prefs.pop("prefs.tracked_preferences_reset", None)
                        changed = True
                    if changed:
                        sec_pref_file.write_text(json.dumps(sec_prefs, indent=2), encoding="utf-8")
                except Exception:
                    pass
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
        auto_cfg: Any = None,
    ) -> Path:
        """Configures persistent browser profiles across Chrome, Chromium, and Edge with AntiCaptcha extension and modern toolbar pinning."""
        base_profile = cls.get_persistent_profile_dir()
        target_dir = profile_dir or base_profile
        target_dir.mkdir(parents=True, exist_ok=True)
        resolved_ext = ExtensionManager.resolve_extension_path(extension_path)

        # 1. Sync API Key to extension directory if provided
        if resolved_ext and resolved_ext.is_dir() and api_key:
            if auto_cfg is not None or not ExtensionManager.is_extension_configured(resolved_ext, api_key):
                ExtensionManager.sync_api_key(resolved_ext, api_key, auto_cfg)

        # 2. Pin into all 3 engine-specific persistent profiles (chrome, chromium, msedge)
        for eng in ["chrome", "chromium", "msedge"]:
            eng_default = base_profile / eng / "Default"
            eng_default.mkdir(parents=True, exist_ok=True)
            cls.pin_extension_in_preferences(eng_default / "Preferences", KNOWN_ANTICAPTCHA_IDS)

        # Also pin target_dir if custom and seed extension state if needed
        if target_dir != base_profile and target_dir not in [base_profile / e for e in ["chrome", "chromium", "msedge"]]:
            target_default = target_dir / "Default"
            target_default.mkdir(parents=True, exist_ok=True)
            cls.pin_extension_in_preferences(target_default / "Preferences", KNOWN_ANTICAPTCHA_IDS)
            chrome_default = base_profile / "chrome" / "Default"
            if chrome_default.is_dir():
                sec_src = chrome_default / "Secure Preferences"
                sec_dst = target_default / "Secure Preferences"
                if sec_src.is_file() and not sec_dst.exists():
                    try:
                        shutil.copy2(sec_src, sec_dst)
                    except Exception as e_sec:
                        logger.debug(f"Note copying Secure Preferences: {e_sec}")
                for ext_sub in ["Extension Rules", "Extension Scripts", "Extension State", "Local Extension Settings", "Sync Extension Settings", "Extensions"]:
                    sub_src = chrome_default / ext_sub
                    sub_dest = target_default / ext_sub
                    if sub_src.is_dir() and not sub_dest.exists():
                        try:
                            shutil.copytree(sub_src, sub_dest, dirs_exist_ok=True)
                        except Exception as e_sub:
                            logger.debug(f"Note copying extension subfolder {ext_sub}: {e_sub}")

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
    def is_profile_locked(cls, profile_dir: Path | str | None) -> bool:
        """Checks if the profile directory is currently locked by a live process."""
        if not profile_dir:
            return False
        p = Path(profile_dir)
        if not p.exists():
            return False

        # 1. Check Windows lockfile
        lock_path = p / "lockfile"
        if lock_path.exists():
            try:
                with open(lock_path, "r+"):
                    pass
            except (PermissionError, OSError):
                return True

        # 2. Check POSIX / Linux Chromium SingletonLock symlink pointing to <hostname>-<pid>
        singleton_lock = p / "SingletonLock"
        if singleton_lock.is_symlink() or singleton_lock.exists():
            if sys.platform != "win32":
                try:
                    import os
                    target = os.readlink(str(singleton_lock))
                    pid_str = target.rsplit("-", 1)[-1]
                    if pid_str.isdigit():
                        pid = int(pid_str)
                        if pid != os.getpid():
                            os.kill(pid, 0)
                            return True
                except (OSError, ValueError):
                    pass
            else:
                return True

        # 3. Check Chromium SingletonSocket
        singleton_socket = p / "SingletonSocket"
        if singleton_socket.exists() and (singleton_lock.exists() or singleton_lock.is_symlink()):
            return True

        return False

    @classmethod
    def clean_profile_locks_and_orphans(cls, profile_dir: Path | str | None, force_kill: bool = False) -> None:
        """Removes stale Chromium Singleton lock files and terminates any orphan browser processes locking profile_dir."""
        if not profile_dir:
            return
        p = Path(profile_dir)
        if not p.exists():
            return

        # 1. On Windows, terminate any lingering orphan browser process using this profile FIRST
        if sys.platform == "win32":
            if force_kill:
                logger.warning("Aggressive Force Kill enabled: Terminating all Google Chrome and Edge background processes.")
                subprocess.run(["taskkill", "/F", "/IM", "chrome.exe", "/T"], capture_output=True)
                subprocess.run(["taskkill", "/F", "/IM", "msedge.exe", "/T"], capture_output=True)
            else:
                try:
                    prof_str = str(p.resolve()).lower()
                    ps_cmd = (
                        f"$p = '{prof_str}'; "
                        f"$pids = Get-CimInstance Win32_Process -Filter \"name = 'chrome.exe' or name = 'msedge.exe'\" -ErrorAction SilentlyContinue | "
                        f"Where-Object {{ $_.CommandLine -and $_.CommandLine.ToLower().Contains($p) }} | "
                        f"Select-Object -ExpandProperty ProcessId; "
                        f"if ($pids) {{ $pids -join ',' }}"
                    )
                    proc = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True, timeout=15)
                    pids_raw = (proc.stdout or "").strip()
                    if pids_raw:
                        for pid_str in pids_raw.split(","):
                            pid_clean = pid_str.strip()
                            if pid_clean.isdigit():
                                subprocess.run(["taskkill", "/F", "/T", "/PID", pid_clean], capture_output=True)
                                logger.info(f"Terminated orphan browser process tree for PID {pid_clean} (profile: {p.name})")
                except Exception as e:
                    logger.debug(f"Process sanitation for {p} skipped or completed: {e}")
        elif force_kill:
            # On Linux container, terminate any lingering orphan browser processes if force_kill requested
            try:
                subprocess.run(["pkill", "-9", "-f", "chrome"], capture_output=True)
            except Exception as e:
                logger.debug(f"Linux force kill skipped: {e}")

        # 2. Allow brief pause for OS kernel handle release
        import time as _time
        _time.sleep(0.3)

        # 3. Clean Chromium/Chrome Singleton lock files AFTER processes have stopped
        for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"):
            lock_path = p / lock_name
            if lock_path.exists() or (hasattr(lock_path, "is_symlink") and lock_path.is_symlink()):
                # On Linux, do NOT remove SingletonLock/SingletonSocket if the holding process is still alive and not force_kill
                if lock_name in ("SingletonLock", "SingletonSocket") and sys.platform != "win32" and not force_kill:
                    try:
                        import os
                        sl = p / "SingletonLock"
                        if sl.is_symlink() or sl.exists():
                            target = os.readlink(str(sl))
                            pid_str = target.rsplit("-", 1)[-1]
                            if pid_str.isdigit() and int(pid_str) != os.getpid():
                                os.kill(int(pid_str), 0)
                                # Process is alive! Preserve lock so callers detect it
                                continue
                    except (OSError, ValueError):
                        pass
                try:
                    lock_path.unlink(missing_ok=True)
                except Exception:
                    pass

        # 4. Clean any stale HMAC reset triggers from Secure Preferences
        for def_dir in (p, p / "Default"):
            sec_pref = def_dir / "Secure Preferences"
            if sec_pref.is_file():
                try:
                    sec_data = json.loads(sec_pref.read_text(encoding="utf-8"))
                    if "prefs.tracked_preferences_reset" in sec_data:
                        sec_data.pop("prefs.tracked_preferences_reset", None)
                        sec_pref.write_text(json.dumps(sec_data, indent=2), encoding="utf-8")
                except Exception:
                    pass

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
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-features=msFirstRunExperience,msEdgeWelcomePage",
        ]

        has_ext = bool(self.extension_path and self.extension_path.is_dir())
        if has_ext and self.anticaptcha_api_key:
            if self.auto_cfg is not None or not ExtensionManager.is_extension_configured(self.extension_path, self.anticaptcha_api_key):
                ExtensionManager.sync_api_key(self.extension_path, self.anticaptcha_api_key, self.auto_cfg)

        # Profile directory: Strictly enforce Scenario 2 (Fallback if empty)
        clean_user_dir = str(self.user_data_dir).strip() if self.user_data_dir else ""
        target_dir = Path(clean_user_dir) if clean_user_dir else None

        if not self.isolated_profile and self.worker_id is None and target_dir and target_dir.is_dir() and "Default" not in str(target_dir):
            self.profile_to_use = target_dir
            self.is_temp_profile = False
            launch_args.append(f"--disk-cache-dir={cache_dir}")
        else:
            pfx = f"uaic_worker_{self.worker_id}_" if self.worker_id is not None else "uaic_chrome_profile_"
            temp_path = Path(tempfile.mkdtemp(prefix=pfx))
            self.profile_to_use = temp_path
            self.is_temp_profile = True

        # Ensure profile directory is unlocked (Pass force_kill flag)
        self.clean_profile_locks_and_orphans(self.profile_to_use, force_kill=self.force_kill)

        # Check if profile is still locked by an external browser instance
        if not self.is_temp_profile and self.is_profile_locked(self.profile_to_use):
            if not self.force_kill:
                # If canonical profile is still locked, safely fall back to an isolated seeded temp profile
                logger.warning(
                    f"Profile '{self.profile_to_use}' remains locked by another process. "
                    f"Auto-falling back to an isolated session profile pre-seeded from canonical profile."
                )
                pfx = f"uaic_worker_{self.worker_id}_" if self.worker_id is not None else "uaic_chrome_profile_"
                temp_path = Path(tempfile.mkdtemp(prefix=pfx))
                source_user_data = self.profile_to_use
                self.profile_to_use = temp_path
                self.is_temp_profile = True
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
                        # Note: Secure Preferences is explicitly omitted to prevent HMAC corruption across profile directories
                    except Exception as e:
                        logger.debug(f"Failed to seed fallback profile: {e}")

        # Pre-seed isolated profile from canonical RPA profile to inherit pinned extensions
        if self.is_temp_profile:
            canonical_engine = engine
            canonical_profile = self.get_persistent_profile_dir(canonical_engine)
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
                    # Note: Secure Preferences is explicitly omitted to prevent HMAC corruption across profile directories

                    for ext_sub in ["Extension Rules", "Extension Scripts", "Extension State", "Local Extension Settings", "Sync Extension Settings", "Extensions"]:
                        sub_src = source_user_data / "Default" / ext_sub
                        sub_dest = default_target / ext_sub
                        if sub_src.is_dir():
                            shutil.copytree(sub_src, sub_dest, dirs_exist_ok=True)

                    logger.info(f"Pre-seeded {engine.upper()} temporary worker profile from {source_user_data}.")
                except Exception as e:
                    logger.debug(f"Failed to seed {engine.upper()} session profile from {source_user_data}: {e}")

        # Ensure profile Preferences pins AntiCaptcha on browser toolbar across all engines (Chrome, Edge, Chromium)
        default_profile_dir = self.profile_to_use / "Default"
        default_profile_dir.mkdir(parents=True, exist_ok=True)
        pref_file = default_profile_dir / "Preferences"
        self.pin_extension_in_preferences(pref_file, KNOWN_ANTICAPTCHA_IDS)

        # Always check, configure, and pin AntiCaptcha across all persistent profiles before launching
        try:
            self.configure_and_pin_profile(
                profile_dir=self.profile_to_use,
                api_key=self.anticaptcha_api_key,
                extension_path=self.extension_path,
                auto_cfg=self.auto_cfg,
            )
            logger.info(f"[ChromeSession] Pre-flight: AntiCaptcha extension automatically configured & pinned at {self.profile_to_use}")
        except Exception as e_pin:
            logger.warning(f"[ChromeSession] Note auto-configuring/pinning extension profile: {e_pin}")

        if has_ext and self.load_extension:
            ext_norm = os.path.normpath(str(self.extension_path))
            launch_args.extend([
                f"--disable-extensions-except={ext_norm}",
                f"--load-extension={ext_norm}",
                "--enable-developer-mode",
                # Bypass Chrome content verifier hash-check for unpacked/modified extensions.
                # Chrome logs show "content mismatch for _locales/*/messages.json & manifest.json"
                # because the Web Store signature doesn't match the unpacked files on disk.
                "--disable-extension-content-verification",
                "--disable-extensions-file-access-check",
                "--allow-outdated-plugins",
                "--disable-infobars",
            ])
            if sys.platform != "win32":
                launch_args.append("--no-sandbox")
        else:
            launch_args.extend(["--disable-infobars"])
            if sys.platform != "win32":
                launch_args.append("--no-sandbox")

        is_headless = self.headless
        if sys.platform != "win32" and "DISPLAY" not in os.environ:
            if not is_headless:
                logger.info("Attended GUI requested but running in container without DISPLAY. Executing headlessly.")
            is_headless = True
            launch_args.extend(["--disable-gpu", "--disable-dev-shm-usage"])

        if is_headless and has_ext:
            launch_args.append("--headless=new")
            # In Playwright, to load extensions in headless mode, persistent context must receive headless=False
            # while Chromium executes silently via --headless=new.
            if sys.platform != "win32" and "DISPLAY" not in os.environ:
                context_headless = True
            else:
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

        chrome_exe = None
        if engine in ("chrome", "google-chrome"):
            chrome_exe = self.find_chrome_executable(self.chrome_binary_path)
            if not chrome_exe and sys.platform != "win32":
                chrome_exe = self.find_chromium_executable()
            if self.chrome_binary_path and not chrome_exe:
                raise RuntimeError(
                    f"Google Chrome executable was not found on this system "
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

            if engine in ("chrome", "google-chrome"):
                if chrome_exe:
                    launch_kwargs["executable_path"] = str(chrome_exe)
                else:
                    launch_kwargs["channel"] = "chrome"
            elif engine in ("edge", "msedge", "microsoft-edge"):
                edge_exe = self.find_default_edge_executable()
                if self.chrome_binary_path and "edge" in str(self.chrome_binary_path).lower() and os.path.isfile(self.chrome_binary_path):
                    launch_kwargs["executable_path"] = str(self.chrome_binary_path)
                elif edge_exe:
                    launch_kwargs["executable_path"] = str(edge_exe)
                else:
                    launch_kwargs["channel"] = "msedge"
            elif engine == "chromium":
                chrom_exe = self.find_chromium_executable(self.chrome_binary_path)
                if chrom_exe:
                    launch_kwargs["executable_path"] = str(chrom_exe)

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
                # Catch profile lock and exitCode 21 (RESULT_CODE_PROFILE_IN_USE)
                if (
                    "exitcode=21" in err_str.lower()
                    or "opening in existing browser session" in err_str.lower()
                    or "profile is already in use" in err_str.lower()
                ):
                    if not self.is_temp_profile:
                        logger.warning(
                            f"Persistent profile '{self.profile_to_use}' collision detected ({err_str}). "
                            f"Auto-falling back to an isolated session profile pre-seeded from canonical profile."
                        )
                        pfx = f"uaic_worker_{self.worker_id}_" if self.worker_id is not None else "uaic_chrome_profile_"
                        temp_path = Path(tempfile.mkdtemp(prefix=pfx))
                        source_user_data = self.profile_to_use
                        self.profile_to_use = temp_path
                        self.is_temp_profile = True
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
                                for ext_sub in ["Extension Rules", "Extension Scripts", "Extension State", "Local Extension Settings", "Sync Extension Settings", "Extensions"]:
                                    sub_src = source_user_data / "Default" / ext_sub
                                    sub_dest = default_target / ext_sub
                                    if sub_src.is_dir():
                                        shutil.copytree(sub_src, sub_dest, dirs_exist_ok=True)
                            except Exception as seed_err:
                                logger.debug(f"Failed to seed fallback profile: {seed_err}")
                        self.pin_extension_in_preferences(self.profile_to_use / "Default" / "Preferences", KNOWN_ANTICAPTCHA_IDS)
                        try:
                            self.configure_and_pin_profile(
                                profile_dir=self.profile_to_use,
                                api_key=self.anticaptcha_api_key,
                                extension_path=self.extension_path,
                                auto_cfg=self.auto_cfg,
                            )
                        except Exception:
                            pass
                        launch_kwargs["user_data_dir"] = str(self.profile_to_use)
                        self.context = await self.playwright.chromium.launch_persistent_context(**launch_kwargs)
                    else:
                        raise RuntimeError(
                            f"PROFILE LOCK DETECTED (exitCode=21): The profile directory '{self.profile_to_use}' is currently locked by another active Chrome process.\n\n"
                            f"Even if the browser window is not visible, background processes or stale locks are holding the profile.\n\n"
                            f"HOW TO FIX:\n"
                            f"1) Click 'Force Kill Chrome & Retry' in Settings to terminate all background browser processes.\n"
                            f"2) Or open Windows Task Manager and close any remaining 'chrome.exe' / 'msedge.exe' tasks."
                        ) from e
                elif "executable doesn't exist" in err_str.lower() or ("browser executable" in err_str.lower() and "not found" in err_str.lower()):
                    raise RuntimeError(
                        f"Browser executable could not be launched for engine '{engine}': {err_str}. "
                        f"Please verify the browser binary path in Settings."
                    ) from e
                raise

            # Verify extension loading and extract metadata
            if has_ext and self.load_extension:
                api_key_to_use = self.anticaptcha_api_key
                config_payload = (
                    ExtensionManager.runtime_config(api_key_to_use, self.auto_cfg)
                    if api_key_to_use and self.auto_cfg is not None else None
                )
                detected_id = None

                # Helper to scan for AntiCaptcha extension ID, recognizing known IDs and extension service workers
                def _scan_for_extension():
                    import re as _re
                    for sw in self.context.service_workers:
                        url = getattr(sw, "url", "")
                        for kid in KNOWN_ANTICAPTCHA_IDS:
                            if kid in url:
                                return kid
                        m = _re.search(r"chrome-extension://([a-z0-9]+)/", url)
                        if m:
                            return m.group(1)
                    for bg in self.context.background_pages:
                        url = getattr(bg, "url", "")
                        for kid in KNOWN_ANTICAPTCHA_IDS:
                            if kid in url:
                                return kid
                        m = _re.search(r"chrome-extension://([a-z0-9]+)/", url)
                        if m:
                            return m.group(1)
                    return None

                # Wait for service worker to register — Chrome takes longer than Chromium for unpacked extensions.
                # Extended from 15x0.2s=3s to 30x0.3s=9s to accommodate Chrome's slower extension loading.
                for attempt_i in range(30):
                    detected_id = _scan_for_extension()
                    if detected_id:
                        break
                    if attempt_i % 10 == 9:
                        logger.debug(f"[BrowserLaunch] Waiting for extension service worker... ({(attempt_i+1)*0.3:.1f}s elapsed)")
                    await asyncio.sleep(0.3)

                # If not detected via dormant service worker list, probe chrome://extensions to query registry directly
                if not detected_id and self.context:
                    try:
                        probe_page = await self.context.new_page()
                        try:
                            await probe_page.goto("chrome://extensions", wait_until="domcontentloaded", timeout=5000)
                            # Ensure Developer Mode toggle is activated
                            await probe_page.evaluate("""() => {
                                try {
                                    const manager = document.querySelector('extensions-manager');
                                    const toolbar = manager?.shadowRoot?.querySelector('extensions-toolbar');
                                    const devModeToggle = toolbar?.shadowRoot?.querySelector('#devMode');
                                    if (devModeToggle && !devModeToggle.checked) {
                                        devModeToggle.click();
                                    }
                                } catch (e) {}
                            }""")
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
                                if item.get("id") in KNOWN_ANTICAPTCHA_IDS or "anticaptcha" in item.get("name", "").lower():
                                    if item.get("state") == "ENABLED":
                                        detected_id = item.get("id")
                                        break
                        finally:
                            await probe_page.close()
                    except Exception as probe_err:
                        logger.debug(f"Probe for extension on chrome://extensions note: {probe_err}")

                if not detected_id:
                    logger.warning(
                        f"[ChromeSession] AntiCaptcha extension service worker not detected in {engine} after 9s. "
                        f"Launched with --disable-extension-content-verification flag. "
                        f"Check chrome://extensions to confirm the extension is ENABLED."
                    )

                # Verify Configuration if Extension is active
                if detected_id:
                    self.extension_id = detected_id
                    self.extension_loaded = True
                    self.service_worker_active = True

                    # Compare every configured solver option so changes take effect on the next launch.
                    already_configured = False
                    if config_payload:
                        for sw in self.context.service_workers:
                            if detected_id in getattr(sw, "url", ""):
                                try:
                                    stored = await sw.evaluate("keys => chrome.storage.local.get(keys)", list(config_payload))
                                    already_configured = isinstance(stored, dict) and all(stored.get(key) == value for key, value in config_payload.items())
                                    if already_configured:
                                        logger.info(f"[BrowserLaunch] AntiCaptcha already configured via service worker (ID: {self.extension_id}).")
                                        break
                                except Exception:
                                    pass

                    if config_payload and not already_configured:
                        setup_page = None
                        try:
                            setup_page = await self.context.new_page()
                            popup_url = f"chrome-extension://{self.extension_id}/popup_v3.html"

                            await setup_page.goto(popup_url, wait_until="domcontentloaded", timeout=8000)

                            # Apply the configured values after popup controls initialize their store.
                            configured = await setup_page.evaluate("""async (config) => {
                                if (typeof chrome === 'undefined' || !chrome.storage?.local) return false;
                                const keys = Object.keys(config);
                                const matches = res => keys.every(
                                    key => JSON.stringify(res[key]) === JSON.stringify(config[key])
                                );
                                const inp = document.getElementById('account_key');
                                const chk = document.getElementById('enable_checkbox');
                                if (chk && chk.checked !== config.enable) chk.click();
                                if (inp && inp.value !== config.account_key) {
                                    inp.value = config.account_key;
                                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                                    const submitBtn = document.querySelector('input[type="submit"], button.btn-primary');
                                    if (submitBtn) submitBtn.click();
                                }
                                await new Promise(resolve => setTimeout(resolve, 100));
                                await new Promise(resolve => chrome.storage.local.set(config, resolve));
                                if (chrome.storage.sync) {
                                    await new Promise(resolve => chrome.storage.sync.set(config, resolve));
                                }
                                const stored = await new Promise(resolve => chrome.storage.local.get(keys, resolve));
                                return matches(stored);
                            }""", config_payload)

                            await setup_page.close()
                            if configured is True:
                                logger.info(f"[BrowserLaunch] AntiCaptcha verified and configuration synced (ID: {self.extension_id}).")
                            else:
                                self.warning_message = "AntiCaptcha settings could not be verified after browser launch."
                                logger.warning(self.warning_message)
                        except Exception as e:
                            logger.warning(f"[BrowserLaunch] Failed to inspect/update AntiCaptcha config: {e}")
                            if setup_page:
                                try:
                                    await setup_page.close()
                                except Exception:
                                    pass
                    elif not api_key_to_use:
                        self.warning_message = "AntiCaptcha extension loaded without an API key; automatic solving is unavailable."
                        logger.warning(self.warning_message)
                    else:
                        logger.info("AntiCaptcha extension loaded with existing preferences preserved.")
                else:
                    self.extension_loaded = False
                    self.service_worker_active = False
                    self.warning_message = (
                        f"AntiCaptcha extension was not loaded by {engine}. "
                        "Please verify Developer Mode is enabled and the unpacked extension is loaded in chrome://extensions."
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
        elif self.profile_to_use and self.profile_to_use.exists():
            try:
                self.clean_profile_locks_and_orphans(self.profile_to_use)
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
        auto_cfg: Any = None,
    ):
        configured_extension = extension_path if extension_path is not None else getattr(auto_cfg, "chrome_extension_dir", None)
        resolved_ext = ExtensionManager.resolve_extension_path(configured_extension)
        self.auto_cfg = auto_cfg
        configured_key = (
            getattr(auto_cfg, "anticaptcha_api_key", None) if auto_cfg is not None
            else anticaptcha_api_key if anticaptcha_api_key is not None else getattr(settings, "ANTICAPTCHA_API_KEY", None)
        )
        self.session = ChromeSession(
            headless=getattr(auto_cfg, "headless_mode", headless),
            extension_path=resolved_ext,
            anticaptcha_api_key=configured_key,
            user_data_dir=user_data_dir if user_data_dir is not None else getattr(auto_cfg, "chrome_user_data_dir", None),
            user_agent=user_agent if user_agent is not None else getattr(auto_cfg, "user_agent", None),
            chrome_binary_path=chrome_binary_path if chrome_binary_path is not None else getattr(auto_cfg, "chrome_binary_path", None),
            browser_engine=getattr(auto_cfg, "browser_engine", browser_engine),
            auto_cfg=auto_cfg,
        )
        self.captcha_manager = CaptchaManager(
            timeout_seconds=getattr(auto_cfg, "captcha_wait_seconds", getattr(settings, "CAPTCHA_TIMEOUT_SECONDS", 120))
        )
        self.timeout_ms = int(getattr(auto_cfg, "page_timeout_seconds", settings.PLAYWRIGHT_TIMEOUT_MS / 1000) * 1000)
        self.tab_manager: TabManager | None = None
        self.stage_timings: dict[str, Any] = {}

    async def __aenter__(self) -> "BrowserManager":
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
            "detail": (
                f"{'Microsoft Edge' if self.session.browser_engine in ('edge', 'msedge') else ('Chromium' if self.session.browser_engine == 'chromium' else 'Google Chrome')} "
                f"({'Headless (Background)' if self.session.headless else 'Attended (Visible GUI)'})"
                f"{' + AntiCaptcha' if self.session.extension_path else ''}"
            ),
        }
        self.tab_manager = TabManager(context, timeout_ms=self.timeout_ms)
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
    """Executes a browser coroutine on an isolated Proactor event loop on Windows.

    Playwright spawns and communicates with the browser subprocess driver via pipes.
    Running it in a dedicated thread with its own ProactorEventLoop prevents
    driver subprocess I/O and pipe events from interfering with Uvicorn's HTTP accept loop.
    """
    if sys.platform == "win32":
        def _runner():
            proactor = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(proactor)
            try:
                return proactor.run_until_complete(coro_fn(*args, **kwargs))
            finally:
                try:
                    pending = [t for t in asyncio.all_tasks(proactor) if not t.done()]
                    for t in pending:
                        t.cancel()
                    if pending:
                        proactor.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                except Exception:
                    pass
                try:
                    proactor.close()
                except Exception:
                    pass
        return await asyncio.to_thread(_runner)
    return await coro_fn(*args, **kwargs)


