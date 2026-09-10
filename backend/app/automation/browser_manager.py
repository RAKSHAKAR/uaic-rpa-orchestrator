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
        """Resolves existing AntiCaptcha extension directory on disk with dynamic relative fallback."""
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

        candidate_paths.extend([
            repo_root / "anticaptcha-plugin_v0.83",
            backend_dir / "anticaptcha-plugin_v0.83",
            Path.cwd() / "anticaptcha-plugin_v0.83",
            Path.cwd().parent / "anticaptcha-plugin_v0.83",
            Path(r"D:\UAIG\Bot Automation Project\anticaptcha-plugin_v0.83_1"),
            Path(r"C:\UAIG\Bot Automation Project\anticaptcha-plugin_v0.83_1"),
        ])

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
    def sync_api_key(extension_dir: Path | str, api_key: str) -> bool:
        """Injects Anti-Captcha API key into config_ac_api_key.js if not already configured."""
        if not api_key:
            return False

        if ExtensionManager.is_extension_configured(extension_dir, api_key):
            logger.debug("AntiCaptcha extension on disk is already configured with current API key.")
            return True

        ext_path = Path(extension_dir)
        config_file = ext_path / "js" / "config_ac_api_key.js"
        if not config_file.parent.exists():
            config_file.parent.mkdir(parents=True, exist_ok=True)

        clean_key = api_key.strip()
        content = (
            f"// Auto-synchronized runtime Anti-Captcha key and settings (Python 3.14)\n"
            f"var antiCapApiKey = '{clean_key}';\n"
            f"var antiCapAutoSubmitForm = false;\n\n"
            f"(function initAntiCaptchaStorage() {{\n"
            f"    try {{\n"
            f"        if (typeof chrome !== 'undefined' && chrome.storage) {{\n"
            f"            var fullConfig = {{\n"
            f"                account_key: antiCapApiKey,\n"
            f"                account_key_checked: true,\n"
            f"                enable: true,\n"
            f"                auto_submit_form: false,\n"
            f"                play_sounds: false,\n"
            f"                solve_recaptcha2: true,\n"
            f"                solve_invisible_recaptcha: true,\n"
            f"                solve_recaptcha3: true,\n"
            f"                recaptcha3_score: 0.3,\n"
            f"                solve_hcaptcha: true,\n"
            f"                solve_turnstile: true,\n"
            f"                solve_funcaptcha: true,\n"
            f"                solve_geetest: true,\n"
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
            logger.info("Synchronized AntiCaptcha runtime API key to extension config.")
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

        ext_id = "gcpdbjbmekkdlkpldjgffhmapgpdlcpj"
        active = False
        found_id = None

        for sw in sws:
            url = getattr(sw, "url", "")
            if ext_id in url or "anticaptcha" in url.lower():
                active = True
                found_id = ext_id
                break

        if not active:
            for bg in bg_pages:
                url = getattr(bg, "url", "")
                if ext_id in url or "anticaptcha" in url.lower():
                    active = True
                    found_id = ext_id
                    break

        is_loaded = active or (len(sws) > 0)
        return {
            "loaded": is_loaded,
            "service_workers_count": len(sws),
            "background_pages_count": len(bg_pages),
            "extension_id": found_id or (ext_id if is_loaded else None),
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
        browser_engine: str = "chromium",
    ):
        self.headless = headless
        self.extension_path = ExtensionManager.resolve_extension_path(extension_path)
        self.anticaptcha_api_key = anticaptcha_api_key
        self.user_data_dir = user_data_dir
        self.user_agent = user_agent
        self.chrome_binary_path = chrome_binary_path
        self.browser_engine = (browser_engine or "chromium").lower()

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

    async def start(self) -> BrowserContext:
        """Launches Google Chrome or Chromium persistent context with extension loading."""
        cache_dir = Path(__file__).resolve().parent.parent.parent / "data" / "browser_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        engine = self.browser_engine

        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--window-position=50,50",
            f"--disk-cache-dir={cache_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-features=msFirstRunExperience,msEdgeWelcomePage",
        ]

        has_ext = bool(self.extension_path and self.extension_path.is_dir())
        if has_ext and self.anticaptcha_api_key:
            ExtensionManager.sync_api_key(self.extension_path, self.anticaptcha_api_key)

        # Profile directory
        target_dir = Path(self.user_data_dir) if self.user_data_dir else None
        if target_dir and target_dir.is_dir() and "Default" not in str(target_dir):
            self.profile_to_use = target_dir
            self.is_temp_profile = False
        else:
            temp_path = Path(tempfile.mkdtemp(prefix="uaic_chrome_profile_"))
            self.profile_to_use = temp_path
            self.is_temp_profile = True

        # When running Google Chrome or Edge with a temp profile, seed with user's profile preferences if available
        # so Developer Mode and installed unpacked extensions load seamlessly with pinned toolbar
        if engine in ("chrome", "msedge") and self.is_temp_profile:
            source_user_data = target_dir if (target_dir and target_dir.is_dir()) else (
                self.find_default_chrome_user_data_dir() if engine == "chrome" else self.find_default_edge_user_data_dir()
            )
            if source_user_data and source_user_data.is_dir():
                try:
                    default_target = self.profile_to_use / "Default"
                    default_target.mkdir(parents=True, exist_ok=True)
                    for fname in ["Local State"]:
                        src = source_user_data / fname
                        if src.is_file():
                            shutil.copy2(src, self.profile_to_use / fname)
                    for fname in ["Preferences", "Secure Preferences"]:
                        src = source_user_data / "Default" / fname
                        if src.is_file():
                            shutil.copy2(src, default_target / fname)
                    logger.info(f"Pre-seeded {engine.upper()} temporary profile from {source_user_data} for Developer Mode & pinned toolbar support.")
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

        # Ensure profile Preferences pins AntiCaptcha on browser toolbar across all engines (Chrome, Edge, Chromium)
        try:
            default_profile_dir = self.profile_to_use / "Default"
            default_profile_dir.mkdir(parents=True, exist_ok=True)
            pref_file = default_profile_dir / "Preferences"
            prefs: dict[str, Any] = {}
            if pref_file.is_file():
                try:
                    prefs = json.loads(pref_file.read_text(encoding="utf-8"))
                except Exception:
                    prefs = {}
            ext_prefs = prefs.setdefault("extensions", {})
            ext_prefs["developer_mode"] = True
            pinned = ext_prefs.setdefault("pinned_extensions", [])
            ext_id_to_pin = "gcpdbjbmekkdlkpldjgffhmapgpdlcpj"
            if ext_id_to_pin not in pinned:
                pinned.append(ext_id_to_pin)
            ext_prefs["pinned_extension_migration"] = True

            # Ensure Edge / Chromium toolbar button visibility
            browser_prefs = prefs.setdefault("browser", {})
            browser_prefs["show_extensions_toolbar_menu"] = True

            pref_file.write_text(json.dumps(prefs, indent=2), encoding="utf-8")
        except Exception as e:
            logger.debug(f"Failed to pre-seed profile Preferences for pinned extension: {e}")

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

        try:
            self.playwright = await async_playwright().start()
        except FileNotFoundError as e:
            raise RuntimeError(
                f"Failed to spawn Playwright driver process ({e}). "
                f"Please ensure Playwright dependencies are installed via 'python -m playwright install chromium' or setup.ps1."
            ) from e

        launch_kwargs: dict[str, Any] = {
            "user_data_dir": str(self.profile_to_use),
            "headless": context_headless,
            "args": launch_args,
            "ignore_default_args": ["--disable-extensions"] if has_ext else None,
            "no_viewport": True if not is_headless else False,
            "viewport": {"width": settings.PLAYWRIGHT_VIEWPORT_WIDTH, "height": settings.PLAYWRIGHT_VIEWPORT_HEIGHT} if is_headless else None,
        }

        # Resolve authentic User-Agent for engine if default or unset
        from app.schemas.settings import CHROME_USER_AGENT, MSEDGE_USER_AGENT, get_engine_user_agent
        effective_user_agent = self.user_agent
        if not effective_user_agent or effective_user_agent in (CHROME_USER_AGENT, MSEDGE_USER_AGENT):
            effective_user_agent = get_engine_user_agent(engine)

        launch_kwargs["user_agent"] = effective_user_agent

        if engine == "chrome":
            chrome_exe = self.find_chrome_executable(self.chrome_binary_path)
            if chrome_exe:
                launch_kwargs["executable_path"] = str(chrome_exe)
            else:
                raise RuntimeError(
                    f"Google Chrome executable (chrome.exe) was not found on this system "
                    f"(searched: {self.chrome_binary_path or 'standard Program Files and LocalAppData locations'}). "
                    f"Please verify Google Chrome is installed or specify the path in Settings."
                )
        elif engine == "msedge":
            launch_kwargs["channel"] = "msedge"
        else:
            # "chromium": Playwright bundled browser engine with full extension support
            pass

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
            # Poll up to 1.5s for service worker or background page registration
            for _ in range(15):
                if self.context.service_workers or self.context.background_pages:
                    break
                await asyncio.sleep(0.1)

            # Auto-fallback to Chromium if enterprise policy blocked extension in Google Chrome
            if not (self.context.service_workers or self.context.background_pages) and engine == "chrome":
                logger.warning(
                    "[BrowserLaunch] Google Chrome enterprise policy blocked unpacked extension sideloading. "
                    "Automatically falling back to Chromium engine where AntiCaptcha extension is verified and active..."
                )
                try:
                    await self.context.close()
                except Exception:
                    pass
                launch_kwargs["executable_path"] = None
                launch_kwargs["channel"] = None
                self.engine = "chromium"
                self.context = await self.playwright.chromium.launch_persistent_context(**launch_kwargs)
                for _ in range(15):
                    if self.context.service_workers or self.context.background_pages:
                        break
                    await asyncio.sleep(0.1)

            if self.context.service_workers or self.context.background_pages:
                self.extension_loaded = True
                self.service_worker_active = bool(self.context.service_workers)
                ext_id = "gcpdbjbmekkdlkpldjgffhmapgpdlcpj"
                if self.context.service_workers:
                    worker = self.context.service_workers[0]
                    m = re.search(r"chrome-extension://([a-z0-9]+)/", worker.url)
                    if m:
                        ext_id = m.group(1)
                elif self.context.background_pages:
                    bg = self.context.background_pages[0]
                    m = re.search(r"chrome-extension://([a-z0-9]+)/", bg.url)
                    if m:
                        ext_id = m.group(1)
                self.extension_id = ext_id

                # Check if AntiCaptcha extension runtime is ALREADY properly configured with active API key in local storage
                api_key_to_use = self.anticaptcha_api_key or "28b486b8f31f74c6bf4453735815aa53"
                already_configured = False

                if self.context.service_workers:
                    try:
                        stored = await self.context.service_workers[0].evaluate("""() => {
                            return new Promise(resolve => {
                                if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
                                    chrome.storage.local.get(['account_key', 'enable', 'account_key_checked'], res => resolve(res));
                                } else {
                                    resolve(null);
                                }
                            });
                        }""")
                        if stored and stored.get("account_key") == api_key_to_use and stored.get("enable") is True:
                            already_configured = True
                    except Exception:
                        already_configured = False

                if already_configured:
                    logger.info(f"AntiCaptcha extension already verified and configured with active API key in local runtime storage (ID: {ext_id}). Skipping redundant popup setup.")
                else:
                    # Extension not yet configured in runtime: configure both local and sync storages
                    if self.context.service_workers:
                        try:
                            await self.context.service_workers[0].evaluate("""(apiKey) => {
                                return new Promise(resolve => {
                                    const fullConfig = {
                                        account_key: apiKey,
                                        account_key_checked: true,
                                        enable: true,
                                        auto_submit_form: false,
                                        play_sounds: false,
                                        solve_recaptcha2: true,
                                        solve_invisible_recaptcha: true,
                                        solve_recaptcha3: true,
                                        recaptcha3_score: 0.3,
                                        solve_hcaptcha: true,
                                        solve_turnstile: true,
                                        solve_funcaptcha: true,
                                        solve_geetest: true,
                                        use_predefined_image_captcha_marks: true,
                                        start_recaptcha2_solving_when_challenge_shown: true,
                                        use_recaptcha_precaching: false,
                                        k_precached_solution_count_min: 2,
                                        k_precached_solution_count_max: 4,
                                        dont_reuse_recaptcha_solution: false,
                                        solve_only_presented_recaptcha2: false,
                                        solve_proxy_on_tasks: false,
                                        set_incoming_workers_user_agent: false,
                                        run_explicit_invisible_hcaptcha_callback_when_challenge_shown: false,
                                        delay_onready_callback: false,
                                        reenable_contextmenu: false,
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

                    # To ensure Vue options store initializes, binds credentials, and verifies live balance, activate popup briefly
                    try:
                        setup_page = await self.context.new_page()
                        popup_url = f"chrome-extension://{ext_id}/popup_v3.html"
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
                        logger.info(f"AntiCaptcha runtime activated and verified with API key in browser profile (ID: {ext_id}).")
                    except Exception as e:
                        logger.warning(f"Note during AntiCaptcha runtime setup page activation: {e}")
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
        browser_engine: str = "chromium",
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
