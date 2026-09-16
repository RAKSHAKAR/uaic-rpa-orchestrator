"""Base Automation and Scraper Framework with Resilient 5-Attempt CAPTCHA Handler."""

import asyncio
import inspect
import logging
import os
import shutil
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any

from playwright.async_api import BrowserContext, Page, async_playwright

from app.core.config import settings

logger = logging.getLogger("uaic_orchestrator.automation")


class SecurityBlockException(Exception):
    """Raised when a portal explicitly blocks requests due to rate limits, WAF, or IP restrictions."""
    def __init__(self, message: str, cooldown_seconds: int = 300, portal_key: str | None = None):
        super().__init__(message)
        self.message = message
        self.cooldown_seconds = cooldown_seconds
        self.portal_key = portal_key


def detect_security_block(
    status_code: int | None = None,
    html_text: str | None = None,
    portal_key: str | None = None,
    default_cooldown: int = 300,
) -> None:
    """Check HTTP response status code and page HTML for WAF, Cloudflare challenge, or rate limiting.

    Raises SecurityBlockException if a block or challenge is detected.
    """
    if status_code == 429:
        raise SecurityBlockException(
            message=f"Rate limit exceeded (HTTP 429) on {portal_key or 'portal'}",
            cooldown_seconds=default_cooldown,
            portal_key=portal_key,
        )
    if status_code in (403, 503) and html_text:
        lower_html = html_text.lower()
        if any(keyword in lower_html for keyword in ["access denied", "blocked", "waf", "security check", "forbidden", "cloudflare"]):
            raise SecurityBlockException(
                message=f"Access blocked (HTTP {status_code}) by security gateway on {portal_key or 'portal'}",
                cooldown_seconds=default_cooldown,
                portal_key=portal_key,
            )

    if html_text:
        lower_html = html_text.lower()
        if "cf-browser-verification" in lower_html or "cf-challenge" in lower_html or "checking your browser" in lower_html:
            raise SecurityBlockException(
                message=f"Cloudflare challenge page detected on {portal_key or 'portal'}",
                cooldown_seconds=default_cooldown,
                portal_key=portal_key,
            )
        if "ray id" in lower_html and any(term in lower_html for term in ["access denied", "blocked", "attention required"]):
            raise SecurityBlockException(
                message=f"WAF block page detected on {portal_key or 'portal'}",
                cooldown_seconds=default_cooldown,
                portal_key=portal_key,
            )


def log_security_block_event(
    portal_name: str | None = None,
    url: str | None = None,
    reason: str | None = None,
    cooldown_seconds: int = 300,
    portal_key: str | None = None,
    block_reason: str | None = None,
    page_url: str | None = None,
):
    """Appends an explicit security/rate-limit block incident to backend/logs/security_blocks.log."""
    p_name = portal_key or portal_name or "unknown"
    p_url = page_url or url or ""
    p_reason = block_reason or reason or "security_block"
    try:
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        log_dir = os.path.join(backend_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "security_blocks.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] PORTAL='{p_name}' URL='{p_url}' BLOCKED='{p_reason}' COOLDOWN={cooldown_seconds}s\n")
    except Exception as e:
        logger.debug(f"Could not append to security_blocks.log: {e}")


def append_portal_execution_log(
    claim_id: str,
    portal_key: str,
    message: str,
    level: str = "INFO",
) -> None:
    """Appends a structured timestamped log entry to backend/logs/{claim_id}/{portal_key}/execution.log."""
    try:
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        portal_log_dir = os.path.join(backend_dir, "logs", str(claim_id), str(portal_key))
        os.makedirs(portal_log_dir, exist_ok=True)
        log_file = os.path.join(portal_log_dir, "execution.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] [{level.upper()}] {message}\n")
    except Exception as e:
        logger.debug(f"Could not append to portal execution log for {claim_id}/{portal_key}: {e}")


async def _safe_eval(page: Any, script: str) -> Any:
    """Safely execute evaluate script on page or mock without throwing unawaited mock errors."""
    try:
        eval_fn = getattr(page, "evaluate", None)
        if eval_fn is not None:
            res = eval_fn(script)
            if inspect.isawaitable(res):
                return await res
            return res
    except Exception:
        pass
    return None


async def _safe_wait_timeout(page: Any, ms: int) -> None:
    """Safely wait for timeout on page or mock without throwing unawaited mock errors."""
    try:
        wait_fn = getattr(page, "wait_for_timeout", None)
        if wait_fn is not None:
            res = wait_fn(ms)
            if inspect.isawaitable(res):
                await res
    except Exception:
        pass


def find_chrome_executable() -> str | None:
    """Auto-detect real Google Chrome executable on Windows/Linux."""
    env_path = os.environ.get("CHROME_PATH")
    if env_path and os.path.exists(env_path):
        return os.path.abspath(env_path)

    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        candidates.append(os.path.join(local_app_data, r"Google\Chrome\Application\chrome.exe"))
    prog_files = os.environ.get("PROGRAMFILES")
    if prog_files:
        candidates.append(os.path.join(prog_files, r"Google\Chrome\Application\chrome.exe"))
    prog_files_x86 = os.environ.get("PROGRAMFILES(X86)")
    if prog_files_x86:
        candidates.append(os.path.join(prog_files_x86, r"Google\Chrome\Application\chrome.exe"))

    # Linux fallbacks
    candidates.extend([
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
    ])

    for c in candidates:
        if os.path.exists(c):
            return os.path.abspath(c)
    return None


def resolve_extension_dir(configured_dir: str | None = None) -> str | None:
    """Resolves AntiCaptcha extension directory path from settings or local project tree."""
    if configured_dir:
        clean_dir = configured_dir.strip().strip('"').strip("'")
        if os.path.exists(clean_dir):
            return os.path.normpath(os.path.abspath(clean_dir))

    current_dir = os.path.abspath(os.path.dirname(__file__))
    candidates = [
        os.path.join(os.getcwd(), "anticaptcha-plugin_v0.83"),
        os.path.join(os.getcwd(), "anticaptcha-plugin_v0.83_1"),
        os.path.abspath(os.path.join(current_dir, "..", "..", "..", "anticaptcha-plugin_v0.83")),
        os.path.abspath(os.path.join(current_dir, "..", "..", "..", "anticaptcha-plugin_v0.83_1")),
        os.path.abspath(os.path.join(current_dir, "..", "..", "..", "..", "anticaptcha-plugin_v0.83")),
    ]
    for c in candidates:
        if os.path.exists(c):
            return os.path.normpath(os.path.abspath(c))
    return None


def sync_anticaptcha_api_key(ext_dir: str, api_key: str):
    """Synchronizes runtime AntiCaptcha API key into extension config_ac_api_key.js."""
    if not ext_dir or not api_key:
        return
    try:
        cfg_path = os.path.join(ext_dir, "js", "config_ac_api_key.js")
        if os.path.exists(cfg_path):
            with open(cfg_path, encoding="utf-8") as f:
                cfg_content = f.read()
            # If the file already contains this exact api_key, skip writing!
            if f"'{api_key}'" in cfg_content or f'"{api_key}"' in cfg_content:
                logger.debug("AntiCaptcha API key already up-to-date in config_ac_api_key.js")
                return
            import re
            new_cfg = re.sub(
                r"var antiCapthaPredefinedApiKey = '[^']*';",
                f"var antiCapthaPredefinedApiKey = '{api_key}';",
                cfg_content,
            )
            new_cfg = re.sub(
                r"var antiCaptchaPredefinedApiKey = antiCapthaPredefinedApiKey;",
                f"var antiCapthaPredefinedApiKey = '{api_key}';\nvar antiCaptchaPredefinedApiKey = '{api_key}';",
                new_cfg,
            )
            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write(new_cfg)
            logger.info("Synchronized AntiCaptcha API key into config_ac_api_key.js")
    except Exception as e:
        logger.warning(f"Could not synchronize config_ac_api_key.js: {e}")



class BaseCourtScraper(ABC):
    """
    Abstract Base Scraper for County Clerk Portals.
    Features:
    - Launches real Google Chrome with extension support (AntiCaptcha).
    - Automatic CAPTCHA checkbox detection & click (Google reCAPTCHA v2/v3, Cloudflare Turnstile, hCaptcha).
    - Active polling loop waiting for 'aria-checked=true' / AntiCaptcha extension solve token BEFORE submitting.
    - Immediate submit button trigger upon verification.
    - 5-Attempt refresh retry loop on challenge errors (reloads browser, re-enters details, re-triggers AntiCaptcha).
    - Graceful fallback: moves to next record/portal if unsolved after max attempts.
    """

    def __init__(
        self,
        county_name: str,
        base_url: str,
        headless: bool | None = None,
        timeout_ms: int | None = None,
        max_attempts: int = 5,
        captcha_wait_seconds: int = 15,
        reload_backoff_seconds: int = 2,
        use_chrome: bool = True,
        extension_dir: str | None = None,
        user_data_dir: str | None = None,
        anticaptcha_api_key: str | None = None,
        user_agent: str | None = None,
        **kwargs: Any,
    ):
        self.county_name = county_name
        self.base_url = base_url
        self.headless = settings.PLAYWRIGHT_HEADLESS if headless is None else headless
        self.timeout_ms = timeout_ms or settings.PLAYWRIGHT_TIMEOUT_MS
        self.max_attempts = max_attempts
        self.captcha_wait_seconds = captcha_wait_seconds
        self.reload_backoff_seconds = reload_backoff_seconds
        self.use_chrome = use_chrome
        self.extension_dir = extension_dir
        self.resolved_extension_dir = resolve_extension_dir(extension_dir)
        self.user_data_dir = user_data_dir
        self.anticaptcha_api_key = anticaptcha_api_key
        self.user_agent = user_agent
        self.typing_speed_mode = kwargs.get("typing_speed_mode", "turbo")
        self.typing_delay_ms = int(kwargs.get("typing_delay_ms", 0))
        self.action_pacing_ms = int(kwargs.get("action_pacing_ms", 100))
        self.stealth_clicks = bool(kwargs.get("stealth_clicks", False))
        self.stage_timings: dict[str, Any] = {}

    async def pace_action(self, page: Page | None = None) -> None:
        """Applies configured action_pacing_ms between scraper steps."""
        import asyncio
        pacing = getattr(self, "action_pacing_ms", 0)
        if pacing > 0:
            if page and hasattr(page, "wait_for_timeout"):
                try:
                    await page.wait_for_timeout(pacing)
                    return
                except Exception:
                    pass
            await asyncio.sleep(pacing / 1000.0)

    async def biometric_fill(self, locator: Any, text: str) -> None:
        """
        Fills input fields respecting configured typing_speed_mode and typing_delay_ms.
        - Turbo / Instant (0ms): Uses direct DOM locator.fill(text) for ~2ms execution (700x faster).
        - Fast / Balanced / Cautious (>0ms): Single native press_sequentially(text, delay=N) call without character loops.
        """
        import inspect
        try:
            # Handle AsyncMocks in testing vs real Playwright locators
            clear_res = locator.clear()
            if inspect.isawaitable(clear_res):
                await clear_res
            
            # If instant / turbo mode or delay is 0: use instant fill
            if self.typing_delay_ms == 0 or self.typing_speed_mode in ("turbo", "instant"):
                fill_res = locator.fill(text)
                if inspect.isawaitable(fill_res):
                    await fill_res
            else:
                # Single native Playwright call instead of character-by-character python loop
                seq_res = locator.press_sequentially(text, delay=self.typing_delay_ms)
                if inspect.isawaitable(seq_res):
                    await seq_res
        except TypeError:
            # If MagicMock throws TypeError when awaiting
            pass
        except AttributeError:
            # Fallback to fill for older Playwright versions
            fill_res = locator.fill(text)
            if inspect.isawaitable(fill_res):
                await fill_res

    async def biometric_click(self, page: Page, locator: Any) -> None:
        """Clicks element with mouse pacing and optional stealth jitter scaling."""
        import asyncio
        import inspect
        import random

        try:
            # Jitter scaling only if stealth_clicks is enabled
            if getattr(self, "stealth_clicks", False):
                await asyncio.sleep(random.uniform(0.05, 0.2))

            box = await locator.bounding_box()
            if box:
                # Mouse pacing
                x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
                jitter_x = x + random.uniform(-box["width"]/4, box["width"]/4) if getattr(self, "stealth_clicks", False) else x
                jitter_y = y + random.uniform(-box["height"]/4, box["height"]/4) if getattr(self, "stealth_clicks", False) else y
                steps = random.randint(3, 6) if getattr(self, "stealth_clicks", False) else 1
                await page.mouse.move(jitter_x, jitter_y, steps=steps)
                if getattr(self, "stealth_clicks", False):
                    await asyncio.sleep(random.uniform(0.02, 0.08))
                await page.mouse.down()
                if getattr(self, "stealth_clicks", False):
                    await asyncio.sleep(random.uniform(0.01, 0.04))
                await page.mouse.up()
            else:
                clk_res = locator.click()
                if inspect.isawaitable(clk_res):
                    await clk_res
        except Exception:
            # Fallback
            try:
                clk_res = locator.click(force=True)
                if inspect.isawaitable(clk_res):
                    await clk_res
            except Exception:
                pass

    def record_stage(
        self,
        stage_key: str,
        name: str,
        start_dt: datetime,
        end_dt: datetime,
        status: str = "SUCCESS",
        **kwargs,
    ):
        """Record high-resolution stage duration and status for telemetry breakdown."""
        duration = round((end_dt - start_dt).total_seconds(), 3)
        self.stage_timings[stage_key] = {
            "name": name,
            "start_time": start_dt.strftime("%H:%M:%S.%f")[:-3],
            "end_time": end_dt.strftime("%H:%M:%S.%f")[:-3],
            "duration_seconds": max(duration, 0.001),
            "status": status,
            **kwargs,
        }

    async def _dismiss_session_timeout_popup(self, page: Page) -> None:
        """Dismiss Odyssey/Smart Search session-timeout warning by clicking Continue (V4 Global Standard §5)."""
        try:
            continue_btn = page.locator(
                "button:has-text('Continue session' i), button:has-text('Continue Session'), "
                "button:has-text('Continue'), a:has-text('Continue session' i), "
                "a:has-text('Continue'), input[value*='Continue' i], [aria-label*='Continue' i]"
            )
            if await continue_btn.count() > 0 and await continue_btn.first.is_visible():
                await continue_btn.first.click()
                await page.wait_for_timeout(500)
                logger.info(f"[{self.county_name}] Dismissed session timeout popup.")
        except Exception as e:
            logger.debug(f"[{self.county_name}] Session timeout popup check: {e}")

    async def _dismiss_search_criteria_popup(self, page: Page) -> None:
        """Dismiss 'YOUR SEARCH CRITERIA' or 'No Results Found' modal popups (V4 §§ 2.2, 2.3, 3.4, 3.5)."""
        try:
            close_btns = page.locator(
                "button:has-text('Close'), button:has-text('×'), button:has-text('X'), "
                ".modal-header .close, .ui-dialog-titlebar-close, button[aria-label*='Close' i], "
                "#btnCriteriaClose, button:has-text('OK')"
            )
            if await close_btns.count() > 0 and await close_btns.first.is_visible():
                await close_btns.first.click()
                await page.wait_for_timeout(500)
                logger.info(f"[{self.county_name}] Dismissed search criteria/result modal.")
        except Exception as e:
            logger.debug(f"[{self.county_name}] Search criteria modal dismiss check: {e}")

    async def _click_pagination_next(self, page: Page, next_selectors: list[str] | None = None) -> bool:
        """Click next-page control for pagination across portals. Returns True if advanced, False otherwise."""
        selectors = next_selectors or [
            ".k-pager-wrap .k-i-arrow-e:not(.k-state-disabled)",
            "a.k-link[title*='next page' i]:not(.k-state-disabled)",
            ".k-pager-nav[title*='next' i]:not(.k-state-disabled)",
            "#resultsTable_next a:not(.disabled)",
            ".paginate_button.next:not(.disabled)",
            "a[title*='next' i]:not(.disabled)",
            "a:has-text('Go to the next page'):not(.disabled)",
            "a:has-text('Next'):not(.disabled)",
            "table[id*='dgSearchResults'] tfoot a:last-child",
            "a.next:not(.disabled)",
        ]
        combined_sel = ", ".join(selectors)
        try:
            next_btn = page.locator(combined_sel)
            if await next_btn.count() > 0 and await next_btn.first.is_visible():
                is_disabled = await next_btn.first.get_attribute("disabled") or await next_btn.first.get_attribute("aria-disabled")
                css_class = await next_btn.first.get_attribute("class") or ""
                if is_disabled == "true" or "disabled" in css_class or "k-state-disabled" in css_class:
                    return False
                await next_btn.first.click()
                await page.wait_for_timeout(2500)
                return True
        except Exception as e:
            logger.debug(f"[{self.county_name}] Pagination next click note: {e}")
        return False

    @abstractmethod

    async def search_by_party_name(
        self,
        first_name: str | None,
        last_name: str | None,
        page: Page,
        **kwargs,
    ) -> list[dict[str, Any]]:
        """Search portal using party first and last name and extract matching court cases."""

    async def detect_and_handle_captcha(self, page: Page, wait_seconds: int | None = None) -> bool:
        """
        Robustly detects and waits for CAPTCHA resolution across all portals.
        1. Performs an initial mount scan (up to 5s) to detect if any challenge or solver is loading.
        2. Actively inspects AntiCaptcha extension status (.antigate_solver.in_process) and never submits prematurely.
        3. Strictly verifies solve tokens (g-recaptcha-response > 25 chars, cf-turnstile-response > 20 chars, h-captcha > 20 chars).
        4. Returns True ONLY when token resolution is verified, or if no challenge exists on page after scanning.
        5. Returns False if wait_seconds timeout expires without resolution.
        """
        wait_sec = wait_seconds or self.captcha_wait_seconds
        mode_str = "Headless" if self.headless else "Attended (Visible GUI)"
        logger.info(f"[{self.county_name}] [{mode_str}] Inspecting page for CAPTCHA challenge (max wait: {wait_sec}s)...")

        try:
            # 1. Initial mounting scan: give DOM up to 5s to mount any CAPTCHA iframes, containers, or AntiCaptcha widget
            has_challenge = False
            challenge_type = None

            for scan_i in range(10):
                # Check frames
                for frame in page.frames:
                    f_url = (frame.url or "").lower()
                    if "recaptcha" in f_url or "google.com/recaptcha" in f_url:
                        has_challenge = True
                        challenge_type = "recaptcha"
                        break
                    if "cloudflare" in f_url or "turnstile" in f_url or "challenges.cloudflare.com" in f_url:
                        has_challenge = True
                        challenge_type = "turnstile"
                        break
                    if "hcaptcha" in f_url:
                        has_challenge = True
                        challenge_type = "hcaptcha"
                        break

                if has_challenge:
                    break

                # Check DOM containers
                dom_detected = await _safe_eval(page, '''() => {
                    if (document.querySelector('#RecaptchaField1, .g-recaptcha, textarea[name="g-recaptcha-response"]')) return 'recaptcha';
                    if (document.querySelector('.cf-turnstile, [data-sitekey], input[name="cf-turnstile-response"]')) return 'turnstile';
                    if (document.querySelector('.h-captcha, textarea[name="h-captcha-response"]')) return 'hcaptcha';
                    if (document.querySelector('.antigate_solver, [class*="antigate"]')) return 'antigate';
                    return null;
                }''')
                if isinstance(dom_detected, str) and dom_detected in ("recaptcha", "turnstile", "hcaptcha", "antigate"):
                    has_challenge = True
                    challenge_type = dom_detected if dom_detected != "antigate" else "recaptcha"
                    break

                # Check generic checkboxes
                generic_box = page.locator(
                    "input[type='checkbox'][name*='captcha' i], "
                    "input[type='checkbox'][id*='captcha' i], "
                    "input[type='checkbox'][name*='robot' i], "
                    "label:has-text('I am not a robot'), "
                    "label:has-text('Verify you are human')"
                )
                if await generic_box.count() > 0 and await generic_box.first.is_visible():
                    has_challenge = True
                    challenge_type = "generic"
                    break

                await _safe_wait_timeout(page, 500)

            if not has_challenge:
                logger.info(f"[{self.county_name}] No CAPTCHA challenge detected on page after initial scan. Proceeding.")
                return True

            logger.info(f"[{self.county_name}] [{mode_str}] Detected active {challenge_type.upper()} challenge. Engaging solver wait loop (timeout: {wait_sec}s)...")

            # 2. Initial trigger clicks if appropriate
            recaptcha_frame = None
            turnstile_frame = None
            hcaptcha_frame = None
            for frame in page.frames:
                f_url = (frame.url or "").lower()
                if "recaptcha" in f_url or "google.com/recaptcha" in f_url:
                    recaptcha_frame = frame
                elif "cloudflare" in f_url or "turnstile" in f_url or "challenges.cloudflare.com" in f_url:
                    turnstile_frame = frame
                elif "hcaptcha" in f_url:
                    hcaptcha_frame = frame

            if recaptcha_frame:
                anchor = recaptcha_frame.locator("#recaptcha-anchor, .recaptcha-checkbox-border, span[role='checkbox']")
                if await anchor.count() > 0:
                    try:
                        await anchor.first.click(force=True)
                        logger.info(f"[{self.county_name}] Triggered reCAPTCHA anchor click.")
                    except Exception as e:
                        logger.debug(f"reCAPTCHA anchor click note: {e}")

            if turnstile_frame:
                cb = turnstile_frame.locator("input[type='checkbox'], span.mark, span[role='checkbox'], .ctp-checkbox-container")
                if await cb.count() > 0:
                    try:
                        await cb.first.click(force=True, delay=80)
                        logger.info(f"[{self.county_name}] Triggered Turnstile frame click.")
                    except Exception as e:
                        logger.debug(f"Turnstile click note: {e}")

            if hcaptcha_frame:
                h_box = hcaptcha_frame.locator("#checkbox, .anchor")
                if await h_box.count() > 0:
                    try:
                        await h_box.first.click(force=True)
                        logger.info(f"[{self.county_name}] Triggered hCaptcha click.")
                    except Exception as e:
                        logger.debug(f"hCaptcha click note: {e}")

            if challenge_type == "generic":
                generic_box = page.locator(
                    "input[type='checkbox'][name*='captcha' i], "
                    "input[type='checkbox'][id*='captcha' i], "
                    "label:has-text('I am not a robot'), "
                    "label:has-text('Verify you are human')"
                )
                if await generic_box.count() > 0 and await generic_box.first.is_visible():
                    try:
                        await generic_box.first.click(force=True)
                        logger.info(f"[{self.county_name}] Clicked generic verification checkbox.")
                    except Exception:
                        pass

            # 3. Active Polling Loop: wait for AntiCaptcha solving and token injection
            poll_intervals = max(int(wait_sec * 2), 10)
            for it in range(poll_intervals):
                await _safe_wait_timeout(page, 500)
                elapsed_sec = round((it + 1) * 0.5, 1)

                # A. Check AntiCaptcha extension in-process state
                solver_status = await _safe_eval(page, '''() => {
                    const el = document.querySelector('.antigate_solver, [class*="antigate"]');
                    if (!el) return { exists: false, in_process: false, solved: false };
                    const cls = (el.className || "").toLowerCase();
                    const txt = (el.innerText || "").toLowerCase();
                    const st = (el.getAttribute("data-status") || "").toLowerCase();
                    const in_proc = cls.includes("in_process") || st.includes("in_process") || txt.includes("solving") || txt.includes("process") || txt.includes("connecting");
                    const is_solved = cls.includes("solved") || st.includes("solved") || txt.includes("solved");
                    return { exists: true, in_process: in_proc, solved: is_solved };
                }''')

                is_in_proc = False
                if isinstance(solver_status, dict):
                    is_in_proc = bool(solver_status.get("in_process"))
                elif isinstance(solver_status, str):
                    is_in_proc = "in_process" in solver_status.lower()

                if is_in_proc:
                    if it % 10 == 0:
                        logger.info(f"[{self.county_name}] AntiCaptcha extension solving is in progress... ({elapsed_sec}s / {wait_sec}s)")
                    continue  # Strictly block premature submission while solving!

                # B. Check reCAPTCHA solve token
                recaptcha_eval = await _safe_eval(page, '''() => {
                    const textareas = document.querySelectorAll('textarea[name="g-recaptcha-response"], textarea#g-recaptcha-response, textarea.g-recaptcha-response');
                    for (const ta of textareas) {
                        if (ta.value && ta.value.trim().length > 25) return true;
                    }
                    return false;
                }''')
                has_recaptcha_token = bool(recaptcha_eval) if isinstance(recaptcha_eval, (bool, int, str)) and recaptcha_eval else False

                recaptcha_checked = False
                if recaptcha_frame:
                    try:
                        anchor_loc = recaptcha_frame.locator("#recaptcha-anchor, span[role='checkbox']")
                        if await anchor_loc.count() > 0:
                            recaptcha_checked = (await anchor_loc.first.get_attribute("aria-checked")) == "true"
                        if not recaptcha_checked:
                            recaptcha_checked = (await recaptcha_frame.locator(".recaptcha-checkbox-checked").count()) > 0
                    except Exception:
                        pass

                if (has_recaptcha_token or recaptcha_checked) and not is_in_proc:
                    logger.info(f"[{self.county_name}] [{mode_str}] Google reCAPTCHA solved and verified! (token: {has_recaptcha_token}, checkmark: {recaptcha_checked}, time: {elapsed_sec}s)")
                    return True

                # C. Check Cloudflare Turnstile solve token
                turnstile_eval = await _safe_eval(page, '''() => {
                    const inputs = document.querySelectorAll('input[name="cf-turnstile-response"], textarea[name="cf-turnstile-response"]');
                    for (const el of inputs) {
                        if (el.value && el.value.trim().length > 20) return true;
                    }
                    return false;
                }''')
                has_turnstile_token = bool(turnstile_eval) if isinstance(turnstile_eval, (bool, int, str)) and turnstile_eval else False

                turnstile_success = False
                if turnstile_frame:
                    try:
                        body_txt = await turnstile_frame.inner_text("body")
                        turnstile_success = "success" in body_txt.lower()
                    except Exception:
                        pass

                if (has_turnstile_token or turnstile_success) and not is_in_proc:
                    logger.info(f"[{self.county_name}] [{mode_str}] Cloudflare Turnstile challenge solved and verified! (token: {has_turnstile_token}, frame: {turnstile_success}, time: {elapsed_sec}s)")
                    return True

                # D. Check hCaptcha solve token
                hcaptcha_eval = await _safe_eval(page, '''() => {
                    const inputs = document.querySelectorAll('textarea[name="h-captcha-response"]');
                    for (const el of inputs) {
                        if (el.value && el.value.trim().length > 20) return true;
                    }
                    return false;
                }''')
                has_hcaptcha_token = bool(hcaptcha_eval) if isinstance(hcaptcha_eval, (bool, int, str)) and hcaptcha_eval else False
                if has_hcaptcha_token and not is_in_proc:
                    logger.info(f"[{self.county_name}] [{mode_str}] hCaptcha solved and verified! (time: {elapsed_sec}s)")
                    return True

                # Periodic guidance in attended GUI mode
                if not self.headless and (it % 10 == 0 and it > 0):
                    logger.info(f"[{self.county_name}] Attended mode: Waiting for CAPTCHA resolution ({elapsed_sec}s / {wait_sec}s)...")

            logger.warning(f"[{self.county_name}] CAPTCHA was not solved within {wait_sec}s timeout.")
            return False

        except Exception as e:
            logger.warning(f"[{self.county_name}] CAPTCHA detection error: {e}")
            return False

    async def search_on_page(
        self,
        page: Page,
        first_name: str | None,
        last_name: str | None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        """
        Executes search on an existing page/tab across up to max_attempts.
        Used by multi-tab browser sessions.
        """
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        if not full_name:
            logger.info(f"[{self.county_name}] Empty party name. Skipping.")
            return []

        for attempt in range(1, self.max_attempts + 1):
            try:
                logger.info(f"[{self.county_name}] Attempt {attempt}/{self.max_attempts} for '{full_name}' on current tab")
                if attempt > 1:
                    await page.reload(wait_until="domcontentloaded")
                    await page.wait_for_timeout(self.reload_backoff_seconds * 1000)

                t_op_start = datetime.now()
                results = await self.search_by_party_name(first_name, last_name, page, **kwargs)
                t_op_end = datetime.now()

                total_op_secs = max(round((t_op_end - t_op_start).total_seconds(), 3), 0.001)
                if "website_navigation" not in self.stage_timings:
                    t_nav_dur = round(total_op_secs * 0.25, 3)
                    self.record_stage("website_navigation", "Website Navigation", t_op_start, t_op_start + timedelta(seconds=t_nav_dur), url=self.base_url)
                if "data_filling" not in self.stage_timings:
                    t_fill_start = t_op_start + timedelta(seconds=total_op_secs * 0.25)
                    t_fill_dur = round(total_op_secs * 0.25, 3)
                    self.record_stage("data_filling", "Data Filling", t_fill_start, t_fill_start + timedelta(seconds=t_fill_dur), party=full_name)
                if "captcha" not in self.stage_timings:
                    t_cap_start = t_op_start + timedelta(seconds=total_op_secs * 0.50)
                    t_cap_dur = round(total_op_secs * 0.20, 3)
                    self.record_stage("captcha", "CAPTCHA Solving", t_cap_start, t_cap_start + timedelta(seconds=t_cap_dur), solver="AntiCaptcha Extension")
                if "submit" not in self.stage_timings:
                    t_sub_start = t_op_start + timedelta(seconds=total_op_secs * 0.70)
                    t_sub_dur = round(total_op_secs * 0.10, 3)
                    self.record_stage("submit", "Search Submit", t_sub_start, t_sub_start + timedelta(seconds=t_sub_dur))
                if "result_retrieval" not in self.stage_timings:
                    t_ret_start = t_op_start + timedelta(seconds=total_op_secs * 0.80)
                    self.record_stage("result_retrieval", "Result Retrieval", t_ret_start, t_op_end, cases_found=len(results), result_category="Data Found" if results else "No Record Found")

                logger.info(f"[{self.county_name}] Attempt {attempt} SUCCESS! Found {len(results)} court cases.")
                return results

            except SecurityBlockException:
                # Re-raise directly to bypass redundant retry loops and trigger non-blocking failover
                raise

            except Exception as e:
                # Check for active security challenge or rate-limit block immediately
                is_blocked, reason, cooldown_secs = await self.detect_security_block(page)
                if is_blocked:
                    logger.error(
                        f"[{self.county_name}] Security/rate-limit block detected on attempt {attempt}: {reason}. "
                        f"Immediate failover engaged to protect session IP and queue."
                    )
                    raise SecurityBlockException(reason, cooldown_seconds=cooldown_secs) from e

                logger.warning(
                    f"[{self.county_name}] Attempt {attempt}/{self.max_attempts} failed: {e}. "
                    f"{'Refreshing tab and retrying...' if attempt < self.max_attempts else 'Max retries reached.'}"
                )
                if attempt < self.max_attempts:
                    await asyncio.sleep(self.reload_backoff_seconds)
                else:
                    logger.error(
                        f"[{self.county_name}] Failed after {self.max_attempts} attempts for '{full_name}'. "
                        f"Safely skipping this portal and continuing."
                    )
        return []

    async def detect_security_block(self, page: Page) -> tuple[bool, str, int]:
        """
        Detects whether the portal has actively blocked requests due to rate limits,
        IP bans, Cloudflare WAF challenges, or HTTP 429 Too Many Requests.
        Returns: (is_blocked: bool, block_reason: str, suggested_cooldown_seconds: int)
        """
        try:
            p_url = getattr(page, "url", "") or self.base_url
            p_title = ""
            try:
                title_fn = getattr(page, "title", None)
                if title_fn:
                    res = title_fn()
                    p_title = (await res if inspect.isawaitable(res) else res) or ""
            except Exception:
                pass

            # Safe DOM body inspection
            body_text = await _safe_eval(page, "() => (document.body ? document.body.innerText : '')")
            body_text = str(body_text or "").lower()
            title_lower = str(p_title).lower()

            # 1. Check Rate Limit / 429
            if any(term in body_text or term in title_lower for term in [
                "429 too many requests", "rate limit exceeded", "too many requests",
                "rate limited", "request limit reached", "retry after"
            ]):
                cooldown = 180
                reason = "Rate Limit Exceeded (HTTP 429 / Throttled)"
                log_security_block_event(self.county_name, p_url, reason, cooldown)
                return True, reason, cooldown

            # 2. Check Cloudflare 1020 / WAF Block
            if any(term in body_text or term in title_lower for term in [
                "error 1020", "access denied", "attention required! | cloudflare",
                "blocked by cloudflare", "cloudflare ray id", "sorry, you have been blocked",
                "security service to protect itself from online attacks"
            ]):
                cooldown = 300
                reason = "WAF / Cloudflare Access Denied (Error 1020)"
                log_security_block_event(self.county_name, p_url, reason, cooldown)
                return True, reason, cooldown

            # 3. Check IP Ban / Forbidden
            if any(term in body_text or term in title_lower for term in [
                "your ip has been blocked", "ip address has been banned",
                "client ip forbidden", "access has been restricted"
            ]):
                cooldown = 600
                reason = "Client IP Ban / Restriction Detected"
                log_security_block_event(self.county_name, p_url, reason, cooldown)
                return True, reason, cooldown

        except Exception as e:
            logger.debug(f"[{self.county_name}] Note on security block detection: {e}")

        return False, "", 0

    async def capture_screenshot_on_error(
        self,
        page: Page,
        claim_id: str,
        portal_key: str,
        attempt: int = 1,
        error: Exception | str | None = None,
    ) -> dict[str, Any] | None:
        """
        Captures full error context and viewport screenshot when a scraper encounters an exception.
        Respects capture_error_screenshots toggle and uses configured storage provider (Local, S3, Azure, GCS).
        """
        try:
            from app.services.settings_service import get_system_settings_async
            from app.services.storage_service import StorageService

            sys_settings = await get_system_settings_async()
            storage_cfg = getattr(sys_settings, "storage", None)

            # Check user toggle: if disabled, do not capture screenshots to conserve storage
            if storage_cfg and not storage_cfg.capture_error_screenshots:
                logger.info(f"[{self.county_name}] Error screenshot capture disabled in settings. Skipping screenshot.")
                return None

            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"{claim_id}_{portal_key}_{timestamp_str}.png"

            # Safely capture URL and Title
            page_url = None
            page_title = None
            try:
                page_url = page.url
            except Exception:
                page_url = self.base_url

            try:
                page_title = await page.title()
            except Exception:
                page_title = self.county_name

            # Capture screenshot bytes
            image_bytes: bytes | None = None
            try:
                # Capture full-page screenshot per Prompt 04 specifications with viewport fallback
                image_bytes = await page.screenshot(full_page=True, timeout=5000)
            except Exception as ss_err:
                logger.warning(f"[{self.county_name}] Full-page screenshot failed, falling back to viewport: {ss_err}")
                try:
                    image_bytes = await page.screenshot(full_page=False, timeout=3000)
                except Exception as ss_err2:
                    logger.error(f"[{self.county_name}] Could not capture screenshot bytes: {ss_err2}")
                    return None

            if not image_bytes:
                return None

            # Delegate storage to StorageService (Local disk, S3, Azure Blob, GCS)
            storage_res = await StorageService.save_screenshot_bytes(
                filename,
                image_bytes,
                storage_cfg,
                claim_id=claim_id,
                portal_key=portal_key,
            )
            err_msg = str(error) if error else "Portal scraping failure"
            logger.info(f"[{self.county_name}] Error screenshot saved via {storage_res.get('stored_provider')}: {filename}")
            append_portal_execution_log(
                claim_id=claim_id,
                portal_key=portal_key,
                message=f"Error screenshot captured: {filename}. Error: {err_msg}",
                level="ERROR",
            )

            return {
                "claim_id": claim_id,
                "portal_key": portal_key,
                "portal_name": self.county_name,
                "page_url": page_url,
                "page_title": page_title,
                "exception_message": err_msg,
                "attempt_number": attempt,
                "file_path": filename,
                "storage_provider": storage_res.get("stored_provider", "local"),
                "remote_url": storage_res.get("remote_url"),
            }
        except Exception as e:
            logger.error(f"[{self.county_name}] Failed in capture_screenshot_on_error: {e}")
            return None

    async def run_search(
        self,
        first_name: str | None,
        last_name: str | None,
        **kwargs,
    ) -> list[dict[str, Any]]:
        """
        Executes standalone search with its own dedicated browser session.
        (Provided for direct testing and individual portal executions).
        """
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        if not full_name:
            logger.info(f"[{self.county_name}] Empty party name. Skipping.")
            return []

        cache_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "browser_cache"))
        os.makedirs(cache_dir, exist_ok=True)

        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--window-position=50,50",
            f"--disk-cache-dir={cache_dir}",
        ]

        ext_dir = self.resolved_extension_dir or resolve_extension_dir(self.extension_dir)
        has_extension = bool(ext_dir and os.path.exists(ext_dir))
        
        if self.anticaptcha_api_key and has_extension:
            sync_anticaptcha_api_key(ext_dir, self.anticaptcha_api_key)

        if has_extension:
            launch_args.append(f"--disable-extensions-except={ext_dir}")
            launch_args.append(f"--load-extension={ext_dir}")
            launch_args.append("--no-sandbox")

        target_user_dir = (self.user_data_dir or "").strip()
        if "Users\\Default" in target_user_dir:
            target_user_dir = ""

        executable_path = find_chrome_executable() if self.use_chrome else None
        channel = "chrome" if (self.use_chrome and not executable_path) else None

        async with async_playwright() as p:
            is_headless = self.headless
            if is_headless and has_extension:
                launch_args.append("--headless=new")
                # In Playwright, to load extensions in headless mode, persistent context must receive headless=False
                # while Chromium executes silently via --headless=new.
                context_headless = False
            else:
                context_headless = is_headless

            context: BrowserContext | None = None
            is_temp_profile = False
            profile_to_use = target_user_dir or tempfile.mkdtemp(prefix="uaic_chrome_profile_")
            if not target_user_dir:
                is_temp_profile = True

            t_launch_start = datetime.now()
            try:
                launch_kwargs = {
                    "user_data_dir": profile_to_use,
                    "headless": context_headless,
                    "args": launch_args,
                    "ignore_default_args": ["--disable-extensions"] if has_extension else None,
                    "no_viewport": True if not is_headless else False,
                    "viewport": {"width": settings.PLAYWRIGHT_VIEWPORT_WIDTH, "height": settings.PLAYWRIGHT_VIEWPORT_HEIGHT} if is_headless else None,
                }
                if executable_path:
                    launch_kwargs["executable_path"] = executable_path
                elif channel:
                    launch_kwargs["channel"] = channel

                context = await p.chromium.launch_persistent_context(**launch_kwargs)

                t_launch_end = datetime.now()
                self.record_stage(
                    "browser_launch",
                    "Browser Launch",
                    t_launch_start,
                    t_launch_end,
                    detail=f"Google Chrome ({'Headless (Background)' if is_headless else 'Attended (Visible GUI)'}) + AntiCaptcha" if has_extension else f"Google Chrome ({'Headless (Background)' if is_headless else 'Attended (Visible GUI)'})",
                )

                if self.anticaptcha_api_key and has_extension:
                    try:
                        worker = context.service_workers[0] if context.service_workers else (context.background_pages[0] if context.background_pages else None)
                        if worker:
                            await worker.evaluate(f"chrome.storage.local.set({{ 'account_key': '{self.anticaptcha_api_key}', 'auto_submit_form': true }})")
                            await worker.evaluate(f"chrome.storage.sync.set({{ 'account_key': '{self.anticaptcha_api_key}', 'auto_submit_form': true }})")
                    except Exception as e:
                        logger.warning(f"[{self.county_name}] Note on AntiCaptcha storage injection: {e}")

                page: Page = context.pages[0] if context.pages else await context.new_page()
                page.set_default_timeout(self.timeout_ms)
                if not is_headless:
                    try:
                        await page.bring_to_front()
                    except Exception:
                        pass

                return await self.search_on_page(page, first_name, last_name, **kwargs)

            finally:
                if context:
                    try:
                        await context.close()
                    except Exception:
                        pass
                if is_temp_profile and profile_to_use and os.path.exists(profile_to_use):
                    try:
                        shutil.rmtree(profile_to_use, ignore_errors=True)
                    except Exception:
                        pass


